import pandas as pd

dados_omie_excel = pd.read_excel('pivot.xlsx', header=8)
dados_omie_excel = dados_omie_excel.drop(columns='Situação')
dados_omie_excel = dados_omie_excel.drop(dados_omie_excel.index[-1])

coluna_cliente = dados_omie_excel['Cliente (Nome Fantasia)'].to_list()
coluna_licencas = dados_omie_excel['Quantidade'].to_list()
coluna_desc = dados_omie_excel['Descrição do Serviço (resumida)'].to_list()

cliente_atual = None
lista_divergentes = []
clientes_omie = {}
ultimo_divergente = False

for cliente, licencas, desc in zip(coluna_cliente, coluna_licencas, coluna_desc):
  cliente =  str(cliente)
  desc = str(desc)

  palavras_workspace = ['workspace', 'business', 'standard', 'starter', 'enterprise', 'plus']
  itIsWorkspace = False
  for palavra in palavras_workspace:
    if palavra in desc.lower() and 'microsoft' not in desc.lower():
      itIsWorkspace = True
      break

  if not itIsWorkspace:
    continue

  if any(char in str(cliente) for char in ['/', '|', '-']) and cliente != 'nan':
    print('DIVERGENTEEEEEEEEEEEEE')
    lista_divergentes.append(cliente)
    ultimo_divergente = True
    continue

  if cliente == 'nan' and ultimo_divergente:
    print('ignorando')
    continue
  else:
    ultimo_divergente = False

  if cliente_atual is None and cliente != 'nan':
    ultimo_divergente = False
    cliente_atual = cliente

  arquivado = False
  
  if ('arquivado' in desc.lower()) or ('arquivada' in desc.lower()):
    arquivado = True
  else:
    arquivado = False

  if cliente == 'nan' and cliente_atual:
    ultimo_divergente = False
    if arquivado:
      clientes_omie[cliente_atual]['arquivado'] = licencas 
      continue
    else:
      clientes_omie[cliente_atual]['ativo'] = licencas
      continue

  cliente_atual = cliente.lower()

  if arquivado:
    ultimo_divergente = False
    clientes_omie[cliente.lower()] = { 'ativo': 0, 'arquivado': licencas, 'produto': desc}
    continue
  ultimo_divergente = False
  clientes_omie[cliente.lower()] = { 'ativo': licencas, 'arquivado': 0, 'produto': desc }

print(clientes_omie)
lista_sem_duplicatas = []
[lista_sem_duplicatas.append(item) for item in lista_divergentes if item not in lista_sem_duplicatas]

dados_tdn = pd.read_csv('tdn.csv')
coluna_cliente_tdn = dados_tdn['Cliente'].to_list()
coluna_licencas_tdn = dados_tdn['Licenças atribuídas'].to_list()
coluna_produto_tdn = dados_tdn['Produto'].to_list()

clientes_tdn = {}

for cliente, licencas, produto in zip(coluna_cliente_tdn, coluna_licencas_tdn, coluna_produto_tdn):
  if 'Google Workspace' not in produto:
    continue  

  caso = 'arquivado' if 'Archived' in produto else 'ativo'
  ativos_e_arquivados = {'ativo': licencas, 
                         'arquivado': 0, 
                         'produto': produto} if caso == 'ativo' else {'ativo': 0, 
                                                                      'arquivado': licencas, 
                                                                      'produto': produto}

  if cliente in clientes_tdn:
    clientes_tdn[cliente][caso] = licencas
    continue

  else:
    clientes_tdn[cliente] = ativos_e_arquivados

clientes_divergentes = []

# Verificar divergências e adicionar informações relevantes à lista
for i in clientes_omie.keys():
    print(i)
    try:
      if (clientes_omie[i]['arquivado'] != clientes_tdn[i]['arquivado'] or 
          clientes_omie[i]['ativo'] != clientes_tdn[i]['ativo']):

          cliente_info = {
              'Cliente': i,
              'Omie': f'Ativo: {clientes_omie[i]["ativo"]} | Arquivado: {clientes_omie[i]["arquivado"]}',
              'Painel': f'Ativo: {clientes_tdn[i]["ativo"]} | Arquivado: {clientes_tdn[i]["arquivado"]}',
              'Status': 'Licenças divergentes'
          }

          clientes_divergentes.append(cliente_info)
    except:
      cliente_info = {
          'Cliente': i,
          'Omie': f'Ativo: {clientes_omie[i]["ativo"]} | Arquivado: {clientes_omie[i]["arquivado"]}',
          'Painel': 'Não encontrado',
          'Status': 'Domínio divergente entre Omie e Painel'
      }

      clientes_divergentes.append(cliente_info)
# Criar um DataFrame com as informações dos clientes divergentes
df_clientes_divergentes = pd.DataFrame(clientes_divergentes)

# Salvar o DataFrame em um arquivo Excel
df_clientes_divergentes.to_excel('clientes_divergentes.xlsx', index=False)

# Exibir os dados salvos
print("Arquivo 'clientes_divergentes.xlsx' criado com sucesso!")

def extrairProduto(produto) -> str:
  produtos = ['starter', 'standard', 'plus', 'enterprise', 'enterprise standard', 'enterprise plus']
  for item in produtos:
    if item in produto.lower():
  
      if item == 'enterprise':
        if 'standard' in produto.lower():
          return 'enterprise standard'
        elif 'plus' in produto.lower():
          return 'enterprise plus'

      return item
