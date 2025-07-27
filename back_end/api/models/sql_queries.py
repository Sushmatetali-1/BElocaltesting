"""
sql_queries.py
---------------
Stores raw SQL queries used for CRUD operations on user data:
- Select, insert, update, delete, and search queries.
"""


USER_QUERIES = {
    "list_base": """
        SELECT * FROM user
    """,
    "search": """
        SELECT * FROM user
        WHERE email LIKE :query OR username LIKE :query OR name LIKE :query
    """,
    "get_by_id": """
        SELECT * FROM user WHERE user_id = :user_id
    """,
    "create": """
        INSERT INTO user (
            user_id, user_type_id, customer_id, email, password_hash,
            username, department, name, contact_info, is_active,
            created_at, updated_at
        ) VALUES (
            :user_id, :user_type_id, :customer_id, :email, :password_hash,
            :username, :department, :name, :contact_info, TRUE,
            NOW(), NOW()
        )
    """,
    "update_base": """
        UPDATE user SET {fields}, updated_at = NOW() WHERE user_id = :user_id
    """,
    "delete": """
        DELETE FROM user WHERE user_id = :user_id
    """
}
