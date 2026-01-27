from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.asyncio import (async_sessionmaker, create_async_engine)


class Darwin:
    def __init__(self, database_url):
        self.engine = create_engine(
            url=database_url,
            pool_size=100,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=360,
            pool_timeout=60 * 60
        )

        try:
            # attempt to connect to database
            with self.engine.connect() as connection:
                print("connection established successfully..")
        except Exception as ex:
            print(f"database connection failed due to -> {ex}")
            raise ConnectionError(f"Failed to db connect due to - > {ex}")

        self.session_local = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False
        )


# class Darwin:
#     def __init__(self, database_url):
#         self.engine = create_async_engine(database_url)
#         try:
#             print("trying to establish a db connection..")
#             with self.engine.connect() as connection:
#                 print("connection established successfully.")
#         except Exception as ex:
#             print(f"failed to connect to db due to => {ex}")
#             raise ConnectionError("DATABASE connection failed.")
#
#         # create a local session
#         self.async_session_local = async_sessionmaker(bind=self.engine,
#                                                       expire_on_commit=False
#                                                       )
