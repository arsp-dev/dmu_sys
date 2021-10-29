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
bsn = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred.xlsx','Beta-Hemolytic Streptococci')
sal_shi = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','sal_shi')
ent_vic = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','ent_vic')
bsn_ant = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','bsn')

enterics = pd.read_excel(dirpath + '/whonet/static/whonet_xl/org_list_ent.xlsx')
fastidious = pd.read_excel(dirpath + '/whonet/static/whonet_xl/org_list_fast.xlsx')


ent_list_review = enterics['ORG'].values.tolist()
fast_list_review = fastidious['ORG'].values.tolist()
bsn_list_review = bsn_ant['ORG'].values.tolist()
# sal_shi_list = sal_shi['ORG'].values.tolist()
# ent_vic_list = ent_vic['ORG'].values.tolist()
# other_ent_list = ['efa','efm','ngo','hin','spn','nme','bca']

ent_list_q = ['efa','efm']


enterobact_all_list = enterobact_all['WHON5_CODE'].values.tolist()
pae_list = pae['WHON5_CODE'].values.tolist()
aba_list = aba['WHON5_CODE'].values.tolist()
sau_list = sau['WHON5_CODE'].values.tolist()
ent_list = ent['WHON5_CODE'].values.tolist()
bsn_list = bsn['WHON5_CODE'].values.tolist()

enterobact_all_list_mic = enterobact_all['WHON5_CODE_MIC'].values.tolist()
pae_list_mic = pae['WHON5_CODE_MIC'].values.tolist()
aba_list_mic = aba['WHON5_CODE_MIC'].values.tolist()
sau_list_mic = sau['WHON5_CODE_MIC'].values.tolist()
ent_list_mic = ent['WHON5_CODE_MIC'].values.tolist()
bsn_list_mic = bsn['WHON5_CODE_MIC'].values.tolist()

def summary_report_referred(file_id,file_name,config = 'raw'):
    df = concat_all_df(file_id,config)
    df.columns = map(str.upper, df.columns)
    
    df_ent_list_review = df[df['ORGANISM'].isin(ent_list_review)]
    df_fast_list_review = df[df['ORGANISM'].isin(fast_list_review)]
    
    df['SPEC_DATE'] = pd.to_datetime(df['SPEC_DATE'],errors='ignore')
    df['comp'] = df['SPEC_DATE'].apply(lambda df: get_date_to_compute(df) )
    df['ent_fast'] = df['comp'] - df['SPEC_DATE']
    # df['X_REFERRED'] = df['X_REFERRED'].astype(str)
    df['X_REFERRED'] = df['X_REFERRED'].str.replace('.0', '', regex=False)
    # df['X_REFERRED'] = pd.to_numeric(df['X_REFERRED'], downcast='signed',errors='ignore')
    df_referred = df[df['X_REFERRED'] == '1']
    # df = df[df['X_REFERRED'] != '1']    
        
    
    
    df_enterobact_all = df[df['ORGANISM'].isin(['eco','kpn'])]
    df_enterobact_col = df_enterobact_all[df_enterobact_all['X_REFERRED'] != '1']
    if len(df_enterobact_all) > 0:
        df_enterobact_all = df_enterobact_all[df_enterobact_all['X_REFERRED'] != '1']
        # df_enterobact_col = df_enterobact_all
        # df_enterobact_all = df_enterobact_all[df_enterobact_all['ent_fast'].dt.days >= 0]
    
    df_enterobact_all_referred = df_referred[df_referred['ORGANISM'].isin(['eco','kpn'])]
    df_enterobact_col_referred = df_enterobact_all_referred[df_enterobact_all_referred['X_REFERRED'] == '1']
    if len(df_enterobact_all_referred) > 0:
        df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['X_REFERRED'] == '1']
        # df_enterobact_col_referred = df_enterobact_all_referred
        # df_enterobact_all_referred = df_enterobact_all_referred[df_enterobact_all_referred['ent_fast'].dt.days >= 0]
    
    df_pae = df[df['ORGANISM'].isin(['pae'])]
    df_pae_col = df_pae[df_pae['X_REFERRED'] != '1']
    if len(df_pae) > 0:
        df_pae = df_pae[df_pae['X_REFERRED'] != '1']
        # df_pae_col = df_pae
        df_pae = df_pae[df_pae['ent_fast'].dt.days >= 0]
    
    df_pae_referred = df_referred[df_referred['ORGANISM'].isin(['pae'])]
    df_pae_col_referred = df_pae_referred[df_pae_referred['X_REFERRED'] == '1']
    if len(df_pae_referred) > 0:
        df_pae_referred = df_pae_referred[df_pae_referred['X_REFERRED'] == '1']
        # df_pae_col_referred = df_pae_referred
        # df_pae_referred = df_pae_referred[df_pae_referred['ent_fast'].dt.days >= 0]
    
    
    df_aba = df[df['ORGANISM'].isin(['aba'])]
    
    df_aba_col =  df_aba[df_aba['X_REFERRED'] != '1']
    if len(df_aba) > 0:
        df_aba = df_aba[df_aba['X_REFERRED'] != '1']
        # df_aba_col = df_aba
        df_aba = df_aba[df_aba['ent_fast'].dt.days >= 0]
    
    
    df_aba_referred = df_referred[df_referred['ORGANISM'].isin(['aba'])]
    df_aba_col_referred = df_aba_referred[df_aba_referred['X_REFERRED'] == '1']
    if len(df_aba_referred) > 0:
        df_aba_referred = df_aba_referred[df_aba_referred['X_REFERRED'] == '1']
        # df_aba_col_referred = df_aba_referred
        # df_aba_referred = df_aba_referred[df_aba_referred['ent_fast'].dt.days >= 0]
        
    
    df_sau = df[df['ORGANISM'].isin(['sau'])]
    df_sau_ir = df_sau[df_sau['X_REFERRED'] != '1']
    if len(df_sau) > 0:
        df_sau = df_sau[df_sau['X_REFERRED'] != '1']
        # df_sau_ir = df_sau
        df_sau = df_sau[df_sau['ent_fast'].dt.days >= 0]
    
    
    df_sau_referred = df_referred[df_referred['ORGANISM'].isin(['sau'])]
    df_sau_ir_referred = df_sau_referred[df_sau_referred['X_REFERRED'] == '1']
    if len(df_sau_referred) > 0:
        df_sau_referred = df_sau_referred[df_sau_referred['X_REFERRED'] == '1']
        # df_sau_ir_referred = df_sau_referred
        # df_sau_referred = df_sau_referred[df_sau_referred['ent_fast'].dt.days >= 0]
        
          
    df_ent = df[df['ORGANISM'].isin(ent_list_q)]
    df_ent_ir = df_ent[df_ent['X_REFERRED'] != '1']
    if len(df_ent) > 0:
        df_ent = df_ent[df_ent['X_REFERRED'] != '1']
        # df_ent_ir = df_ent
        df_ent = df_ent[df_ent['ent_fast'].dt.days >= 0]
    
    df_bsn = df[df['ORGANISM'].isin(bsn_list_review)]
    if len(df_bsn) > 0:
        df_bsn = df_bsn[df_bsn['X_REFERRED'] != 1]
    
    df_bsn_reffered = df_referred[df_referred['ORGANISM'].isin(bsn_list_review)]
    if len(df_bsn_reffered) > 0:
        df_bsn_reffered = df_bsn_reffered[df_bsn_reffered['X_REFERRED'] == 1]
    
    
    
    
    df_ent_referred = df_referred[df_referred['ORGANISM'].isin(ent_list_q)]
    df_ent_referred_ir = df_ent_referred[df_ent_referred['X_REFERRED'] == '1']
    if len(df_ent_referred) > 0:
        df_ent_referred = df_ent_referred[df_ent_referred['X_REFERRED'] == '1']
        # df_ent_referred_ir = df_ent_referred
        # df_ent_referred = df_ent_referred[df_ent_referred['ent_fast'].dt.days >= 0]
    for value in bsn_list_mic:
        df_bsn = df_bsn.apply(lambda row: calculate_R_S_MIC(row,value,bsn,bsn_list_mic), axis = 1)
        df_bsn_reffered = df_bsn_reffered.apply(lambda row: calculate_R_S_MIC(row,value,bsn,bsn_list_mic), axis = 1)
    
    for value in bsn_list:
        df_bsn = df_bsn.apply(lambda row: calculate_R_S(row,value,bsn,bsn_list), axis = 1)
        df_bsn_reffered = df_bsn_reffered.apply(lambda row: calculate_R_S(row,value,bsn,bsn_list), axis = 1)
    
    
    for value in enterobact_all_list_mic:
        df_enterobact_all = df_enterobact_all.apply(lambda row: calculate_R_S_MIC(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: calculate_R_S_MIC(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        df_enterobact_col_referred = df_enterobact_col_referred.apply(lambda row: calculate_R_S_MIC_COL(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        df_enterobact_col = df_enterobact_col.apply(lambda row: calculate_R_S_MIC_COL(row,value,enterobact_all,enterobact_all_list_mic), axis = 1)
        
    for value in enterobact_all_list:
        df_enterobact_all = df_enterobact_all.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_all_referred = df_enterobact_all_referred.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_col_referred = df_enterobact_col_referred.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
        df_enterobact_col = df_enterobact_col.apply(lambda row: calculate_R_S(row,value,enterobact_all,enterobact_all_list), axis = 1)
   
    for value in pae_list_mic:
        df_pae = df_pae.apply(lambda row: calculate_R_S_MIC(row,value,pae,pae_list_mic), axis = 1)
        df_pae_col = df_pae_col.apply(lambda row: calculate_R_S_MIC_COL(row,value,pae,pae_list_mic), axis = 1)
        df_pae_referred = df_pae_referred.apply(lambda row: calculate_R_S_MIC(row,value,pae,pae_list_mic), axis = 1)
        df_pae_col_referred = df_pae_col_referred.apply(lambda row: calculate_R_S_MIC_COL(row,value,pae,pae_list_mic), axis = 1)
  
  
    for value in pae_list:
        df_pae = df_pae.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_col = df_pae_col.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_referred = df_pae_referred.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
        df_pae_col_referred = df_pae_col_referred.apply(lambda row: calculate_R_S(row,value,pae,pae_list), axis = 1)
   
    for value in aba_list_mic:
        df_aba = df_aba.apply(lambda row: calculate_R_S_MIC(row,value,aba,aba_list_mic), axis = 1)
        df_aba_referred = df_aba_referred.apply(lambda row: calculate_R_S_MIC(row,value,aba,aba_list_mic), axis = 1)
        df_aba_col = df_aba_col.apply(lambda row: calculate_R_S_MIC_COL(row,value,aba,aba_list_mic), axis = 1)
        df_aba_col_referred = df_aba_col_referred.apply(lambda row: calculate_R_S_MIC_COL(row,value,aba,aba_list_mic), axis = 1)
   
    
    for value in aba_list:
        df_aba = df_aba.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_referred = df_aba_referred.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_col = df_aba_col.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        df_aba_col_referred = df_aba_col_referred.apply(lambda row: calculate_R_S(row,value,aba,aba_list), axis = 1)
        
    for value in sau_list_mic:
        df_sau = df_sau.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
        df_sau_referred = df_sau_referred.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
        df_sau_ir = df_sau.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
        df_sau_ir_referred = df_sau_referred.apply(lambda row: calculate_R_S_MIC(row,value,sau,sau_list_mic), axis = 1)
    
    for value in sau_list:
        df_sau = df_sau.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
        df_sau_referred = df_sau_referred.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
        df_sau_ir = df_sau.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
        df_sau_ir_referred = df_sau_referred.apply(lambda row: calculate_R_S(row,value,sau,sau_list), axis = 1)
    
    for value in ent_list_mic:
        df_ent = df_ent.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
        df_ent_referred = df_ent_referred.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
        df_ent_ir = df_ent.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
        df_ent_referred_ir = df_ent_referred_ir.apply(lambda row: calculate_R_S_MIC(row,value,ent,ent_list_mic), axis = 1)
    
    for value in ent_list:
        df_ent = df_ent.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
        df_ent_referred = df_ent_referred.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
        df_ent_ir = df_ent.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
        df_ent_referred_ir = df_ent_referred_ir.apply(lambda row: calculate_R_S(row,value,ent,ent_list), axis = 1)
    
    bsn_ant_list = ['AMP_ND10','AMP_NM','PEN_ND10','PEN_NM','VAN_ND30','VAN_NM','LVX_ND5','LVX_NM','CRO_ND30','CRO_NM','LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM','CLI_ND2','CLI_NM','CHL_ND30','CHL_NM','ERY_ND15','ERY_NM','CTX_ND30','CTX_NM','FEP_ND30','FEP_NM'] 
    if len(df_bsn) > 0:
        df_bsn = df_bsn.apply(lambda row: check_R_bsn(row,bsn_ant_list), axis = 1)
        df_bsn = df_bsn[(df_bsn['Test'] == 'I')  | (df_bsn['Test'] == 'R')]
        df_bsn.dropna(how = 'all',inplace = True)
        df_bsn = df_bsn.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_bsn = df_bsn.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_bsn['SPEC_DATE'] = df_bsn['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        df_bsn, cols = remove_null_cols(df_bsn,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','ESBL','CAZ_ND30','CAZ_NM','CAZ_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS','FEP_ND30','FEP_NM','FEP_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_bsn = df_bsn[cols]
    
    if len(df_bsn_reffered) > 0:
        df_bsn_reffered = df_bsn_reffered.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_bsn_reffered = df_bsn_reffered.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
        df_bsn_reffered['SPEC_DATE'] = df_bsn_reffered['SPEC_DATE'].dt.strftime('%m/%d/%Y')
      
        df_bsn_reffered, cols = remove_null_cols(df_bsn_reffered,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','ESBL','CAZ_ND30','CAZ_NM','CAZ_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS','FEP_ND30','FEP_NM','FEP_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_bsn_reffered = df_bsn_reffered[cols]
    
    enterobact_list = ['CAZ_ND30','CTX_ND30','CRO_ND30','FEP_ND30','IPM_ND10','MEM_ND10','ETP_ND10','CAZ_NM','CTX_NM','CRO_NM','FEP_NM','IPM_NM','MEM_NM','ETP_NM','COL_NM']
    if len(df_enterobact_all) > 0:
        # df_enterobact_all_concat = df_enterobact_all.apply(lambda row: check_R_entero(row,enterobact_all_list), axis = 1)
        df_enterobact_all = df_enterobact_all.apply(lambda row: check_R_entero(row,enterobact_list), axis = 1)
        # frames = [df_enterobact_all_concat,df_enterobact_all]
        # df_enterobact_all= pd.concat(frames)
        df_enterobact_all = df_enterobact_all[df_enterobact_all['Test'] == 'R']
        df_enterobact_col = df_enterobact_col[(df_enterobact_col['COL_NM'] == 'R')]
        frames = [df_enterobact_all,df_enterobact_col]
        df_enterobact_all= pd.concat(frames,sort=False)
        df_enterobact_all.dropna(how = 'all',inplace = True)
        df_enterobact_all = df_enterobact_all.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_enterobact_all = df_enterobact_all.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_enterobact_all['SPEC_DATE'] = df_enterobact_all['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        
     
        df_enterobact_all, cols = remove_null_cols(df_enterobact_all,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','ESBL','CAZ_ND30','CAZ_NM','CAZ_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS','FEP_ND30','FEP_NM','FEP_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_enterobact_all = df_enterobact_all[cols]
    
    if len(df_enterobact_all_referred) > 0:
        df_enterobact_all_referred = df_enterobact_all_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_enterobact_all_referred = df_enterobact_all_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
        df_enterobact_all_referred['SPEC_DATE'] = df_enterobact_all_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
      
        df_enterobact_all_referred, cols = remove_null_cols(df_enterobact_all_referred,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','ESBL','CAZ_ND30','CAZ_NM','CAZ_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS','FEP_ND30','FEP_NM','FEP_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_enterobact_all_referred = df_enterobact_all_referred[cols]
    
    pae_list_all = ['IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
    if len(df_pae) > 0:
        df_pae = df_pae.apply(lambda row: check_R_nfo(row,pae_list_all), axis = 1)
        df_pae = df_pae[df_pae['Test'] == 'R']
        df_pae_col = df_pae_col[(df_pae_col['COL_NM'] == 'R')]
        frames = [df_pae,df_pae_col]
        df_pae = pd.concat(frames,sort=False)
        df_pae.dropna(how = 'all',inplace = True)
        df_pae = df_pae.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_pae = df_pae.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_pae['SPEC_DATE'] = df_pae['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        
        df_pae, cols = remove_null_cols(df_pae,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_pae = df_pae[cols]
    
    if len(df_pae_referred) > 0:
        df_pae_referred = df_pae_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_pae_referred = df_pae_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
        df_pae_referred['SPEC_DATE'] = df_pae_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
       
        df_pae_referred, cols = remove_null_cols(df_pae_referred,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_pae_referred = df_pae_referred[cols]
    
    aba_list_all = ['IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
    if len(df_aba) > 0:
        
     
        df_aba = df_aba.apply(lambda row: check_R_nfo(row,aba_list_all), axis = 1)
       
        # if len(df_aba) > 0:
        df_aba = df_aba[df_aba['Test'] == 'R']
        
        # if len(df_aba_col) > 0:
        # df_aba_col = df_aba_col[(df_aba_col['COL_NM'] == 'I')  | (df_aba_col['COL_NM'] == 'R')]
        df_aba_col = df_aba_col[(df_aba_col['COL_NM'] == 'R')]
        
        # if len(df_aba) > 0 and len(df_aba_col) > 0:
        frames = [df_aba,df_aba_col]
        df_aba = pd.concat(frames,sort=False)
        # elif len(df_aba) > 0 and len(df_aba_col) <= 0:
        # df_aba = df_aba
        # elif len(df_aba) <= 0 and len(df_aba_col) > 0:
        # df_aba = df_aba_col
        
        # if len(df_aba) > 0:
        df_aba.dropna(how = 'all',inplace = True)
        df_aba = df_aba.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_aba = df_aba.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'], errors='ignore')
        df_aba['SPEC_DATE'] = df_aba['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        # df_aba = df_aba.dropna(axis=1,how='all')
        
        df_aba, cols = remove_null_cols(df_aba,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','CARBAPENEM','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','DOR_ND10','DOR_NM','DOR_RIS','COL_NM','COL_RIS'])
        df_aba = df_aba[cols]
        
    
    if len(df_aba_referred) > 0:
        
        if len(df_aba_referred) > 0:
            df_aba_referred.dropna(how = 'all',inplace = True)
            df_aba_referred = df_aba_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
            df_aba_referred = df_aba_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
            df_aba_referred['SPEC_DATE'] = df_aba_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
    sau_list_1_7 = ['FOX_ND30','FOX_NM','OXA_NM']
    sau_list_ir = ['LNZ_ND30','LNZ_NM','DAP_ND30','DAP_NM','VAN_NM','ERY_ND15','ERY_NM','CLI_ND2','CLI_NM']
    if len(df_sau) > 0:
        # df_sau_concat = df_sau.apply(lambda row: check_R(row,sau_list_all), axis = 1)
        df_sau = df_sau.apply(lambda row: check_R_sau_1_7(row,sau_list_1_7), axis = 1)
        df_sau_ir = df_sau_ir.apply(lambda row: check_R_sau_ir(row,sau_list_ir), axis = 1)
        df_sau = df_sau[df_sau['Test'] == 'R']
        df_sau_ir = df_sau_ir[df_sau_ir['Test'] == 'R']
        frames = [df_sau,df_sau_ir]
        df_sau = pd.concat(frames,sort=False)
        df_sau.dropna(how = 'all',inplace = True)
        df_sau = df_sau.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_sau = df_sau.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_sau['SPEC_DATE'] = df_sau['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        # df_sau = df_sau.dropna(axis=1,how='all')
      
        df_sau, cols = remove_null_cols(df_sau,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','INDUC_CLI','MRSA','FOX_ND30','FOX_NM','FOX_RIS','OXA_NM','OXA_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','DAP_ND30','DAP_NM','DAP_RIS','VAN_NM','VAN_RIS','ERY_ND15','ERY_NM','ERY_RIS','CLI_ND2','CLI_NM','CLI_RIS'])
        df_sau = df_sau[cols]
    
    if len(df_sau_referred) > 0:
        df_sau_referred = df_sau_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_sau_referred = df_sau_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
        df_sau_referred['SPEC_DATE'] = df_sau_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
      
     
        df_sau_referred, cols = remove_null_cols(df_sau_referred,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','INDUC_CLI','MRSA','FOX_ND30','FOX_NM','FOX_RIS','OXA_NM','OXA_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','DAP_ND30','DAP_NM','DAP_RIS','VAN_NM','VAN_RIS','ERY_ND15','ERY_NM','ERY_RIS','CLI_ND2','CLI_NM','CLI_RIS'])
        df_sau_referred = df_sau_referred[cols]
       
    ent_list_1_7 = ['STH_RIS','GEH_RIS']
    ent_list_ir = ['VAN_RIS','LNZ_RIS','DAP_RIS']
   
    if len(df_ent) > 0:
       
     
        df_ent = df_ent.apply(lambda row: check_R(row,ent_list_1_7), axis = 1)
        df_ent_ir = df_ent_ir.apply(lambda row: check_R(row,ent_list_ir), axis = 1)
        
        df_ent = df_ent[df_ent['Test'] == 'R']
      
        df_ent_ir = df_ent_ir[(df_ent_ir['Test'] == 'R') | (df_ent_ir['Test'] == 'I')]
        
        frames = [df_ent,df_ent_ir]
        df_ent = pd.concat(frames,sort=False)
        
    
  
        df_ent.dropna(how = 'all',inplace = True)
        df_ent = df_ent.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep='last')
        df_ent = df_ent.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
        df_ent['SPEC_DATE'] = df_ent['SPEC_DATE'].dt.strftime('%m/%d/%Y')
        # df_ent = df_ent.dropna(axis=1,how='all')
        cols = ['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','GEH_ND120','GEH_NM','GEH_RIS','STH_ND300','STH_NM','STH_RIS','VAN_ND30','VAN_NM','VAN_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','DAP_ND30','DAP_NM','DAP_RIS']
        # df_ent, cols = remove_null_cols(df_ent,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','GEH_ND120','GEH_NM','GEH_RIS','STH_ND300','STH_NM','STH_RIS','VAN_ND30','VAN_NM','VAN_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','DAP_ND30','DAP_NM','DAP_RIS'])
        df_ent = df_ent[cols]
   
    
    if len(df_ent_referred) > 0:
        df_ent_referred = df_ent_referred.drop_duplicates(['PATIENT_ID','LAST_NAME','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM'], keep=False)
        df_ent_referred = df_ent_referred.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
        df_ent_referred['SPEC_DATE'] = df_ent_referred['SPEC_DATE'].dt.strftime('%m/%d/%Y')
      
        df_ent_referred, cols = remove_null_cols(df_ent_referred,['PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','GEH_ND120','GEH_NM','GEH_RIS','STH_ND300','STH_NM','STH_RIS','VAN_ND30','VAN_NM','VAN_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','DAP_ND30','DAP_NM','DAP_RIS'])
        df_ent_referred = df_ent_referred[cols]
     
    ent_fast_list = ['LABORATORY','PATIENT_ID','FIRST_NAME','MID_NAME','LAST_NAME','SEX','AGE','DATE_BIRTH','AGE_GRP','PAT_TYPE','DATE_DATA','X_REFERRED','X_RECNUM','DATE_ADMIS','NOSOCOMIAL','DIAGNOSIS','STOCK_NUM','WARD','INSTITUT','DEPARTMENT','WARD_TYPE','SPEC_NUM','SPEC_DATE','SPEC_TYPE','SPEC_CODE','LOCAL_SPEC','ORGANISM','ORG_TYPE']
    if len(df_ent_list_review) > 0:
        df_ent_list_review = df_ent_list_review[ent_fast_list]
    
    if len(df_fast_list_review) > 0:
        df_fast_list_review = df_fast_list_review[ent_fast_list]
        
        
    
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
    
    if len(df_bsn) > 0:
        df_bsn.to_excel(writer,sheet_name='bsn',index=False)
        
    if len(df_bsn_reffered) > 0:
        df_bsn_reffered.to_excel(writer,sheet_name='bsn_reffered',index=False)
    
    if len(df_ent_list_review) > 0:
        df_ent_list_review.to_excel(writer,sheet_name='ENTERICS PATHOGENS', index=False)
        
    if len(df_fast_list_review) > 0:
        df_fast_list_review.to_excel(writer,sheet_name='FASTIDIOUS ORGANISMS', index=False)
    
    writer.save()
    
    return writer 



# lambda functions
#
def get_date_to_compute(df):
    if pd.isna(df) == False:
        year = int(df.year)
        month = int(df.month)
        return datetime(year,month,5)

def remove_null_cols(df,ant_list):
    for x in ant_list:
        if x not in df.columns:
            ant_list.remove(x)
       
    return df,ant_list

def calculate_R_S(row,value,frame,org_list):
        row[value] = row[value].replace('>=','')
        row[value] = row[value].replace('<=','')
        row[value] = row[value].replace('>','')
        row[value] = row[value].replace('<','')
        if value.split('_')[0] + '_RIS' not in frame.columns:
            if row[value].replace('.','').isdigit() == True:
                if frame['R<='][org_list.index(value)] != '':
                    if float(row[value]) <= float(frame['R<='][org_list.index(value)]):
                        row[value.split('_')[0] + '_RIS'] = 'R'        
                        return row
                    elif float(row[value]) >= float(frame['S>='][org_list.index(value)]):
                        row[value.split('_')[0] + '_RIS'] = 'S'
                        return row
                    elif (float(row[value]) < float(frame['S>='][org_list.index(value)])) and (float(row[value]) > float(frame['R<='][org_list.index(value)])):
                        row[value.split('_')[0] + '_RIS'] = 'I'
                        return row
                    else:
                        return row
                else:
                    if float(row[value]) <= float(frame['S>='][org_list.index(value)]):
                        row[value.split('_')[0] + '_RIS'] = 'R'
                        return row
                    elif float(row[value]) >= float(frame['S>='][org_list.index(value)]):
                        row[value.split('_')[0] + '_RIS'] = 'S'
                        return row
                    elif (float(row[value]) > float(frame['S>='][org_list.index(value)])) and (float(row[value]) < float(frame['R<='][org_list.index(value)])):
                        row[value.split('_')[0] + '_RIS'] = 'I'
                        return row
                    else:
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
    row[value.split('_')[0] + '_RIS'] = '' 
    if row[value].replace('.','').isdigit() == True:
            if frame['R>='][org_list.index(value)] != '':
                if float(row[value]) >= float(frame['R>='][org_list.index(value)]):
                    row[value.split('_')[0] + '_RIS'] =  'R' 
                      
                    return row
                elif float(row[value]) <= float(frame['S<='][org_list.index(value)]):
                    row[value.split('_')[0] + '_RIS'] = 'S'
                 
                    return row
                elif float(row[value]) < float(frame['R>='][org_list.index(value)]) and float(row[value]) > float(frame['S<='][org_list.index(value)]):
                    row[value.split('_')[0] + '_RIS'] = 'I'
                
                    return row
                else:
                    return row             
    else:
        return row
    
def calculate_R_S_MIC_COL(row,value,frame,org_list):
    row[value] = row[value].replace('>=','')
    row[value] = row[value].replace('<=','')
    row[value] = row[value].replace('>','')
    row[value] = row[value].replace('<','')
    if row[value].replace('.','').isdigit() == True:
            if frame['R>='][org_list.index(value)] != '':
                if float(row[value]) >= float(frame['R>='][org_list.index(value)]):
                    row[value.split('_')[0] + '_RIS'] = 'R'        
                    return row
                # elif float(row[value]) <= float(frame['S<='][org_list.index(value)]):
                #     row[value] = 'S'
                #     return row
                elif float(row[value]) >= 2 and float(row[value]) < 4:
                    row[value.split('_')[0] + '_RIS'] = 'I'
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
        
def check_R_bsn(row,value_list):
    for x in value_list:
        if row[x] == 'R' or (row['INDUC_CLI'] == 1 or (row['ERY_RIS'] == 'R' and row['CLI_RIS'] == 'S')):
            row['Test'] = 'R'
            return row
        elif row[x] == 'I':
            row['Test'] = 'I'
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
aba_list_all = ['IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
pae_list_all = ['IPM_ND10','MEM_ND10','ETP_ND10','DOR_ND10','IPM_NM','MEM_NM','ETP_NM','DOR_NM','COL_NM']
def check_R_nfo(row,value_list):
    row['Test'] = ''
    for x in value_list:
        if row['IPM_RIS'] == 'R' \
        or row['MEM_RIS'] == 'R'  \
        or row['ETP_RIS'] == 'R':
        # or row['DOR_RIS'] == 'R'  \
        # or row['CARBAPENEM'] == 1 \
        # or row['CARBAPENEM'] == '+':
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row
    
def check_R_sau_1_7(row,value_list):
     for x in value_list:
        #  if row[x] == 'R' or row['MRSA'] == '+' or row['INDUC_CLI'] == 1:
         if row[x] == 'R' or row['INDUC_CLI'] == 1:
             row['Test'] = 'R'
             return row
         else:
             row['Test'] = 'S'
             return row
         
def check_R_sau_ir(row,value_list):
    for x in value_list:
        if row[x] == 'R' or row['INDUC_CLI'] == 1 or ((row['ERY_ND15'] == 'R' or row['ERY_NM'] == 'R') and (row['CLI_ND2'] == 'S' or row['CLI_NM'] == 'S')):
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row
    
            
                       