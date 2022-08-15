import os
import pandas as pd
from pandas import DataFrame
import typing

from pip import main


class CombineDataFrame:
    def __init__(self,file_name : str, blood_dict : typing.Dict[str,int], 
    blood_others : typing.Dict[str,int], blood_negative : typing.Dict[str,int]) -> None:
        self.blood_dict = blood_dict
        self.blood_others = blood_others
        self.file_name = file_name
        self.blood_negative = blood_negative


    def create_dataframe(self):
        blood_positive_df = list(self.blood_dict.items())
        blood_others_df = list(self.blood_others.items())
        blood_negative_df = list(self.blood_negative.items())
        blood_positive_df = pd.DataFrame(blood_positive_df,columns=['Organism','Count'])
        blood_others_df = pd.DataFrame(blood_others_df,columns=['Organism','Count'])
        blood_negative_df = pd.DataFrame(blood_negative_df,columns=['Organism','Count'])


        writer = pd.ExcelWriter('POTENTIAL_PATHOGENS_{}.xlsx'.format(self.file_name), engine='xlsxwriter')
        blood_positive_df.to_excel(writer,sheet_name="Blood - Positive Grams",index=False)
        blood_negative_df.to_excel(writer,sheet_name="Blood - Negative Grams", index=False)
        blood_others_df.to_excel(writer,sheet_name="Blood - Other Organism",index=False)
        
        writer.save()
        return writer
