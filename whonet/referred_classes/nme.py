import os
import pandas as pd
from whonet.functions.summary_report_helper import remove_null_cols, calculate_R_S, calculate_R_S_MIC, check_R_nme_phenotype_of_interest
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','nme')

class Nme:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["nme"])]
        self.ast_panel = abx_panel['WHON5_CODE'].values.tolist()
        self.ast_panel_mic = abx_panel['WHON5_CODE_MIC'].values.tolist()     
       
    

    def process(self) -> pd.DataFrame:
        df = self.df
        frames = []
        df = self.calc_RIS(df)
        df = self.calc_RIS_MIC(df)
        df_refer_all = self.nme_phenotype_of_interest(df)
        frames.append(df_refer_all)


        df = self.concat_df(frames)
        df = df[df['SPEC_TYPE'].isin(["bl", "ti", "sf", "ab", "ga", "dr", "fl", "am", "at", "fn", "se", "pf", "di", "pd", "dn", "hf", "jf", "kf", "pu", "su", "wd", "ul", "as","sp","ta","ue","va"])]
        # df = df.loc[df['Test'] == 'R']
        
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df =  df[df['Test'].isin(['R'])]
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast'])
            df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','Test'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','CIP_ND5','CIP_NM','CIP_RIS','MEM_ND10','MEM_NM','MEM_RIS','RIF_ND5','RIF_NM','RIF_RIS','CRO_ND30','CRO_NM','CRO_RIS','AMP_ND10','AMP_NM','AMP_RIS','PEN_NM','PEN_RIS'])
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
    
    def nme_phenotype_of_interest(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_R_nme_phenotype_of_interest(row),axis = 1)

    def concat_df(self,df_array: list) -> pd.DataFrame:
        return pd.concat(df_array,sort=False)






    ################ create another classes for NON referred and referred



    

