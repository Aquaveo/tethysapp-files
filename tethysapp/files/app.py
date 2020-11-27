from tethys_sdk.base import TethysAppBase, url_map_maker


class Files(TethysAppBase):
    """
    Tethys app class for Files.
    """

    name = 'Files'
    index = 'files:home'
    icon = 'files/images/icon.gif'
    package = 'files'
    root_url = 'files'
    color = '#f54245'
    description = 'A project used to demonstrate the FileDatabase functionality of ATCORE.'
    tags = '"File","Database","File Database"'
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='files',
                controller='files.controllers.home'
            ),
        )

        return url_maps