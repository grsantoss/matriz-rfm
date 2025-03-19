# RFM Insights

RFM Insights is a powerful customer segmentation and analysis platform that uses RFM (Recency, Frequency, Monetary) analysis to help businesses understand and target their customers effectively.

## Features

- **RFM Analysis**: Analyze your customer data using the RFM methodology
- **Customer Segmentation**: Automatically segment customers based on their purchasing behavior
- **Marketing Recommendations**: Get AI-powered recommendations for each customer segment
- **Message Generation**: Create targeted marketing messages for different segments
- **Integration**: Connect with your existing data sources

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **Containerization**: Docker and Docker Compose
- **Web Server**: Nginx

## Deployment Instructions

### Prerequisites

- Docker and Docker Compose installed
- Domain names configured (for production deployment)
- Git (optional)

### Local Deployment (Windows)

1. Make sure Docker Desktop for Windows is installed and running

2. Clone or download this repository

3. Open PowerShell as Administrator and navigate to the project directory

4. Run the Windows deployment script:
   ```powershell
   .\deploy-windows.ps1
   ```

5. Follow the on-screen instructions to complete the deployment

6. Access the application at:
   - Frontend: http://localhost
   - API: http://localhost:8000

### Production Deployment (Linux)

1. Make sure Docker and Docker Compose are installed

2. Ensure your domain names (app.rfminsights.com.br and api.rfminsights.com.br) are pointing to your server

3. Clone or download this repository

4. Navigate to the project directory and run the deployment script:
   ```bash
   sudo bash deploy.sh
   ```

5. Follow the on-screen instructions to complete the deployment

6. Access the application at:
   - Frontend: https://app.rfminsights.com.br
   - API: https://api.rfminsights.com.br

## Configuration

### Environment Variables

The application uses the following environment variables:

- `DATABASE_URL`: The PostgreSQL database connection URL
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `OPENAI_API_KEY`: API key for OpenAI integration
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: AWS credentials for email delivery

These variables can be configured in the `.env` file.

## Database

The application uses PostgreSQL for data storage. The database schema includes the following main tables:

- `users`: User accounts and authentication
- `rfm_analyses`: RFM analysis results and metadata
- `messages`: Marketing messages generated for customer segments
- `api_keys`: API keys for integration with other systems

The database is automatically initialized during deployment.

## Troubleshooting

If you encounter any issues during deployment:

1. Check the logs in the `logs/` directory
2. Verify that all required services are running:
   ```
   docker-compose ps
   ```
3. Ensure that the environment variables are correctly set in the `.env` file
4. Make sure ports 80, 443, and 8000 are not being used by other applications

## License

This software is proprietary and confidential.

## Support

For support, please contact support@rfminsights.com.br 