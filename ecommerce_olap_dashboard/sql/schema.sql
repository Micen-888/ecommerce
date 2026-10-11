DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(120) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    country VARCHAR(80) NOT NULL,
    region VARCHAR(80) NOT NULL,
    UNIQUE (customer_name, customer_segment, country, region)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_category VARCHAR(80) NOT NULL,
    product_name VARCHAR(160) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    UNIQUE (product_category, product_name, unit_price)
);

CREATE TABLE orders (
    order_id VARCHAR(30) PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    total_sales NUMERIC(14, 2) NOT NULL,
    profit NUMERIC(14, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product_id ON orders(product_id);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_products_category ON products(product_category);
