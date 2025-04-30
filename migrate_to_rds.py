from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from datetime import datetime

# Criar bases
SQLiteBase = declarative_base()
PostgresBase = declarative_base()

# Modelo para SQLite
class SQLiteUser(SQLiteBase):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String)
    hashed_password = Column(String)
    nome_completo = Column(String)
    numero_oab = Column(String(50))
    estado_oab = Column(String(2))
    verificado = Column(Boolean)
    data_criacao = Column(DateTime)
    ultima_atualizacao = Column(DateTime)
    creditos_disponiveis = Column(Integer)
    plano = Column(String(50))
    is_active = Column(Boolean)
    role = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Modelo para PostgreSQL
class PostgresUser(PostgresBase):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    oab_number = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    token_credits = Column(Integer)
    plan = Column(String(50))
    is_active = Column(Boolean)
    is_admin = Column(Boolean)

def migrate_data():
    # Configuração dos bancos de dados
    SQLITE_URL = "sqlite:///./app.db"
    POSTGRES_URL = "postgresql://goliveira:advogadaparceira2012@advogada-parceira-db.cfgy6m4oww5k.us-east-2.rds.amazonaws.com:5432/advogada_parceira"

    # Criar engines
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    # Criar sessões
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()

    try:
        print("Iniciando migração...")
        
        # Verificar a estrutura atual da tabela
        print("Verificando estrutura da tabela...")
        inspector = inspect(postgres_engine)
        columns = {col['name']: col for col in inspector.get_columns('users')}
        print("Colunas existentes:")
        for col_name, col_info in columns.items():
            print(f"- {col_name}: {col_info['type']}")
        
        # Limpar dados da tabela
        print("\nLimpando dados da tabela...")
        postgres_session.execute(text("DELETE FROM users"))
        postgres_session.commit()
        print("Dados limpos com sucesso!")
        
        # Ler dados do SQLite
        print("\nLendo dados do SQLite...")
        sqlite_users = sqlite_session.query(SQLiteUser).all()
        print(f"Encontrados {len(sqlite_users)} usuários no SQLite")
        
        # Inserir dados no PostgreSQL
        print("\nInserindo dados no PostgreSQL...")
        for sqlite_user in sqlite_users:
            try:
                # Converter dados do SQLite para o formato do PostgreSQL
                nome_parts = sqlite_user.nome_completo.split() if sqlite_user.nome_completo else ['', '']
                first_name = nome_parts[0] if nome_parts else ''
                last_name = ' '.join(nome_parts[1:]) if len(nome_parts) > 1 else ''
                
                # Gerar um ID numérico baseado no hash do UUID
                numeric_id = abs(hash(sqlite_user.id)) % (2**31-1)  # Garantir que seja um inteiro positivo de 32 bits
                
                # Inserir usando SQL direto para evitar problemas com o SQLAlchemy
                postgres_session.execute(
                    text("""
                        INSERT INTO users (
                            id, email, hashed_password, first_name, last_name,
                            oab_number, created_at, updated_at, token_credits,
                            plan, is_active, is_admin
                        ) VALUES (
                            :id, :email, :hashed_password, :first_name, :last_name,
                            :oab_number, :created_at, :updated_at, :token_credits,
                            :plan, :is_active, :is_admin
                        )
                    """),
                    {
                        "id": numeric_id,
                        "email": sqlite_user.email,
                        "hashed_password": sqlite_user.hashed_password,
                        "first_name": first_name,
                        "last_name": last_name,
                        "oab_number": sqlite_user.numero_oab,
                        "created_at": sqlite_user.data_criacao or sqlite_user.created_at,
                        "updated_at": sqlite_user.ultima_atualizacao or sqlite_user.updated_at,
                        "token_credits": sqlite_user.creditos_disponiveis,
                        "plan": sqlite_user.plano,
                        "is_active": sqlite_user.is_active,
                        "is_admin": sqlite_user.role == 'admin'
                    }
                )
                postgres_session.commit()
                print(f"Usuário migrado com sucesso: {sqlite_user.email} (ID: {numeric_id})")
            except Exception as e:
                print(f"Erro ao migrar usuário {sqlite_user.email}: {str(e)}")
                postgres_session.rollback()
                continue
        
        print("\nMigração concluída!")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        postgres_session.rollback()
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    migrate_data() 