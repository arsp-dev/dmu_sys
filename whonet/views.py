from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
import pandas as pd
from whonet.models import *
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
import os
import zipfile
# import datetime


dirpath = os.getcwd()
whonet_region_island = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_region_island.xlsx')
whonet_organism = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_organism.xlsx')
whonet_specimen = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_specimen.xlsx')
whonet_data_fields = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx')
whonet_data_fields_mic = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','mic')
whonet_data_fields_etest = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','etest')
comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/org_all.xlsx')
spec_type = pd.read_excel(dirpath + '/whonet/static/whonet_xl/specimen_type.xlsx')
spn = pd.DataFrame(spec_type, columns=['C_ENGLISH'])
org = pd.DataFrame(comp,columns=['ORG'])
org_list = org.to_numpy()
spec_list = spn.to_numpy()
lab_chk = whonet_region_island['LABORATORY'].values.tolist()
org_chk = whonet_organism['ORGANISM'].values.tolist()
spec_chk = whonet_specimen['SPEC_TYPE'].values.tolist()
data_fields = whonet_data_fields['Data fields'].values.tolist()
data_fields_mic = whonet_data_fields_mic['Data fields'].values.tolist()
data_fields_etest = whonet_data_fields_etest['Data fields'].values.tolist()

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
     

    response = HttpResponse(content_type='application/zip')
    zf = zipfile.ZipFile(response, 'w')
    
    summary_report = compute_summary_report(file_name,file_id)
    summary_review = xl_for_review(file_id,file_name.file_name,getYearInt(file_name.file_name))
    
    zf.write(summary_report)
    zf.write(summary_review)
    
    zf.close()
    
    
    response['Content-Disposition'] = 'attachment; filename=SUMMARY_REPORT_{}.zip'.format(file_name)
    
    os.remove('DATA_SUMMARY_{}.xlsx'.format(file_name))
    os.remove('SUMMARY_FOR_REVIEW_{}.xlsx'.format(file_name))
    return response






@login_required(login_url='/arsp_dmu/login')
def whonet_transform(request):
    f_names = RawFileName.objects.values_list('file_name', flat=True)
    
    retArray = []
    retYear = []
    
    for ret in f_names:
        retArray.append(ret.split('_')[1])
          
    f_names = list(dict.fromkeys(retArray))
    f_names.sort()
    
    return render(request,'whonet/whonet_transform.html',{'f_names': f_names})


@login_required(login_url='/arsp_dmu/login')
def whonet_transform_year(request):
    start_time = datetime.now() 
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
    tmp_year_df = []
    
    writer = pd.ExcelWriter(response, engine='xlsxwriter')
    
    for val in coll:
        df = bigwork(val.id,val.file_name.split('_'),options)
        tmp_year_df.append(df)
        df['SPEC_DATE'] = pd.to_datetime(df['SPEC_DATE'],errors='ignore')
        df = df[df['SPEC_DATE'].dt.year == int(year)]
        df =  df[df['SPEC_DATE'] != '']
        con_df.append(df)
        df.to_excel(writer, sheet_name=val.file_name,index=False)
        
    concat_df = pd.concat(con_df)
    tmp_df  = pd.concat(tmp_year_df)
    
    crt_year = tmp_df
    tmp_year = []
    if 'CORRECT_YEAR' in options:
        crt_year['SPEC_DATE'] = pd.to_datetime(crt_year['SPEC_DATE'],errors='ignore')
        tmp_year.append(crt_year[crt_year['SPEC_DATE'].dt.year != int(year) ])
        tmp_year.append(crt_year[(crt_year['SPEC_DATE'] == '')])
        
        df_year = pd.concat(tmp_year)
        df_year.to_excel(writer,sheet_name='INCORRECT_DATE',index=False)
 
    concat_df.to_excel(writer, sheet_name=site + '_' + year,index=False)
        
    writer.save()
    
    time_elapsed = datetime.now() - start_time
    print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    return response




@login_required(login_url='/arsp_dmu/login')
def whonet_transform_data(request,file_id):
    start_time = datetime.now()
    options = request.POST.getlist('options')
    file_name = RawFileName.objects.get(id=file_id)
    search_file_name = file_name.file_name.split('_')
    
   
    df = bigwork(file_id,search_file_name,options)
    
    
    
    response = HttpResponse( df.to_csv(index=False,mode = 'w'),content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=TRANSFORM_{}_{}.csv".format(file_name,datetime.now())
    
    
    time_elapsed = datetime.now() - start_time
    print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
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
    # output = mp.Queue()
    
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

def check_str_to_date(date):
    try:
       datetime.strptime(date)
       return True
    except:
        return False

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
    elif spn == 'NS':
        return 'NS'
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

def getYearInt(file_name):
    q = file_name.split('_')
    g = q[0]
    
    year = '20' + g[3:5]
    
    ret = int(year)
    
    return ret
        


def bigwork(file_id,search_file_name,options, year = ''):
    start_time = datetime.now() 
    df = concat_all_df(file_id)

    df['comment'] = df['comment'].str.replace('=', '', regex=False)
    df['comment'] = df['comment'].str.replace('-', '', regex=False)
    
    
    
    #changing patient_id if 7777777 seven(7)
    if 'PATIENT_ID' in options:
        df = df.apply(lambda row: patient_id_transform(row), axis=1)
    
  
    #removing rows if x_referred == 1
    if 'X_REFERRED' in options:
        df = df[df['x_referred'] != 1]

    
    
    # loc_chk = [x.lower() for x in loc_chk]
 
    
    whonet_site_location = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_codes_location.xlsx',search_file_name[1].lower())
    loc_chk = whonet_site_location['WARD'].values.tolist()

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
    new_ward = []
    
    new_diag = []
    
    new_noso = []
    
    new_mrsa = []
    
    new_pen = []
    new_oxa = []
    
    new_country = []
    new_lab = []
    
    x_growth = []
    
    
    start_time = datetime.now() 
    if 'Origin' in options:
        df = df.apply(lambda row: origin_transform(row,lab_chk,whonet_region_island), axis = 1)
    
    
    
    for index,row in df.iterrows():
        new_country.append('PHL')
        new_lab.append(search_file_name[1])
        new_institut.append(search_file_name[1])
        if 'NE_NM' in options:
            for atx in data_fields_mic:
                atx_name = atx.split('_')
                if row[atx.lower()] == '' and row[atx_name[0].lower() + '_ne'] != '':
                    df.at[index,atx.lower()] = row[atx_name[0].lower() + '_ne']
                else:
                    df.at[index,atx.lower()] = row[atx.lower()]
        
    df['country_a'] = new_country
    df['laboratory'] = new_lab
    df['institut'] = new_institut
    
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
                new_department.append(whonet_site_location['DEPARTMENT'][loc_chk.index(row['ward'])])
                new_ward_type.append(whonet_site_location['WARD_TYPE'][loc_chk.index(row['ward'])])
                new_ward.append(whonet_site_location['S_WARD'][loc_chk.index(row['ward'])])
            else:
                new_department.append('unk')
                new_ward_type.append('unk')
                new_ward.append('unk')
        
        
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
        
        
        # if 'Origin' in options:
        #     if row['laboratory'].upper() in lab_chk:
        #         region.append(whonet_region_island['REGION'][lab_chk.index(row['laboratory'])])
        #         island.append(whonet_region_island['ISLAND'][lab_chk.index(row['laboratory'])])
        #     else:
        #         region.append('')
        #         island.append('')
        
                
        #     if pd.isna(row['age']) == True or row['age'] == '':
        #             age.append('U')
                
        #     elif 'w' in str(row['age']) or 'W' in str(row['age']) or 'd' in str(row['age']) or 'D' in str(row['age']) or 'm' in str(row['age']) or 'M' in str(row['age']) or 'nb' in str(row['age']) or 'NB' in str(row['age']):
        #             age.append('A')
        #     elif row['age'] == 'nan':
        #             age.append('U')  
                
        #     elif float(row['age']) >= 0 and float(row['age']) <= 5:
        #             age.append('A')
                
        #     elif float(row['age']) >= 6 and float(row['age']) <= 17:
        #             age.append('B')
                
        #     elif float(row['age']) > 17 and float(row['age']) <= 64:
        #             age.append('C')
                
        #     elif float(row['age']) > 64:
        #             age.append('D')
                
        #     else:
        #             age.append('U')  
        
        
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
        
    
 
    # if 'Origin' in options:
    #     df['region'] = region
    #     df['island'] = island
    #     df['age_grp'] = age
    
    if 'Specimen' in options:
        df['organism'] = new_org
        df['org_type'] = new_org_type
        df['spec_type'] = new_spec_type
        df['spec_code'] = new_spec_code
    
    if 'Location' in options:
        df['department'] = new_department
        df['ward_type'] = new_ward_type
        df['ward'] = new_ward
    
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
                elif row['fox_nd30'] == 'I' or row['oxa_nm'] == 'I' or row['fox_nm'] == 'I':
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
                    if (row['date_admis'] != '' and row['spec_date'] != '') and ('/' in row['date_admis'] and '/' in row['spec_date']):
                        # if check_str_to_date(row['spec_date']) and check_str_to_date(row['date_admis']):
                        x = datetime.strptime(row['spec_date'],'%m/%d/%Y') - datetime.strptime(row['date_admis'],'%m/%d/%Y')
                        if x.days > 2:
                            new_noso.append('Y')
                        else:
                            new_noso.append('N')
                        # else:
                        #     new_noso.append('')   
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
    df = df.drop(columns=data_fields_etest)
    time_elapsed = datetime.now() - start_time 
    print('Time elapsed zzz (hh:mm:ss.ms) {}'.format(time_elapsed))
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
    df = set_pd_columns(df)
    row_iter = df.iterrows()
    try:
        file_name.save()
    except IntegrityError as e:
        file_name = RawFileName.objects.get(file_name=tmp_name.split('.')[0])
        file_name.updated_at = datetime.now()
        file_name.save()
        RawOrigin.objects.select_related('rawlocation','rawmicrobiology','rawspecimen','rawantidisk','rawantimic','rawantietest').filter(file_ref=file_name).delete()
        # RawFileName.objects.get(file_name=tmp_name.split('.')[0]).delete()
        import_raw_data(row_iter,file_name)
        
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded. System updated the file.'

    try:
        import_raw_data(row_iter,file_name)
        return 'File ' + tmp_name.split('.')[0]  +' successfully uploaded.'
     
    except IntegrityError as e:
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded.'


def concat_all_df(file_id):
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
      
    df['comment'] = df['comment'].str.replace('/^=/', '', regex=True)

    return df

'''
FUNCTIONS BELOW ARE FOR DATA SUMMARY REPORT
'''
def compute_summary_report(file_name,file_id):
    df_data_completeness = get_data_completeness(file_id)
    df_entero = get_data_entero(file_id)
    df_sal_shi = get_data_sal_shi(file_id)
    df_ent_vic = get_data_ent_vic(file_id)
    df_non_ent = get_data_non_ent(file_id)
    df_pae = get_data_pae(file_id)
    df_hin = get_data_hin(file_id)
    df_bca = get_data_bca(file_id)
    df_ngo_nko = get_data_ngo_nko(file_id)
    df_spn = get_data_spn(file_id)
    df_ent_positive = get_data_ent_positive(file_id)
    df_sta = get_data_sta(file_id)
    df_pce = get_data_pce(file_id)
    df_pma = get_data_pma(file_id)
    # df_other_non_ent = get_data_other_non_ent(file_id)
    df_svi = get_data_svi(file_id)
    df_bsn = get_data_bsn(file_id)
    
    
    summary = []
    ave = 0
    
    
    mrsa_esbl = get_mrsa_esbl(file_id)
    
    # df_esbl = pd.DataFrame(data=[df_entero[1]], columns=['Organism','Number','Percent'])
    
    if len(df_entero) == 3:
        summary.append(df_entero[1])
        ave += df_entero[2]
    
    if len(df_sal_shi) == 3:
        summary.append(df_sal_shi[1])
        ave += df_sal_shi[2]
        
    if len(df_ent_vic) == 3:
        summary.append(df_ent_vic[1])
        ave += df_ent_vic[2]
    
    if len(df_non_ent) == 3:
        summary.append(df_non_ent[1])
        ave += df_non_ent[2]
        
    if len(df_pae) == 3:
        summary.append(df_pae[1])
        ave += df_pae[2]
        
    if len(df_hin) == 3:
        summary.append(df_hin[1])
        ave += df_hin[2]
    
    if len(df_bca) == 3:
        summary.append(df_bca[1])
        ave += df_bca[2]
        
    if len(df_ngo_nko) == 3:
        summary.append(df_ngo_nko[1])
        ave += df_ngo_nko[2]
    
    if len(df_spn) == 3:
        summary.append(df_spn[1])
        ave += df_spn[2]
    
    if len(df_ent_positive) == 3:
        summary.append(df_ent_positive[1])
        ave += df_ent_positive[2]

    
    if len(df_sta) == 3:
        summary.append(df_sta[1])
        ave += df_sta[2]
    
    if len(df_pce) == 3:
        summary.append(df_pce[1])
        ave += df_pce[2]
    
    if len(df_pma) == 3:
        summary.append(df_pma[1])
        ave += df_pma[2]
    
    if len(df_svi) == 3:
        summary.append(df_svi[1])
        ave += df_svi[2]
    
    if len(df_bsn) == 3:
        summary.append(df_bsn[1])
        ave += df_bsn[2]
    
    
        
    summary.append(['','Average',str( round(ave / len(summary),2) ) + '%'])
    summary.append(['','',''])
    summary.append(['Other Phenotypic Test','Number','Percent'])
    summary.append(mrsa_esbl[0])
    summary.append(mrsa_esbl[1])
    
    final = pd.DataFrame(data=summary, columns=['Organism','Number','Percent'])
    # writer = pd.ExcelWriter(output, engine='xlsxwriter')
    writer = pd.ExcelWriter('DATA_SUMMARY_{}.xlsx'.format(file_name), engine='xlsxwriter')
    df_data_completeness.to_excel(writer, sheet_name='data_complete',index=False)
    df_entero[0].to_excel(writer, sheet_name='ent_xsal_xshi',index=False)
    df_sal_shi[0].to_excel(writer, sheet_name='ent_sal_shi', index=False)
    df_ent_vic[0].to_excel(writer, sheet_name='ent_vic', index=False)
    df_non_ent[0].to_excel(writer, sheet_name='non_ent_acs', index=False)
    df_pae[0].to_excel(writer, sheet_name='pae', index=False)
    df_hin[0].to_excel(writer, sheet_name='hin', index=False)
    df_bca[0].to_excel(writer, sheet_name='bca', index=False)
    df_ngo_nko[0].to_excel(writer, sheet_name='ngo_nko', index=False)
    df_spn[0].to_excel(writer, sheet_name='spn', index=False)
    df_ent_positive[0].to_excel(writer, sheet_name='ent sp.', index=False)
    df_sta[0].to_excel(writer, sheet_name='STA sp.', index=False)
    df_pce[0].to_excel(writer, sheet_name='pce', index=False)
    df_pma[0].to_excel(writer, sheet_name='pma', index=False)
    # df_other_non_ent.to_excel(writer, sheet_name='other non ent', index=False)
    df_svi[0].to_excel(writer, sheet_name='svi', index=False)
    df_bsn[0].to_excel(writer, sheet_name='bsn', index=False)
    # df_esbl.to_excel(writer, sheet_name='esbl', index=False)
    final.to_excel(writer, sheet_name='summary', index=False)
    
    writer.save()
    

    return writer



def xl_for_review(file_id,file_name,file_year):
    df = concat_all_df(file_id)
    df['patient_id'] = df['patient_id'].apply(str)
    df['date_admis'] = pd.to_datetime(df['date_admis'])
    df['spec_date'] = pd.to_datetime(df['spec_date'])
    df['date_birth'] = pd.to_datetime(df['date_birth'])
    
    df_date_of_admission = df[ df['date_admis'].dt.year != file_year ]
    df_spec_date = df[ df['spec_date'].dt.year != file_year]
    df_date_birth = df[ df['date_birth'] > datetime.now()]
    df_sex = df.apply(lambda row: summary_err_gender(row), axis=1)
    df_org = df.apply(lambda row: summary_err_org(row), axis=1)
    df_spec_type = df.apply(lambda row: summary_err_spec_type(row), axis=1)
    # df_sex = df[ (df['sex'] != 'm') | (df['sex'] != 'f') ]
    

    writer = pd.ExcelWriter('SUMMARY_FOR_REVIEW_{}.xlsx'.format(file_name), engine='xlsxwriter')
    # if len(df_date_of_admission) > 0:
    # df_date_of_admission.columns = map(str.upper, df_date_of_admission.columns)
    df_date_of_admission.to_excel(writer, sheet_name='Date of Admission', index=False)
    # if len(df_spec_date) > 0:
    # df_spec_date.columns = map(str.upper, df_spec_date.columns)
    df_spec_date.to_excel(writer, sheet_name='Specimen Date', index=False)
    # if len(df_date_birth) > 0:
    # df_date_birth.columns = map(str.upper, df_date_birth.columns)
    df_date_birth.to_excel(writer,sheet_name='Date of Birth', index=False)
    # if  'sex' in df_sex:
    # df_sex.columns = map(str.upper, df_sex.columns)
    df_sex.to_excel(writer, sheet_name='Sex', index=False)
    # if 'organism' in df_org:
    # df_org.columns = map(str.upper, df_org)
    df_org.to_excel(writer, sheet_name='Organism', index=False)
    
    # if 'spec_type' in df_spec_type:
    # df_spec_type.columns = map(str.upper, df_spec_type)
    df_spec_type.to_excel(writer, sheet_name='Specimen Type', index=False)
    
    writer.save()
    
    return writer



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
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','entero')
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
              
    
    ret = []
    
    df = pd.DataFrame(data=ess_data_ent, columns=['ENTEROBACTERIACEAE','Number',ess_all])  
    
    tmp_ess_data_summary =  round(((round(((ess_amk)/(ess_all))*100,2) +  round(((ess_amc)/(ess_all))*100,2) +  round(((ess_amp)/(ess_all))*100,2) \
                             + round(((ess_atm)/(ess_all))*100,2) + round(((ess_czo)/(ess_all))*100,2) + round(((ess_fep)/(ess_all))*100,2) \
                             + round(((ess_ctx)/(ess_all))*100,2) + round(((ess_fox)/(ess_all))*100,2) +  round(((ess_caz)/(ess_all))*100,2) \
                             + round(((ess_cro)/(ess_all))*100,2) + round(((ess_cxa)/(ess_all))*100,2) +  round(((ess_cip)/(ess_all))*100,2) \
                             + round(((ess_etp)/(ess_all))*100,2) + round(((ess_gen)/(ess_all))*100,2) +  round(((ess_ipm)/(ess_all))*100,2) \
                             + round(((ess_mem)/(ess_all))*100,2) + round(((ess_tzp)/(ess_all))*100,2) +  round(((ess_sxt)/(ess_all))*100,2) \
                             + round(((ess_col)/(ess_all))*100,2) if ess_all > 0 else 0 + round(((ess_fos)/(ess_ur))*100,2) + round(((ess_nit)/(ess_ur))*100,2)) / 21),2) if ess_all > 0 else 0
      
                             
      
      
    ess_data_summary = ['ENTEROBACTERIACEAE',ess_all,str(tmp_ess_data_summary) + '%']
    
    
    ret.append(df)
    if ess_all > 0:
        ret.append(ess_data_summary)
        ret.append(tmp_ess_data_summary)
    
    return ret


def get_data_non_ent(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','non_ent')
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
    
    ret = []
    
    df = pd.DataFrame(data=non_ent_data, columns=['Acinetobacter sp.','Number', non_ent_all])
    
    tmp_non_ent =  round(((round(((non_ent_amk)/(non_ent_all))*100,2) + round(((non_ent_sam)/(non_ent_all))*100,2) + round(((non_ent_fep)/(non_ent_all))*100,2) + round(((non_ent_caz)/(non_ent_all))*100,2) \
                     + round(((non_ent_cip)/(non_ent_all))*100,2) + round(((non_ent_col)/(non_ent_all))*100,2) + round(((non_ent_ipm)/(non_ent_all))*100,2) + round(((non_ent_mem)/(non_ent_all))*100,2) \
                     + round(((non_ent_mno)/(non_ent_all))*100,2) + round(((non_ent_gen)/(non_ent_all))*100,2) + round(((non_ent_tzp)/(non_ent_all))*100,2) + round(((non_ent_sxt)/(non_ent_all))*100,2) \
                     +  round(((non_ent_tet)/(non_ent_ur) if non_ent_ur > 0 else 0)*100,2)) / 13),2) if non_ent_all > 0 else 0
      
    non_ent_summary = ['Acinetobacter sp.',non_ent_all,str(tmp_non_ent) + '%']
    
    ret.append(df)
    if non_ent_all > 0:
        ret.append(non_ent_summary)
        ret.append(tmp_non_ent)
    
    
    
    
    return ret



def get_data_sal_shi(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','sal_shi')
    comp_add = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','sal_shi_add')
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

    ret = []
    
    df = pd.DataFrame(data=ent_data_sal_shi, columns=['Salmonella & Shigella sp.','Number',ent_all])
    
    tmp_ent_data_summary = round(((round(((ent_amc)/(ent_all))*100,2)   + round(((ent_amp)/(ent_all))*100,2) +  round(((ent_atm)/(ent_all))*100,2) + round(((ent_fep)/(ent_all))*100,2) \
                            + round(((ent_ctx)/(ent_all))*100,2) + round(((ent_fox)/(ent_all))*100,2) +  round(((ent_cro)/(ent_all))*100,2) + round(((ent_chl)/(ent_all))*100,2) \
                            + round(((ent_cip)/(ent_all))*100,2) + round(((ent_etp)/(ent_all))*100,2) +  round(((ent_ipm)/(ent_all))*100,2) + round(((ent_sxt)/(ent_all))*100,2) \
                            + round(((ent_azm)/(ent_azm_all) if ent_azm_all > 0 else 0) *100,2)) / 13) ,2) if ent_all > 0 else 0
    
    ent_data_summary = ['Salmonella & Shigella sp.',ent_all,str(tmp_ent_data_summary) + '%']
    
    ret.append(df)
    if ent_all > 0:
        ret.append(ent_data_summary)
        ret.append(tmp_ent_data_summary) 
        
    
    return ret


def get_data_ent_vic(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','ent_vic')
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
    
    
    ent_vic_amp = 0
    ent_vic_azm = 0
    ent_vic_chl = 0
    ent_vic_dox = 0
    ent_vic_sss = 0
    ent_vic_tet = 0
    ent_vic_sxt = 0
    ent_vic_all = 0
    
    for index,row in df.iterrows():
            if row['organism'] in cmp:
                  ent_vic_all += 1
                  if row['amp_nd10'] != '' or row['amp_nm'] != '':
                        ent_vic_amp += 1
                  if row['azm_nd15'] != '' or row['azm_nm'] != '':
                        ent_vic_azm += 1
                  if row['chl_nd30'] != '' or row['chl_nm'] != '':
                        ent_vic_chl += 1
                  if row['dox_nd30'] != '' or row['dox_nm'] != '':
                        ent_vic_dox += 1
                  if row['sss_nd200'] != '' or row['sss_nm'] != '':
                        ent_vic_sss += 1
                  if row['tcy_nd30'] != '' or row['tcy_nm'] != '':
                        ent_vic_tet += 1
                  if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                        ent_vic_sxt += 1
    
    ent_data_vic = [['Antibiotic','Number tested','Percentage'],
                    ['1. Ampicillin',ent_vic_amp,str(  round(((ent_vic_amp)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%'],
                    ['2. Azithromycin',ent_vic_azm,str(  round(((ent_vic_azm)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%'],
                    ['3. Chloramphenicol',ent_vic_chl,str(  round(((ent_vic_chl)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%'],
                    ['4. Doxycycline',ent_vic_dox,str(  round(((ent_vic_dox)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%'],
                    ['5. Sulfonamides',ent_vic_sss,str(  round(((ent_vic_sss)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%'],
                    ['6. Tetracycline',ent_vic_tet,str(  round(((ent_vic_tet)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%'],
                    ['7. Trimethoprim-Sulfamethoxazole',ent_vic_sxt,str(  round(((ent_vic_sxt)/(ent_vic_all))*100,2) ) + "%" if ent_vic_all > 0 else '0%']
                    ]

    
    ret = []
    df = pd.DataFrame(data=ent_data_vic, columns=['Vibrio Cholerae','Number', ent_vic_all])
    
    tmp_ent_data_vic = round(((round(((ent_vic_amp)/(ent_vic_all))*100,2) + round(((ent_vic_azm)/(ent_vic_all))*100,2) + round(((ent_vic_chl)/(ent_vic_all))*100,2) + round(((ent_vic_dox)/(ent_vic_all))*100,2) \
                         + round(((ent_vic_sss)/(ent_vic_all))*100,2) + round(((ent_vic_tet)/(ent_vic_all))*100,2) + round(((ent_vic_sxt)/(ent_vic_all))*100,2)) / 7),2) if ent_vic_all > 0 else 0
      
      
    ent_data_vic_summary = ['Vibrio Cholerae',ent_vic_all,str(tmp_ent_data_vic) + '%']
      
    ret.append(df)
    if ent_vic_all > 0:
        ret.append(ent_data_vic_summary)
        ret.append(tmp_ent_data_vic)
    
    
    return ret



def get_data_pae(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    
    
    pae_all = 0
    pae_amk = 0
    pae_atm = 0
    pae_fep = 0
    pae_caz = 0
    pae_cip = 0
    pae_col = 0
    pae_ipm = 0
    pae_mem = 0
    pae_gen = 0
    pae_tzp = 0
    
    
    for index,row in df.iterrows():
        if row['organism'] == 'pae':
                pae_all += 1
                if row['amk_nd30'] != '' or row['amk_nm'] != '':
                    pae_amk += 1
                if row['atm_nd30'] != '' or row['atm_nm'] != '':
                    pae_atm += 1
                if row['fep_nd30'] != '' or row['fep_nm'] != '':
                    pae_fep += 1
                if row['caz_nd30'] != '' or row['caz_nm'] != '':
                    pae_caz += 1
                if row['cip_nd5'] != '' or row['cip_nm'] != '':
                    pae_cip += 1
                if row['col_nd10'] != '' or row['col_nm'] != '':
                    pae_col += 1
                if row['ipm_nd10'] != '' or row['ipm_nm'] != '':
                    pae_ipm += 1
                if row['mem_nd10'] != '' or row['mem_nm'] != '':
                    pae_mem += 1
                if row['gen_nd10'] != '' or row['gen_nm'] != '':
                    pae_gen += 1
                if row['tzp_nd100'] != '' or row['tzp_nm'] != '':
                    pae_tzp += 1
    
    
    pae_ent_data = [['Antibiotic','Number tested','Percentage'],
                      ['1. Amikacin',pae_amk,str(  round(((pae_amk)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['2. Aztreonam',pae_atm,str(  round(((pae_atm)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['3. Cefepime',pae_fep,str(  round(((pae_fep)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['4. Ceftazidime',pae_caz,str(  round(((pae_caz)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['5. Ciprofloxacin',pae_cip,str(  round(((pae_cip)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['6. Colistin',pae_col,str(  round(((pae_col)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['7. Imipenem',pae_ipm,str(  round(((pae_ipm)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['8. Meropenem',pae_mem,str(  round(((pae_mem)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['9. Gentamicin',pae_gen,str(  round(((pae_gen)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%'],
                      ['10. Piperacillin-tazobactam',pae_tzp,str(  round(((pae_tzp)/(pae_all))*100,2) ) + "%" if pae_all > 0 else '0%']
                     ]
    
    ret = []
    df = pd.DataFrame(data=pae_ent_data, columns=['Pseudomonas aeruginosa','Number',pae_all])
    
    
    tmp_pae_ent_data = round(((round(((pae_amk)/(pae_all))*100,2) +  round(((pae_atm)/(pae_all))*100,2) + round(((pae_fep)/(pae_all))*100,2) + round(((pae_caz)/(pae_all))*100,2) \
                         + round(((pae_cip)/(pae_all))*100,2) + round(((pae_col)/(pae_all))*100,2) + round(((pae_ipm)/(pae_all))*100,2) + round(((pae_mem)/(pae_all))*100,2) \
                         + round(((pae_gen)/(pae_all))*100,2) + round(((pae_tzp)/(pae_all))*100,2)) / 10), 2) if pae_all > 0 else 0
      
    pae_ent_summary = ['Pseudomonas aeruginosa',pae_all, str(tmp_pae_ent_data) + '%']
    
    ret.append(df)
    if pae_all > 0:
        ret.append(pae_ent_summary)
        ret.append(tmp_pae_ent_data)
    
    return ret
    
    
    


def get_data_hin(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    
    hin_all = 0
    hin_amc = 0
    hin_amp = 0
    hin_sam = 0
    hin_azm = 0
    hin_cro = 0
    hin_cip_lev = 0
    hin_mem = 0
    hin_tet = 0
    hin_sxt = 0
    
    for index,row in df.iterrows():
            if row['organism'].lower() == 'hin' or row['organism'].lower()  == 'hxt' or row['organism'].lower()  == 'hxb' or row['organism'].lower()  == 'hib' or row['organism'].lower()  == 'hpi':
                  hin_all += 1
                  if row['amc_nd20'] != '' or row['amc_nm'] != '':
                        hin_amc += 1
                  if row['amp_nd10'] != '' or row['amp_nm'] != '':
                        hin_amp += 1
                  if row['sam_nd10'] != '' or row['sam_nm'] != '':
                        hin_sam += 1
                  if row['azm_nd15'] != '' or row['azm_nm'] != '':
                        hin_azm += 1
                  if row['cro_nd30'] != '' or row['cro_nm'] != '':
                        hin_cro += 1
                  if (row['cip_nd5'] != '' or row['cip_nm'] != '') or (row['lvx_nd5'] != '' or row['lvx_nm'] != ''):
                        hin_cip_lev += 1
                  if row['mem_nd10'] != '' or row['mem_nm'] != '':
                        hin_mem += 1
                  if row['tcy_nd30'] != '' or row['tcy_nm'] != '':
                        hin_tet += 1
                  if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                        hin_sxt += 1

    hin_fast_data = [['Antibiotic','Number tested','Percentage'],
                       ['1. Amoxicillin-clavulanate',hin_amc,str(  round(((hin_amc)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['2. Ampicillin',hin_amp,str(  round(((hin_amp)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['3. Ampicillin/Sulbactam',hin_sam,str(  round(((hin_sam)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['4. Azithromycin',hin_azm,str(  round(((hin_azm)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'] ,
                       ['5. Ceftriaxone',hin_cro,str(  round(((hin_cro)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['6. Ciprofloxacin or Levofloxacin',hin_cip_lev,str(  round(((hin_cip_lev)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['7. Meropenem',hin_mem,str(  round(((hin_mem)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['8. Tetracycline',hin_tet,str(  round(((hin_tet)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%'],
                       ['9. Trimethoprim-Sulfamethoxazole',hin_sxt,str(  round(((hin_sxt)/(hin_all))*100,2) ) + "%" if hin_all > 0 else '0%']
                       ]

    ret = []
    df = pd.DataFrame(data=hin_fast_data, columns=['Haemophilus influenza and Haemophilus parainfluenzae','Number',hin_all])
    
    tmp_hin_fast_data = round(((round(((hin_amc)/(hin_all))*100,2) + round(((hin_amp)/(hin_all))*100,2) + round(((hin_sam)/(hin_all))*100,2) + round(((hin_azm)/(hin_all))*100,2) + round(((hin_cro)/(hin_all))*100,2) \
                          + round(((hin_cip_lev)/(hin_all))*100,2) + round(((hin_mem)/(hin_all))*100,2) +  round(((hin_tet)/(hin_all))*100,2) + round(((hin_sxt)/(hin_all))*100,2)) / 9),2) if hin_all > 0 else 0
      
    hin_fast_summary = ['Haemophilus influenza and Haemophilus parainfluenzae',hin_all,str(tmp_hin_fast_data) + '%']
    
    ret.append(df)
    if hin_all > 0:
        ret.append(hin_fast_summary)
        ret.append(tmp_hin_fast_data)
    
    return ret


def get_data_bca(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    mox_all = 0
    mox_amc = 0
    mox_cxa = 0
    mox_sxt = 0
    
    for index,row in df.iterrows():
        if row['organism'] == 'bca':
                mox_all += 1
                if row['amc_nd20'] != '' or row['amc_nm'] != '':
                    mox_amc += 1
                if row['cxa_nd30'] != '' or row['cxa_nm'] != '':
                    mox_cxa += 1
                if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '': 
                    mox_sxt += 1
                    
    mox_fast_data = [['Antibiotic','Number tested','Percentage'],
                    ['1. Amoxicillin-clavulanate',mox_amc,str(  round(((mox_amc)/(mox_all))*100,2) ) + "%" if mox_all > 0 else '0%'],
                    ['2. Cefuroxime',mox_cxa,str(  round(((mox_cxa)/(mox_all))*100,2) ) + "%" if mox_all > 0 else '0%'],
                    ['3. Trimethoprim-Sulfamethoxazole',mox_sxt,str(  round(((mox_sxt)/(mox_all))*100,2) ) + "%" if mox_all > 0 else '0%']
                    ]
    ret = []
    df = pd.DataFrame(data=mox_fast_data, columns=['Moraxella catarrhalis','Number',mox_all])
    
    tmp_mox_fast = round(((round(((mox_amc)/(mox_all))*100,2) + round(((mox_cxa)/(mox_all))*100,2) + round(((mox_sxt)/(mox_all))*100,2)) / 3),2) if mox_all > 0 else 0
    
    mox_fast_summary = ['Moraxella catarrhalis',mox_all,str(tmp_mox_fast) + '%']
    ret.append(df)
    if mox_all > 0:
        ret.append(mox_fast_summary)
        ret.append(tmp_mox_fast)
    
    return ret

def get_data_nme(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','nme')
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
    
    
    nme_all = 0
    nme_amp = 0
    nme_azm = 0
    nme_cro = 0
    nme_cip = 0
    nme_mem = 0
    nme_pen = 0
    
    for index,row in df.iterrows():
        if row['organism'] in cmp:
                nme_all += 1
                if row['amp_nd10'] != '' or row['amp_nm'] != '':
                    nme_amp += 1
                if row['azm_nd15'] != '' or row['azm_nm'] != '':
                    nme_azm += 1
                if row['cro_nd30'] != '' or row['cro_nm'] != '':
                    nme_cro += 1
                if row['cip_nd5'] != '' or row['cip_nm'] != '':
                    nme_cip += 1
                if row['mem_nd10'] != '' or row['mem_nm'] != '':
                    nme_mem += 1
                if row['pen_nd10'] != '' or row['pen_nm'] != '':
                    nme_pen += 1
                    
    nme_fast_data = [['Antibiotic','Number tested','Percentage'],
                       ['1. Ampicillin',nme_amp,str(  round(((nme_amp)/(nme_all))*100,2) ) + "%" if nme_all > 0 else '0%'],
                       ['2. Azithromycin',nme_azm,str(  round(((nme_azm)/(nme_all))*100,2) ) + "%" if nme_all > 0 else '0%'],
                       ['3. Ceftriaxone',nme_cro,str(  round(((nme_cro)/(nme_all))*100,2) ) + "%" if nme_all > 0 else '0%'],
                       ['4. Ciprofloxacin',nme_cip,str(  round(((nme_cip)/(nme_all))*100,2) ) + "%" if nme_all > 0 else '0%'],
                       ['5. Meropenem',nme_mem,str(  round(((nme_mem)/(nme_all))*100,2) ) + "%" if nme_all > 0 else '0%'],
                       ['6. Penicillin',nme_pen,str(  round(((nme_pen)/(nme_all))*100,2) ) + "%" if nme_all > 0 else '0%']
                       ]
    
    df = pd.DataFrame(data=nme_fast_data, columns=['Neisseria meningitidis','Number',nme_all])
    
    return df


def get_data_ngo_nko(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    ngo_all = 0
    ngo_azm = 0
    ngo_cfm = 0
    ngo_cro = 0
    ngo_cip = 0
    ngo_gen = 0
    ngo_nal = 0
    ngo_spe = 0
    ngo_tet = 0
    
    for index,row in df.iterrows():
        if row['organism'] == 'ngo' or row['organism'] == 'nko':
                ngo_all += 1
                if row['azm_nd15'] != '' or row['azm_nm'] != '':
                    ngo_azm += 1
                if row['cfm_nd5'] != '' or row['cfm_nm'] != '':
                    ngo_cfm += 1
                if row['cro_nd30'] != '' or row['cro_nm'] != '':
                    ngo_cro += 1
                if row['cip_nd5'] != '' or row['cip_nm'] != '':
                    ngo_cip += 1
                if row['gen_nd10'] != '' or row['gen_nm'] != '':
                    ngo_gen += 1
                if row['nal_nd30'] != '' or row['nal_nm'] != '':
                    ngo_nal += 1
                if row['spt_nd100'] != '' or row['spt_nm'] != '':
                    ngo_spe += 1
                if row['tcy_nd30'] != '' or row['tcy_nm'] != '':
                    ngo_tet += 1
                    
    ngo_fast_data = [['Antibiotic','Number tested','Percentage'],
                    ['1. Azithromycin',ngo_azm,str(  round(((ngo_azm)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['2. Cefixime',ngo_cfm,str(  round(((ngo_cfm)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['3. Ceftriaxone',ngo_cro,str(  round(((ngo_cro)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['4. Ciprofloxacin',ngo_cip,str(  round(((ngo_cip)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['5. Gentamicin',ngo_gen,str(  round(((ngo_gen)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['6. Nalixidic acid',ngo_nal,str(  round(((ngo_nal)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['7. Spectinomycin',ngo_spe,str(  round(((ngo_spe)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%'],
                    ['8. Tetracycline',ngo_tet,str(  round(((ngo_tet)/(ngo_all))*100,2) ) + "%" if ngo_all > 0 else '0%']
                    ]
    
    ret = []
    df = pd.DataFrame(data=ngo_fast_data, columns=['Neisseria gonorrhoeae','Number',ngo_all])
    
    tmp_ngo_fast = round(((round(((ngo_azm)/(ngo_all))*100,2) + round(((ngo_cfm)/(ngo_all))*100,2) + round(((ngo_cro)/(ngo_all))*100,2) + round(((ngo_cip)/(ngo_all))*100,2) + round(((ngo_gen)/(ngo_all))*100,2) \
                     + round(((ngo_nal)/(ngo_all))*100,2) + round(((ngo_spe)/(ngo_all))*100,2) + round(((ngo_tet)/(ngo_all))*100,2)) / 8) , 2) if ngo_all > 0 else 0
      
    ngo_fast_summary = ['Neisseria gonorrhoeae',ngo_all,str(tmp_ngo_fast) + '%']
    
    ret.append(df)
    if ngo_all > 0:
        ret.append(ngo_fast_summary)
        ret.append(tmp_ngo_fast)
    
    return ret


def get_data_spn(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    
    spn_all = 0
    spn_cro = 0
    spn_cli = 0
    spn_ery = 0
    spn_lev = 0
    spn_mem = 0
    spn_oxa_pen = 0                
    spn_tet = 0
    spn_sxt = 0
    spn_van = 0
    
    for index,row in df.iterrows():
        if row['organism'] == 'spn':
                spn_all += 1
                if row['cro_nd30'] != '' or row['cro_nm'] != '':
                    spn_cro += 1
                if row['cli_nd2'] != '' or row['cli_nm'] != '':
                    spn_cli += 1
                if row['ery_nd15'] != '' or row['ery_nm'] != '':
                    spn_ery += 1
                if row['lvx_nd5'] != '' or row['lvx_nm'] != '':
                    spn_lev += 1
                if row['mem_nd10'] != '' or row['mem_nm'] != '':
                    spn_mem += 1
                if (row['oxa_nd1'] != '' or row['oxa_nm'] != '') or (row['pen_nd10'] != '' or row['pen_nm'] != ''):
                    spn_oxa_pen += 1
                if row['tcy_nd30'] != '' or row['tcy_nm'] != '':
                    spn_tet += 1
                if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                    spn_sxt += 1
                if row['van_nd30'] != '' or row['van_nm'] != '':
                    spn_van += 1
    
    spn_fast_data = [['Antibiotic','Number tested','Percentage'],
                    ['1. Ceftriaxone non-meningitis or Ceftriaxone meningitis',spn_cro,str(  round(((spn_cro)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['2. Clindamycin',spn_cli,str(  round(((spn_cli)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['3. Erythromycin',spn_ery,str(  round(((spn_ery)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['4. Levofloxacin',spn_lev,str(  round(((spn_lev)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['5. Meropenem',spn_mem,str(  round(((spn_mem)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['6. Oxacillin or Penicillin',spn_oxa_pen,str(  round(((spn_oxa_pen)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['7. Tetracycline',spn_tet,str(  round(((spn_tet)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['8. Trimethoprim-Sulfamethoxazole',spn_sxt,str(  round(((spn_sxt)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%'],
                    ['9. Vancomycin',spn_van,str(  round(((spn_van)/(spn_all))*100,2) ) + "%" if spn_all > 0 else '0%']
                    ]
    
    ret = []
    df = pd.DataFrame(data=spn_fast_data, columns=['Streptococcus pneumonia','Number',spn_all])
    
    tmp_spn_fast = round(((round(((spn_cro)/(spn_all))*100,2) + round(((spn_cli)/(spn_all))*100,2) + round(((spn_ery)/(spn_all))*100,2) + round(((spn_lev)/(spn_all))*100,2) + round(((spn_mem)/(spn_all))*100,2) \
                     + round(((spn_oxa_pen)/(spn_all))*100,2) + round(((spn_tet)/(spn_all))*100,2) + round(((spn_sxt)/(spn_all))*100,2) + round(((spn_van)/(spn_all))*100,2)) / 9) , 2) if spn_all > 0 else 0
      
    spn_fast_summary = ['Streptococcus pnuemonia',spn_all,str(tmp_spn_fast) + '%']
    ret.append(df)
    if spn_all > 0:
        ret.append(spn_fast_summary)
        ret.append(tmp_spn_fast)
    
    return ret



def get_data_ent_positive(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','ent_positive')
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

    ent_positive_all = 0
    ent_positive_amp = 0
    ent_positive_dap = 0
    ent_positive_geh = 0
    ent_positive_lnz = 0
    ent_positive_pen = 0
    ent_positive_sth = 0
    ent_positive_van = 0
    ent_positive_fos = 0
    ent_positive_nit = 0
    ent_positive_ur = 0
    
    for index,row in df.iterrows():
        if row['organism'] in cmp:
                ent_positive_all += 1
                if row['amp_nd10'] != '' or row['amp_nm'] != '':
                    ent_positive_amp += 1
                if row['dap_nd30'] != '' or row['dap_nm'] != '':
                    ent_positive_dap += 1
                if row['geh_nd120'] != '' or row['geh_nm'] != '':
                    ent_positive_geh += 1
                if row['lnz_nd30'] != '' or row['lnz_nm'] != '':
                    ent_positive_lnz += 1
                if row['pen_nd10'] != '' or row['pen_nm'] != '':
                    ent_positive_pen += 1
                if row['sth_nd300'] != '' or row['sth_nm'] != '': 
                    ent_positive_sth += 1
                if row['van_nd30'] != '' or row['van_nm'] != '':
                    ent_positive_van += 1
                if row['spec_type'] == 'ur':
                    ent_positive_ur += 1
                if (row['fos_nd200'] != '' or row['fos_nm'] != '') and row['spec_type'] == 'ur':
                    ent_positive_fos += 1
                if (row['nit_nd300'] != '' or row['nit_nm'] != '') and row['spec_type'] == 'ur':
                    ent_positive_nit += 1
    ent_positive_data = [['Antibiotic','Number tested','Percentage'],
                        ['1. Ampicillin',ent_positive_amp,str(  round(((ent_positive_amp)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['2. Daptomycin',ent_positive_dap,str(  round(((ent_positive_dap)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['3. Gentamicin High Level',ent_positive_geh,str(  round(((ent_positive_geh)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['4. Linezolid',ent_positive_lnz,str(  round(((ent_positive_lnz)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['5. Penicillin',ent_positive_pen,str(  round(((ent_positive_pen)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['6. Streptomycin High Level',ent_positive_sth,str(  round(((ent_positive_sth)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['7. Vancomycin',ent_positive_van,str(  round(((ent_positive_van)/(ent_positive_all))*100,2) ) + "%" if ent_positive_all > 0 else '0%'],
                        ['','Additional for Urine',ent_positive_ur],
                        ['1. Fosfomycin',ent_positive_fos,str(  round(((ent_positive_fos)/(ent_positive_ur))*100,2) ) + "%" if ent_positive_ur > 0 else '0%'],
                        ['2. Nitrofurantoin',ent_positive_nit,str(  round(((ent_positive_nit)/(ent_positive_ur))*100,2) ) + "%" if ent_positive_ur > 0 else '0%']
                        ]
    
    ret = []
    df = pd.DataFrame(data=ent_positive_data, columns=['Enterococcus sp.','Number',ent_positive_all])
    
    tmp_ent_positive = round(((round(((ent_positive_amp)/(ent_positive_all))*100,2) + round(((ent_positive_dap)/(ent_positive_all))*100,2) + round(((ent_positive_geh)/(ent_positive_all))*100,2) + round(((ent_positive_lnz)/(ent_positive_all))*100,2) \
                         + round(((ent_positive_pen)/(ent_positive_all))*100,2) + round(((ent_positive_sth)/(ent_positive_all))*100,2) + round(((ent_positive_van)/(ent_positive_all))*100,2) \
                         + round(((ent_positive_fos)/(ent_positive_ur)if ent_positive_ur > 0 else 0)*100,2) + round(((ent_positive_nit)/(ent_positive_ur)if ent_positive_ur > 0 else 0)*100,2)) / 9) ,2) if ent_positive_all > 0 else 0
      
    ent_positive_summary = ['Enterococcus sp.',ent_positive_all,str(tmp_ent_positive) + '%']
    
    ret.append(df)
    if ent_positive_all > 0:
        ret.append(ent_positive_summary)
        ret.append(tmp_ent_positive)
    
    return ret



def get_data_sta(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','sta')
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
    
    
    sta_all = 0
    sta_fox_oxa = 0
    sta_cip = 0
    sta_cli = 0
    sta_dap = 0
    sta_ery = 0
    sta_lnz = 0
    sta_pen = 0
    sta_rif = 0
    sta_tet = 0
    sta_sxt = 0
    sta_van = 0
    
    for index,row in df.iterrows():
        if row['organism']  in cmp:
                sta_all += 1
                if (row['fox_nd30'] != '' or row['fox_nm'] != '') or (row['oxa_nd1'] != '' or row['oxa_nm'] != ''):
                    sta_fox_oxa += 1
                if row['cip_nd5'] != '' or row['cip_nm'] != '':
                    sta_cip += 1
                if row['cli_nd2'] != '' or row['cli_nm'] != '':
                    sta_cli += 1
                if row['dap_nd30'] != '' or row['dap_nm'] != '':
                    sta_dap += 1
                if row['ery_nd15'] != '' or row['ery_nm'] != '':
                    sta_ery += 1
                if row['lnz_nd30'] != '' or row['lnz_nm'] != '':
                    sta_lnz += 1
                if row['pen_nd10'] != '' or row['pen_nm'] != '':
                    sta_pen += 1
                if row['rif_nd5'] != '' or row['rif_nm'] != '':
                    sta_rif += 1
                if row['tcy_nd30'] != '' or row['tcy_nm'] != '':
                    sta_tet += 1
                if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                    sta_sxt += 1 
                if row['van_nd30'] != '' or row['van_nm'] != '':
     
                    sta_van += 1  
    sta_data = [['Antibiotic','Number tested','Percentage'],
                ['1. Cefoxitin or Oxacillin',sta_fox_oxa,str(  round(((sta_fox_oxa)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['2. Ciprofloxacin',sta_cip,str(  round(((sta_cip)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['3. Clindamycin',sta_cli,str(  round(((sta_cli)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['4. Daptomycin',sta_dap,str(  round(((sta_dap)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['5. Erythromycin',sta_ery,str(  round(((sta_ery)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['6. Linezolid',sta_lnz,str(  round(((sta_lnz)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['7. Penicillin',sta_pen,str(  round(((sta_pen)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['8. Rifampin',sta_rif,str(  round(((sta_rif)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['9. Tetracycline',sta_tet,str(  round(((sta_tet)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['10. Trimethoprim-Sulfamethoxazole',sta_sxt,str(  round(((sta_sxt)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%'],
                ['11. Vancomycin',sta_van,str(  round(((sta_van)/(sta_all))*100,2) ) + "%" if sta_all > 0 else '0%']
                ]
    
    ret = []
    df = pd.DataFrame(data=sta_data, columns=['Staphylococcus sp.','Number',sta_all])
    
    
    tmp_sta = round(((round(((sta_fox_oxa)/(sta_all))*100,2) + round(((sta_cip)/(sta_all))*100,2) + round(((sta_cli)/(sta_all))*100,2) + round(((sta_dap)/(sta_all))*100,2) + round(((sta_ery)/(sta_all))*100,2) \
                + round(((sta_lnz)/(sta_all))*100,2) +  round(((sta_pen)/(sta_all))*100,2) + round(((sta_rif)/(sta_all))*100,2) + round(((sta_tet)/(sta_all))*100,2) + round(((sta_sxt)/(sta_all))*100,2) \
                + round(((sta_van)/(sta_all))*100,2)) / 11) ,2) if sta_all > 0 else 0
      
    sta_summary = ['Staphylococcus sp.',sta_all,str(tmp_sta) + '%']
    
    
    ret.append(df)
    if sta_all > 0:
        ret.append(sta_summary)
        ret.append(tmp_sta)
    
    return ret

def get_data_pce(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    
    pce_all = 0
    pce_caz = 0
    pce_chl = 0
    pce_lev = 0
    pce_mem = 0
    pce_mno = 0
    pce_sxt = 0
    
    
    for index,row in df.iterrows():
        if row['organism'] == 'pce':
                pce_all += 1
                if row['caz_nd30'] != '' or row['caz_nm'] != '':
                    pce_caz += 1
                if row['chl_nd30'] != '' or row['chl_nm'] != '':
                    pce_chl += 1
                if row['lvx_nd5'] != '' or row['lvx_nm'] != '':
                    pce_lev += 1
                if row['mem_nd10'] != '' or row['mem_nm'] != '':
                    pce_mem += 1
                if row['mno_nd30'] != '' or row['mno_nm'] != '':
                    pce_mno += 1
                if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                    pce_sxt += 1
    
    pce_data = [['Antibiotic','Number tested','Percentage'],
                ['1. Ceftazidime',pce_caz,str(  round(((pce_caz)/(pce_all))*100,2) ) + "%" if pce_all > 0 else '0%'],
                ['2. Chloramphenicol',pce_chl,str(  round(((pce_chl)/(pce_all))*100,2) ) + "%" if pce_all > 0 else '0%'],
                ['3. Levofloxacin',pce_lev,str(  round(((pce_lev)/(pce_all))*100,2) ) + "%" if pce_all > 0 else '0%'],
                ['4. Meropenem',pce_mem,str(  round(((pce_mem)/(pce_all))*100,2) ) + "%" if pce_all > 0 else '0%'],
                ['5. Minocycline',pce_mno,str(  round(((pce_mno)/(pce_all))*100,2) ) + "%" if pce_all > 0 else '0%'],
                ['6. Trimethoprim-Sulfamethoxazole',pce_sxt,str(  round(((pce_sxt)/(pce_all))*100,2) ) + "%" if pce_all > 0 else '0%']
                ]
    
    ret = []
    df = pd.DataFrame(data=pce_data, columns=['Burkholderia cepacia','Number',pce_all])
    
    
    tmp_pce = round(((round(((pce_caz)/(pce_all))*100,2) + round(((pce_chl)/(pce_all))*100,2) + round(((pce_lev)/(pce_all))*100,2) + round(((pce_mem)/(pce_all))*100,2) \
                + round(((pce_mno)/(pce_all))*100,2) + round(((pce_sxt)/(pce_all))*100,2)) / 6),2) if pce_all > 0 else 0
      
    pce_summary = ['Burkholderia cepacia',pce_all,str(tmp_pce) + '%']
    
    ret.append(df)
    if pce_all > 0:
        ret.append(pce_summary)
        ret.append(tmp_pce)
    
    
    
    return ret

def get_data_pma(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    df = df[~df['comment'].str.contains('light growth',regex=True,flags=re.IGNORECASE)]
    df = df[~df['comment'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lg',regex=True,flags=re.IGNORECASE)]
    df = df[~df['growth'].str.contains('lcc',regex=True,flags=re.IGNORECASE)]
    
    pma_all = 0
    pma_caz = 0
    pma_chl = 0
    pma_lev = 0
    pma_mno = 0
    pma_sxt = 0
    
    for index,row in df.iterrows():
        if row['organism'] == 'pma':
                pma_all += 1
                if row['caz_nd30'] != '' or row['caz_nm'] != '':
                    pma_caz += 1
                if row['chl_nd30'] != '' or row['chl_nm'] != '':
                    pma_chl += 1
                if row['lvx_nd5'] != '' or row['lvx_nm'] != '':
                    pma_lev += 1
                if row['mno_nd30'] != '' or row['mno_nm'] != '':
                    pma_mno += 1
                if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                    pma_sxt += 1 
    
    pma_data = [['Antibiotic','Number tested','Percentage'],
                  ['1. Ceftazidime',pma_caz,str(  round(((pma_caz)/(pma_all))*100,2) ) + "%" if pma_all > 0 else '0%'],
                  ['2. Chloramphenicol',pma_chl,str(  round(((pma_chl)/(pma_all))*100,2) ) + "%" if pma_all > 0 else '0%'],
                  ['3. Levofloxacin',pma_lev,str(  round(((pma_lev)/(pma_all))*100,2) ) + "%" if pma_all > 0 else '0%'],
                  ['4. Minocycline',pma_mno,str(  round(((pma_mno)/(pma_all))*100,2) ) + "%" if pma_all > 0 else '0%'],
                  ['5. Trimethoprim-Sulfamethoxazole',pma_sxt,str(  round(((pma_sxt)/(pma_all))*100,2) ) + "%" if pma_all > 0 else '0%']
                  ]
    
    ret = []
    df = pd.DataFrame(data=pma_data, columns=['Stenotrophomonas maltophilia','Number',pma_all])
    
    tmp_pma = round(((round(((pma_caz)/(pma_all))*100,2) + round(((pma_chl)/(pma_all))*100,2) + round(((pma_lev)/(pma_all))*100,2) + round(((pma_mno)/(pma_all))*100,2) + round(((pma_sxt)/(pma_all))*100,2)) / 5),2) if pma_all > 0 else 0
      
    pma_summary = ['Stenotrophomonas maltophilia',pma_all,str(tmp_pma) + '%']
    
    ret.append(df)
    if pma_all > 0:
        ret.append(pma_summary)
        ret.append(tmp_pma)
    
    return ret



def get_data_other_non_ent(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','other_non_ent')
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
    
    other_all = 0
    other_amk = 0
    other_atm = 0
    other_fep = 0
    other_ctx_cro_caz = 0
    other_chl = 0
    other_cip_lev = 0
    other_gen_tob = 0
    other_imp_mem = 0
    other_tzp = 0
    other_sxt = 0
    other_tet = 0
    other_ur = 0
    
    for index,row in df.iterrows():
        if row['organism'] in cmp:
                other_all += 1
                if row['amk_nd30'] != '' or row['amk_nm'] != '':
                    other_amk += 1
                if row['atm_nd30'] != '' or row['atm_nm'] != '':
                    other_atm += 1   
                if row['fep_nd30'] != '' or row['fep_nm'] != '':
                    other_fep += 1 
                if (row['ctx_nd30'] != '' or row['ctx_nm'] != '') or (row['cro_nd30'] != '' or row['cro_nm'] != '') or (row['caz_nd30'] != '' or row['caz_nm'] != ''):
                    other_ctx_cro_caz += 1
                if row['chl_nd30'] != '' or row['chl_nm'] != '':
                    other_chl += 1
                if (row['cip_nd5'] != '' or row['cip_nm'] != '') or (row['lvx_nd5'] != '' or row['lvx_nm'] != ''):
                    other_cip_lev += 1 
                if (row['gen_nd10'] != '' or row['gen_nm'] != '') or (row['tob_nd10'] != '' or row['tob_nm'] != ''):
                    other_gen_tob += 1
                if (row['ipm_nd10'] != '' or row['ipm_nm'] != '') or (row['mem_nd10'] != '' or row['mem_nm'] != ''):
                    other_imp_mem += 1
                if row['tzp_nd100'] != '' or row['tzp_nm'] != '':
                    other_tzp += 1 
                if row['sxt_nd1_2'] != '' or row['sxt_nm'] != '':
                    other_sxt += 1
                if (row['tcy_nd30'] != '' or row['tcy_nm'] != '') and row['spec_type'] == 'ur':
                    other_tet += 1 
                if row['spec_type'] == 'ur':  
                    other_ur += 1
                    
                    
    other_data = [['Antibiotic','Number tested','Percentage'],
                    ['1. Amikacin',other_amk,str(  round(((other_amk)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['2. Aztreonam',other_atm,str(  round(((other_atm)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['3. Cefepime',other_fep,str(  round(((other_fep)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['4. Cefotaxime or Cefriaxone or Ceftazidime',other_ctx_cro_caz,str(  round(((other_ctx_cro_caz)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['5. Chloramphenicol',other_chl,str(  round(((other_chl)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['6. Ciprofloxacin or Levofloxacin',other_cip_lev,str(  round(((other_cip_lev)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['7. Gentamicin or Tobramycin',other_gen_tob,str(  round(((other_gen_tob)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['8. Imipenem or Meropenem',other_imp_mem,str(  round(((other_imp_mem)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['9. Piperacillin-sulfamethoxazole',other_tzp,str(  round(((other_tzp)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['10. Trimethoprim-sulfamethoxazole',other_sxt,str(  round(((other_sxt)/(other_all))*100,2) ) + "%" if other_all > 0 else '0%'],
                    ['','Additional for Urine',other_ur],
                    ['1. Tetracycline',other_tet,str(  round(((other_tet)/(other_ur))*100,2) ) + "%" if other_ur > 0 else '0%']
                    ]
    
    df = pd.DataFrame(data=other_data, columns=['Other Non-Enterobacteriaceae','Number',other_all])
    
    return df

def get_data_svi(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','svi')
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
    
    
    svi_all = 0
    svi_amp = 0
    svi_cro = 0
    svi_chl = 0
    svi_cli = 0
    svi_ery = 0
    svi_lnz = 0
    svi_pen = 0
    svi_van = 0
    
    for index,row in df.iterrows():
        if row['organism'] in cmp:
                svi_all += 1
                if row['amp_nd10'] != '' or row['amp_nm'] != '':
                    svi_amp += 1
                if row['cro_nd30'] != '' or row['cro_nm'] != '':
                    svi_cro += 1
                if row['chl_nd30'] != '' or row['chl_nm'] != '':
                    svi_chl += 1
                if row['cli_nd2'] != '' or row['cli_nm'] != '':
                    svi_cli += 1
                if row['ery_nd15'] != '' or row['ery_nm'] != '':
                    svi_ery += 1
                if row['lnz_nd30'] != '' or row['lnz_nm'] != '':
                    svi_lnz += 1
                if row['pen_nd10'] != '' or row['pen_nm'] != '':
                    svi_pen += 1
                if row['van_nd30'] != '' or row['van_nm'] != '':
                    svi_van += 1
                    
                    
    svi_data = [['Antibiotic','Number tested','Percentage'],
                  ['1. Ampicillin',svi_amp,str(  round(((svi_amp)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['2. Cefriaxone',svi_cro,str(  round(((svi_cro)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['3. Chloramphenicol',svi_chl,str(  round(((svi_chl)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['4. Clindamycin',svi_cli,str(  round(((svi_cli)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['5. Erythromycin',svi_ery,str(  round(((svi_ery)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['6. Linezolid',svi_lnz,str(  round(((svi_lnz)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['7. Penicillin',svi_pen,str(  round(((svi_pen)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%'],
                  ['8. Vancomycin',svi_van,str(  round(((svi_van)/(svi_all))*100,2) ) + "%" if svi_all > 0 else '0%']
                  ]
    
    ret = []
    df = pd.DataFrame(data=svi_data, columns=['Streptococcus Viridans Group','Number',svi_all])
    
    tmp_svi = round(((round(((svi_amp)/(svi_all))*100,2) + round(((svi_cro)/(svi_all))*100,2) + round(((svi_chl)/(svi_all))*100,2) + round(((svi_cli)/(svi_all))*100,2) + round(((svi_ery)/(svi_all))*100,2) \
                + round(((svi_lnz)/(svi_all))*100,2) + round(((svi_pen)/(svi_all))*100,2) + round(((svi_van)/(svi_all))*100,2)) / 8),2) if svi_all > 0 else 0
      
    svi_summary = ['Streptococcus Viridans Group',svi_all,str(tmp_svi) + '%']
    
    ret.append(df)
    if svi_all > 0:
        ret.append(svi_summary)
        ret.append(tmp_svi)

    
    return ret



def get_data_bsn(file_id):
    df = concat_all_df(file_id)
    comp = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_org_list.xlsx','bsn')
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
    
    
    bsn_all = 0
    bsn_amp_pen = 0
    bsn_fep_ctx_cro = 0
    bsn_chl = 0
    bsn_cli = 0
    bsn_dap = 0
    bsn_ery = 0
    bsn_lev = 0
    bsn_lnz = 0
    bsn_van = 0
    
    for index,row in df.iterrows():
        if row['organism'] in cmp:
                bsn_all += 1
                if (row['amp_nd10'] != '' or row['amp_nm'] != '') or (row['pen_nd10'] != '' or row['pen_nm'] != ''):
                    bsn_amp_pen += 1
                if (row['fep_nd30'] != '' or row['fep_nm'] != '') or (row['ctx_nd30'] != '' or row['ctx_nm'] != '') or (row['cro_nd30'] != '' or row['cro_nm'] != ''):
                    bsn_fep_ctx_cro += 1
                if row['chl_nd30'] != '' or row['chl_nm'] != '':
                    bsn_chl += 1 
                if row['cli_nd2'] != '' or row['cli_nm'] != '':
                    bsn_cli += 1
                if row['dap_nd30'] != '' or row['dap_nm'] != '':
                    bsn_dap += 1
                if row['ery_nd15'] != '' or row['ery_nm'] != '':
                    bsn_ery += 1
                if row['lvx_nd5'] != '' or row['lvx_nm'] != '':
                    bsn_lev += 1
                if row['lnz_nd30'] != '' or row['lnz_nm'] != '':
                    bsn_lnz += 1
                if row['van_nd30'] != '' or row['van_nm'] != '':
                    bsn_van += 1  
    
    bsn_data = [['Antibiotic','Number tested','Percentage'],
                  ['1. Ampicillin or Penicillin',bsn_amp_pen,str(  round(((bsn_amp_pen)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['2. Cefepime or Cefotaxime or Cetriaxone',bsn_fep_ctx_cro,str(  round(((bsn_fep_ctx_cro)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['3. Chloramphenicol',bsn_chl,str(  round(((bsn_chl)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['4. Clindamycin',bsn_cli,str(  round(((bsn_cli)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['5. Daptomycin',bsn_dap,str(  round(((bsn_dap)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['6. Erythromycin',bsn_ery,str(  round(((bsn_ery)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['7. Levofloxacin',bsn_lev,str(  round(((bsn_lev)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['8. Linezolid',bsn_lnz,str(  round(((bsn_lnz)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%'],
                  ['9. Vancomycin',bsn_van,str(  round(((bsn_van)/(bsn_all))*100,2) ) + "%" if bsn_all > 0 else '0%']
                  ]
    
    ret = []
    df = pd.DataFrame(data=bsn_data, columns=['Beta-Hemolytic Streptococci','Number',bsn_all])
    
    tmp_bsn = round(((round(((bsn_amp_pen)/(bsn_all))*100,2) +  round(((bsn_fep_ctx_cro)/(bsn_all))*100,2) + round(((bsn_chl)/(bsn_all))*100,2) + round(((bsn_cli)/(bsn_all))*100,2) + round(((bsn_dap)/(bsn_all))*100,2) \
                + round(((bsn_ery)/(bsn_all))*100,2) + round(((bsn_lev)/(bsn_all))*100,2) + round(((bsn_lnz)/(bsn_all))*100,2) + round(((bsn_van)/(bsn_all))*100,2)) / 9),2) if bsn_all > 0 else 0
      
    bsn_summary = ['Beta-Hemolytic Streptococci',bsn_all,str(tmp_bsn) + '%']
    
    ret.append(df)
    if bsn_all > 0:
        ret.append(bsn_summary)
        ret.append(tmp_bsn)
    
    
    return ret       


def get_mrsa_esbl(file_id):
    df = concat_all_df(file_id)
    
    df = df[ df['spec_type'].str.lower() != 'qc' ]
    df = df[ df['spec_type'].str.lower() != 'en' ]
    df = df[ df['spec_type'].str.lower() != 'wa' ]
    df = df[ df['spec_type'].str.lower() != 'fo' ]
    df = df[ df['spec_type'].str.lower() != 'mi' ]
    
    
    eco_all = 0
    eco_nega = 0
    eco_posi = 0
    eco_no = 0
    
    kpn_all = 0
    kpn_nega = 0
    kpn_posi = 0
    kpn_no = 0
    
    sau_all = 0
    sau_nega = 0
    sau_posi = 0
    sau_no = 0
    for index,row in df.iterrows():
        if row['organism'] == 'eco':
                eco_all += 1
                if row['esbl'] == '+':
                    eco_posi += 1
                if row['esbl'] == '-':
                    eco_nega += 1
                if row['esbl'] == '':
                    eco_no += 1
        
        if row['organism'] == 'kpn':
                kpn_all += 1
                if row['esbl'] == '+':
                    kpn_posi += 1
                if row['esbl'] == '-':
                    kpn_nega += 1
                if row['esbl'] == '':
                    kpn_no += 1
        
        if row['organism'] == 'sau':
                sau_all += 1
                if row['mrsa'] == '+':
                    sau_posi += 1
                if row['mrsa'] == '-':
                    sau_nega += 1
                if row['mrsa'] == '':
                    sau_no += 1
                    
    esbl_all = eco_all + kpn_all
    esbl_posi = eco_posi + kpn_posi
    esbl_nega = eco_nega + kpn_nega
    esbl_data = ['ESBL for K. pnuemonia and E. coli',esbl_all,str( round( ((esbl_nega+esbl_posi) / esbl_all) * 100 ,2  )) + '%' if esbl_all > 0 else '0%']
    
    
    mrsa_data = ['MRSA',sau_all,str( round( ((sau_nega+sau_posi) / sau_all) * 100 ,2  )) + '%' if sau_all > 0 else '0%']
    
    ret  = [esbl_data,mrsa_data]
    
    return ret




'''
END OF DATA SUMMARY REPORTS
'''




















def import_raw_data(row_iter,file_name):
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
            
            fos_nd200 = row['FOS_ND200'],
            
            dox_nd30 = row['DOX_ND30'],
            
            sss_nd200 = row['SSS_ND200'],
            
            
            
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
            
            van_nm = row['VAN_NM'],
            
            fos_nm = row['FOS_NM'],
            
            dox_nm = row['DOX_NM'],
            
            sss_nm = row['SSS_NM'],
        )
        
        ant_mic.save()
        
        ant_est = RawAntietest(
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



# functions that will be used on lambda
# lambda function for origin
def origin_transform(row,lab_chk,whonet_region_island):
    
    if row['laboratory'].upper() in lab_chk:
        row['region'] = whonet_region_island['REGION'][lab_chk.index(row['laboratory'])]
        row['island'] = whonet_region_island['ISLAND'][lab_chk.index(row['laboratory'])]
    else:
        row['region'] = ''
        row['island'] = ''
    
    if pd.isna(row['age']) == True or row['age'] == '':
            # age.append('U')
            row['age_grp'] = 'U'
        
    elif 'w' in str(row['age']) or 'W' in str(row['age']) or 'd' in str(row['age']) or 'D' in str(row['age']) or 'm' in str(row['age']) or 'M' in str(row['age']) or 'nb' in str(row['age']) or 'NB' in str(row['age']) or 'y' in str(row['age']):
            # age.append('A')
            row['age_grp'] = 'A'
    elif row['age'] == 'nan':
            row['age_grp'] = 'U'  
        
    elif float(row['age']) >= 0 and float(row['age']) <= 5:
            row['age_grp'] = 'A'
        
    elif float(row['age']) >= 6 and float(row['age']) <= 17:
            row['age_grp'] = 'B'
        
    elif float(row['age']) > 17 and float(row['age']) <= 64:
            row['age_grp'] = 'C'
        
    elif float(row['age']) > 64:
            row['age_grp'] = 'D'
        
    else:
            row['age_grp'] = 'U'
    
    
    return row


def patient_id_transform(row):
    if row['patient_id'] == '7777777' or row['patient_id'] == 7777777:
        row['patient_id'] = ''
        
    
    return row

def summary_err_gender(row):
    sex = ['m','f']
    if row['sex'] not in sex:
        return row
    
def summary_err_org(row):
    if row['organism'] not in org_list:
        return row

def summary_err_spec_type(row):
    if row['spec_type'] not in spec_list:
        return row














@login_required(login_url='/arsp_dmu/login')
@permission_required('whonet.add_rawfilename', raise_exception=True)
def old_referred_import(request):
    if request.method == 'POST':
        raw_data = request.FILES.getlist('raw_data')           
        # raw data import
        results = []
        
        for p in raw_data:
            results.append(import_old(p))
        
    
        return render(request, 'whonet/old_referred.html',{'multi_import' : results})
    else:
        return render(request,'whonet/old_referred.html')
        

def import_old(raw_data):
    try:
        df = pd.read_csv(raw_data,encoding='iso-8859-1')
    except:
        return 'File ' + raw_data.name + ' is invalid format'
    
    tmp_name = raw_data.name

    file_name = OldFileName(file_name=tmp_name.split('.')[0])
    df = set_old_pd_columns(df)
    row_iter = df.iterrows()
    try:
        file_name.save()
    except IntegrityError as e:
        file_name = OldFileName.objects.get(file_name=tmp_name.split('.')[0])
        file_name.updated_at = datetime.now()
        file_name.save()
        OldOrigin.objects.select_related('oldlocation','oldmicrobiology','oldspecimen','oldantidisk','oldantimic','oldantidiskris','oldantimicris').filter(file_ref=file_name).delete()
        import_old_data(row_iter,file_name)
        
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded. System updated the file.'

    try:
        import_old_data(row_iter,file_name)
        return 'File ' + tmp_name.split('.')[0]  +' successfully uploaded.'
     
    except IntegrityError as e:
        return 'File ' + tmp_name.split('.')[0] + ' is already uploaded.'



def set_old_pd_columns(clm):
    
    whonet_data_fields = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','RIS')
    # whonet_data_fields_etest = pd.read_excel(dirpath + '/whonet/static/whonet_xl/whonet_data_fields.xlsx','etest')
    data_fields = whonet_data_fields['Data fields'].values.tolist()
    # etest = whonet_data_fields_etest['Data fields'].values.tolist()
    # etest = [x.lower() for x in etest]
    
    for col in data_fields:
        if col not in clm.columns:
            clm[col] = ''

    
    return clm



def import_old_data(row_iter,file_name):
    for index, row in  row_iter:

        origin = OldOrigin(
        
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


        loc = OldLocation(

            origin_ref = origin,

            ward = row['WARD'],

            institut = row['INSTITUT'],

            department = row['DEPARTMENT'],

            ward_type = row['WARD_TYPE'],

        )

        loc.save()
        
        mic = OldMicrobiology(
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
            
            arsrl_pre = row['ARSRL_PRE'],
            
            arsrl_final = row['ARSRL_FINAL'],
            
            arsrl_post = row['ARSRL_POST'],
        
            x_esbl_ct = row['X_ESBL_CT'],
            
            x_esbl_tz = row['X_ESBL_TZ'],
            
            x_ip_ipi = row['X_IP_IPI'],
            
            x_cn_cni = row['X_CN_CNI'],
            
            edta = row['EDTA'],
        )
        
        mic.save()
        
        spec = OldSpecimen(
            origin_ref = origin,
            
            spec_num = row['SPEC_NUM'],
            
            spec_date = row['SPEC_DATE'],
            
            spec_type = row['SPEC_TYPE'],
            
            spec_code = row['SPEC_CODE'],
            
            local_spec = row['LOCAL_SPEC'],
            
            date_refer = row['DATE_REFER'],
            
            reason = row['REASON'],
        )
        
        spec.save()
        
        ant_disk = OldAntidisk(
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
        
        ant_disk_ris = OldAntidiskris(
                origin_ref = origin,
                
                amk_nd30_ris = row['AMK_ND30_RIS'],
                
                amc_nd20_ris = row['AMC_ND20_RIS'],
                
                amp_nd10_ris = row['AMP_ND10_RIS'],
                
                sam_nd10_ris = row['SAM_ND10_RIS'],
                
                azm_nd15_ris = row['AZM_ND15_RIS'],
                
                atm_nd30_ris = row['ATM_ND30_RIS'],
                
                cec_nd30_ris = row['CEC_ND30_RIS'],
                
                man_nd30_ris = row['MAN_ND30_RIS'],
                
                czo_nd30_ris = row['CZO_ND30_RIS'],
                
                fep_nd30_ris = row['FEP_ND30_RIS'],
                
                cfm_nd5_ris = row['CFM_ND5_RIS'],
                
                cfp_nd75_ris = row['CFP_ND75_RIS'],
                
                ctx_nd30_ris = row['CTX_ND30_RIS'],
                
                fox_nd30_ris = row['FOX_ND30_RIS'],
                
                caz_nd30_ris = row['CAZ_ND30_RIS'],
                
                cro_nd30_ris = row['CRO_ND30_RIS'],
                
                cxm_nd30_ris = row['CXM_ND30_RIS'],
                
                cxa_nd30_ris = row['CXA_ND30_RIS'],
                
                cep_nd30_ris = row['CEP_ND30_RIS'],
                
                chl_nd30_ris = row['CHL_ND30_RIS'],
                
                cip_nd5_ris = row['CIP_ND5_RIS'],
                
                clr_nd15_ris = row['CLR_ND15_RIS'],
                
                cli_nd2_ris = row['CLI_ND2_RIS'],
                
                col_nd10_ris = row['COL_ND10_RIS'],
                
                sxt_nd1_2_ris = row['SXT_ND1_2_RIS'],
                
                dap_nd30_ris = row['DAP_ND30_RIS'],
                
                dor_nd10_ris = row['DOR_ND10_RIS'],
                
                etp_nd10_ris = row['ETP_ND10_RIS'],
                
                ery_nd15_ris = row['ERY_ND15_RIS'],
                
                gen_nd10_ris = row['GEN_ND10_RIS'],
                
                geh_nd120_ris = row['GEH_ND120_RIS'],
                
                ipm_nd10_ris = row['IPM_ND10_RIS'],
                
                kan_nd30_ris = row['KAN_ND30_RIS'],
                
                lvx_nd5_ris = row['LVX_ND5_RIS'],
                
                lnz_nd30_ris = row['LNZ_ND30_RIS'],
                
                mem_nd10_ris = row['MEM_ND10_RIS'],
                
                mno_nd30_ris = row['MNO_ND30_RIS'],
                
                mfx_nd5_ris = row['MFX_ND5_RIS'],
                
                nal_nd30_ris = row['NAL_ND30_RIS'],
                
                net_nd30_ris = row['NET_ND30_RIS'],
                
                nit_nd300_ris = row['NIT_ND300_RIS'],
                
                nor_nd10_ris = row['NOR_ND10_RIS'],
                
                nov_nd5_ris = row['NOV_ND5_RIS'],
                
                ofx_nd5_ris = row['OFX_ND5_RIS'],
                
                oxa_nd1_ris = row['OXA_ND1_RIS'],
                
                pen_nd10_ris = row['PEN_ND10_RIS'],
                
                pip_nd100_ris = row['PIP_ND100_RIS'],
                
                tzp_nd100_ris = row['TZP_ND100_RIS'],
                
                pol_nd300_ris = row['POL_ND300_RIS'],
                
                qda_nd15_ris = row['QDA_ND15_RIS'],
                
                rif_nd5_ris = row['RIF_ND5_RIS'],
                
                spt_nd100_ris = row['SPT_ND100_RIS'],
                
                str_nd10_ris = row['STR_ND10_RIS'],
                
                sth_nd300_ris = row['STH_ND300_RIS'],
                
                tcy_nd30_ris = row['TCY_ND30_RIS'],
                
                tic_nd75_ris = row['TIC_ND75_RIS'],
                
                tcc_nd75_ris = row['TCC_ND75_RIS'],
                
                tgc_nd15_ris = row['TGC_ND15_RIS'],
                
                tob_nd10_ris = row['TOB_ND10_RIS'],
                
                van_nd30_ris = row['VAN_ND30_RIS'],
                
                fos_nd200_ris = row['FOS_ND200_RIS'],
                
                dox_nd30_ris = row['DOX_ND30_RIS'],
                
                sss_nd200_ris = row['SSS_ND200_RIS'],
                
                
                
            )
        
        ant_disk_ris.save()
        
        ant_mic = OldAntimic(
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
        
        ant_micris = OldAntimicris(
            origin_ref = origin,
            
            amk_nm_ris = row['AMK_NM_RIS'],
            
            amc_nm_ris = row['AMC_NM_RIS'],
            
            amp_nm_ris = row['AMP_NM_RIS'],
            
            sam_nm_ris = row['SAM_NM_RIS'],
            
            azm_nm_ris = row['AZM_NM_RIS'],
            
            atm_nm_ris = row['ATM_NM_RIS'],
            
            cec_nm_ris = row['CEC_NM_RIS'],
            
            man_nm_ris = row['MAN_NM_RIS'],
            
            czo_nm_ris = row['CZO_NM_RIS'],
            
            fep_nm_ris = row['FEP_NM_RIS'],
            
            cfm_nm_ris = row['CFM_NM_RIS'],
            
            cfp_nm_ris = row['CFP_NM_RIS'],
            
            ctx_nm_ris = row['CTX_NM_RIS'],
            
            fox_nm_ris = row['FOX_NM_RIS'],
            
            caz_nm_ris = row['CAZ_NM_RIS'],
            
            cro_nm_ris = row['CRO_NM_RIS'],
            
            cxm_nm_ris = row['CXM_NM_RIS'],
            
            cxa_nm_ris = row['CXA_NM_RIS'],
            
            cep_nm_ris = row['CEP_NM_RIS'],
            
            chl_nm_ris = row['CHL_NM_RIS'],
            
            cip_nm_ris = row['CIP_NM_RIS'],
            
            clr_nm_ris = row['CLR_NM_RIS'],
            
            cli_nm_ris = row['CLI_NM_RIS'],
            
            col_nm_ris = row['COL_NM_RIS'],
            
            sxt_nm_ris = row['SXT_NM_RIS'],
            
            dap_nm_ris = row['DAP_NM_RIS'],
            
            dor_nm_ris = row['DOR_NM_RIS'],
            
            etp_nm_ris = row['ETP_NM_RIS'],
            
            ery_nm_ris = row['ERY_NM_RIS'],
            
            gen_nm_ris = row['GEN_NM_RIS'],
            
            geh_nm_ris = row['GEH_NM_RIS'],
            
            ipm_nm_ris = row['IPM_NM_RIS'],
            
            kan_nm_ris = row['KAN_NM_RIS'],
            
            lvx_nm_ris = row['LVX_NM_RIS'],
            
            lnz_nm_ris = row['LNZ_NM_RIS'],
            
            mem_nm_ris = row['MEM_NM_RIS'],
            
            mno_nm_ris = row['MNO_NM_RIS'],
            
            mfx_nm_ris = row['MFX_NM_RIS'],
            
            nal_nm_ris = row['NAL_NM_RIS'],
            
            net_nm_ris = row['NET_NM_RIS'],
            
            nit_nm_ris = row['NIT_NM_RIS'],
            
            nor_nm_ris = row['NOR_NM_RIS'],
            
            nov_nm_ris = row['NOV_NM_RIS'],
            
            ofx_nm_ris = row['OFX_NM_RIS'],
            
            oxa_nm_ris = row['OXA_NM_RIS'],
            
            pen_nm_ris= row['PEN_NM_RIS'],
            
            pip_nm_ris = row['PIP_NM_RIS'],
            
            tzp_nm_ris = row['TZP_NM_RIS'],
            
            pol_nm_ris = row['POL_NM_RIS'],
            
            qda_nm_ris = row['QDA_NM_RIS'],
            
            rif_nm_ris = row['RIF_NM_RIS'],
            
            spt_nm_ris = row['SPT_NM_RIS'],
            
            str_nm_ris = row['STR_NM_RIS'],
            
            sth_nm_ris = row['STH_NM_RIS'],
            
            tcy_nm_ris = row['TCY_NM_RIS'],
            
            tic_nm_ris = row['TIC_NM_RIS'],
            
            tcc_nm_ris = row['TCC_NM_RIS'],
            
            tgc_nm_ris = row['TGC_NM_RIS'],
            
            tob_nm_ris = row['TOB_NM_RIS'],
            
            van_nm_ris = row['VAN_NM_RIS'],
            
            fos_nm_ris = row['FOS_NM_RIS'],
            
            dox_nm_ris = row['DOX_NM_RIS'],
            
            sss_nm_ris = row['SSS_NM_RIS'],
        )
        
        ant_micris.save()