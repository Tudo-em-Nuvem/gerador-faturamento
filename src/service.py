from drive_service import DriveService
from generate_plan import GeneratePlan
from config import FOLDER_ID, DOWNLOAD_DIR
import os

class Service:
  def __init__(self, drive_service: DriveService, generate_plan_service: GeneratePlan): 
    self.drive_service = drive_service
    self.__generate_plan_service = generate_plan_service

  def __download_itens_from_dir(self, files_to_download):
    print("\nIniciando download dos arquivos...")
    for file_info in files_to_download:
      file_id = file_info['id']
      file_name = file_info['name']
      mime_type = file_info.get('mimeType', 'application/octet-stream') # Default para tipo genérico

      if mime_type == 'application/vnd.google-apps.folder':
        print(f"Pulando '{file_name}' (é uma pasta).")
        continue

      if mime_type != '': self.drive_service.download_file(file_id, file_name, mime_type)

  def create_dir_downloads(self):
    if not os.path.exists(DOWNLOAD_DIR):
      os.makedirs(DOWNLOAD_DIR)
      print(f"Diretório de download '{DOWNLOAD_DIR}' criado.")
    else:
      print(f"Diretório de download '{DOWNLOAD_DIR}' já existe.")

  def clear_dir_downloads(self):
     for file in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, file)
        if os.path.isfile(file_path):
          os.remove(file_path)
          print(f"Arquivo '{file}' removido do diretório de download.")

  def remove_file_uploaded(self, name: str):
    if not name.startswith("./"):
      name = f"./{name}"

    if os.path.exists(name):
      os.remove(name)
      print(f"Arquivo '{name}' removido após upload.")

    else:
      print(f"Arquivo '{name}' não encontrado para remoção.")

  def exec_check_fat_dir(self):
    files = self.drive_service.list_files_in_folder(FOLDER_ID)

    if len(files) != 2: return

    self.__download_itens_from_dir(files)
    name = self.__generate_plan_service.exec()
    self.drive_service.upload_file_to_drive_folder(f"{DOWNLOAD_DIR}/{name}", FOLDER_ID)

    self.clear_dir_downloads()
    self.remove_file_uploaded(name)
