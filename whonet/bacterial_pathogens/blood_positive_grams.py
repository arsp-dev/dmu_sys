import os
import pandas as pd
from pandas import DataFrame
import operator


class BloodPositive:
    
    def __init__(self,df: DataFrame):
        self.df = df[df['spec_type'] == 'bl']
        self.df_list = self.unique(self.df['organism'].values.tolist())
        self.dirpath = os.getcwd()
        self.blood_gram_positive_organism = pd.read_excel(self.dirpath + '/whonet/static/bacterial_pathogens/blood_gram_positive.xlsx')
        self.org_list = self.blood_gram_positive_organism['ORGANISM'].values.tolist()

    def create_bacterial_pathogens(self):
        x = {}
        for item in self.org_list:
            if len(self.df[self.df['organism'] == item]) > 0:
                x[self.blood_gram_positive_organism['ORG_CLEAN'][self.org_list.index(item)]] = len(self.df[self.df['organism'] == item])
        x = dict(sorted(x.items(),key=operator.itemgetter(1),reverse=True))
        return x 

    def unique(self,list1):
        # insert the list to the set
        list_set = set(list1)
        # convert the set to the list
        unique_list = (list(list_set))
        return unique_list

