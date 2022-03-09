from pandas.core.reshape.merge import merge
from whonet.models import *
import pandas as pd
import numpy as np
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
import os
from whonet.functions.insert_rows import import_metadata, import_mlst_salmonella, import_qualifyr, import_arsp_qualifyr
from django.forms import model_to_dict

dirpath = os.getcwd()
epi_data = pd.read_excel(dirpath + '/whonet/static/bioinfo_xl/EPI_DATA_CLEAN.xlsx')
# epi_data = epi_data.drop(['Sample id'], axis=1)

def import_data(metadata,qualifyr,mlst,mlst_organism):
   if(metadata is not None):
     df_metadata = pd.read_excel(metadata)
    #  EpiMetaData.objects.all().delete()
     df_metadata_processed = import_metadata(df_metadata.iterrows())
    
  
   
   if(qualifyr is not None):
    df_qualifyr = pd.read_excel(qualifyr)
    #  RetroQualifyr.objectes.all().delete()
    df_qualifyr_processed = import_qualifyr(df_qualifyr.iterrows())
  
  
   if(mlst is not None):
     df_mlst = pd.read_excel(mlst)
     
     if(mlst_organism == 'salmonella'):
        df_mlst_processed = import_mlst_salmonella(df_mlst.iterrows())
  
    
   # return df_metadata

def import_arsp_data(metadata,qualifyr,mlst,mlst_organism):
   if(metadata is not None):
     df_metadata = pd.read_excel(metadata)
    #  EpiMetaData.objects.all().delete()
     df_metadata_processed = import_metadata(df_metadata.iterrows())
    
  
   
   if(qualifyr is not None):
    df_qualifyr = pd.read_excel(qualifyr)
    #  RetroQualifyr.objectes.all().delete()
    df_qualifyr_processed = import_arsp_qualifyr(df_qualifyr.iterrows())
  
  
   if(mlst is not None):
     df_mlst = pd.read_excel(mlst)
     
     if(mlst_organism == 'salmonella'):
        df_mlst_processed = import_mlst_salmonella(df_mlst.iterrows())



def clean_amr_data(input):
    df = pd.read_csv(input)
    df.drop([col for col in df.columns if 'ref_seq' not in col and 'name' not in col],axis=1,inplace=True)
    df.fillna('NO', inplace=True)
    return df
  
  

def create_report(organism_list):
   epimetadata  = [ model_to_dict(pallobj) for pallobj in EpiMetaData.objects.filter(wgs_id__in=organism_list)] 
   df_metadata = pd.DataFrame(epimetadata)
   sample_list = df_metadata['sample_id'].to_list()
   
   retro_qualifyr = [ model_to_dict(pallobj) for pallobj in RetroQualifyr.objects.filter(sample_name__in=sample_list)]
   df_qualifyr = pd.DataFrame(retro_qualifyr)
   
   mlst = [ model_to_dict(pallobj) for pallobj in MlstSalmonella.objects.filter(sample_id__in=sample_list)]
   df_mlst = pd.DataFrame(mlst)
   
   sequence_type_list = df_mlst['sequence_type'].unique()
   sequence_type_count = df_mlst['sequence_type'].value_counts()
   sequence_type = create_df_from_list(sequence_type_list,sequence_type_count,'Sequence Type')
   
   ## creating dataframe of patient gender
   patient_gender_list = df_metadata['patient_gender'].unique()
   gender_count = df_metadata['patient_gender'].value_counts()
   gender = create_df_from_list(patient_gender_list,gender_count,'Gender')
   ## end dataframe of patient gender
   
   
   #creating dataframe of origin
   patient_origin_list = df_metadata['origin'].unique()
   origin_count = df_metadata['origin'].value_counts()
   origin = create_df_from_list(patient_origin_list,origin_count,'Origin')
   #end dataframe of origin
   
   
   #creating dataframe of specimen type
   patient_specimen_type_list = df_metadata['specimen_type'].unique()
   specimen_type_count = df_metadata['specimen_type'].value_counts()
   specimen_type = create_df_from_list(patient_specimen_type_list,specimen_type_count,'Specimen Type')
   #end dataframe of specimen type
   
   patient_age_list = df_metadata['patient_age'].to_list()
   age_group = create_df_from_list_age(patient_age_list)
   
   
   ast_profile_list = df_metadata['ast_profile'].unique()
   ast_profile_count = df_metadata['ast_profile'].value_counts()
   ast_profile = create_df_from_list(ast_profile_list,ast_profile_count,'AST Profile')
  #  print(ast_profile)
   
   
   site_list = df_metadata['sentinel_site_code'].unique()
   site_count = df_metadata['sentinel_site_code'].value_counts()
   site = create_df_from_list(site_list,site_count,'Sentinel Site')
   
   patient_type_list = df_metadata['patient_type'].unique()
   patient_type_count = df_metadata['patient_type'].value_counts()
   patient_type = create_df_from_list(patient_type_list,patient_type_count,'Patient Type')
   
   year_list = df_metadata['year'].unique()
   year_count = df_metadata['year'].value_counts()
   year = create_df_from_list(year_list,year_count,'Year')
   
   
   serotype_list = df_metadata['wgs_id'].unique()
   serotype_count = df_metadata['wgs_id'].value_counts()
   serotype = create_df_from_list(serotype_list,serotype_count,'Serotype')

   
   new_df = pd.merge(df_metadata,df_qualifyr,left_on='sample_id',right_on='sample_name',how="outer")
  #  print(df_mlst_salmonella.columns.values)
   df = pd.merge(new_df,df_mlst,on=["sample_id", "sample_id"],how='outer')
   
   df = df.replace(['nan'],' ')
   df = df.drop(columns=['id','id_x','id_y','sample_name'])
   
   return df,gender,origin,specimen_type,age_group,ast_profile,site,patient_type,year,serotype,sequence_type
   
   
   
   
   
 
def create_df_from_list(df_lists,df_count,df_type):
  data = []
  for df_list in df_lists:
    data.append([str(df_list),str(df_count[str(df_list)])])
    
  df = pd.DataFrame(data, columns = [df_type, 'Count'])
  
  return df


def create_df_from_list_age(df_lists):
  zero_to_five = 0
  six_to_seventeen = 0
  eighteen_to_sixtyfour = 0
  sixtyfive_up = 0
  nan_else = 0
  for df_list in df_lists:
    df_list = str(df_list)
    if 'd' in df_list:
      zero_to_five += 1
    elif 'm' in df_list:
      zero_to_five += 1
    elif int(df_list) >= 0 and int(df_list) <= 5:
      zero_to_five += 1
    elif int(df_list) >= 6 and int(df_list) <= 17:
      six_to_seventeen += 1
    elif int(df_list) >= 18 and int(df_list) <= 64:
      eighteen_to_sixtyfour += 1
    elif int(df_list) >= 65 and int(df_list) <= 199:
      sixtyfive_up += 1
    else:
      nan_else += 1
  
  data = [
     ['0 - 5',zero_to_five], ['6 - 17',six_to_seventeen],['18 - 64',eighteen_to_sixtyfour],['65 +', sixtyfive_up], ['Others',nan_else]
   ]
  
  df = pd.DataFrame(data, columns = ['Age Group', 'Count'])
  
  
  return df
 
     