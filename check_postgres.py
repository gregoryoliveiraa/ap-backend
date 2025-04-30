from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database URL
POSTGRES_URL = "postgresql://goliveira:advogadaparceira2012@advogada-parceira-db.cfgy6m4oww5k.us-east-2.rds.amazonaws.com:5432/advogada_parceira"

# Create engine and session
engine = create_engine(POSTGRES_URL)
Session = sessionmaker(bind=engine)
session = Session()

# List of tables to check
tables = [
    'users', 
    'documents', 
    'templates', 
    'chat_sessions', 
    'chat_messages', 
    'generated_documents', 
    'legal_theses', 
    'notifications', 
    'payments', 
    'usage', 
    'user_notifications', 
    'document_templates', 
    'document_thesis_association', 
    'jurisprudencia_buscas', 
    'jurisprudencia_resultados'
]

# Check each table
for table in tables:
    try:
        count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"{table}: {count} registros")
    except Exception as e:
        print(f"Erro ao verificar tabela {table}: {str(e)}")

session.close() 