import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from gspread_formatting import *
from PIL import Image
from datetime import date

# Connect to Google Sheets

scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)
sa = gspread.service_account('service_account.json')

@st.cache(allow_output_mutation=True)
def bases(sa):
    
    name_sheet = 'Bases para sequenciamento'
    worksheet = 'Carga_Vendas'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list = wks.get_all_records()
    table1 = pd.DataFrame(list)

    name_sheet = 'modelo levantamento'
    worksheet = 'base conjuntos'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list = wks.get_all_records()
    table2 = pd.DataFrame(list)

    name_sheet = 'SALDO DE RECURSO'
    worksheet = 'saldo_python'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list = wks.get_all_records()
    table3 = pd.DataFrame(list)

    return(table1, table2, table3)

with st.form(key="Fform"):
    
    data_carga = st.date_input("Data da carga").strftime("%d/%m/%Y")

    if st.form_submit_button("Gerar"):
        
        base_vendas, base_conjuntos, base_saldo = bases(sa)
        base_vendas = base_vendas.loc[base_vendas['PED_PREVISAOEMISSAODOC'] == data_carga][['PED_NUMEROSERIE','PED_PREVISAOEMISSAODOC','PED_RECURSO.CODIGO','PED_QUANTIDADE']]
        
        carretas_quantidade = base_vendas[['PED_RECURSO.CODIGO','PED_QUANTIDADE']].groupby(['PED_RECURSO.CODIGO']).sum().reset_index()
        carretas_quantidade['PED_RECURSO.CODIGO'] = carretas_quantidade['PED_RECURSO.CODIGO'].str.replace('AN','') # Azul
        carretas_quantidade['PED_RECURSO.CODIGO'] = carretas_quantidade['PED_RECURSO.CODIGO'].str.replace('VJ','') # Verde
        carretas_quantidade['PED_RECURSO.CODIGO'] = carretas_quantidade['PED_RECURSO.CODIGO'].str.replace('LC','') # Laranja
        carretas_quantidade['PED_RECURSO.CODIGO'] = carretas_quantidade['PED_RECURSO.CODIGO'].str.replace('VM','') # Vermelho
        carretas_quantidade['PED_RECURSO.CODIGO'] = carretas_quantidade['PED_RECURSO.CODIGO'].str.replace('AV','') # Amarelo
        carretas_quantidade['PED_RECURSO.CODIGO'] = carretas_quantidade['PED_RECURSO.CODIGO'].str.strip()

        lista_carretas = list(carretas_quantidade['PED_RECURSO.CODIGO'])
        
        conjuntos_filtrados = base_conjuntos[base_conjuntos['Recurso'].isin(lista_carretas)][['Código','Peca','Qtde']].loc[base_conjuntos['Peca'] != '']
        conjuntos_filtrados['Qtde'] = conjuntos_filtrados['Qtde'].astype(int)
        conjuntos_filtrados = conjuntos_filtrados.reset_index(drop=True)
        conjuntos_filtrados['Código'] = conjuntos_filtrados['Código'].astype(str)
        conjuntos_filtrados = conjuntos_filtrados.groupby(['Código','Peca']).sum().reset_index()

        pecas_quantidade = conjuntos_filtrados.groupby(['Código','Peca']).sum().reset_index()
    
        base_saldo['codigo'] = base_saldo['2o. Agrupamento'].str[:6]
        base_saldo = base_saldo[['codigo','Saldo','4o. Agrupamento']]

        for i in range(len(conjuntos_filtrados)):
            if len(conjuntos_filtrados['Código'][i]) == 5:
                conjuntos_filtrados['Código'][i] = "0" + conjuntos_filtrados['Código'][i] 

        lista_conjuntos = list(conjuntos_filtrados['Código'])

        saldo_filtrado = base_saldo[base_saldo['codigo'].isin(lista_conjuntos)].groupby(['codigo','4o. Agrupamento']).sum().reset_index()
        
        for i in range(len(saldo_filtrado)):
            if saldo_filtrado['4o. Agrupamento'][i] == '':
                saldo_filtrado['4o. Agrupamento'][i] = 'Finalizado' 
        
        colunas = list(saldo_filtrado['4o. Agrupamento'].drop_duplicates())
        
        for i in range(len(colunas)):
            j = colunas[i]
            saldo_filtrado[j] = ''

            for c in range(len(saldo_filtrado)):
                if saldo_filtrado['4o. Agrupamento'][c] == j:
                    saldo_filtrado[j][c] = saldo_filtrado['Saldo'][c]
                else:
                    pass

        #for k in range(len(saldo_filtrado)):
        #    if saldo_filtrado['4o. Agrupamento'][k].str.contains('Serras').any():
        #        saldo_filtrado['4o. Agrupamento'][k] = 'Serras'

        #saldo_filtrado['4o. Agrupamento'] = saldo_filtrado['4o. Agrupamento'].astype(str)
        #saldo_filtrado['4o. Agrupamento'][43].str.contains('Serras')

        saldo_filtrado
        #base_saldo
        conjuntos_filtrados
        #st.dataframe(base_vendas)
        
