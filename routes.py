from flask import request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal

from models import db, Product, Inventory, Warehouse, Company, Supplier, Sale, product_suppliers

def register_routes(app):
    
    @app.route('/api/products', methods=['POST'])
    def create_product():
        data = request.get_json()

        required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return {"error": f"Missing fields: {', '.join(missing_fields)}"}, 400

        try:
            price = float(data['price'])
            initial_quantity = int(data['initial_quantity'])
        except ValueError:
            return {"error": "Invalid data types for price or quantity."}, 400

        if Product.query.filter_by(sku=data['sku']).first():
            return {"error": "SKU must be unique."}, 400

        try:
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=Decimal(price),
            )
            db.session.add(product)
            db.session.flush()

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=data['warehouse_id'],
                quantity=initial_quantity
            )
            db.session.add(inventory)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

        return {"message": "Product created", "product_id": product.id}, 201

    @app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
    def get_low_stock_alerts(company_id):
        try:
            recent_threshold = datetime.utcnow() - timedelta(days=30)

            recent_sales = (
                db.session.query(Sale.product_id)
                .join(Warehouse, Sale.warehouse_id == Warehouse.id)
                .filter(Warehouse.company_id == company_id)
                .filter(Sale.timestamp >= recent_threshold)
                .distinct()
                .subquery()
            )

            results = (
                db.session.query(
                    Product.id.label("product_id"),
                    Product.name.label("product_name"),
                    Product.sku,
                    Warehouse.id.label("warehouse_id"),
                    Warehouse.name.label("warehouse_name"),
                    Inventory.quantity.label("current_stock"),
                    Product.low_stock_threshold.label("threshold"),
                    Supplier.id.label("supplier_id"),
                    Supplier.name.label("supplier_name"),
                    Supplier.contact_email,
                    func.ceil(
                        Inventory.quantity / func.nullif(func.avg(Sale.quantity).over(partition_by=Inventory.product_id), 0)
                    ).label("days_until_stockout")
                )
                .join(Inventory, Inventory.product_id == Product.id)
                .join(Warehouse, Inventory.warehouse_id == Warehouse.id)
                .outerjoin(Sale, (Sale.product_id == Product.id) & (Sale.timestamp >= recent_threshold))
                .join(product_suppliers, product_suppliers.c.product_id == Product.id)
                .join(Supplier, Supplier.id == product_suppliers.c.supplier_id)
                .filter(Warehouse.company_id == company_id)
                .filter(Product.id.in_(recent_sales))
                .filter(Inventory.quantity < Product.low_stock_threshold)
                .group_by(Product.id, Warehouse.id, Inventory.quantity, Supplier.id)
            )

            alerts = []
            for row in results:
                alerts.append({
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "sku": row.sku,
                    "warehouse_id": row.warehouse_id,
                    "warehouse_name": row.warehouse_name,
                    "current_stock": row.current_stock,
                    "threshold": row.threshold,
                    "days_until_stockout": int(row.days_until_stockout or 0),
                    "supplier": {
                        "id": row.supplier_id,
                        "name": row.supplier_name,
                        "contact_email": row.contact_email
                    }
                })

            return jsonify({
                "alerts": alerts,
                "total_alerts": len(alerts)
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500
