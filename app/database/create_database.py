from app.database.connection import engine, init_db
from app.database.models import Base


def main():
    print("Initializing database tables...")
    init_db()
    print(f"Database ready: {engine.url}")
    print(f"Registered tables: {list(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    main()
