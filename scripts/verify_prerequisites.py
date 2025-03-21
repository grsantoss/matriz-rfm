"""Pre-deployment verification script."""

import sys
import os
import subprocess
import platform
import socket
import requests
import psycopg2
from typing import List, Tuple
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentVerifier:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.project_root = Path(__file__).parent.parent

    def verify_all(self) -> bool:
        """Run all verifications and return True if all critical checks pass."""
        checks = [
            self.verify_python_version,
            self.verify_required_files,
            self.verify_env_file,
            self.verify_docker,
            self.verify_ports,
            self.verify_database_connection,
            self.verify_openai_key,
            self.verify_directory_permissions,
            self.verify_dependencies
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f"Error in {check.__name__}: {str(e)}")

        self.display_results()
        return len(self.errors) == 0

    def verify_python_version(self):
        """Verify Python version meets requirements."""
        required_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < required_version:
            self.errors.append(
                f"Python version {required_version[0]}.{required_version[1]} or higher required. "
                f"Found version {current_version[0]}.{current_version[1]}"
            )

    def verify_required_files(self):
        """Verify all required files exist."""
        required_files = [
            ".env.template",
            "requirements.txt",
            "docker-compose.yml",
            "Dockerfile.api",
            "backend/main.py",
            "backend/database.py",
            "backend/models.py",
            "backend/schemas.py",
            "backend/security.py",
            "backend/utils/openai_client.py",
            "backend/utils/prompts.py",
            "alembic.ini",
            "alembic/env.py",
            "nginx/nginx.conf"
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.errors.append(f"Required file missing: {file_path}")

    def verify_env_file(self):
        """Verify environment variables configuration."""
        env_template_path = self.project_root / ".env.template"
        env_path = self.project_root / ".env"

        if not env_template_path.exists():
            self.errors.append(".env.template file missing")
            return

        if not env_path.exists():
            self.warnings.append(".env file not found. Will be created from template.")
            return

        required_vars = [
            "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME",
            "SECRET_KEY", "OPENAI_API_KEY", "ENVIRONMENT"
        ]

        env_vars = {}
        with open(env_path) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

        for var in required_vars:
            if var not in env_vars:
                self.errors.append(f"Missing required environment variable: {var}")
            elif not env_vars[var]:
                self.warnings.append(f"Empty environment variable: {var}")

    def verify_docker(self):
        """Verify Docker and Docker Compose installation and configuration."""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.errors.append("Docker or Docker Compose not installed properly")
        except FileNotFoundError:
            self.errors.append("Docker or Docker Compose not found in PATH")

    def verify_ports(self):
        """Verify required ports are available."""
        ports = [80, 443, 5432, 8000]
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("localhost", port))
            except socket.error:
                self.warnings.append(f"Port {port} is already in use")
            finally:
                sock.close()

    def verify_database_connection(self):
        """Verify database connection and permissions."""
        try:
            env_path = self.project_root / ".env"
            if not env_path.exists():
                self.errors.append("Cannot verify database: .env file missing")
                return

            # Read database configuration from .env
            db_config = {}
            with open(env_path) as f:
                for line in f:
                    if line.startswith('DB_'):
                        key, value = line.strip().split('=', 1)
                        db_config[key] = value

            conn = psycopg2.connect(
                dbname=db_config.get('DB_NAME', 'rfm_insights'),
                user=db_config.get('DB_USER', 'postgres'),
                password=db_config.get('DB_PASSWORD', ''),
                host=db_config.get('DB_HOST', 'localhost'),
                port=db_config.get('DB_PORT', '5432')
            )
            conn.close()
        except Exception as e:
            self.errors.append(f"Database connection failed: {str(e)}")

    def verify_openai_key(self):
        """Verify OpenAI API key is valid."""
        env_path = self.project_root / ".env"
        if not env_path.exists():
            self.errors.append("Cannot verify OpenAI key: .env file missing")
            return

        api_key = None
        with open(env_path) as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.strip().split('=', 1)[1]
                    break

        if not api_key:
            self.errors.append("OpenAI API key not found in .env file")
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers
            )
            if response.status_code != 200:
                self.errors.append("Invalid OpenAI API key")
        except Exception as e:
            self.errors.append(f"Failed to verify OpenAI API key: {str(e)}")

    def verify_directory_permissions(self):
        """Verify write permissions in required directories."""
        directories = [
            "uploads",
            "logs",
            "alembic/versions"
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True)
                except Exception as e:
                    self.errors.append(f"Cannot create directory {directory}: {str(e)}")
            
            try:
                test_file = dir_path / ".test"
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                self.errors.append(f"No write permission in {directory}: {str(e)}")

    def verify_dependencies(self):
        """Verify Python dependencies installation."""
        try:
            requirements_path = self.project_root / "requirements.txt"
            if not requirements_path.exists():
                self.errors.append("requirements.txt not found")
                return

            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.errors.append("Dependency conflicts found:")
                self.errors.extend(result.stdout.splitlines())
        except Exception as e:
            self.errors.append(f"Failed to verify dependencies: {str(e)}")

    def display_results(self):
        """Display verification results."""
        print("\n=== Deployment Verification Results ===\n")
        
        if self.errors:
            print("\nErrors (must be fixed):")
            for error in self.errors:
                print(f"❌ {error}")
        
        if self.warnings:
            print("\nWarnings (should be reviewed):")
            for warning in self.warnings:
                print(f"⚠️ {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed successfully!")

        print("\nVerification complete!")

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    success = verifier.verify_all()
    sys.exit(0 if success else 1) 