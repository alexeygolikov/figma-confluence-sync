from datetime import datetime


class Figma2ConfluenceAttachment:
    def __init__(self, attachment_id: str, attachment_title: str, created: datetime, page_id: str,
                 attachment_media_type_extension: str):
        self.attachment_id = attachment_id
        self.attachment_title = attachment_title
        self.attachment_media_type_extension = attachment_media_type_extension
        self.created = created
        self.page_id = page_id
        self.figma_node_id: str = ""
        self.figma_file: str = ""
        self.figma_image_url: str = ""
        self.figma_downloaded_file_path: str = ""

    def fill_figma_properties(self, figma_file: str, figma_node_id: str):
        self.figma_file = figma_file
        self.figma_node_id = figma_node_id

    def fill_figma_image_url(self, figma_image_url: str):
        self.figma_image_url = figma_image_url

    def fill_figma_downloaded_file_path(self, figma_downloaded_file_path: str):
        self.figma_downloaded_file_path = figma_downloaded_file_path
