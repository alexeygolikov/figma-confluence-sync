import base64
import re
from datetime import datetime
from typing import Pattern

import requests

from figma_confluence_mapping import Figma2ConfluenceAttachment


class Confluence:
    def __init__(self, base_url: str, api_key: str, email: str, export: str):
        self.base_url = base_url
        self.filePatternFilter: Pattern[str] = re.compile(export, re.IGNORECASE)
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(f'{email}:{api_key}'.encode()).decode()}",
            "Accept": "application/json",
        }

    # 1. Get a Confluence page and its child pages
    def get_pages(self, page_id) -> list[str]:
        pages = [page_id]
        url = f"{self.base_url}/api/v2/pages/{page_id}/children"
        response = requests.get(url, headers=self.headers).json()

        for child_page in response["results"]:
            pages.extend(self.get_pages(child_page["id"]))

        return pages

    # 2. Find PNG attachments in Confluence pages
    def find_attachments(self, pages) -> dict[str, list[Figma2ConfluenceAttachment]]:
        attachments = {}

        for page in pages:
            url = f"{self.base_url}/api/v2/pages/{page}/attachments"
            response = requests.get(url, headers=self.headers).json()

            for attachment in response["results"]:
                if re.search(self.filePatternFilter, attachment["title"]) and attachment["mediaType"].startswith(
                        "image/"):
                    # remove extension from title
                    attachment_title = attachment["title"].split(".")[0]
                    if attachment_title not in attachments:
                        attachments[attachment_title] = []
                    attachments[attachment_title].append(Figma2ConfluenceAttachment(
                        attachment_id=attachment["id"],
                        attachment_title=attachment_title,
                        attachment_media_type_extension=attachment["mediaType"].replace("image/", ""),
                        created=datetime.fromisoformat(attachment['version']['createdAt'].replace("Z", "+00:00")),
                        page_id=page
                    ))

        return attachments

    # 7. Update Confluence attachments
    def update_attachments(self, attachments: dict[str, list[Figma2ConfluenceAttachment]]):
        results = []
        headers = self.headers.copy()
        headers['X-Atlassian-Token'] = 'nocheck'

        for title, tattachments in attachments.items():
            for attachment in tattachments:
                file_path = attachment.figma_downloaded_file_path
                if not file_path:
                    continue

                url = f"{self.base_url}/rest/api/content/{attachment.page_id}/child/attachment/{attachment.attachment_id}/data"

                with open(file_path, "rb") as f:
                    response = requests.post(url, headers=headers, files={"file": f})
                if response.status_code != 200:
                    print(
                        f"Error updating attachment {attachment.attachment_id}"
                        f" in page {attachment.page_id}({response.status_code}): {response.text}")
                else:
                    results.append(attachment)
        return results
