import os
import pandas as pd
from whonet.functions.summary_report_helper import remove_null_cols, calculate_R_S, calculate_R_S_MIC
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','bs-')

class Str:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["bs-"])]
        self.ast_panel = abx_panel['WHON5_CODE'].values.tolist()
        self.ast_panel_mic = abx_panel['WHON5_CODE_MIC'].values.tolist()  
       
    

    def process(self) -> pd.DataFrame:
        df = self.df
        df = self.calc_RIS(df)
        df = self.calc_RIS_MIC(df)
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','AMP_ND10','AMP_NM','PEN_ND10','PEN_NM','CTX_ND30','CTX_NM','CRO_ND30','CRO_NM','FEP_ND30','FEP_NM','DAP_ND30','DAP_NM','LNZ_ND30','LNZ_NM','VAN_ND30','VAN_NM'])
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
 






    ################ create another classes for NON referred and referred



    

