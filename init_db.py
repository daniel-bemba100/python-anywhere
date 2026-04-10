import pymysql
from config import Config

def init_database():
    connection = None
    try:
        print("🔄 Connecting to MariaDB...")
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=int(Config.DB_PORT),
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database if not exists
            db_name = Config.DB_NAME
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            cursor.execute(f"USE `{db_name}`")
            
            # Create/enhance subscribers table with online_status
            sql = """
            CREATE TABLE IF NOT EXISTS subscribers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                online_status ENUM('online', 'offline') DEFAULT 'offline',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(sql)
            
            # Add columns if missing (for existing DB)
            cursor.execute("""
                ALTER TABLE subscribers 
                ADD COLUMN IF NOT EXISTS online_status ENUM('online', 'offline') DEFAULT 'offline'
            """)
            cursor.execute("""
                ALTER TABLE subscribers 
                ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            """)
            
            connection.commit()
            print(f"✅ Database '{db_name}' ready with online_status column!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Ensure MariaDB running, copy .env.example → .env with DB creds.")
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    init_database()

