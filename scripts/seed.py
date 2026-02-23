from app.db import init_db
from app.utils import seed_data

def main():
    init_db()
    seed_data()
    print("Seeded database with sample data.")

if __name__ == '__main__':
    main()
