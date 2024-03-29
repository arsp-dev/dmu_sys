import pandas as pd
from whonet.models import *
from django.forms import model_to_dict


def concat_all_df(file_id,config = 'raw'):
    if config == 'raw':
        orig = RawOrigin.objects.select_related('rawlocation','rawmicrobiology','rawspecimen','rawantidisk','rawantimic','rawantietest').filter(file_ref=file_id)
        pallobjs = [ model_to_dict(pallobj) for pallobj in RawOrigin.objects.select_related('rawlocation','rawmicrobiology','rawspecimen','rawantidisk','rawantimic','rawantietest').filter(file_ref=file_id)] 
        # objs_spec = [model_to_dict(obj.rawspecimen) for obj in orig]
        objs_spec = [model_to_dict(obj.rawspecimen) for obj in orig]
        objs_location = [model_to_dict(obj.rawlocation) for obj in orig]
        objs_micro = [model_to_dict(obj.rawmicrobiology) for obj in orig]
        objs_dsk = [model_to_dict(obj.rawantidisk) for obj in orig]
        objs_mic = [model_to_dict(obj.rawantimic) for obj in orig]
        objs_etest = [model_to_dict(obj.rawantietest) for obj in orig]
        df = pd.DataFrame(pallobjs)
        df_spec = pd.DataFrame(objs_spec)
        # df_spec.drop(columns=['id'])
        df_loc = pd.DataFrame(objs_location)
        # df_loc.drop(columns=['id'])
        df_micro = pd.DataFrame(objs_micro)
        # df_micro.drop(columns=['id'])
        df_dsk = pd.DataFrame(objs_dsk)
        # df_dsk.drop(columns=['id'])
        df_mic = pd.DataFrame(objs_mic)
        # df_mic.drop(columns=['id'])
        df_etest = pd.DataFrame(objs_etest)
        
        df2 = pd.merge(df_loc,df_spec,on='origin_ref')
        df2 = pd.merge(df2,df_micro,on='origin_ref')
        df2 = pd.merge(df2,df_dsk,on='origin_ref')
        df2 = pd.merge(df2,df_mic,on='origin_ref')
        df2 = pd.merge(df2,df_etest,on='origin_ref')
        # df = pd.merge(df,df2,on='origin_ref')
        # return HttpResponse(df.columns)
        df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    else:
        orig = FinalOrigin.objects.select_related('finallocation','finalmicrobiology','finalspecimen','finalantidisk','finalantimic','finalantietest').filter(file_ref_id=file_id)
        pallobjs = [ model_to_dict(pallobj) for pallobj in FinalOrigin.objects.select_related('finallocation','finalmicrobiology','finalspecimen','finalantidisk','finalantimic','finalantietest').filter(file_ref_id=file_id)] 
        # objs_spec = [model_to_dict(obj.rawspecimen) for obj in orig]
        objs_spec = [model_to_dict(obj.finalspecimen) for obj in orig]
        objs_location = [model_to_dict(obj.finallocation) for obj in orig]
        objs_micro = [model_to_dict(obj.finalmicrobiology) for obj in orig]
        objs_dsk = [model_to_dict(obj.finalantidisk) for obj in orig]
        objs_mic = [model_to_dict(obj.finalantimic) for obj in orig]
        objs_etest = [model_to_dict(obj.finalantietest) for obj in orig]
        df = pd.DataFrame(pallobjs)
        df_spec = pd.DataFrame(objs_spec)
        # df_spec.drop(columns=['id'])
        df_loc = pd.DataFrame(objs_location)
        # df_loc.drop(columns=['id'])
        df_micro = pd.DataFrame(objs_micro)
        # df_micro.drop(columns=['id'])
        df_dsk = pd.DataFrame(objs_dsk)
        # df_dsk.drop(columns=['id'])
        df_mic = pd.DataFrame(objs_mic)
        # df_mic.drop(columns=['id'])
        df_etest = pd.DataFrame(objs_etest)
        
        df2 = pd.merge(df_loc,df_spec,on='origin_ref')
        df2 = pd.merge(df2,df_micro,on='origin_ref')
        df2 = pd.merge(df2,df_dsk,on='origin_ref')
        df2 = pd.merge(df2,df_mic,on='origin_ref')
        df2 = pd.merge(df2,df_etest,on='origin_ref')
        # df = pd.merge(df,df2,on='origin_ref')
        # return HttpResponse(df.columns)
        df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    # df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    # df = pd.concat([df,df2],axis=1,join="inner")
    df = df.replace('nan','')
    # df = df.replace(pd.NaN,'')
    
    # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
    
    df['amk_nd30'] = df['amk_nd30'].str.replace('.0', '', regex=False)
    df['amc_nd20'] = df['amc_nd20'].str.replace('.0', '', regex=False)
    df['amp_nd10'] = df['amp_nd10'].str.replace('.0', '', regex=False)
    df['sam_nd10'] = df['sam_nd10'].str.replace('.0', '', regex=False)
    df['azm_nd15'] = df['azm_nd15'].str.replace('.0', '', regex=False)
    df['atm_nd30'] = df['atm_nd30'].str.replace('.0', '', regex=False)
    df['cec_nd30'] = df['cec_nd30'].str.replace('.0', '', regex=False)
    df['man_nd30'] = df['man_nd30'].str.replace('.0', '', regex=False)
    df['czo_nd30'] = df['czo_nd30'].str.replace('.0', '', regex=False)
    df['fep_nd30'] = df['fep_nd30'].str.replace('.0', '', regex=False)
    df['cfm_nd5'] = df['cfm_nd5'].str.replace('.0', '', regex=False)
    df['cfp_nd75'] = df['cfp_nd75'].str.replace('.0', '', regex=False)
    df['ctx_nd30'] = df['ctx_nd30'].str.replace('.0', '', regex=False)
    df['fox_nd30'] = df['fox_nd30'].str.replace('.0', '', regex=False)
    df['caz_nd30'] = df['caz_nd30'].str.replace('.0', '', regex=False)
    df['cro_nd30'] = df['cro_nd30'].str.replace('.0', '', regex=False)
    df['cxm_nd30'] = df['cxm_nd30'].str.replace('.0', '', regex=False)
    df['cxa_nd30'] = df['cxa_nd30'].str.replace('.0', '', regex=False)
    df['cep_nd30'] = df['cep_nd30'].str.replace('.0', '', regex=False)
    df['chl_nd30'] = df['chl_nd30'].str.replace('.0', '', regex=False)
    df['cip_nd5'] = df['cip_nd5'].str.replace('.0', '', regex=False)
    df['clr_nd15'] = df['clr_nd15'].str.replace('.0', '', regex=False)
    df['cli_nd2'] = df['cli_nd2'].str.replace('.0', '', regex=False)
    df['col_nd10'] = df['col_nd10'].str.replace('.0', '', regex=False)
    df['sxt_nd1_2'] = df['sxt_nd1_2'].str.replace('.0', '', regex=False)
    df['dap_nd30'] = df['dap_nd30'].str.replace('.0', '', regex=False)
    df['dor_nd10'] = df['dor_nd10'].str.replace('.0', '', regex=False)
    df['etp_nd10'] = df['etp_nd10'].str.replace('.0', '', regex=False)
    df['ery_nd15'] = df['ery_nd15'].str.replace('.0', '', regex=False)
    df['gen_nd10'] = df['gen_nd10'].str.replace('.0', '', regex=False)
    df['geh_nd120'] = df['geh_nd120'].str.replace('.0', '', regex=False)
    df['ipm_nd10'] = df['ipm_nd10'].str.replace('.0', '', regex=False)
    df['kan_nd30'] = df['kan_nd30'].str.replace('.0', '', regex=False)
    df['lvx_nd5'] = df['lvx_nd5'].str.replace('.0', '', regex=False)
    df['lnz_nd30'] = df['lnz_nd30'].str.replace('.0', '', regex=False)
    df['mem_nd10'] = df['mem_nd10'].str.replace('.0', '', regex=False)
    df['mno_nd30'] = df['mno_nd30'].str.replace('.0', '', regex=False)
    df['mfx_nd5'] = df['mfx_nd5'].str.replace('.0', '', regex=False)
    df['nal_nd30'] = df['nal_nd30'].str.replace('.0', '', regex=False)
    df['net_nd30'] = df['net_nd30'].str.replace('.0', '', regex=False)
    df['nit_nd300'] = df['nit_nd300'].str.replace('.0', '', regex=False)
    df['nor_nd10'] = df['nor_nd10'].str.replace('.0', '', regex=False)
    df['nov_nd5'] = df['nov_nd5'].str.replace('.0', '', regex=False)
    df['ofx_nd5'] = df['ofx_nd5'].str.replace('.0', '', regex=False)
    df['oxa_nd1'] = df['oxa_nd1'].str.replace('.0', '', regex=False)
    df['pen_nd10'] = df['pen_nd10'].str.replace('.0', '', regex=False)
    df['pip_nd100'] = df['pip_nd100'].str.replace('.0', '', regex=False)
    df['tzp_nd100'] = df['tzp_nd100'].str.replace('.0', '', regex=False)
    df['pol_nd300'] = df['pol_nd300'].str.replace('.0', '', regex=False)
    df['qda_nd15'] = df['qda_nd15'].str.replace('.0', '', regex=False)
    df['rif_nd5'] = df['rif_nd5'].str.replace('.0', '', regex=False)
    df['spt_nd100'] = df['spt_nd100'].str.replace('.0', '', regex=False)
    df['str_nd10'] = df['str_nd10'].str.replace('.0', '', regex=False)
    df['sth_nd300'] = df['sth_nd300'].str.replace('.0', '', regex=False)
    df['tcy_nd30'] = df['tcy_nd30'].str.replace('.0', '', regex=False)
    df['tic_nd75'] = df['tic_nd75'].str.replace('.0', '', regex=False)
    df['tcc_nd75'] = df['tcc_nd75'].str.replace('.0', '', regex=False)
    df['tgc_nd15'] = df['tgc_nd15'].str.replace('.0', '', regex=False)
    df['tob_nd10'] = df['tob_nd10'].str.replace('.0', '', regex=False)
    df['van_nd30'] = df['van_nd30'].str.replace('.0', '', regex=False)
    df['fos_nd200'] = df['fos_nd200'].str.replace('.0', '', regex=False)
    df['dox_nd30'] = df['dox_nd30'].str.replace('.0', '', regex=False)
    df['sss_nd200'] = df['sss_nd200'].str.replace('.0', '', regex=False)
    df['fdc_nd'] = df['fdc_nd'].str.replace('.0', '', regex=False)
    df['cza_nd30'] = df['cza_nd30'].str.replace('.0', '', regex=False)
    df['imr_nd10'] = df['imr_nd10'].str.replace('.0', '', regex=False)
    df['plz_nd'] = df['plz_nd'].str.replace('.0', '', regex=False)
    df['czt_nd30'] = df['czt_nd30'].str.replace('.0', '', regex=False)
    df['mev_nd20'] = df['mev_nd20'].str.replace('.0', '', regex=False)
    df['tzd_nd'] = df['tzd_nd'].str.replace('.0', '', regex=False)
    
      
    df['comment'] = df['comment'].str.replace('/^=/', '', regex=True)

    
    df['spec_num'] = df['spec_num'].str.replace('.0', '', regex=False)
    df['age'] = df['age'].str.replace('.0', '', regex=False)
    df['patient_id'] = df['patient_id'].apply(str)
    df['patient_id'] = df['patient_id'].str.replace('.', '', regex=False)
    
    df['x_referred'] = df['x_referred'].apply(str)
    df['x_referred'] = df['x_referred'].str.replace('.0', '', regex=False)
    
    
    # df['sex'] = df['sex'].apply(str)
    return df



def concat_all_df_referred(file_id):
    orig = ReferredOrigin.objects.select_related('referredlocation','referredmicrobiology','referredspecimen','referredantidisk','referredantimic','referredantidiskris','referredantimicris').filter(file_ref=file_id)
    pallobjs = [ model_to_dict(pallobj) for pallobj in ReferredOrigin.objects.select_related('referredlocation','referredmicrobiology','referredspecimen','referredantidisk','referredantimic','referredantidiskris','referredantimicris').filter(file_ref=file_id)] 
    # objs_spec = [model_to_dict(obj.rawspecimen) for obj in orig]
    objs_spec = [model_to_dict(obj.referredspecimen) for obj in orig]
    objs_location = [model_to_dict(obj.referredlocation) for obj in orig]
    objs_micro = [model_to_dict(obj.referredmicrobiology) for obj in orig]
    objs_dsk = [model_to_dict(obj.referredantidisk) for obj in orig]
    objs_mic = [model_to_dict(obj.referredantimic) for obj in orig]
    # objs_etest = [model_to_dict(obj.referredantietest) for obj in orig]
    objs_dsk_ris = [model_to_dict(obj.referredantidiskris) for obj in orig]
    objs_mic_ris = [model_to_dict(obj.referredantimicris) for obj in orig]
    df = pd.DataFrame(pallobjs)
    df_spec = pd.DataFrame(objs_spec)
    # df_spec.drop(columns=['id'])
    df_loc = pd.DataFrame(objs_location)
    # df_loc.drop(columns=['id'])
    df_micro = pd.DataFrame(objs_micro)
    # df_micro.drop(columns=['id'])
    df_dsk = pd.DataFrame(objs_dsk)
    # df_dsk.drop(columns=['id'])
    df_mic = pd.DataFrame(objs_mic)
    # df_mic.drop(columns=['id'])
    # df_etest = pd.DataFrame(objs_etest)
    
    df_dsk_ris = pd.DataFrame(objs_dsk_ris)
    df_mic_ris = pd.DataFrame(objs_mic_ris)
    
    df2 = pd.merge(df_loc,df_spec,on='origin_ref')
    df2 = pd.merge(df2,df_micro,on='origin_ref')
    df2 = pd.merge(df2,df_dsk,on='origin_ref')
    df2 = pd.merge(df2,df_mic,on='origin_ref')
    # df2 = pd.merge(df2,df_etest,on='origin_ref')
    df2 = pd.merge(df2,df_dsk_ris,on='origin_ref')
    df2 = pd.merge(df2,df_mic_ris,on='origin_ref')
    # df = pd.merge(df,df2,on='origin_ref')
    # return HttpResponse(df.columns)
    df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    # df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    # df = pd.concat([df,df2],axis=1,join="inner")
    df = df.replace('nan','')
    # df = df.replace(pd.NaN,'')
    
    # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
    
    df['amk_nd30'] = df['amk_nd30'].str.replace('.0', '', regex=False)
    df['amc_nd20'] = df['amc_nd20'].str.replace('.0', '', regex=False)
    df['amp_nd10'] = df['amp_nd10'].str.replace('.0', '', regex=False)
    df['sam_nd10'] = df['sam_nd10'].str.replace('.0', '', regex=False)
    df['azm_nd15'] = df['azm_nd15'].str.replace('.0', '', regex=False)
    df['atm_nd30'] = df['atm_nd30'].str.replace('.0', '', regex=False)
    df['cec_nd30'] = df['cec_nd30'].str.replace('.0', '', regex=False)
    df['man_nd30'] = df['man_nd30'].str.replace('.0', '', regex=False)
    df['czo_nd30'] = df['czo_nd30'].str.replace('.0', '', regex=False)
    df['fep_nd30'] = df['fep_nd30'].str.replace('.0', '', regex=False)
    df['cfm_nd5'] = df['cfm_nd5'].str.replace('.0', '', regex=False)
    df['cfp_nd75'] = df['cfp_nd75'].str.replace('.0', '', regex=False)
    df['ctx_nd30'] = df['ctx_nd30'].str.replace('.0', '', regex=False)
    df['fox_nd30'] = df['fox_nd30'].str.replace('.0', '', regex=False)
    df['caz_nd30'] = df['caz_nd30'].str.replace('.0', '', regex=False)
    df['cro_nd30'] = df['cro_nd30'].str.replace('.0', '', regex=False)
    df['cxm_nd30'] = df['cxm_nd30'].str.replace('.0', '', regex=False)
    df['cxa_nd30'] = df['cxa_nd30'].str.replace('.0', '', regex=False)
    df['cep_nd30'] = df['cep_nd30'].str.replace('.0', '', regex=False)
    df['chl_nd30'] = df['chl_nd30'].str.replace('.0', '', regex=False)
    df['cip_nd5'] = df['cip_nd5'].str.replace('.0', '', regex=False)
    df['clr_nd15'] = df['clr_nd15'].str.replace('.0', '', regex=False)
    df['cli_nd2'] = df['cli_nd2'].str.replace('.0', '', regex=False)
    df['col_nd10'] = df['col_nd10'].str.replace('.0', '', regex=False)
    df['sxt_nd1_2'] = df['sxt_nd1_2'].str.replace('.0', '', regex=False)
    df['dap_nd30'] = df['dap_nd30'].str.replace('.0', '', regex=False)
    df['dor_nd10'] = df['dor_nd10'].str.replace('.0', '', regex=False)
    df['etp_nd10'] = df['etp_nd10'].str.replace('.0', '', regex=False)
    df['ery_nd15'] = df['ery_nd15'].str.replace('.0', '', regex=False)
    df['gen_nd10'] = df['gen_nd10'].str.replace('.0', '', regex=False)
    df['geh_nd120'] = df['geh_nd120'].str.replace('.0', '', regex=False)
    df['ipm_nd10'] = df['ipm_nd10'].str.replace('.0', '', regex=False)
    df['kan_nd30'] = df['kan_nd30'].str.replace('.0', '', regex=False)
    df['lvx_nd5'] = df['lvx_nd5'].str.replace('.0', '', regex=False)
    df['lnz_nd30'] = df['lnz_nd30'].str.replace('.0', '', regex=False)
    df['mem_nd10'] = df['mem_nd10'].str.replace('.0', '', regex=False)
    df['mno_nd30'] = df['mno_nd30'].str.replace('.0', '', regex=False)
    df['mfx_nd5'] = df['mfx_nd5'].str.replace('.0', '', regex=False)
    df['nal_nd30'] = df['nal_nd30'].str.replace('.0', '', regex=False)
    df['net_nd30'] = df['net_nd30'].str.replace('.0', '', regex=False)
    df['nit_nd300'] = df['nit_nd300'].str.replace('.0', '', regex=False)
    df['nor_nd10'] = df['nor_nd10'].str.replace('.0', '', regex=False)
    df['nov_nd5'] = df['nov_nd5'].str.replace('.0', '', regex=False)
    df['ofx_nd5'] = df['ofx_nd5'].str.replace('.0', '', regex=False)
    df['oxa_nd1'] = df['oxa_nd1'].str.replace('.0', '', regex=False)
    df['pen_nd10'] = df['pen_nd10'].str.replace('.0', '', regex=False)
    df['pip_nd100'] = df['pip_nd100'].str.replace('.0', '', regex=False)
    df['tzp_nd100'] = df['tzp_nd100'].str.replace('.0', '', regex=False)
    df['pol_nd300'] = df['pol_nd300'].str.replace('.0', '', regex=False)
    df['qda_nd15'] = df['qda_nd15'].str.replace('.0', '', regex=False)
    df['rif_nd5'] = df['rif_nd5'].str.replace('.0', '', regex=False)
    df['spt_nd100'] = df['spt_nd100'].str.replace('.0', '', regex=False)
    df['str_nd10'] = df['str_nd10'].str.replace('.0', '', regex=False)
    df['sth_nd300'] = df['sth_nd300'].str.replace('.0', '', regex=False)
    df['tcy_nd30'] = df['tcy_nd30'].str.replace('.0', '', regex=False)
    df['tic_nd75'] = df['tic_nd75'].str.replace('.0', '', regex=False)
    df['tcc_nd75'] = df['tcc_nd75'].str.replace('.0', '', regex=False)
    df['tgc_nd15'] = df['tgc_nd15'].str.replace('.0', '', regex=False)
    df['tob_nd10'] = df['tob_nd10'].str.replace('.0', '', regex=False)
    df['van_nd30'] = df['van_nd30'].str.replace('.0', '', regex=False)
    df['fos_nd200'] = df['fos_nd200'].str.replace('.0', '', regex=False)
    df['dox_nd30'] = df['dox_nd30'].str.replace('.0', '', regex=False)
    df['sss_nd200'] = df['sss_nd200'].str.replace('.0', '', regex=False)
    df['fdc_nd'] = df['fdc_nd'].str.replace('.0', '', regex=False)
    df['cza_nd30'] = df['cza_nd30'].str.replace('.0', '', regex=False)
    df['imr_nd10'] = df['imr_nd10'].str.replace('.0', '', regex=False)
    df['plz_nd'] = df['plz_nd'].str.replace('.0', '', regex=False)
    df['czt_nd30'] = df['czt_nd30'].str.replace('.0', '', regex=False)
    df['mev_nd20'] = df['mev_nd20'].str.replace('.0', '', regex=False)
    df['tzd_nd'] = df['tzd_nd'].str.replace('.0', '', regex=False)
      
    df['comment'] = df['comment'].str.replace('/^=/', '', regex=True)

    
    df['spec_num'] = df['spec_num'].str.replace('.0', '', regex=False)
    df['age'] = df['age'].str.replace('.0', '', regex=False)
    df['patient_id'] = df['patient_id'].apply(str)
    df['patient_id'] = df['patient_id'].str.replace('.', '', regex=False)
    return df