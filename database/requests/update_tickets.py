def request_update_tickets(
    ticket: str, sender_email: str, user_login: str
) -> str:
    """Добавление новых заявок в tickets"""
    return (f"""
    INSERT INTO
        tickets (
            ticket,
            user_id
        )
    SELECT
        '{ticket}',
        (
            SELECT user_id
            FROM users
            WHERE
                user_name = '{sender_email}'
                AND user_login = '{user_login}'
        )
    WHERE NOT EXISTS (
        SELECT 1 FROM tickets WHERE ticket = '{ticket}'
    );
    """)
