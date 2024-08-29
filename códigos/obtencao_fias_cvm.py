# -*- coding: utf-8 -*-
"""
Created on Fri May 17 16:08:42 2024

@author: Isa_Lisboa
"""

#%% Instalação das Bibliotecas

!pip install pandas
!pip install requests

#%% Importação das bibliotecas
import pandas as pd
import requests as rq
import zipfile
import os
import shutil

#%% Caminhos para salvar downloads e extrações
path_save = r"C:\Users\User\Documents\GitHub\Analise_FIAs\download_files"
path_extract = r"C:\Users\User\Documents\GitHub\Analise_FIAs\extract_files"
path_csv = r"C:\Users\User\Documents\GitHub\Analise_FIAs"

#%% Funções para obtenção de dados

def download_zip(url, year, month, path_save):
    complemento = f"cda_fi_{year}{month:02d}.zip"
    full_url = url + complemento
    
    path_zip = os.path.join(path_save, complemento)
    extract_to = os.path.join(path_extract, f"cda_fi_{year}{month}")
    
    # Baixar o arquivo ZIP
    response = rq.get(full_url)
    if response.status_code == 200:
        with open(path_zip, "wb") as file:
            file.write(response.content)
        print(f"Arquivo salvo em: {path_zip}")
    else:
        print(f"Erro ao baixar o arquivo: {full_url}, Status Code: {response.status_code}")
        return
    
    os.makedirs(extract_to, exist_ok=True)
    
    try:
        with zipfile.ZipFile(path_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Arquivos extraídos para {extract_to}")
        os.remove(path_zip)
        print(f"Arquivo ZIP removido de: {path_zip}")
    except zipfile.BadZipFile:
        print(f"Erro: {path_zip} não é um arquivo ZIP válido")
        os.remove(path_zip)

def years_month(url, path_save, start_year, start_month, end_year, end_month):
    current_year = start_year
    current_month = start_month
    
    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        download_zip(url, current_year, current_month, path_save)
        
        next_month = current_month + 1
        if next_month > 12:
            next_month = 1
            current_year += 1
        current_month = next_month

def move_and_rename_csv_files(path_extract, path_csv):
    # Cria o diretório para os arquivos CSV se não existir
    os.makedirs(path_csv, exist_ok=True)
    
    for root, dirs, files in os.walk(path_extract):
        for file in files:
            if file.endswith(".csv"):
                old_csv_path = os.path.join(root, file)
                year_month = file.split('_')[-1].split('.')[0]  # Extrai o ano e mês do nome do arquivo
                new_csv_name = f"cda_fi_{year_month}.csv"
                new_csv_path = os.path.join(path_csv, new_csv_name)  # Caminho no diretório csv_files
                
                shutil.move(old_csv_path, new_csv_path)
                print(f"Arquivo CSV movido para: {new_csv_path}")

#%% Obtenção dos dados
url = "https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/"

os.makedirs(path_save, exist_ok=True)
os.makedirs(path_extract, exist_ok=True)

start_year = 2023
start_month = 1
end_year = 2024
end_month = 8

years_month(url, path_save, start_year, start_month, end_year, end_month)
move_and_rename_csv_files(path_extract, path_csv)

#%% Para dados históricos
# Caminhos para salvar downloads e extrações de históricos
path_save_hist = r"C:\Users\User\Documents\GitHub\Analise_FIAs\download_files\hist"
path_extract_hist = r"C:\Users\User\Documents\GitHub\Analise_FIAs\extract_files\hist"
path_csv_hist = r"C:\Users\User\Documents\GitHub\Analise_FIAs\hist"

def download_zip_hist(url, year, path_save):
    complemento = f"cda_fi_{year}.zip"
    full_url = url + complemento
    
    path_zip = os.path.join(path_save, complemento)
    extract_to = os.path.join(path_extract_hist, f"cda_fi_{year}")
    
    # Baixando o arquivo ZIP
    response = rq.get(full_url)
    if response.status_code == 200:
        with open(path_zip, "wb") as file:
            file.write(response.content)
        print(f"Arquivo salvo em: {path_zip}")
    else:
        print(f"Erro ao baixar o arquivo: {full_url}, Status Code: {response.status_code}")
        return
    
    os.makedirs(extract_to, exist_ok=True)
    
    try:
        with zipfile.ZipFile(path_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Arquivos extraídos para {extract_to}")
        os.remove(path_zip)
        print(f"Arquivo ZIP removido de: {path_zip}")
    except zipfile.BadZipFile:
        print(f"Erro: {path_zip} não é um arquivo ZIP válido")
        os.remove(path_zip)

def years_hist(url, path_save, start_year, end_year):
    current_year = start_year
    
    while current_year <= end_year:
        download_zip_hist(url, current_year, path_save)
        current_year += 1  # Incrementa o ano

#%% Obtenção dos dados até 2022
url_hist = "https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/HIST/"

os.makedirs(path_save_hist, exist_ok=True)
os.makedirs(path_extract_hist, exist_ok=True)

start_year_hist = 2018
end_year_hist = 2023

years_hist(url_hist, path_save_hist, start_year_hist, end_year_hist)
move_and_rename_csv_files(path_extract_hist, path_csv_hist)

#%% Lendo e filtrando arquivos CSV no diretório extract_files
dirs = [path_extract_hist, path_extract]

# Lista para armazenar os DataFrames filtrados
df_list = []

# Iterando pelos diretórios e arquivos CSV
for dir_path in dirs:
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    print(f"Lendo o arquivo: {file_path}")  # Mensagem de log
                    try:
                        df = pd.read_csv(file_path, encoding='cp1252', sep=';')
                        # Filtrar onde TP_APLIC = "Ações"
                        df_filtered = df[df['TP_APLIC'] == "Ações"]
                        # Adicionar o DataFrame filtrado à lista
                        df_list.append(df_filtered)
                    except Exception as e:
                        print(f"Erro ao ler o arquivo {file_path}: {e}")
    else:
        print(f"O diretório {dir_path} não existe.")

# Concatenando todos os DataFrames filtrados em um único DataFrame
if df_list:
    FIAs_completo = pd.concat(df_list, ignore_index=True)
    # Exibir as primeiras linhas do DataFrame resultante para verificação
    print(FIAs_completo.head())
    
    # Salvando o DataFrame filtrado em um arquivo CSV
    output_path = os.path.join(path_csv, "FIAs_completo_acoes.csv")
    FIAs_completo.to_csv(output_path, index=False)
    print(f"DataFrame completo salvo em: {output_path}")
    
    # Limpando o diretório, deixando apenas o arquivo FIAs_completo
    for root, dirs, files in os.walk(path_extract):
        for file in files:
            file_path = os.path.join(root, file)
            if file != "FIAs_completo_acoes.csv":
                os.remove(file_path)
                print(f"Arquivo removido: {file_path}")
else:
    print("Nenhum arquivo CSV filtrado encontrado ou nenhum DataFrame foi criado.")