import os
import pandas as pd
from datetime import datetime
from whonet.functions.summary_report_helper import get_date_to_compute, calculate_R_S, calculate_R_S_MIC, remove_null_cols, check_resistant_inter_sal_shi, check_resistant_sal_shi
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','sal_shi')

class SalShi:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(['sal','shi'])]
        self.num_of_days = num_of_days
        self.ast_panel = abx_panel['WHON5_CODE'].values.tolist()
        self.ast_panel_mic = abx_panel['WHON5_CODE_MIC'].values.tolist()
    

    def process(self) -> pd.DataFrame:
        df = self.df
        df_referred = df[df['X_REFERRED'] == '1']
        df_referred['Test'] = ''
        df = df[df['X_REFERRED'] != '1']
        frames = []
        df = self.calc_RIS(df)
        df = self.calc_RIS_MIC(df)


        df_inter_resistant = self.resistant_inter_only(df)
        frames.append(df_inter_resistant)

        df_resistant = self.resistant_only(df)
        frames.append(df_resistant)


        df = self.concat_df(frames)
        df = df[df['SPEC_TYPE'].isin(["bl", "ti", "sf", "ab", "ga", "dr", "fl", "am", "at", "fn", "se", "pf", "di", "pd", "dn", "hf", "jf", "kf", "pu", "su", "ur", "wd", "ul", "as","st","re"])]
        df = pd.concat([df, df_referred])
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df =  df[df['Test'].isin(['R']) | (df['X_REFERRED'] == '1')]
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast'])
            df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','Test'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','INSTITUT','LABORATORY','STOCK_NUM','PATIENT_ID','FIRST_NAME','LAST_NAME','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','AZM_ND15','AZM_NM','AZM_RIS','CIP_ND5','CIP_NM','CIP_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS'])
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

    
    def resistant_inter_only(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_resistant_inter_sal_shi(row), axis = 1)
    
    def resistant_only(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_resistant_sal_shi(row),axis = 1)
    
   

    def concat_df(self,df_array: list) -> pd.DataFrame:
        return pd.concat(df_array,sort=False)
    

    


    

    ################ create another classes for NON referred and referred



    

