from whonet.models import *
import pandas as pd
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
import os
from django.db import IntegrityError


dirpath = os.getcwd()


def import_satscan(raw_data):
    
    tmp_name = raw_data.name
    
    file_name = tmp_name.split('.')[0]
    
    tmp_year_month = file_name.split('_')
    
    year_month = tmp_year_month[len(tmp_year_month) - 1]
    
    
    
    
    if 'cluster' in file_name:
        try:
            df = pd.read_csv(raw_data,encoding='iso-8859-1',dtype=str,parse_dates=['Cluster start date','Cluster end date','Date of first signal','Date of last signal'])
        except:
            return 'File ' + raw_data.name + ' is invalid format or columns are incorrect.'
        
        df = set_pd_columns_cluster(df)
        df['Cluster start date'] = (df['Cluster start date'].astype(str).replace({'NaT': None}))
        df['Cluster end date'] = (df['Cluster end date'].astype(str).replace({'NaT': None}))
        df['Date of first signal'] = (df['Date of first signal'].astype(str).replace({'NaT': None}))
        df['Date of last signal'] = (df['Date of last signal'].astype(str).replace({'NaT': None}))
        # df['Cluster end date'].fillna(None,inplace=True)
        # df['Date of first signal'].fillna(None,inplace=True)
        # df['Date of last signal'].fillna(None,inplace=True)
        row_iter = df.iterrows()
        save_satscan_cluster(row_iter,year_month)
        return 'File ' + file_name  +' successfully uploaded.'
    elif 'patient' in file_name:
        try:
            df = pd.read_csv(raw_data,encoding='iso-8859-1',dtype=str,parse_dates=['Specimen date','Date of admission'])
        except:
            return 'File ' + raw_data.name + ' is invalid format or columns are incorrect.'

        df = set_pd_columns_patient_list(df)
        df['Specimen date'] = (df['Specimen date'].astype(str).replace({'NaT': None}))
        df['Date of admission'] = (df['Date of admission'].astype(str).replace({'NaT': None}))
        
        row_iter = df.iterrows()
        save_satscan_patient_list(row_iter,year_month)
        return 'File ' + file_name  +' successfully uploaded.'
    else:
        return 'Keywords for ' + file_name  +' not found. Please try again.'

def save_satscan_patient_list(row_iter,year_month):
    SatScanPatientList.objects.filter(year_month = year_month).delete()
    
    for index, row in  row_iter:
        if row['Laboratory'] != '':
            patien_list = SatScanPatientList(
                year_month = year_month,
                cluster_number = row['Cluster number'],
                lab = row['Laboratory'],
                identification_number = row['Identification number'],
                first_name = row['First name'],
                last_name = row['Last name'],
                sex = row['Sex'],
                age = row['Age'],
                date_of_birth = row['Date of birth'],
                age_group = row['Age group'],
                location = row['Location'],
                department = row['Department'],
                location_type = row['Location type'],
                specimen_number = row['Specimen number'],
                specimen_date = row['Specimen date'],
                specimen_type = row['Specimen type'],
                organism = row['Organism'],
                beta_lactamase = row['Beta-lactamase'],
                comment = row['Comment'],
                referral_isolates = row['Referral Isolates'],
                mrsa = row['MRSA'],
                icr = row['ICR'],
                meca = row['MECA'],
                ampc = row['AMPC'],
                carb = row['CARB'],
                date_of_admission = row['Date of admission'],
                esbl = row['ESBL'],
                nosocomial = row['Nosocomial infection'],
                urine_colony = row['Urine colony count'],
                diagnosis = row['Diagnosis'],
                # january = row['January'],
                # february = row['February'],
                # march = row['March'], 
                # april = row['April'],
                # may = row['May'],
                # june = row['June'],
                # july = row['July'],
                # august = row['August'],
                # september = row['September'],
                # october = row['October'],
                # november = row['November'],
                # december = row['December'],
            )
            patien_list.save()




def save_satscan_cluster(row_iter,year_month):
    # if SatScanCluster.objects.filter(year_month = year_month).exists():
    SatScanCluster.objects.filter(year_month = year_month).delete()
   
    for index, row in  row_iter:
        if row['LAB'] != '':
            cluster = SatScanCluster(
                year_month = year_month,
                lab = row['LAB'],
                cluster_number = row['Cluster number'],
                cluster_code = row['Cluster code'],
                cluster_description = row['Cluster description'],
                cluster_start_date = row['Cluster start date'],
                cluster_end_date = row['Cluster end date'],
                date_first_signal = row['Date of first signal'],
                date_last_signal = row['Date of last signal'],
                recurrence_interval = row['Recurrence interval - First'],
                recurrence_highest = row['Recurrence interval - Highest'],
                recurrence_final = row['Recurrence interval - Final'],
                p_value_first = row['p-value - First'],
                p_value_lowest = row['p-value - Lowest'],
                p_value_final = row['p-value - Final'],
                number_observed_first = row['Number observed - First'],
                number_observed_max = row['Number observed - Maximum'],
                number_observed_final = row['Number observed - Final'],
                number_observed_total = row['Number observed - Total'],
                number_expected_first = row['Number expected - First'],
                number_expected_max = row['Number expected - Maximum'],
                number_expected_final = row['Number expected - Final'],
                days_to_first_signal = row['Days to first signal'],
                total_days_cluster = row['Total days in cluster'],
                number_of_signals = row['Number of signals'],
                number_of_locations = row['Number of locations'],
                radius = row['Radius'],
                satscan_x = row['X'],
                satscan_y = row['Y'],
                january = row['January'],
                february = row['February'],
                march = row['March'], 
                april = row['April'],
                may = row['May'],
                june = row['June'],
                july = row['July'],
                august = row['August'],
                september = row['September'],
                october = row['October'],
                november = row['November'],
                december = row['December'],
            )
            
            cluster.save()

def set_pd_columns_cluster(clm):
    
    whonet_data_fields = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','cluster')
    # whonet_data_fields_etest = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','etest')
    data_fields = whonet_data_fields['Data fields'].values.tolist()
    # etest = whonet_data_fields_etest['Data fields'].values.tolist()
    # etest = [x.lower() for x in etest]
    
    for col in data_fields:
        if col not in clm.columns:
            clm[col] = ''

    
    return clm



def set_pd_columns_patient_list(clm):
    
    whonet_data_fields = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','patient_list')
    # whonet_data_fields_etest = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','etest')
    data_fields = whonet_data_fields['Data fields'].values.tolist()
    # etest = whonet_data_fields_etest['Data fields'].values.tolist()
    # etest = [x.lower() for x in etest]
    
    for col in data_fields:
        if col not in clm.columns:
            clm[col] = ''

    
    return clm