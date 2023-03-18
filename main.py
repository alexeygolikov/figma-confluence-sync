"""
This script retrieves attachments from a Confluence page, requests images from Figma based on the mapping between
Confluence attachments and Figma files, and updates the Confluence page with the requested images.
"""

import os
import logging

from dotenv import load_dotenv
from confluence_client import Confluence
from figma_client import Figma
from figma_confluence_mapping import Figma2ConfluenceAttachment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()  # load environment variables from .env file

confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
confluence_email = os.getenv("CONFLUENCE_EMAIL")
confluence_base_url = os.getenv("CONFLUENCE_BASE_URL")
confluence_page_id = os.getenv("CONFLUENCE_PAGE_ID")
confluence_file_pattern_filter = os.getenv("CONFLUENCE_FILE_PATTERN_FILTER")
figma_api_key = os.getenv("FIGMA_API_KEY")
figma_team_id = os.getenv("FIGMA_TEAM_ID")
figma_files_filter = os.getenv("FIGMA_FILES_FILTER")

confluence = Confluence(confluence_base_url, confluence_api_key, confluence_email, confluence_file_pattern_filter)
figma = Figma(figma_api_key, figma_team_id, figma_files_filter)

# Retrieve pages from Confluence
logging.info("Retrieving pages from Confluence...")
pages: list[str] = confluence.get_pages(confluence_page_id)

# Find attachments on Confluence pages
logging.info("Finding attachments on Confluence pages...")
attachments: dict[str, list[Figma2ConfluenceAttachment]] = confluence.find_attachments(pages)
logging.info(f"Found {len(attachments)} attachments.")

# Retrieve Figma files
logging.info("Retrieving Figma files...")
figma_files: list[str] = figma.get_files()
logging.info(f"Retrieved {len(figma_files)} Figma files.")

# Find mappings between Figma files and Confluence attachments
logging.info("Finding mappings between Figma files and Confluence attachments...")
matching_mappings = figma.find_nodes_mappings(figma_files, attachments)
logging.info(f"Found {len(matching_mappings)} mappings.")

# Request images from Figma using matching mappings
logging.info("Requesting images from Figma...")
figma.request_images(matching_mappings)
logging.info(f"Downloaded {len(figma.downloaded_files)} images.")

# Update Confluence attachments with requested images
logging.info("Updating Confluence attachments...")
updated_responses = confluence.update_attachments(attachments)
logging.info(f"Updated {len(updated_responses)} attachments.")
