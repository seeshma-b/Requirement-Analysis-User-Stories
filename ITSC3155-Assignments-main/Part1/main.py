# main.py
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
    Delete an ingredient by its ID and reset IDs.
    """
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found.")

    # Delete the ingredient
    db.delete(db_ingredient)
    db.commit()

    # Reset IDs
    ingredients = db.query(models.Ingredient).order_by(models.Ingredient.id).all()
    for index, ingredient in enumerate(ingredients, start=1):
        ingredient.id = index
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
    Delete a Product by its ID and reset IDs.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # Delete the product
    db.delete(db_product)
    db.commit()

    # Reset IDs
    products = db.query(models.Product).order_by(models.Product.id).all()
    for index, product in enumerate(products, start=1):
        product.id = index
    db.commit()

    return db_product # Return the deleted product for confirmation
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
