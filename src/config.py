# Configuration settings for the project

# Google Drive API configuration
SERVICE_ACCOUNT_FILE = './token-drive.json'  # Path to the service account file
SCOPES = ['https://www.googleapis.com/auth/drive']  # Scopes for Google Drive API access

# Google Drive folder IDs
FOLDER_FATURAMENTO_ID = '1M1t6nhxRVEbHkkcIqzQmC0i0WnSRqedQ'  # ID of the Google Drive folder
FOLDER_OFX_ID = '1cVJomAa6JPMEoJXJaioFLQxotJVrrw4l'  # ID of the Google Drive folder
FOLDER_SUBSCRIPTIONS_ID = '1yzkZs2BWma0aJVoVVvDmEJtRQ8q37RMP'  # ID of the Google Drive folder for subscriptions
FOLDER_ASAAS_OMIE_CHECKER_ID = "1qy_acXUADdRB0_vdZAfSshBt942XbBYC" # ID of the Google Drive folder for Asaas and Omie checker

# Local directories for storing files
FAT_DIR = './src/planilhas'  # Directory for downloaded files
OFX_DIR = './src/ofx'  # Directory for OFX files
SUBSCRIPTIONS_DIR = './src/subscriptions'  # Directory for subscriptions
ASAAS_OMIE_CHECKER_DIR = './src/asaas-omie-checker'  # Directory for Asaas and Omie checker

# Mapping of MIME types for exporting Google Workspace files
MIME_TYPE_MAP = {
  'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}