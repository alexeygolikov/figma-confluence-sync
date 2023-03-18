import concurrent.futures
import os
import threading
import re
from typing import Pattern, Optional

from datetime import datetime

import requests

from figma_confluence_mapping import Figma2ConfluenceAttachment

FIGMA_DOWNLOADS = "figma_downloads"


class Figma:
    def __init__(self, api_key, figma_team_id, figma_files_filter):
        self.mappings_by_node_id: dict[str, list[Figma2ConfluenceAttachment]] = {}
        self.headers = {
            "X-FIGMA-TOKEN": api_key,
        }
        self.figma_team_id = figma_team_id
        if figma_files_filter:
            self.figma_files_filter: Pattern[str] = re.compile(figma_files_filter, re.IGNORECASE)
        # Define a dictionary to store URLs and file paths
        self.downloaded_files = {}

        # Create a lock object to synchronize access to the downloaded_files dictionary
        self.lock = threading.Lock()

        # Define the subfolder to store the downloaded images
        self.download_folder = "figma_downloads"
        os.makedirs(self.download_folder, exist_ok=True)

    # 3. Get Figma projects and files
    def get_files(self) -> list[str]:
        url = f"https://api.figma.com/v1/teams/{self.figma_team_id}/projects"
        response = requests.get(url, headers=self.headers).json()
        projects = response["projects"]

        files = []

        for project in projects:
            url = f"https://api.figma.com/v1/projects/{project['id']}/files"
            response = requests.get(url, headers=self.headers).json()

            for file in response["files"]:
                if self.figma_files_filter is None or re.search(self.figma_files_filter, file["key"]):
                    files.append(file["key"])

        return files

    # 4. Scan Figma nodes for matching names
    def find_nodes_mappings(self, figma_files: list[str],
                            attachments: dict[str, list[Figma2ConfluenceAttachment]]
                            ) -> dict[str, list[Figma2ConfluenceAttachment]]:
        matching_nodes = {}

        def process_node(node: dict) -> Optional[list[Figma2ConfluenceAttachment]]:
            if "exportSettings" not in node:
                return None

            mappings = []

            for exportSettings in node["exportSettings"]:
                figma_export_file_name = node["name"] + exportSettings["suffix"]
                if figma_export_file_name in attachments:
                    att_mappings = [att for att in attachments[figma_export_file_name] if
                                    node_last_modified > att.created]

                    for att_mapping in att_mappings:
                        att_mapping.fill_figma_properties(file_key, node["id"])
                        mappings.append(att_mapping)
                        self.mappings_by_node_id.setdefault(node["id"], []).append(att_mapping)

            return mappings

        def scan_node(node: dict) -> list[Figma2ConfluenceAttachment]:
            node_mappings = process_node(node) or []

            if "children" in node:
                for child in node["children"]:
                    node_mappings.extend(scan_node(child))

            return node_mappings

        for file_key in figma_files:
            url = f"https://api.figma.com/v1/files/{file_key}"
            response = requests.get(url, headers=self.headers).json()
            node_last_modified = datetime.fromisoformat(response["lastModified"].replace("Z", "+00:00"))
            mappings = scan_node(response["document"])
            if mappings:
                matching_nodes[file_key] = mappings

        return matching_nodes

    # 5. Request Figma image URLs
    def request_images(self, matching_mappings: dict[str, list[Figma2ConfluenceAttachment]]):
        for file_key, mappings_from_file in matching_mappings.items():
            # Group mappings by attachment media type
            mappings_by_media_type = {}
            for mapping in mappings_from_file:
                media_type = mapping.attachment_media_type_extension
                if media_type in mappings_by_media_type:
                    mappings_by_media_type[media_type].append(mapping)
                else:
                    mappings_by_media_type[media_type] = [mapping]
            for media_type, mappings in mappings_by_media_type.items():
                node_ids = set(m.figma_node_id for m in mappings)
                url = f"https://api.figma.com/v1/images/{file_key}?ids={','.join(node_ids)}&format={media_type}&scale=2"
                response = requests.get(url, headers=self.headers).json()

                for node_id, image_data in response["images"].items():
                    for mn in self.mappings_by_node_id[node_id]:
                        mn.fill_figma_image_url(image_data)

                self.download_images(mappings)

    # 6. Download Figma images
    def download_image(self, mapping: Figma2ConfluenceAttachment):

        file_name = f"{mapping.attachment_title}.{mapping.attachment_media_type_extension}"
        file_path = os.path.join(self.download_folder, file_name)

        # Check if the file has already been downloaded
        with self.lock:
            if mapping.figma_image_url in self.downloaded_files:
                return
            else:
                self.downloaded_files[mapping.figma_image_url] = file_path
                mapping.fill_figma_downloaded_file_path(self.downloaded_files[mapping.figma_image_url])

        # Download the image
        response = requests.get(mapping.figma_image_url)

        # Check if the file already exists and delete it if necessary
        if os.path.isfile(file_path):
            os.remove(file_path)

        # Write the downloaded data to the file
        with open(file_path, "wb") as f:
            f.write(response.content)

    def download_images(self, mappings_from_file: list[Figma2ConfluenceAttachment]):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.download_image, mapping) for mapping in mappings_from_file]

            for future in concurrent.futures.as_completed(futures):
                future.result()
