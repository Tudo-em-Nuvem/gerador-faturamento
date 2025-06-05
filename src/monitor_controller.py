from service import Service
import time

class MonitorController:
  def __init__(self, service: Service):
    self.service = service

  def run_monitor_loop(self):
    while True:
      try:
        self.service.exec_check_fat_dir()
        self.service.exec_check_ofx_gen()
      
      except Exception as e:
        print(f"Erro durante a execução do monitor:\n{e}")

      # Aguarda um tempo antes de verificar novamente
      time.sleep(60)
