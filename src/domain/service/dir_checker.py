from domain.service.drive import DriveService
from domain.utils.asas_omie_checker import asaas_omie_checker
from domain.utils.subscriptions_comparator import subscriptions_comparator
from domain.utils.generate_plan import GeneratePlan
from domain.utils.ofx_generator import OfxGenerator
from config import ASAAS_OMIE_CHECKER_DIR, FOLDER_FATURAMENTO_ID, FOLDER_OFX_ID, FAT_DIR, FOLDER_SUBSCRIPTIONS_ID, OFX_DIR, SUBSCRIPTIONS_DIR, FOLDER_ASAAS_OMIE_CHECKER_ID
import os

class DirCheckerService:
  def __init__(self, drive_service: DriveService, generate_plan_service: GeneratePlan): 
    self.drive_service = drive_service
    self.__generate_plan_service = generate_plan_service
    self.create_dirs()

  def __download_itens_to_dir(self, files_to_download, dir):
    file_names = []
    print("\nIniciando download dos arquivos...")
    for file_info in files_to_download:
      file_id = file_info['id']
      file_name = file_info['name']
      mime_type = file_info.get('mimeType', 'application/octet-stream') # Default para tipo genérico

      if mime_type == 'application/vnd.google-apps.folder':
        print(f"Pulando '{file_name}' (é uma pasta).")
        continue
      
      file_names.append(file_name)
      self.drive_service.download_file(file_id, file_name, mime_type, dir)

    return file_names

  def create_dirs(self):
    dirs = [FAT_DIR, OFX_DIR, SUBSCRIPTIONS_DIR, ASAAS_OMIE_CHECKER_DIR]
    for dir in dirs:
      if not os.path.exists(dir):
        os.makedirs(dir)
        print(f"Diretório '{dir}' criado.")

  def clear_dir(self, dir: str):
     for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
          os.remove(file_path)
          print(f"Arquivo '{file}' removido do diretório de download.")

  def exec_check_fat_dir(self):
    files = self.drive_service.list_files_in_folder(FOLDER_FATURAMENTO_ID)

    if len(files) != 2: return

    self.__download_itens_to_dir(files, FAT_DIR)
    print("Todos os downloads foram efetuados")
    name = self.__generate_plan_service.exec()
    self.drive_service.upload_file_to_drive_folder(f"{FAT_DIR}/{name}", FOLDER_FATURAMENTO_ID)

    self.clear_dir(FAT_DIR)

  def exec_check_ofx_gen(self):
    ofx_gen = OfxGenerator() 
    archive_name = ofx_gen.extract_name_from_dates()
    if not os.path.isfile(OFX_DIR +'/' + archive_name + '.html'):
      self.clear_dir(OFX_DIR)
      ofx_gen.main()
      print("Arquivo OFX gerado com sucesso.")
      self.drive_service.upload_file_to_drive_folder(f"{OFX_DIR}/{archive_name}.html", FOLDER_OFX_ID)

  def exec_check_asaas_omie(self):
    files = self.drive_service.list_files_in_folder(FOLDER_SUBSCRIPTIONS_ID)

    if len(files) != 2: return

    file_names = self.__download_itens_to_dir(files, SUBSCRIPTIONS_DIR)
    print("Todos os downloads foram efetuados")
    subscriptions_comparator(file_names[0], file_names[1])
    self.drive_service.upload_file_to_drive_folder(f"{SUBSCRIPTIONS_DIR}/valores_diferentes.xlsx", FOLDER_SUBSCRIPTIONS_ID)

    self.clear_dir(SUBSCRIPTIONS_DIR)

  def exec_asaas_omie_checker(self):
    files = self.drive_service.list_files_in_folder(FOLDER_ASAAS_OMIE_CHECKER_ID)

    if len(files) != 2: return

    file_names = self.__download_itens_to_dir(files, ASAAS_OMIE_CHECKER_DIR)
    print("Todos os downloads foram efetuados")
    asaas_omie_checker(file_names[0], file_names[1])
    self.drive_service.upload_file_to_drive_folder(f"{ASAAS_OMIE_CHECKER_DIR}/asaas_que_nao_estao_na_omie.xlsx", FOLDER_ASAAS_OMIE_CHECKER_ID)

    self.clear_dir(ASAAS_OMIE_CHECKER_DIR)
