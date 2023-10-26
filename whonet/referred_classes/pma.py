import os
import pandas as pd
from datetime import datetime
from whonet.functions.summary_report_helper import get_date_to_compute, calculate_R_S, calculate_R_S_MIC, remove_null_cols, check_R_beta_lactam_pma
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','pma')

class Pme:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df
        self.num_of_days = num_of_days
        self.ast_panel = abx_panel['WHON5_CODE'].values.tolist()
        self.ast_panel_mic = abx_panel['WHON5_CODE_MIC'].values.tolist()
    

    def process(self) -> pd.DataFrame:
        df = self.df
        frames = []
        df = self.calc_RIS(df)
        df = self.calc_RIS_MIC(df)

        # df_col = self.col_resistant(df[df['ORGANISM'].isin(['pma'])])
        # frames.append(df_col)

        # df_referral_days = self.df_referral_days_based_on_phenotype_of_interest(df)

        # df_pheno_of_interest = self.resistant_only_to_aminoglycosides(df_referral_days)
        # frames.append(df_pheno_of_interest)

        # df_carbapenems = self.intermidiate_resistant_to_carbapenems(df_referral_days)
        # frames.append(df_carbapenems)

        df_beta_lactam = self.intermidiate_resistant_beta_lactam(df[df['ORGANISM'].isin(['pma'])])
        frames.append(df_beta_lactam)


      

        df = self.concat_df(frames)
        df = df[df['SPEC_TYPE'].isin(["bl", "ti", "sf", "ab", "ga", "dr", "fl", "am", "at", "fn", "se", "pf", "di", "pd", "dn", "hf", "jf", "kf", "pu", "su", "ur", "wd", "ul", "as", "sp"])]
        # df = df.loc[df['Test'] == 'R']
        
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df =  df[df['Test'].isin(['R'])]
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast'])
            df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','Test'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE',
                                            'ORGANISM','X_REFERRED','ESBL','SXT_ND1_2','SXT_NM','SXT_RIS','FDC_ND30','FDC_NM','FDC_RIS'])
            df = df[cols]
            return df
        return df




    # def df_referral_days_based_on_phenotype_of_interest(self, df : pd.DataFrame) -> pd.DataFrame:
    #     df = df[df['ORGANISM'].isin(['pae'])]
    #     df['comp'] = df['SPEC_DATE'].apply(lambda df: get_date_to_compute(df,self.num_of_days))
    #     df['ent_fast'] = df['comp'] - df['SPEC_DATE']
    #     return df[df['ent_fast'].dt.days >= 0]


    def calc_RIS(self, df : pd.DataFrame) -> pd.DataFrame:
        for value in self.ast_panel:
              df = df.apply(lambda row: calculate_R_S(row,value,abx_panel,self.ast_panel), axis = 1)
        return df


    def calc_RIS_MIC(self, df : pd.DataFrame) -> pd.DataFrame:
        for value in self.ast_panel_mic:
              df = df.apply(lambda row: calculate_R_S_MIC(row,value,abx_panel,self.ast_panel_mic), axis = 1)
        return df

    
    # def resistant_only_to_aminoglycosides(self, df: pd.DataFrame) -> pd.DataFrame:
    #     return df.apply(lambda row: check_R_to_aminoglycoside_pae(row), axis = 1)
    
    # def intermidiate_resistant_to_carbapenems(self, df: pd.DataFrame) -> pd.DataFrame:
    #     return df.apply(lambda row: check_R_to_carbapenems_pae(row),axis = 1)
    
    def intermidiate_resistant_beta_lactam(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_R_beta_lactam_pma(row), axis = 1)
    
   
    # def col_resistant(self, df: pd.DataFrame) -> pd.DataFrame:
    #     return df.apply(lambda row: check_R_to_col_pae(row), axis = 1)


    def concat_df(self,df_array: list) -> pd.DataFrame:
        return pd.concat(df_array,sort=False)
    

    


    

    ################ create another classes for NON referred and referred



    

