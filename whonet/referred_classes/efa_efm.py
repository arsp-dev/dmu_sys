import os
import pandas as pd
from datetime import datetime
from whonet.functions.summary_report_helper import get_date_to_compute, calculate_R_S, calculate_R_S_MIC, remove_null_cols, check_R_to_aminoglycoside_efa_efm, check_R_to_pens_efa_efm
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','efa_efm')

class EfaEfm:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["efa","efm"])]
        self.num_of_days = num_of_days
        self.ast_panel = abx_panel['WHON5_CODE'].values.tolist()
        self.ast_panel_mic = abx_panel['WHON5_CODE_MIC'].values.tolist()
    

    def process(self) -> pd.DataFrame:
        df = self.df
        frames = []
        df = self.calc_RIS(df)
        df = self.calc_RIS_MIC(df)


        df_referral_days = self.df_referral_days_based_on_phenotype_of_interest(df)

        df_pheno_of_interest = self.resistant_only_to_aminoglycosides(df)
        frames.append(df_pheno_of_interest)

        df_nonsuscep = self.nonsuscep_to_pens(df_referral_days)
        frames.append(df_nonsuscep)



      

        df = self.concat_df(frames)
        df = df[df['SPEC_TYPE'].isin(["bl", "ti", "sf", "ab", "ga", "dr", "fl", "am", "at", "fn", "se", "pf", "di", "pd", "dn", "hf", "jf", "kf", "pu", "su", "ur", "wd", "ul","as","ta"])]
        # df = df.loc[df['Test'] == 'R']
        
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df =  df[df['Test'].isin(['R'])]
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast'])
            df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast','Test'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','AMK_ND30','GEH_ND120','GEH_NM','GEH_RIS','STH_ND300','STH_NM','STH_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','VAN_ND30','VAN_NM','VAN_RIS','DAP_NM','DAP_RIS','TZD_ND','TZD_NM','TZD_RIS'])
            df = df[cols]
            return df
        return df




    def df_referral_days_based_on_phenotype_of_interest(self, df : pd.DataFrame) -> pd.DataFrame:
        df = df[df['ORGANISM'].isin(['efa','efm'])]
        df['comp'] = df['SPEC_DATE'].apply(lambda df: get_date_to_compute(df,self.num_of_days))
        df['ent_fast'] = df['comp'] - df['SPEC_DATE']
        return df[df['ent_fast'].dt.days >= 0]


    def calc_RIS(self, df : pd.DataFrame) -> pd.DataFrame:
        for value in self.ast_panel:
              df = df.apply(lambda row: calculate_R_S(row,value,abx_panel,self.ast_panel), axis = 1)
        return df


    def calc_RIS_MIC(self, df : pd.DataFrame) -> pd.DataFrame:
        for value in self.ast_panel_mic:
              df = df.apply(lambda row: calculate_R_S_MIC(row,value,abx_panel,self.ast_panel_mic), axis = 1)
        return df

    
    def resistant_only_to_aminoglycosides(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_R_to_aminoglycoside_efa_efm(row), axis = 1)
    
    def nonsuscep_to_pens(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_R_to_pens_efa_efm(row), axis = 1)
    
 

    def concat_df(self,df_array: list) -> pd.DataFrame:
        return pd.concat(df_array,sort=False)
    

    


    

    ################ create another classes for NON referred and referred



    

