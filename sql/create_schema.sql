-- Retail Auto Parts System - PostgreSQL schema
-- This script creates all tables and constraints based on the Django models.

DROP TABLE IF EXISTS returnitem CASCADE;
DROP TABLE IF EXISTS delivery CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS orderitem CASCADE;
DROP TABLE IF EXISTS customer_order CASCADE;
DROP TABLE IF EXISTS order_item CASCADE;
DROP TABLE IF EXISTS purchase_order CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS part CASCADE;
DROP TABLE IF EXISTS supplier CASCADE;
DROP TABLE IF EXISTS employee CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS store CASCADE;

CREATE TABLE store (
    store_id       SERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    phone          VARCHAR(20),
    address_line1  VARCHAR(255) NOT NULL,
    address_line2  VARCHAR(255),
    city           VARCHAR(100) NOT NULL,
    state          VARCHAR(50) NOT NULL,
    postal_code    VARCHAR(20) NOT NULL
);

CREATE INDEX store_city_state_idx ON store(city, state);

CREATE TABLE customer (
    customer_id    SERIAL PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    customer_email VARCHAR(254) NOT NULL UNIQUE,
    customer_phone VARCHAR(20),
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    username       VARCHAR(50) NOT NULL UNIQUE,
    password       VARCHAR(255) NOT NULL
);

CREATE INDEX customer_username_idx ON customer(username);
CREATE INDEX customer_email_idx ON customer(customer_email);

CREATE TABLE supplier (
    supplier_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    contact_email VARCHAR(254) NOT NULL,
    phone         VARCHAR(20),
    address       TEXT
);

CREATE INDEX supplier_name_idx ON supplier(name);

CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    store_id    INTEGER NOT NULL REFERENCES store(store_id) ON DELETE CASCADE,
    full_name   VARCHAR(100) NOT NULL,
    role        VARCHAR(50) NOT NULL,
    email       VARCHAR(254) NOT NULL UNIQUE,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL
);

CREATE INDEX employee_store_role_idx ON employee(store_id, role);
CREATE INDEX employee_username_idx ON employee(username);

CREATE TABLE part (
    part_id       SERIAL PRIMARY KEY,
    sku           VARCHAR(50) NOT NULL UNIQUE,
    name          VARCHAR(200) NOT NULL,
    category      VARCHAR(100) NOT NULL,
    condition     VARCHAR(20) NOT NULL,
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0.01),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0)
);

CREATE INDEX part_category_idx ON part(category);
CREATE INDEX part_name_idx ON part(name);

CREATE TABLE inventory (
    store_id         INTEGER NOT NULL REFERENCES store(store_id) ON DELETE CASCADE,
    part_id          INTEGER NOT NULL REFERENCES part(part_id) ON DELETE CASCADE,
    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    PRIMARY KEY (store_id, part_id)
);

CREATE INDEX inventory_qty_idx ON inventory(quantity_on_hand);

CREATE TABLE purchase_order (
    po_id         SERIAL PRIMARY KEY,
    store_id      INTEGER NOT NULL REFERENCES store(store_id) ON DELETE CASCADE,
    supplier_id   INTEGER NOT NULL REFERENCES supplier(supplier_id) ON DELETE CASCADE,
    order_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_date DATE NOT NULL,
    status        VARCHAR(20) NOT NULL
        CHECK (status IN ('PENDING','APPROVED','RECEIVED','CANCELLED'))
);

CREATE INDEX po_status_orderdate_idx ON purchase_order(status, order_date);
CREATE INDEX po_store_status_idx ON purchase_order(store_id, status);

CREATE TABLE order_item (
    id                SERIAL PRIMARY KEY,
    purchase_order_id INTEGER NOT NULL REFERENCES purchase_order(po_id) ON DELETE CASCADE,
    part_id           INTEGER NOT NULL REFERENCES part(part_id),
    quantity          INTEGER NOT NULL CHECK (quantity >= 1),
    unit_cost         NUMERIC(10,2) NOT NULL CHECK (unit_cost >= 0.01),
    UNIQUE (purchase_order_id, part_id)
);

CREATE TABLE customer_order (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(customer_id) ON DELETE CASCADE,
    store_id    INTEGER NOT NULL REFERENCES store(store_id) ON DELETE CASCADE,
    order_date  TIMESTAMP NOT NULL DEFAULT NOW(),
    status      VARCHAR(20) NOT NULL
        CHECK (status IN ('PENDING','PROCESSING','SHIPPED','DELIVERED','CANCELLED'))
);

CREATE INDEX customer_order_customer_date_idx ON customer_order(customer_id, order_date);
CREATE INDEX customer_order_status_idx ON customer_order(status);

CREATE TABLE orderitem (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES customer_order(order_id) ON DELETE CASCADE,
    part_id    INTEGER NOT NULL REFERENCES part(part_id),
    quantity   INTEGER NOT NULL CHECK (quantity >= 1),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0.01),
    UNIQUE (order_id, part_id)
);

CREATE TABLE payment (
    payment_id        SERIAL PRIMARY KEY,
    order_id          INTEGER NOT NULL UNIQUE REFERENCES customer_order(order_id) ON DELETE CASCADE,
    payment_method    VARCHAR(20) NOT NULL
        CHECK (payment_method IN ('CREDIT_CARD','DEBIT_CARD','PAYPAL')),
    amount            NUMERIC(10,2) NOT NULL CHECK (amount >= 0.01),
    paid_date         TIMESTAMP NOT NULL DEFAULT NOW(),
    card_last_four_digit VARCHAR(4),
    authentication_code  VARCHAR(100) NOT NULL
);

CREATE INDEX payment_paid_date_idx ON payment(paid_date);

CREATE TABLE delivery (
    delivery_id     SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL UNIQUE REFERENCES customer_order(order_id) ON DELETE CASCADE,
    ship_date       DATE,
    delivery_date   DATE,
    employee_id     INTEGER REFERENCES employee(employee_id),
    tracking_number VARCHAR(100) NOT NULL UNIQUE,
    delivery_status VARCHAR(20) NOT NULL
        CHECK (delivery_status IN ('PREPARING','SHIPPED','IN_TRANSIT','DELIVERED','FAILED'))
);

CREATE INDEX delivery_tracking_idx ON delivery(tracking_number);
CREATE INDEX delivery_status_idx ON delivery(delivery_status);

CREATE TABLE returnitem (
    return_id    SERIAL PRIMARY KEY,
    order_id     INTEGER NOT NULL REFERENCES customer_order(order_id) ON DELETE CASCADE,
    part_id      INTEGER NOT NULL REFERENCES part(part_id),
    quantity     INTEGER NOT NULL CHECK (quantity >= 1),
    reason       TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX returnitem_created_idx ON returnitem(created_date);