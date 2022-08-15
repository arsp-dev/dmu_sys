import os
import pandas as pd
from pandas import DataFrame
import operator


class BloodPositiveOthers:
    
    def __init__(self,df: DataFrame):
        self.df = df[df['spec_type'] == 'bl']
        self.df_list = self.unique(self.df['organism'].values.tolist())
        self.dirpath = os.getcwd()
        self.all_organism = pd.read_excel(self.dirpath + '/whonet/static/bacterial_pathogens/all_organism.xlsx')
        self.org_list = self.all_organism['ORGANISM'].values.tolist()
        self.blood_gram_positive_organism = pd.read_excel(self.dirpath + '/whonet/static/bacterial_pathogens/blood_gram_positive.xlsx')
        self.blood_gram_positive_organism_list = self.blood_gram_positive_organism['ORGANISM'].values.tolist()
        self.blood_gram_negative_organism = pd.read_excel(self.dirpath + '/whonet/static/bacterial_pathogens/all_gram_negative.xlsx')
        self.blood_gram_negative_organism_list = self.blood_gram_negative_organism['ORGANISM'].values.tolist()

    def create_bacterial_pathogens(self):
        x = {}
        self.df_list = set(self.df_list) - set(self.blood_gram_positive_organism_list)
        self.df_list = set(self.df_list) - set(self.blood_gram_negative_organism_list)
        for index,item in enumerate(self.df_list):
            if len(self.df[self.df['organism'] == item]) > 0:
               x[self.all_organism['ORG_CLEAN'][self.org_list.index(item)]] = len(self.df[self.df['organism'] == item])
        x = dict(sorted(x.items(),key=operator.itemgetter(1),reverse=True))
        return x 

    def unique(self,list1):
        # insert the list to the set
        list_set = set(list1)
        # convert the set to the list
        unique_list = (list(list_set))
        return unique_list

