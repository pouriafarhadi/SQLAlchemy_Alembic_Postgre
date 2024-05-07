from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

"""
first create essential libraries and docker container using terminal by this command:
pip install SQLAlchemy
pip install asyncpg
pip install psycopg2-binary
docker run --name postgresql -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=user -p 5432:5432 -d postgres
"""
# connection string format: driver+postgresql://user:pass@host:port/dbname
url = URL.create(
    drivername="postgresql+psycopg2",
    username="user",
    password="password",
    host="localhost",
    port=5432,
    database="user",
)
engine = create_engine(url=url, echo=True)

session_pool = sessionmaker(engine)


# session = session_pool()
# session.execute()
# session.commit()
# session.close()

# with session_pool() as session:
#     session.execute(text('SELECT 1'))
