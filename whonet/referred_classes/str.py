import os
import pandas as pd
from whonet.functions.summary_report_helper import remove_null_cols, calculate_R_S, calculate_R_S_MIC, check_R_beta_lactam_str
dirpath = os.getcwd()
abx_panel = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_summary_referred_2023.xlsx','bs-')

class Str:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["bs-"])]
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
        df_beta_lactam = self.intermidiate_resistant_beta_lactam(df[df['ORGANISM'].isin(['bs-'])])
        frames.append(df_beta_lactam)


      

        df = self.concat_df(frames)
        df = df[df['SPEC_TYPE'].isin(["bl", "ti", "sf", "ab", "ga", "dr", "fl", "am", "at", "fn", "se", "pf", "di", "pd", "dn", "hf", "jf", "kf", "pu", "su", "ur", "wd", "ul", "as", "th","ta"])]
        df = pd.concat([df, df_referred])
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df =  df[df['Test'].isin(['R']) | (df['X_REFERRED'] == '1')]
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','comp','ent_fast'])
            df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID','Test'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','INSTITUT','LABORATORY','STOCK_NUM','PATIENT_ID','FIRST_NAME','LAST_NAME','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE',
                                            'ORGANISM','X_REFERRED','ESBL',
                                            'AMP_ND10','AMP_NM','AMP_RIS','PEN_ND10','PEN_NM','PEN_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS',
                                            'FEP_ND30','FEP_NM','FEP_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','DAP_ND30','DAP_NM','DAP_RIS',
                                            'VAN_ND30','VAN_NM','VAN_RIS','LNZ_ND30','LNZ_NM','LNZ_RIS','TZD_ND','TZD_NM','TZD_RIS'])
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
    
    def intermidiate_resistant_beta_lactam(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda row: check_R_beta_lactam_str(row), axis = 1)
    
   
    # def col_resistant(self, df: pd.DataFrame) -> pd.DataFrame:
    #     return df.apply(lambda row: check_R_to_col_pae(row), axis = 1)


    def concat_df(self,df_array: list) -> pd.DataFrame:
        return pd.concat(df_array,sort=False)
 






    ################ create another classes for NON referred and referred



    

