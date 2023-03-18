# Figma-Confluence Sync

Figma-Confluence Sync is a Python script that automates the process of updating Confluence page attachments with the
latest images from Figma files. It retrieves attachments from Confluence, requests images from Figma based on the
mapping between Confluence attachments and Figma files, and updates the Confluence page with the requested images.

## Prerequisites

- Python 3.10
- Docker (optional, for deployment)

## Installation

1. Clone the repository:

```commandline
git clone https://github.com/yourusername/figma-confluence-sync.git
cd figma-confluence-sync
```

2. Install the required packages:

```commandline
pip install -r requirements.txt
```

3. Copy the `.env.example` file to `.env`:

```commandline
cp .env.example .env
```

4. Fill in the necessary environment variables in the `.env` file:

- `CONFLUENCE_API_KEY`: Your Confluence API key.
- `CONFLUENCE_EMAIL`: Your Confluence email.
- `CONFLUENCE_BASE_URL`: The base URL of your Confluence instance.
- `CONFLUENCE_PAGE_ID`: The ID of the Confluence page to sync with Figma.
- `CONFLUENCE_FILE_PATTERN_FILTER`: The file pattern filter for Confluence attachments.
- `FIGMA_API_KEY`: Your Figma API key.
- `FIGMA_TEAM_ID`: Your Figma team ID.
- `FIGMA_FILES_FILTER`: The file pattern filter for Figma files.

## Usage

Run the script:

```commandline
python main.py
```

## Deployment with Docker

1. Build the Docker image:

```commandline
docker build -t figma-confluence-sync .
```

2. Run the Docker container:

```commandline
docker run -d --name figma-confluence-sync --env-file .env your-dockerhub-username/figma-confluence-sync:latest
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for more information.
