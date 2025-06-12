import pandas as pd

from config import ASAAS_OMIE_CHECKER_DIR

def asaas_omie_checker(file_name1, file_name2):
  file1 = pd.read_excel(f"{ASAAS_OMIE_CHECKER_DIR}/{file_name1}", header=2)

  if "Nº do Contrato de Venda" in file1.columns.values.tolist():
    omie = file1
    asaas = pd.read_excel(f"{ASAAS_OMIE_CHECKER_DIR}/{file_name2}", header=0)
  else:
    asaas = pd.read_excel(f"{ASAAS_OMIE_CHECKER_DIR}/{file_name1}", header=0)
    omie = pd.read_excel(f"{ASAAS_OMIE_CHECKER_DIR}/{file_name2}", header=2)

  asaas['contrato'] = asaas['Nome'].str.split(',').str[0]

  asaas_not_in_omie = asaas[~asaas['contrato'].isin(omie['Nº do Contrato de Venda'])]
  asaas_not_in_omie.to_excel(f'{ASAAS_OMIE_CHECKER_DIR}/asaas_que_nao_estao_na_omie.xlsx', index=False)
