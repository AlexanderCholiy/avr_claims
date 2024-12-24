def request_update_tickets_statuses(
    ticket: str, status: str, date_and_time: str
) -> str:
    """Добавление уникальных статусов в statuses."""
    return (f"""
    INSERT INTO
        statuses (
            ticket_id,
            status,
            date_and_time
        )
    SELECT
        (SELECT ticket_id FROM tickets WHERE ticket = '{ticket}'),
        '{status}',
        '{date_and_time}'
    WHERE NOT EXISTS (
        SELECT 1 FROM statuses
        WHERE
            ticket_id = (
                SELECT ticket_id FROM tickets WHERE ticket = '{ticket}'
            )
            AND status = '{status}'
    );
    UPDATE
        statuses
    SET
        date_and_time = '{date_and_time}'
    WHERE
        ticket_id = (SELECT ticket_id FROM tickets WHERE ticket = '{ticket}')
        AND status = '{status}';
    """)
