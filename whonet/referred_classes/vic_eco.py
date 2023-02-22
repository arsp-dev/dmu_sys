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
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','AMK_ND30','AMK_NM','AMK_RIS','GEN_ND10','GEN_NM','GEN_RIS','TOB_ND10','TOB_NM','TOB_RIS','IPM_ND10','IPM_NM','IPM_RIS','MEM_ND10','MEM_NM','MEM_RIS','ETP_ND10','ETP_NM','ETP_RIS','CAZ_ND30','CAZ_NM','CAZ_RIS','CTX_ND30','CTX_NM','CTX_RIS','CRO_ND30','CRO_NM','CRO_RIS','FEP_ND30','FEP_NM','FEP_RIS','COL_NM','POL_NM'])
            df = df[cols]
            return df
        return df
     
     






    ################ create another classes for NON referred and referred



    

