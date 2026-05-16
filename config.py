import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-super-secret-key-change-in-prod')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-super-secret-key-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24  # 1 day
    # Configure CORS if needed
    CORS_HEADERS = 'Content-Type'
