import os
import pandas as pd
from datetime import datetime
from whonet.functions.summary_report_helper import get_date_to_compute, calculate_R_S, calculate_R_S_MIC, remove_null_cols, check_R_spn_phenotype_of_interest
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','spn')

class Spn:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["spn"])]
        self.ast_panel = abx_panel['WHON5_CODE'].values.tolist()
        self.ast_panel_mic = abx_panel['WHON5_CODE_MIC'].values.tolist()
       
    

    def process(self) -> pd.DataFrame:
        df = self.df
        frames = []
        df = self.calc_RIS(df)
        df = self.calc_RIS_MIC(df)
        df_refer_all = self.spn_phenotype_of_interest(df)
        frames.append(df_refer_all)


        df = self.concat_df(frames)
        # df = df.loc[df['Test'] == 'R']
        
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df =  df[df['Test'].isin(['R'])]
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast'])
            df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','Test'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','INDUC_CLI','AMK_ND30','AMK_NM','AMK_RIS','GEN_ND10','GEN_NM','GEN_RIS','TOB_ND10','TOB_NM','TOB_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS','FEP_ND30','FEP_NM','FEP_RIS','COL_NM','POL_NM'])
            df = df[cols]
            return df
        return df
     
     
    def calc_RIS(self, df : pd.DataFrame) -> pd.DataFrame:
        for value in self.ast_panel:
              df = df.apply(lambda row: calculate_R_S(row,value,abx_panel,self.ast_panel), axis = 1)
        return df


    def calc_RIS_MIC(self, df : pd.DataFrame) -> pd.DataFrame:
        for value in self.ast_panel_mic:
              df = df.apply(lambda row: calculate_R_S_MIC(row,value,abx_panel,self.ast_panel_mic), axis = 1)
        return df
    
    def spn_phenotype_of_interest(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_R_spn_phenotype_of_interest(row),axis = 1)
    

    def concat_df(self,df_array: list) -> pd.DataFrame:
        return pd.concat(df_array,sort=False)
     
     






    ################ create another classes for NON referred and referred



    

