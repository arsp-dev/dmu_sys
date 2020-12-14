from whonet.models import *
import pandas as pd
import numpy as np
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
import os
from django.db import IntegrityError
from whonet.functions.df_helper import concat_all_df


dirpath = os.getcwd()

enterics = pd.read_excel(dirpath + '/whonet/static/whonet_xl/org_list_ent.xlsx')
fastidious = pd.read_excel(dirpath + '/whonet/static/whonet_xl/org_list_fast.xlsx')

ent_list = enterics['ORG'].values.tolist()
fast_list = fastidious['ORG'].values.tolist()


def get_ent_fast(file_id,file_name):
    df = concat_all_df(file_id)
    df.columns = map(str.upper, df.columns)
    
    df_ent = df[df['ORGANISM'].isin(ent_list)]
    df_fast = df[df['ORGANISM'].isin(fast_list)]
    
    
    writer = pd.ExcelWriter('ENTERIC_PATHOGENS_FASTIDIOUS_ORGANISM_{}.xlsx'.format(file_name), engine='xlsxwriter')
    if len(df_ent) > 0:
        df_ent.to_excel(writer,sheet_name='ENTERICS PATHOGENS', index=False)
        
    if len(df_fast) > 0:
        df_fast.to_excel(writer,sheet_name='FASTIDIOUS ORGANISMS', index=False)
   
    
    writer.save()
    
    return writer