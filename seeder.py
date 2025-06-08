import asyncio
from sqlmodel import Session
from auth.hashing import hash_password
from db.database import engine, create_db_and_tables, drop_db_and_tables
from models.user import User
from models.order import Order
from crud.items_ordered import add_item_ordered
# from auth.hashing import hash_password  # Importamos la función para hashear contraseñas

async def seed_data():
    # Borrar la base de datos y las tablas existentes
    drop_db_and_tables() 
    # Crear la base de datos y las tablas
    create_db_and_tables()

    with Session(engine) as session:

        pass_user1 = hash_password("password1")
        pass_user2 = hash_password("password2")

        # Crear usuarios
        try:
            user1 = User(username="user1", email="user1@example.com", hashed_password=pass_user1, role="client")
            user2 = User(username="user2", email="user2@example.com", hashed_password=pass_user2, role="admin")
            session.add_all([user1, user2])
            session.commit()
            session.refresh(user1)
            session.refresh(user2)
            print("✅ Users created.")
        except Exception as e:
            print(f"Error creating users: {e}")

        # Crear orders linkadas a usuarios
        try:
            order1 = Order(owner_id=user1.id)
            order2 = Order(owner_id=user2.id)
            order3 = Order(owner_id=user1.id)
            session.add_all([order1, order2, order3])
            session.commit()
            session.refresh(order1)
            session.refresh(order2)
            session.refresh(order3)
            print("✅ Orders created.")
        except Exception as e:
            print(f"Error creating orders: {e}")

        # Crear items de orden
        try:
            await add_item_ordered(session, product_id=1, order_id=order1.id, quantity=2)
            await add_item_ordered(session, product_id=2, order_id=order1.id, quantity=1)
            await add_item_ordered(session, product_id=1, order_id=order2.id, quantity=1)
            await add_item_ordered(session, product_id=3, order_id=order3.id, quantity=5)
            print("✅ Items created.")
        except Exception as e:
            print(f"Error creating items: {e}")

if __name__ == "__main__":
    asyncio.run(seed_data())
    print("Seeding completed.")