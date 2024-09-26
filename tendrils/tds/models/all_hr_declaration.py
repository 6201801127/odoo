from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from odoo.addons import decimal_precision as dp

class FiscalYearFilter(models.TransientModel):
    _name = 'fiscal_year_filter_wizard'
    _description = 'IT Declaration Wizard For Fiscal Year'


    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always')

    def get_yearly_declarations(self):
        if self.date_range:
            total_emp = self.env['hr.employee'].sudo().search(['|',('active','=',True),('active','=',False)])
            active_true_emp =  total_emp.filtered(lambda x:x.active==True and x.date_of_joining <= self.date_range.date_stop and x.employement_type.code != 'O').ids
            active_false_emp =  total_emp.filtered(lambda x:x.active==False and x.employement_type.code != 'O')
            active_false_emp = active_false_emp.filtered(lambda x:x.date_of_joining <= self.date_range.date_stop  if x.date_of_joining else None)
            active_false_emp = active_false_emp.filtered(lambda x:x.last_working_day <=  self.date_range.date_stop if x.last_working_day else None).ids
            total_employees = active_true_emp + active_false_emp
            view_id = self.env.ref('tds.yearly_hr_declaration_view_tree').id
            rc = {
                'name': 'Yearly IT Declaration',
                'type': 'ir.actions.act_window',
                'res_model': 'yearly_hr_declaration',
                'view_id': view_id,
                'view_mode': 'tree',
                'view_type': 'form',
                'domain': [('date_range','=',self.date_range.id)],
                'target': 'self',
            }
            if total_employees:
                query = ''
                for emp in total_employees:
                    payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', emp),('state', '=', 'done'),('date_to','>=',self.date_range.date_start),('date_to','<=',self.date_range.date_stop)])
                    payslip_basic = 0
                    for line in payslip:
                        payslip_basic = sum(line.line_ids.filtered(lambda x:x.code=='BASIC').mapped('amount'))
                    contract = self.env['hr.contract'].sudo().search([('employee_id', '=', emp)],order='id desc' , limit=1)
                    if contract and payslip and payslip_basic > 0:
                        ctc = contract.wage
                        yearly_ctc = ctc * 12
                        # if yearly_ctc >= 500000:
                        yearly_dec = self.env['yearly_hr_declaration'].sudo().search(
                            [('employee_id', '=', emp), ('date_range', '=', self.date_range.id)])
                        if yearly_dec:
                            hr_declaration = self.env['hr.declaration'].sudo().search(
                                [('employee_id', '=', emp), ('date_range', '=', self.date_range.id)])
                            if hr_declaration:
                                if hr_declaration.state != 'approved':
                                    query += f"update yearly_hr_declaration set state='s' where id = {yearly_dec.id};"
                                else:
                                    query += f"update yearly_hr_declaration set state='c' where id = {yearly_dec.id};"
                            else:
                                query += f"update yearly_hr_declaration set state='ns' where id = {yearly_dec.id};"
                        else:
                            hr_declaration = self.env['hr.declaration'].sudo().search(
                                [('employee_id', '=', emp), ('date_range', '=', self.date_range.id)])
                            if hr_declaration:
                                if hr_declaration.state != 'approved':
                                    query += f"insert into yearly_hr_declaration (employee_id,date_range,state) values({emp},{self.date_range.id},'s');"
                                else:
                                    query += f"insert into yearly_hr_declaration (employee_id,date_range,state) values({emp},{self.date_range.id},'c');"
                            else:
                                query += f"insert into yearly_hr_declaration (employee_id,date_range,state) values({emp},{self.date_range.id},'ns');"
                if len(query) >0:
                    self._cr.execute(query)
                    
            return rc

    def delete_yearly_declarations(self):
        if self.date_range:
            query = f"delete from yearly_hr_declaration where date_range ={self.date_range.id}"
            self._cr.execute(query)
            self.env.user.notify_danger("Record Removed Successfully.")

    def delete_declarations(self):
        if self.date_range:
            query = f"delete from non_hr_declaration where date_range ={self.date_range.id}"
            self._cr.execute(query)
            self.env.user.notify_danger("Record Removed Successfully.")


    def get_no_declarations(self):
        if self.date_range:
            payslip_emp = self.env['hr.payslip'].sudo().search([('date_to','>=',self.date_range.date_start),('date_to','<=',self.date_range.date_stop),('state','=','done')]).mapped('employee_id.id')
            unique_emp = set(payslip_emp)
            total_employees = list(unique_emp)
            if total_employees:
                declarations = self.env['hr.declaration'].sudo().search([('employee_id','in',total_employees),('date_range','=',self.date_range.id)]).mapped('employee_id').ids
                non_declaration_emp = list(set(total_employees) - set(declarations))
                query1 = ''
                for var in non_declaration_emp:
                    payslip = self.env['hr.payslip'].sudo().search([('employee_id','=',var),('date_to','>=',self.date_range.date_start),('date_to','<=',self.date_range.date_stop),('state','=','done')])
                    if payslip:
                        query = f"SELECT (select {var}) as employee_id,1 as red,(select {self.date_range.id}) as date_range,sum(line.amount) FILTER (WHERE line.code = 'BASIC') as basic_salary,sum(line.amount) FILTER (WHERE line.code = 'HRAMN') as hra,sum(line.amount) FILTER (WHERE line.code = 'TDS') as tax_recovered,(select sum(line.amount) FILTER (WHERE line.code = 'GROSS')- sum(line.amount) FILTER (WHERE line.code ='BASIC') - sum(line.amount) FILTER (WHERE line.code = 'HRAMN')) as other_allowance,case when sum(line.amount) FILTER (WHERE line.code = 'GROSS') - sum(line.amount) FILTER (WHERE line.code = 'LWOP') > 0 then (SELECT sum(line.amount) FILTER (WHERE line.code = 'GROSS') - sum(line.amount) FILTER (WHERE line.code = 'LWOP')) else 0 end AS total, 0 as previous_employer_income_final,0 as hra_exemption,sum(line.amount) FILTER (WHERE line.code = 'PTD') as professional_tax,50000 as standard_deduction,case when sum(line.amount) FILTER (WHERE line.code = 'GROSS') - sum(line.amount) FILTER (WHERE line.code = 'LWOP') - sum(line.amount) FILTER (WHERE line.code = 'PTD') - 50000 > 0 then (SELECT sum(line.amount) FILTER (WHERE line.code = 'GROSS') - sum(line.amount) FILTER (WHERE line.code = 'LWOP') - sum(line.amount) FILTER (WHERE line.code = 'PTD') - 50000) else 0 end as income_from_salary, 0 as calculate_interest_payment,sum(line.amount) FILTER (WHERE line.code = 'EEPF') as allowed_rebate_under_80c, 0 as allowed_rebate_under_80ccd, sum(line.amount) FILTER (WHERE line.code = 'HID') as allowed_rebate_under_80d,0 as allowed_rebate_under_80dd, 0 as allowed_rebate_under_80e,0 as allowed_rebate_under_80g,sum(line.amount) FILTER (WHERE line.code in ('EEPF', 'HID')) as final_amount,0 as tds_previous_employer,0 as balance_tax_payable,'--' as housing_loan_institute, '--' as housing_loan_institute_pan,'--' as name_of_landlord,'--' as pan_of_landlord FROM hr_payslip p  JOIN hr_payslip_line line ON p.id = line.slip_id WHERE p.state = 'done' and p.employee_id= {var} and  p.date_to BETWEEN '{self.date_range.date_start}' and '{self.date_range.date_stop}';"
                        
                        self._cr.execute(query)
                        data_query = self._cr.dictfetchall()
                        for ids in data_query:
                            tax_recovered =ids['tax_recovered'] if ids['tax_recovered']!= None else 0
                            query1 += f"insert into non_hr_declaration (employee_id,basic_salary,hra,other_allowance,total,previous_employer_income_final,hra_exemption,professional_tax,standard_deduction,income_from_salary,calculate_interest_payment,gross_total_income,allowed_rebate_under_80c,allowed_rebate_under_80ccd,allowed_rebate_under_80d,allowed_rebate_under_80dd,allowed_rebate_under_80e,allowed_rebate_under_80g,final_amount,tds_by_company,balance_tax_payable,tax_regime,tax_payable,rebate,net_tax_payable,additional_sub_chrg,additional_edu_cess,total_tax_payable,tds_previous_employer,tax_recovered,red,housing_loan_institute,housing_loan_institute_pan,name_of_landlord,pan_of_landlord,date_range,state,final_amount_other_income) \
                            values({ids['employee_id']},{ids['basic_salary'] if ids['basic_salary'] != None else 0},{ids['hra'] if ids['hra'] != None else 0},{ids['other_allowance'] if ids['other_allowance'] != None else 0},{ids['total']if ids['total'] != None else 0},{ids['previous_employer_income_final'] if ids['previous_employer_income_final'] != None else 0},{ids['hra_exemption'] if ids['hra_exemption'] != None else 0},{ids['professional_tax'] if ids['professional_tax'] != None else 0},{ids['standard_deduction']},{ids['income_from_salary'] if ids['income_from_salary'] != None else 0},{ids['calculate_interest_payment'] if ids['calculate_interest_payment'] != None else 0},{ids['income_from_salary'] if ids['income_from_salary'] != None else 0},{ids['allowed_rebate_under_80c'] if ids['allowed_rebate_under_80c'] != None else 0},{ids['allowed_rebate_under_80ccd'] if ids['allowed_rebate_under_80ccd'] != None else 0},{ids['allowed_rebate_under_80d'] if ids['allowed_rebate_under_80d']!= None else 0},{ids['allowed_rebate_under_80dd'] if ids['allowed_rebate_under_80dd'] != None else 0},{ids['allowed_rebate_under_80e'] if ids['allowed_rebate_under_80e'] != None else 0},{ids['allowed_rebate_under_80g'] if ids['allowed_rebate_under_80g'] != None else 0},{ids['final_amount'] if ids['final_amount']!= None else 0},0,{ids['balance_tax_payable'] if ids['balance_tax_payable'] != None else 0},'old_regime',0,0,0,0,0,0,0,{tax_recovered},1,'{ids['housing_loan_institute']}','{ids['housing_loan_institute_pan']}','{ids['name_of_landlord']}','{ids['pan_of_landlord']}',{self.date_range.id},'not_submitted',0);"
                        
                
                # tds_by_company = ids['tds_by_company'] if ids['tds_by_company'] else 0
                tds = ''
                for employee in declarations:
                    tds += f"select date_range,(select 2) as red,tax_regime,employee_id,basic_salary,hra,professional_tax,standard_deduction,income_from_salary,calculate_interest_payment,gross_total_income,allowed_rebate_under_80c,allowed_rebate_under_80ccd,previous_employer_income_final,allowed_rebate_under_80d,allowed_rebate_under_80dd,allowed_rebate_under_80e,allowed_rebate_under_80g,final_amount,taxable_income,tax_payable,rebate,net_tax_payable,additional_sub_chrg,hra_exemption,additional_edu_cess,total_tax_payable,total,tds_previous_employer,tax_recovered,balance_tax_payable,housing_loan_institute,housing_loan_institute_pan,name_of_landlord,other_income as other_allowance,pan_of_landlord,state,final_amount_other_income from hr_declaration where date_range = {self.date_range.id} and employee_id = {employee};"
                    self._cr.execute(tds)
                    tds_data = self._cr.dictfetchall()
                    for ids in tds_data:
                        tds_previous_employer = ids['tds_previous_employer'] if ids['tds_previous_employer'] != None else 0
                        housing_loan_institute = ids['housing_loan_institute'] if ids['housing_loan_institute'] != None else '--'
                        housing_loan_institute_pan = ids['housing_loan_institute_pan'] if ids['housing_loan_institute_pan'] != None else '--'
                        name_of_landlord = ids['name_of_landlord'] if ids['name_of_landlord'] != None else '--'
                        pan_of_landlord = ids['pan_of_landlord'] if ids['pan_of_landlord'] != None else '--'
                        query1 += f"insert into non_hr_declaration (employee_id,\
                                    date_range,\
                                    basic_salary,\
                                    hra,\
                                    other_allowance,\
                                    total,\
                                    previous_employer_income_final,\
                                    hra_exemption,\
                                    professional_tax,\
                                    standard_deduction,\
                                    income_from_salary,\
                                    calculate_interest_payment,\
                                    gross_total_income,\
                                    allowed_rebate_under_80c,\
                                    allowed_rebate_under_80ccd,\
                                    allowed_rebate_under_80d,\
                                    allowed_rebate_under_80dd,\
                                    allowed_rebate_under_80e,\
                                    allowed_rebate_under_80g,\
                                    final_amount,\
                                    tds_by_company,\
                                    balance_tax_payable,\
                                    tax_regime,\
                                    tax_payable,\
                                    rebate,\
                                    net_tax_payable,\
                                    additional_sub_chrg,\
                                    additional_edu_cess,\
                                    total_tax_payable,\
                                    tds_previous_employer,\
                                    tax_recovered,\
                                    red,\
                                    housing_loan_institute,\
                                    housing_loan_institute_pan,\
                                    name_of_landlord,\
                                    pan_of_landlord, \
                                    state,final_amount_other_income)\
                            values({ids['employee_id']},\
                                    {self.date_range.id},\
                                    {ids['basic_salary'] if ids['basic_salary'] != None else 0},\
                                    {ids['hra'] if ids['hra'] != None else 0},\
                                    {ids['other_allowance'] if ids['other_allowance'] != None else 0},\
                                    {ids['total'] if ids['total'] != None else 0},\
                                    {ids['previous_employer_income_final'] if ids['previous_employer_income_final'] != None  else 0},\
                                    {ids['hra_exemption'] if ids['hra_exemption'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['professional_tax'] if ids['professional_tax'] != None and  ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['standard_deduction'] if ids['standard_deduction'] != None and  ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['income_from_salary'] if ids['income_from_salary'] != None else 0},\
                                    {ids['calculate_interest_payment'] if ids['calculate_interest_payment'] != None else 0},\
                                    {ids['gross_total_income'] if ids['gross_total_income'] != None else 0},\
                                    {ids['allowed_rebate_under_80c'] if ids['allowed_rebate_under_80c'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['allowed_rebate_under_80ccd'] if ids['allowed_rebate_under_80ccd'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['allowed_rebate_under_80d'] if ids['allowed_rebate_under_80d'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['allowed_rebate_under_80dd'] if ids['allowed_rebate_under_80dd'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['allowed_rebate_under_80e'] if ids['allowed_rebate_under_80e'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['allowed_rebate_under_80g'] if ids['allowed_rebate_under_80g'] != None and ids['tax_regime'] == 'old_regime' else 0},\
                                    {ids['final_amount'] if ids['final_amount'] != None else 0},\
                                    0,\
                                    {ids['balance_tax_payable'] if ids['balance_tax_payable'] != None else 0},\
                                    '{ids['tax_regime'] if ids['tax_regime'] != None else 0}',{ids['tax_payable'] if ids['tax_payable'] != None else 0},\
                                    {ids['rebate'] if ids['rebate'] != None else 0},\
                                    {ids['net_tax_payable'] if ids['net_tax_payable'] != None else 0},\
                                    {ids['additional_sub_chrg'] if ids['additional_sub_chrg'] != None else 0},\
                                    {ids['additional_edu_cess'] if ids['additional_edu_cess'] != None else 0},\
                                    {ids['total_tax_payable'] if ids['total_tax_payable'] != None else 0},\
                                    {tds_previous_employer},\
                                    {ids['tax_recovered'] if ids['tax_recovered'] != None else 0},2,\
                                    '{housing_loan_institute}',\
                                    '{housing_loan_institute_pan}',\
                                    '{name_of_landlord}',\
                                    '{pan_of_landlord}',\
                                     '{ids['state']}','{ids['final_amount_other_income']  if ids['final_amount_other_income'] != None else 0}');"
                
                self._cr.execute(query1)
            # return rc


class NonHrDeclaration(models.Model):
    _name = 'non_hr_declaration'
    _description = 'Non IT Declaration'

    employee_id = fields.Many2one('hr.employee',string="Employee")
    basic_salary = fields.Float('Basic')
    hra = fields.Float('HRA')
    other_allowance = fields.Float('Other')
    total = fields.Float('Total')
    previous_employer_income_final = fields.Float('Previous Income')
    hra_exemption = fields.Float('HRA')
    professional_tax = fields.Float('Professional Tax')
    standard_deduction = fields.Float('Standard Deduction')
    income_from_salary = fields.Float('Income')
    calculate_interest_payment = fields.Float('Interest')
    gross_total_income = fields.Float('Gross')
    allowed_rebate_under_80c = fields.Float('80C')
    allowed_rebate_under_80ccd = fields.Float('80CCD')
    allowed_rebate_under_80d = fields.Float('80D')
    allowed_rebate_under_80dd = fields.Float('80DD')
    allowed_rebate_under_80e = fields.Float('80E')
    allowed_rebate_under_80g = fields.Float('80G')
    final_amount = fields.Float('Final Amount')
    tds_by_company = fields.Float('TDS')
    tds_previous_employer = fields.Float('TDS Previous')
    balance_tax_payable = fields.Float('')
    housing_loan_institute = fields.Char('')
    housing_loan_institute_pan = fields.Char('')
    name_of_landlord = fields.Char('')
    pan_of_landlord = fields.Char('')
    tax_regime=fields.Selection([('old_regime', 'Old Regime'), ('new_regime', 'New Regime')], default='old_regime',
                             string='Tax Regime', track_visibility="alaways")
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always')
    taxable_income = fields.Float()
    tax_payable = fields.Float()
    rebate = fields.Float()
    net_tax_payable = fields.Float()
    additional_sub_chrg = fields.Float()
    additional_edu_cess = fields.Float()
    total_tax_payable = fields.Float()
    tds_previous_employer = fields.Float()
    tax_recovered = fields.Float()
    red = fields.Integer()
    emp_code = fields.Char(related='employee_id.emp_code')
    pan_number = fields.Char(string='PAN of the Employee', compute='_compute_pan_num', track_visibility="always")
    bank_account = fields.Char(string='Bank A/c#', compute='_compute_pan_num',)
    date_of_joining = fields.Date(related='employee_id.date_of_joining', string='Date to which Employed with Current Employer')
    last_working_day = fields.Date(related='employee_id.last_working_day', string='Date of Leaving Service from Current Employer')
    cal_tds_by_company = fields.Float(compute='calculate_tds_by_company',)
    cal_taxable_income = fields.Float(compute='calculate_taxable_income',)
    cal_tax_payable = fields.Float(compute='calculate_taxable_income',)
    cal_rebate = fields.Float(compute='calculate_taxable_income',)
    cal_net_tax_payable = fields.Float(compute='calculate_taxable_income',)
    cal_additional_sub_chrg = fields.Float(compute='calculate_taxable_income',)
    cal_additional_edu_cess = fields.Float(compute='calculate_taxable_income',)
    cal_total_tax_payable = fields.Float(compute='calculate_taxable_income',)
    emp = fields.Char(related='employee_id.name', string='Name')
    cal_balance_tax_payable = fields.Float(compute='calculate_taxable_income',)
    emp_type = fields.Char(string='Employement Type', related='employee_id.employement_type.name')
    state = fields.Selection([('draft', 'Submitted'), ('approved', 'Approved'),('not_submitted', 'Not-Submitted')],string='Status', track_visibility='always')
    final_amount_other_income = fields.Float()

    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            for record in rec.employee_id.identification_ids:
                if record.name == '1':
                    rec.pan_number = record.doc_number
            contract = self.env['hr.contract'].sudo().search([('state','=','open'),('employee_id','=',rec.employee_id.id)])
            if contract:
                rec.bank_account = contract.bank_account if contract.bank_account else contract.personal_bank_account

    @api.depends('tax_recovered','tds_previous_employer','red')
    def calculate_tds_by_company(self):
            for rec in self:
                if rec.red == 2:
                    rec.cal_tds_by_company = rec.tax_recovered - rec.tds_previous_employer if rec.tax_recovered - rec.tds_previous_employer > 0 else 0
                else:
                    rec.cal_tds_by_company = rec.tax_recovered

    @api.depends('taxable_income','red','tax_payable','gross_total_income','final_amount','rebate','net_tax_payable','additional_sub_chrg','additional_edu_cess','total_tax_payable','balance_tax_payable','date_range')
    def calculate_taxable_income(self):
        for rec in self:
            temp_taxable_income = rec.gross_total_income - rec.final_amount

            if (temp_taxable_income % 10) >= 5:
                z = 10 - (temp_taxable_income % 10)
                tax_amount = temp_taxable_income + z
            else:
                tax_amount = temp_taxable_income - (temp_taxable_income % 10)
            rec.cal_taxable_income = tax_amount if tax_amount > 0 else 0

            if rec.red == 2:
                rec.cal_tax_payable = rec.tax_payable
                rec.cal_rebate = rec.rebate
                rec.cal_net_tax_payable = rec.net_tax_payable
                rec.cal_additional_sub_chrg = rec.additional_sub_chrg
                rec.cal_additional_edu_cess = rec.additional_edu_cess
                rec.cal_total_tax_payable = rec.total_tax_payable
                rec.cal_balance_tax_payable = rec.balance_tax_payable

            else:
                temp_tax_payable =temp_balance_tax_payable= 0
                if rec.cal_taxable_income > 250000 and rec.cal_taxable_income <= 500000:
                    tds_amount = rec.cal_taxable_income - 250000
                    tax_slab = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',rec.cal_taxable_income),('salary_to','>=',rec.cal_taxable_income),('tax_regime','=','old_regime')],limit=1)
                    temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
                elif rec.cal_taxable_income > 500000 and rec.cal_taxable_income <= 1000000:
                    tds_above5 = rec.cal_taxable_income - 500000
                    tax_slab = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',rec.cal_taxable_income),('salary_to','>=',rec.cal_taxable_income),('tax_regime','=','old_regime')],limit=1)
                    tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
                    tax_slab_1 = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','old_regime')],limit=1)
                    tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
                    temp_tax_payable = tds_above5percentage + tds_below5percentage
                elif rec.cal_taxable_income > 1000000:
                    tds_above10 = rec.cal_taxable_income - 1000000
                    tax_slab = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',rec.cal_taxable_income),('salary_to','>=',rec.cal_taxable_income),('tax_regime','=','old_regime')],limit=1)
                    tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
                    tax_slab_1 = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','>=',500001),('salary_to','<=',1000000),('tax_regime','=','old_regime')],limit=1)
                    tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
                    tax_slab_2 = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','old_regime')],limit=1)
                    tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
                    temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage

                rec.cal_tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0
                rec.cal_rebate = rec.cal_tax_payable if rec.cal_taxable_income < 500000 and rec.cal_taxable_income > 0 else 0
                temp_net_tax_payable = 0 
                temp_net_tax_payable = rec.cal_tax_payable - rec.cal_rebate
                rec.cal_net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
                tax_slab_rec = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',rec.cal_taxable_income),('salary_to','>=',rec.cal_taxable_income),('tax_regime','=','old_regime')],limit=1)
                
                surcharge_slab = self.env['tax_surcharge'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',rec.cal_taxable_income),('salary_to','>=',rec.cal_taxable_income),('tax_regime','=','old_regime')],limit=1)
                
                cess_slab = self.env['tax_cess'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',rec.cal_taxable_income),('salary_to','>=',rec.cal_taxable_income),('tax_regime','=','old_regime')],limit=1)
                
                rec.cal_additional_sub_chrg = rec.cal_net_tax_payable * surcharge_slab.surcharge / 100 
                rec.cal_additional_edu_cess = rec.cal_net_tax_payable * cess_slab.cess / 100
                total_tax_payable = 0
                var_tax_payable = 0
                total_tax_payable = rec.cal_net_tax_payable + rec.cal_additional_sub_chrg + rec.cal_additional_edu_cess
                if (total_tax_payable % 10) >= 5:
                    z = 10 - (total_tax_payable % 10)
                    var_tax_payable = total_tax_payable + z
                else:
                    var_tax_payable = total_tax_payable - (total_tax_payable % 10)
                rec.cal_total_tax_payable = var_tax_payable
                temp_balance_tax_payable = rec.cal_total_tax_payable - rec.tax_recovered
                
                rec.cal_balance_tax_payable = temp_balance_tax_payable

    def view_payslips(self):
        if self.employee_id and self.date_range:
            payslips = self.env['hr.payslip'].sudo().search([('date_to','>=',self.date_range.date_start),('date_to','<=',self.date_range.date_stop),('employee_id','=',self.employee_id.id),('state','=','done')])
            if payslips:
                rc = {
                    'name': f'Payslips for {self.employee_id.name}',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'views': [(self.env.ref('payroll_inherit.user_payroll_tree_view').id, 'tree')],
                    'view_id': self.env.ref('payroll_inherit.user_payroll_tree_view').id,
                    'res_model': 'hr.payslip',
                    'domain':[('id','in',payslips.ids)],
                    'type': 'ir.actions.act_window',
                    'target': 'self',
                }
                return rc
            else:
                raise ValidationError('No Payslip Found!')

    def view_yearly_hr_declaration(self):
        for rec in self:
            # yearly_dec = self.env['yearly_hr_declaration'].sudo().search([('employee_id','=',rec.employee_id.id),('date_range','=',rec.date_range.id)])
            hr_dec = self.env['hr.declaration'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('date_range', '=', rec.date_range.id)])
            view_id = self.env.ref('tds.hr_declaration_bifurcation_view_form').id
            if hr_dec:
                rc = {
                    'name': 'IT Declaration',
                    'type': 'ir.actions.act_window',
                    'res_model': 'hr.declaration',
                    'view_id': view_id,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': hr_dec.id,
                    'target': 'self',
                }
                return rc
            else:
                month_dict = {1: 3, 2: 2, 3: 1, 4: 12, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5, 12: 4}
                # month_dict={3:2}
                currentMonth = datetime.now().month
                c = 0

                financial_year = rec.date_range

                gross = 0.00
                total_gross = 0.00
                bs = 0.00
                house_rent = 0.00
                total_basic = 0.00
                total_conveyance = 0.00
                total_hra = 0.00
                total_pb = 0.00
                total_cb = 0.00
                lwop = 0.00
                ptd = 0.00
                tds = 0.00
                total_after_lwop = 0.00
                professional_tax = 0.00
                total_after_pt_sd = 0.00
                forcast_basic = 0.00
                forcast_hra = 0.00
                other_allowance = 0.00
                tax_payable = 0.00
                epf = 0.00

                # Fetch all the payslips of the current financial year
                payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                ('state', '=', 'done'),
                                                                ('date_from', '>=', financial_year.date_start),
                                                                ('date_to', '<=', financial_year.date_stop),
                                                                ])
                prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
                                                                    ('slip_id.state', '=', 'done'),
                                                                    ('slip_id.date_from', '>=',
                                                                     financial_year.date_start),
                                                                    ('slip_id.date_to', '<=', financial_year.date_stop),
                                                                    ])

                # Dynamically set remaining month till end of financial year
                
                j_date = rec.employee_id.date_of_joining
                if j_date >= financial_year.date_start and j_date <= financial_year.date_stop:
                    remain_months = (financial_year.date_stop.year - j_date.year) * 12 + (
                            financial_year.date_stop.month - j_date.month)
                    month_limit = int(remain_months) + 1
                else:
                    month_limit = 12

                blk_date_lst = []
                counter = 0
                last_counter = 0
                block_payslips = self.env['hr_block_salary'].sudo().search([('employee_id','=',rec.employee_id.id)])
                for blk_payslp in block_payslips:
                    blk_year = int(blk_payslp.year)
                    blk_month = int(blk_payslp.month)
                    blk_date = date(blk_year,blk_month,1)
                    blk_date_lst.append(blk_date)
                for dates in blk_date_lst:
                    if financial_year.date_start <= dates <= financial_year.date_stop:
                        chk_payslip = payslip.filtered(lambda x:x.date_from <= dates <= x.date_to)
                        if not chk_payslip:
                            counter += 1
                if rec.employee_id.last_working_day:
                    if financial_year.date_start <= rec.employee_id.last_working_day <= financial_year.date_stop and rec.employee_id.active == False:
                        last_counter =  (financial_year.date_stop.year -  rec.employee_id.last_working_day.year) * 12 + financial_year.date_stop.month -  rec.employee_id.last_working_day.month

                # remaining_month = month_limit - len(payslip) - counter - last_counter 
                remaining_month = month_limit - len(payslip) - counter - last_counter if date.today() < financial_year.date_stop else 0
                
                # calculate the gross salary of the employee
                for pr in prl_id:
                    if pr.code == 'GROSS':
                        gross += pr.amount
                    if pr.code == 'BASIC':
                        bs += pr.amount
                    if pr.code == 'LWOP':
                        lwop += pr.amount
                    if pr.code == 'PTD':
                        ptd += pr.amount
                    if pr.code == 'TDS':
                        tds += pr.amount
                    if pr.code == 'HRAMN':
                        house_rent += pr.amount
                    if pr.code == 'EEPF':
                        epf += pr.amount
                   

                # check if any variable allowance is present for the current month
                alw_rec_start = self.env['allowance_allocation_master'].sudo().search(
                    [('month', 'not in', [1,2,3]), ('year', '=', str(rec.date_range.date_start.year)),
                    ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
                
                alw_rec_end = self.env['allowance_allocation_master'].sudo().search(
                    [('month', 'in', [1,2,3]), ('year', '=', str(rec.date_range.date_stop.year)),
                    ('employee', '=', rec.employee_id.id), ('boolean_readonly', '=', False)])
                
                
                c = 0
                start_c = 0
                end_c = 0
                if alw_rec_start:
                    for alw in alw_rec_start:
                        start_c += alw.amount
                else:
                    start_c = 0
                
                if alw_rec_end:
                    for alw in alw_rec_end:
                        end_c += alw.amount
                else:
                    end_c = 0

                c = start_c + end_c

                contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                 ('state', '=', 'open')
                                                                 ], limit=1)

                total_basic = contrct.current_basic
                total_hra = contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100
                total_conveyance = contrct.current_basic * contrct.conveyance / 100
                total_pb = contrct.productivity
                total_cb = contrct.commitment
                total_bonus = contrct.bonus
                forcast_basic = bs + (contrct.current_basic * remaining_month)
                sum_prl = 0.00

                for record in prl_id:
                    if record.code == 'HRAMN':
                        sum_prl += record.amount
                
                forcast_hra = (sum_prl + (
                        contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100) * remaining_month)
                total_gross = (total_basic + total_hra + total_conveyance + total_pb + total_cb + total_bonus) * remaining_month + gross + c 
                
                other_allowance = total_gross - (forcast_hra + forcast_basic)

                total_after_lwop = 0 if (total_gross - lwop) < 0 else (total_gross - lwop)
                # calculate the professional tax
                pt_gross = total_basic + total_hra + total_conveyance + total_pb + total_cb + total_bonus
               
                if pt_gross * 12 >= 300000:
                    extra_amount = 0 if remaining_month == 0 else 100
                    pt = ptd + (200 * remaining_month) + extra_amount
                elif pt_gross * 12 >= 160000 and pt_gross * 12 < 300000:
                    pt = ptd + (125 * remaining_month)
                else:
                    pt = 0

                professional_tax = pt

                # print('professional tax=========', professional_tax)

                # Employee Epf
                if contrct.enable_epf == 'yes':
                    if contrct.pf_deduction == 'other':
                        if  contrct.epf_percent:
                            employee_epf = epf + (contrct.current_basic * contrct.epf_percent / 100) * remaining_month
                        else :
                            employee_epf = epf + 0
                    elif contrct.pf_deduction == 'avail1800' and contrct.current_basic >= 15000:
                        employee_epf = epf + (1800 * remaining_month)
                    else:
                        employee_epf = epf + (contrct.current_basic * 12 / 100) * remaining_month
                else:
                    employee_epf = 0
                # print('employee_epf===========',employee_epf)
                # Insurance Dependent
                health_dependant = self.env['health_insurance_dependant'].sudo().search(
                    [('employee_id', '=', rec.employee_id.id),
                     ('date_range.date_start', '<=', rec.date_range.date_start),
                     ('date_range.date_stop', '>=', rec.date_range.date_stop),('state', '=', 'approved')])
                hid_amount = 0
                if health_dependant:
                    hid_amount += sum(health_dependant.emi_details_ids.mapped('installment'))
                
                total_deduction = employee_epf +  hid_amount
                total_after_pt_sd = 0 if ((total_after_lwop - (professional_tax)) - 50000) < 0 else (
                        (total_after_lwop - (professional_tax)) - 50000)
                a = total_after_pt_sd - total_deduction
                # print('a==========', a)
                if (a % 10) >= 5:
                    z = 10 - (a % 10)
                    # print(a + z)
                    tax_amount = a + z
                else:
                    # print(a - (a % 10))
                    tax_amount = a - (a % 10)

                taxable_income = tax_amount
                # calculate tax based on formula
                temp_tax_payable = 0.00
                if taxable_income > 250000 and taxable_income <= 500000:
                    tds_amount = taxable_income - 250000
                    tax_slab = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','old_regime')],limit=1)
                    temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
                elif taxable_income > 500000 and taxable_income <= 1000000:
                    tds_above5 = taxable_income - 500000
                    tax_slab = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','old_regime')],limit=1)
                    tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
                    tax_slab_1 = self.env['tax_slab'].sudo().search([('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','old_regime')],limit=1)
                    tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
                    temp_tax_payable = tds_above5percentage + tds_below5percentage
                elif taxable_income > 1000000:
                    tds_above10 = taxable_income - 1000000
                    tax_slab = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','old_regime')],limit=1)
                    tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
                    tax_slab_1 = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','>=',500001),('salary_to','<=',1000000),('tax_regime','=','old_regime')],limit=1)
                    tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
                    tax_slab_2 = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','>=',250001),('salary_to','<=',5000000),('tax_regime','=','old_regime')],limit=1)
                    tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
                    temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage

                tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0

                rebate = tax_payable if taxable_income < 500000 and tax_payable > 0 else 0
                temp_net_tax_payable = tax_payable - rebate
                net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
                tax_slab_rec = self.env['tax_slab'].sudo().search([('date_range','=',rec.date_range.id),('salary_from','<=',taxable_income),('salary_to','>=',taxable_income),('tax_regime','=','old_regime')],limit=1)
                additional_sub_chrg = net_tax_payable * tax_slab_rec.surcharge / 100
                additional_edu_cess = net_tax_payable * tax_slab_rec.cess / 100 if net_tax_payable > 0 else 0
                var_tax_payable = round(net_tax_payable + additional_sub_chrg + additional_edu_cess)
                if (var_tax_payable % 10) >= 5:
                    remaining = 10 - (var_tax_payable % 10)
                    tax_to_be_paid = var_tax_payable + remaining
                else:
                    tax_to_be_paid = var_tax_payable - (var_tax_payable % 10)
                total_tax_payable = tax_to_be_paid
                tax_recovered = tds
                temp_balance_tax_payable = total_tax_payable - tax_recovered
                balance_tax_payable = temp_balance_tax_payable

                return {
                    'name': 'IT Declaration',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'yearly_notsubmitted_declaration',
                    'view_id': self.env.ref('tds.yearly_notsubmitted_declaration_view_form').id,
                    'type': 'ir.actions.act_window',
                    'target': 'self',
                    'context': {'employee_id': rec.employee_id.id, 'basic': forcast_basic, 'hra': forcast_hra,
                                'gross': total_gross, 'oalw': other_allowance, 'lwop': lwop,
                                'afterlwop': total_after_lwop, 'professional_tax': professional_tax,
                                'total_after_pt_sd': total_after_pt_sd,
                                'tax_payable': tax_payable, 'rebate': rebate, 'net_tax_payable': net_tax_payable,
                                'additional_sub_chrg': additional_sub_chrg,
                                'additional_edu_cess': additional_edu_cess, 'total_tax_payable': total_tax_payable,
                                'tax_recovered': tax_recovered, 'balance_tax_payable': balance_tax_payable,
                                'employee_epf': employee_epf, 'self_insurance': 0,
                                'hid_amount': hid_amount, 'total_deduction': total_deduction,
                                'taxable_income': taxable_income},
                }

                