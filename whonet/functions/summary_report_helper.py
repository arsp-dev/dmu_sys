import pandas as pd
from datetime import datetime
import os
import numpy as np


def get_date_to_compute(df : pd.DataFrame,num_of_days : int) -> datetime:
    if pd.isna(df) == False:
        year = int(df.year)
        month = int(df.month)
        return datetime(year,month,num_of_days)

def remove_null_cols(df,ant_list):
    for x in ant_list:
        if x not in df.columns:
            ant_list.remove(x)
    return df,ant_list

def check_R_to_aminoglycoside_eco(row):
        value_list = ['AMK_RIS','GEN_RIS','TOB_RIS']
        for x in value_list:
            if row[x] == 'R':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


def check_R_to_carbapenems_eco(row):
        value_list = ['IPM_RIS','MEM_RIS','ETP_RIS']
        for x in value_list:
            if row[x] == 'R' or row[x] == 'I':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


def check_R_to_cephalosporins_eco(row):
        value_list = ['CAZ_RIS','CTX_RIS','CRO_RIS','FEP_RIS']
        for x in value_list:
            if row[x] == 'R' or row[x] == 'I' or row['ESBL'] == '+':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row
    

def check_R_to_col_eco(row):
    row['COL_NM'] =  row['COL_NM'].replace('>=','')
    row['COL_NM'] =  row['COL_NM'].replace('<=','')
    row['COL_NM'] =  row['COL_NM'].replace('>','')
    row['COL_NM'] =  row['COL_NM'].replace('<','')

    row['POL_NM'] =  row['POL_NM'].replace('>=','')
    row['POL_NM'] =  row['POL_NM'].replace('<=','')
    row['POL_NM'] =  row['POL_NM'].replace('>','')
    row['POL_NM'] =  row['POL_NM'].replace('<','')
    if  row['COL_NM'] != '' and row['COL_NM'] not in ['R','I','S']:
        if float(row['COL_NM']) > 4.0:
            row['Test'] = 'R'
            return row

    if  row['POL_NM'] != '' and row['POL_NM'] not in ['R','I','S']:
        if float(row['POL_NM']) > 4.0:
            row['Test'] = 'R'
            return row
    row['Test'] = 'None'
    return row






def check_R_to_aminoglycoside_kpn(row):
        value_list = ['GEN_RIS','TOB_RIS']
        for x in value_list:
            if row[x] == 'R':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


def check_R_to_carbapenems_kpn(row):
        value_list = ['IPM_RIS','MEM_RIS','ETP_RIS']
        for x in value_list:
            if row[x] == 'R' or row[x] == 'I':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


    
def check_R_to_col_kpn(row):
    row['COL_NM'] =  row['COL_NM'].replace('>=','')
    row['COL_NM'] =  row['COL_NM'].replace('<=','')
    row['COL_NM'] =  row['COL_NM'].replace('>','')
    row['COL_NM'] =  row['COL_NM'].replace('<','')

    row['POL_NM'] =  row['POL_NM'].replace('>=','')
    row['POL_NM'] =  row['POL_NM'].replace('<=','')
    row['POL_NM'] =  row['POL_NM'].replace('>','')
    row['POL_NM'] =  row['POL_NM'].replace('<','')
    if  row['COL_NM'] != ''  and row['COL_NM'] not in ['R','I','S']:
        if float(row['COL_NM']) > 4.0:
            row['Test'] = 'R'
            return row

    if  row['POL_NM'] != '' and row['POL_NM'] not in ['R','I','S']:
        if float(row['POL_NM']) > 4.0 :
            row['Test'] = 'R'
            return row
    row['Test'] = 'None'
    return row




def check_R_to_carbapenems_aba(row):
        value_list = ['IPM_RIS','MEM_RIS']
        for x in value_list:
            if row[x] == 'R' or row[x] == 'I':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


    
def check_R_to_col_aba(row):
    row['COL_NM'] =  row['COL_NM'].replace('>=','')
    row['COL_NM'] =  row['COL_NM'].replace('<=','')
    row['COL_NM'] =  row['COL_NM'].replace('>','')
    row['COL_NM'] =  row['COL_NM'].replace('<','')

    row['POL_NM'] =  row['POL_NM'].replace('>=','')
    row['POL_NM'] =  row['POL_NM'].replace('<=','')
    row['POL_NM'] =  row['POL_NM'].replace('>','')
    row['POL_NM'] =  row['POL_NM'].replace('<','')
    if  row['COL_NM'] != '' and row['COL_NM'] not in ['R','I','S']:
        if float(row['COL_NM']) > 4.0 :
            row['Test'] = 'R'
            return row

    if  row['POL_NM'] != '' and row['POL_NM'] not in ['R','I','S']:
        if float(row['POL_NM']) > 4.0 :
            row['Test'] = 'R'
            return row
    row['Test'] = 'None'
    return row



def check_R_to_carbapenems_pae(row):
        value_list = ['IPM_RIS','MEM_RIS']
        for x in value_list:
            if row[x] == 'R' or row[x] == 'I':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


def check_R_to_aminoglycoside_pae(row):
        value_list = ['AMK_RIS','GEN_RIS','TOB_RIS']
        for x in value_list:
            if row[x] == 'R':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row
    

def check_R_to_col_pae(row):
    row['COL_NM'] =  row['COL_NM'].replace('>=','')
    row['COL_NM'] =  row['COL_NM'].replace('<=','')
    row['COL_NM'] =  row['COL_NM'].replace('>','')
    row['COL_NM'] =  row['COL_NM'].replace('<','')

    row['POL_NM'] =  row['POL_NM'].replace('>=','')
    row['POL_NM'] =  row['POL_NM'].replace('<=','')
    row['POL_NM'] =  row['POL_NM'].replace('>','')
    row['POL_NM'] =  row['POL_NM'].replace('<','')
    if  row['COL_NM'] != '' and row['COL_NM'] not in ['R','I','S']:
        if float(row['COL_NM']) > 4.0 :
            row['Test'] = 'R'
            return row

    if  row['POL_NM'] != '' and row['POL_NM'] not in ['R','I','S']:
        if float(row['POL_NM']) > 4.0 :
            row['Test'] = 'R'
            return row
    row['Test'] = 'None'
    return row


def check_R_to_aminoglycoside_efa_efm(row):
    row['DAP_NM'] =  row['DAP_NM'].replace('>=','')
    row['DAP_NM'] =  row['DAP_NM'].replace('<=','')
    row['DAP_NM'] =  row['DAP_NM'].replace('>','')
    row['DAP_NM'] =  row['DAP_NM'].replace('<','')
    if row['DAP_NM'] not in ['R','I','S'] and row['DAP_NM'] != '':
        if float(row['DAP_NM']) >= 8:
            row['DAP_RIS'] = 'R'
        elif float(row['DAP_NM']) <= 2:
            row['DAP_RIS'] = 'S'
        elif float(row['DAP_NM']) > 2 and float(row['DAP_NM']) < 8:
            row['DAP_RIS'] = 'I'
        else:
            row['DAP_RIS'] = ''
    else:
        row['DAP_RIS'] = ''
        


    value_list = ['GEH_RIS','STH_RIS','LNZ_RIS','VAN_RIS','DAP_RIS']
    for x in value_list:
        if row[x] == 'R':
            row['Test'] = 'R'
            return row
        row['Test'] = 'None'
        return row



def clean_sau_days(row):
    row['OXA_NM'] =  row['OXA_NM'].replace('>=','')
    row['OXA_NM'] =  row['OXA_NM'].replace('<=','')
    row['OXA_NM'] =  row['OXA_NM'].replace('>','')
    row['OXA_NM'] =  row['OXA_NM'].replace('<','')
    if row['OXA_NM'] not in ['R','I','S'] and row['OXA_NM'] != '':
        if float(row['OXA_NM']) >= 1:
            row['OXA_RIS'] = 'R'
        elif float(row['OXA_NM']) <= 0.5:
            row['OXA_RIS'] = 'S'
        elif float(row['OXA_NM']) > 0.5 and float(row['OXA_NM']) < 1:
            row['OXA_RIS'] = 'I'
        else:
            row['OXA_RIS'] = ''
    else:
        row['OXA_RIS'] = ''

    value_list = ['FOX_RIS','OXA_RIS']
    for x in value_list:
        if row[x] == 'R':
            row['Test'] = 'R'
            return row
        row['Test'] = 'None'
        return row


def clean_sau(row):
    row['DAP_NM'] =  row['DAP_NM'].replace('>=','')
    row['DAP_NM'] =  row['DAP_NM'].replace('<=','')
    row['DAP_NM'] =  row['DAP_NM'].replace('>','')
    row['DAP_NM'] =  row['DAP_NM'].replace('<','')
    if row['DAP_NM'] not in ['R','I','S'] and row['DAP_NM'] != '':
        if float(row['DAP_NM']) >= 1:
            row['DAP_RIS'] = 'R'
        elif float(row['DAP_NM']) <= 0.5:
            row['DAP_RIS'] = 'S'
        elif float(row['DAP_NM']) > 0.5 and float(row['DAP_NM']) < 1:
            row['DAP_RIS'] = 'I'
        else:
            row['DAP_RIS'] = ''
    else:
        row['DAP_RIS'] = ''
        


    value_list = ['LNZ_RIS','DAP_RIS']
    for x in value_list:
        if row[x] == 'R' or row['INDUC_CLI'] == '+':
            row['Test'] = 'R'
            return row
        row['Test'] = 'None'
        return row



def check_resistant_inter_sal_shi(row):
        value_list = ['CTX_NM','CRO_NM','CIP_NM']
        for x in value_list:
            if row[x] == 'R' or row[x] == 'I' or row['ESBL'] == '+':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


def check_resistant_sal_shi(row):
        value_list = ['AZM_NM']
        for x in value_list:
            if row[x] == 'R' or row['ESBL'] == '+':
                row['Test'] = 'R'
                return row
        row['Test'] = 'None'
        return row


def check_R_hin_hpn(row):
    row['COL_NM'] =  row['COL_NM'].replace('>=','')
    row['COL_NM'] =  row['COL_NM'].replace('<=','')
    row['COL_NM'] =  row['COL_NM'].replace('>','')
    row['COL_NM'] =  row['COL_NM'].replace('<','')

    row['POL_NM'] =  row['POL_NM'].replace('>=','')
    row['POL_NM'] =  row['POL_NM'].replace('<=','')
    row['POL_NM'] =  row['POL_NM'].replace('>','')
    row['POL_NM'] =  row['POL_NM'].replace('<','')
    if  row['COL_NM'] != ''  and row['COL_NM'] not in ['R','I','S']:
        if float(row['COL_NM']) > 4.0:
            row['Test'] = 'R'
            return row

    if  row['POL_NM'] != '' and row['POL_NM'] not in ['R','I','S']:
        if float(row['POL_NM']) > 4.0 :
            row['Test'] = 'R'
            return row
    row['Test'] = 'None'
    return row



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
                elif frame['S>='][org_list.index(value)] != '':
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
    if value.split('_')[0] + '_RIS' not in row:
        row[value.split('_')[0] + '_RIS'] = ''
    return row





