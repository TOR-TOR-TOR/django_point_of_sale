-- ============================================================
-- TICKET #001
-- Requested by : Sales Team
-- Date         : 2026-04-09
-- Description  : Full customer list for marketing campaign
-- Tables used  : Customers
-- ============================================================

SELECT 
    first_name,
    last_name,
    email,
    phone
FROM Customers
ORDER BY last_name ASC;



-- ============================================================
-- TICKET #002
-- Requested by : Management
-- Date         : 2026-04-09
-- Description  : Total sales count and overall revenue summary
-- Tables used  : Sales
-- ============================================================

SELECT
    COUNT(*) AS total_sales,
    SUM(grand_total) AS total_revenue,
    AVG(grand_total) AS average_transaction_value,
    MIN(grand_total) AS minimum_sales_value,
    MAX(grand_total) AS maximum_sales_value
FROM 
    sales;


SELECT *
FROM 
    CATEGORY
WHERE 
    STATUS = 'ACTIVE'
ORDER BY
    ID ASC;


SELECT 
    ID,
    PRICE,
    QUANTITY,
    SALE
FROM
    SALEDETAILS
WHERE
    sale = 2
ORDER BY
    ID ASC;


