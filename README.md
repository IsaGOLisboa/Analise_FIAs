Analise_FIAs

Descrição
Este repositório tem como objetivo a obtenção e análise de dados de Fundos de Investimento em Ações (FIAs) disponibilizados pela CVM. O projeto permite a coleta automatizada de dados históricos e atuais dos FIAs, filtrando especificamente para fundos que investem em ações, e a realização de diversas análises, como preços médios de compra e venda, movimentações, e decisões dos fundos após lucros ou prejuízos.

Funcionalidades
Obtenção dos Dados: Os dados são obtidos automaticamente do site da CVM através do script obtencao_fundos_cvm.
Análise por Fundo: O script fundos_top realiza a análise detalhada dos fundos selecionados.
Filtragem Específica: Foco nos fundos que investem em ações, com análises direcionadas para os anos de 2023 e 2024, e histórico desde 2018.
Análises Realizadas:
Compra e Venda de Ações: Identifica quais ações os fundos de interesse têm comprado ou vendido, e a quais valores.
Preço Justo da Ação: Determina o preço considerado justo para cada ação pelos fundos analisados.
Manutenção de Posição: Verifica se a posição na carteira foi mantida, aumentada ou diminuída nos últimos anos.
Reação a Prejuízos: Analisa se, após um prejuízo, o fundo comprou, vendeu ou manteve sua posição na ação na data de competência seguinte.
Como Usar
Pré-requisitos
Python 3.x
Bibliotecas Python:
pandas
requests
zipfile
os
shutil
matplotlib
fpdf (opcional, para gerar relatórios em PDF)
Instalação
Clone o repositório:

bash
Copiar código
git clone https://github.com/IsaGOLisboa/Analise_FIAs.git
cd Analise_FIAs
Instale as dependências necessárias:

bash
Copiar código
pip install -r requirements.txt
Execução
Obtenção dos Dados:

Execute o script obtencao_fundos_cvm.py para baixar e processar os dados dos FIAs.
Os dados serão baixados e extraídos para os diretórios configurados no script.
Análise dos Fundos:

Execute o script fundos_top.py para realizar as análises sobre os fundos de interesse.
Atualize os CNPJs dos fundos de interesse diretamente no script, caso queira analisar outros fundos.
Geração de Relatórios:

Os resultados podem ser exportados para arquivos CSV ou PDF, dependendo da configuração.
Estrutura do Projeto
plaintext
Copiar código
Analise_FIAs/
│
├── download_files/           # Diretório onde os arquivos ZIP são baixados
├── extract_files/            # Diretório onde os arquivos CSV são extraídos
├── scripts/
│   ├── obtencao_fundos_cvm.py # Script para obtenção dos dados da CVM
│   └── fundos_top.py          # Script para análise dos fundos
├── FIAs_completo_acoes.csv    # Arquivo CSV final com todos os dados filtrados (não incluído no repositório)
├── README.md                  # Documentação do projeto
└── .gitignore                 # Arquivos e diretórios ignorados no Git
Personalização
Alterar Diretórios de Input e Output:

Para replicar as análises, atualize os caminhos dos diretórios de input e output conforme necessário nos scripts.
Adicionar Novos Fundos:

Para analisar novos fundos, adicione os CNPJs dos fundos desejados no script fundos_top.py.
Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests para melhorias, correções de bugs ou novas funcionalidades.

Licença
Este projeto está licenciado sob a Licença Apache 2.0. Veja o arquivo LICENSE para mais detalhes.

Contato
Para dúvidas ou sugestões, entre em contato com ilisboa@yahoo.com.br.





  
