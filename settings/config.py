import os

from dotenv import load_dotenv


CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
ENV_PATH: str = os.path.join(CURRENT_DIR, '.env')
load_dotenv(ENV_PATH)


class DB_SETTINGS:
    """Параметры подключения к БД."""
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = int(os.getenv('DB_PORT'))
    DB_USER: str = os.getenv('DB_USER')
    DB_PSWD: str = os.getenv('DB_PSWD')
    DB_NAME_TECH_PRIS: str = os.getenv('DB_NAME_TECH_PRIS')
    DB_NAME_AVR: str = os.getenv('DB_NAME_AVR')
    DB_NAME_WEB: str = os.getenv('DB_NAME_WEB')


class BOT_EMAIL_SETTINGS:
    """Почта бота."""
    EMAIL_SERVER: str = os.getenv("EMAIL_SERVER")
    BOT_EMAIL_LOGIN_1: str = os.getenv("BOT_EMAIL_LOGIN_1")
    BOT_EMAIL_PSWD_1: str = os.getenv("BOT_EMAIL_PSWD_1")


db_settings = DB_SETTINGS()
bot_email_settings = BOT_EMAIL_SETTINGS()
