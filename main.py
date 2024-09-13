import pandas as pd
import re

class Service:
  def __init__(self):
    self.cliente_atual_baseado_na_coluna_cliente = None
    self.status_atual_baseado_na_coluna_status = None
    self.ultimo_cliente_tratado = ''
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
    REGEX_DOMAIN = r"\b(?:[a-zA-Z0-9][a-zA-Z0-9\-_@]*\.)+(?:xn--[a-zA-Z0-9]+|[a-zA-Z0-9]{2,}|[a-zA-Z0-9]{2}\.[a-zA-Z0-9]{2})\b"
    padraoDomain = re.compile(REGEX_DOMAIN)
    resultados = padraoDomain.findall(desc)

    if len(resultados) > 1:
      cliente = resultados[0]
      if self.eh_float(cliente):
        cliente = resultados[1]
  
    elif len(resultados) == 1:
      cliente = resultados[0]

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
        self.ultimo_cliente_tratado = dominio
        self.clientes_nao_divergentes.append({'dominio': dominio,
                                              'licencas omie ativa/arquivada': 'Cliente Microsoft',
                                              'licencas google ativa/arquivada': 'Cliente Microsoft',
                                              'produto': 'Cliente Microsoft',
                                              'status': 'Cliente Microsoft'})
        continue

      microsoft = False
      for i in self.clientes_nao_divergentes:
        if dominio in i['dominio']:
          if i['status'] == 'Cliente Microsoft':
            microsoft = True
      if microsoft: continue

      nao_mensais = 'não'
      desc: str

      for i in ['proporc', 'migraç', 'solicitação', 'pro rata']:
        if i in desc.lower():
          nao_mensais = 'sim'
          break

      if 'support' in desc.lower():
        nao_mensais = 'sim'

      situacao = 'Ativa' if self.status_atual_baseado_na_coluna_status == 'Ativo' else 'Suspenso'

      ativas = 0
      arquivadas = 0

      if ('arquivado' in desc.lower()) or ('arquivada' in desc.lower()): 
        arquivadas = licencas
      elif 'supor' in desc.lower():
        pass
      else: ativas = licencas

      existe = False

      for i in self.clientes_omie:
        if dominio.lower() == i['dominio'].lower():

          if i['produto'] == 'não encontrado':
            i['produto'] = self.extrair_plano(desc)

          i['ativas'] = ativas if ativas != 0 and self.extrair_plano(desc) != 'não encontrado' else i['ativas']
          i['arquivadas'] = arquivadas if arquivadas != 0 else i['arquivadas']
          i['nao_mensais'] = nao_mensais if nao_mensais != 'não' else i['nao_mensais']
          i['status'] = situacao
          existe = True
          break

      if not existe:
        produto = self.extrair_plano(desc)

        item = {
          'dominio': dominio.lower(),
          'produto': produto,
          'ativas': ativas,
          'arquivadas': arquivadas,
          'nao_mensais': nao_mensais,
          'status': situacao,
          'dia_faturamento': self.dia_atual_baseado_na_coluna_faturamento
        }

        self.clientes_omie.append(item)

      self.ultimo_cliente_tratado = dominio

  def define_clientes_painel(self):
    for cliente,                 licencas,                 produto,             status,             plano_pagamento in zip(
        self.coluna_cliente_tdn, self.coluna_licencas_tdn, self.coluna_sku_tdn, self.coluna_status, self.coluna_plano_pagamento_tdn
                                              ): 
      is_a_valid = False

      if 'Identity' in produto: continue
      if 'AppSheet' in produto: continue

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
          'produto': produto
        })

  def compara_omie_e_painel(self):
    dias_faturamento = []
    message = ""

    campos =    ['ativas',               'arquivadas',           'status']
    mensagens = ['licenças divergentes', 'licenças divergentes', 'status divergente']

    for painel in self.clientes_painel:

      for omie in self.clientes_omie:

        divergencia = False
        dias_faturamento.append(int(omie['dia_faturamento'])) if omie['dia_faturamento'] not in dias_faturamento else None

        if painel['dominio'] == omie['dominio']:
          for campo, mensagem in zip(campos, mensagens):
            if painel[campo] != omie[campo]:
              message+= f"{mensagem} | "
              divergencia = True

          if  omie['produto'] not in painel['produto'] and painel['produto'] != '-':
            divergencia = True
            message += f"Produto divergente | "

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
          if len([cliente for cliente in self.clientes_nao_divergentes if cliente['dominio'] == painel['dominio']]) > 0:
            self.clientes_nao_divergentes = [cliente for cliente in self.clientes_nao_divergentes if cliente['dominio'] != painel['dominio']]

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

    clientes_que_nao_estao_no_painel = [i['dominio'].lower() for i in self.clientes_omie if i['dominio'].lower() not in [j['dominio'].lower() for j in self.clientes_painel]]

    for i in clientes_que_nao_estao_no_painel:
      self.clientes_divergentes.append({'dominio': i,
                                        'licencas omie ativa/arquivada': 'n/a',
                                        'licencas google ativa/arquivada': 'n/a',
                                        'status omie/google': 'n/a',
                                        'message': 'Cliente não encontrado no painel',
                                        'dia_faturamento': 'n/a'
                                        })

    df_divergentes = pd.DataFrame(self.clientes_divergentes)
    df_nao_divergentes = pd.DataFrame(self.clientes_nao_divergentes)

    name_arquivo = ''
    for day in sorted(dias_faturamento):
      name_arquivo += f'{day} '

    with pd.ExcelWriter(f'{name_arquivo.strip()}.xlsx') as writer:
      df_divergentes.to_excel(writer, sheet_name='Divergentes', index=False)
      df_nao_divergentes.to_excel(writer, sheet_name='Não Divergentes', index=False)

  def eh_float(self, valor: str):
    """Verifica se uma string pode ser convertida em um float.

    Args:
      valor: A string a ser verificada.

    Returns:
      True se a string representar um float, False caso contrário.
    """

    try:
      float(valor)
      return True
    except ValueError:
      return False
  
  def main(self):
    self.define_clientes_omie()
    self.define_clientes_painel()
    self.compara_omie_e_painel() 

classe = Service()
classe.main()
