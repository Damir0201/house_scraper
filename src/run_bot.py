from src.database import init_db
from src.bot import run_bot_listener

if __name__ == "__main__":
    print("Initializing db on bot...")
    init_db()
    run_bot_listener()