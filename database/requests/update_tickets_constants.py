def request_tickets_constants_update(
    ticket: str, constant_type_id: int, constant_value, date_and_time
) -> str:
    """Обновление таблицы constants"""
    return (f"""
    INSERT INTO
        constants (
            ticket_id,
            constant_type_id,
            constant_value,
            date_and_time
        )
    SELECT (
        SELECT ticket_id FROM tickets WHERE ticket = '{ticket}'
    ),
    {constant_type_id},
    '{constant_value}',
    '{date_and_time}'
    WHERE NOT EXISTS (
        SELECT 1 FROM constants WHERE ticket_id = (
            SELECT ticket_id FROM tickets WHERE ticket = '{ticket}'
        )
        AND constant_type_id = {constant_type_id}
        AND constant_value = '{constant_value}'
    );
    """)
