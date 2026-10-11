-- =========================================================
-- SQL ANALYTIC QUERIES - POSTGRESQL
-- Project: Global E-Commerce OLAP Dashboard
-- =========================================================

-- Problem 1: Profitability by category, segment, and region
SELECT
    c.region,
    c.country,
    c.customer_segment,
    p.product_category,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_sales) AS total_sales,
    SUM(o.profit) AS total_profit,
    ROUND((SUM(o.profit) / NULLIF(SUM(o.total_sales), 0)) * 100, 2) AS profit_margin_percent
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.region, c.country, c.customer_segment, p.product_category
ORDER BY total_profit DESC;

-- Problem 2: Monthly sales and profit trend
SELECT
    DATE_TRUNC('month', o.order_date)::date AS month,
    SUM(o.total_sales) AS total_sales,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    ROUND((SUM(o.profit) / NULLIF(SUM(o.total_sales), 0)) * 100, 2) AS profit_margin_percent
FROM orders o
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;

-- Problem 2: Best and worst products by selected period
SELECT
    p.product_category,
    p.product_name,
    SUM(o.total_sales) AS total_sales,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    ROUND((SUM(o.profit) / NULLIF(SUM(o.total_sales), 0)) * 100, 2) AS profit_margin_percent
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_category, p.product_name
ORDER BY total_profit DESC;

-- Problem 3: Base data for MongoDB cross-reference by order_id
SELECT
    o.order_id,
    o.order_date,
    c.region,
    c.country,
    c.customer_segment,
    p.product_category,
    p.product_name,
    o.quantity,
    p.unit_price,
    o.total_sales,
    o.profit,
    ROUND((o.profit / NULLIF(o.total_sales, 0)) * 100, 2) AS profit_margin_percent
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id;
