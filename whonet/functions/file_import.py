from whonet.models import *
import pandas as pd
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
import os
from django.db import IntegrityError

dirpath = os.getcwd()

def import_final(raw_data):
    try:
        df = pd.read_csv(raw_data,encoding='iso-8859-1',dtype=str)
    except:
        return 'File ' + raw_data.name + ' is invalid format'

    #File name Model
    # f_names = RawFileName.objects.all()
    tmp_name = raw_data.name

    file_name = FinalFileName(file_name=tmp_name.split('.')[0])
    df = set_pd_columns(df)
    row_iter = df.iterrows()
    try:
        file_name.save()
    except IntegrityError as e:
        file_name = FinalFileName.objects.get(file_name=tmp_name.split('.')[0])
        file_name.updated_at = datetime.now()
        file_name.save()
        FinalOrigin.objects.select_related('finallocation','finalmicrobiology','finalspecimen','finalantidisk','finalantimic','finalantietest').filter(file_ref=file_name).delete()
        import_final_data(row_iter,file_name)
        
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded. System updated the file.'

    try:
        import_final_data(row_iter,file_name)
        return 'File ' + tmp_name.split('.')[0]  +' successfully uploaded.'
     
    except IntegrityError as e:
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded.'



def import_final_data(row_iter,file_name):
    for index, row in  row_iter:

        origin = FinalOrigin(
        
        file_ref = file_name,

        country_a = row['COUNTRY_A'],

        region  = row['REGION'],

        island  = row['ISLAND'],

        laboratory  = row['LABORATORY'],

        patient_id = row['PATIENT_ID'],

        first_name = row['FIRST_NAME'],

        mid_name = row['MID_NAME'],

        last_name = row['LAST_NAME'],

        sex = row['SEX'],

        age = row['AGE'],

        date_birth = row['DATE_BIRTH'],

        age_grp = row['AGE_GRP'],

        pat_type = row['PAT_TYPE'],

        date_data = row['DATE_DATA'],

        x_referred = row['X_REFERRED'],

        x_recnum = row['X_RECNUM'],

        date_admis = row['DATE_ADMIS'],

        nosocomial = row['NOSOCOMIAL'],

        diagnosis = row['DIAGNOSIS'],

        stock_num = row['STOCK_NUM'],

        )

        origin.save()


        loc = FinalLocation(

            origin_ref = origin,

            ward = row['WARD'],

            institut = row['INSTITUT'],

            department = row['DEPARTMENT'],

            ward_type = row['WARD_TYPE'],

        )

        loc.save()
        
        mic = FinalMicrobiology(
            origin_ref = origin,
            
            organism = row['ORGANISM'],
            
            org_type = row['ORG_TYPE'],
            
            beta_lact = row['BETA_LACT'],
            
            comment = row['COMMENT'],
            
            mrsa = row['MRSA'],
            
            induc_cli = row['INDUC_CLI'],
            
            x_meca = row['X_MECA'],
            
            ampc = row['AMPC'],
            
            x_mrse = row['X_MRSE'],
            
            x_carb = row['X_CARB'],
            
            esbl = row['ESBL'],
            
            urine_count = row['URINECOUNT'],
            
            serotype = row['SEROTYPE'],
            
            carbapenem = row['CARBAPENEM'],
            
            mbl = row['MBL'],
            
            growth = row['GROWTH'], 
        )
        
        mic.save()
        
        spec = FinalSpecimen(
            origin_ref = origin,
            
            spec_num = row['SPEC_NUM'],
            
            spec_date = row['SPEC_DATE'],
            
            spec_type = row['SPEC_TYPE'],
            
            spec_code = row['SPEC_CODE'],
            
            local_spec = row['LOCAL_SPEC'],
        )
        
        spec.save()
        
        ant_disk = FinalAntidisk(
            origin_ref = origin,
            
            amk_nd30 = row['AMK_ND30'],
            
            amc_nd20 = row['AMC_ND20'],
            
            amp_nd10 = row['AMP_ND10'],
            
            sam_nd10 = row['SAM_ND10'],
            
            azm_nd15 = row['AZM_ND15'],
            
            atm_nd30 = row['ATM_ND30'],
            
            cec_nd30 = row['CEC_ND30'],
            
            man_nd30 = row['MAN_ND30'],
            
            czo_nd30 = row['CZO_ND30'],
            
            fep_nd30 = row['FEP_ND30'],
            
            cfm_nd5 = row['CFM_ND5'],
            
            cfp_nd75 = row['CFP_ND75'],
            
            ctx_nd30 = row['CTX_ND30'],
            
            fox_nd30 = row['FOX_ND30'],
            
            caz_nd30 = row['CAZ_ND30'],
            
            cro_nd30 = row['CRO_ND30'],
            
            cxm_nd30 = row['CXM_ND30'],
            
            cxa_nd30 = row['CXA_ND30'],
            
            cep_nd30 = row['CEP_ND30'],
            
            chl_nd30 = row['CHL_ND30'],
            
            cip_nd5 = row['CIP_ND5'],
            
            clr_nd15 = row['CLR_ND15'],
            
            cli_nd2 = row['CLI_ND2'],
            
            col_nd10 = row['COL_ND10'],
            
            sxt_nd1_2 = row['SXT_ND1_2'],
            
            dap_nd30 = row['DAP_ND30'],
            
            dor_nd10 = row['DOR_ND10'],
            
            etp_nd10 = row['ETP_ND10'],
            
            ery_nd15 = row['ERY_ND15'],
            
            gen_nd10 = row['GEN_ND10'],
            
            geh_nd120 = row['GEH_ND120'],
            
            ipm_nd10 = row['IPM_ND10'],
            
            kan_nd30 = row['KAN_ND30'],
            
            lvx_nd5 = row['LVX_ND5'],
            
            lnz_nd30 = row['LNZ_ND30'],
            
            mem_nd10 = row['MEM_ND10'],
            
            mno_nd30 = row['MNO_ND30'],
            
            mfx_nd5 = row['MFX_ND5'],
            
            nal_nd30 = row['NAL_ND30'],
            
            net_nd30 = row['NET_ND30'],
            
            nit_nd300 = row['NIT_ND300'],
            
            nor_nd10 = row['NOR_ND10'],
            
            nov_nd5 = row['NOV_ND5'],
            
            ofx_nd5 = row['OFX_ND5'],
            
            oxa_nd1 = row['OXA_ND1'],
            
            pen_nd10 = row['PEN_ND10'],
            
            pip_nd100 = row['PIP_ND100'],
            
            tzp_nd100 = row['TZP_ND100'],
            
            pol_nd300 = row['POL_ND300'],
            
            qda_nd15 = row['QDA_ND15'],
            
            rif_nd5 = row['RIF_ND5'],
            
            spt_nd100 = row['SPT_ND100'],
            
            str_nd10 = row['STR_ND10'],
            
            sth_nd300 = row['STH_ND300'],
            
            tcy_nd30 = row['TCY_ND30'],
            
            tic_nd75 = row['TIC_ND75'],
            
            tcc_nd75 = row['TCC_ND75'],
            
            tgc_nd15 = row['TGC_ND15'],
            
            tob_nd10 = row['TOB_ND10'],
            
            van_nd30 = row['VAN_ND30'],
            
            fos_nd200 = row['FOS_ND200'],
            
            dox_nd30 = row['DOX_ND30'],
            
            sss_nd200 = row['SSS_ND200'],
            
            
            
        )
        
        ant_disk.save()
        
        ant_mic = FinalAntimic(
            origin_ref = origin,
            
            amk_nm = row['AMK_NM'],
            
            amc_nm = row['AMC_NM'],
            
            amp_nm = row['AMP_NM'],
            
            sam_nm = row['SAM_NM'],
            
            azm_nm = row['AZM_NM'],
            
            atm_nm = row['ATM_NM'],
            
            cec_nm = row['CEC_NM'],
            
            man_nm = row['MAN_NM'],
            
            czo_nm = row['CZO_NM'],
            
            fep_nm = row['FEP_NM'],
            
            cfm_nm = row['CFM_NM'],
            
            cfp_nm = row['CFP_NM'],
            
            ctx_nm = row['CTX_NM'],
            
            fox_nm = row['FOX_NM'],
            
            caz_nm = row['CAZ_NM'],
            
            cro_nm = row['CRO_NM'],
            
            cxm_nm = row['CXM_NM'],
            
            cxa_nm = row['CXA_NM'],
            
            cep_nm = row['CEP_NM'],
            
            chl_nm = row['CHL_NM'],
            
            cip_nm = row['CIP_NM'],
            
            clr_nm = row['CLR_NM'],
            
            cli_nm = row['CLI_NM'],
            
            col_nm = row['COL_NM'],
            
            sxt_nm = row['SXT_NM'],
            
            dap_nm = row['DAP_NM'],
            
            dor_nm = row['DOR_NM'],
            
            etp_nm = row['ETP_NM'],
            
            ery_nm = row['ERY_NM'],
            
            gen_nm = row['GEN_NM'],
            
            geh_nm = row['GEH_NM'],
            
            ipm_nm = row['IPM_NM'],
            
            kan_nm = row['KAN_NM'],
            
            lvx_nm = row['LVX_NM'],
            
            lnz_nm = row['LNZ_NM'],
            
            mem_nm = row['MEM_NM'],
            
            mno_nm = row['MNO_NM'],
            
            mfx_nm = row['MFX_NM'],
            
            nal_nm = row['NAL_NM'],
            
            net_nm = row['NET_NM'],
            
            nit_nm = row['NIT_NM'],
            
            nor_nm = row['NOR_NM'],
            
            nov_nm = row['NOV_NM'],
            
            ofx_nm = row['OFX_NM'],
            
            oxa_nm = row['OXA_NM'],
            
            pen_nm = row['PEN_NM'],
            
            pip_nm = row['PIP_NM'],
            
            tzp_nm = row['TZP_NM'],
            
            pol_nm = row['POL_NM'],
            
            qda_nm = row['QDA_NM'],
            
            rif_nm = row['RIF_NM'],
            
            spt_nm = row['SPT_NM'],
            
            str_nm = row['STR_NM'],
            
            sth_nm = row['STH_NM'],
            
            tcy_nm = row['TCY_NM'],
            
            tic_nm = row['TIC_NM'],
            
            tcc_nm = row['TCC_NM'],
            
            tgc_nm = row['TGC_NM'],
            
            tob_nm = row['TOB_NM'],
            
            van_nm = row['VAN_NM'],
            
            fos_nm = row['FOS_NM'],
            
            dox_nm = row['DOX_NM'],
            
            sss_nm = row['SSS_NM'],
        )
        
        ant_mic.save()
        
        ant_est = FinalAntietest(
            origin_ref = origin,
            
            amk_ne = row['AMK_NE'],
            
            amc_ne = row['AMC_NE'],
            
            amp_ne = row['AMP_NE'],
            
            sam_ne = row['SAM_NE'],
            
            azm_ne = row['AZM_NE'],
            
            atm_ne = row['ATM_NE'],
            
            cec_ne = row['CEC_NE'],
            
            man_ne = row['MAN_NE'],
            
            czo_ne = row['CZO_NE'],
            
            fep_ne = row['FEP_NE'],
            
            cfm_ne = row['CFM_NE'],
            
            cfp_ne = row['CFP_NE'],
            
            ctx_ne = row['CTX_NE'],
            
            fox_ne = row['FOX_NE'],
            
            caz_ne = row['CAZ_NE'],
            
            cro_ne = row['CRO_NE'],
            
            cxm_ne = row['CXM_NE'],
            
            cxa_ne = row['CXA_NE'],
            
            cep_ne = row['CEP_NE'],
            
            chl_ne = row['CHL_NE'],
            
            cip_ne = row['CIP_NE'],
            
            clr_ne = row['CLR_NE'],
            
            cli_ne = row['CLI_NE'],
            
            col_ne = row['COL_NE'],
            
            sxt_ne = row['SXT_NE'],
            
            dap_ne = row['DAP_NE'],
            
            dor_ne = row['DOR_NE'],
            
            etp_ne = row['ETP_NE'],
            
            ery_ne = row['ERY_NE'],
            
            gen_ne = row['GEN_NE'],
            
            geh_ne = row['GEH_NE'],
            
            ipm_ne = row['IPM_NE'],
            
            kan_ne = row['KAN_NE'],
            
            lvx_ne = row['LVX_NE'],
            
            lnz_ne = row['LNZ_NE'],
            
            mem_ne = row['MEM_NE'],
            
            mno_ne = row['MNO_NE'],
            
            mfx_ne = row['MFX_NE'],
            
            nal_ne = row['NAL_NE'],
            
            net_ne = row['NET_NE'],
            
            nit_ne = row['NIT_NE'],
            
            nor_ne = row['NOR_NE'],
            
            nov_ne = row['NOV_NE'],
            
            ofx_ne = row['OFX_NE'],
            
            oxa_ne = row['OXA_NE'],
            
            pen_ne = row['PEN_NE'],
            
            pip_ne = row['PIP_NE'],
            
            tzp_ne = row['TZP_NE'],
            
            pol_ne = row['POL_NE'],
            
            qda_ne = row['QDA_NE'],
            
            rif_ne = row['RIF_NE'],
            
            spt_ne = row['SPT_NE'],
            
            str_ne = row['STR_NE'],
            
            sth_ne = row['STH_NE'],
            
            tcy_ne = row['TCY_NE'],
            
            tic_ne = row['TIC_NE'],
            
            tcc_ne = row['TCC_NE'],
            
            tgc_ne = row['TGC_NE'],
            
            tob_ne = row['TOB_NE'],
            
            van_ne = row['VAN_NE'],
            
            fos_ne = row['FOS_NE'],
            
            dox_ne = row['DOX_NE'],
            
            sss_ne = row['SSS_NE'],
        )
        
        ant_est.save()

def set_pd_columns(clm):
    
    whonet_data_fields = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx')
    # whonet_data_fields_etest = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','etest')
    data_fields = whonet_data_fields['Data fields'].values.tolist()
    # etest = whonet_data_fields_etest['Data fields'].values.tolist()
    # etest = [x.lower() for x in etest]
    
    for col in data_fields:
        if col not in clm.columns:
            clm[col] = ''

    
    return clm