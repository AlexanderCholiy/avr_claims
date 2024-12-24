from datetime import datetime

from colorama import init, Fore, Style

from app.models.base_model import AVR
from settings.config import bot_email_settings
from app.common.log_timer import log_timer

init(autoreset=True)


@log_timer()
def run_avr():
    avr = AVR(
        bot_email_settings.BOT_EMAIL_LOGIN_1,
        bot_email_settings.BOT_EMAIL_PSWD_1,
        bot_email_settings.EMAIL_SERVER,
    )
    avr.download_new_files()
    if avr.prepare_new_files():
        avr.update_avr_db()


if __name__ == '__main__':
    start_time = datetime.now()
    print(Fore.MAGENTA + Style.BRIGHT + f'Запуск {__file__}')
    run_avr()
