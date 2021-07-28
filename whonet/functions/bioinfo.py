from whonet.models import *
import pandas as pd
import numpy as np
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
import os


dirpath = os.getcwd()
epi_data = pd.read_excel(dirpath + '/whonet/static/bioinfo_xl/EPI_DATA_CLEAN.xlsx')
epi_data = epi_data.drop(['Sample id'], axis=1)

def merge_epi_data(input):
   df_input = pd.read_excel(input)
   df_merge_col = pd.merge(df_input, epi_data,  on='Alternative sample id', how = 'outer')
   df_merge_col.dropna(subset = ["Sample id"], inplace=True)
   
   df_merge_col = df_merge_col[df_merge_col.columns.drop(list(df_merge_col.filter(regex='Unnamed')))]
    
   return df_merge_col



def clean_amr_data(input):
    df = pd.read_csv(input)
    df.drop([col for col in df.columns if 'ref_seq' not in col and 'name' not in col],axis=1,inplace=True)
    df.fillna('NO', inplace=True)
    return df