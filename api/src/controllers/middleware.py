# RFM Insights - Middleware Module

from fastapi import Request, HTTPException, status
from typing import Dict, List, Callable, Optional
import time
import logging
from collections import defaultdict

# Setup logger
logger = logging.getLogger('app.middleware')

# Rate limiting middleware for authentication endpoints
class RateLimiter:
    """
    Rate limiting middleware to prevent brute force attacks
    Tracks requests by IP address and blocks excessive requests
    """
    def __init__(self, 
                 app,
                 rate_limit: int = 5, 
                 time_window: int = 60,
                 block_time: int = 300):
        """
        Initialize rate limiter
        
        Args:
            app: FastAPI application
            rate_limit: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            block_time: Time to block in seconds after exceeding rate limit
        """
        self.app = app
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.block_time = block_time
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        
    async def __call__(self, scope, receive, send):
        """
        ASGI middleware implementation
        
        Args:
            scope: ASGI connection scope
            receive: ASGI receive function
            send: ASGI send function
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Create request object
        request = Request(scope=scope, receive=receive)
        
        # Define a send wrapper to intercept the response
        async def send_wrapper(message):
            await send(message)
            
        # Process the request with rate limiting
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            path = request.url.path
            
            # Only apply rate limiting to authentication endpoints
            if not self._is_auth_endpoint(path):
                return await self.app(scope, receive, send)
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                block_time = self.blocked_ips[client_ip]
                current_time = time.time()
                
                # If block time has expired, remove from blocked list
                if current_time > block_time:
                    del self.blocked_ips[client_ip]
                    logger.info(f"Unblocked IP {client_ip} after timeout period")
                else:
                    # Calculate remaining block time
                    remaining = int(block_time - current_time)
                    logger.warning(f"Blocked request from {client_ip} to {path} (remaining block time: {remaining}s)")
                    
                    # Create HTTP exception
                    exc = HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Too many requests. Please try again in {remaining} seconds."
                    )
                    
                    # Return error response
                    from starlette.responses import JSONResponse
                    response = JSONResponse(
                        status_code=exc.status_code,
                        content={"detail": exc.detail}
                    )
                    
                    await send({
                        "type": "http.response.start",
                        "status": exc.status_code,
                        "headers": [
                            (b"content-type", b"application/json")
                        ]
                    })
                    
                    await send({
                        "type": "http.response.body",
                        "body": response.body
                    })
                    
                    return
            
            # Clean up old requests
            self._cleanup_old_requests(client_ip)
            
            # Check rate limit
            if len(self.requests[client_ip]) >= self.rate_limit:
                # Block the IP
                self.blocked_ips[client_ip] = time.time() + self.block_time
                logger.warning(f"Blocked IP {client_ip} for {self.block_time} seconds due to rate limit exceeded")
                
                # Create HTTP exception
                exc = HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Please try again later."
                )
                
                # Return error response
                from starlette.responses import JSONResponse
                response = JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail}
                )
                
                await send({
                    "type": "http.response.start",
                    "status": exc.status_code,
                    "headers": [
                        (b"content-type", b"application/json")
                    ]
                })
                
                await send({
                    "type": "http.response.body",
                    "body": response.body
                })
                
                return
            
            # Add current request timestamp
            self.requests[client_ip].append(time.time())
            
            # Process the request
            return await self.app(scope, receive, send)
        # Get client IP
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # Only apply rate limiting to authentication endpoints
        if not self._is_auth_endpoint(path):
            return await call_next(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            current_time = time.time()
            
            # If block time has expired, remove from blocked list
            if current_time > block_time:
                del self.blocked_ips[client_ip]
                logger.info(f"Unblocked IP {client_ip} after timeout period")
            else:
                # Calculate remaining block time
                remaining = int(block_time - current_time)
                logger.warning(f"Blocked request from {client_ip} to {path} (remaining block time: {remaining}s)")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Please try again in {remaining} seconds."
                )
        
        # Clean up old requests
        self._cleanup_old_requests(client_ip)
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.rate_limit:
            # Block the IP
            self.blocked_ips[client_ip] = time.time() + self.block_time
            logger.warning(f"Blocked IP {client_ip} for {self.block_time} seconds due to rate limit exceeded")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again later."
            )
        
        # Add current request timestamp
        self.requests[client_ip].append(time.time())
        
        # Process the request
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request headers or connection info
        
        Args:
            request: FastAPI request object
        """
        # Try to get IP from X-Forwarded-For header (when behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_ip: str) -> None:
        """
        Remove requests older than the time window
        
        Args:
            client_ip: Client IP address
        """
        if client_ip in self.requests:
            current_time = time.time()
            self.requests[client_ip] = [
                timestamp for timestamp in self.requests[client_ip]
                if current_time - timestamp < self.time_window
            ]
    
    def _is_auth_endpoint(self, path: str) -> bool:
        """
        Check if the path is an authentication endpoint
        
        Args:
            path: Request path
        """
        auth_endpoints = [
            "/api/auth/token",
            "/api/auth/register",
            "/api/auth/password-reset"
        ]
        return any(path.startswith(endpoint) for endpoint in auth_endpoints)


# Input validation middleware
class RequestValidator:
    """
    Middleware for additional request validation
    Performs basic sanity checks on incoming requests
    """
    def __init__(self, app):
        """
        Initialize request validator
        
        Args:
            app: FastAPI application
        """
        self.app = app
        
    async def __call__(self, scope, receive, send):
        """
        ASGI middleware implementation
        
        Args:
            scope: ASGI connection scope
            receive: ASGI receive function
            send: ASGI send function
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Create request object
        request = Request(scope=scope, receive=receive)
        
        # Get request content type
        content_type = request.headers.get("content-type", "")
        
        # For JSON requests, validate content length
        if "application/json" in content_type:
            content_length = request.headers.get("content-length", "0")
            try:
                if int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                    # Create HTTP exception
                    exc = HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Request body too large"
                    )
                    # Return error response
                    return await self._handle_error(exc, send)
            except ValueError:
                pass
        
        # Process the request
        return await self.app(scope, receive, send)
        
    async def _handle_error(self, exc: HTTPException, send):
        """
        Handle HTTP exceptions by returning appropriate response
        
        Args:
            exc: HTTPException to handle
            send: ASGI send function
        """
        from starlette.responses import JSONResponse
        
        # Create JSON response from exception
        response = JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
        
        # Send response headers
        await send({
            "type": "http.response.start",
            "status": exc.status_code,
            "headers": [
                (b"content-type", b"application/json")
            ]
        })
        
        # Send response body
        await send({
            "type": "http.response.body",
            "body": response.body
        })
        
        return