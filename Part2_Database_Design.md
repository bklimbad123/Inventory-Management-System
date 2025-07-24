# Part 2: Database Design

## 1. Schema (PostgreSQL-style DDL)

```sql
-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Warehouses
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name TEXT NOT NULL
);

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_bundle BOOLEAN DEFAULT FALSE
);

-- Bundled Products (junction)
CREATE TABLE product_bundles (
    bundle_id INT REFERENCES products(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    PRIMARY KEY(bundle_id, product_id)
);

-- Inventory
CREATE TABLE inventory (
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity INT NOT NULL,
    PRIMARY KEY(product_id, warehouse_id)
);

-- Inventory History
CREATE TABLE inventory_changes (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity_change INT NOT NULL,
    change_type TEXT CHECK (change_type IN ('sale', 'restock', 'adjustment')),
    change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    contact_email TEXT
);

-- Product-Supplier
CREATE TABLE product_suppliers (
    product_id INT REFERENCES products(id),
    supplier_id INT REFERENCES suppliers(id),
    PRIMARY KEY(product_id, supplier_id)
);
