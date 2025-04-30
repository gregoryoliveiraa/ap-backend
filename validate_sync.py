from sqlalchemy import create_engine, text, inspect
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

def clean_value_for_comparison(value):
    """Clean value for comparison."""
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

def validate_sync():
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
        print("Iniciando validação de sincronização...")
        
        # Get all tables from SQLite
        sqlite_tables = get_table_names(sqlite_engine)
        print(f"\nTabelas encontradas no SQLite: {', '.join(sqlite_tables)}")
        
        # Get all tables from PostgreSQL
        postgres_tables = get_table_names(postgres_engine)
        print(f"Tabelas encontradas no PostgreSQL: {', '.join(postgres_tables)}")
        
        # Check for missing tables in PostgreSQL
        missing_tables = [table for table in sqlite_tables if table not in postgres_tables and table != "template"]
        if missing_tables:
            print(f"\nAVISO: As seguintes tabelas existem no SQLite mas não no PostgreSQL: {', '.join(missing_tables)}")
        
        # Check for missing tables in SQLite
        extra_tables = [table for table in postgres_tables if table not in sqlite_tables]
        if extra_tables:
            print(f"\nAVISO: As seguintes tabelas existem no PostgreSQL mas não no SQLite: {', '.join(extra_tables)}")
        
        # Compare data in common tables
        common_tables = [table for table in sqlite_tables if table in postgres_tables and table != "template"]
        
        for table_name in common_tables:
            try:
                print(f"\nValidando tabela: {table_name}")
                
                # Get data from SQLite
                sqlite_data = get_table_data(sqlite_session, table_name)
                if not sqlite_data:
                    print(f"Nenhum dado encontrado na tabela {table_name} no SQLite")
                    continue
                
                print(f"Encontrados {len(sqlite_data)} registros no SQLite")
                
                # Get data from PostgreSQL
                postgres_data = get_table_data(postgres_session, table_name)
                if not postgres_data:
                    print(f"Nenhum dado encontrado na tabela {table_name} no PostgreSQL")
                    continue
                
                print(f"Encontrados {len(postgres_data)} registros no PostgreSQL")
                
                # Clean data for comparison
                sqlite_data_cleaned = [{k: clean_value_for_comparison(v) for k, v in record.items()} for record in sqlite_data]
                postgres_data_cleaned = [{k: clean_value_for_comparison(v) for k, v in record.items()} for record in postgres_data]
                
                # Check if all SQLite records exist in PostgreSQL
                missing_records = []
                for sqlite_record in sqlite_data_cleaned:
                    found = False
                    for postgres_record in postgres_data_cleaned:
                        if all(sqlite_record.get(k) == postgres_record.get(k) for k in sqlite_record.keys()):
                            found = True
                            break
                    if not found:
                        missing_records.append(sqlite_record)
                
                if missing_records:
                    print(f"AVISO: {len(missing_records)} registros do SQLite não foram encontrados no PostgreSQL")
                    print("Exemplo de registro ausente:")
                    print(json.dumps(missing_records[0], indent=2, default=str))
                else:
                    print(f"Todos os {len(sqlite_data)} registros do SQLite foram encontrados no PostgreSQL")
                
                # Check if there are extra records in PostgreSQL
                if len(postgres_data) > len(sqlite_data):
                    print(f"AVISO: O PostgreSQL tem {len(postgres_data) - len(sqlite_data)} registros extras")
                
            except Exception as e:
                print(f"Erro ao validar tabela {table_name}: {str(e)}")
                continue
        
        print("\nValidação concluída!")
        
    except Exception as e:
        print(f"Erro durante a validação: {str(e)}")
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    validate_sync() 