import requests
import dotenv
import os
from datetime import date, timedelta
import pandas as pd
from config import OFX_DIR

dotenv.load_dotenv()

class OfxGenerator:
  def __init__(self):
    self.date = self.get_date() # ('2025-04-19', '2025-04-21') #
    self.date0_br = self.date[0].split('-')[2] + '/' + self.date[0].split('-')[1] + '/' + self.date[0].split('-')[0]

  def get_date(self) -> tuple[str, str]:
      hoje = date.today()

      if hoje.weekday() == 0:  # Se for segunda-feira
          data_inicial = hoje - timedelta(days=3)  # Sexta
          data_final = hoje - timedelta(days=1)  # Domingo
      else:
          data_inicial = hoje - timedelta(days=1)  # Ontem
          data_final = hoje - timedelta(days=1)  # Ontem

      return data_inicial.strftime('%Y-%m-%d'), data_final.strftime('%Y-%m-%d')

  def get_financial_transactions(self):
    url = f'https://apitdnomieasaas.squareweb.app/asaas/extract'

    header = { 'x-api-key': os.getenv('ACCESS_TOKEN') }

    data_inicial = self.date[0]
    data_final   = self.date[1]
    params = {
      'startDate': data_inicial, 'endDate': data_final,
      'offSet': 0, 'limit': 100
    }

    transactions = []
    offset = 0

    while True:
      res = requests.get(url=url, headers=header, params=params)
      transactions += res.json()['data']
      hasMore = res.json()['hasMore']

      print(hasMore)
      if not hasMore:
        break
 
      offset += 100
      params['offSet'] = offset

    return transactions

  def gen_model(self, date, desc, doc, value, dc):
    return { 'Data de Movimento': date, 'Descrição': desc, 'Documento': doc, 'Valor': value, 'd/c': dc }

  def some_transactions(self, res):
    transactions = [
      self.gen_model(self.date0_br, 'Cobrança recebida', self.date[0].replace('-', ''), 0, 'C'),
      self.gen_model(self.date0_br, 'Taxa de boleto, cartão ou Pix', self.date[0].replace('-', ''), 0, 'D')
    ]

    for i in res:
      if i['type'] in ['PAYMENT_RECEIVED', 'RECEIVABLE_ANTICIPATION_GROSS_CREDIT']:
        transactions[0]['Valor'] += float(i['value'])

      elif i['type'] in ['PAYMENT_FEE', 'RECEIVABLE_ANTICIPATION_FEE']:
        transactions[1]['Valor'] += float(i['value'])

      elif i['type'] in ['TRANSFER', 'TRANSFER_FEE', 'REVERSAL']:
        transactions.append(self.gen_model(self.date0_br, i['description'], self.date[0].replace('-', ''), i['value'], 'C' if float(i['value']) > 0 else 'D'))

      else:
        transactions.append(self.gen_model(self.date0_br, i['description'], self.date[0].replace('-', ''), i['value'], 'C' if float(i['value']) > 0 else 'D'))
       
    return transactions

  def extract_name_from_dates(self) -> str:
    str_dates = self.date[0].split('-')[2] + ' ' + self.date[1].split('-')[2] 
    list_dates = str_dates.split(' ')
    if list_dates[0] == list_dates[1]:
      return list_dates[0]

    return list_dates[0] + ' a ' + list_dates[1]

  def main(self):
    res          = self.get_financial_transactions()
    transactions = self.some_transactions(res)

    types_data = list(set([response['type'] for response in res]))
    for i in types_data:
      if i not in ['RECEIVABLE_ANTICIPATION_FEE', 'PAYMENT_RECEIVED', 'RECEIVABLE_ANTICIPATION_GROSS_CREDIT', 'PAYMENT_FEE', 'TRANSFER', 'TRANSFER_FEE']:
        print(f"\033[93mATENÇÃO, TIPO NÃO ENCONTRADO NA LISTA. POR FAVOR, AJUSTE\n{i}\033[0m")

    for i in transactions:
      i['Valor'] = round(i['Valor'], 2)
      i['Valor'] = str(i['Valor']).replace('.', ',')

    df_transactions = pd.DataFrame(transactions)
    df_transactions.to_html(f'{OFX_DIR}/{self.extract_name_from_dates()}.html')

if __name__ == "__main__":
  service = OfxGenerator()
  service.main()
