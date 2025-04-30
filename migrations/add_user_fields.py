from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Add new fields to users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Add estado_oab column if it doesn't exist
        connection.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='estado_oab'
                ) THEN 
                    ALTER TABLE users ADD COLUMN estado_oab VARCHAR;
                END IF;
            END $$;
        """))
        
        # Add verificado column if it doesn't exist
        connection.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='verificado'
                ) THEN 
                    ALTER TABLE users ADD COLUMN verificado BOOLEAN DEFAULT FALSE;
                END IF;
            END $$;
        """))
        
        connection.commit()

if __name__ == "__main__":
    run_migration() 