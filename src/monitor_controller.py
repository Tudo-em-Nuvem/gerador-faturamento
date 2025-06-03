from service import Service
from drive_service import DriveService
import time

class MonitorController:
  def __init__(self, service: Service, drive_service: DriveService, ):
    self.service = service

  def run_monitor_loop(self):
    while True:
      try:
        self.service.exec_check_fat_dir()

      except Exception as e:
        print(f"Erro durante a execução do monitor:\n{e}")

      # Aguarda um tempo antes de verificar novamente
      time.sleep(60)
