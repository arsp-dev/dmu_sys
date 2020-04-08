from whonet.models import *
import pandas as pd
import numpy as np
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
import os
from django.db import IntegrityError
from whonet.functions.df_helper import concat_all_df

dirpath = os.getcwd()
whonet_data_summary_referred = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx')
enterobact_all = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx','ENTEROBACTERIACEAE_X_SAL_SHI')
pae = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx','Pseudomonas_aeruginosa')
aba = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx','Acinetobacter_species')
enterobact_all_list = enterobact_all['WHON5_CODE'].values.tolist()
pae_list = pae['WHON5_CODE'].values.tolist()
aba_list = aba['WHON5_CODE'].values.tolist()

def summary_report_referred(file_id,file_name):
    df = concat_all_df(file_id)
    df.columns = map(str.upper, df.columns)
    df['SPEC_DATE'] = pd.to_datetime(df['SPEC_DATE'],errors='ignore')
    df['comp'] = df['SPEC_DATE'].apply(lambda df: get_date_to_compute(df) )
    df['ent_fast'] = df['comp'] - df['SPEC_DATE']
    df['X_REFERRED'] = df['X_REFERRED'].str.replace('.0', '', regex=False)
    df['X_REFERRED'] = pd.to_numeric(df['X_REFERRED'], downcast='signed')
    
    
    
    df_enterobact_all = df[df['ORGANISM'].isin(['eco','kpn'])]
    if len(df_enterobact_all) > 0:
        df_enterobact_all = df_enterobact_all[df_enterobact_all['X_REFERRED'] != 1]
        df_enterobact_all = df_enterobact_all[df_enterobact_all['ent_fast'].dt.days >= 0]
    
    df_enterobact_all_referred = df[df['ORGANISM'].isin(['eco','kpn'])]
    if len(df_enterobact_all_referred) > 0:
        df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['X_REFERRED'] == 1]
        df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['ent_fast'].dt.days >= 0]
    
    df_pae = df[df['ORGANISM'].isin(['pae'])]
    if len(df_pae) > 0:
        df_pae = df_pae[df_pae['X_REFERRED'] != 1]
        df_pae = df_pae[df_pae['ent_fast'].dt.days >= 0]
    
    df_pae_referred = df[df['ORGANISM'].isin(['pae'])]
    if len(df_pae_referred) > 0:
        df_pae_referred = df_pae_referred[df_pae_referred['X_REFERRED'] == 1]
        df_pae_referred = df_pae_referred[df_pae_referred['ent_fast'].dt.days >= 0]
    
    
    df_aba = df[df['ORGANISM'].isin(['aba'])]
    if len(df_aba) > 0:
        df_aba = df_aba[df_aba['X_REFERRED'] != 1]
        df_aba = df_aba[df_aba['ent_fast'].dt.days >= 0]
    
    
    df_aba_referred = df[df['ORGANISM'].isin(['aba'])]
    if len(df_aba_referred) > 0:
        df_aba_referred = df_aba_referred[df_aba_referred['X_REFERRED'] == 1]
        df_aba_referred = df_aba_referred[df_aba_referred['ent_fast'].dt.days >= 0]
    
    for value in enterobact_all_list:
        df_enterobact_all = df_enterobact_all.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
    
    for value in pae_list:
        df_pae = df_pae.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_referred = df_pae_referred.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
    
    for value in aba_list:
        df_aba = df_aba.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_referred = df_aba_referred.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
    
    
    if len(df_enterobact_all) > 0:
        df_enterobact_all = df_enterobact_all.apply(lambda row: check_R(row,enterobact_all_list), axis = 1)
        df_enterobact_all = df_enterobact_all[df_enterobact_all['Test'] == 'R']
        df_enterobact_all.dropna(how = 'all',inplace = True)
        df_enterobact_all = df_enterobact_all.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
    
    if len(df_enterobact_all_referred) > 0:
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: check_R(row,enterobact_all_list), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['Test'] == 'R']
        df_enterobact_all_referred.dropna(how = 'all',inplace = True)
        df_enterobact_all_referred = df_enterobact_all_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
    
    if len(df_pae) > 0:
        df_pae = df_pae.apply(lambda row: check_R(row,pae_list), axis = 1)
        df_pae = df_pae[df_pae['Test'] == 'R']
        df_pae.dropna(how = 'all',inplace = True)
        df_pae = df_pae.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
    
    if len(df_pae_referred) > 0:
        df_pae_referred = df_pae_referred.apply(lambda row: check_R(row,pae_list), axis = 1)
        df_pae_referred = df_pae_referred[df_pae_referred['Test'] == 'R']
        df_pae_referred.dropna(how = 'all',inplace = True)
        df_pae_referred = df_pae_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
    
    
    if len(df_aba) > 0:
        df_aba = df_aba.apply(lambda row: check_R(row,aba_list), axis = 1)
        df_aba = df_aba[df_aba['Test'] == 'R']
        df_aba.dropna(how = 'all',inplace = True)
        df_aba = df_aba.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
    
    
    if len(df_aba_referred) > 0:
        df_aba_referred = df_aba_referred.apply(lambda row: check_R(row,aba_list), axis = 1)
        df_aba_referred = df_aba_referred[df_aba_referred['Test'] == 'R']
        df_aba_referred.dropna(how = 'all',inplace = True)
        df_aba_referred = df_aba_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
    
    
    writer = pd.ExcelWriter('REFERRED_FOR_REVIEW_{}.xlsx'.format(file_name), engine='xlsxwriter')
    if len(df_enterobact_all) > 0:
        df_enterobact_all.to_excel(writer,sheet_name='enterobact_all', index=False)
        
    if len(df_enterobact_all_referred) > 0:
        df_enterobact_all_referred.to_excel(writer,sheet_name='enterobact_all referred', index=False)
    
    if len(df_pae) > 0:
        df_pae.to_excel(writer,sheet_name='pae',index=False)
        
    if len(df_pae_referred) > 0:
        df_pae_referred.to_excel(writer,sheet_name='pae_referred',index=False)
    
    if len(df_aba) > 0:
        df_aba.to_excel(writer, sheet_name='aba', index=False)
    
    if len(df_aba_referred) > 0:
        df_aba_referred.to_excel(writer, sheet_name='aba_referred', index=False)
    
    writer.save()
    
    return writer 



# lambda functions

def get_date_to_compute(df):
    if pd.isna(df) == False:
        year = int(df.year)
        month = int(df.month)
        return datetime(year,month,7)



def calculate_R_S(row,value,frame,org_list):
        if row[value].replace('.','').isdigit() == True:
            if frame['R<='][org_list.index(value)] != '':
                if float(row[value]) <= float(frame['R<='][org_list.index(value)]):
                    row[value] = 'R'        
                    return row
                elif float(row[value]) >= float(frame['S>='][org_list.index(value)]):
                    row[value] = 'S'
                    return row
                else:
                    return row
            else:
                if float(row[value]) <= float(frame['S>='][org_list.index(value)]):
                    row[value] = 'R'
                    return row
                elif float(row[value]) >= float(frame['S>='][org_list.index(value)]):
                    row[value] = 'S'
                    return row
                else:
                    return row
        else:
            return row

                
def check_R(row,value_list):
    for x in value_list:
        if row[x] == 'R':
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row
    
            
                       