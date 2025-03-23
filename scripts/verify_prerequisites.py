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
import urllib.parse
import time
import shutil

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
            self.verify_database_schema,
            self.verify_user_creation,
            self.verify_openai_key,
            self.verify_directory_permissions,
            self.verify_dependencies,
            self.verify_network_connectivity,
            self.verify_file_upload
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
            self.warnings.append(".env file not found. Creating from template.")
            try:
                # Create .env from template
                shutil.copy(env_template_path, env_path)
                logger.info("Created .env file from template. Please update with your settings.")
            except Exception as e:
                self.errors.append(f"Failed to create .env file: {str(e)}")
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
            
            # Check if Docker is running
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode != 0:
                self.errors.append("Docker daemon is not running. Please start Docker service.")
                return
                
            # Check if user has Docker permissions
            try:
                subprocess.run(["docker", "ps"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                self.errors.append("Current user doesn't have permission to use Docker. Try using sudo or add user to docker group.")
                
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
            
            # Check database permissions
            cursor = conn.cursor()
            cursor.execute("SELECT current_user")
            current_user = cursor.fetchone()[0]
            
            # Check if user has necessary permissions
            cursor.execute("""
                SELECT * FROM information_schema.role_table_grants 
                WHERE grantee = %s AND privilege_type = 'INSERT'
            """, (current_user,))
            
            if cursor.rowcount == 0:
                self.warnings.append(f"Database user {current_user} may not have sufficient permissions")
                
            cursor.close()
            conn.close()
        except Exception as e:
            self.errors.append(f"Database connection failed: {str(e)}")
            # Try to create database if it doesn't exist
            if "does not exist" in str(e):
                try:
                    self.create_database(db_config)
                except Exception as create_e:
                    self.errors.append(f"Failed to create database: {str(create_e)}")
    
    def create_database(self, db_config):
        """Create database if it doesn't exist."""
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=db_config.get('DB_USER', 'postgres'),
                password=db_config.get('DB_PASSWORD', ''),
                host=db_config.get('DB_HOST', 'localhost'),
                port=db_config.get('DB_PORT', '5432')
            )
            conn.autocommit = True
            cursor = conn.cursor()
            db_name = db_config.get('DB_NAME', 'rfm_insights')
            cursor.execute(f"CREATE DATABASE {db_name}")
            cursor.close()
            conn.close()
            logger.info(f"Created database {db_name}")
        except Exception as e:
            raise Exception(f"Failed to create database: {str(e)}")
    
    def verify_database_schema(self):
        """Verify database schema is properly set up."""
        try:
            env_path = self.project_root / ".env"
            if not env_path.exists():
                self.errors.append("Cannot verify database schema: .env file missing")
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
            cursor = conn.cursor()
            
            # Check if alembic_version table exists
            cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'alembic_version'
                )
            """)
            alembic_exists = cursor.fetchone()[0]
            
            if not alembic_exists:
                self.errors.append("Database schema hasn't been initialized with Alembic migrations")
                cursor.close()
                conn.close()
                return
            
            # Check essential tables
            essential_tables = ['users', 'analysis_results', 'rfm_segments']
            for table in essential_tables:
                cursor.execute(f"""
                    SELECT EXISTS (
                       SELECT FROM information_schema.tables 
                       WHERE table_name = '{table}'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    self.errors.append(f"Essential table '{table}' doesn't exist in the database")
            
            cursor.close()
            conn.close()
        except Exception as e:
            self.errors.append(f"Failed to verify database schema: {str(e)}")
    
    def verify_user_creation(self):
        """Verify that an admin user can be created in the database."""
        try:
            # First check if the users table exists
            env_path = self.project_root / ".env"
            if not env_path.exists():
                self.errors.append("Cannot verify user creation: .env file missing")
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
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'users'
                )
            """)
            users_table_exists = cursor.fetchone()[0]
            
            if not users_table_exists:
                self.warnings.append("Users table doesn't exist. Run migrations first.")
                cursor.close()
                conn.close()
                return
            
            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE email = 'admin@rfminsights.com'")
            admin_exists = cursor.rowcount > 0
            
            if not admin_exists:
                self.warnings.append("Admin user doesn't exist. It will be created during deployment.")
            
            cursor.close()
            conn.close()
            
            # Test user login via API if it's running
            try:
                login_url = "http://localhost:8000/auth/token"
                response = requests.post(
                    login_url,
                    data={
                        "username": "admin@rfminsights.com",
                        "password": "admin"  # Default password from .env
                    },
                    timeout=5
                )
                
                if response.status_code != 200:
                    self.warnings.append("Admin user login not working. Check API and credentials.")
            except requests.RequestException:
                self.warnings.append("Couldn't test user login via API. API may not be running.")
            
        except Exception as e:
            self.errors.append(f"Failed to verify user creation: {str(e)}")

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
                headers=headers,
                timeout=10
            )
            if response.status_code != 200:
                self.errors.append("Invalid OpenAI API key")
            
            # Check if GPT-4 or GPT-3.5 is available
            if response.status_code == 200:
                models = response.json().get("data", [])
                model_ids = [model.get("id") for model in models]
                
                required_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
                available_models = [model for model in required_models if any(model in model_id for model_id in model_ids)]
                
                if not available_models:
                    self.warnings.append("Required OpenAI models (GPT-4 or GPT-3.5) not available for this API key")
                    
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
                    logger.info(f"Created directory: {directory}")
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
                
            # Check for specific required packages
            essential_packages = ["fastapi", "sqlalchemy", "alembic", "psycopg2", "python-jose", "openai"]
            for package in essential_packages:
                try:
                    __import__(package)
                except ImportError:
                    self.errors.append(f"Essential package '{package}' is not installed")
        except Exception as e:
            self.errors.append(f"Failed to verify dependencies: {str(e)}")
    
    def verify_network_connectivity(self):
        """Verify network connectivity to external services."""
        external_services = [
            ("api.openai.com", 443),
            ("github.com", 443),
            ("pypi.org", 443)
        ]
        
        for host, port in external_services:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))
                sock.close()
            except socket.error:
                self.warnings.append(f"Cannot connect to {host}:{port}. Check your network/firewall settings.")
    
    def verify_file_upload(self):
        """Verify file upload functionality."""
        uploads_dir = self.project_root / "uploads"
        if not uploads_dir.exists():
            try:
                uploads_dir.mkdir(parents=True)
            except Exception as e:
                self.errors.append(f"Cannot create uploads directory: {str(e)}")
                return
        
        # Check if we can write a test file
        test_file = uploads_dir / "test_upload.csv"
        try:
            with open(test_file, 'w') as f:
                f.write("test,data\n1,2\n")
            
            # Check if we can read it back
            with open(test_file, 'r') as f:
                content = f.read()
                if "test,data" not in content:
                    self.errors.append("File upload test failed: could not read test file")
            
            # Clean up
            test_file.unlink()
        except Exception as e:
            self.errors.append(f"File upload test failed: {str(e)}")

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
        
        # Display summary with progress percentage
        total_checks = len(self.verify_all.__defaults__[0])
        passed_checks = total_checks - len(self.errors)
        progress_percent = (passed_checks / total_checks) * 100
        
        print(f"\nVerification progress: {passed_checks}/{total_checks} checks passed ({progress_percent:.1f}%)")
        print("\nVerification complete!")

        # Print next steps based on results
        if self.errors:
            print("\nNext steps to fix errors:")
            if any("Docker" in error for error in self.errors):
                print("1. Install Docker and Docker Compose")
                print("   Windows: https://docs.docker.com/desktop/install/windows-install/")
                print("   Linux: https://docs.docker.com/engine/install/")
            
            if any("database" in error.lower() for error in self.errors):
                print("1. Ensure PostgreSQL is installed and running")
                print("2. Create the database: createdb -U postgres rfm_insights")
                print("3. Check database credentials in .env file")
            
            if any("OpenAI" in error for error in self.errors):
                print("1. Get a valid OpenAI API key from https://platform.openai.com/")
                print("2. Add it to your .env file as OPENAI_API_KEY=your-key-here")
                
            if any("permission" in error.lower() for error in self.errors):
                print("1. Ensure you have write permissions to project directories")
                print("2. On Windows, run as Administrator")
                print("3. On Linux, check directory ownership: sudo chown -R $USER:$USER ./")

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    success = verifier.verify_all()
    sys.exit(0 if success else 1) 