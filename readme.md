# Gerador de Faturamento Automático

## Descrição

Este projeto automatiza a conciliação de planos de clientes entre o sistema Omie e o painel do Google, realizando o download dos relatórios do Google Drive, processando-os e gerando um relatório de divergências para facilitar o faturamento.

## Funcionalidades

- Monitoramento contínuo de uma pasta no Google Drive.
- Download automático dos relatórios necessários (Omie e Painel).
- Processamento e comparação dos dados dos relatórios.
- Geração de planilha de divergências.
- Upload automático do relatório gerado para o Google Drive.
- Limpeza automática dos arquivos processados.

## Requisitos

- Python 3
- Conta de serviço do Google com permissão de leitura e escrita na pasta do Drive
- Relatório da Omie em Excel (.xlsx)
- Relatório de clientes do painel do Google em CSV (.csv)

## Instalação

1. Clone este repositório:
   ```sh
   git clone <url-do-repositorio>
   ```
2. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
3. Coloque o arquivo `token-drive.json` (credenciais da conta de serviço) na raiz do projeto.

## Configuração

- Edite o arquivo `src/config.py` para ajustar o caminho das credenciais, o ID da pasta do Drive e o diretório de downloads, se necessário.

## Como usar

1. Faça upload dos relatórios da Omie (.xlsx) e do Painel (.csv) para a pasta do Google Drive configurada.
2. Execute o sistema:
   ```sh
   python src/main.py
   ```
3. O sistema irá monitorar a pasta do Drive. Quando ambos os arquivos forem encontrados, fará o download, processará, gerará o relatório de divergências e fará o upload do resultado para o Drive.
4. Os arquivos processados serão removidos automaticamente da pasta de downloads local.

## Estrutura do Projeto

```
gerador-faturamento/
├── src/
│   ├── config.py
│   ├── drive_service.py
│   ├── generate_plan.py
│   ├── main.py
│   ├── monitor_controller.py
│   ├── service.py
│   └── planilhas/           # Pasta para arquivos baixados
├── requirements.txt
├── token-drive.json         # Credenciais da conta de serviço
└── readme.md
```

## Observações

- O sistema executa o monitoramento em loop, verificando a cada 60 segundos.
- Certifique-se de que a conta de serviço tem permissão de editor na pasta do Google Drive.
- O nome do arquivo gerado será baseado na data do relatório da Omie.

## Contato

Dúvidas ou sugestões? Entre em contato com o responsável pelo projeto.
