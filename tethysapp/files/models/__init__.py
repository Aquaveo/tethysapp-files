from tethysext.atcore.models.app_users import initialize_app_users_db
from tethysext.atcore.models.file_database import FileDatabase, FileCollection


def init_primary_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    # Initialize app users tables
    initialize_app_users_db(engine, first_time)