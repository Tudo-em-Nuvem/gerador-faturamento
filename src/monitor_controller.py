from domain.service.dir_checker import DirCheckerService
import time

class MonitorController:
  def __init__(self, dir_service: DirCheckerService):
    self.service = dir_service

  def run_monitor_loop(self):
    while True:
      try:
        # self.service.exec_check_fat_dir()
        # self.service.exec_check_ofx_gen()
        # self.service.exec_check_asaas_omie()
        self.service.exec_oportunity_checker()
        time.sleep(10)  # Aguarda 10 segundos antes de verificar novamente
        # self.service.exec_asaas_omie_checker()
      except Exception as e:
        print(f"Erro durante a execução do monitor:\n{e}")

      # Aguarda um tempo antes de verificar novamente
      time.sleep(60)
