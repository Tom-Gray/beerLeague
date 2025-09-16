from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import Config

class Database:
    """Database management class."""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.engine = create_engine(
            self.config.SQLALCHEMY_DATABASE_URI,
            echo=self.config.SQLALCHEMY_ECHO if hasattr(self.config, 'SQLALCHEMY_ECHO') else False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all database tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)

# Global database instance
db = Database()

def get_db():
    """Dependency to get database session."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

def init_db():
    """Initialize the database."""
    db.create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
