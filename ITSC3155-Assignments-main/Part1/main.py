# main.py
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
import asyncio
from typing import List
from models import Base
from database import engine
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Create the database tables
Base.metadata.create_all(bind=engine)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Get list of orders in the queue (not completed)
@app.get("/orders/queue", response_model=List[schemas.Order])
def get_order_queue(db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.order_status != 'completed').all()
    return orders

# Update the status of a specific order
@app.put("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, order_status: str, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order_status not in [status.value for status in models.OrderStatusEnum]:
        raise HTTPException(status_code=400, detail="Invalid order status")
    db_order.order_status = order_status
    db.commit()
    db.refresh(db_order)
    return db_order

# Create a new payment for an order
@app.post("/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    db_payment = models.Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_status=payment.payment_status
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Get payment details by ID
@app.get("/payments/{payment_id}", response_model=schemas.Payment)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

# Update order details
@app.put("/orders/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order

# Cancel an order
@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"detail": "Order deleted"}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws/orders/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Check if customer exists based on unique phone number
    customer = db.query(models.Customer).filter(
        models.Customer.phone == order.customer.phone
    ).first()

    if not customer:
        # Create a new customer
        customer = models.Customer(
            name=order.customer.name,
            phone=order.customer.phone,
            address=order.customer.address
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # Create the order linked to the customer
    db_order = models.Order(
        order_number=order.order_number,
        customer_id=customer.id,
        order_type=order.order_type,
        order_status=order.order_status,
        total_amount=order.total_amount,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Handle order items
    for item in order.items:
        # Verify that the menu_item_id exists
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item with id {item.menu_item_id} does not exist."
            )
        db_item = models.OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            total_amount=menu_item.price * item.quantity
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.post("/order_items/", response_model=schemas.OrderItem)
def create_order_item(order_item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == order_item.menu_item_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db_order_item = models.OrderItem(
        order_id=order_item.order_id,
        menu_item_id=order_item.menu_item_id,
        quantity=order_item.quantity,
        total_amount=db_menu_item.price * order_item.quantity
    )
    db.add(db_order_item)

    # Update order total_amount
    db_order = db.query(models.Order).filter(models.Order.id == order_item.order_id).first()
    if db_order:
        db_order.total_amount += db_order_item.total_amount

    db.commit()
    db.refresh(db_order_item)
    return db_order_item


# Apply a promotion code to an order
@app.post("/orders/{order_id}/apply_promotion/")
def apply_promotion(order_id: int, code: str, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Compute the total amount of the order if not already computed
    if db_order.total_amount == 0.0:
        total = 0.0
        for item in db_order.items:
            total += item.quantity * item.menu_item.price
        db_order.total_amount = total
        db.commit()
        db.refresh(db_order)

    db_promotion = db.query(models.Promotion).filter(
        models.Promotion.code == code,
        models.Promotion.is_active == True,
        models.Promotion.start_date <= datetime.utcnow(),
        models.Promotion.end_date >= datetime.utcnow()
    ).first()
    if db_promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found or inactive")

    discount_amount = db_order.total_amount * (db_promotion.discount_percentage / 100)
    db_order.total_amount -= discount_amount
    db.commit()
    db.refresh(db_order)
    return {
        "detail": "Promotion applied",
        "discount_amount": discount_amount,
        "new_total_amount": db_order.total_amount
    }


# Submit feedback
@app.post("/feedbacks/", response_model=schemas.Feedback)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = models.Feedback(
        customer_id=feedback.customer_id,
        order_id=feedback.order_id,
        rating=feedback.rating,
        comments=feedback.comments
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# Get feedback details
@app.get("/feedbacks/{feedback_id}", response_model=schemas.Feedback)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback


# Create new training material
@app.post("/training_materials/", response_model=schemas.TrainingMaterial)
def create_training_material(training_material: schemas.TrainingMaterialCreate, db: Session = Depends(get_db)):
    db_training_material = models.TrainingMaterial(
        title=training_material.title,
        content=training_material.content
    )
    db.add(db_training_material)
    db.commit()
    db.refresh(db_training_material)
    return db_training_material

# Get training material details
@app.get("/training_materials/{material_id}", response_model=schemas.TrainingMaterial)
def get_training_material(material_id: int, db: Session = Depends(get_db)):
    db_material = db.query(models.TrainingMaterial).filter(models.TrainingMaterial.id == material_id).first()
    if db_material is None:
        raise HTTPException(status_code=404, detail="Training material not found")
    return db_material

# Get sales analytics
@app.get("/analytics/sales")
def get_sales_data(db: Session = Depends(get_db)):
    total_sales = db.query(func.sum(models.Order.total_amount)).scalar() or 0.0
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    return {
        "total_sales": total_sales,
        "total_orders": total_orders
    }

# Get popular menu items
@app.get("/analytics/popular_items")
def get_popular_items(db: Session = Depends(get_db)):
    popular_items = db.query(
        models.MenuItem.name,
        func.sum(models.OrderItem.quantity).label('total_quantity')
    ).join(models.OrderItem).group_by(models.MenuItem.id).order_by(func.sum(models.OrderItem.quantity).desc()).all()
    return [{"menu_item": item[0], "total_quantity": item[1]} for item in popular_items]

@app.get("/customers/", response_model=List[schemas.Customer])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/customers/ids", response_model=List[int])
def get_customer_ids(db: Session = Depends(get_db)):
    customer_ids = db.query(models.Customer.id).all()
    customer_ids = [id_tuple[0] for id_tuple in customer_ids]
    return customer_ids

@app.post("/menu_items/", response_model=schemas.MenuItem)
def create_menu_item(menu_item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    db_menu_item = models.MenuItem(
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price
    )
    try:
        db.add(db_menu_item)
        db.commit()
        db.refresh(db_menu_item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Menu item already exists.")
    return db_menu_item

@app.get("/menu_items/", response_model=List[schemas.MenuItem])
def get_menu_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menu_items = db.query(models.MenuItem).offset(skip).limit(limit).all()
    return menu_items