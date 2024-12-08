# main.py
from collections import Counter
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Float, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from starlette import status

import models, schemas
from api.dependencies.database import Base
from database import engine, get_db

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=engine)


@app.post("/ingredients/", response_model=schemas.Ingredient, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    """
    Create a new ingredient.
    """
    db_ingredient = models.Ingredient(name=ingredient.name, quantity=ingredient.quantity)
    db.add(db_ingredient)
    try:
        db.commit()
        db.refresh(db_ingredient)
        return db_ingredient
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ingredient already exists.")



@app.get("/ingredients/", response_model=List[schemas.Ingredient], status_code=status.HTTP_200_OK)
def get_all_ingredients(db: Session = Depends(get_db)):
    """
    Retrieve a list of all ingredients.
    """
    # db.query(models.Ingredient).delete()  # Clear all rows
    # db.commit()
    #
    # with engine.connect() as connection:
    #     connection.execute(text("ALTER TABLE ingredients AUTO_INCREMENT = 1"))  # Reset auto-increment

    try:
        ingredients = db.query(models.Ingredient).all()  # Fetch all ingredients
        if not ingredients:
            raise HTTPException(status_code=404, detail="No ingredients found")
        return ingredients
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

@app.get("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """
    Update an existing Ingredient and its specific ingredients.
    """
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found.")

    return db_ingredient

@app.patch("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(ingredient_id: int, ingredient_update: schemas.IngredientUpdate, db: Session = Depends(get_db)):
    """
    Update an existing Ingredient and its specific ingredients.
    """
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found.")

    # Update product fields
    if ingredient_update.name is not None:
        db_ingredient.name = ingredient_update.name
    if ingredient_update.quantity is not None:
        db_ingredient.quantity = ingredient_update.quantity

    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@app.delete("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """
    Delete an ingredient by its ID.
    """
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found.")

    # Delete the ingredient
    db.delete(db_ingredient)
    db.commit()

    return db_ingredient  # Return the deleted ingredient for confirmation


@app.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new Product.
    """
    fixed_ingredients = [ingredient.dict() for ingredient in product.ingredients]
    db_product = models.Product(name=product.name,
                                price=product.price,
                                promotion=product.promotion,
                                dietary_type=product.dietary_type,
                                ingredients=fixed_ingredients)
    db.add(db_product)
    try:
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product already exists.")

@app.get("/products/", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def get_all_products(db: Session = Depends(get_db)):
    """
    Retrieve a list of all products.
    """
    # db.query(models.Product).delete()  # Clear all rows
    # db.commit()
    # #
    # with engine.connect() as connection:
    #     connection.execute(text("ALTER TABLE products AUTO_INCREMENT = 1"))  # Reset auto-increment

    try:
        products = db.query(models.Product).all()  # Fetch all ingredients
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        return products
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Update an existing Ingredient and its specific ingredients.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")

    return db_product

@app.patch("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """
    Update an existing product and its specific ingredients.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Update product fields
    if product_update.name is not None:
        db_product.name = product_update.name
    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.promotion is not None:
        db_product.promotion = product_update.promotion
    if product_update.dietary_type is not None:
        db_product.dietary_type = product_update.dietary_type
    if product_update.ingredients is not None:
        db_product.ingredients = product_update.ingredients


    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a Product by its ID.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Delete the product
    db.delete(db_product)
    db.commit()

    # Reset IDs
    # products = db.query(models.Product).order_by(models.Product.id).all()
    # for index, product in enumerate(products, start=1):
    #     product.id = index
    # db.commit()

    return db_product # Return the deleted product for confirmation


@app.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.CreateOrder, db: Session = Depends(get_db)):
    try:
        # Fetch products based on IDs
        products = db.query(models.Product).filter(models.Product.id.in_(order.product_ids)).all()

        if not products:
            raise HTTPException(status_code=404, detail="One or more products not found.")

        # Calculate the total required quantities of each ingredient
        required_ingredients = {}

        for product_id in order.product_ids:
            product = db.query(models.Product).filter(models.Product.id == product_id).first()
            for ingredient in product.ingredients:
                if ingredient["name"] not in required_ingredients:
                    required_ingredients[ingredient["name"]] = 0
                required_ingredients[ingredient["name"]] += ingredient["quantity"]

        # Check ingredient availability in the database
        for ingredient_name, required_quantity in required_ingredients.items():
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_name).first()
            if not ingredient or ingredient.quantity < required_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough of ingredient '{ingredient_name}' to fulfill the order. "
                           f"Required: {required_quantity}, Available: {ingredient.quantity if ingredient else 0}"
                )

        # Prepare JSON for storage in the `products` column
        products_json = [{"product_id": product.id, "quantity": order.product_ids.count(product.id)} for product in products]

        # Create and store the new order
        new_order = models.Order(
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=datetime.utcnow(),
            products=products_json
        )

        db.add(new_order)

        # Deduct used ingredient quantities
        for ingredient_name, required_quantity in required_ingredients.items():
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_name).first()
            ingredient.quantity -= required_quantity
            db.add(ingredient)

        db.commit()
        db.refresh(new_order)

        # Convert SQLAlchemy products to Pydantic models, duplicating products based on `quantity`
        full_products = []
        for item in products_json:
            product = db.query(models.Product).filter(models.Product.id == item["product_id"]).first()
            for _ in range(item["quantity"]):  # Duplicate based on quantity
                full_products.append(
                    schemas.ProductUpdate(
                        name=product.name,
                        price=product.price,
                        promotion=product.promotion,
                        dietary_type=product.dietary_type,
                        ingredients=[
                            schemas.IngredientUpdate(
                                name=ingredient["name"],
                                quantity=ingredient["quantity"]
                            )
                            for ingredient in product.ingredients  # Parse each ingredient
                        ]
                    )
                )

        # Return the newly created order with detailed product information
        return schemas.Order(
            id=new_order.id,
            order_type=new_order.order_type,
            order_status=new_order.order_status,
            order_date=new_order.order_date,
            products=full_products
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")


@app.get("/orders/", response_model=List[schemas.Order], status_code=status.HTTP_200_OK)
def get_all_orders(db: Session = Depends(get_db)):
    """
    Retrieve a list of all orders with detailed product information.
    """
    try:
        orders = db.query(models.Order).all()
        if not orders:
            raise HTTPException(status_code=404, detail="No orders found")

        # Transform orders for the response
        response_orders = []
        for order in orders:
            # Safely handle cases where `products` might be None
            order_products = order.products or []

            # Transform the JSON products into ProductUpdate schemas
            full_products = []
            for item in order_products:
                product = db.query(models.Product).filter(models.Product.id == item["product_id"]).first()
                if product:
                    for _ in range(item["quantity"]):  # Duplicate based on quantity
                        full_products.append(
                            schemas.ProductUpdate(
                                name=product.name,
                                price=product.price,
                                promotion=product.promotion,
                                dietary_type=product.dietary_type,
                                ingredients=[
                                    schemas.IngredientUpdate(
                                        name=ingredient["name"],
                                        quantity=ingredient["quantity"]
                                    )
                                    for ingredient in product.ingredients
                                ]
                            )
                        )

            # Add the transformed order to the response
            response_orders.append(
                schemas.Order(
                    id=order.id,
                    order_type=order.order_type,
                    order_status=order.order_status,
                    order_date=order.order_date,
                    products=full_products
                )
            )

        return response_orders

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orders: {str(e)}")

@app.get("/orders/{order_id}", response_model=schemas.Order, status_code=status.HTTP_200_OK)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single order by its ID.
    """
    try:
        # Fetch the order by ID
        order = db.query(models.Order).filter(models.Order.id == order_id).first()

        if not order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

        # Safely handle cases where `products` might be None
        order_products = order.products or []

        # Transform the JSON products into ProductUpdate schemas
        full_products = []
        for item in order_products:
            product = db.query(models.Product).filter(models.Product.id == item["product_id"]).first()
            if product:
                for _ in range(item["quantity"]):  # Duplicate based on quantity
                    full_products.append(
                        schemas.ProductUpdate(
                            name=product.name,
                            price=product.price,
                            promotion=product.promotion,
                            dietary_type=product.dietary_type,
                            ingredients=[
                                schemas.IngredientUpdate(
                                    name=ingredient["name"],
                                    quantity=ingredient["quantity"]
                                )
                                for ingredient in product.ingredients
                            ]
                        )
                    )

        # Return the transformed order
        return schemas.Order(
            id=order.id,
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=order.order_date,
            products=full_products
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving order: {str(e)}")


@app.put("/orders/{order_id}", response_model=schemas.Order, status_code=status.HTTP_200_OK)
def update_order(order_id: int, updated_order: schemas.CreateOrder, db: Session = Depends(get_db)):
    """
    Update an existing order by ID.
    """
    try:
        # Fetch the existing order
        order = db.query(models.Order).filter(models.Order.id == order_id).first()

        if not order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

        # Fetch the products from the database based on updated product IDs
        products = db.query(models.Product).filter(models.Product.id.in_(updated_order.product_ids)).all()

        if not products:
            raise HTTPException(status_code=404, detail="One or more products not found")

        # Check ingredient availability for the new products
        product_counts = {product_id: updated_order.product_ids.count(product_id) for product_id in updated_order.product_ids}
        for product in products:
            for ingredient in product.ingredients:
                db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient["name"]).first()
                if not db_ingredient or db_ingredient.quantity < (ingredient["quantity"] * product_counts[product.id]):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient {ingredient['name']} for product {product.name}"
                    )

        # Prepare the new products JSON
        updated_products_json = [{"product_id": product.id, "quantity": product_counts[product.id]} for product in products]

        # Update the order's fields
        order.order_type = updated_order.order_type
        order.order_status = updated_order.order_status
        order.products = updated_products_json

        # Update ingredient quantities in the database
        for product in products:
            for ingredient in product.ingredients:
                db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient["name"]).first()
                if db_ingredient:
                    db_ingredient.quantity -= ingredient["quantity"] * product_counts[product.id]

        # Commit the updates
        db.commit()
        db.refresh(order)

        # Transform the updated order into the response model
        full_products = []
        for item in updated_products_json:
            product = db.query(models.Product).filter(models.Product.id == item["product_id"]).first()
            for _ in range(item["quantity"]):  # Duplicate based on quantity
                full_products.append(
                    schemas.ProductUpdate(
                        name=product.name,
                        price=product.price,
                        promotion=product.promotion,
                        dietary_type=product.dietary_type,
                        ingredients=[
                            schemas.IngredientUpdate(
                                name=ingredient["name"],
                                quantity=ingredient["quantity"]
                            )
                            for ingredient in product.ingredients
                        ]
                    )
                )

        return schemas.Order(
            id=order.id,
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=order.order_date,
            products=full_products
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating order: {str(e)}")


@app.delete("/orders/{order_id}", response_model=schemas.Order, status_code=status.HTTP_200_OK)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    Delete an order by its ID and return the deleted order.
    """
    try:
        # Retrieve the order to be deleted
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found.")

        # Convert the order's products to Pydantic schema for response
        full_products = []
        for product_json in order.products:
            product = db.query(models.Product).filter(models.Product.id == product_json["product_id"]).first()
            if product:
                for _ in range(product_json["quantity"]):  # Duplicate based on quantity
                    full_products.append(
                        schemas.ProductUpdate(
                            name=product.name,
                            price=product.price,
                            promotion=product.promotion,
                            dietary_type=product.dietary_type,
                            ingredients=[
                                schemas.IngredientUpdate(
                                    name=ingredient["name"],
                                    quantity=ingredient["quantity"]
                                )
                                for ingredient in product.ingredients
                            ]
                        )
                    )

        # Prepare the response schema
        deleted_order = schemas.Order(
            id=order.id,
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=order.order_date,
            products=full_products
        )

        # Delete the order
        db.delete(order)
        db.commit()

        return deleted_order

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting order: {str(e)}")





#
# @app.post("/customers/", response_model=schemas.Customer)
# def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
#     db_customer = models.Customer(name=customer.name, phone=customer.phone, address=customer.address)
#     db.add(db_customer)
#     db.commit()
#     db.refresh(db_customer)
#     return db_customer
#
# @app.get("/customers/{customer_id}", response_model=schemas.Customer)
# def get_customer(customer_id: int, db: Session = Depends(get_db)):
#     db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
#     if db_customer is None:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     return db_customer
#
# # Menu Item Endpoints
# @app.post("/menu_items/", response_model=schemas.MenuItem)
# def create_menu_item(menu_item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
#     db_menu_item = models.MenuItem(
#         name=menu_item.name,
#         ingredients=menu_item.ingredients,
#         price=menu_item.price,
#         calories=menu_item.calories,
#         category=menu_item.category
#     )
#     db.add(db_menu_item)
#     db.commit()
#     db.refresh(db_menu_item)
#     return db_menu_item
#
# @app.get("/menu_items/{menu_item_id}", response_model=schemas.MenuItem)
# def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
#     db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
#     if db_menu_item is None:
#         raise HTTPException(status_code=404, detail="Menu item not found")
#     return db_menu_item
#
# # Order Endpoints
# @app.post("/orders/", response_model=schemas.Order)
# def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
#     db_order = models.Order(
#         order_number=order.order_number,
#         customer_id=order.customer_id,
#         order_type=order.order_type,
#         order_status=order.order_status
#     )
#     db.add(db_order)
#     db.commit()
#     db.refresh(db_order)
#     return db_order
#
# @app.get("/orders/{order_id}", response_model=schemas.Order)
# def get_order(order_id: int, db: Session = Depends(get_db)):
#     db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
#     if db_order is None:
#         raise HTTPException(status_code=404, detail="Order not found")
#     return db_order
#
# # Order Item Endpoints
# @app.post("/order_items/", response_model=schemas.OrderItem)
# def create_order_item(order_item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
#     db_order_item = models.OrderItem(
#         order_id=order_item.order_id,
#         menu_item_id=order_item.menu_item_id,
#         quantity=order_item.quantity
#     )
#     db.add(db_order_item)
#     db.commit()
#     db.refresh(db_order_item)
#     return db_order_item
#
# @app.get("/order_items/{order_item_id}", response_model=schemas.OrderItem)
# def get_order_item(order_item_id: int, db: Session = Depends(get_db)):
#     db_order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
#     if db_order_item is None:
#         raise HTTPException(status_code=404, detail="Order item not found")
#     return db_order_item
