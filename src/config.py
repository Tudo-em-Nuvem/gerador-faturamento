# Configuration settings for the project

SERVICE_ACCOUNT_FILE = './token-drive.json'  # Path to the service account file
SCOPES = ['https://www.googleapis.com/auth/drive']  # Scopes for Google Drive API access
FOLDER_FATURAMENTO_ID = '1M1t6nhxRVEbHkkcIqzQmC0i0WnSRqedQ'  # ID of the Google Drive folder
FOLDER_OFX_ID = '1cVJomAa6JPMEoJXJaioFLQxotJVrrw4l'  # ID of the Google Drive folder
DOWNLOAD_DIR = './src/planilhas'  # Directory for downloaded files
OFX_DIR = './src/ofx'  # Directory for OFX files
# Mapping of MIME types for exporting Google Workspace files
MIME_TYPE_MAP = {
  'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}