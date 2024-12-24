import sys
import time
import schedule
import subprocess
import threading


def run_script(script_name):
    subprocess.run([sys.executable, script_name])


def schedule_script(script_name):
    # Запускаем скрипт каждые 3 часа:
    schedule.every(3).hours.do(
        lambda script=script_name: threading.Thread(
            target=run_script, args=(script,)
        ).start()
    )


def main():
    schedule_script('run_avr.py')

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
