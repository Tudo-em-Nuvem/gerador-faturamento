import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload # Para baixar arquivos
import io # Para usar BytesIO
from googleapiclient.http import MediaFileUpload # Importar para upload de arquivos
from generate_plan import GeneratePlan

# --- Configurações ---
SERVICE_ACCOUNT_FILE = './token-drive.json' # Verifique se o caminho está correto
SCOPES = ['https://www.googleapis.com/auth/drive'] # Escopo 'drive' permite leitura e escrita
FOLDER_ID = '1M1t6nhxRVEbHkkcIqzQmC0i0WnSRqedQ' # ID da pasta no Drive Compartilhado
DOWNLOAD_DIR = './planilhas' # Diretório onde os arquivos serão salvos

# --- Mapeamento de MIME Types para Exportação (apenas para arquivos do Google Workspace) ---
# Você pode adicionar mais, se necessário
MIME_TYPE_MAP = {
  'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

def authenticate_drive_service():
    """Autentica a conta de serviço e retorna o objeto de serviço do Drive."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        credentials.refresh(Request())

        if not credentials.valid:
            print("ERRO: Credenciais não válidas. Não é possível prosseguir.")
            return None

        service = build('drive', 'v3', credentials=credentials)
        print("Autenticação do Google Drive bem-sucedida.")
        return service
  
    except Exception as e:
        print(f"Erro durante a autenticação: {e}")
        return None

def list_files_in_folder(service, folder_id):
    """
    Lista os arquivos em uma determinada pasta do Google Drive,
    com suporte para Shared Drives.
    """
    query = f"'{folder_id}' in parents and trashed=false"
    
    files = []
    page_token = None
    try:
        while True:
            results = service.files().list(
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

        if not files:
            print(f'Nenhum arquivo encontrado na pasta com ID: {folder_id}.')
        else:
            print(f'Arquivos encontrados na pasta com ID {folder_id}:')
            for file in files:
              #print(f"  Nome: {file['name']}, ID: {file['id']}, Tipo: {file.get('mimeType', 'N/A')}")
              pass
        return files

    except Exception as e:
        print(f"Ocorreu um erro ao listar arquivos: {e}")
        return []

def download_file(service, file_id, file_name, mime_type):
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
                request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            
            else: # Este é o bloco para arquivos não-Google Workspace
              # É um arquivo não-Google Workspace, pode ser baixado diretamente
              print(f"Baixando '{file_name}' (ID: {file_id}) para '{file_path}'...")
              request = service.files().get_media(fileId=file_id)

        else:
            # É um arquivo não-Google Workspace, pode ser baixado diretamente
            print(f"Baixando '{file_name}' (ID: {file_id}) para '{file_path}'...")
            request = service.files().get_media(fileId=file_id)

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
    
def upload_file_to_drive_folder(service, local_file_path, drive_folder_id):
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

        # Objeto MediaFileUpload para lidar com o upload do conteúdo do arquivo
        # O mimetype 'application/octet-stream' é um mimetype genérico,
        # o Drive tentará inferir o tipo correto. Para maior precisão,
        # você pode usar a biblioteca `mimetypes` para detectar:
        # import mimetypes
        # mime_type, _ = mimetypes.guess_type(local_file_path)
        # if mime_type is None: mime_type = 'application/octet-stream'
        media = MediaFileUpload(local_file_path, mimetype='application/octet-stream', resumable=True)

        print(f"Fazendo upload de '{file_name}' para a pasta do Drive '{drive_folder_id}'...")

        # Executa a requisição de upload
        # supportsAllDrives=True é necessário para uploads em Shared Drives
        file = service.files().create(
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

# --- Fluxo Principal ---
if __name__ == '__main__':
    # 1. Autenticar o serviço do Drive
    drive_service = authenticate_drive_service()

    if drive_service:
        while True:
            # 2. Listar arquivos na pasta (com suporte a Shared Drives)
            files_to_download = list_files_in_folder(drive_service, FOLDER_ID)
            if len(files_to_download) != 2:
                print("diferente de 2")
                time.sleep(60)
                continue
            # 3. Baixar cada arquivo listado
            if files_to_download:
                print("\nIniciando download dos arquivos...")
                for file_info in files_to_download:
                    file_id = file_info['id']
                    file_name = file_info['name']
                    mime_type = file_info.get('mimeType', 'application/octet-stream') # Default para tipo genérico

                    if mime_type == 'application/vnd.google-apps.folder':
                        print(f"Pulando '{file_name}' (é uma pasta).")
                        continue

                    download_file(drive_service, file_id, file_name, mime_type)

                plan_generator = GeneratePlan()
                name = plan_generator.main()
                name = f"./{name}"
                upload_file_to_drive_folder(drive_service, name, FOLDER_ID)
                print("Todos os arquivos foram baixados e o plano foi gerado e enviado com sucesso.")

                # Limpa pasta "planilhas"
                for file in os.listdir(DOWNLOAD_DIR):
                    file_path = os.path.join(DOWNLOAD_DIR, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Arquivo '{file}' removido do diretório de download.")
                
                # Remove arquivo enviado
                if os.path.exists(name):
                    os.remove(name)
                    print(f"Arquivo '{name}' removido após upload.")
                else:
                    print(f"Arquivo '{name}' não encontrado para remoção.")

            else:
                print("Nenhum arquivo para baixar.")

            # Espera 60 segundos antes de verificar novamente
            print("Aguardando 60 segundos antes de verificar novamente...")
            time.sleep(60)
