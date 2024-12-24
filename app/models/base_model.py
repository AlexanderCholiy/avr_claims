import os
import imaplib
import email
import shutil
import warnings
from datetime import datetime
from typing import Optional

import pandas as pd
from contextlib import contextmanager
from colorama import init, Fore, Style

from database.db_conn import sql_queries
from database.requests.update_tickets import request_update_tickets
from database.requests.update_tickets_statuses import (
    request_update_tickets_statuses
)
from database.requests.update_tickets_constants import (
    request_tickets_constants_update
)


init(autoreset=True)
warnings.filterwarnings("ignore", category=UserWarning)
CURRENT_DIR: str = os.path.dirname(__file__)
BASE_DIR: str = os.path.join(CURRENT_DIR, '..', '..', 'data')


class AVR:
    def __init__(self, user_email: str, user_pswd: str, email_server: str):
        self.user_email: str = user_email
        self.user_pswd: str = user_pswd
        self.email_server: str = email_server
        self.archive_folder_dir: str = os.path.join(
            BASE_DIR, user_email, 'archive'
        )
        self.inbox_folder_dir: str = os.path.join(
            BASE_DIR, user_email, 'inbox'
        )
        self.sender_email: str = 'sapbo@megafon.ru'
        os.makedirs(self.archive_folder_dir, exist_ok=True)
        os.makedirs(self.inbox_folder_dir, exist_ok=True)

    @property
    def find_last_archive_file_data(self) -> datetime:
        files: list[str] = os.listdir(self.archive_folder_dir)

        if not files:
            return datetime.now()

        last_date = sorted(files)[-1].replace('.xlsx', '')
        return datetime.strptime(last_date, '%Y-%m-%d-%H-%M-%S')

    @contextmanager
    def open_connection(self):
        """Контекстный менеджер для подключения к IMAP-серверу."""
        mail = imaplib.IMAP4_SSL(self.email_server)
        try:
            mail.login(self.user_email, self.user_pswd)
            yield mail
        finally:
            mail.logout()

    def download_new_files(self):
        with self.open_connection() as mail:
            mail.select('inbox')
            since_date = (
                self.find_last_archive_file_data.strftime('%d-%b-%Y')
            )
            _, data = mail.search(
                None, '(FROM "{}" SINCE {})'.format(
                    self.sender_email, since_date
                )
            )

            for num in data[0].split():
                _, data = mail.fetch(num, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                if msg.get_content_maintype() == 'multipart':
                    for part in msg.walk():
                        filename = part.get_filename()
                        if filename:
                            filepath = os.path.join(
                                self.archive_folder_dir, filename
                            )
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))

    def prepare_new_files(self) -> bool:
        """
        Return:
        ------
        bool:
            True если найдены новые файлы, иначе False.
        """
        inbox_files: list[str] = os.listdir(self.inbox_folder_dir)
        archive_files: list[str] = os.listdir(self.archive_folder_dir)
        if not inbox_files:
            shutil.copyfile(
                os.path.join(
                    self.archive_folder_dir, sorted(archive_files)[-1]
                ),
                os.path.join(self.inbox_folder_dir, sorted(archive_files)[-1])
            )
            return True
        else:
            last_inbox_file = (
                datetime.strptime(
                    sorted(inbox_files)[-1].replace('.xlsx', ''),
                    '%Y-%m-%d-%H-%M-%S'
                )
            )
            newer_files = [
                file for file in archive_files if datetime.strptime(
                    file.split('.')[0], '%Y-%m-%d-%H-%M-%S'
                ) > last_inbox_file
            ]

            for inbox_file in inbox_files:
                if last_inbox_file != datetime.strptime(
                    inbox_file.replace('.xlsx', ''), '%Y-%m-%d-%H-%M-%S'
                ):
                    file_path = os.path.join(self.inbox_folder_dir, inbox_file)
                    os.remove(file_path)

            for newer_file in newer_files:
                shutil.copyfile(
                    os.path.join(self.archive_folder_dir, newer_file),
                    os.path.join(self.inbox_folder_dir, newer_file)
                )

            return bool(newer_files)

    def prepare_avr_df(self) -> pd.DataFrame:
        df = pd.DataFrame()
        for file in os.listdir(self.inbox_folder_dir):
            new_df: pd.DataFrame = pd.read_excel(
                os.path.join(self.inbox_folder_dir, file)
            )
            new_df['Файл'] = file
            df = pd.concat([df, new_df], ignore_index=True)

        return df

    def update_avr_db(self):
        df = self.prepare_avr_df()

        def replace_quotes(value):
            if isinstance(value, str):
                value = (
                    value.replace("'", '"').replace("«", '"').replace("»", '"')
                )
                value = value if value != ' ' else None
            return value

        df = df.apply(
            lambda col: col.apply(
                replace_quotes
            ) if col.dtype == 'object' else col
        )

        df = df.where(pd.notna(df), None)

        for index, row in df.iterrows():
            file_name: str = row['Файл']
            ticket: str = row['Код']
            status: Optional[str] = row['Статус']
            subdivision: Optional[str] = row['Подразделение']
            title: Optional[str] = row['Заголовок']
            description: Optional[str] = row['Описание']
            object_cipher: Optional[str] = row['Шифр объекта']
            internal_cipher: Optional[str] = row['Внутренний шифр']
            base_station_number: Optional[str] = row['Номер базовой станции']
            telecommunications_operator: Optional[str] = row['Оператор связи']
            standard_registration_time: Optional[str] = (
                row['Нормативное время регистрации']
            )
            standard_localization_time: Optional[str] = (
                row['Нормативное время локализации']
            )
            standard_time_for_eliminating_AVR: Optional[str] = (
                row['Нормативное время Устранения АВР']
            )
            standard_time_elimination_of_RVR: Optional[str] = (
                row['Нормативное время Устранения РВР']
            )
            branch: Optional[str] = row['Филиал']
            region: Optional[str] = row['Регион']
            facility_address: Optional[str] = row['Адрес объекта']
            contractor: Optional[str] = row['Подрядчик']
            registration_method: Optional[str] = row['Способ регистрации']
            availability_of_departure: Optional[str] = row['Наличие выезда']
            latitude: Optional[float] = row['Широта']
            longitude: Optional[float] = row['Долгота']
            time_of_occurrence: Optional[datetime] = (
                row['Время возникновения'] if pd.notna(
                    row['Время возникновения']
                ) else None
            )
            planned_elimination_time: Optional[datetime] = (
                row['Плановое время устранения'] if pd.notna(
                    row['Плановое время устранения']
                ) else None
            )
            registration_time: Optional[datetime] = (
                row['Время регистрации'] if pd.notna(
                    row['Время регистрации']
                ) else None
            )

            date_and_time: datetime = (
                datetime.strptime(
                    file_name.replace('.xlsx', ''), '%Y-%m-%d-%H-%M-%S'
                )
            )

            sql_queries(
                request_update_tickets(
                    ticket, self.sender_email, self.user_email
                )
            )

            if status:
                sql_queries(
                    request_update_tickets_statuses(
                        ticket, status, date_and_time
                    )
                )

            def constants_update_funk(
                ticket: str,
                constant_type_id: int,
                constant_value: str,
                date_and_time: str
            ):
                if constant_value:
                    sql_queries(
                        request_tickets_constants_update(
                            ticket,
                            constant_type_id,
                            constant_value,
                            date_and_time
                        )
                    )

            constants_update_funk(ticket, 1, subdivision, date_and_time)
            constants_update_funk(ticket, 2, title, date_and_time)
            constants_update_funk(ticket, 3, description, date_and_time)
            constants_update_funk(ticket, 4, object_cipher, date_and_time)
            constants_update_funk(ticket, 5, internal_cipher, date_and_time)
            constants_update_funk(
                ticket, 6, base_station_number, date_and_time
            )
            constants_update_funk(
                ticket, 7, telecommunications_operator, date_and_time
            )
            constants_update_funk(ticket, 8, time_of_occurrence, date_and_time)
            constants_update_funk(
                ticket, 9, planned_elimination_time, date_and_time
            )
            constants_update_funk(
                ticket, 10, standard_registration_time, date_and_time
            )
            constants_update_funk(
                ticket, 11, standard_localization_time, date_and_time
            )
            constants_update_funk(
                ticket, 12, standard_time_for_eliminating_AVR, date_and_time
            )
            constants_update_funk(
                ticket, 13, standard_time_elimination_of_RVR, date_and_time
            )
            constants_update_funk(ticket, 14, registration_time, date_and_time)
            constants_update_funk(ticket, 15, longitude, date_and_time)
            constants_update_funk(ticket, 16, latitude, date_and_time)
            constants_update_funk(ticket, 17, branch, date_and_time)
            constants_update_funk(ticket, 18, region, date_and_time)
            constants_update_funk(ticket, 19, facility_address, date_and_time)
            constants_update_funk(ticket, 20, contractor, date_and_time)
            constants_update_funk(
                ticket, 21, registration_method, date_and_time
            )
            constants_update_funk(
                ticket, 22, availability_of_departure, date_and_time
            )
            constants_update_funk(ticket, 23, file_name, date_and_time)

            print(
                Fore.CYAN + Style.DIM +
                'Загрузка заявок для АВР' +
                ' — ' +
                Style.RESET_ALL + Fore.WHITE + Style.BRIGHT +
                f'{(round(100*(index + 1)/len(df), 2))}%',
                end='\r'
            )

        print()
