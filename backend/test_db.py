from sqlalchemy import text

from app.database.connection import engine


try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    print("SQLite database connection successful!")

except Exception as error:
    print("SQLite database connection failed:")
    print(error)