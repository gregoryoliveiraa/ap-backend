from sqlalchemy import create_engine, text, inspect, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

def get_table_names(engine):
    """Get all table names from the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table_data(session, table_name):
    """Get all data from a table as a list of dictionaries."""
    result = session.execute(text(f"SELECT * FROM {table_name}"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]

def get_table_columns(engine, table_name):
    """Get column information for a table."""
    inspector = inspect(engine)
    return inspector.get_columns(table_name)

def create_table_if_not_exists(engine, table_name, columns):
    """Create a table if it doesn't exist."""
    metadata = MetaData()
    
    # Map SQLite types to PostgreSQL types
    type_mapping = {
        'TEXT': Text,
        'VARCHAR': String,
        'INTEGER': Integer,
        'BOOLEAN': Boolean,
        'DATETIME': DateTime,
        'JSON': JSON
    }
    
    # Create column definitions
    table_columns = []
    for col in columns:
        col_type = type_mapping.get(col['type'].upper(), String)
        table_columns.append(
            Column(col['name'], col_type, primary_key=col.get('primary_key', False))
        )
    
    # Create table
    Table(table_name, metadata, *table_columns)
    metadata.create_all(engine)

def clean_value_for_insert(value):
    """Clean value for SQL insert."""
    if isinstance(value, (datetime, bool, int, float)):
        return value
    if value is None:
        return None
    try:
        # Try to parse as JSON if it's a string that looks like JSON
        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
            return json.loads(value)
        return value
    except:
        return value

def sync_to_rds():
    # Database URLs
    SQLITE_URL = "sqlite:///./app.db"
    POSTGRES_URL = "postgresql://goliveira:advogadaparceira2012@advogada-parceira-db.cfgy6m4oww5k.us-east-2.rds.amazonaws.com:5432/advogada_parceira"

    # Create engines
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()

    try:
        print("Iniciando sincronização com RDS...")
        
        # Get all tables from SQLite
        tables = get_table_names(sqlite_engine)
        print(f"\nTabelas encontradas: {', '.join(tables)}")
        
        for table_name in tables:
            try:
                print(f"\nSincronizando tabela: {table_name}")
                
                # Get table structure from SQLite
                columns = get_table_columns(sqlite_engine, table_name)
                
                # Create table in PostgreSQL if it doesn't exist
                create_table_if_not_exists(postgres_engine, table_name, columns)
                print(f"Estrutura da tabela {table_name} verificada/criada")
                
                # Get data from SQLite
                sqlite_data = get_table_data(sqlite_session, table_name)
                if not sqlite_data:
                    print(f"Nenhum dado encontrado na tabela {table_name}")
                    continue
                
                print(f"Encontrados {len(sqlite_data)} registros")
                
                # Clean RDS table
                postgres_session.execute(text(f"DELETE FROM {table_name}"))
                postgres_session.commit()
                print("Dados antigos removidos do RDS")
                
                # Insert data into RDS
                for record in sqlite_data:
                    # Clean values
                    cleaned_record = {k: clean_value_for_insert(v) for k, v in record.items()}
                    
                    # Create placeholders and values for SQL
                    columns = list(cleaned_record.keys())
                    placeholders = [f":{col}" for col in columns]
                    
                    # Create INSERT statement
                    insert_stmt = f"""
                        INSERT INTO {table_name} ({', '.join(columns)})
                        VALUES ({', '.join(placeholders)})
                    """
                    
                    try:
                        postgres_session.execute(text(insert_stmt), cleaned_record)
                        postgres_session.commit()
                    except Exception as e:
                        print(f"Erro ao inserir registro: {str(e)}")
                        postgres_session.rollback()
                        continue
                
                print(f"Tabela {table_name} sincronizada com sucesso!")
                
            except Exception as e:
                print(f"Erro ao sincronizar tabela {table_name}: {str(e)}")
                continue
        
        print("\nSincronização concluída!")
        
    except Exception as e:
        print(f"Erro durante a sincronização: {str(e)}")
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    sync_to_rds() 