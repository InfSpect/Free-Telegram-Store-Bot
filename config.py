import os
import logging
from dotenv import load_dotenv

load_dotenv('config.env')

class BotConfig:
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    STORE_CURRENCY = os.getenv('STORE_CURRENCY', 'USD')
    STORE_NAME = os.getenv('STORE_NAME', 'Rafay Store')

    DB_FILE = 'shop_data.json'
    DB_BACKUP_INTERVAL = 3600

    NOWPAYMENTS_API_BASE = 'https://api.nowpayments.io/v1'
    COINGECKO_API_BASE = 'https://api.coingecko.com/api/v3'

    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT = 3600

    MAX_FILE_SIZE = 10 * 1024 * 1024
    ALLOWED_FILE_TYPES = ['.txt', '.pdf', '.doc', '.docx']
    UPLOAD_FOLDER = 'uploads'
    KEYS_FOLDER = 'Keys'

    MAX_REQUESTS_PER_MINUTE = 30
    MAX_REQUESTS_PER_HOUR = 1000

    LOG_LEVEL = logging.INFO
    LOG_FILE = 'bot.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024
    LOG_BACKUP_COUNT = 5

    CACHE_TTL = 300
    CACHE_MAX_SIZE = 1000

    MAX_MESSAGE_LENGTH = 4096
    MAX_CAPTION_LENGTH = 1024

    MAX_PRODUCTS_PER_CATEGORY = 100
    MAX_CATEGORIES = 50
    MAX_PRODUCT_NAME_LENGTH = 100
    MAX_PRODUCT_DESCRIPTION_LENGTH = 1000
    
    # Order Settings
    ORDER_TIMEOUT = 1800  # 30 minutes
    MAX_ORDERS_PER_USER_PER_DAY = 10
    
    @classmethod
    def validate_config(cls):
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def get_db_url(cls):
        return cls.DB_FILE
    
    @classmethod
    def get_log_config(cls):
        return {
            'level': cls.LOG_LEVEL,
            'filename': cls.LOG_FILE,
            'maxBytes': cls.LOG_MAX_SIZE,
            'backupCount': cls.LOG_BACKUP_COUNT
        }

class APIConfig:
    NOWPAYMENTS_TIMEOUT = 30
    COINGECKO_TIMEOUT = 10

    NOWPAYMENTS_RATE_LIMIT = 100
    COINGECKO_RATE_LIMIT = 100

    MAX_RETRIES = 3
    RETRY_DELAY = 1

    @classmethod
    def get_headers(cls, api_key=None):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RafayBot/1.0'
        }

        if api_key:
            headers['x-api-key'] = api_key

        return headers

class SecurityConfig:
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    DANGEROUS_SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER',
        'EXEC', 'EXECUTE', 'SCRIPT', 'UNION', 'SELECT'
    ]

    DANGEROUS_HTML_TAGS = [
        '<script>', '</script>', '<iframe>', '</iframe>',
        '<object>', '</object>', '<embed>', '</embed>'
    ]

    DANGEROUS_FILE_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.jar', '.php', '.asp', '.aspx'
    ]

    @classmethod
    def is_safe_filename(cls, filename):
        import os

        _, ext = os.path.splitext(filename.lower())
        if ext in cls.DANGEROUS_FILE_EXTENSIONS:
            return False

        if '..' in filename or '/' in filename or '\\' in filename:
            return False

        return True

config = BotConfig()

try:
    config.validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    exit(1)