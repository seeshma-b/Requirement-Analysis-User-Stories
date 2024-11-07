from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import models, schemas


def create(db: Session, order):
    # Create a new instance of the Order model with the provided data
    db_order = models.Order(
        customer_name=order.customer_name,
        description=order.description
    )
    # Add the newly created Order object to the database session
    db.add(db_order)
    # Commit the changes to the database
    db.commit()
    # Refresh the Order object to ensure it reflects the current state in the database
    db.refresh(db_order)
    # Return the newly created Order object
    return db_order


def read_all(db: Session):
    return db.query(models.Order).all()


def read_one(db: Session, order_id):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def update(db: Session, order_id, order):
    # Query the database for the specific order to update
    db_order = db.query(models.Order).filter(models.Order.id == order_id)
    # Extract the update data from the provided 'order' object
    update_data = order.model_dump(exclude_unset=True)
    # Update the database record with the new data, without synchronizing the session
    db_order.update(update_data, synchronize_session=False)
    # Commit the changes to the database
    db.commit()
    # Return the updated order record
    return db_order.first()


def delete(db: Session, order_id):
    # Query the database for the specific order to delete
    db_order = db.query(models.Order).filter(models.Order.id == order_id)
    # Delete the database record without synchronizing the session
    db_order.delete(synchronize_session=False)
    # Commit the changes to the database
    db.commit()
    # Return a response with a status code indicating success (204 No Content)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
