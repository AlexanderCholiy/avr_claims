def update_relevant_status() -> str:
    """Выставляем актуальный статус заявкам."""
    return ("""
        -- Создаем временную таблицу для хранения последних статусов
        CREATE TEMP TABLE latest_statuses AS (
        SELECT
            ticket_id,
            MAX(date_and_time) AS last_date_and_time
        FROM statuses
        WHERE ticket_id IN (
            SELECT DISTINCT ticket_id
            FROM constants
            WHERE date_and_time IN (
            SELECT DISTINCT date_and_time
            FROM constants
            WHERE constant_type_id = 23
            ORDER BY date_and_time DESC
            LIMIT 4
            )
        )
        GROUP BY ticket_id
        );

        -- Сначала обновляем все записи на False
        UPDATE statuses
        SET is_status_relevant = False;

        -- Затем устанавливаем True только для последних статусов
        UPDATE statuses
        SET is_status_relevant = True
        WHERE (ticket_id, date_and_time) IN (
        SELECT ticket_id, last_date_and_time
        FROM latest_statuses
        );

        -- Удаляем временную таблицу после использования
        DROP TABLE latest_statuses;
    """)
