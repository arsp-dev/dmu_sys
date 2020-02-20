from django.db import models

class RawFileName(models.Model):
    file_name = models.TextField(null=True,blank=True,default=None,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name
    

class RawOrigin(models.Model):
    file_ref = models.ForeignKey(RawFileName, on_delete=models.CASCADE)
    country_a = models.TextField(null=True,blank=True,default=None)
    region = models.TextField(null=True,blank=True,default=None)
    island = models.TextField(null=True,blank=True,default=None)
    laboratory = models.TextField(null=True,blank=True,default=None)
    patient_id = models.TextField(null=True,blank=True,default=None)
    first_name = models.TextField(null=True,blank=True,default=None)
    mid_name = models.TextField(null=True,blank=True,default=None)
    last_name = models.TextField(null=True,blank=True,default=None)
    sex = models.TextField(null=True,blank=True,default=None)
    age = models.TextField(null=True,blank=True,default=None)
    date_birth = models.TextField(null=True,blank=True,default=None)
    age_grp = models.TextField(null=True,blank=True,default=None)
    pat_type = models.TextField(null=True,blank=True,default=None)
    date_data = models.TextField(null=True,blank=True,default=None)
    x_referred = models.TextField(null=True,blank=True,default=None)
    x_recnum = models.TextField(null=True,blank=True,default=None)
    date_admis = models.TextField(null=True,blank=True,default=None)
    nosocomial = models.TextField(null=True,blank=True,default=None)
    diagnosis = models.TextField(null=True,blank=True,default=None)
    stock_num = models.TextField(null=True,blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_ref

class RawLocation(models.Model):
    origin_ref = models.OneToOneField(RawOrigin,  on_delete = models.CASCADE, primary_key = True) 
    ward = models.TextField(null=True,blank=True,default=None)
    institut = models.TextField(null=True,blank=True,default=None)
    department = models.TextField(null=True,blank=True,default=None)
    ward_type = models.TextField(null=True,blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ward



class RawMicrobiology(models.Model):
    origin_ref = models.OneToOneField(RawOrigin,  on_delete = models.CASCADE, primary_key = True) 
    organism = models.TextField(null=True,blank=True,default=None)
    org_type = models.TextField(null=True,blank=True,default=None)
    beta_lact = models.TextField(null=True,blank=True,default=None)
    comment = models.TextField(null=True,blank=True,default=None)
    mrsa = models.TextField(null=True,blank=True,default=None)
    induc_cli = models.TextField(null=True,blank=True,default=None)
    meca = models.TextField(null=True,blank=True,default=None)
    ampc = models.TextField(null=True,blank=True,default=None)
    x_mrse = models.TextField(null=True,blank=True,default=None)
    x_carb = models.TextField(null=True,blank=True,default=None)
    esbl = models.TextField(null=True,blank=True,default=None)
    urine_count = models.TextField(null=True,blank=True,default=None)
    serotype = models.TextField(null=True,blank=True,default=None)
    carbapenem = models.TextField(null=True,blank=True,default=None)
    mbl = models.TextField(null=True,blank=True,default=None)
    growth = models.TextField(null=True,blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organism
    

class RawSpecimen(models.Model):
    origin_ref = models.OneToOneField(RawOrigin,  on_delete = models.CASCADE, primary_key = True) 
    spec_num = models.TextField(null=True,blank=True,default=None)
    spec_date = models.TextField(null=True,blank=True,default=None)
    spec_type = models.TextField(null=True,blank=True,default=None)
    spec_code = models.TextField(null=True,blank=True,default=None)
    local_spec = models.TextField(null=True,blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.spec_type



class RawAntidisk(models.Model):
    origin_ref = models.OneToOneField(RawOrigin,  on_delete = models.CASCADE, primary_key = True) 
    amk_nd30 = models.TextField(null=True,blank=True,default=None)
    amc_nd20 = models.TextField(null=True,blank=True,default=None)
    amp_nd10 = models.TextField(null=True,blank=True,default=None)
    sam_nd10 = models.TextField(null=True,blank=True,default=None)
    azm_nd15 = models.TextField(null=True,blank=True,default=None)
    atm_nd30 = models.TextField(null=True,blank=True,default=None)
    cec_nd30 = models.TextField(null=True,blank=True,default=None)
    man_nd30 = models.TextField(null=True,blank=True,default=None)
    czo_nd30 = models.TextField(null=True,blank=True,default=None)
    fep_nd30 = models.TextField(null=True,blank=True,default=None)
    cfm_nd5 = models.TextField(null=True,blank=True,default=None)
    cfp_nd75 = models.TextField(null=True,blank=True,default=None)
    ctx_nd30 = models.TextField(null=True,blank=True,default=None)
    fox_nd30 = models.TextField(null=True,blank=True,default=None)
    caz_nd30 = models.TextField(null=True,blank=True,default=None)
    cro_nd30 = models.TextField(null=True,blank=True,default=None)
    cxm_nd30 = models.TextField(null=True,blank=True,default=None)
    cxa_nd30 = models.TextField(null=True,blank=True,default=None)
    cep_nd30 = models.TextField(null=True,blank=True,default=None)
    chl_nd30 = models.TextField(null=True,blank=True,default=None)
    cip_nd5 = models.TextField(null=True,blank=True,default=None)
    clr_nd15 = models.TextField(null=True,blank=True,default=None)
    cli_nd2 = models.TextField(null=True,blank=True,default=None)
    col_nd10 = models.TextField(null=True,blank=True,default=None)
    sxt_nd1_2 = models.TextField(null=True,blank=True,default=None)
    dap_nd30 = models.TextField(null=True,blank=True,default=None)
    dor_nd10 = models.TextField(null=True,blank=True,default=None)
    etp_nd10 = models.TextField(null=True,blank=True,default=None)
    ery_nd15 = models.TextField(null=True,blank=True,default=None)
    gen_nd10 = models.TextField(null=True,blank=True,default=None)
    geh_nd120 = models.TextField(null=True,blank=True,default=None)
    ipm_nd10 = models.TextField(null=True,blank=True,default=None)
    kan_nd30 = models.TextField(null=True,blank=True,default=None)
    lvx_nd5 = models.TextField(null=True,blank=True,default=None)
    lnz_nd30 = models.TextField(null=True,blank=True,default=None)
    mem_nd10 = models.TextField(null=True,blank=True,default=None)
    mno_nd30 = models.TextField(null=True,blank=True,default=None)
    mfx_nd5 = models.TextField(null=True,blank=True,default=None)
    nal_nd30 = models.TextField(null=True,blank=True,default=None)
    net_nd30 = models.TextField(null=True,blank=True,default=None)
    nit_nd300 = models.TextField(null=True,blank=True,default=None)
    nor_nd10 = models.TextField(null=True,blank=True,default=None)
    nov_nd5 = models.TextField(null=True,blank=True,default=None)
    ofx_nd5 = models.TextField(null=True,blank=True,default=None)
    oxa_nd1 = models.TextField(null=True,blank=True,default=None)
    pen_nd10 = models.TextField(null=True,blank=True,default=None)
    pip_nd100 = models.TextField(null=True,blank=True,default=None)
    tzp_nd100 = models.TextField(null=True,blank=True,default=None)
    pol_nd300 = models.TextField(null=True,blank=True,default=None)
    qda_nd15 = models.TextField(null=True,blank=True,default=None)
    rif_nd5 = models.TextField(null=True,blank=True,default=None)
    spt_nd100 = models.TextField(null=True,blank=True,default=None)
    str_nd10 = models.TextField(null=True,blank=True,default=None)
    sth_nd300 = models.TextField(null=True,blank=True,default=None)
    tcy_nd30 = models.TextField(null=True,blank=True,default=None)
    tic_nd75 = models.TextField(null=True,blank=True,default=None)
    tcc_nd75 = models.TextField(null=True,blank=True,default=None)
    tgc_nd15 = models.TextField(null=True,blank=True,default=None)
    tob_nd10 = models.TextField(null=True,blank=True,default=None)
    van_nd30 = models.TextField(null=True,blank=True,default=None)
    fos_nd200 = models.TextField(null=True,blank=True,default=None)
    dox_nd30 = models.TextField(null=True,blank=True,default=None)
    sss_nd200 = models.TextField(null=True,blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.origin_ref
    

class RawAntimic(models.Model):
    origin_ref = models.OneToOneField(RawOrigin,  on_delete = models.CASCADE, primary_key = True) 
    amk_nm = models.TextField(null=True,blank=True,default=None)
    amc_nm = models.TextField(null=True,blank=True,default=None)
    amp_nm = models.TextField(null=True,blank=True,default=None)
    sam_nm = models.TextField(null=True,blank=True,default=None)
    azm_nm = models.TextField(null=True,blank=True,default=None)
    atm_nm = models.TextField(null=True,blank=True,default=None)
    cec_nm = models.TextField(null=True,blank=True,default=None)
    man_nm = models.TextField(null=True,blank=True,default=None)
    czo_nm = models.TextField(null=True,blank=True,default=None)
    fep_nm = models.TextField(null=True,blank=True,default=None)
    cfm_nm = models.TextField(null=True,blank=True,default=None)
    cfp_nm = models.TextField(null=True,blank=True,default=None)
    ctx_nm = models.TextField(null=True,blank=True,default=None)
    fox_nm = models.TextField(null=True,blank=True,default=None)
    caz_nm = models.TextField(null=True,blank=True,default=None)
    cro_nm = models.TextField(null=True,blank=True,default=None)
    cxm_nm = models.TextField(null=True,blank=True,default=None)
    cxa_nm = models.TextField(null=True,blank=True,default=None)
    cep_nm = models.TextField(null=True,blank=True,default=None)
    chl_nm = models.TextField(null=True,blank=True,default=None)
    cip_nm = models.TextField(null=True,blank=True,default=None)
    clr_nm = models.TextField(null=True,blank=True,default=None)
    cli_nm = models.TextField(null=True,blank=True,default=None)
    col_nm = models.TextField(null=True,blank=True,default=None)
    sxt_nm = models.TextField(null=True,blank=True,default=None)
    dap_nm = models.TextField(null=True,blank=True,default=None)
    dor_nm = models.TextField(null=True,blank=True,default=None)
    etp_nm = models.TextField(null=True,blank=True,default=None)
    ery_nm = models.TextField(null=True,blank=True,default=None)
    gen_nm = models.TextField(null=True,blank=True,default=None)
    geh_nm = models.TextField(null=True,blank=True,default=None)
    ipm_nm = models.TextField(null=True,blank=True,default=None)
    kan_nm = models.TextField(null=True,blank=True,default=None)
    lvx_nm = models.TextField(null=True,blank=True,default=None)
    lnz_nm = models.TextField(null=True,blank=True,default=None)
    mem_nm = models.TextField(null=True,blank=True,default=None)
    mno_nm = models.TextField(null=True,blank=True,default=None)
    mfx_nm = models.TextField(null=True,blank=True,default=None)
    nal_nm = models.TextField(null=True,blank=True,default=None)
    net_nm = models.TextField(null=True,blank=True,default=None)
    nit_nm = models.TextField(null=True,blank=True,default=None)
    nor_nm = models.TextField(null=True,blank=True,default=None)
    nov_nm = models.TextField(null=True,blank=True,default=None)
    ofx_nm = models.TextField(null=True,blank=True,default=None)
    oxa_nm = models.TextField(null=True,blank=True,default=None)
    pen_nm = models.TextField(null=True,blank=True,default=None)
    pip_nm = models.TextField(null=True,blank=True,default=None)
    tzp_nm = models.TextField(null=True,blank=True,default=None)
    pol_nm = models.TextField(null=True,blank=True,default=None)
    qda_nm = models.TextField(null=True,blank=True,default=None)
    rif_nm = models.TextField(null=True,blank=True,default=None)
    spt_nm = models.TextField(null=True,blank=True,default=None)
    str_nm = models.TextField(null=True,blank=True,default=None)
    sth_nm = models.TextField(null=True,blank=True,default=None)
    tcy_nm = models.TextField(null=True,blank=True,default=None)
    tic_nm = models.TextField(null=True,blank=True,default=None)
    tcc_nm = models.TextField(null=True,blank=True,default=None)
    tgc_nm = models.TextField(null=True,blank=True,default=None)
    tob_nm = models.TextField(null=True,blank=True,default=None)
    van_nm = models.TextField(null=True,blank=True,default=None)
    fos_nm = models.TextField(null=True,blank=True,default=None)
    dox_nm = models.TextField(null=True,blank=True,default=None)
    sss_nm = models.TextField(null=True,blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.origin_ref
    
    
    
    