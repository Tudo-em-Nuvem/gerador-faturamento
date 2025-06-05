from drive_service import DriveService
from utils.generate_plan import GeneratePlan
from utils.ofx_generator import OfxGenerator

from config import FOLDER_FATURAMENTO_ID, FOLDER_OFX_ID, DOWNLOAD_DIR, OFX_DIR
import os

class Service:
  def __init__(self, drive_service: DriveService, generate_plan_service: GeneratePlan): 
    self.drive_service = drive_service
    self.__generate_plan_service = generate_plan_service
    self.create_dirs()

  def __download_itens_from_dir(self, files_to_download):
    print("\nIniciando download dos arquivos...")
    for file_info in files_to_download:
      file_id = file_info['id']
      file_name = file_info['name']
      mime_type = file_info.get('mimeType', 'application/octet-stream') # Default para tipo genérico

      if mime_type == 'application/vnd.google-apps.folder':
        print(f"Pulando '{file_name}' (é uma pasta).")
        continue
        
      self.drive_service.download_file(file_id, file_name, mime_type)

  def create_dirs(self):
    if not os.path.exists(DOWNLOAD_DIR):
      os.makedirs(DOWNLOAD_DIR)
      print(f"Diretório de download '{DOWNLOAD_DIR}' criado.")

    if not os.path.exists(OFX_DIR):
      os.makedirs(OFX_DIR)
      print(f"Diretório OFX '{OFX_DIR}' criado.")

  def clear_dir(self, dir: str):
     for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
          os.remove(file_path)
          print(f"Arquivo '{file}' removido do diretório de download.")

  def exec_check_fat_dir(self):
    files = self.drive_service.list_files_in_folder(FOLDER_FATURAMENTO_ID)

    if len(files) != 2: return

    self.__download_itens_from_dir(files)
    print("Todos os downloads foram efetuados")
    name = self.__generate_plan_service.exec()
    self.drive_service.upload_file_to_drive_folder(f"{DOWNLOAD_DIR}/{name}", FOLDER_FATURAMENTO_ID)

    self.clear_dir(DOWNLOAD_DIR)

  def exec_check_ofx_gen(self):
    ofx_gen = OfxGenerator() 
    archive_name = ofx_gen.extract_name_from_dates()
    if not os.path.isfile(OFX_DIR +'/' + archive_name + '.html'):
      self.clear_dir(OFX_DIR)
      ofx_gen.main()
      print("Arquivo OFX gerado com sucesso.")
      self.drive_service.upload_file_to_drive_folder(f"{OFX_DIR}/{archive_name}.html", FOLDER_OFX_ID)

    else: print("arquivo ja existe")
