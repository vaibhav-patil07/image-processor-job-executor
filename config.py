import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Redis BullMQ consumer"""
    # Database configuration
    DB_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/image_processor')
    # Redis configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Queue configuration
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'image-processor')

    STORAGE_END_POINT = os.getenv('STORAGE_END_POINT', '')
    STORAGE_REGION = os.getenv('STORAGE_REGION', '')
    ACCESS_KEY = os.getenv('ACCESS_KEY', '')
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    STORAGE_BUCKET = os.getenv('STORAGE_BUCKET', '')
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Job processing configuration
    JOB_TIMEOUT = int(os.getenv('JOB_TIMEOUT', 30))  # seconds
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
