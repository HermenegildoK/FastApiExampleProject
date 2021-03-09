from simple_example.repository_implementation.memory_repo import Database
from simple_example.repository_implementation.sqlalchemy_repo import setup_db_connection
from simple_example.web_app_example.settings import Settings

database = None


def set_database(database_settings: Settings):
    global database
    if database_settings.USE_DATABASE:
        database = setup_db_connection(database_settings.DATABASE_URL)
    else:
        database = Database()
