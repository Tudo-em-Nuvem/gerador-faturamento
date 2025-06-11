from domain.service.drive import DriveService
from domain.utils.generate_plan import GeneratePlan
from domain.service.dir_checker import DirCheckerService
from monitor_controller import MonitorController

class App:
  def __init__(self):
    self.drive_service = DriveService()
    self.generate_plan_service = GeneratePlan()
    self.service = DirCheckerService(self.drive_service, self.generate_plan_service)
    self.monitor_controller = MonitorController(self.service)

  def run(self):
    print("Iniciando o monitoramento do Google Drive...")
    self.monitor_controller.run_monitor_loop()

if __name__ == "__main__":
  app = App()
  app.run()
