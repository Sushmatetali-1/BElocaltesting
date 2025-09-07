"""
Central store for raw SQL used by user routes (email-first design).
"""
USER_QUERIES = {
    # --- Reads ---
    "list_all": """
        SELECT user_id, user_type_id, customer_id, email, username, department,
               name, contact_info, is_active, created_at, updated_at
        FROM user
        ORDER BY created_at DESC
    """,
    "list_active": """
        SELECT user_id, user_type_id, customer_id, email, username, department,
               name, contact_info, is_active, created_at, updated_at
        FROM user
        WHERE is_active = TRUE
        ORDER BY created_at DESC
    """,
    # Scoped lists (by customer)
    "list_active_by_customer": """
        SELECT user_id, user_type_id, customer_id, email, username, department,
               name, contact_info, is_active, created_at, updated_at
        FROM user
        WHERE is_active = TRUE AND customer_id = :customer_id
        ORDER BY created_at DESC
    """,

    "get_by_id": "SELECT * FROM user WHERE user_id = :user_id",
    "get_by_email": "SELECT * FROM user WHERE email = :email",
    "get_by_email_scoped": """
        SELECT * FROM user WHERE email = :email AND customer_id = :customer_id
    """,

    # --- Search (name/username/email) ---
    "search": """
        SELECT user_id, user_type_id, customer_id, email, username, department,
               name, contact_info, is_active, created_at, updated_at
        FROM user
        WHERE (email LIKE :query OR username LIKE :query OR name LIKE :query)
        ORDER BY updated_at DESC
    """,
    "search_by_customer": """
        SELECT user_id, user_type_id, customer_id, email, username, department,
               name, contact_info, is_active, created_at, updated_at
        FROM user
        WHERE customer_id = :customer_id
          AND (email LIKE :query OR username LIKE :query OR name LIKE :query)
        ORDER BY updated_at DESC
    """,

    # --- Create ---
    "create_user": """
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
    "user_type_exists": "SELECT user_type_id FROM user_type WHERE user_type_id = :user_type_id",
    "email_exists":     "SELECT user_id FROM user WHERE email = :email",
    "username_exists":  "SELECT user_id FROM user WHERE username = :username",

    # --- Update (email is key) ---
    "update_by_email_base": """
        UPDATE user
        SET {fields}, updated_at = NOW()
        WHERE email = :email
    """,

    # --- Delete ---
    "hard_delete_by_email_scoped": """
        DELETE FROM user
        WHERE email = :email AND customer_id = :customer_id
    """,
}
