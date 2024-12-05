from app import db

def add_to_db(instance):
    """Adds an instance to the database."""
    try:
        db.session.add(instance)
        db.session.commit()
    except Exception as e:
        print(f"Error adding to DB: {e}")
        db.session.rollback()
        raise

def delete_from_db(instance):
    """Deletes an instance from the database."""
    try:
        db.session.delete(instance)
        db.session.commit()
    except Exception as e:
        print(f"Error deleting from DB: {e}")
        db.session.rollback()
        raise
