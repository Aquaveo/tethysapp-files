import os
import uuid
import json

from tethysext.atcore.models.app_users import AppUsersBase
from tethysext.atcore.models.file_database import FileCollection, FileCollectionClient, \
    FileDatabase, FileDatabaseClient

from .app import Files as app


def init_primary_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    # Create all the tables
    AppUsersBase.metadata.create_all(engine)


def add_uploaded_files(workspace, session, name, database_id, upload_files):
    """
    Upload a new file collection
    """
    # Serialize data to json
    database_uuid = uuid.UUID('{' + database_id + '}')
    metadata_dict = {
        'name': name,
    }

    file_collection_client = FileCollectionClient.new(session=session, file_database_id=database_uuid,
                                                      meta=metadata_dict)
    for f in upload_files:
        temp_file_dir = os.path.join(workspace.path, 'temp')
        temp_file_path = os.path.join(temp_file_dir, f.name)
        if not os.path.exists(temp_file_dir):
            os.makedirs(temp_file_dir, exist_ok=True)
        with open(temp_file_path, 'wb') as tf:
            tf.write(f.read())
        file_collection_client.add_item(temp_file_path, move=True)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def add_new_file_database(db_directory, name):
    """
    Add a new FileDatabase
    """
    # Get connection/session to database
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    # Serialize data to json
    metadata_dict = {
        'name': name,
    }

    _ = FileDatabaseClient.new(session, db_directory, meta=metadata_dict)


def get_all_file_databases():
    """
    Get a list of all file databases.
    """
    # Get connection/session to database
    Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
    session = Session()

    file_databases = session.query(FileDatabase).all()
    databases = []
    for file_database in file_databases:
        file_database_client = FileDatabaseClient(session, file_database.id)
        file_collection_count = session.query(FileCollection).filter_by(file_database_id=file_database.id).count()
        databases.append(
            {
                'id': file_database.id,
                'path': file_database_client.path,
                'collection_count': file_collection_count,
                'meta': file_database_client.instance.meta,
            }
        )
    return databases


def get_file_collections_for_database(session, database_id):
    file_database_uuid = uuid.UUID('{' + database_id + '}')
    file_collections = session.query(FileCollection).filter_by(file_database_id=file_database_uuid)
    collections = []
    for collection in file_collections:
        file_collection_client = FileCollectionClient(session, collection.id)
        collections.append(
            {
                'id': file_collection_client.instance.id,
                'path': file_collection_client.path,
                'meta': file_collection_client.instance.meta,
                'files': [x for x in file_collection_client.files]
            }
        )
    return collections
