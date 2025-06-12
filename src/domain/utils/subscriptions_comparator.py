import pandas as pd

from config import SUBSCRIPTIONS_DIR
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def subscriptions_comparator(file_name1, file_name2):
  file1 = pd.read_excel(f"{SUBSCRIPTIONS_DIR}/{file_name1}", header=2)

  if "Cliente (Nome Fantasia)" in file1.columns.values.tolist():
    omie = file1
    asaas = pd.read_excel(f"{SUBSCRIPTIONS_DIR}/{file_name2}", header=0)
  else:
    asaas = pd.read_excel(f"{SUBSCRIPTIONS_DIR}/{file_name1}", header=0)
    omie = pd.read_excel(f"{SUBSCRIPTIONS_DIR}/{file_name2}", header=2)

  asaas_df = {'contrato': [], 'valor': []}
  for domain, valor in zip(asaas['Nome'], asaas['Valor']):
    asaas_df['contrato'].append(domain.split(',')[0])
    asaas_df['valor'].append(valor)

  asaas_df = pd.DataFrame(asaas_df)
  asaas_df.count()

  omie_df = {'contrato': [], 'valor': []}
  for contrato, valor in zip(omie['Nº do Contrato de Venda'], omie['Valor da Conta']):
    omie_df['contrato'].append(contrato)
    omie_df['valor'].append(valor)

  omie_df = pd.DataFrame(omie_df)

  valores_diferentes = {'contrato': [], 'valor_asaas': [], 'valor_omie': []}

  for contrato_omie in omie_df['contrato']:
    for contrato_asaas in asaas_df['contrato']:
      if contrato_omie == contrato_asaas:
        valor_omie = omie_df[omie_df['contrato'] == contrato_omie]['valor'].values[0]
        valor_asaas = asaas_df[asaas_df['contrato'] == contrato_asaas]['valor'].values[0]

        if valor_omie != valor_asaas:
          valores_diferentes['contrato'].append(contrato_omie)
          valores_diferentes['valor_asaas'].append(valor_asaas)
          valores_diferentes['valor_omie'].append(valor_omie)

  valores_diferentes_df = pd.DataFrame(valores_diferentes)
  
  valores_diferentes_df = valores_diferentes_df.drop_duplicates(subset=['contrato'])
  valores_diferentes_df.to_excel(f'{SUBSCRIPTIONS_DIR}/valores_diferentes.xlsx', index=False)
