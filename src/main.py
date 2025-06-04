import subprocess
import sys
import os

# Ajusta o caminho para o requirements.txt
requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')

# Instala/atualiza as dependências necessárias
print("Instalando/atualizando dependências...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])

# Verifica especificamente o openpyxl
print("Verificando instalação do openpyxl...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "openpyxl"])

from drive_service import DriveService
from generate_plan import GeneratePlan
from service import Service
from monitor_controller import MonitorController

class App:
  def __init__(self):
    self.drive_service = DriveService()
    self.generate_plan_service = GeneratePlan()
    self.service = Service(self.drive_service, self.generate_plan_service)
    self.monitor_controller = MonitorController(self.service, self.drive_service)

  def run(self):
    print("Iniciando o monitoramento do Google Drive...")
    self.monitor_controller.run_monitor_loop()

if __name__ == "__main__":
  app = App()
  app.run()