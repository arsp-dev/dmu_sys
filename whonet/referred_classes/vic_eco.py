import pandas as pd
from whonet.functions.summary_report_helper import remove_null_cols

class Vic157:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["vie", "val", "via", "vca", "vic", "vel", "vo1", "vhi", "vin", "vog", '139', "vx1", "vci", "pdm", "cfe", "vfl", "vfu", "vca", "vho", "vme", "vmi", "vip", "lpe", "vi-", "moi", "vvu", '157'])]
       
    

    def process(self) -> pd.DataFrame:
        df = self.df
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','CAZ_ND30','CAZ_NM','GEN_ND10','GEN_NM','TOB_ND10','TOB_NM','AMK_ND30','AMK_NM','FEP_ND30','FEP_NM','CIP_ND5','CIP_NM','IPM_ND10','IPM_NM','MEM_ND10','MEM_NM'])
            df = df[cols]
            return df
        return df
     
     






    ################ create another classes for NON referred and referred



    

