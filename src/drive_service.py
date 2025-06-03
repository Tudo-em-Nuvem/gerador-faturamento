from google.oauth2 import service_account
from config import MIME_TYPE_MAP, SERVICE_ACCOUNT_FILE, SCOPES, DOWNLOAD_DIR
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

import os
import io

class DriveService:
  def __init__(self):
    """Autentica a conta de serviço e retorna o objeto de serviço do Drive."""
    try:
      credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
      )
      credentials.refresh(Request())

      if not credentials.valid:
        print("ERRO: Credenciais não válidas. Não é possível prosseguir.")
        self.service
        return

      service = build('drive', 'v3', credentials=credentials)
      print("Autenticação do Google Drive bem-sucedida.")
      self.service = service

    except Exception as e:
      print(f"Erro durante a autenticação: {e}")
      self.service = service
      return 

  def list_files_in_folder(self, folder_id):
      """
      Lista os arquivos em uma determinada pasta do Google Drive,
      com suporte para Shared Drives.
      """
      query = f"'{folder_id}' in parents and trashed=false"
      
      files = []
      page_token = None

      try:
        while True:
          results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, size)',
            pageToken=page_token,
            includeItemsFromAllDrives=True, # Necessário para Shared Drives
            supportsAllDrives=True # Necessário para Shared Drives
          ).execute()

          items = results.get('files', [])
          files.extend(items)
          page_token = results.get('nextPageToken', None)

          if page_token is None:
            break

        return files

      except Exception as e:
        print(f"Ocorreu um erro ao listar arquivos: {e}")
        return []

  def download_file(self, file_id, file_name, mime_type):
    """
    Baixa um arquivo do Google Drive para o diretório local.
    Trata arquivos nativos do Google Workspace e outros tipos.
    """
    # Garante que o diretório de download exista
    if not os.path.exists(DOWNLOAD_DIR):
      os.makedirs(DOWNLOAD_DIR)

    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    try:
      if 'google-apps' in mime_type:
        # É um arquivo nativo do Google Workspace, precisa ser exportado
        export_mime_type = MIME_TYPE_MAP.get(mime_type)
        if not export_mime_type:
          print(f"AVISO: Tipo de arquivo Google Docs '{mime_type}' sem mapeamento para exportação. Pulando '{file_name}'.")
          return False

        # Ajusta a extensão do arquivo para o tipo exportado
        base_name, _ = os.path.splitext(file_name)

        if 'spreadsheetml' in export_mime_type:
          file_path = os.path.join(DOWNLOAD_DIR, f"{base_name}.xlsx") 
          print(f"Exportando '{file_name}' (ID: {file_id}) como {export_mime_type} para '{file_path}'...")
          request = self.service.files().export_media(fileId=file_id, mimeType=export_mime_type)
        
        else: # Este é o bloco para arquivos não-Google Workspace
          # É um arquivo não-Google Workspace, pode ser baixado diretamente
          print(f"Baixando '{file_name}' (ID: {file_id}) para '{file_path}'...")
          request = self.service.files().get_media(fileId=file_id)

      else:
        # É um arquivo não-Google Workspace, pode ser baixado diretamente
        print(f"Baixando '{file_name}' (ID: {file_id}) para '{file_path}'...")
        request = self.service.files().get_media(fileId=file_id)

      fh = io.FileIO(file_path, 'wb')
      downloader = MediaIoBaseDownload(fh, request)
      done = False
      while done is False:
        status, done = downloader.next_chunk()
        # Opcional: print do progresso
        # print(f"Download progresso de '{file_name}': {int(status.progress() * 100)}%.")
      print(f"Download de '{file_name}' concluído com sucesso!")
      return True

    except Exception as e:
      print(f"ERRO ao baixar/exportar '{file_name}' (ID: {file_id}): {e}")
      return False

  def upload_file_to_drive_folder(self, local_file_path, drive_folder_id):
    """
    Faz o upload de um arquivo local para uma pasta específica do Google Drive.
    """
    file_name = os.path.basename(local_file_path) # Obtém apenas o nome do arquivo
    
    if not os.path.exists(local_file_path):
      print(f"ERRO: Arquivo local não encontrado: {local_file_path}")
      return None

    try:
      # Metadados do arquivo a ser criado no Drive
      file_metadata = {
        'name': file_name,
        'parents': [drive_folder_id] # Define a pasta pai no Drive
      }

      media = MediaFileUpload(local_file_path, mimetype='application/octet-stream', resumable=True)

      print(f"Fazendo upload de '{file_name}' para a pasta do Drive '{drive_folder_id}'...")

      # Executa a requisição de upload
      # supportsAllDrives=True é necessário para uploads em Shared Drives
      file = self.service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webContentLink, webViewLink', # Campos que queremos na resposta
        supportsAllDrives=True # Necessário para Shared Drives
      ).execute()

      print(f"Upload de '{file['name']}' concluído. ID do arquivo no Drive: {file['id']}")
      print(f"Link de visualização (Web): {file.get('webViewLink')}")
      return file

    except Exception as e:
      print(f"ERRO ao fazer upload de '{file_name}': {e}")
      return None
