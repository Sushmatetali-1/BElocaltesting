-- Sample data for testing authentication and permissions
-- Run this script after creating your database tables

-- 1. Insert customers
INSERT INTO customer (customer_id, name, address, phone)
VALUES
(1001, 'Acme Corp',         '123 Elm Street, Springfield',      '+1-555-0101'),
(1002, 'Globex Inc',        '456 Oak Ave, Metropolis',          '+1-555-0102'),
(1003, 'Initech',           '789 Maple Dr, Gotham',             '+1-555-0103'),
(1004, 'Umbrella Corp',     '321 Pine Lane, Raccoon City',      '+1-555-0104'),
(1005, 'Vandelay Industries','777 Walnut St, New York',         '+1-555-0105'),
(1006, 'Wonka Industries',  '1 Candy Lane, London',             '+44-555-0106'),
(1007, 'Stark Industries',  '10880 Malibu Point, Malibu',       '+1-555-0107'),
(1008, 'Wayne Enterprises', '1007 Mountain Dr, Gotham',         '+1-555-0108'),
(1009, 'Hooli',             '1 Silicon Valley Rd, Palo Alto',   '+1-555-0109'),
(1010, 'Cyberdyne Systems', '2029 Skynet Ave, Los Angeles',     '+1-555-0110');

-- 2. Insert user_type (Simplified to 2 types only)
INSERT INTO user_type (user_type_id, user_type, description)
VALUES
(1, 'Admin',         'Administrator with full system privileges - can create, update, delete users'),
(2, 'Regular User',  'Regular user with limited privileges - can only list and search users');

-- 3. Insert role_types (Simplified to match 2-tier user system)
INSERT INTO role_types (role_id, role_name, description)
VALUES
(1, 'Admin', 'Full system privileges - can create, update, delete users'),
(2, 'User',  'Limited privileges - can only list and search users');

-- 4. Insert customer_apps
INSERT INTO customer_apps (app_id, customer_id, title, description)
VALUES
(501, 1001, 'Acme CRM',          'CRM App for Acme'),
(502, 1002, 'Globex Analytics',  'Analytics platform for Globex'),
(503, 1003, 'Initech Support',   'Support app for Initech'),
(504, 1004, 'Umbrella Portal',   'Employee portal for Umbrella'),
(505, 1005, 'Vandelay Sales',    'Sales management app for Vandelay'),
(506, 1006, 'Wonka Factory',     'Wonka production management'),
(507, 1007, 'Stark ERP',         'ERP for Stark Industries'),
(508, 1008, 'Wayne Security',    'Security systems for Wayne'),
(509, 1009, 'Hooli HR',          'HR systems for Hooli'),
(510, 1010, 'Cyberdyne AI',      'AI management for Cyberdyne');

-- 5. Insert users (passwords are hashed with SHA256 - password is 'password123' for all)
-- Updated to use only 2 user types: Admin (1) and Regular User (2)
INSERT INTO user (user_id, user_type_id, customer_id, email, password_hash, username, department, name, contact_info)
VALUES
-- Admin users (user_type_id = 1)
(2001, 1, 1001, 'admin1@acme.com',      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'acmeadmin',   'IT',        'Alice Admin',    '555-111-1001'),
(2002, 1, 1007, 'admin2@stark.com',     'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'starkadmin',  'IT',        'Tony Admin',     '555-111-1007'),

-- Regular users (user_type_id = 2) 
(2003, 2, 1002, 'manager1@globex.com',  'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'globexmgr',   'Sales',     'Bob Manager',    '555-111-1002'),
(2004, 2, 1003, 'support1@initech.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'initechsup',  'Support',   'Charlie Support','555-111-1003'),
(2005, 2, 1004, 'user1@umbrella.com',   'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'umbrellauser','Research',  'Dana User',      '555-111-1004'),
(2006, 2, 1005, 'analyst@vandelay.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'vandelyana',  'Analytics', 'Eve Analyst',    '555-111-1005'),
(2007, 2, 1006, 'user2@wonka.com',      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'wonkauser',   'Production','Frank User',     '555-111-1006'),
(2008, 2, 1008, 'user3@wayne.com',      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'wayneuser',   'Security',  'Bruce User',     '555-111-1008'),
(2009, 2, 1009, 'user4@hooli.com',      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'hooliuser',   'Engineering','Dinesh User',    '555-111-1009'),
(2010, 2, 1010, 'user5@cyberdyne.com',  'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'cyberuser',   'AI Research','Sarah User',     '555-111-1010');

-- 6. Insert user_access
INSERT INTO user_access (user_id, app_id, customer_id)
VALUES
(2001, 501, 1001),
(2002, 502, 1002),
(2003, 503, 1003),
(2004, 504, 1004),
(2005, 505, 1005),
(2006, 506, 1006),
(2007, 507, 1007),
(2008, 508, 1008),
(2009, 509, 1009),
(2010, 510, 1010);

-- 7. Insert config
INSERT INTO config (config_id, customer_id, app_id, item, value, faq_questions)
VALUES
(301, 1001, 501, 'theme',     'dark',          'How to change theme?'),
(302, 1002, 502, 'timezone',  'UTC+1',         'How do I set my timezone?'),
(303, 1003, 503, 'max_users', '100',           'What is the max number of users?'),
(304, 1004, 504, 'support',   'contact@email.com', 'Who do I contact for support?'),
(305, 1005, 505, 'currency',  'USD',           'How to set default currency?'),
(306, 1006, 506, 'language',  'en-GB',         'How to change language?'),
(307, 1007, 507, 'region',    'US',            'How do I change my region?'),
(308, 1008, 508, 'backup',    'daily',         'How frequent are backups?'),
(309, 1009, 509, 'alerts',    'enabled',       'How to enable/disable alerts?'),
(310, 1010, 510, 'api_key',   'abc123xyz',     'Where can I find my API key?');
