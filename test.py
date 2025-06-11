import pandas as pd
import os
import re 

class ReportGenerator:
  def get_data_omie(self):
    for i in os.listdir("./planilhas"):
      if str(i).endswith(".xlsx"):
        # Attempt to read the Excel file with the current header row
        data_omie = pd.read_excel(f'./planilhas/{str(i)}', header=1)
        print(f"Successfully read {i} as Excel")
        data_omie.dropna(subset=['Descrição do Serviço (completa)'], inplace=True)
        return data_omie
      
  def get_data_google(self):
    for i in os.listdir("./planilhas"):
      if str(i).endswith(".csv"):
        data_google = pd.read_csv(f'./planilhas/{str(i)}')
        print(f"Successfully read {i} as CSV")
        return data_google

  def definir_dominio(self, desc):
    REGEX_DOMAIN = r"\b(?:[a-zA-Z0-9][a-zA-Z0-9\-_@]*\.)+(?:xn--[a-zA-Z0-9]+|[a-zA-Z0-9]{2,}|[a-zA-Z0-9]{2}\.[a-zA-Z0-9]{2})\b"
    padraoDomain = re.compile(REGEX_DOMAIN)
    resultados = padraoDomain.findall(desc)

    cliente = None

    if len(resultados) > 1:
      cliente = resultados[0]
      if self.eh_float(cliente):
        cliente = resultados[1]

    elif len(resultados) == 1:
      cliente = resultados[0]

    return cliente

  def extrair_plano(self, desc: str) -> str:
    if 'microsoft' in desc.lower(): return 'microsoft'
    PLANOS_NA_DESC = [('stater', 'starter'), ('workspace standard', 'business standard', 'standard'), ('workspace plus', 'business plus'),
                      ('workspace enterprise', 'enterprise standard', 'enterprise'), 'enterprise plus']
    RETURN_PLANOS = ['Business Starter', 'Business Standard', 'Business Plus', 'Enterprise Standard', 'Enterprise Plus']

    return_plano = None

    for plano, retorno in zip(PLANOS_NA_DESC, RETURN_PLANOS):
      if type(plano) == tuple:
        for i in plano:

          if i in desc.lower().strip():
            return_plano = retorno

      else:
        if plano in desc.lower().strip():
          return_plano = retorno

    return return_plano

  def eh_float(self, valor: str):
    try:
      float(valor)
      return True
    except ValueError:
      return False

  def fill_nans_with_last(self, item):
      last = None
      result = []
      for d in item:
          if not pd.isna(d):
              last = d
          result.append(last)
      return result

  def exec_report(self):
    data_omie = self.get_data_omie()
    data_google = self.get_data_google()

    domains_omie = self.fill_nans_with_last(data_omie['Cliente (Nome Fantasia)'].to_list())
    descs_omie = data_omie['Descrição do Serviço (completa)'].to_list()
    situations_omie = self.fill_nans_with_last(data_omie['Situação'].to_list())
    day_omie = self.fill_nans_with_last(data_omie['Dia de Faturamento'].to_list())
    quantity_omie = self.fill_nans_with_last(data_omie['Quantidade'].to_list())
    archiveds_omie = []

    counter = 0
    while counter < len(domains_omie):
  
  
      if type(descs_omie[counter]) != str:
        counter += 1
        continue

      if ('arquivado' in descs_omie[counter].lower()) or ('arquivada' in descs_omie[counter].lower()):
        archiveds_omie.append(True)
      else: archiveds_omie.append(False)

      domain = self.definir_dominio(descs_omie[counter])
      if not domain and type(domains_omie[counter]) == str: domain = domains_omie[counter]

      if not domain:
        i = 1

        while True:
          domain = domains_omie[counter - i]
          if type(domain) == str:
            break

          i += 1

      domains_omie[counter] = domain

      plano = self.extrair_plano(descs_omie[counter])

      if plano:
        if domain in domains_omie[:counter]:
          index = domains_omie[:counter].index(domain)
          descs_omie[index] = plano
        descs_omie[counter] = plano

      else:
        i = 1
        while i < 5:
          if domain in domains_omie[counter - i]:
            if self.extrair_plano(descs_omie[counter-i]):
              descs_omie[counter] = descs_omie[counter-i]
            break
          i += 1

      counter += 1

    omie_clients = list(zip(domains_omie, descs_omie, situations_omie, day_omie, quantity_omie, archiveds_omie))

    omie_clients_objects = {}
    for domain, plan, situation, day, quantity, archived in omie_clients:
        if domain not in omie_clients_objects:
            omie_clients_objects[domain] = {"domain": domain, "planos": [], "fatDay": day, "situation": situation}
        omie_clients_objects[domain]["planos"].append({"name": plan, "quantity": quantity, "archived": archived})

    omie_clients_objects = list(omie_clients_objects.values())
    print(omie_clients_objects)

if __name__ == "__main__":
  report_generator = ReportGenerator()
  report_generator.exec_report()
