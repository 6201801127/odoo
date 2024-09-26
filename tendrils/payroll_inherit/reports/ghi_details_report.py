from odoo import tools, models, fields, api
from datetime import date

class PayrollGhiDetailsReport(models.Model):
    _name = 'payroll_ghi_details_report'
    _auto = False
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_code = fields.Char('Employee Code')
    status = fields.Char('Status')
    insurance_year = fields.Many2one('account.fiscalyear', 'Financial Year')
    department_id = fields.Many2one('hr.department', string='Department')
    job_branch_id = fields.Many2one('kw_res_branch', string='Work Location	')
    joining_date = fields.Date('Joining Date')
    date_of_employee_id_creation = fields.Datetime('Date of Employee ID Creation')
    last_working_day = fields.Date('Last Working Day')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    dob = fields.Date('Date of Birth')
    emp_status = fields.Char('Employee Status')
    no_of_dependents = fields.Integer('Number of Dependents')
    payroll_status = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    period_from = fields.Date()
    period_to = fields.Date()
    valid_till = fields.Date(string='Valid Till')
    insurance_doc = fields.Binary(string='Insurance Document',related='employee_id.uplod_insurance_doc')
    file_name_insurance = fields.Char(string="File Name",related='employee_id.file_name_insurance')  
    document_bool = fields.Boolean(compute='check_ins_type')
    coverage_type = fields.Selection([('Self', 'Self'), ('Dependent', 'Dependent')],string='Coverage Type')
    
    
    def check_ins_type(self):
        for rec in self:
            if rec.status in ('Personal Insurance' ,'International-Insurance') or rec.employee_id.employement_type.code == 'R':
                rec.document_bool = True
    
    def action_upload_doc(self):
        view_id = self.env.ref('payroll_inherit.upload_employee_insurance_doc').id
        return {
            'name':'Upload Document',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'update_emp_insurance_doc',
            'view_id': view_id,
            'context':{'employee_id':self.employee_id.id},
            'target': 'new',
        }

 
    @api.model_cr
    def init(self):
        date_from = self.env.context.get('from_date') or date.today().strftime('%Y-%m-%d')
        date_to = self.env.context.get('date_to') or date.today().strftime('%Y-%m-%d')
        insurance_year = self.env.context.get('insurance_year') if self.env.context.get('insurance_year') else 1
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW payroll_ghi_details_report AS (
                SELECT
                    e.id AS id,
                    hid.period_from as period_from,
                    hid.period_to as period_to,
                    hid.employee_id AS employee_id,
                    e.emp_code AS employee_code,
                    'GHI' AS status,
                    'Dependent' as coverage_type,
                    hid.date_range AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                    CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    hid.num_dependant AS no_of_dependents,
                    (select validity_upto from health_insurance_policy_master) as valid_till
                FROM
                    health_insurance_dependant hid
                    JOIN hr_employee e ON e.id = hid.employee_id
                WHERE 
                    hid.state = 'approved'
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    and e.employement_type is not null
                    and hid.date_range = {insurance_year}
                UNION
                SELECT
                    e.id AS id,
                    '{date_from}' as period_from,
                    '{date_to}' as period_to,
                    e.id AS employee_id,
                    e.emp_code AS employee_code,
                    'ESI' AS status,
                    'Self' as coverage_type,
                    Null AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                    CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    0 AS no_of_dependents,
                    Null as valid_till
                FROM
                    hr_employee e
                    
                WHERE
                    e.id not in (select employee_id from health_insurance_dependant where date_range={insurance_year} and state='approved')
                    and
                    e.id not in (select employee_id from non_esi_employee_report where fiscalyr={insurance_year})
                    and
                    e.esi_applicable = TRUE
                    AND e.is_consolidated = FALSE
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    AND
                    e.company_id = 1
                    and e.employement_type is not null
                    
                    AND (
                        (e.date_of_joining <= '{date_from}' AND e.last_working_day IS NULL AND e.active = true)
                        OR (e.date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                        OR (e.last_working_day > '{date_from}' AND e.date_of_joining <= '{date_from}' AND e.active = false)
                        OR (e.last_working_day BETWEEN '{date_from}' AND '{date_to}' AND e.date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND e.active = false)
                    )
                UNION
                SELECT
                    e.id AS id,
                    '{date_from}' as period_from,
                    '{date_to}' as period_to,
                    e.id AS employee_id,
                    e.emp_code AS employee_code,
                    'Stipend' AS status,
                    'Self' as coverage_type,
                    Null AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                    CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    0 AS no_of_dependents,
                    Null as valid_till
                FROM
                    hr_employee e

                WHERE
                    e.id not in (select employee_id from health_insurance_dependant where date_range={insurance_year} and state='approved')
                    and 
                    e.id not in (select employee_id from non_esi_employee_report where fiscalyr={insurance_year})
                    AND e.is_consolidated = True
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    AND
                    e.company_id = 1
                    and e.employement_type is not null
                    
                    AND (
                        (e.date_of_joining <= '{date_from}' AND e.last_working_day IS NULL AND e.active = true)
                        OR (e.date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                        OR (e.last_working_day > '{date_from}' AND e.date_of_joining <= '{date_from}' AND e.active = false)
                        OR (e.last_working_day BETWEEN '{date_from}' AND '{date_to}' AND e.date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND e.active = false)
                    )
                    UNION
                SELECT
                    e.id AS id,
                    '{date_from}' as period_from,
                    '{date_to}' as period_to,
                    e.id AS employee_id,
                    e.emp_code AS employee_code,
                    'Personal Insurance' AS status,
                    'Self' as coverage_type,
                    Null AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                    CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    0 AS no_of_dependents,
                    e.insurance_validate_date as valid_till
                FROM
                    hr_employee e
                    
                WHERE
                    e.id not in (select employee_id from health_insurance_dependant where date_range={insurance_year} and state='approved')
                    and e.department_id = (select id from hr_department where code='OFFS')
                    AND
                    e.company_id = 1
                    AND
                    e.personal_insurance='Yes'
                    and e.employement_type is not null
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    AND (
                        (e.date_of_joining <= '{date_from}' AND e.last_working_day IS NULL AND e.active = true)
                        OR (e.date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                        OR (e.last_working_day > '{date_from}' AND e.date_of_joining <= '{date_from}' AND e.active = false)
                        OR (e.last_working_day BETWEEN '{date_from}' AND '{date_to}' AND e.date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND e.active = false)
                    )
                UNION
                SELECT
                    e.id AS id,
                    '{date_from}' as period_from,
                    '{date_to}' as period_to,
                    e.id AS employee_id,
                    e.emp_code AS employee_code,
                    'GHI' AS status,
                    'Self' as coverage_type,
                    Null AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                    CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    0 AS no_of_dependents,
                    (select validity_upto from health_insurance_policy_master) as valid_till
                FROM
                    hr_employee e
                   
                WHERE
                    e.id not in (select employee_id from health_insurance_dependant where date_range={insurance_year} and state='approved')
                    and
                    e.esi_applicable = FALSE
                    AND e.is_consolidated = FALSE
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    AND
                    (e.personal_insurance !='Yes' or e.personal_insurance is null) 
                    and
                    e.company_id = 1
                    and e.employement_type is not null
                    AND e.id NOT IN (SELECT employee_id FROM non_esi_employee_report)
                    AND (
                        (e.date_of_joining <= '{date_from}' AND e.last_working_day IS NULL AND e.active = true)
                        OR (e.date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                        OR (e.last_working_day > '{date_from}' AND e.date_of_joining <= '{date_from}' AND e.active = false)
                        OR (e.last_working_day BETWEEN '{date_from}' AND '{date_to}' AND e.date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND e.active = false)
                    )
                UNION
                SELECT
                    e.id AS id,
                    '{date_from}' as period_from,
                    '{date_to}' as period_to,
                    n.employee_id AS employee_id,
                    e.emp_code AS employee_code,
                    n.state AS status,
                    'Self' as coverage_type,
                    Null AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                   CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    0 AS no_of_dependents,
                    Null as valid_till
                    
                    
                FROM
                    hr_employee e
                    JOIN non_esi_employee_report n ON n.employee_id = e.id
                WHERE
                    e.id not in (select employee_id from health_insurance_dependant where date_range={insurance_year} and state='approved')
                    and
                    e.esi_applicable = FALSE
                    AND e.is_consolidated = FALSE
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    and e.department_id = (select id from hr_department where code='OFFS')
                    AND
                    e.company_id = 1
                    and e.employement_type is not null
                    and n.fiscalyr = {insurance_year}
                    
                    AND (
                        (e.date_of_joining <= '{date_from}' AND e.last_working_day IS NULL AND e.active = true)
                        OR (e.date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                        OR (e.last_working_day > '{date_from}' AND e.date_of_joining <= '{date_from}' AND e.active = false)
                        OR (e.last_working_day BETWEEN '{date_from}' AND '{date_to}' AND e.date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND e.active = false)
                    )
                UNION
                SELECT
                    e.id AS id,
                    '{date_from}' as period_from,
                    '{date_to}' as period_to,
                    e.id AS employee_id,
                    e.emp_code AS employee_code,
                    'International-Insurance' AS status,
                    'Self' as coverage_type,
                    Null AS insurance_year,
                    e.department_id AS department_id,
                    e.job_branch_id AS job_branch_id,
                    e.enable_payroll AS payroll_status,
                    e.date_of_joining AS joining_date,
                    e.create_date AS date_of_employee_id_creation,
                    e.last_working_day AS last_working_day,
                    e.gender AS gender,
                    e.birthday AS dob,
                     CASE WHEN e.id in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Applied EOS'
                    when e.id not in (select applicant_id from  kw_resignation where state not in ('reject', 'cancel')) and e.active=true then 'Active'
                    when e.active = false then 'Inactive' end as emp_status,
                    0 AS no_of_dependents,
                    e.insurance_validate_date as valid_till
                FROM
                    hr_employee e
                WHERE
                    e.id not in (select employee_id from health_insurance_dependant where date_range={insurance_year} and state='approved')
                    and
                    e.personal_insurance='Yes'
                    and
                    e.company_id != 1 and  e.company_id is not null
                    and e.employement_type not in (select id from kwemp_employment_type where code in ('O'))
                    and e.employement_type is not null
                    AND (
                        (e.date_of_joining <= '{date_from}' AND e.last_working_day IS NULL AND e.active = true)
                        OR (e.date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                        OR (e.last_working_day > '{date_from}' AND e.date_of_joining <= '{date_from}' AND e.active = false)
                        OR (e.last_working_day BETWEEN '{date_from}' AND '{date_to}' AND e.date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND e.active = false)
                    )
            )
        """)