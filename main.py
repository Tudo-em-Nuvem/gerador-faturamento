import pandas as pd

for i in range(10):
  try:
    dados_omie_excel = pd.read_excel('pivot.xlsx', header=i)
    coluna_cliente = dados_omie_excel['Cliente (Nome Fantasia)'].to_list()
    coluna_licencas = dados_omie_excel['Quantidade'].to_list()
    coluna_desc = dados_omie_excel['Descrição do Serviço (resumida)'].to_list()
    coluna_dia_faturamento = dados_omie_excel['Dia de Faturamento do Contrato'].to_list()
    break
  except:
    continue

dados_omie_excel = dados_omie_excel.drop(dados_omie_excel.index[-1])
cliente_atual = None
ultimo_divergente = False

lista_divergentes = []
clientes_omie = {}

for cliente, licencas, dia_faturamento, desc in zip(coluna_cliente, 
                                                    coluna_licencas, 
                                                    coluna_dia_faturamento, 
                                                    coluna_desc):
  cliente =  str(cliente)
  desc = str(desc)

  palavras_workspace = ['workspace', 'business', 'standard', 'starter', 'enterprise', 'plus']

  itIsWorkspace = False

  for palavra in palavras_workspace:
    if palavra in desc.lower() and 'microsoft' not in desc.lower():
      itIsWorkspace = True
      break

  if not itIsWorkspace: continue

  if any(char in str(cliente) for char in ['/', '|', '-']) and cliente != 'nan':
    lista_divergentes.append(cliente)
    ultimo_divergente = True
    continue

  if cliente == 'nan' and ultimo_divergente: continue

  else: ultimo_divergente = False

  if cliente_atual is None and cliente != 'nan':
    ultimo_divergente = False
    cliente_atual = cliente

  arquivado = False
  
  if ('arquivado' in desc.lower()) or ('arquivada' in desc.lower()): arquivado = True
  else: arquivado = False

  proporcional = False
  if 'prop' in desc.lower(): proporcional = True
  else: proporcional = False

  if cliente == 'nan' and cliente_atual:
    ultimo_divergente = False
    if proporcional:
      clientes_omie[cliente_atual]['proporcional'] = 'sim'
      continue
    elif arquivado:
      clientes_omie[cliente_atual]['arquivado'] = licencas 
      continue
    else:
      clientes_omie[cliente_atual]['ativo'] = licencas
      continue

  cliente_atual = cliente.lower()

  if proporcional:
    ultimo_divergente = False
    clientes_omie[cliente.lower()] = { 
                                      'ativo': 0, 'arquivado': 0, 
                                      'produto': desc, 'dia_faturamento': dia_faturamento,
                                      'proporcional': 'sim'
                                      }
    continue

  elif arquivado:
    ultimo_divergente = False
    clientes_omie[cliente.lower()] = { 
                                      'ativo': 0, 'arquivado': licencas, 
                                      'produto': desc, 'dia_faturamento': dia_faturamento,
                                      'proporcional': 'não'
                                      }
    continue

  ultimo_divergente = False
  clientes_omie[cliente.lower()] = {  
                                    'ativo': licencas, 'arquivado': 0, 
                                    'produto': desc, 'dia_faturamento': dia_faturamento,
                                    'proporcional': 'não'
                                    }

lista_sem_duplicatas = []
[lista_sem_duplicatas.append(item) for item in lista_divergentes if item not in lista_sem_duplicatas]

dados_tdn = pd.read_csv('tdn.csv')
coluna_cliente_tdn = dados_tdn['Cliente'].to_list()
coluna_licencas_tdn = dados_tdn['Licenças atribuídas'].to_list()
coluna_produto_tdn = dados_tdn['Produto'].to_list()
coluna_status = dados_tdn['Status da assinatura'].to_list()

clientes_tdn = {}

for cliente, licencas, produto, status in zip(
                                              coluna_cliente_tdn, 
                                              coluna_licencas_tdn, 
                                              coluna_produto_tdn, 
                                              coluna_status
                                              ):
  if cliente.lower() not in clientes_omie: continue
  if 'Google Workspace' not in produto: continue
  caso = 'arquivado' if 'Archived' in produto else 'ativo'
  ativos_e_arquivados = {
                        'ativo': licencas, 
                         'arquivado': 0, 
                         'produto': produto,
                         'status': status
                         } if caso == 'ativo' else {
                                                    'ativo': 0, 
                                                    'arquivado': licencas, 
                                                    'produto': produto,
                                                    'status': status
                                                    }

  if cliente in clientes_tdn:
    clientes_tdn[cliente][caso] = licencas
    continue

  else: clientes_tdn[cliente] = ativos_e_arquivados

clientes_divergentes = []

# Verificar divergências e adicionar informações relevantes à lista
for i in clientes_omie.keys():
    i = i.lower()
    try:
      if (clientes_omie[i]['arquivado'] != clientes_tdn[i]['arquivado'] or 
          clientes_omie[i]['ativo'] != clientes_tdn[i]['ativo']):
          cliente_info = {
              'Cliente': i,
              'Omie': f'Ativo: {clientes_omie[i]["ativo"]} | Arquivado: {clientes_omie[i]["arquivado"]}',
              'Painel': f'Ativo: {clientes_tdn[i]["ativo"]} | Arquivado: {clientes_tdn[i]["arquivado"]}',
              'Dia Faturamento': clientes_omie[i]['dia_faturamento'],
              'Proporiocnal': clientes_omie[i]['proporcional'],
              'Status': 'Licenças divergentes',
              'Status da assinatura': clientes_tdn[i]['status']
          }

          clientes_divergentes.append(cliente_info)

      elif clientes_omie[i]['proporcional'] == 'sim':
        cliente_info = {
            'Cliente': i,
            'Omie': f'Ativo: {clientes_omie[i]["ativo"]} | Arquivado: {clientes_omie[i]["arquivado"]}',
            'Painel': f'Ativo: {clientes_tdn[i]["ativo"]} | Arquivado: {clientes_tdn[i]["arquivado"]}',
            'Dia Faturamento': clientes_omie[i]['dia_faturamento'],
            'Proporiocnal': clientes_omie[i]['proporcional'],
            'Status': 'Proporcional divergente',
            'Status da assinatura': clientes_tdn[i]['status']
        }

        clientes_divergentes.append(cliente_info)

    except:
      cliente_info = {
          'Cliente': i,
          'Omie': f'Ativo: {clientes_omie[i]["ativo"]} | Arquivado: {clientes_omie[i]["arquivado"]}',
          'Painel': 'Não encontrado',
          'Dia Faturamento': clientes_omie[i]["dia_faturamento"],
          'Proporiocnal': clientes_omie[i]['proporcional'],
          'Status': 'Domínio divergente entre Omie e Painel',
          'Status da assinatura': 'Não encontrado'
      }

      clientes_divergentes.append(cliente_info)

for i in lista_divergentes:
  if i not in clientes_omie:
    cliente_info = {
        'Cliente': i,
        'Omie': 'erro',
        'Painel': 'erro',
        'Dia Faturamento': 'erro',
        'Proporiocnal': 'erro',
        'Status da assinatura': 'erro',
        'Status': 'Contrato com mais de um domínio, checar manualmente'
    }

    clientes_divergentes.append(cliente_info)
# Criar um DataFrame com as informações dos clientes divergentes
df_clientes_divergentes = pd.DataFrame(clientes_divergentes)

# Salvar o DataFrame em um arquivo Excel
df_clientes_divergentes.to_excel('clientes_divergentes.xlsx', index=False)

# Exibir os dados salvos
print("Arquivo 'clientes_divergentes.xlsx' criado com sucesso!")

def extrairProduto(produto):
  produtos = ['starter', 'standard', 'plus', 'enterprise', 'enterprise standard', 'enterprise plus']
  for item in produtos:
    if item in produto.lower():
  
      if item == 'enterprise':
        if 'standard' in produto.lower():
          return 'enterprise standard'
        elif 'plus' in produto.lower():
          return 'enterprise plus'

      return item
