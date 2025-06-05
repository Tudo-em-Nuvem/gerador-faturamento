from drive_service import DriveService
from utils.generate_plan import GeneratePlan
from service import Service
from monitor_controller import MonitorController

class App:
  def __init__(self):
    self.drive_service = DriveService()
    self.generate_plan_service = GeneratePlan()
    self.service = Service(self.drive_service, self.generate_plan_service)
    self.monitor_controller = MonitorController(self.service)

  def run(self):
    print("Iniciando o monitoramento do Google Drive...")
    self.monitor_controller.run_monitor_loop()

if __name__ == "__main__":
  app = App()
  app.run()
