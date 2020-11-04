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
sau = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx','Staphylococcus species')
ent = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx','Enterococcus species')
sal_shi = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','sal_shi')
ent_vic = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','ent_vic')

# sal_shi_list = sal_shi['ORG'].values.tolist()
# ent_vic_list = ent_vic['ORG'].values.tolist()
# other_ent_list = ['efa','efm','ngo','hin','spn','nme','bca']

ent_list_q = ['efa','efm']


enterobact_all_list = enterobact_all['WHON5_CODE'].values.tolist()
pae_list = pae['WHON5_CODE'].values.tolist()
aba_list = aba['WHON5_CODE'].values.tolist()
sau_list = sau['WHON5_CODE'].values.tolist()
ent_list = ent['WHON5_CODE'].values.tolist()

enterobact_all_list_mic = enterobact_all['WHON5_CODE_MIC'].values.tolist()
pae_list_mic = pae['WHON5_CODE_MIC'].values.tolist()
aba_list_mic = aba['WHON5_CODE_MIC'].values.tolist()
sau_list_mic = sau['WHON5_CODE_MIC'].values.tolist()
ent_list_mic = ent['WHON5_CODE_MIC'].values.tolist()

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
        df_enterobact_col = df_enterobact_all
        df_enterobact_all = df_enterobact_all[df_enterobact_all['ent_fast'].dt.days >= 0]
    
    df_enterobact_all_referred = df[df['ORGANISM'].isin(['eco','kpn'])]
    if len(df_enterobact_all_referred) > 0:
        df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['X_REFERRED'] == 1]
        df_enterobact_col_referred = df_enterobact_all_referred
        # df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['ent_fast'].dt.days >= 0]
    
    df_pae = df[df['ORGANISM'].isin(['pae'])]
    if len(df_pae) > 0:
        df_pae = df_pae[df_pae['X_REFERRED'] != 1]
        df_pae_col = df_pae
        df_pae = df_pae[df_pae['ent_fast'].dt.days >= 0]
    
    df_pae_referred = df[df['ORGANISM'].isin(['pae'])]
    if len(df_pae_referred) > 0:
        df_pae_referred = df_pae_referred[df_pae_referred['X_REFERRED'] == 1]
        df_pae_col_referred = df_pae_referred
        # df_pae_referred = df_pae_referred[df_pae_referred['ent_fast'].dt.days >= 0]
    
    
    df_aba = df[df['ORGANISM'].isin(['aba'])]
    if len(df_aba) > 0:
        df_aba = df_aba[df_aba['X_REFERRED'] != 1]
        df_aba_col = df_aba
        df_aba = df_aba[df_aba['ent_fast'].dt.days >= 0]
    
    
    df_aba_referred = df[df['ORGANISM'].isin(['aba'])]
    if len(df_aba_referred) > 0:
        df_aba_referred = df_aba_referred[df_aba_referred['X_REFERRED'] == 1]
        df_aba_col_referred = df_aba_referred
        # df_aba_referred = df_aba_referred[df_aba_referred['ent_fast'].dt.days >= 0]
        
    
    df_sau = df[df['ORGANISM'].isin(['sau'])]
    if len(df_sau) > 0:
        df_sau = df_sau[df_sau['X_REFERRED'] != 1]
        df_sau_ir = df_sau
        df_sau = df_sau[df_sau['ent_fast'].dt.days >= 0]
    
    
    df_sau_referred = df[df['ORGANISM'].isin(['sau'])]
    if len(df_sau_referred) > 0:
        df_sau_referred = df_sau_referred[df_sau_referred['X_REFERRED'] == 1]
        df_sau_ir_referred = df_sau_referred
        # df_sau_referred = df_sau_referred[df_sau_referred['ent_fast'].dt.days >= 0]
        
          
    df_ent = df[df['ORGANISM'].isin(ent_list_q)]
    if len(df_ent) > 0:
        df_ent = df_ent[df_ent['X_REFERRED'] != 1]
        df_ent_ir = df_ent
        df_ent = df_ent[df_ent['ent_fast'].dt.days >= 0]
    
    df_ent_referred = df[df['ORGANISM'].isin(ent_list_q)]
    if len(df_ent_referred) > 0:
        df_ent_referred = df_ent_referred[df_ent_referred['X_REFERRED'] != 1]
        df_ent_referred_ir = df_ent_referred
        # df_ent_referred = df_ent_referred[df_ent_referred['ent_fast'].dt.days >= 0]
    
    for value in enterobact_all_list:
        df_enterobact_all = df_enterobact_all.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_col_referred = df_enterobact_col_referred.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_col = df_enterobact_col.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
    
    for value in enterobact_all_list_mic:
        df_enterobact_all = df_enterobact_all.apply(lambda row: calculate_R_S_MIC(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: calculate_R_S_MIC(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        df_enterobact_col_referred = df_enterobact_col_referred.apply(lambda row: calculate_R_S_MIC(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        df_enterobact_col = df_enterobact_col.apply(lambda row: calculate_R_S_MIC(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        
    for value in pae_list:
        df_pae = df_pae.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_col = df_pae_col.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_referred = df_pae_referred.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_col_referred = df_pae_col_referred.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
    
    for value in pae_list_mic:
        df_pae = df_pae.apply(lambda row: calculate_R_S_MIC(row,value,pae,pae_list_mic), axis = 1)
        df_pae_col = df_pae_col.apply(lambda row: calculate_R_S_MIC(row,value,pae,pae_list_mic), axis = 1)
        df_pae_referred = df_pae_referred.apply(lambda row: calculate_R_S_MIC(row,value,pae,pae_list_mic), axis = 1)
        df_pae_col_referred = df_pae_col_referred.apply(lambda row: calculate_R_S_MIC(row,value,pae,pae_list_mic), axis = 1)
    
    for value in aba_list:
        df_aba = df_aba.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_referred = df_aba_referred.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_col = df_aba_col.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_col_referred = df_aba_col_referred.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        
    for value in aba_list_mic:
        df_aba = df_aba.apply(lambda row: calculate_R_S_MIC(row,value,aba,aba_list_mic), axis = 1)
        df_aba_referred = df_aba_referred.apply(lambda row: calculate_R_S_MIC(row,value,aba,aba_list_mic), axis = 1)
        df_aba_col = df_aba_col.apply(lambda row: calculate_R_S_MIC(row,value,aba,aba_list_mic), axis = 1)
        df_aba_col_referred = df_aba_col_referred.apply(lambda row: calculate_R_S_MIC(row,value,aba,aba_list_mic), axis = 1)
    
    for value in sau_list:
        df_sau = df_sau.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
        df_sau_referred = df_sau_referred.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
        df_sau_ir = df_sau.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
        df_sau_ir_referred = df_sau_referred.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
    
    for value in sau_list_mic:
        df_sau = df_sau.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
        df_sau_referred = df_sau_referred.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
        df_sau_ir = df_sau.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
        df_sau_ir_referred = df_sau_referred.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
    
    for value in ent_list:
        df_ent = df_ent.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
        df_ent_referred = df_ent_referred.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
        df_ent_ir = df_ent.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
        df_ent_referred_ir = df_ent_referred_ir.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
    
    for value in ent_list_mic:
        df_ent = df_ent.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
        df_ent_referred = df_ent_referred.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
        df_ent_ir = df_ent.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
        df_ent_referred_ir = df_ent_referred_ir.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
    
    enterobact_list = ['CAZ_ND30','CTX_ND30','CRO_ND30','FEP_ND30','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','CAZ_NM','CTX_NM','CRO_NM','FEP_NM','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
    if len(df_enterobact_all) > 0:
        # df_enterobact_all_concat = df_enterobact_all.apply(lambda row: check_R_entero(row,enterobact_all_list), axis = 1)
        df_enterobact_all = df_enterobact_all.apply(lambda row: check_R_entero(row,enterobact_list), axis = 1)
        # frames = [df_enterobact_all_concat,df_enterobact_all]
        # df_enterobact_all= pd.concat(frames)
        df_enterobact_all = df_enterobact_all[df_enterobact_all['Test'] == 'R']
        df_enterobact_col = df_enterobact_col[(df_enterobact_col['COL_NM'] == 'I')  | (df_enterobact_col['COL_NM'] == 'R')]
        frames = [df_enterobact_all,df_enterobact_col]
        df_enterobact_all= pd.concat(frames)
        df_enterobact_all.dropna(how = 'all',inplace = True)
        df_enterobact_all = df_enterobact_all.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_enterobact_all = df_enterobact_all.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_enterobact_all['SPEC_DATE'] = df_enterobact_all['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_enterobact_all = df_enterobact_all[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','ESBL','CAZ_ND30','CTX_ND30','CRO_ND30','FEP_ND30','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','CAZ_NM','CTX_NM','CRO_NM','FEP_NM','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']]
    
    if len(df_enterobact_all_referred) > 0:
        # df_enterobact_all_referred_concat = df_enterobact_all_referred.apply(lambda row: check_R(row,enterobact_all_list_mic), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: check_R_entero(row,enterobact_list), axis = 1)
        # frames = [df_enterobact_all_referred,df_enterobact_all_referred_concat]
        df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['Test'] == 'R']
        df_enterobact_col_referred = df_enterobact_col_referred[(df_enterobact_col_referred['COL_NM'] == 'I')  | (df_enterobact_col_referred['COL_NM'] == 'R')]
        frames = [df_enterobact_all_referred,df_enterobact_col_referred]
        df_enterobact_all_referred = pd.concat(frames)
        df_enterobact_all_referred.dropna(how = 'all',inplace = True)
        df_enterobact_all_referred = df_enterobact_all_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_enterobact_all_referred = df_enterobact_all_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_enterobact_all_referred['SPEC_DATE'] = df_enterobact_all_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_enterobact_all_referred = df_enterobact_all_referred[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','ESBL','CAZ_ND30','CTX_ND30','CRO_ND30','FEP_ND30','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','CAZ_NM','CTX_NM','CRO_NM','FEP_NM','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']]
    
    pae_list_all = ['IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
    if len(df_pae) > 0:
        # df_pae_concat = df_pae.apply(lambda row: check_R(row,pae_list_mic), axis = 1)
        df_pae['CARBAPENEM'] = df_pae['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        df_pae_col['CARBAPENEM'] = df_pae_col['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        df_pae = df_pae.apply(lambda row: check_R_nfo(row,pae_list_all), axis = 1)
        # frames = [df_pae,df_pae_concat]
        # df_pae = pd.concat(frames)
        df_pae = df_pae[df_pae['Test'] == 'R']
        df_pae_col = df_pae_col[(df_pae_col['COL_NM'] == 'I')  | (df_pae_col['COL_NM'] == 'R')]
        frames = [df_pae,df_pae_col]
        df_pae = pd.concat(frames)
        df_pae.dropna(how = 'all',inplace = True)
        df_pae = df_pae.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_pae = df_pae.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_pae['SPEC_DATE'] = df_pae['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_pae = df_pae[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']]
    
    if len(df_pae_referred) > 0:
        df_pae_referred['CARBAPENEM'] = df_pae_referred['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        df_pae_col_referred['CARBAPENEM'] = df_pae_col_referred['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        # df_pae_referred_concat = df_pae_referred.apply(lambda row: check_R(row,pae_list_mic), axis = 1)
        df_pae_referred = df_pae_referred.apply(lambda row: check_R_nfo(row,pae_list_all), axis = 1)
        # frames = [df_pae_referred,df_pae_referred_concat]
        # df_pae_referred = pd.concat(frames)
        df_pae_referred = df_pae_referred[df_pae_referred['Test'] == 'R']
        df_pae_col_referred = df_pae_col_referred[(df_pae_col_referred['COL_NM'] == 'I')  | (df_pae_col_referred['COL_NM'] == 'R')]
        frames = [df_pae_referred,df_pae_col_referred]
        df_pae_referred = pd.concat(frames)
        df_pae_referred.dropna(how = 'all',inplace = True)
        df_pae_referred = df_pae_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_pae_referred = df_pae_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_pae_referred['SPEC_DATE'] = df_pae_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_pae_referred = df_pae_referred[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']]
    
    aba_list_all = ['IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
    if len(df_aba) > 0:
        df_aba['CARBAPENEM'] = df_aba['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        df_aba_col['CARBAPENEM'] = df_aba_col['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        # df_aba_concat = df_aba.apply(lambda row: check_R(row,aba_list_mic), axis = 1)
        df_aba = df_aba.apply(lambda row: check_R_nfo(row,aba_list_all), axis = 1)
       
        df_aba = df_aba[df_aba['Test'] == 'R']
        df_aba_col = df_aba_col[(df_aba_col['COL_NM'] == 'I')  | (df_aba_col['COL_NM'] == 'R')]
        frames = [df_aba,df_aba_col]
        df_aba = pd.concat(frames)
        df_aba.dropna(how = 'all',inplace = True)
        df_aba = df_aba.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_aba = df_aba.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_aba['SPEC_DATE'] = df_aba['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_aba = df_aba[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']]
    
    
    if len(df_aba_referred) > 0:
        # df_aba_referred_concat = df_aba_referred.apply(lambda row: check_R(row,aba_list_mic), axis = 1)
        df_aba_referred['CARBAPENEM'] = df_aba_referred['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        df_aba_col_referred['CARBAPENEM'] = df_aba_col_referred['CARBAPENEM'].replace({"1": "+", "0" : "-"}, inplace=True)
        df_aba_referred = df_aba_referred.apply(lambda row: check_R_nfo(row,aba_list_all), axis = 1)
        
        df_aba_referred = df_aba_referred[df_aba_referred['Test'] == 'R']
        df_aba_col_referred = df_aba_col_referred[(df_aba_col_referred['COL_NM'] == 'I')  | (df_aba_col_referred['COL_NM'] == 'R')]
        frames = [df_aba_referred,df_aba_col_referred]
        df_aba_referred = pd.concat(frames)
        df_aba_referred.dropna(how = 'all',inplace = True)
        df_aba_referred = df_aba_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_aba_referred = df_aba_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_aba_referred['SPEC_DATE'] = df_aba_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_aba_referred = df_aba_referred[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']]
        
    # sau_list_all = ['FOX_ND30','FOX_NM','OXA_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM','VAN_NM','ERY_ND15','ERY_NM','CLI_ND2','CLI_NM']
    sau_list_1_7 = ['FOX_ND30','FOX_NM','OXA_NM']
    sau_list_ir = ['LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM','VAN_NM','ERY_ND15','ERY_NM','CLI_ND2','CLI_NM']
    if len(df_sau) > 0:
        # df_sau_concat = df_sau.apply(lambda row: check_R(row,sau_list_all), axis = 1)
        df_sau = df_sau.apply(lambda row: check_R_sau_1_7(row,sau_list_1_7), axis = 1)
        df_sau_ir = df_sau_ir.apply(lambda row: check_R_sau_ir(row,sau_list_ir), axis = 1)
        df_sau = df_sau[df_sau['Test'] == 'R']
        df_sau_ir = df_sau_ir[df_sau_ir['Test'] == 'R']
        frames = [df_sau,df_sau_ir]
        df_sau = pd.concat(frames)
        df_sau.dropna(how = 'all',inplace = True)
        df_sau = df_sau.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_sau = df_sau.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_sau['SPEC_DATE'] = df_sau['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_sau = df_sau[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','INDUC_CLI','MRSA','FOX_ND30','FOX_NM','OXA_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM','VAN_NM','ERY_ND15','ERY_NM','CLI_ND2','CLI_NM']]
    
    if len(df_sau_referred) > 0:
        # df_sau_referred_concat = df_sau_referred.apply(lambda row: check_R(row,sau_list_mic), axis = 1)
        df_sau_referred = df_sau_referred.apply(lambda row: check_R_sau_1_7(row,sau_list), axis = 1)
        df_sau_ir_referred = df_sau_ir_referred.apply(lambda row: check_R_sau_ir(row,sau_list), axis = 1)
        df_sau_referred = df_sau_referred[df_sau_referred['Test'] == 'R']
        df_sau_ir_referred = df_sau_ir_referred[df_sau_ir_referred['Test'] == 'R']
        frames = [df_sau_referred,df_sau_ir_referred]
        df_sau_referred = pd.concat(frames)
        df_sau_referred.dropna(how = 'all',inplace = True)
        df_sau_referred = df_sau_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_sau_referred = df_sau_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_sau_referred['SPEC_DATE'] = df_sau_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_sau_referred = df_sau_referred[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','INDUC_CLI','MRSA','FOX_ND30','FOX_NM','OXA_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM','VAN_NM','ERY_ND15','ERY_NM','CLI_ND2','CLI_NM']]
        
        
    ent_list_1_7 = ['GEH_ND120','GEH_NM','STH_ND300','STH_NM']
    ent_list_ir = ['VAN_ND30','VAN_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM']
    if len(df_ent) > 0:
        # df_ent_concat = df_ent.apply(lambda row: check_R(row,ent_list_mic), axis = 1)
        df_ent = df_ent.apply(lambda row: check_R(row,ent_list_1_7), axis = 1)
        df_ent_ir = df_ent_ir.apply(lambda row: check_R(row,ent_list_ir), axis = 1)
        frames = [df_ent,df_ent_ir]
        df_ent = pd.concat(frames)
        df_ent = df_ent[df_ent['Test'] == 'R']
        df_ent.dropna(how = 'all',inplace = True)
        df_ent = df_ent.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_ent = df_ent.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_ent['SPEC_DATE'] = df_ent['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_ent = df_ent[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','GEH_ND120','GEH_NM','STH_ND300','STH_NM','VAN_ND30','VAN_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM']]
    
    if len(df_ent_referred) > 0:
        # df_ent_referred_concat = df_ent_referred.apply(lambda row: check_R(row,ent_list_mic), axis = 1)
        df_ent_referred = df_ent_referred.apply(lambda row: check_R(row,ent_list_1_7), axis = 1)
        df_ent_referred_ir = df_ent_referred_ir.apply(lambda row: check_R(row,ent_list_ir), axis = 1)
        frames = [df_ent_referred,df_ent_referred_ir]
        df_ent_referred = pd.concat(frames)
        df_ent_referred = df_ent_referred[df_ent_referred['Test'] == 'R']
        df_ent_referred.dropna(how = 'all',inplace = True)
        df_ent_referred = df_ent_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_ent_referred = df_ent_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_ent_referred['SPEC_DATE'] = df_ent_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_ent = df_ent[['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','GEH_ND120','GEH_NM','STH_ND300','STH_NM','VAN_ND30','VAN_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM']]
    
    
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
    
    if len(df_sau) > 0:
        df_sau.to_excel(writer, sheet_name='sau', index=False)
    
    if len(df_sau_referred) > 0:
        df_sau_referred.to_excel(writer, sheet_name='sau_referred', index=False)
    
    if len(df_ent) > 0:
        df_ent.to_excel(writer,sheet_name='ent',index=False)
        
    if len(df_ent_referred) > 0:
        df_ent_referred.to_excel(writer,sheet_name='ent_referred',index=False)
    
    writer.save()
    
    return writer 



# lambda functions
#
def get_date_to_compute(df):
    if pd.isna(df) == False:
        year = int(df.year)
        month = int(df.month)
        return datetime(year,month,7)



def calculate_R_S(row,value,frame,org_list):
        row[value] = row[value].replace('>=','')
        row[value] = row[value].replace('<=','')
        row[value] = row[value].replace('>','')
        row[value] = row[value].replace('<','')
        if row[value].replace('.','').isdigit() == True:
            if frame['R<='][org_list.index(value)] != '':
                if float(row[value]) <= float(frame['R<='][org_list.index(value)]):
                    row[value] = 'R'        
                    return row
                elif float(row[value]) >= float(frame['S>='][org_list.index(value)]):
                    row[value] = 'S'
                    return row
                elif (float(row[value]) < float(frame['S>='][org_list.index(value)])) and (float(row[value]) > float(frame['R<='][org_list.index(value)])):
                    row[value] = 'I'
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
                elif (float(row[value]) > float(frame['S>='][org_list.index(value)])) and (float(row[value]) < float(frame['R<='][org_list.index(value)])):
                    row[value] = 'I'
                    return row
                else:
                    return row
        else:
            return row


def calculate_R_S_MIC(row,value,frame,org_list):
    row[value] = row[value].replace('>=','')
    row[value] = row[value].replace('<=','')
    row[value] = row[value].replace('>','')
    row[value] = row[value].replace('<','')
    if row[value].replace('.','').isdigit() == True:
            if frame['R>='][org_list.index(value)] != '':
                if float(row[value]) >= float(frame['R>='][org_list.index(value)]):
                    row[value] = 'R'        
                    return row
                elif float(row[value]) <= float(frame['S<='][org_list.index(value)]):
                    row[value] = 'S'
                    return row
                elif float(row[value]) < float(frame['R>='][org_list.index(value)]) and float(row[value]) > float(frame['S<='][org_list.index(value)]):
                    row[value] = 'I'
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

def check_R_entero(row,value_list):
    for x in value_list:
        if row[x] == 'R' or row['ESBL'] == '+':
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row

def check_R_nfo(row,value_list):
    for x in value_list:
        if row[x] == 'R' or row['CARBAPENEM'] == 1 or row['CARBAPENEM'] == '+':
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row
    
def check_R_sau_1_7(row,value_list):
     for x in value_list:
         if row[x] == 'R' or row['MRSA'] == '+' or row['INDUC_CLI'] == 1:
             row['Test'] = 'R'
             return row
         else:
             row['Test'] = 'S'
             return row
         
def check_R_sau_ir(row,value_list):
    for x in value_list:
        if row[x] == 'R' or row['INDUC_CLI'] == 1 or ((row['ERY_ND15'] == 'R' or row['ERY_NM'] == 'R') and (row['CLI_ND2'] == 'R' or row['CLI_NM'] == 'R')):
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row
    
            
                       