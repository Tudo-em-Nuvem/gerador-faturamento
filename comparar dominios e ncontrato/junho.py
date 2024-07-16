import re
import pandas as pd
REGEX_DOMAIN = r"\b(?:[a-zA-Z][a-zA-Z0-9\-_@]*\.)+(?:xn--[a-zA-Z0-9]+|[a-zA-Z0-9]{2,}|[a-zA-Z0-9]{2}\.[a-zA-Z0-9]{2})\b"
class Service:
  def __init__(self):

    self.coluna_cliente_pivot:  list = []
    self.coluna_desc_pivot:     list = []
    self.coluna_contrato_pivot: list = []

    self.coluna_dominio_junho:  list = []
    self.coluna_contrato_junho: list = []

    self.itens_pivot:           list = []
    self.itens_junho:           list = []

    self.itens_divergentes:     list = []

    for linha in range(10):
      try:
        dados_omie_excel = pd.read_excel("pivot.xlsx", header=linha)
        dados_omie_excel = dados_omie_excel.drop(dados_omie_excel.index[-1])
        self.coluna_cliente_pivot = dados_omie_excel["Cliente (Nome Fantasia)"].to_list()
        self.coluna_desc_pivot = dados_omie_excel["Descrição do Serviço (completa)"].to_list()
        self.coluna_contrato_pivot = dados_omie_excel["Contrato"].to_list()
        break
      except: continue

    dados_junho = pd.read_excel("julho.xlsx", header=0)
    self.coluna_dominio_junho = dados_junho["ANUAL"].to_list()
    self.coluna_contrato_junho = dados_junho["N. do contrato"].to_list()

    self.gerar_lista_de_itens_pivot()
    self.gerar_lista_de_itens_junho()
    self.verificar()

    for item in self.itens_divergentes:
      print(f'Domínio: {item["dominio"]} - {item["message"]} - {item["contrato_pivot"]}')

  def gerar_lista_de_itens_pivot(self):
    ultimo_domain = None
    nContrato = None
    for nome, desc, contrato in zip(self.coluna_cliente_pivot, self.coluna_desc_pivot, self.coluna_contrato_pivot):
      dominio = None
      if type(nome) == str: ultimo_domain = nome
      if type(contrato) == str: nContrato = contrato

      padraoDomain = re.compile(REGEX_DOMAIN)
      cliente = padraoDomain.search(desc)

      if cliente: 
        if len(cliente.groups()) > 1: dominio = cliente.groups()[1]
        else: dominio = cliente.group()
      else: dominio = ultimo_domain

      exists = False
      for item in self.itens_pivot:
        if item["dominio"] == dominio: exists = True
      
      if not exists:
        self.itens_pivot.append({
         "dominio": dominio,
         "contrato": nContrato
        })

  def gerar_lista_de_itens_junho(self):
    for dominio, contrato in zip(self.coluna_dominio_junho, self.coluna_contrato_junho):
      if type(dominio) == str:
        self.itens_junho.append({
          "dominio": dominio,
          "contrato": contrato
        })

  def verificar(self):
    exists = False
    for item in self.itens_pivot:
      for item_junho in self.itens_junho:
        if item["dominio"].lower() == item_junho["dominio"].lower().split(' ')[0]:
          exists = True
          if item["contrato"] != item_junho["contrato"]:
            self.itens_divergentes.append({
              "dominio": item["dominio"],
              "message": "Contrato divergente",
              "contrato_pivot": item["contrato"]
              })

      if not exists:
        self.itens_divergentes.append({
          "dominio": item["dominio"],
          "message": "Domínio não encontrado no arquivo de julho",
          "contrato_pivot": item["contrato"],
        })
      exists = False

Service()
