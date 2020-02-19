from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
import pandas as pd
from whonet.models import RawFileName,RawOrigin,RawLocation,RawMicrobiology,RawSpecimen,RawAntidisk,RawAntimic
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.forms import model_to_dict
import re
from django.db import IntegrityError
import multiprocessing as mp
import time


# GET : view for landing page
@login_required(login_url='/arsp_dmu/login')
def whonet_landing(request):
    return render(request, 'whonet/whonet_landing.html')
# end view for landing page


# GET : year for AJAX request TRANSFORM DATA YEARLY
@login_required(login_url='/arsp_dmu/login')
def whonet_transform_sentinel(request,site):
    x = getYear(site)
    return JsonResponse(x, safe=False)
#end


@login_required(login_url='/arsp_dmu/login')
@permission_required('auth.can_clean_create_data_summary_report', raise_exception=True)
def whonet_data_summary(request):
    f_names = RawFileName.objects.all()
    return render(request,'whonet/whonet_data_summary.html',{'f_names': f_names})


@login_required(login_url='/arsp_dmu/login')
@permission_required('auth.can_clean_create_data_summary_report', raise_exception=True)
def whonet_data_summary_report(request,file_id):
    options = request.POST.getlist('options')
    file_name = RawFileName.objects.get(id=file_id)
    search_file_name = file_name.file_name.split('_')
     
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=DATA_SUMMARY_{}_{}.xlsx'.format(file_name,datetime.now()
    )
    
    
    df_data_completeness = get_data_completeness(file_id)
    df_entero = get_data_entero(file_id)
    df_sal_shi = get_data_sal_shi(file_id)
    
    writer = pd.ExcelWriter(response, engine='xlsxwriter')
    df_data_completeness.to_excel(writer, sheet_name='data_complete',index=False)
    df_entero.to_excel(writer, sheet_name='ent_xsal_xshi',index=False)
    df_sal_shi.to_excel(writer, sheet_name='ent_sal_shi', index=False)
    writer.save()
    
    
    
    
    return response


@login_required(login_url='/arsp_dmu/login')
def whonet_transform(request):
    f_names = RawFileName.objects.values_list('file_name', flat=True)
    
    retArray = []
    retYear = []
    
    for ret in f_names:
        retArray.append(ret.split('_')[1])
          
    f_names = list(dict.fromkeys(retArray))
    
    return render(request,'whonet/whonet_transform.html',{'f_names': f_names})


@login_required(login_url='/arsp_dmu/login')
def whonet_transform_year(request):
    site = request.POST['sentinel_site']
    year = request.POST['year']
    options = request.POST.getlist('options')
    #W0119PHL_VSM
    query = year[2:4] + "PHL_" + site
    
    coll = RawFileName.objects.filter(file_name__contains=query)
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={name}.xlsx'.format(
        name=query,
    )
    
    con_df = []
    
    writer = pd.ExcelWriter(response, engine='xlsxwriter')
    
    for val in coll:
        df = bigwork(val.id,val.file_name.split('_'),options)
        con_df.append(df)
        df.to_excel(writer, sheet_name=val.file_name,index=False)
    
    concat_df = pd.concat(con_df)
    
    concat_df.to_excel(writer, sheet_name=site + '_' + year,index=False)
        
    writer.save()
    
    
    return response




@login_required(login_url='/arsp_dmu/login')
def whonet_transform_data(request,file_id):
    options = request.POST.getlist('options')
    file_name = RawFileName.objects.get(id=file_id)
    search_file_name = file_name.file_name.split('_')
    
    df = bigwork(file_id,search_file_name,options)
    
    
    response = HttpResponse( df.to_csv(index=False,mode = 'w'),content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=TRANSFORM_{}_{}.csv".format(file_name,datetime.now())
    
    return response


    
   
# <! --- staff login and logout --- !>
def staff_login(request):
     if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
             if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/arsp_dmu')
        else:
            return render(request, 'whonet/staff_login.html',{'error':'User not found.'})

     else:
        return render(request, 'whonet/staff_login.html')
    

def staff_logout(request):
    logout(request)
    return HttpResponseRedirect('/arsp_dmu/login')
# <! --- end of staff login and logout --!>


@login_required(login_url='/arsp_dmu/login')
@permission_required('whonet.view_rawfilename', raise_exception=True)
def whonet_import_data(request,file_id):
    file_name = RawFileName.objects.get(id=file_id)
    df = concat_all_df(file_id)
    df.columns = map(str.upper, df.columns)

    df = df.drop(columns=['ORIGIN_REF','FILE_REF'])
    
    response = HttpResponse(df.to_csv(index=False,mode = 'w'),content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=RAW_{}_{}.csv".format(file_name,datetime.now())
    return response




@login_required(login_url='/arsp_dmu/login')
@permission_required('whonet.add_rawfilename', raise_exception=True)
def whonet_import(request):
    f_names = RawFileName.objects.all()
    output = mp.Queue()
    
    if request.method == 'POST':
        raw_data = request.FILES.getlist('raw_data')           
        # raw data import
        results = []
        
        for p in raw_data:
            results.append(import_raw(p))
        
    
        return render(request, 'whonet/whonet_import.html',{'multi_import' : results,'f_names': f_names})
    else:
        return render(request, 'whonet/whonet_import.html',{'f_names': f_names})


#helping functions

def set_pd_columns(clm):
    
    whonet_data_fields = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_data_fields.xlsx')
    data_fields = whonet_data_fields['Data fields'].values.tolist()
    # data_fields = [x.lower() for x in data_fields]
    
    for col in data_fields:
        if col not in clm.columns:
            clm[col] = ''
    
    return clm

def getfloat(strx):
    x = ['>','<','<=','>=']
    flt = []
    if strx != '':
        if '<=' in strx:
            q = strx.split('<=')
            flt.append(q[1])
        elif '>=' in strx:
            q = strx.split('>=')
            flt.append(q[1])
        elif '>' in strx:
            q = strx.split('>')
            flt.append(q[1])
        elif '<' in strx:
            q = strx.split('<')
            flt.append(q[1])
        else:
            flt.append(strx)
    
    if len(flt) > 0:
        return flt[0]
    else:
        return strx
    

def spn_def(spn):
    if spn == 'R':
        return ''
    elif spn == 'S':
        return 'S'
    elif float(spn) >= 20:
        return 'S'
    else:
        return ''


def getYear(site):
    #W0119PHL_VSM
    x = RawFileName.objects.filter(file_name__contains=site)
    ret = []
    for y in x:
        q = y.file_name.split('_')
        g = q[0]
        ret.append('20'+ g[3:5])
    
    ret_yr = list(dict.fromkeys(ret))
    
    return ret_yr
    
    
        


def bigwork(file_id,search_file_name,options):
  
    df = concat_all_df(file_id)
    #removing rows if x_referred == 1
    if 'X_REFERRED' in options:
        df = df[df['x_referred'] != 1]


    whonet_region_island = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_region_island.xlsx')
    whonet_organism = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_organism.xlsx')
    whonet_specimen = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_specimen.xlsx')
    whonet_site_location = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_codes_location.xlsx',search_file_name[1])
    whonet_data_fields = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_data_fields.xlsx')
    
    # return HttpResponse(whonet_site_location)
    
    lab_chk = whonet_region_island['LABORATORY'].values.tolist()
    org_chk = whonet_organism['ORGANISM'].values.tolist()
    spec_chk = whonet_specimen['SPEC_TYPE'].values.tolist()
    loc_chk = whonet_site_location['WARD'].values.tolist()
    data_fields = whonet_data_fields['Data fields'].values.tolist()
    loc_chk = [x.lower() for x in loc_chk]
    
    region = []
    island = []
    age = []
    new_org = []
    new_org_type = []
    new_spec_type = []
    new_spec_code = []
    
    new_institut = []
    new_department = []
    new_ward_type = []
    
    new_diag = []
    
    new_noso = []
    
    new_mrsa = []
    
    new_pen = []
    new_oxa = []
    
    new_country = []
    new_lab = []
    
    x_growth = []
    
    
    #removing nan strings
    # df = df.replace(regex='nan',value='')
    
    for index,row in df.iterrows():
        new_country.append('PHL')
        new_lab.append(search_file_name[1])
    df['country_a'] = new_country
    df['laboratory'] = new_lab
    
    for index,row in df.iterrows():
        
        if 'growth' in row['comment'].lower():
            x_growth.append(row['comment'])
        else:
            x_growth.append('')
        
        
        if 'Diagnosis' in options:
            if 'dx:' in row['comment']:
                x = row['comment'].split('dx:')
                new_diag.append(x[1].lstrip())
            elif 'dx : ' in row['comment']:
                x = row['comment'].split('dx : ')
                new_diag.append(x[1].lstrip())
            elif 'dX;' in row['comment']:
                x = row['comment'].split('dX;')
                new_diag.append(x[1].lstrip())
            elif 'dx;' in row['comment']:
                x = row['comment'].split('dx;')
                new_diag.append(x[1].lstrip())
            elif 'Dx:' in row['comment']:
                x = row['comment'].split('Dx:')
                new_diag.append(x[1].lstrip())
            elif 'FINAL REPORT:' in row['comment']:
                 x = row['comment'].split('FINAL REPORT:')
                 new_diag.append(x[1].lstrip())
            elif 'final report:' in row['comment']:
                 x = row['comment'].split('final report:')
                 new_diag.append(x[1].lstrip())
            else:
                new_diag.append(row['comment'].lstrip())
        
        
        if 'Location' in options:
            if row['ward'] in loc_chk:
                new_institut.append(whonet_site_location['INSTITUT'][loc_chk.index(row['ward'])])
                new_department.append(whonet_site_location['DEPARTMENT'][loc_chk.index(row['ward'])])
                new_ward_type.append(whonet_site_location['WARD_TYPE'][loc_chk.index(row['ward'])])
            else:
                new_institut.append('unknown')
                new_department.append('unknown')
                new_ward_type.append('unknown')
        
        
        if 'Specimen' in options:
            if row['spec_type'] in spec_chk:
                x = whonet_specimen['SPEC_ARS'][spec_chk.index(row['spec_type'])]
                new_spec_type.append(x)
                new_spec_code.append(whonet_specimen['SPEC_CODE'][spec_chk.index(x)])
            else:
                new_spec_type.append('un')
                new_spec_code.append('98')
            
            if row['organism'] in org_chk:
                new_org.append(whonet_organism['ORG_ARS'][org_chk.index(row['organism'])])
                new_org_type.append(whonet_organism['GRAM'][org_chk.index(row['organism'])])
            else:
                new_org.append('unk')
                new_org_type.append('o')
        
        
        if 'Origin' in options:
            if row['laboratory'].upper() in lab_chk:
                region.append(whonet_region_island['REGION'][lab_chk.index(row['laboratory'])])
                island.append(whonet_region_island['ISLAND'][lab_chk.index(row['laboratory'])])
            else:
                region.append('')
                island.append('')
        
                
            if pd.isna(row['age']) == True or row['age'] == '':
                    age.append('U')
                
            elif 'w' in str(row['age']) or 'W' in str(row['age']) or 'd' in str(row['age']) or 'D' in str(row['age']) or 'm' in str(row['age']) or 'M' in str(row['age']) or 'nb' in str(row['age']) or 'NB' in str(row['age']):
                
                    age.append('A')
            elif row['age'] == 'nan':
                    age.append('U')  
                
            elif int(row['age']) >= 0 and int(row['age']) <= 5:
                    age.append('A')
                
            elif int(row['age']) >= 6 and int(row['age']) <= 17:
                    age.append('B')
                
            elif int(row['age']) > 17 and int(row['age']) <= 64:
                    age.append('C')
                
            elif int(row['age']) > 64:
                    age.append('D')
                
            else:
                    age.append('U')  
        
        
        if 'SPN' in options:
            if row['organism'] == 'spn' and row['spec_type'] != 'qc':
                if row['pen_nd10'] != '' and row['oxa_nd1'] != '':
                    new_pen.append(spn_def(getfloat(row['pen_nd10'])))
                    new_oxa.append(row['pen_nd10'])
                elif row['pen_nd10'] == '' and row['oxa_nd1'] != '':
                    new_pen.append(spn_def(getfloat(row['oxa_nd1'])))
                    new_oxa.append(row['oxa_nd1'])
                else:
                    new_pen.append('')
                    new_oxa.append('')
            else:
                if row['spec_type'] != 'qc':
                    new_pen.append('')
                    new_oxa.append('')
                else:
                    new_pen.append(row['pen_nd10'])
                    new_oxa.append(row['oxa_nd1'])
        
    
 
    if 'Origin' in options:
        df['region'] = region
        df['island'] = island
        df['age_grp'] = age
    
    if 'Specimen' in options:
        df['organism'] = new_org
        df['org_type'] = new_org_type
        df['spec_type'] = new_spec_type
        df['spec_code'] = new_spec_code
    
    if 'Location' in options:
        new_institut = [x.upper() for x in new_institut]
        df['institut'] = new_institut
        df['department'] = new_department
        df['ward_type'] = new_ward_type
    
    if 'Diagnosis' in options:
        df['diagnosis'] = new_diag
    
    if 'SPN' in options:
        df['pen_nd10'] = new_pen
        df['oxa_nd1'] = new_oxa
    
     
    xx_ward = []
    xx_ward_type = []
    xx_institut = []
    xx_dept = []
       
    for index,row in df.iterrows():
        if 'MRSA' in options:
            if row['organism'] == 'sau':
                if row['fox_nd30'] == 'R' or row['oxa_nm'] == 'R' or row['fox_nm'] == 'R':
                    new_mrsa.append('+')
                elif row['fox_nd30'] == 'S' or row['oxa_nm'] == 'S' or row['fox_nm'] == 'S':
                    new_mrsa.append('-')
                elif ( row['fox_nd30'] != '' and float(getfloat(row['fox_nd30'])) <= 21) or (row['oxa_nm'] != '' and float(getfloat(row['oxa_nm'])) >= 4)  or (row['fox_nm'] != '' and float(getfloat(row['fox_nm'])) >= 8):
                    new_mrsa.append('+')
                elif (row['fox_nd30'] != '' and float(getfloat(row['fox_nd30'])) >= 22) or (row['oxa_nm'] != '' and float(getfloat(row['oxa_nm'])) <= 2) or (row['fox_nm'] != ''and float(getfloat(row['fox_nm'])) <= 4):
                    new_mrsa.append('-')
                else:
                    new_mrsa.append('') 
            else:
                new_mrsa.append('')
        
        
        
        if 'Nosocomial' in options:
                if row['ward_type'] == 'in' or row['ward_type'] == 'eme':
                    if row['date_admis'] != '':
                        x = datetime.strptime(row['spec_date'],'%m/%d/%Y') - datetime.strptime(row['date_admis'],'%m/%d/%Y')
                        if x.days > 2:
                            new_noso.append('Y')
                        else:
                            new_noso.append('N')
                    else:
                        new_noso.append('X')
                elif row['ward_type'] == 'out':
                    new_noso.append('O')
                else:
                    new_noso.append('UNK')
        
        if 'qc' in row['spec_type'].lower():
            xx_ward.append('atc')
            # xx_institut.append(row['institut'])
            xx_dept.append('lab')
            xx_ward_type.append('lab')
        else:
            xx_ward.append(row['ward'])
            xx_dept.append(row['department'])
            xx_ward_type.append(row['ward_type'])
        
    
    df['ward'] = xx_ward
    df['department'] = xx_dept
    df['ward_type'] = xx_ward_type    
    
    if 'MRSA' in options:
        df['mrsa'] = new_mrsa
    
    if 'Nosocomial' in options:
        df['nosocomial'] = new_noso
    
    
    

    
    
    df['growth'] = x_growth
    #df columns to upper
    df.columns = map(str.upper, df.columns)
    
    
    #removing excess columns
    # df = df.drop(columns=['ID_X', 'ID_Y','ORIGIN_REF','FILE_REF','ID'])
    df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID'])

    df = df.reindex(columns = data_fields)
    return df


def import_raw(raw_data):
    try:
        df = pd.read_csv(raw_data,encoding='iso-8859-1')
        
    except:
        return 'File ' + raw_data.name + ' is invalid format'
        # output.put('File ' + raw_data.name + ' is invalid format')
        # time.sleep(0.1)
        # return render(request,'whonet/whonet_import.html',{'danger':'Invalid file format. Please upload WHONET output file.'})

    #File name Model
    # f_names = RawFileName.objects.all()
    tmp_name = raw_data.name

    file_name = RawFileName(file_name=tmp_name.split('.')[0])
    try:
        file_name.save()
    except IntegrityError as e:
        # output.put('File ' + tmp_name.split('.')[0] + ' is already uploaded.')
        # time.sleep(0.1)
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded.'
            # return render(request,'whonet/whonet_import.html',{'danger':e.args,'f_names': f_names})

    df = set_pd_columns(df)
    row_iter = df.iterrows()

    try:
        for index, row in  row_iter:

            origin = RawOrigin(
            
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


            loc = RawLocation(

                origin_ref = origin,

                ward = row['WARD'],

                institut = row['INSTITUT'],

                department = row['DEPARTMENT'],

                ward_type = row['WARD_TYPE'],

            )

            loc.save()
            
            mic = RawMicrobiology(
                origin_ref = origin,
                
                organism = row['ORGANISM'],
                
                org_type = row['ORG_TYPE'],
                
                beta_lact = row['BETA_LACT'],
                
                comment = row['COMMENT'],
                
                mrsa = row['MRSA'],
                
                induc_cli = row['INDUC_CLI'],
                
                meca = row['MECA'],
                
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
            
            spec = RawSpecimen(
                origin_ref = origin,
                
                spec_num = row['SPEC_NUM'],
                
                spec_date = row['SPEC_DATE'],
                
                spec_type = row['SPEC_TYPE'],
                
                spec_code = row['SPEC_CODE'],
                
                local_spec = row['LOCAL_SPEC'],
            )
            
            spec.save()
            
            ant_disk = RawAntidisk(
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
                
            )
            
            ant_disk.save()
            
            ant_mic = RawAntimic(
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
                
                van_nm = row['VAN_NM']
            )
            
            ant_mic.save()
            
        # return render(request,'whonet/whonet_import.html',{'success':'File '+ tmp_name.split('.')[0]  +' successfully uploaded.','f_names': f_names})
        return 'File ' + tmp_name.split('.')[0]  +' successfully uploaded.'
        # output.put('File ' + tmp_name.split('.')[0]  +' successfully uploaded.')
        # time.sleep(0.1)
    except IntegrityError as e:
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded.'
        # output.put('File ' + tmp_name.split('.')[0] + ' is already uploaded.')
        # time.sleep(0.1)
            # return render(request,'whonet/whonet_import.html',{'danger':e.message,'f_names': f_names})  


def concat_all_df(file_id):
    orig = RawOrigin.objects.select_related('rawlocation','rawmicrobiology','rawspecimen','rawantidisk','rawantimic').filter(file_ref=file_id)
    pallobjs = [ model_to_dict(pallobj) for pallobj in RawOrigin.objects.select_related('rawlocation','rawmicrobiology','rawspecimen','rawantidisk','rawantimic').filter(file_ref=file_id)] 
    objs_spec = [model_to_dict(obj.rawspecimen) for obj in orig]
    objs_location = [model_to_dict(obj.rawlocation) for obj in orig]
    objs_micro = [model_to_dict(obj.rawmicrobiology) for obj in orig]
    objs_dsk = [model_to_dict(obj.rawantidisk) for obj in orig]
    objs_mic = [model_to_dict(obj.rawantimic) for obj in orig]
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
    
    df2 = pd.merge(df_loc,df_spec,on='origin_ref')
    df2 = pd.merge(df2,df_micro,on='origin_ref')
    df2 = pd.merge(df2,df_dsk,on='origin_ref')
    df2 = pd.merge(df2,df_mic,on='origin_ref')
    # df = pd.merge(df,df2,on='origin_ref')
    # return HttpResponse(df.columns)
    df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    # df = pd.merge(df,df2,right_on='origin_ref',left_on='id')
    # df = pd.concat([df,df2],axis=1,join="inner")
    df = df.replace('nan','')
    # df = df.replace(pd.NaN,'')
    
    # df = df.drop(columns=['ORIGIN_REF','FILE_REF','ID'])
    
    return df

def get_data_completeness(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    

    totalDf = len(df)
    
    xId = len(df[df['patient_id'] != ''])
    xLn = len(df[df['last_name'] != ''])
    xSe = len(df[df['sex'] != ''])
    xAg = len(df[ df['age'] != '' ])
    xDb = len(df[ df['date_birth'] != '' ])
    xLo = len(df[ df['ward'] != '' ])
    xDe = len(df[ df['department'] != '' ])
    xWt = len(df[ df['ward_type'] != '' ])
    xSp = len(df[ df['spec_num'] != '' ])
    xSd = len(df[ df['spec_date'] != '' ])
    xSt = len(df[ df['spec_type'] != '' ])
    xOr = len(df[ df['organism'] != '' ])
    xDa = len(df[ (df['date_admis'] != '') & (df['ward_type'] == 'in') ])
    # xDa = len(df[df['date_admis'] != '' ])
    xIn = len(df[ df['ward_type'] == 'in' ])
    xDi = len(df[ df['diagnosis'] != '' ])
        
    
    yData = [['','Number','Percentage'],
               ['1. Identification number',xId,str( round(((xId)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['2. Name (Last name)',xLn,str( round(((xLn)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['3. Sex',xSe,str( round(((xSe)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['4. Age',xAg,str( round(((xAg)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['5. Date of birth',xDb,str( round(((xDb)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['6. Location/Ward',xLo,str( round(((xLo)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['7. Department',xDe,str( round(((xDe)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['8. Ward type',xWt,str( round(((xWt)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['9. Specimen number',xSp,str( round(((xSp)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['10. Specimen date',xSd,str( round(((xSd)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['11. Specimen type',xSt,str( round(((xSt)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['12. Organism',xOr,str( round(((xOr)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ['13. Date of admission (total inpatient)',str(xDa) + " (" + str(xIn) +")",str( round(((xDa)/(xIn))*100,2) ) + "%" if totalDf > 0 and xIn > 0 else '0%'],
               ['14. Diagnosis',xDi,str( round(((xDi)/(totalDf))*100,2) ) + '%' if totalDf > 0 else '0%'],
               ]

    df = pd.DataFrame(data=yData, columns=['Completeness of data','Number',totalDf])
    
    return df


def get_data_entero(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_org_list.xlsx','entero')
    df_list = pd.DataFrame(comp, columns=['ORG'])
    
    cmp = df_list.to_numpy()
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    
    ess_amk = 0
    ess_amc = 0
    ess_amp = 0
    ess_atm = 0
    ess_czo = 0
    ess_fep = 0
    ess_ctx = 0
    ess_fox = 0
    ess_caz = 0
    ess_cro = 0
    ess_cxa = 0
    ess_cip = 0
    ess_etp = 0
    ess_gen = 0
    ess_ipm = 0
    ess_mem = 0
    ess_tzp = 0
    ess_sxt = 0
    ess_fos = 0
    ess_nit = 0
    ess_col = 0
    ess_all = 0
    ess_ur = 0
    
    for index,row in df.iterrows():
        if row['organism'] in cmp:
            ess_all += 1
            if row['amk_nd30'] != '' or row['amk_nm'] != '':
                ess_amk += 1
            if row['amc_nd20'] != '' or row['amc_nm'] != '':
                ess_amc += 1
            if row['amp_nd10'] != '' or row['amp_nm'] != '':
                ess_amp += 1
            if row['atm_nd30'] != '' or row['atm_nm'] != '':
                ess_atm += 1
            if row['czo_nd30'] != '' or row['czo_nm'] != '':
                ess_czo += 1
            if row['fep_nd30'] != '' or row['fep_nm'] != '':
                ess_fep += 1
            if row['ctx_nd30'] != '' or row['ctx_nm'] != '':
                ess_ctx += 1
            if row['fox_nd30'] != '' or row['fox_nm'] != '':
                ess_fox += 1
            if row['caz_nd30'] != '' or row['caz_nm'] != '':
                ess_caz += 1
            if row['cro_nd30'] != '' or row['cro_nm'] != '':
                ess_cro += 1
            if row['cxa_nd30'] != '' or row['cxa_nm'] != '':
                ess_cxa += 1
            if row['cip_nd5'] != '' or row['cip_nm'] != '':
                ess_cip += 1
            if row['etp_nd10'] != '' or row['etp_nm'] != '':
                ess_etp += 1
            if row['gen_nd10'] != '' or row['gen_nm'] != '':
                ess_gen += 1
            if row['ipm_nd10'] != '' or row['ipm_nm'] != '':
                ess_ipm += 1
            if row['mem_nd10'] != '' or row['mem_nm'] != '':
                ess_mem += 1
            if row['tzp_nd100'] != '' or row['tzp_nm'] != '':
                ess_tzp += 1
            if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                ess_sxt += 1
            if row['spec_type'] == 'ur':
                ess_ur += 1
            if (row['fos_nd200'] != '' or row['fos_nm'] != '') and (row['spec_type'] == 'ur'):
                ess_fos += 1
            if (row['nit_nd300'] != '' or row['nit_nm'] != '') and (row['spec_type'] == 'ur'):
                ess_nit += 1
            if row['col_nd10'] != '' or row['col_nm'] != '':
                ess_col += 1
            
            
    ess_data_ent = [['Antibiotic','Number tested','Percentage'],
                   ['1. Amikacin',ess_amk,str(  round(((ess_amk)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['2. Amoxicillin-Clavulanate',ess_amc, str(  round(((ess_amc)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['3. Ampicillin',ess_amp,str(  round(((ess_amp)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['4. Aztreonam',ess_atm,str(  round(((ess_atm)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['5. Cefazolin',ess_czo,str(  round(((ess_czo)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['6. Cefepime',ess_fep,str(  round(((ess_fep)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['7. Cefotaxime',ess_ctx,str(  round(((ess_ctx)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['8. Cefoxitin',ess_fox,str(  round(((ess_fox)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['9. Ceftazidime',ess_caz,str(  round(((ess_caz)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['10. Ceftriaxone',ess_cro,str(  round(((ess_cro)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['11. Cefuroxime',ess_cxa,str(  round(((ess_cxa)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['12. Ciprofloxacin',ess_cip,str(  round(((ess_cip)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['13. Ertapenem',ess_etp,str(  round(((ess_etp)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['14. Gentamicin',ess_gen,str(  round(((ess_gen)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['15. Imipenem',ess_ipm,str(  round(((ess_ipm)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['16. Meropenem',ess_mem,str(  round(((ess_mem)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['17. Piperacillin-tazobactam',ess_tzp,str(  round(((ess_tzp)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['18. Trimethoprim-sulfamethoxazole',ess_sxt,str(  round(((ess_sxt)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['19. Colistin',ess_col,str(  round(((ess_col)/(ess_all))*100,2) ) + "%" if ess_all > 0 else '0%'],
                   ['','Additional for Urine',ess_ur],
                   ['1. Fosfomycin',ess_fos,str(  round(((ess_fos)/(ess_ur))*100,2) ) + "%" if ess_ur > 0 else '0%'],
                   ['2. Nitrofurantoin',ess_nit,str(  round(((ess_nit)/(ess_ur))*100,2) ) + "%" if ess_ur > 0 else '0%']]
              
    
    df = pd.DataFrame(data=ess_data_ent, columns=['ENTEROBACTERIACEAE','Number',ess_all])  
    
    return df


def get_data_non_ent(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_org_list.xlsx','non_ent')
    df_list = pd.DataFrame(comp, columns=['ORG'])
    
    cmp = df_list.to_numpy()
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    
    
    non_ent_all = 0
    non_ent_amk = 0
    non_ent_sam = 0
    non_ent_fep = 0
    non_ent_caz = 0
    non_ent_cip = 0
    non_ent_col = 0
    non_ent_ipm = 0
    non_ent_mem = 0
    non_ent_mno = 0
    non_ent_gen = 0
    non_ent_tzp = 0
    non_ent_sxt = 0
    non_ent_tet = 0
    non_ent_ur = 0 
    
    for index,row in df.iterrows():
            if row['organism'] in cmp:
                  non_ent_all += 1
                  if row['amk_nd30'] != '' or row['amk_nm'] != '':
                        non_ent_amk += 1
                  if row['sam_nd10'] != '' or row['sam_nm'] != '':
                        non_ent_sam += 1
                  if row['fep_nd30'] != '' or row['fep_nm'] != '':
                        non_ent_fep += 1
                  if row['caz_nd30'] != '' or row['caz_nm'] != '':
                        non_ent_caz += 1
                  if row['cip_nd5'] != '' or row['cip_nm'] != '':
                        non_ent_cip += 1
                  if row['col_nd10'] != '' or row['col_nm'] != '':
                        non_ent_col += 1
                  if row['ipm_nd10'] != '' or row['ipm_nm'] != '':
                        non_ent_ipm += 1
                  if row['mem_nd10'] != '' or row['mem_nm'] != '':
                        non_ent_mem += 1
                  if row['mno_nd30'] != '' or row['mno_nm'] != '':
                        non_ent_mno += 1
                  if row['gen_nd10'] != '' or row['gen_nm'] != '':
                        non_ent_gen += 1
                  if row['tzp_nd100'] != '' or row['tzp_nm'] != '':
                        non_ent_tzp += 1
                  if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                        non_ent_sxt += 1
                  if row['tcy_nd30'] != '' and row['spec_type'] == 'ur':
                        non_ent_tet += 1
                  if row['spec_type'] == 'ur':
                        non_ent_ur += 1
    
    non_ent_data = [['Antibiotic','Number tested','Percentage'],
                      ['1. Amikacin',non_ent_amk,str(  round(((non_ent_amk)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['2. Amipicillin-Sulbactam',non_ent_sam,str(  round(((non_ent_sam)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['3. Cefepime',non_ent_fep,str(  round(((non_ent_fep)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['4. Ceftazidime',non_ent_caz,str(  round(((non_ent_caz)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['5. Ciprofloxacin',non_ent_cip,str(  round(((non_ent_cip)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['6. Colistin',non_ent_col,str(  round(((non_ent_col)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['7. Imipenem',non_ent_ipm,str(  round(((non_ent_ipm)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['8. Meropenem',non_ent_mem,str(  round(((non_ent_mem)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['9. Minocycline',non_ent_mno,str(  round(((non_ent_mno)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['10. Gentamicin',non_ent_gen,str(  round(((non_ent_gen)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['11. Piperacillin-tazobactam',non_ent_tzp,str(  round(((non_ent_tzp)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['12. Trimethoprim-Sulfamethoxazole',non_ent_sxt,str(  round(((non_ent_sxt)/(non_ent_all))*100,2) ) + "%" if non_ent_all > 0 else '0%'],
                      ['','Additional for Urine',non_ent_ur],
                      ['1. Tetracycline',non_ent_tet,str(  round(((non_ent_tet)/(non_ent_ur))*100,2) ) + "%" if non_ent_ur > 0 else '0%']
                      ]
    
    
    df = pd.DataFrame(data=non_ent_data, columns=['Acinetobacter sp.','Number', non_ent_all])
    
    return df



def get_data_sal_shi(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_org_list.xlsx','sal_shi')
    comp_add = pd.read_excel('D:\PROJECT\dmu_sys\whonet\static\whonet_xl\whonet_org_list.xlsx','sal_shi_add')
    df_list = pd.DataFrame(comp, columns=['ORG'])
    df_list_add = pd.DataFrame(comp_add, columns=['ORG'])
    
    cmp = df_list.to_numpy()
    cmp_add = df_list_add.to_numpy()
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]


    ent_amc = 0
    ent_amp = 0
    ent_atm = 0
    ent_fep = 0
    ent_ctx = 0
    ent_fox = 0
    ent_cro = 0
    ent_chl = 0
    ent_cip = 0
    ent_etp = 0
    ent_ipm = 0
    ent_sxt = 0
    ent_azm = 0
    ent_azm_all = 0
    ent_all = 0
    
    for index,row in df.iterrows():
             if row['organism'] in cmp:
                  ent_all += 1
                  if row['amc_nd20'] != '' or row['amc_nm'] != '':
                        ent_amc += 1
                  if row['amp_nd10'] != '' or row['amp_nm'] != '':
                        ent_amp += 1
                  if row['atm_nd30'] != '' or row['atm_nm'] != '':
                        ent_atm += 1
                  if row['fep_nd30'] != '' or row['fep_nm'] != '':
                        ent_fep += 1
                  if row['ctx_nd30'] != '' or row['ctx_nm'] != '':
                        ent_ctx += 1
                  if row['fox_nd30'] != '' or row['fox_nm'] != '':
                        ent_fox += 1
                  if row['cro_nd30'] != '' or row['cro_nm'] != '':
                        ent_cro += 1
                  if row['chl_nd30'] != '' or row['chl_nm'] != '':
                        ent_chl += 1
                  if row['cip_nd5'] != '' or row['cip_nm'] != '':
                        ent_cip += 1
                  if row['etp_nd10'] != '' or row['etp_nm'] != '':
                        ent_etp += 1
                  if row['ipm_nd10'] != '' or row['ipm_nm'] != '':
                        ent_ipm += 1
                  if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                        ent_sxt += 1
    
    for index,row in df.iterrows():
            if row['organism'] in cmp_add:
                  ent_azm_all += 1
                  if row['azm_nd15'] != '' or row['azm_nm']:
                        ent_azm += 1
    
    ent_data_sal_shi = [['Antibiotic','Number tested','Percentage'],
                          ['1. Amoxicillin-Clavulanate',ent_amc, str(  round(((ent_amc)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['2. Ampicillin',ent_amp,str(  round(((ent_amp)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['3. Aztreonam',ent_atm,str(  round(((ent_atm)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['4. Cefepime',ent_fep,str(  round(((ent_fep)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['5. Cefotaxime',ent_ctx,str(  round(((ent_ctx)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['6. Cefoxitin',ent_fox,str(  round(((ent_fox)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['7. Ceftriaxone',ent_cro,str(  round(((ent_cro)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['8. Chloramphenicol',ent_chl,str(  round(((ent_chl)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['9. Ciprofloxacin',ent_cip,str(  round(((ent_cip)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['10. Ertapenem',ent_etp,str(  round(((ent_etp)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['11. Imipenem',ent_ipm,str(  round(((ent_ipm)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['12. Trimethoprim-sulfamethoxazole',ent_sxt,str(  round(((ent_sxt)/(ent_all))*100,2) ) + "%" if ent_all > 0 else '0%'],
                          ['','Additional Antibiotics',''],
                          ['1. Azithromycin',ent_azm,str(  round(((ent_azm)/(ent_azm_all))*100,2) ) + "%" if ent_azm_all > 0 else '0%']
                          ]

    
    df = pd.DataFrame(data=ent_data_sal_shi, columns=['Salmonella & Shigella sp.','Number',ent_all])
    
    
    return df
    