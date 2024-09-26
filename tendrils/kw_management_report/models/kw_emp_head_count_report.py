# *******************************************************************************************************************
#  File Name             :   kw_emp_head_count_report.py
#  Description           :   This model is used to fetch employee head count with their historical data 
#  Created by            :   Monalisha rout
#  Created On            :   24-02-2023
#  Modified by           :   Monalisha Rout
#  Modified On           :   28-02-2023
#  Modification History  :   Query optimization
# *******************************************************************************************************************

from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from odoo.addons import decimal_precision as dp


class HeadCountreport(models.Model):
    _name = 'kw_emp_head_count_report'
    _description = 'Head count Report'
    _auto = False

    fiscal_year = fields.Many2one('account.fiscalyear', string='Financial Year')
    male_count = fields.Integer(string='Male',compute='_compute_emp_count')
    female_count = fields.Integer(string='Female',compute='_compute_emp_count')
    ctc = fields.Float(string='CTC', digits=dp.get_precision('Payroll'))
    new_joiner = fields.Integer(string='New Joined')
    ex_emp = fields.Integer(string='Resigned')
    emp_count = fields.Integer(compute='_compute_emp_count')
    check_fy = fields.Boolean(compute='_compute_emp_count')

    """ORM to fetch employee head count"""
    @api.depends('fiscal_year')
    def _compute_emp_count(self):
        male_occurrence,female_occurrence,ex_emp_gender= 0,0,[]
        for rec in self:
            if rec.fiscal_year:
                total_emp = self.env['hr.employee'].sudo().search(['|',('active','=',True),('active','=',False)])
                emps = total_emp.filtered(lambda x:x.date_of_joining <= rec.fiscal_year.date_stop  if x.date_of_joining else None)
                active_true_emp =  emps.filtered(lambda x:x.active==True and x.date_of_joining <= rec.fiscal_year.date_stop and x.employement_type.code not in ('O','CE'))
                active_false_emp =  emps.filtered(lambda x:x.active==False and x.employement_type.code not in ('O','CE'))
                active_false_emp = active_false_emp.filtered(lambda x:x.date_of_joining <= rec.fiscal_year.date_stop  if x.date_of_joining else None)
                active_false_emp = active_false_emp.filtered(lambda x:x.last_working_day >=  rec.fiscal_year.date_stop if x.last_working_day else None)
                rec.emp_count = len(active_true_emp) +  len(active_false_emp)
                active_true_emp_gender = active_true_emp.mapped('gender')
                active_false_emp_gender = active_false_emp.mapped('gender')
                male_occurrence = active_true_emp_gender.count('male') + active_false_emp_gender.count('male')
                female_occurrence = active_true_emp_gender.count('female') + active_false_emp_gender.count('female')
                rec.male_count = male_occurrence
                rec.female_count = female_occurrence
                if rec.fiscal_year.date_start < date.today() < rec.fiscal_year.date_stop:
                    rec.check_fy =True

    def action_button_update(self):
        if self.fiscal_year:
            date_start = self.fiscal_year.date_start
            date_stop = self.fiscal_year.date_stop
            query = f" select hr.id as employee_id,case when hr.last_working_day between '{date_start}' AND '{date_stop}' then  1 when hr.date_of_joining between '{date_start}' AND '{date_stop}' then  2 else 0 end as red,(SELECT SUM(line.amount) FROM hr_payslip_line line WHERE line.code='CTC' and  line.slip_id IN (SELECT p.id FROM hr_payslip p WHERE p.date_to BETWEEN '{date_start}' AND '{date_stop}' and p.state='done' and hr.id = p.employee_id) ) as ctc,(select name from hr_department where id = hr.department_id) as department,(select name from hr_department where id = hr.division) as division,(select name from hr_job where id = hr.job_id) as job_id FROM hr_employee hr where (hr.date_of_joining <= '{date_stop}' and hr.last_working_day is null and hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))) or (hr.last_working_day > '{date_stop}' and hr.date_of_joining <= '{date_stop}' and hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))) or (hr.last_working_day between '{date_start}' AND '{date_stop}' and hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE')))"
            self._cr.execute(query)
            ids = self._cr.dictfetchall()
            if len(ids) > 0 :
                query1 =''
                for record in ids:
                    employee_id = record['employee_id']
                    red = record['red']
                    ctc= record['ctc'] if record['ctc'] != None else 0
                    job = record['job_id'] if record['job_id'] != None else '--'
                    department = record['department'] if record['department'] != None else '--'
                    division = record['division'] if record['division'] != None else '--'

                    exist_rec = self.env['kw_emp_head_count_details'].sudo().search([('date_start','=',date_start),('employee_id','=',employee_id)])
                    if exist_rec:
                        query1 += f"update kw_emp_head_count_details set ctc= {ctc}, job_id = '{job}' , department_id = '{department}' , division = '{division}' where employee_id = {employee_id} and date_start = '{date_start}';"
                    else:
                        query1 += f"insert into kw_emp_head_count_details (employee_id,date_start,date_stop,red,ctc,department_id,division,job_id) values({employee_id},'{date_start}','{date_stop}',{red},{ctc},'{department}','{division}','{job}');"


                self._cr.execute(query1)


    """query to fetch all employee head count on each fy"""
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
                select 
                row_number() over(ORDER BY fy.name asc) as id,  
                fy.id as fiscal_year,
                (SELECT SUM(line.amount) FROM hr_payslip_line line 
				join hr_employee m on line.employee_id=m.id 
                    WHERE line.code='CTC' and m.employement_type in (select id from kwemp_employment_type where code not in ('O','CE')) and line.slip_id IN (SELECT p.id FROM hr_payslip p 
                    WHERE p.date_to BETWEEN fy.date_start AND fy.date_stop and p.state='done')) as ctc,
                (SELECT COUNT(m.id) FROM hr_employee m
                    WHERE date_of_joining BETWEEN fy.date_start AND fy.date_stop and employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))) as new_joiner,
                (SELECT COUNT(*) FROM hr_employee 
                    WHERE last_working_day BETWEEN fy.date_start AND fy.date_stop and employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))) as ex_emp
                FROM hr_employee hr 
                JOIN account_fiscalyear fy ON hr.date_of_joining BETWEEN fy.date_start AND fy.date_stop
                where hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))
                GROUP BY fy.id, fy.date_start, fy.date_stop
        )""" % (self._table))

    """button to fetch all employees having joined or exited during a particular date range"""
    def action_button_view_details(self):
        # self.env['kw_emp_head_count_details'].with_context(date_stop=self.fiscal_year.date_stop,date_start=self.fiscal_year.date_start).init()
        view_id = self.env.ref('kw_management_report.kw_emp_head_count_details_view_tree').id
        action =  {
            'name':f'Employee details for Fy : {self.fiscal_year.name}',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'kw_emp_head_count_details',
            'domain': [('date_start','=',self.fiscal_year.date_start)],
            'view_id': view_id,
            'target': 'current',
        }
        return action


class HeadCountDetailReport(models.Model):
    _name = 'kw_emp_head_count_details'
    _description = 'Head Count Employee Details Report'


    employee_id = fields.Many2one('hr.employee')
    location = fields.Char(string='Location', related='employee_id.base_branch_id.alias')
    employement_type = fields.Char(string='Type of Employment', related='employee_id.employement_type.name')
    name = fields.Char(string='Employee Name', related='employee_id.name')
    code = fields.Char(string='Employee Code', related='employee_id.emp_code')
    ctc = fields.Float(string='CTC')
    job_id = fields.Char(string='Designation')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ], string='Gender',related='employee_id.gender')
    date_of_joining = fields.Date(string="Date of Joining",related='employee_id.date_of_joining')
    last_working_day = fields.Date(string="Exit Date",related='employee_id.last_working_day')
    date_of_birth = fields.Date(string="Date of Birth",related='employee_id.birthday')
    department_id = fields.Char(string='Department')
    division = fields.Char(string="Division")
    red = fields.Integer()
    date_start = fields.Date()
    date_stop = fields.Date()
    status =  fields.Selection([('regular', 'Existing'), ('new', 'New-Joiner'), ('exemp', 'EX-Employee'),('jl','joined/Leave') ], string='Status',compute='employee_last_working_day')

   

    """method used for tree decoration when employee status is inactive"""
    @api.depends('red','date_start','date_stop')
    def employee_last_working_day(self):
        for rec in self:
            if rec.date_start and rec.date_stop:
                if rec.employee_id.last_working_day and rec.date_stop >= rec.employee_id.date_of_joining >= rec.date_start and rec.date_stop >= rec.employee_id.last_working_day >= rec.date_start:
                    rec.status = 'jl'
                elif  rec.employee_id.last_working_day and rec.employee_id.date_of_joining < rec.date_start and rec.date_stop >= rec.employee_id.last_working_day >= rec.date_start:
                    rec.status = 'exemp'
                elif  rec.employee_id.date_of_joining < rec.date_start and (not rec.employee_id.last_working_day or rec.date_stop < rec.employee_id.last_working_day):
                    rec.status = 'regular'
                elif  rec.date_stop >= rec.employee_id.date_of_joining >= rec.date_start and(not rec.employee_id.last_working_day or rec.date_stop > rec.employee_id.last_working_day  ):
                    rec.status = 'new'
                    

class GetHeadCountEmployeeDeatials(models.TransientModel):
    _name = "get_head_count_employee_details"
    _description = "Filter to get employee Data"

    fiscal_year = fields.Many2one('account.fiscalyear', string='Financial Year')

    def remove_employee_data(self):
        if self.fiscal_year:
            self._cr.execute(f"delete from kw_emp_head_count_details where date_start = '{self.fiscal_year.date_start}' and date_stop='{self.fiscal_year.date_stop}'")


    def get_employee_data(self):
        if self.fiscal_year:
            date_start = self.fiscal_year.date_start
            date_stop = self.fiscal_year.date_stop
            query = f" select hr.id as employee_id,case when hr.last_working_day between '{date_start}' AND '{date_stop}' then  1 when hr.date_of_joining between '{date_start}' AND '{date_stop}' then  2 else 0 end as red,(SELECT SUM(line.amount) FROM hr_payslip_line line WHERE line.code='CTC' and  line.slip_id IN (SELECT p.id FROM hr_payslip p WHERE p.date_to BETWEEN '{date_start}' AND '{date_stop}' and p.state='done' and hr.id = p.employee_id) ) as ctc,(select name from hr_department where id = hr.department_id) as department,(select name from hr_department where id = hr.division) as division,(select name from hr_job where id = hr.job_id) as job_id FROM hr_employee hr where (hr.date_of_joining <= '{date_stop}' and hr.last_working_day is null and hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))) or (hr.last_working_day > '{date_stop}' and hr.date_of_joining <= '{date_stop}' and hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE'))) or (hr.last_working_day between '{date_start}' AND '{date_stop}' and hr.employement_type  in (select id from kwemp_employment_type where code not in ('O','CE')))"
            self._cr.execute(query)
            ids = self._cr.dictfetchall()
            if len(ids) > 0 :
                query1 =''
                for record in ids:
                    employee_id = record['employee_id']
                    red = record['red']
                    ctc= record['ctc'] if record['ctc'] != None else 0
                    job = record['job_id'] if record['job_id'] != None else '--'
                    department = record['department'] if record['department'] != None else '--'
                    division = record['division'] if record['division'] != None else '--'

                    exist_rec = self.env['kw_emp_head_count_details'].sudo().search([('date_start','=',date_start),('employee_id','=',employee_id)])
                    if exist_rec:
                        query1 += f"update kw_emp_head_count_details set ctc= {ctc}, job_id = '{job}' , department_id = '{department}' , division = '{division}' where employee_id = {employee_id} and date_start = '{date_start}';"
                    else:
                        query1 += f"insert into kw_emp_head_count_details (employee_id,date_start,date_stop,red,ctc,department_id,division,job_id) values({employee_id},'{date_start}','{date_stop}',{red},{ctc},'{department}','{division}','{job}');"


                self._cr.execute(query1)

