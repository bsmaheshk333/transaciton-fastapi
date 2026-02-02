from app.db.database import Darwin
# from sqlalchemy.ext.asyncio import async_session
from urllib.parse import quote_plus

password = "Harekrishna@123$"
password_encoded = quote_plus(password)
print(f"{password_encoded= }")
DB_URL = "postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
# DB_URL = "postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


def get_db():
    darwin_db = Darwin(
        database_url=DB_URL.format(
            POSTGRES_USER="postgres",
            POSTGRES_PASSWORD=password_encoded,
            POSTGRES_SERVER="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_DB="darwin"
        )
    )
    db = darwin_db.session_local()  # connection takes from pool
    try:
        yield db  # inject this into db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()  # returned to pool

#
# async def get_db():
#     darwin_obj = Darwin(
#             database_url=DB_URL.format(
#                 POSTGRES_USER="postgres",
#                 POSTGRES_PASSWORD="Radhamohan@333",
#                 POSTGRES_SERVER="localhost",
#                 POSTGRES_PORT=5432,
#                 POSTGRES_DB="darwin"
#             )
#         )
#     async with darwin_obj.async_session_local() as session:
#         try:
#             yield session
#             session.commit()
#         except:
#             session.rollback()
#             raise
#         finally:
#             session.close()
