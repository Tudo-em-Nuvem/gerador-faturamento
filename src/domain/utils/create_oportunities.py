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

    logging.info(f"Iniciando processamento do arquivo: {file_name}")
    df = pd.read_excel(f'{FOLDER_OPORTUNITY_DIR}/{file_name}', header=None)

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

    for idx, i in df.iterrows():
      ja_existe = False
      name = i["nome"]
      if type(name) is not str:
        logging.warning(f"Linha {idx}: Nome inválido: {name}. Oportunidade não criada.")
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
        logging.warning(f"Linha {idx}: Vendedor '{vendedor}' não encontrado. Oportunidade não criada.")
        continue

      # Cria a conta
      status_code = None
      tentativas_conta = 0
      while status_code != 200:
        uuid = uuid4().hex
        account_data = {
          "identificacao": {"cNome": name if not business_name else business_name, "cCodInt": uuid, "nCodVend": id_vendedor},
          "telefone_email": {"cDDDTel": phone_ddd, "cNumTel": phone_number, "cEmail": email},
          "endereco": {"cEndereco": "A ver"}
        }

        if cnpj:
          account_data["identificacao"]["cDoc"] = cnpj

        logging.info(f"Linha {idx}: Criando conta para {name} (tentativa {tentativas_conta+1})...")
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
            logging.error(f"Linha {idx}: Falha ao criar conta (status {status_code}): {response.text}")
            if "já existe" in response.text: 
              ja_existe = True
              erros.append(f"Linha {idx}: Conta já existe para {name}.")
              break

          sleep(3)
          tentativas_conta += 1
          
        except Exception as e:
          logging.exception(f"Linha {idx}: Erro ao criar conta: {e}")
          break
      
      if ja_existe: continue
      nCodConta = response.json().get('nCod', None)
      if not nCodConta:
        logging.error(f"Linha {idx}: nCodConta não retornado. Pulando para próxima linha.")
        continue

      # Cria contato
      status_code = None
      tentativas_contato = 0
      while status_code != 200:
        contact_data = {
          "identificacao": {"cNome": name, "cCodInt": uuid, "nCodConta": nCodConta, "nCodVend": id_vendedor},
          "telefone_email": {"cDDDCel1": phone_ddd, "cNumCel1": phone_number, "cEmail": email},
          "endereco": {"cEndereco": "A ver"}
        }
        logging.info(f"Linha {idx}: Criando contato (tentativa {tentativas_contato+1})...")
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
            logging.error(f"Linha {idx}: Falha ao criar contato (status {status_code}): {response.text}")
            if "já existe" in response.text:
              ja_existe = True
              break

          sleep(3)
          tentativas_contato += 1
        except Exception as e:
          logging.exception(f"Linha {idx}: Erro ao criar contato: {e}")
          break

      if ja_existe: continue
      nCodContato = response.json().get('nCod', None)
      if not nCodContato:
        logging.error(f"Linha {idx}: nCodContato não retornado. Pulando para próxima linha.")
        continue

      # Cria oportunidade
      status_code = None
      tentativas_op = 0
      while status_code != 200:
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

        logging.info(f"Linha {idx}: Criando oportunidade (tentativa {tentativas_op+1})...")
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
            logging.error(f"Linha {idx}: Falha ao criar oportunidade (status {status_code}): {response.text}")
            if "já existe" in response.text:
              ja_existe = True
              break

          sleep(3)
          tentativas_op += 1
        except Exception as e:
          logging.exception(f"Linha {idx}: Erro ao criar oportunidade: {e}")
          break

      if status_code == 200:
        logging.info(f"Linha {idx}: Oportunidade criada com sucesso!")
      else:
        logging.error(f"Linha {idx}: Não foi possível criar a oportunidade após {tentativas_op} tentativas.")

    return erros if erros else "Todas as oportunidades foram criadas com sucesso!"