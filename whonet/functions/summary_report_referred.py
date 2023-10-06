from whonet.models import *
import pandas as pd
from datetime import datetime
import os
from whonet.functions.df_helper import concat_all_df
from whonet.referred_classes.e_coli import EColi
from whonet.referred_classes.kpn import Kpn
from whonet.referred_classes.aba import Aba
from whonet.referred_classes.pae import Pae
from whonet.referred_classes.efa_efm import EfaEfm
from whonet.referred_classes.sau import Sau
from whonet.referred_classes.sal_shi import SalShi
from whonet.referred_classes.vic_eco import Vic157
from whonet.referred_classes.hin_hpi import HinHpi
from whonet.referred_classes.ngo import Ngo
from whonet.referred_classes.nme import Nme
from whonet.referred_classes.spn import Spn
from whonet.referred_classes.str import Str

dirpath = os.getcwd()
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
    df['X_REFERRED'] = df['X_REFERRED'].str.replace('.0', '', regex=False)

    df = df[ df['SPEC_TYPE'].str.lower() != 'qc' ]
    df = df[ df['SPEC_TYPE'].str.lower() != 'en' ]
    df = df[ df['SPEC_TYPE'].str.lower() != 'wa' ]
    df = df[ df['SPEC_TYPE'].str.lower() != 'fo' ]
    df = df[ df['SPEC_TYPE'].str.lower() != 'mi' ]
    df = df[ df['SPEC_TYPE'].str.lower() != 'un' ]

    df_eco = EColi(df[df['X_REFERRED'] != '1'])
    df_eco = df_eco.process()
    df_eco_referred = EColi(df[df['X_REFERRED'] == '1'])
    df_eco_referred = df_eco_referred.process()


    df_kpn = Kpn(df[df['X_REFERRED'] != '1'])
    df_kpn = df_kpn.process()
    df_kpn_referred = Kpn(df[df['X_REFERRED'] == '1'])
    df_kpn_referred = df_kpn_referred.process()


    df_aba = Aba(df[df['X_REFERRED'] != '1'])
    df_aba = df_aba.process()
    df_aba_referred = Aba(df[df['X_REFERRED'] == '1'])
    df_aba_referred = df_aba_referred.process()


    df_pae = Pae(df[df['X_REFERRED'] != '1'])
    df_pae = df_pae.process()
    df_pae_referred = Pae(df[df['X_REFERRED'] == '1'])
    df_pae_referred = df_pae_referred.process()

    df_efa_efm = EfaEfm(df[df['X_REFERRED'] != '1'])
    df_efa_efm = df_efa_efm.process()
    df_efa_efm_referred = EfaEfm(df[df['X_REFERRED'] == '1'])
    df_efa_efm_referred = df_efa_efm_referred.process()

    df_sau = Sau(df[df['X_REFERRED'] != '1'])
    df_sau = df_sau.process()
    df_sau_referred = Sau(df[df['X_REFERRED'] == '1'])
    df_sau_referred = df_sau_referred.process()

    df_sal_shi = SalShi(df[df['X_REFERRED'] != '1'])
    df_sal_shi = df_sal_shi.process()
    df_sal_shi_referred = SalShi(df[df['X_REFERRED'] == '1'])
    df_sal_shi_referred = df_sal_shi_referred.process()

    df_vic_eco = Vic157(df[df['X_REFERRED'] != '1'])
    df_vic_eco = df_vic_eco.process()
    df_vic_eco_referred = Vic157(df[df['X_REFERRED'] == '1'])
    df_vic_eco_referred = df_vic_eco_referred.process()

    df_hin_hpi = HinHpi(df[df['X_REFERRED'] != '1'])
    df_hin_hpi = df_hin_hpi.process()
    df_hin_hpi_referred = HinHpi(df[df['X_REFERRED'] == '1'])
    df_hin_hpi_referred = df_hin_hpi_referred.process()


    df_ngo = Ngo(df[df['X_REFERRED'] != '1'])
    df_ngo = df_ngo.process()
    df_ngo_referred = Ngo(df[df['X_REFERRED'] == '1'])
    df_ngo_referred = df_ngo_referred.process()


    df_nme = Nme(df[df['X_REFERRED'] != '1'])
    df_nme = df_nme.process()
    df_nme_referred = Nme(df[df['X_REFERRED'] == '1'])
    df_nme_referred = df_nme_referred.process()


    df_spn = Spn(df[df['X_REFERRED'] != '1'])
    df_spn = df_spn.process()
    df_spn_referred = Spn(df[df['X_REFERRED'] == '1'])
    df_spn_referred = df_spn_referred.process()

    df_str = Str(df[df['X_REFERRED'] != '1'])
    df_str = df_str.process()
    df_str_referred = Str(df[df['X_REFERRED'] == '1'])
    df_str_referred = df_str_referred.process()



    # DITO ANG START PAG NG SEMI CLEANED DATA FRAMES


   
    
    writer = pd.ExcelWriter('REFERRED_FOR_REVIEW_{}.xlsx'.format(file_name), engine='xlsxwriter')
    if len(df_eco) > 0:
        df_eco.to_excel(writer,sheet_name='eco',index=False)
    if len(df_eco_referred) > 0:
        df_eco_referred.to_excel(writer,sheet_name='eco_referred',index=False)

    if len(df_kpn) > 0:
        df_kpn.to_excel(writer,sheet_name='kpn',index=False)
    if len(df_kpn_referred) > 0:
        df_kpn_referred.to_excel(writer,sheet_name='kpn_referred',index=False)
    

    if len(df_aba) > 0:
        df_aba.to_excel(writer,sheet_name='aba',index=False)
    if len(df_aba_referred) > 0:
        df_aba_referred.to_excel(writer,sheet_name='aba_referred',index=False)


    if len(df_pae) > 0:
        df_pae.to_excel(writer,sheet_name='pae',index=False)
    if len(df_aba_referred) > 0:
        df_pae_referred.to_excel(writer,sheet_name='pae_referred',index=False)


    if len(df_efa_efm) > 0:
        df_efa_efm.to_excel(writer,sheet_name='efa_efm',index=False)
    if len(df_efa_efm_referred) > 0:
        df_efa_efm_referred.to_excel(writer,sheet_name='efa_efm_referred',index=False)
    

    if len(df_sau) > 0:
        df_sau.to_excel(writer,sheet_name='sau',index=False)
    if len(df_sau_referred) > 0:
        df_sau_referred.to_excel(writer,sheet_name='sau_referred',index=False)
    

    if len(df_sal_shi) > 0:
        df_sal_shi.to_excel(writer,sheet_name='sal_shi',index=False)
    if len(df_sal_shi_referred) > 0:
        df_sal_shi_referred.to_excel(writer,sheet_name='sal_shi_referred',index=False)


    if len(df_vic_eco) > 0:
        df_vic_eco.to_excel(writer,sheet_name='vic_eco157',index=False)
    if len(df_vic_eco_referred) > 0:
        df_vic_eco_referred.to_excel(writer,sheet_name='vic_eco157_referred',index=False)
        
        
    if len(df_hin_hpi) > 0:
        df_hin_hpi.to_excel(writer,sheet_name='hin_hpn',index=False)
    if len(df_hin_hpi_referred) > 0:
        df_hin_hpi_referred.to_excel(writer,sheet_name='hin_hpn_referred',index=False)

    if len(df_ngo) > 0:
        df_ngo.to_excel(writer,sheet_name='ngo',index=False)
    if len(df_ngo_referred) > 0:
        df_ngo_referred.to_excel(writer,sheet_name='ngo_referred',index=False)


    if len(df_nme) > 0:
        df_nme.to_excel(writer,sheet_name='nme',index=False)
    if len(df_nme_referred) > 0:
        df_nme_referred.to_excel(writer,sheet_name='nme_referred',index=False)

    if len(df_spn) > 0:
        df_spn.to_excel(writer,sheet_name='spn',index=False)
    if len(df_spn_referred) > 0:
        df_spn_referred.to_excel(writer,sheet_name='spn_referred',index=False)


    if len(df_str) > 0:
        df_str.to_excel(writer,sheet_name='str',index=False)
    if len(df_str_referred) > 0:
        df_str_referred.to_excel(writer,sheet_name='str_referred',index=False)

    ## for creation all vic and eco 157


    # if len(df_enterobact_all) > 0:
    #     df_enterobact_all.to_excel(writer,sheet_name='enterobact_all', index=False)
        
    # if len(df_enterobact_all_referred) > 0:
    #     df_enterobact_all_referred.to_excel(writer,sheet_name='enterobact_all referred', index=False)
    
    # if len(df_pae) > 0:
    #     df_pae.to_excel(writer,sheet_name='pae',index=False)
        
    # if len(df_pae_referred) > 0:
    #     df_pae_referred.to_excel(writer,sheet_name='pae_referred',index=False)
    
    # if len(df_aba) > 0:
    #     df_aba.to_excel(writer, sheet_name='aba', index=False)
    
    # if len(df_aba_referred) > 0:
    #     df_aba_referred.to_excel(writer, sheet_name='aba_referred', index=False)
    
    # if len(df_sau) > 0:
    #     df_sau.to_excel(writer, sheet_name='sau', index=False)
    
    # if len(df_sau_referred) > 0:
    #     df_sau_referred.to_excel(writer, sheet_name='sau_referred', index=False)
    
    # if len(df_ent) > 0:
    #     df_ent.to_excel(writer,sheet_name='ent',index=False)
        
    # if len(df_ent_referred) > 0:
    #     df_ent_referred.to_excel(writer,sheet_name='ent_referred',index=False)
    
    # if len(df_bsn) > 0:
    #     df_bsn.to_excel(writer,sheet_name='bsn',index=False)
        
    # if len(df_bsn_reffered) > 0:
    #     df_bsn_reffered.to_excel(writer,sheet_name='bsn_reffered',index=False)
    
    # if len(df_ent_list_review) > 0:
    #     df_ent_list_review.to_excel(writer,sheet_name='ENTERICS PATHOGENS', index=False)
        
    # if len(df_fast_list_review) > 0:
    #     df_fast_list_review.to_excel(writer,sheet_name='FASTIDIOUS ORGANISMS', index=False)
    
    writer.save()
    
    return writer 



# lambda functions
#
def get_date_to_compute(df):
    if pd.isna(df) == False:
        year = int(df.year)
        month = int(df.month)
        return datetime(year,month,3)

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

def check_R_nfo(row,value_list):
    # row['Test'] = ''
    for x in value_list:
        if row[x] == 'R' or row['CARBAPENEM'] == '+':
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
        if row[x] == 'R' or row['INDUC_CLI'] == 1 or ((row['ERY_RIS'] == 'R' ) and (row['CLI_RIS'] == 'S')):
            row['Test'] = 'R'
            return row
        else:
            row['Test'] = 'S'
            return row
    
            
                       