import pandas as pd
from whonet.functions.summary_report_helper import remove_null_cols

class HinHpi:

    def __init__(self, df : pd.DataFrame, num_of_days : int = 3) -> None:
        self.df = df[df['ORGANISM'].isin(["hin","hpi"])]
       
    

    def process(self) -> pd.DataFrame:
        df = self.df
        if len(df) > 0:
            df.dropna(how = 'all',inplace = True)
            df = df.drop_duplicates(subset=['PATIENT_ID','SPEC_DATE','ORGANISM'])
            df['SPEC_DATE'] = df['SPEC_DATE'].dt.strftime('%m/%d/%Y')
            df, cols = remove_null_cols(df,['Test','PATIENT_ID','SEX','AGE','DATE_BIRTH','DATE_ADMIS','SPEC_NUM','SPEC_DATE','SPEC_TYPE','ORGANISM','X_REFERRED','ESBL','AMC_ND20','AMC_NM','AMP_ND10','AMP_NM','CIP_ND5','CIP_NM','LVX_ND5','LVX_NM','CRO_ND30','CRO_NM','MEM_ND10','MEM_NM'])
            df = df[cols]
            return df
        return df
     
     






    ################ create another classes for NON referred and referred



    
