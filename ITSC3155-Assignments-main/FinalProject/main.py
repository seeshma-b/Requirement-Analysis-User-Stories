# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=engine)

@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = models.Customer(name=customer.name, phone=customer.phone, address=customer.address)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# Menu Item Endpoints
@app.post("/menu_items/", response_model=schemas.MenuItem)
def create_menu_item(menu_item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    db_menu_item = models.MenuItem(
        name=menu_item.name,
        ingredients=menu_item.ingredients,
        price=menu_item.price,
        calories=menu_item.calories,
        category=menu_item.category
    )
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@app.get("/menu_items/{menu_item_id}", response_model=schemas.MenuItem)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

# Order Endpoints
@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(
        order_number=order.order_number,
        customer_id=order.customer_id,
        order_type=order.order_type,
        order_status=order.order_status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Order Item Endpoints
@app.post("/order_items/", response_model=schemas.OrderItem)
def create_order_item(order_item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    db_order_item = models.OrderItem(
        order_id=order_item.order_id,
        menu_item_id=order_item.menu_item_id,
        quantity=order_item.quantity
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

@app.get("/order_items/{order_item_id}", response_model=schemas.OrderItem)
def get_order_item(order_item_id: int, db: Session = Depends(get_db)):
    db_order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id).first()
    if db_order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    return db_order_item
