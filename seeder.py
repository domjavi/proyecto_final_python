import asyncio
from sqlmodel import Session, select
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
            users_data = [
                {"username": "user1", "email": "user1@example.com", "hashed_password": pass_user1, "role": "client"},
                {"username": "user2", "email": "user2@example.com", "hashed_password": pass_user2, "role": "admin"}
            ]

            for user_data in users_data:
                existing_user = session.exec(select(User).where(User.username == user_data["username"])).first()
                if existing_user:
                    print(f"User {user_data['username']} already exists, skipping insertion.")
                else:
                    new_user = User(**user_data)
                    session.add(new_user)
                    session.commit()
                    session.refresh(new_user)
                    print(f"User {user_data['username']} created successfully.")

        except Exception as e:
            print(f"Error creating users: {e}")

        # Crear orders linkadas a usuarios
        try:
            orders_data = [
                {"owner_id": 1},  # Assuming user1.id is 1
                {"owner_id": 2},  # Assuming user2.id is 2
                {"owner_id": 1}
            ]

            for order_data in orders_data:
                existing_order = session.exec(select(Order).where(Order.owner_id == order_data["owner_id"])).first()
                if existing_order:
                    print(f"Order for owner_id {order_data['owner_id']} already exists, skipping insertion.")
                else:
                    new_order = Order(**order_data)
                    session.add(new_order)
                    session.commit()
                    session.refresh(new_order)
                    print(f"Order for owner_id {order_data['owner_id']} created successfully.")

        except Exception as e:
            print(f"Error creating orders: {e}")

        # Crear items de orden
        try:
            items_data = [
                {"product_id": 1, "order_id": 1, "quantity": 2},
                {"product_id": 2, "order_id": 1, "quantity": 1},
                {"product_id": 1, "order_id": 2, "quantity": 1},
                {"product_id": 3, "order_id": 3, "quantity": 5}
            ]

            for item_data in items_data:
                # Assuming add_item_ordered handles duplicates internally or you can add similar checks
                await add_item_ordered(session, **item_data)
                print(f"Item with product_id {item_data['product_id']} for order_id {item_data['order_id']} created successfully.")

        except Exception as e:
            print(f"Error creating items: {e}")

if __name__ == "__main__":
    asyncio.run(seed_data())
    print("Seeding completed.")