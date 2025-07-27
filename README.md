### Software - python,pycharm,mysql workbench,postman - download and setup in system for development and testing

### Expected API structure-

db/v1/api/user/create

db/v1/api/user/update

db/v1/api/user/delete

db/v1/api/user/search

db/v1/api/user/list

### API testing links -

return codes  add – standard api codes  - create a module to read the code and display in api along with output

http://127.0.0.1:5000/db/v1/api/user/list - give data of all users

http://127.0.0.1:5000/db/v1/api/user/40011  - current, updated info the department from HR to IT - instead of user_id we need to use(email/user_name/name) - this input field needs to be changed.

http://127.0.0.1:5000/db/v1/api/user/40010 - deleted the user from DB so we will get error message - - instead of user_id we need to use(email/user_name/name) - this input field needs to be changed.

http://127.0.0.1:5000/db/v1/api/version - check the version

http://127.0.0.1:5000/db/v1/api/health - API , DB health check- Debugging

http://127.0.0.1:5000/db/v1/api/user/search?q=newuser – pending -search any new user, existing user with column/features – pending - db/v1/api/user/search - if we have given any user info like email it should get the data

http://127.0.0.1:5000/db/v1/api/user/create – pending. - db/v1/api/user/create

http://127.0.0.1:5000/db/v1/api/user/update/40011 – check – pending – retrieve the only updated data? -- instead of user_id we need to use(email/user_name/name) - this field needs to be changed.

### Pending works for user module API -
1. add return codes 400,500,400 etc in api data return
2. API- create,search
3. instead of user_id , we need to use some columns like email/user_name/name for testing - as id,passwords and other stuff are handlled in BE DB level and are not visible at user leve
4. Admin, user level testing like changing ourself as admin and check how data appers at api level, similarly making ourself as user and check how can we test in api level.
   

### Table structure - 

you may need to add few rows of data for testing purpose.

CREATE TABLE customer (
 id INT AUTO_INCREMENT PRIMARY KEY,
 customer_id INT NOT NULL,
 name VARCHAR(255) NOT NULL,
 address VARCHAR(500),
 phone VARCHAR(50),
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
UNIQUE (customer_id)
);

CREATE TABLE `user` (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 user_type_id INT NOT NULL,
 customer_id INT NOT NULL,
 email VARCHAR(255) NOT NULL,
 password_hash VARCHAR(255) NOT NULL,
 username VARCHAR(100) NOT NULL,
 department VARCHAR(100),
 name VARCHAR(255) NOT NULL,
 contact_info VARCHAR(500),
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 is_active BOOLEAN DEFAULT TRUE,
 FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
 UNIQUE (user_id)
);

CREATE TABLE user_type (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_type_id INT NOT NULL,
 user_type VARCHAR(50) NOT NULL,
 description TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 UNIQUE (user_type_id)
);


CREATE TABLE user_access (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 app_id INT NOT NULL,
 customer_id INT NOT NULL,
 assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES user(user_id),
 FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE  customer_apps (
 id INT AUTO_INCREMENT PRIMARY KEY,
 app_id INT NOT NULL,
 customer_id INT NOT NULL,
 title VARCHAR(255) NOT NULL,
 description TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE config (
 id INT AUTO_INCREMENT PRIMARY KEY,
 config_id INT NOT NULL,
 customer_id INT NOT NULL,
 app_id INT NOT NULL,
 item VARCHAR(100) NOT NULL,
 value TEXT,
faq_questions VARCHAR(100) NOT NULL,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);


CREATE TABLE role_types (
 id INT AUTO_INCREMENT PRIMARY KEY,
 role_id INT NOT NULL,
 role_name VARCHAR(50) NOT NULL,
 description TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 UNIQUE (role_id)
);


