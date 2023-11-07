#%%
import pandas as pd
import json
import streamlit as st

import requests
from bs4 import BeautifulSoup

from io import BytesIO

from datetime import datetime

#%%

st.title("Webscrapping metadata DatosAbiertos.gob.pe")

st.text("Put the links of DATASETS only")

def _get_tables(url):
    # url = "https://www.datosabiertos.gob.pe/dataset/minsa-salud-mental"

    DThtml = requests.get(url)

    #%%
    soup = BeautifulSoup(DThtml.content, 'html.parser')

    #%%
    
    tablex = soup.findAll('div', class_='field-name-field-identifier')
    # reconocer el objeto que tenga por nombre 
    # field-name-field-identifier

    if len(tablex)==1:
        idx = tablex[0].text
        print(idx)
        url_json = f"https://www.datosabiertos.gob.pe/api/3/action/package_show?id={idx}"
        json_mess = requests.get(url_json)
    else:
        print("No identifier found")


    json_content = json_mess.content

    my_json = json_content.decode('utf8').replace("'", '"')

    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(my_json)
    # len(data['result']) ==1


    df = pd.DataFrame.from_dict(data['result']).rename({'id':'dataset_id'}, axis=1)
    dftables = pd.DataFrame.from_dict(data['result'][0]['resources'])
    dftables['dataset_id'] = idx

    return df, dftables

# @st.cache_data
def to_excel(dict_df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    dict_df['datasets'].to_excel(writer, index=True, sheet_name='Datasets')
    dict_df['resources'].to_excel(writer, index=True, sheet_name='Resources')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

df_links = pd.DataFrame(columns=['Links'])
df_links_input = st.data_editor(df_links, num_rows='dynamic', hide_index=True)
# df_links_input = df_links_input.rename({'Links                                                                                               ':'Links'}, axis=1)
df_links_input = df_links_input.dropna(subset=['Links'])
df_links_input.index = range(df_links_input.shape[0])

st.table(df_links_input)

if st.button('Get data'):
    df_main = pd.DataFrame()
    dftables_main = pd.DataFrame()
    for index in df_links_input.index:
        df, dftables = _get_tables(df_links_input.loc[index,'Links'])
        df_main = pd.concat([df_main, df])
        dftables_main = pd.concat([dftables_main, dftables])

    today = str(datetime.today())

    df_main_xlsx = to_excel({'datasets':df_main,'resources':dftables_main})
    st.download_button(label='📥 Download',
                                        data=df_main_xlsx,
                                        file_name= f'Datasets_{today}.xlsx')
