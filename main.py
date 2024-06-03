# the ultimate conciliator

import pandas as pd
import re

class Service:
  def __init__(self):
    self.cliente_atual_baseado_na_coluna_cliente = None
    self.status_atual_baseado_na_coluna_status = None
    self.ultimo_cliente_tratado = None
    self.rodada_inicial = False
    self.ultimo_cliente = None
    self.clientes_omie = []
    self.clientes_painel = []
    self.clientes_divergentes = []
    self.clientes_nao_divergentes = []

    for linha in range(10):
      try:
        dados_omie_excel = pd.read_excel('omie.xlsx', header=linha)
        dados_omie_excel = dados_omie_excel.drop(dados_omie_excel.index[-1])
        self.coluna_cliente = dados_omie_excel['Cliente (Nome Fantasia)'].to_list()
        self.coluna_licencas = dados_omie_excel['Quantidade'].to_list()
        self.coluna_desc = dados_omie_excel['Descrição do Serviço (completa)'].to_list()
        self.coluna_faturamento = dados_omie_excel['Dia de Faturamento'].to_list()
        self.coluna_situacao = dados_omie_excel['Situação'].to_list()
        linha = linha
        break
      except: continue

    dados_tdn = pd.read_csv('tdn.csv')
    self.coluna_cliente_tdn = dados_tdn['Cliente'].to_list()
    self.coluna_licencas_tdn = dados_tdn['Licenças atribuídas'].to_list()
    self.coluna_status = dados_tdn['Status da assinatura'].to_list()
    self.coluna_plano_pagamento_tdn = dados_tdn['Plano de pagamento'].to_list()
    self.coluna_sku_tdn = dados_tdn['SKU'].to_list()

  def extrair_plano(self, desc: str) -> str:
    PLANOS_NA_DESC = ['starter', ('workspace standard', 'business standard'), ('workspace plus', 'business plus'), 
                      ('workspace enterprise', 'enterprise standard', 'enterprise'), 'enterprise plus']
    RETURN_PLANOS = ['Business Starter', 'Business Standard', 'Business Plus', 'Enterprise Standard', 'Enterprise Plus']

    plano_encontrado = 'não encontrado'
    for plano, retorno in zip(PLANOS_NA_DESC, RETURN_PLANOS):
      if type(plano) == tuple:
        for i in plano:

          if i in desc.lower():
            plano_encontrado = retorno

      else:
        if plano in desc.lower():
          plano_encontrado = retorno

    if plano_encontrado == 'Plano não encontrado':
      print(f'Plano não encontrado: {desc}')

    return plano_encontrado

  def definir_dominio(self, desc) -> str:
    REGEX_DOMAIN = r"\b(?:[a-zA-Z0-9\-_@]+\.)+(?:xn--[a-zA-Z0-9]+|[a-zA-Z0-9]{2,}|[a-zA-Z0-9]{2}\.[a-zA-Z0-9]{2})\b"
    padraoDomain = re.compile(REGEX_DOMAIN)
    cliente = padraoDomain.search(desc)

    if cliente:
      cliente = cliente.group()

    elif self.ultimo_cliente_tratado in self.cliente_atual_baseado_na_coluna_cliente:
      cliente = self.ultimo_cliente_tratado

    elif self.rodada_inicial:
      cliente = self.cliente_atual_baseado_na_coluna_cliente
      self.rodada_inicial = False

    else:
      print(f'Cliente não encontrado.\nultimo tratado: {self.ultimo_cliente_tratado}\nobs: {desc}\ncliente: {cliente}\ncliente coluna: {self.cliente_atual_baseado_na_coluna_cliente}')  

    return cliente

  def define_clientes_omie(self):
    for ultimo_cliente, licencas, desc, situacao, dia in zip(self.coluna_cliente,
                                                        self.coluna_licencas,
                                                        self.coluna_desc,
                                                        self.coluna_situacao,
                                                        self.coluna_faturamento):
      if type(ultimo_cliente) == str:
        self.rodada_inicial = True
        self.cliente_atual_baseado_na_coluna_cliente = ultimo_cliente
        self.status_atual_baseado_na_coluna_status = situacao
        self.dia_atual_baseado_na_coluna_faturamento = dia

      dominio = self.definir_dominio(desc)

      if 'microsoft' in desc.lower():
        self.ultimo_cliente_tratado = None
        self.clientes_nao_divergentes.append({'dominio': dominio,
                                              'licencas omie ativa/arquivada': 'Cliente Microsoft',
                                              'licencas google ativa/arquivada': 'Cliente Microsoft',
                                              'produto': 'Cliente Microsoft',
                                              'status': 'Cliente Microsoft'})
        continue

      nao_mensais = 'não'
      desc: str

      for i in ['prop', 'migr', 'solici', 'pro rata']:
        if i in desc.lower():
          nao_mensais = 'sim'
          break

      anual = 'sim' if 'anual' in desc.lower() else 'não'
      situacao = 'Ativa' if self.status_atual_baseado_na_coluna_status == 'Ativo' else 'Suspenso'
      
      ativas = 0
      arquivadas = 0

      if ('arquivado' in desc.lower()) or ('arquivada' in desc.lower()): 
        arquivadas = licencas
      else: ativas = licencas

      existe = False

      for i in self.clientes_omie:
        if dominio in i['dominio']:

          if i['produto'] == 'não encontrado':
            i['produto'] = self.extrair_plano(desc)

          i['ativas'] = ativas if ativas != 0 else i['ativas']
          i['arquivadas'] = arquivadas if arquivadas != 0 else i['arquivadas']
          i['nao_mensais'] = nao_mensais if nao_mensais != 'não' else i['nao_mensais']
          i['anual'] = anual if anual != 'não' else i['anual']
          i['status'] = situacao

          existe = True
          break

      if not existe:
        produto = self.extrair_plano(desc)
        self.clientes_omie.append({
          'dominio': dominio,
          'produto': produto,
          'ativas': ativas,
          'arquivadas': arquivadas,
          'nao_mensais': nao_mensais,
          'anual': anual,
          'status': situacao,
          'dia_faturamento': self.dia_atual_baseado_na_coluna_faturamento
        })

      self.ultimo_cliente_tratado = dominio

  def define_clientes_painel(self):
    for cliente, licencas, produto, status, plano_pagamento in zip(
                                              self.coluna_cliente_tdn,
                                              self.coluna_licencas_tdn,
                                              self.coluna_sku_tdn,
                                              self.coluna_status,
                                              self.coluna_plano_pagamento_tdn
                                              ): 
      is_a_valid = False
      if 'Identity' in produto: continue

      for i in self.clientes_omie:
        if cliente == i['dominio']:
          is_a_valid = True
          break

      if not is_a_valid: continue

      anual = 'sim' if 'annual' in plano_pagamento.lower() else 'não'

      existe = False
      for i in self.clientes_painel:

        if i['dominio'] == cliente:

          if anual == 'sim':
            i['ativas'] = licencas
          else:
            i['ativas'] = licencas if 'Archived' not in produto else i['ativas']
            i['arquivadas'] = licencas if 'Archived' in produto else i['arquivadas']

          i['status'] = status
          i['produto'] = produto
          existe = True
          break

      if not existe:
        self.clientes_painel.append({
          'dominio': cliente,
          'ativas': licencas if 'Archived' not in produto else 0,
          'arquivadas': licencas if 'Archived' in produto else 0,
          'status': status,
          'produto': produto,
          'anual': anual
        })

  def compara_omie_e_painel(self):
    message = ""

    campos = ['ativas', 'arquivadas', 'status', 'anual']
    mensagens = ['licenças divergentes', 'licenças divergentes', 'status divergente', 'anual divergente']

    for painel in self.clientes_painel:
      for omie in self.clientes_omie:
        divergencia = False

        if painel['dominio'] == omie['dominio']:
          for campo, mensagem in zip(campos, mensagens):
            if painel[campo] != omie[campo]:
              message+= f"{mensagem} | "
              divergencia = True

          if  omie['produto'] not in painel['produto'] and painel['produto'] != '-':
            divergencia = True
            message+= f"Produto divergente | "

          if omie['nao_mensais'] == 'sim':
            divergencia = True
            message += f"Produto não mensal a ser removido | "

          if not divergencia and omie['dominio'] not in [i['dominio'] for i in self.clientes_nao_divergentes]:
            self.clientes_nao_divergentes.append({'dominio': omie['dominio'],
                                                  'licencas omie ativa/arquivada': '{}/{}'.format(omie['ativas'], omie['arquivadas']),
                                                  'licencas google ativa/arquivada': '{}/{}'.format(painel['ativas'], painel['arquivadas']),
                                                  'produto': painel['produto'],
                                                  'status': omie['status']})

        if divergencia:
          cliente_info = {
            'dominio': painel['dominio'],
            'licencas omie ativa/arquivada': '{}/{}'.format(omie['ativas'], omie['arquivadas']),
            'licencas google ativa/arquivada': '{}/{}'.format(painel['ativas'], painel['arquivadas']),
            'status omie/google':'{}/{}'.format(omie['status'], painel['status']),
            'message': message,
            'dia_faturamento': omie['dia_faturamento'],
          }

          message = ''
          self.clientes_divergentes.append(cliente_info)

    df_divergentes = pd.DataFrame(self.clientes_divergentes)
    df_divergentes.to_excel('clientes_divergentes.xlsx', index=False)
    df_nao_divergentes = pd.DataFrame(self.clientes_nao_divergentes)
    df_nao_divergentes.to_excel('clientes_nao_divergentes.xlsx', index=False)

  def main(self):
    self.define_clientes_omie()
    self.define_clientes_painel()
    self.compara_omie_e_painel()

classe = Service()
classe.main()
