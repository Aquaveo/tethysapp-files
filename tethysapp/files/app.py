from tethys_sdk.app_settings import CustomSetting, PersistentStoreDatabaseSetting
from tethys_sdk.base import TethysAppBase, url_map_maker

from .models import init_primary_db


class Files(TethysAppBase):
    """
    Tethys app class for Files.
    """

    name = 'Files'
    index = 'files:home'
    icon = 'files/images/files.png'
    package = 'files'
    root_url = 'files'
    color = '#f54245'
    description = 'A project used to demonstrate the FileDatabase functionality of ATCORE.'
    tags = '"File","Database","File Database"'
    enable_feedback = False
    feedback_emails = []

    # Services
    DATABASE_NAME = 'primary_db'

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='files',
                controller='files.controllers.home',
            ),
            UrlMap(
                name='upload_files',
                url='files/uploads/upload',
                controller='files.controllers.upload_files',
            ),
            UrlMap(
                name='add_file_database',
                url='files/file_databases/add',
                controller='files.controllers.add_file_database',
            ),
            UrlMap(
                name='view_file_database',
                url='files/file_database/{file_database_id}',
                controller='files.controllers.view_file_database'
            ),
            UrlMap(
                name='delete_file_database',
                url='files/file_database/delete/{file_database_id}',
                controller='files.controllers.delete_file_database'
            ),
            UrlMap(
                name='delete_file_collection',
                url='files/file_collection/delete/{file_collection_id}',
                controller='files.controllers.delete_file_collection'
            ),
        )

        return url_maps

    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name='max_files',
                type=CustomSetting.TYPE_INTEGER,
                description='Maximum number of files allowed to upload.',
                required=False
            ),
        )
        return custom_settings

    def persistent_store_settings(self):
        """
        Define Persistent Store Settings.
        """
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name=self.DATABASE_NAME,
                description='primary database for Files',
                initializer='files.models.init_primary_db',
                required=True,
                spatial=True,
            ),
        )

        return ps_settings
