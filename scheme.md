```mermaid
erDiagram
  CUSTOMER ||--o{ USER : "has"
  CUSTOMER ||--o{ CUSTOMER_APPS : "owns"
  CUSTOMER ||--o{ USER_ACCESS : "scopes"
  CUSTOMER ||--o{ CONFIG : "has"

  USER_TYPE ||--o{ USER : "categorizes"
  USER ||--o{ USER_ACCESS : "granted"

  CUSTOMER_APPS ||--o{ USER_ACCESS : "grants access to"
  CUSTOMER_APPS ||--o{ CONFIG : "configured by"

  CUSTOMER {
    int id PK
    int customer_id UK
    string name
    string address
    string phone
    datetime created_at
    datetime updated_at
  }

  USER_TYPE {
    int id PK
    int user_type_id UK
    string user_type
    string description
    datetime created_at
    datetime updated_at
  }

  USER {
    int id PK
    int user_id UK
    int user_type_id FK
    int customer_id FK
    string email
    string password_hash
    string username
    string department
    string name
    string contact_info
    datetime created_at
    datetime updated_at
    bool is_active
  }

  CUSTOMER_APPS {
    int id PK
    int app_id
    int customer_id FK
    string title
    text description
    text object_storage_location
    text temp_storage_location
    datetime created_at
  }

  USER_ACCESS {
    int id PK
    int user_id FK
    int app_id
    int customer_id FK
    datetime assigned_at
  }

  CONFIG {
    int id PK
    int config_id
    int customer_id FK
    int app_id
    string item
    text value
    string faq_questions
    datetime created_at
    datetime updated_at
  }

  ROLE_TYPES {
    int id PK
    int role_id UK
    string role_name
    text description
    datetime created_at
  }
