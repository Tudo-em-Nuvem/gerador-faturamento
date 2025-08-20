import os
import pandas as pd
from uuid import uuid4
import re
import requests
import dotenv
from time import sleep
from config import FOLDER_OPORTUNITY_DIR
dotenv.load_dotenv()

def create_opportunities(file_name):
  """
  Função para criar oportunidades de vendas a partir de um arquivo Excel.
  O arquivo deve conter colunas com os seguintes headers:
  """
  import logging
  logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

  def get_oportunidades():
    # Recebe oportunidades da API
    logging.info("Buscando oportunidades da API...")
    oportunidades = []
    page = 1

    while True:
      response = requests.get(
        'https://apitdnomieasaas.squareweb.app/omie/listar_oportunidades',
        json = {
          "pagina": page,
          "registros_por_pagina": 500,
          "status": "A",
          "fase": 1889067044
        }, headers = {
            'Content-Type': 'application/json',
            'x-api-key': os.getenv('ACCESS_TOKEN')
          }
      )

      if response.status_code != 200:
        logging.error(f"Erro ao buscar oportunidades: {response.text}")
        return

      data = response.json()
      if not data:
        logging.info("Nenhuma oportunidade encontrada.")
        return

      oportunidades.extend(data.get('cadastros', []))
      if page == data.get('total_de_paginas', 1):
        break
      
      page += 1
      sleep(1)  # Evita sobrecarga na API

    return oportunidades

  def get_contas():
    # Recebe contas da API
    logging.info("Buscando contas da API...")
    contas = []
    page = 1
    
    while True:
      response = requests.get(
        'https://apitdnomieasaas.squareweb.app/omie/listar_contas_oportunidade',
        json = {
          "pagina": page,
          "registros_por_pagina": 500
        }, headers = {
            'Content-Type': 'application/json',
            'x-api-key': os.getenv('ACCESS_TOKEN')
          }
      )

      if response.status_code != 200:
        logging.error(f"Erro ao buscar contas: {response.text}")
        return

      data = response.json()
      if not data:
        logging.info("Nenhuma oportunidade encontrada.")
        return
      
      contas.extend(data.get('cadastros', []))
      if page == data.get('total_de_paginas', 1):
        break
      page += 1

      sleep(1) # Evita sobrecarga na API

    return contas

  def get_contatos():
    # Recebe contatos da API
    logging.info("Buscando contatos da API...")
    contatos = []
    page = 1
    
    while True:
      response = requests.get(
        'https://apitdnomieasaas.squareweb.app/omie/listar_contatos_oportunidade',
        json = {
          "pagina": page,
          "registros_por_pagina": 500
        }, headers = {
            'Content-Type': 'application/json',
            'x-api-key': os.getenv('ACCESS_TOKEN')
          }
      )

      if response.status_code != 200:
        logging.error(f"Erro ao buscar contatos: {response.text}")
        return

      try:
        data = response.json()

      except Exception as e:
        logging.error(f"Erro ao decodificar JSON: {e} | Resposta: {response.text}")
        return
      
      if not data:
        logging.info("Nenhum contato encontrado.")
        return
      
      contatos.extend(data.get('cadastros', []))
      if page == data.get('total_de_paginas', 1):
        break
      page += 1

      sleep(1)

    return contatos

  logging.info(f"Iniciando processamento do arquivo: {file_name}")
  df = pd.read_excel(f'{FOLDER_OPORTUNITY_DIR}/{file_name}', header=None)
  df = df.dropna(how='all')

  if df.empty:
    logging.warning("O arquivo está vazio. Nenhuma oportunidade criada.")
    return

  df.columns = ['nome', 'telefone', 'email', 'cnpj/nome_empresa', 'vendedor']

  vendedores = {
    "denis": 1889066818,
    "nicolas": 5407562199,
    "guilherme": 5389292040,
    "jhonata": 5131055985,
  }

  erros = []

  # Busca todas as contas, contatos e oportunidades uma vez
  contas = get_contas() or []
  print(len(contas))
  print(contas[0])
  contatos = get_contatos() or []
  oportunidades = get_oportunidades() or []

  for idx, i in df.iterrows():
    line = idx+1
    name = i["nome"]
    
    if type(name) is not str:
      logging.warning(f"Linha {line}: Nome inválido: {name}. Oportunidade não criada.")
      continue

    phone: str = str(i["telefone"])
    if phone.startswith('55'): phone = phone[2:]
    phone_ddd = phone[:2]
    phone_number = phone[2:]

    email = i["email"]
    cnpj_or_company_name = i["cnpj/nome_empresa"]

    cnpj_pattern = r'^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$'
    cnpj = None
    business_name = None
    
    if re.match(cnpj_pattern, cnpj_or_company_name):
      cnpj = cnpj_or_company_name
    else:
      business_name = cnpj_or_company_name

    vendedor = i["vendedor"]
    id_vendedor = vendedores.get(vendedor.lower(), None)
    
    if not id_vendedor:
      logging.warning(f"Linha {line}: Vendedor '{vendedor}' não encontrado. Oportunidade não criada.")
      continue

    account_name = name if not business_name else business_name

    # 1. Verifica se a conta existe
    existing_account = next((c for c in contas if 'identificacao' in c and c['identificacao']['cNome'] == account_name), None)
    
    if existing_account:
      uuid = existing_account["identificacao"]['cCodInt']
      nCodConta = existing_account["identificacao"]['nCod']
    
    else:
      if existing_account:
        uuid = existing_account["identificacao"]['cCodInt']
        nCodConta = existing_account["identificacao"]['nCod']
      
      else:
        # Cria conta
        uuid = uuid4().hex
        account_data = {
          "identificacao": {"cNome": account_name, "cCodInt": uuid, "nCodVend": id_vendedor},
          "telefone_email": {"cDDDTel": phone_ddd, "cNumTel": phone_number, "cEmail": email},
          "endereco": {"cEndereco": "A ver"}
        }

        if cnpj:
          account_data["identificacao"]["cDoc"] = cnpj
       
        logging.info(f"Linha {line}: Criando conta para {account_name}...")
        
        try:
          response = requests.post(
            'https://apitdnomieasaas.squareweb.app/omie/conta_oportunidade',
            json=account_data,
            headers={
              'Content-Type': 'application/json',
              'x-api-key': os.getenv('ACCESS_TOKEN')
            }
          )

          status_code = response.status_code
          
          if status_code != 200:
            msg = f"[Conta] Linha {line} - Nome: {name} | Erro: {response.text}"
            logging.error(msg)
            erros.append(msg)
            continue
          
          sleep(3)
          
          nCodConta = response.json().get('nCod', None)
          
          if not nCodConta:
            msg = f"[Conta] Linha {line} - Nome: {name} | Erro: nCodConta não retornado. Pulando para próxima linha."
            logging.error(msg)
            erros.append(msg)
            continue

          # Atualiza lista de contas para próximos usos
          contas.append({"identificacao": {"cNome": account_name, "cCodInt": uuid, "nCod": nCodConta}})
        
        except Exception as e:
          msg = f"[Conta] Linha {line} - Nome: {name} | Exceção: {e}"
          logging.exception(msg)
          erros.append(msg)
          continue

    # 2. Verifica se o contato existe para esse uuid e nCodConta
    existing_contact = next((c for c in contatos if "identificacao" in c and c["identificacao"]['cCodInt'] == uuid and c["identificacao"]['nCodConta'] == nCodConta), None)
    
    if existing_contact:
      nCodContato = existing_contact["identificacao"]['nCod']
    
    else:
      # Cria contato
      contact_data = {
        "identificacao": {"cNome": name, "cCodInt": uuid, "nCodConta": nCodConta, "nCodVend": id_vendedor},
        "telefone_email": {"cDDDCel1": phone_ddd, "cNumCel1": phone_number, "cEmail": email},
        "endereco": {"cEndereco": "A ver"}
      }

      logging.info(f"Linha {line}: Criando contato...")
      
      try:
        response = requests.post(
          'https://apitdnomieasaas.squareweb.app/omie/contato_oportunidade',
          json=contact_data,
          headers={
            'Content-Type': 'application/json',
            'x-api-key': os.getenv('ACCESS_TOKEN')
          }
        )
        
        status_code = response.status_code
        
        if status_code != 200:
          msg = f"[Contato] Linha {line} - Nome: {name} | Conta: {account_name} | Erro: {response.text}"
          logging.error(msg)
          erros.append(msg)
          continue
        
        sleep(3)
        nCodContato = response.json().get('nCod', None)
        
        if not nCodContato:
          msg = f"[Contato] Linha {line} - Nome: {name} | Conta: {account_name} | Erro: nCodContato não retornado. Pulando para próxima linha."
          logging.error(msg)
          erros.append(msg)
          continue
        
        # Atualiza lista de contatos para próximos usos
        contatos.append({"identificacao": {"cCodInt": uuid, "nCodConta": nCodConta, "nCod": nCodContato}})
      
      except Exception as e:
        msg = f"[Contato] Linha {line} - Nome: {name} | Conta: {account_name} | Exceção: {e}"
        logging.exception(msg)
        erros.append(msg)
        continue

    # 3. Verifica se a oportunidade existe para esse nCodConta e nCodContato
    existing_opportunity = next((o for o in oportunidades if "identificacao" in o and o['identificacao']['nCodConta'] == nCodConta and o['identificacao']['nCodContato'] == nCodContato), None)
    
    if existing_opportunity:
      msg = f"[Oportunidade] Linha {line} - Nome: {name} | Conta: {account_name} | Contato: {nCodContato} | Já existe. Pulando."
      logging.info(msg)
      erros.append(msg)
      continue

    # Cria oportunidade
    opportunity_data = {
      "identificacao": {
        "cCodIntOp": uuid,
        "cDesOp": f"{name} - Serviço",
        "nCodContato": nCodContato,
        "nCodConta": nCodConta,
        "nCodVendedor": id_vendedor,
        "nCodSolucao": 5367777608,
        "nCodOrigem": 1889067064
      }
    }

    logging.info(f"Linha {line}: Criando oportunidade...")

    try:
      response = requests.post(
        'https://apitdnomieasaas.squareweb.app/omie/oportunidade',
        json=opportunity_data,
        headers={
          'Content-Type': 'application/json',
          'x-api-key': os.getenv('ACCESS_TOKEN')
        }
      )
      status_code = response.status_code

      if status_code != 200:
        msg = f"[Oportunidade] Linha {line} - Nome: {name} | Conta: {account_name} | Contato: {nCodContato} | Erro: {response.text}"
        logging.error(msg)
        erros.append(msg)
        continue

      sleep(3)
      msg = f"[Oportunidade] Linha {line} - Nome: {name} | Conta: {account_name} | Contato: {nCodContato} | Criada com sucesso."
      logging.info(msg)

      # Atualiza lista de oportunidades para próximos usos
      oportunidades.append({"identificacao": {"nCodConta": nCodConta, "nCodContato": nCodContato}})

    except Exception as e:
      msg = f"[Oportunidade] Linha {line} - Nome: {name} | Conta: {account_name} | Contato: {nCodContato} | Exceção: {e}"
      logging.exception(msg)
      erros.append(msg)
      continue

  return erros if erros else "Todas as oportunidades foram criadas com sucesso!"
