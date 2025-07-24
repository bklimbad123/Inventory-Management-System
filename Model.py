from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Company
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    warehouses = db.relationship('Warehouse', backref='company', lazy=True)

# Warehouse
class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    inventory = db.relationship('Inventory', backref='warehouse', lazy=True)

# Product
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sku = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    low_stock_threshold = db.Column(db.Integer, default=10)
    is_bundle = db.Column(db.Boolean, default=False)
    inventory = db.relationship('Inventory', backref='product', lazy=True)
    suppliers = db.relationship('Supplier', secondary='product_suppliers', backref='products')

# Inventory
class Inventory(db.Model):
    __tablename__ = 'inventory'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

# InventoryChange (History)
class InventoryChange(db.Model):
    __tablename__ = 'inventory_changes'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    quantity_change = db.Column(db.Integer, nullable=False)
    change_type = db.Column(db.String, nullable=False)
    change_time = db.Column(db.DateTime, default=datetime.utcnow)

# Supplier
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contact_email = db.Column(db.String)

# Many-to-many: Product <-> Supplier
product_suppliers = db.Table(
    'product_suppliers',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('supplier_id', db.Integer, db.ForeignKey('suppliers.id'), primary_key=True)
)

# Sales (used for low-stock analysis)
class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
