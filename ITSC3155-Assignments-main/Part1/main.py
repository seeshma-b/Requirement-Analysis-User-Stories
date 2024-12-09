# main.py
from collections import Counter
from datetime import datetime, date
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from pydantic import parse_obj_as
from sqlalchemy import Float, text, func
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
        # Convert IngredientUpdate objects to dictionaries
        db_product.ingredients = [
            ingredient.dict() for ingredient in product_update.ingredients
        ]

    try:
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")


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
            order_date=datetime.utcnow().date(),
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

        # Use the utility function to transform products into Pydantic models
        full_products = transform_products_to_pydantic(products_json, db)

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

        response_orders = [
            schemas.Order(
                id=order.id,
                order_type=order.order_type,
                order_status=order.order_status,
                order_date=order.order_date.date(),
                products=transform_products_to_pydantic(order.products, db)
            )
            for order in orders
        ]

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

        # Return the transformed order with the date extracted
        return schemas.Order(
            id=order.id,
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=order.order_date.date(),
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

        # Fix order_date to return only the date part
        return schemas.Order(
            id=order.id,
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=order.order_date.date(),
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

        # Prepare the response before deleting
        deleted_order = schemas.Order(
            id=order.id,
            order_type=order.order_type,
            order_status=order.order_status,
            order_date=order.order_date.date() if isinstance(order.order_date, datetime) else order.order_date,
            products=order.products or []
        )

        # Delete the order
        db.delete(order)
        db.commit()

        return deleted_order

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting order: {str(e)}")





@app.post("/reviews/", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.CreateReview, db: Session = Depends(get_db)):
    """
    Create a new review for a product.
    """
    # Check if the product exists
    product = db.query(models.Product).filter(models.Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {review.product_id} does not exist.")

    # Prepare the title with additional product information
    updated_title = f"{review.title} - product: {product.id}, '{product.name}'"

    # Proceed with creating the review
    db_review = models.Review(
        product_id=review.product_id,
        title=updated_title,  # Use the updated title
        description=review.description
    )
    db.add(db_review)
    try:
        db.commit()
        db.refresh(db_review)
        return db_review
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Review could not be created due to a database constraint.")


@app.get("/reviews{review_id}", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """
    Get all reviews for a product.
    """
    try:
        # Fetch the order by ID
        review = db.query(models.Review).filter(models.Review.id == review_id).first()

        if not review:
            raise HTTPException(status_code=404, detail=f"Review with ID {review_id} not found")

        return schemas.Review.model_validate(review)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving review: {str(e)}")


@app.get("/reviews/", response_model=List[schemas.Review], status_code=status.HTTP_200_OK)
def get_all_reviews(db: Session = Depends(get_db)):
    """
    Get all reviews for products.
    """
    try:
        # Fetch all reviews from the database
        reviews = db.query(models.Review).all()
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found")

        # Convert SQLAlchemy models to Pydantic schemas using `model_validate`
        return [schemas.Review.model_validate(review) for review in reviews]
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@app.patch("/reviews/{review_id}", response_model=schemas.Review, status_code=status.HTTP_200_OK)
def update_review(review_id: int, review_update: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    """
    Update an existing review.
    """
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found.")

    db_product = db.query(models.Product).filter(models.Product.id == review_update.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with ID {review_update.product_id} not found.")

    # Update review fields
    if review_update.product_id is not None:
        db_review.product_id = review_update.product_id
    if review_update.title is not None:
        db_review.title = review_update.title
    if review_update.description is not None:
        db_review.description = review_update.description

    db.commit()
    db.refresh(db_review)
    return db_review

@app.delete("/reviews{review_id}", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """
    Delete a review for a product.
    """
    try:
        # Fetch the order by ID
        deleted_review = db.query(models.Review).filter(models.Review.id == review_id).first()

        if not deleted_review:
            raise HTTPException(status_code=404, detail=f"Review with ID {review_id} not found")

        db.delete(deleted_review)
        db.commit()
        return deleted_review

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving review: {str(e)}")

@app.get("/orders_by_date_range/", response_model=List[schemas.Order])
def get_orders_by_date_range(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """
    Retrieve all orders within a specific date range.
    """

    # Remove unnecessary quotes from dates
    start_date = start_date.strip('"')
    end_date = end_date.strip('"')

    # Validate and parse the input dates
    start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Ensure start_date is before end_date
    if start_date_parsed > end_date_parsed:
        raise HTTPException(
            status_code=400,
            detail="Start date must be earlier than or equal to end date.",
        )

    # Query orders within the date range
    orders = db.query(models.Order).filter(
        models.Order.order_date >= start_date_parsed,
        models.Order.order_date <= end_date_parsed,
    ).all()

    # Handle no orders found
    if not orders:
        raise HTTPException(
            status_code=404,
            detail=f"No orders found between {start_date} and {end_date}.",
        )

    # Convert to Pydantic models
    validated_orders = []
    for order in orders:
        # Handle missing or `None` products
        if not order.products:
            order.products = []

        full_products = []
        for product_data in order.products:
            product = db.query(models.Product).filter(models.Product.id == product_data["product_id"]).first()
            if product:
                full_products.append(
                    schemas.ProductUpdate(
                        name=product.name,
                        price=product.price,
                        promotion=product.promotion,
                        dietary_type=product.dietary_type,
                        ingredients=[
                            schemas.IngredientUpdate(
                                name=ingredient["name"],
                                quantity=ingredient["quantity"],
                            )
                            for ingredient in product.ingredients
                        ],
                    )
                )

        validated_orders.append(
            schemas.Order(
                id=order.id,
                order_type=order.order_type,
                order_status=order.order_status,
                order_date=order.order_date,
                products=full_products,
            )
        )

    return validated_orders


@app.get("/revenue/{date}", response_model=str)
def get_daily_revenue(date: str, db: Session = Depends(get_db)):
    """
    Calculate the total revenue generated from orders on a given day.
    """

    # Parse the input date
    given_date = datetime.strptime(date, "%Y-%m-%d").date()

    # Fetch orders for the given date
    orders = db.query(models.Order).filter(
        func.date(models.Order.order_date) == given_date  # Extract date part
    ).all()

    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found for {date}.")

    # Calculate total revenue
    total_revenue = 0
    for order in orders:
        # Ensure products is not None
        order_products = order.products or []

        for product_data in order_products:
            product = db.query(models.Product).filter(models.Product.id == product_data["product_id"]).first()
            if product:
                total_revenue += product.price * product_data["quantity"]

    return f"${total_revenue} of total revenue for {date}"



@app.get("/products/search/", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def search_products_by_dietary_type(dietary_type: str, db: Session = Depends(get_db)):
    """
    Search for products by dietary type.
    """
    try:
        # Query products with the specified dietary type
        products = db.query(models.Product).filter(models.Product.dietary_type == dietary_type).all()

        if not products:
            raise HTTPException(status_code=404, detail=f"No products found for dietary type: {dietary_type}")

        return products

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error searching for products: {str(e)}")


@app.patch("/orders/{order_id}/pay", response_model=schemas.Order, status_code=status.HTTP_200_OK)
def pay_order(order_id: int, db: Session = Depends(get_db)):
    """
    Mark an order as 'paid'.
    """
    try:
        # Fetch the order by ID
        db_order = db.query(models.Order).filter(models.Order.id == order_id).first()

        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found.")

        if db_order.order_status == "paid":
            raise HTTPException(status_code=400, detail=f"Order with ID {order_id} is already paid.")

        # Update the order status to "paid"
        db_order.order_status = "paid"
        db.commit()
        db.refresh(db_order)

        # Transform products for the response
        full_products = transform_products_to_pydantic(db_order.products, db)

        # Return the updated order
        return schemas.Order(
            id=db_order.id,
            order_type=db_order.order_type,
            order_status=db_order.order_status,
            order_date=db_order.order_date.date(),  # Ensure date only
            products=full_products
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error paying for order: {str(e)}")


@app.post("/promo_codes/", response_model=schemas.PromoCodeResponse, status_code=status.HTTP_201_CREATED)
def create_promo_code(promo_code: schemas.CreatePromoCode, db: Session = Depends(get_db)):
    """
    Create a new promotional code.
    """
    try:
        new_promo_code = models.PromoCode(
            code=promo_code.code,
            discount_percentage=promo_code.discount_percentage,
            expiration_date=promo_code.expiration_date,
            is_active=promo_code.is_active,
        )
        db.add(new_promo_code)
        db.commit()
        db.refresh(new_promo_code)
        return new_promo_code
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating promo code: {str(e)}")

@app.get("/promo_codes/", response_model=List[schemas.PromoCodeResponse])
def get_all_promo_codes(db: Session = Depends(get_db)):
    """
    Retrieve all promotional codes.
    """
    promo_codes = db.query(models.PromoCode).all()
    return promo_codes


@app.patch("/orders/{order_id}/apply_promo/{promo_code}", response_model=schemas.Order, status_code=status.HTTP_200_OK)
def apply_promo_code(order_id: int, promo_code: str, db: Session = Depends(get_db)):
    """
    Apply a promotional code to an order by reducing product prices.
    """
    try:
        # Fetch the order by ID
        db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found.")

        # Fetch the promo code
        promo = db.query(models.PromoCode).filter(models.PromoCode.code == promo_code).first()
        if not promo or promo.expiration_date < datetime.utcnow().date():
            raise HTTPException(status_code=400, detail="Invalid or expired promo code.")

        # Apply the promo discount to each product in the order
        for product in db_order.products:
            product_details = db.query(models.Product).filter(models.Product.id == product["product_id"]).first()
            if product_details:
                product["price"] = product_details.price * (1 - promo.discount_percentage / 100)

        # Commit the changes to the database
        db.commit()

        # Refresh the order and convert to Pydantic for response
        db.refresh(db_order)
        return convert_to_pydantic_order(db_order, db)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error applying promo code: {str(e)}")


@app.patch("/promo_codes/{promo_id}/deactivate", response_model=schemas.PromoCodeResponse)
def deactivate_promo_code(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(models.PromoCode).filter(models.PromoCode.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found.")
    promo.is_active = False
    db.commit()
    db.refresh(promo)
    return promo


@app.get("/employee_training", response_model=str, status_code=status.HTTP_200_OK)
def employee_training():
    """
    Provide a detailed explanation of the system for employee training purposes.
    """
    training_text = """
Welcome to the Employee Training Module!

This system is designed to streamline the operations of our business. Below is a comprehensive explanation of the key features and functionalities you will be using:

1. **Order Management**:
   - Orders can be created, updated, retrieved, and deleted.
   - Orders include details such as type (delivery/takeout), status (prepping/paid), and the date.
   - Each order contains a list of products, which include their price, dietary type, and ingredients.

2. **Products and Ingredients**:
   - Products are predefined items like "Fish and Chips" or "Burger".
   - Each product has a list of ingredients required for its preparation. The system tracks ingredient quantities to ensure sufficient stock.
   - **Ingredient Management**:
     - Ingredients can be created, updated, retrieved, and deleted.
     - For example, you can add new ingredients like "Lettuce" or update the stock quantity of existing ones.
     - Deleting unused or incorrect ingredients helps keep the inventory clean and organized.

3. **Promotional Codes**:
   - Promo codes can be created with a discount percentage and an expiration date.
   - When a promo code is applied to an order, it reduces the price of applicable products.
   - Example: A 20% discount promo code will reduce a $25 product to $20.

4. **Revenue Reports**:
   - You can generate daily revenue reports by providing a specific date.
   - The system calculates the total revenue for all orders placed on the given date.

5. **Employee Training Module**:
   - This section provides a high-level overview of the system, including its features and how they interact.

6. **Utilities for Clean Code**:
   - The system employs utility functions like `convert_to_pydantic_order` to ensure clean and maintainable code.
   - These utilities handle conversions between database models (SQLAlchemy) and API schemas (Pydantic).

7. **Error Handling**:
   - The system is designed to catch and report errors, such as missing ingredients, invalid promo codes, or malformed requests.
   - Detailed error messages help in debugging and ensuring a smooth operation.

8. **Usage Guidelines**:
   - Always check stock levels before accepting large orders to avoid ingredient shortages.
   - Ensure that promo codes are valid and not expired before applying them to orders.
   - Use the `/orders_by_date_range` endpoint to analyze trends and improve efficiency.

Remember, this system is built to make your tasks easier and more efficient. If you encounter any issues or have suggestions for improvements, don't hesitate to reach out to your manager or the technical team.

Thank you for your dedication to making our business thrive!
    """
    return training_text




def transform_products_to_pydantic(product_json_list: List[dict], db: Session) -> List[schemas.ProductUpdate]:
    """
    Converts a list of product JSON objects into Pydantic ProductUpdate schemas.
    """
    full_products = []
    for product_json in product_json_list:
        product = db.query(models.Product).filter(models.Product.id == product_json["product_id"]).first()
        if product:
            for _ in range(product_json["quantity"]):  # Duplicate products based on quantity
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
    return full_products


def transform_pydantic_to_json(products: List[schemas.ProductUpdate]) -> List[dict]:
    """
    Converts a list of Pydantic ProductUpdate schemas into JSON-friendly dictionaries.
    """
    return [
        {
            "product_id": product.id,  # Assuming the schema includes `id` for this context
            "quantity": 1,  # Or any logic you have for determining quantity
        }
        for product in products
    ]

def convert_to_pydantic_order(order: models.Order, db: Session) -> schemas.Order:
    """
    Convert a SQLAlchemy Order object to a Pydantic Order schema.
    """
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
        order_date=order.order_date.date(),  # Convert datetime to date
        products=full_products
    )
