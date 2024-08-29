###################Bibliotecas necessárias#########################

!pip install pandas
! pip install fpdf
! pip install numpy


import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np
from datetime import datetime
##########################Diretórios para salvar e obter arquivos#############################
#diretório para obter df com todos os fundos extraídos da cvm:
input_fundos = r"C:\Users\User\Documents\GitHub\Analise_FIAs\FIAs_completo_acoes.csv"

#diretório para salvar pdfs das ações gerados
diretorio_acoes_pdf = r"C:\Users\User\Documents\GitHub\Analise_FIAs\dfs_acoes"

#diretório para salvar os gráficos gerados em pdf
diretorio_graficos = r"C:\Users\User\Documents\GitHub\Analise_FIAs\graficos_fundos.pdf"
#########################Filtrando os fundos de interesse####################################
fundos_completo = pd.read_csv(input_fundos)
# Definindo os CNPJs dos fundos para compor a análise 
cnpjs_filtrar = [
    '10.500.884/0001-05',
    '37.916.879/0001-26',
    '14.213.077/0001-54',
    '14.438.229/0001-17',
    '36.352.539/0001-57',
    '18.302.338/0001-63'
]

# Filtrando os fundos pelos CNPJs especificados
fundos_top_five = fundos_completo[fundos_completo['CNPJ_FUNDO'].isin(cnpjs_filtrar)]

# Mantendo apenas as colunas necessárias
colunas_para_manter = [
    'CNPJ_FUNDO', 'DENOM_SOCIAL', 'DT_COMPTC', 'TP_APLIC',
    'TP_ATIVO', 'QT_VENDA_NEGOC', 'VL_VENDA_NEGOC', 
    'QT_AQUIS_NEGOC', 'VL_AQUIS_NEGOC', 'QT_POS_FINAL', 'CD_ATIVO',
    'VL_MERC_POS_FINAL', 'VL_CUSTO_POS_FINAL', 'DT_CONFID_APLIC'
]

# Criando um dicionário dinâmico de DataFrames por fundo
fundos = {}
dfs_fundos = {}

for fundo in fundos_top_five['DENOM_SOCIAL'].unique():
    # Renomeando com os dois primeiros nomes
    fundo_nome_reduzido = "_".join(fundo.split()[:2]).lower()
    
    fundos[fundo_nome_reduzido] = fundos_top_five[fundos_top_five['DENOM_SOCIAL'] == fundo]
    
    dfs_fundos[fundo_nome_reduzido] = {}
    
    for ativo in fundos[fundo_nome_reduzido]['CD_ATIVO'].unique():
        df_filtrado = fundos[fundo_nome_reduzido][fundos[fundo_nome_reduzido]['CD_ATIVO'] == ativo][colunas_para_manter]
        
        # Calculando VL_venda e VL_compra, substituindo NaN por 0 em VL_compra apenas para o cálculo de lucro
        df_filtrado['VL_venda'] = df_filtrado['VL_VENDA_NEGOC'] / df_filtrado['QT_VENDA_NEGOC']
        df_filtrado['VL_compra'] = df_filtrado['VL_AQUIS_NEGOC'] / df_filtrado['QT_AQUIS_NEGOC']
        
        # Substituindo NaN por 0 apenas para cálculo de lucro
        df_filtrado['VL_compra_corrigido'] = df_filtrado['VL_compra'].fillna(0)

        # Calculando o lucro
        df_filtrado['saldo_acoes'] = df_filtrado['QT_AQUIS_NEGOC'] - df_filtrado['QT_VENDA_NEGOC']
        df_filtrado['lucro'] = df_filtrado['QT_VENDA_NEGOC'] * (df_filtrado['VL_venda'] - df_filtrado['VL_compra_corrigido'])
        
        # Calculando o valor pós-ação
        df_filtrado['valor_pos_acao'] = df_filtrado['VL_MERC_POS_FINAL'] / df_filtrado['QT_POS_FINAL']

        # Para cálculos de média, excluindo zeros
        df_filtrado['VL_compra_media'] = df_filtrado['VL_compra'].replace(0, pd.NA)
        
        dfs_fundos[fundo_nome_reduzido][ativo] = df_filtrado


print(dfs_fundos.keys())

############################################Exemplo de visualização do df de um fundo#####################################
# Visualizando dos dfs filtrados
for ativo, df in dfs_fundos['charles_river'].items():
    print(f"DataFrame para {ativo} no fundo charles_river:")
    print(df.head())

# Exemplo de como salvar um fundo específico em um arquivo Excel
diretorio_destino = r"C:\Users\User\Documents\GitHub\Analise_FIAs"

# Nome do arquivo Excel para salvar
nome_arquivo = "real_investor_completo_corrigido.xlsx"

# Caminho completo do arquivo
caminho_completo = os.path.join(diretorio_destino, nome_arquivo)

# Lista para armazenar todos os DataFrames relacionados ao fundo "real_investor"
real_investor_dfs = []

# Iterando sobre os itens em dfs_fundos e coletar todos os relacionados a "real_investor"
for nome_fundo, dict_ativos in dfs_fundos.items():
    if nome_fundo == 'real_investor':
        for ativo, df_ativo in dict_ativos.items():
            real_investor_dfs.append(df_ativo)

# Concatenando todos os DataFrames relacionados a "real_investor"
df_real_investor_completo = pd.concat(real_investor_dfs)

# Verificando o intervalo de datas presente no DataFrame
min_data = df_real_investor_completo['DT_COMPTC'].min()
max_data = df_real_investor_completo['DT_COMPTC'].max()

print(f"Intervalo de datas no fundo 'real_investor': {min_data} a {max_data}")

# Salvando em Excel
df_real_investor_completo.to_excel(caminho_completo, index=False)

print(f"Dados do fundo 'real_investor' salvos em: {caminho_completo}")

########################################Analisando cada ação do fndo e salvando em pdf############################
# Dicionário para armazenar os DataFrames de cada ação
dfs_acoes = {}

# Iterando sobre cada fundo e seus respectivos DataFrames de ações
for nome_fundo, dict_ativos in dfs_fundos.items():
    for ativo, df_ativo in dict_ativos.items():
        # Se a ação já existe no dicionário dfs_acoes, concatena
        if ativo in dfs_acoes:
            dfs_acoes[ativo] = pd.concat([dfs_acoes[ativo], df_ativo])
        else:
            # Se não existe, cria a entrada no dicionário
            dfs_acoes[ativo] = df_ativo

# Verificando as ações únicas que foram adicionadas ao dicionário
print("Ações únicas presentes em dfs_acoes:")
print(dfs_acoes.keys())

# Coletando todas as ações únicas presentes em dfs_acoes
acoes_unicas = set()

for nome_fundo, df_fundo in dfs_fundos.items():
    for ativo, df_ativo in df_fundo.items():
        acoes_unicas.add(str(ativo))  # Convertendo todos os códigos de ativo para strings

# Removendo valores NaN (ou None) e ordenando a lista de ações únicas
nomes_acoes = sorted([acao for acao in acoes_unicas if pd.notna(acao)])

print(nomes_acoes)

# Função para analisar uma ação por fundo
def analisar_acao_por_fundo(data, nome_acao, diretorio):
    relatorio = f"\nAnalisando a ação: {nome_acao}\n"
    
    # Agrupando os dados por fundo
    fundos = data['DENOM_SOCIAL'].unique()
    
    # Definindo o ano atual e os anos relevantes
    ano_atual = datetime.now().year
    anos_relevantes = ['2023', str(ano_atual)]
    
    for fundo in fundos:
        fundo_data = data[data['DENOM_SOCIAL'] == fundo]

        # Análise Completa
        relatorio += f"\nAnálise completa do fundo: {fundo}\n"
        relatorio += realizar_analise_fundo(fundo_data)
        
        # Filtrando dados para 2023 e 2024 (ou anos relevantes)
        fundo_data_relevante = fundo_data[fundo_data['DT_COMPTC'].str[:4].isin(anos_relevantes)]
        
        if not fundo_data_relevante.empty:
            relatorio += f"\nAnálise específica para 2023 e 2024 do fundo: {fundo}\n"
            relatorio += realizar_analise_fundo(fundo_data_relevante)
        else:
            relatorio += f"\nNão há dados para o fundo {fundo} em 2023 e 2024.\n"
    
    # Salvando o relatório em PDF
    nome_arquivo_pdf = f"{diretorio}\\{nome_acao}_relatorio.pdf"
    salvar_relatorio_em_pdf(relatorio, nome_arquivo_pdf)
    print(f"Relatório para {nome_acao} salvo em: {nome_arquivo_pdf}")

# Função auxiliar para realizar a análise de um fundo
def realizar_analise_fundo(fundo_data):
    relatorio = ""

    # Preenchendo valores NaN em VL_compra com 0 para evitar problemas no cálculo de lucro
    fundo_data['VL_compra'].fillna(0, inplace=True)

    # Ordenando as transações por data (DT_COMPTC)
    fundo_data = fundo_data.sort_values(by='DT_COMPTC')

    # Exibindo as transações: Datas, VL_venda, VL_compra, saldo_acoes
    transacoes = fundo_data[['DT_COMPTC', 'VL_venda', 'VL_compra', 'saldo_acoes']]
    transacoes['VL_venda'] = transacoes['VL_venda'].map('{:.2f}'.format)
    transacoes['VL_compra'] = transacoes['VL_compra'].map('{:.2f}'.format)
    relatorio += "\nTransações do Fundo:\n"
    relatorio += transacoes.to_string(index=False) + "\n"

    # Verificando se após um lucro negativo houve uma compra, venda ou manutenção de posição com base em QT_POS_FINAL
    total_lucro_negativo = 0
    compras_apos_lucro_negativo = 0
    vendas_apos_lucro_negativo = 0
    mantem_posicao_apos_lucro_negativo = 0

    for i in range(1, len(fundo_data)):
        lucro_atual = fundo_data.iloc[i-1]['lucro']
        qt_pos_anterior = fundo_data.iloc[i-1]['QT_POS_FINAL']
        qt_pos_atual = fundo_data.iloc[i]['QT_POS_FINAL']
        
        if lucro_atual < 0:  # Verifica se o lucro na linha anterior foi negativo
            total_lucro_negativo += 1
            # Verificando se houve compra, venda ou manutenção de posição
            if qt_pos_atual > qt_pos_anterior:
                compras_apos_lucro_negativo += 1
            elif qt_pos_atual < qt_pos_anterior:
                vendas_apos_lucro_negativo += 1
            else:
                mantem_posicao_apos_lucro_negativo += 1

    # Exibir mensagem se não houver lucro negativo
    if total_lucro_negativo == 0:
        relatorio += "\nNão houve lucro negativo durante o período analisado.\n"
    else:
        # Calculando porcentagens
        perc_compras_apos_lucro_negativo = (compras_apos_lucro_negativo / total_lucro_negativo) * 100
        perc_vendas_apos_lucro_negativo = (vendas_apos_lucro_negativo / total_lucro_negativo) * 100
        perc_mantem_posicao_apos_lucro_negativo = (mantem_posicao_apos_lucro_negativo / total_lucro_negativo) * 100
        
        relatorio += f"\nO fundo comprou em {perc_compras_apos_lucro_negativo:.2f}% das vezes após lucro negativo, vendeu em {perc_vendas_apos_lucro_negativo:.2f}% das vezes e manteve a posição em {perc_mantem_posicao_apos_lucro_negativo:.2f}% das vezes após lucro negativo.\n"

    # Analisando o preço justo baseado nos valores de compra e venda
    preco_justo_compra = fundo_data[fundo_data['VL_AQUIS_NEGOC'] > 0]['VL_AQUIS_NEGOC'] / fundo_data[fundo_data['VL_AQUIS_NEGOC'] > 0]['QT_AQUIS_NEGOC']
    preco_justo_venda = fundo_data[fundo_data['VL_VENDA_NEGOC'] > 0]['VL_VENDA_NEGOC'] / fundo_data[fundo_data['VL_VENDA_NEGOC'] > 0]['QT_VENDA_NEGOC']
    
    # Excluindo os valores de compra com VL_compra igual a zero para o cálculo de médias
    preco_justo_compra_mean = preco_justo_compra[preco_justo_compra > 0].mean()
    preco_justo_venda_mean = preco_justo_venda.mean()

    preco_medio_pos = fundo_data['valor_pos_acao'].mean()
    lucro_total = fundo_data['lucro'].sum()

    # Adicionando os resultados ao relatório
    relatorio += "\nPreço Médio de Compra: {:.2f} reais por ação\n".format(preco_justo_compra_mean)
    relatorio += "Preço Médio de Venda: {:.2f} reais por ação\n".format(preco_justo_venda_mean)
    relatorio += "Preço Médio Pós: {:.2f} reais por ação\n".format(preco_medio_pos)

    participacao_inicio = fundo_data.iloc[0]['QT_POS_FINAL']  # Definindo participacao_inicio
    participacao_fim = fundo_data.iloc[-1]['QT_POS_FINAL']   # Definindo participacao_fim

    if participacao_fim > participacao_inicio:
        relatorio += f"\nO fundo aumentou sua participação de {participacao_inicio} para {participacao_fim} ações.\n"
    elif participacao_fim < participacao_inicio:
        relatorio += f"\nO fundo reduziu sua participação de {participacao_inicio} para {participacao_fim} ações.\n"
    else:
        relatorio += f"\nO fundo manteve sua participação constante em {participacao_inicio} ações.\n"

    relatorio += f"\nLucro ou Prejuízo Total: {lucro_total:.2f} reais\n"

    return relatorio

# Função para salvar o relatório em PDF
def salvar_relatorio_em_pdf(texto_relatorio, nome_arquivo):
    pdf = FPDF()
    pdf.add_page()

    # Configurações de fonte
    pdf.set_font("Arial", size=12)
    
    # Adicionando o texto ao PDF
    pdf.multi_cell(0, 10, texto_relatorio)
    
    # Salvando o arquivo PDF
    pdf.output(nome_arquivo)

# Diretório de destino para os PDFs das ações
diretorio_acoes = diretorio_acoes_pdf

# Função para salvar DataFrames em CSV
def salvar_acoes_em_csv(dfs_acoes, nomes_acoes, diretorio):
    for nome_acao in nomes_acoes:
        if nome_acao in dfs_acoes:
            caminho_arquivo = os.path.join(diretorio, f"{nome_acao}.csv")
            dfs_acoes[nome_acao].to_csv(caminho_arquivo, index=False)
            print(f"Ação '{nome_acao}' salva em: {caminho_arquivo}")
        else:
            print(f"A ação '{nome_acao}' não foi encontrada no dicionário 'dfs_acoes'.")

############################################Gráficos##############################################################
# Função para gerar e salvar gráficos de pizza em uma única imagem para cada fundo
def gerar_graficos_pizza_pdf(fundos_trim, nome_fundo, pdf):
    # Obter as datas únicas em 'fundos_trim'
    datas_unicas = sorted(fundos_trim['DT_COMPTC'].unique())

    # Preparando o layout para os gráficos
    num_graficos = len(datas_unicas)  # Número de gráficos a serem gerados
    fig, axes = plt.subplots(nrows=(num_graficos + 1) // 2, ncols=2, figsize=(18, 14))  # Aumentar tamanho da figura

    # Garantindo que 'axes' seja sempre uma lista unidimensional
    if num_graficos == 1:
        axes = [axes]
    elif isinstance(axes, np.ndarray):
        axes = axes.flatten()

    temp_files = []  # Lista para armazenar os nomes dos arquivos temporários

    for i, data in enumerate(datas_unicas):
        # Filtrando os dados para a data específica
        fundo_data = fundos_trim[fundos_trim['DT_COMPTC'] == data]
        
        # Agrupando por 'CD_ATIVO' e calculando a soma de 'QT_POS_FINAL'
        composicao = fundo_data.groupby('CD_ATIVO')['QT_POS_FINAL'].sum()

        # Calculando o percentual de cada ativo em relação ao total
        composicao_percentual = (composicao / composicao.sum()) * 100
        
        # Explodindo as fatias do gráfico paramelhorar a visualização
        explode = [0.05] * len(composicao_percentual)  # Explode equal for all

        # Plotando o gráfico de pizza
        ax = axes[i]
        composicao_percentual.plot.pie(ax=ax, autopct='%1.1f%%', startangle=90, explode=explode)
        
        ax.set_ylabel('')
        ax.set_title(f"{nome_fundo} - {data}")

        # Salvando o gráfico como uma imagem temporária
        temp_filename = f'temp_{nome_fundo}_{i}.png'
        plt.savefig(temp_filename)
        temp_files.append(temp_filename)

    # Gráfico para o último DT_COMPTC disponível
    ultima_data = fundos_trim['DT_COMPTC'].max()
    fundo_ultima_data = fundos_trim[fundos_trim['DT_COMPTC'] == ultima_data]
    composicao_ultima = fundo_ultima_data.groupby('CD_ATIVO')['QT_POS_FINAL'].sum()
    composicao_ultima_percentual = (composicao_ultima / composicao_ultima.sum()) * 100
    
    # Explodindo as fatias do gráfico para melhorar a visualização
    explode = [0.05] * len(composicao_ultima_percentual)  # Explode equal for all

    ax = axes[num_graficos] if num_graficos < len(axes) else axes[-1]
    temp_filename_final = f'temp_final_{nome_fundo}.png'
    composicao_ultima_percentual.plot.pie(ax=ax, autopct='%1.1f%%', startangle=90, explode=explode)
    ax.set_ylabel('')
    ax.set_title(f"{nome_fundo} - Última Data Disponível ({ultima_data})")

    plt.tight_layout()  # Ajustando o layout dos gráficos para evitar sobreposição
    plt.savefig(temp_filename_final)
    temp_files.append(temp_filename_final)

    # Fechando a figura para liberar memória
    plt.close(fig)

    # Adicionando a última imagem ao PDF e remover temporárias
    pdf.add_page()
    pdf.image(temp_filename_final, x=10, y=10, w=190)
    
    # Removendo imagens temporárias anteriores, mantendo apenas a final
    for temp_file in temp_files[:-1]:
        os.remove(temp_file)
    
    # Retornando o nome do arquivo temporário final
    return temp_filename_final

# Função para limpar o arquivo temporário final
def limpar_arquivos_temporarios_finais(final_files):
    for final_file in final_files:
        try:
            os.remove(final_file)
            print(f"Arquivo temporário final removido: {final_file}")
        except Exception as e:
            print(f"Erro ao tentar remover o arquivo {final_file}: {e}")

# Definindo o ano atual e o ano anterior
ano_atual = datetime.now().year
ano_anterior = ano_atual - 1

# Meses de interesse
meses_interesse = ['01', '03', '06', '09', '12']  # Janeiro, Março, Junho, Setembro, Dezembro

# Criar um PDF
pdf = FPDF()

# Lista para armazenar os nomes dos arquivos temporários finais
final_files = []

# Iterando sobre cada fundo em dfs_fundos
for nome_fundo, dict_ativos in dfs_fundos.items():
    print(f"Processando fundo: {nome_fundo}")

    # Combinando todos os DataFrames do fundo em um único DataFrame
    df_fundo = pd.concat(dict_ativos.values())

    # Filtrando as datas de interesse para o ano atual e o ano anterior
    fundos_trim = df_fundo[
        ((df_fundo['DT_COMPTC'].str[:4] == str(ano_atual)) & (df_fundo['DT_COMPTC'].str[5:7].isin(meses_interesse))) |
        ((df_fundo['DT_COMPTC'].str[:4] == str(ano_anterior)) & (df_fundo['DT_COMPTC'].str[5:7].isin(meses_interesse)))
    ]

    # Gerando e salvar gráficos de pizza no PDF
    temp_file_final = gerar_graficos_pizza_pdf(fundos_trim, nome_fundo, pdf)
    final_files.append(temp_file_final)

# Salvando o PDF final
output_path = diretorio_graficos
pdf.output(output_path)
print(f"Gráficos salvos em: {output_path}")

# Limpando arquivos temporários finais
limpar_arquivos_temporarios_finais(final_files)