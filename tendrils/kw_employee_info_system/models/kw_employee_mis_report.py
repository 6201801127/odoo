from odoo import models, fields, api
from odoo import tools
from datetime import date, datetime


class MisManagerreportEmployee(models.Model):
    _name = "hr.employee.mis.report"
    _description = "Employee MIS Report"
    _auto = False

    emp_id = fields.Many2one('hr.employee')
    employement_type = fields.Many2one('kwemp_employment_type', string="Type of Employment")
    emp_role = fields.Many2one('kwmaster_role_name', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', string="Employee Category")
    job_branch_id = fields.Many2one('kw_res_branch', string="Work Location")
    department_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practice")
    practise = fields.Many2one('hr.department', string="Section")
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU")
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
                                   string="Budget Type")
    emp_project_id = fields.Many2one('crm.lead', string="Project Name")
    start_date = fields.Date(string="Contract Start Date")
    end_date = fields.Date(string="Contract End Date")
    emp_code = fields.Char(string="Employee Code")
    name = fields.Char(string="Name")
    job_id = fields.Many2one('hr.job', string="Designation")
    date_of_joining = fields.Date(string="Joining Date")
    joining_type = fields.Selection([('Lateral', 'Lateral'), ('Intern', 'Intern')], default="Lateral",
                                    string='Joined as')
    date_of_exit = fields.Date(string="Exit Date")
    grade = fields.Many2one('kwemp_grade_master', string="Grade", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    emp_band = fields.Many2one('kwemp_band_master', string="Band", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    location = fields.Char(string="Location")
    current_ctc = fields.Integer(string="CTC2", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    contract_ctc = fields.Integer(string="CTC", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    edu_qualification = fields.Char(string="Education Qualification")

    total_experience_display = fields.Char(string="Total Experience")
    csm_experience_display = fields.Char(string="CSM Experience")

    emp_refered = fields.Many2one('utm.source', string="Reference Mode", domain=[('source_type', '=', 'recruitment')],
                                  groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    # referred_by = fields.Char(string="Referred By")

    previous_company_display = fields.Char(string="Previous Company")
    previous_company_experience_display_abbr = fields.Char(string="Previous Company Experience")

    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Hour")
    parent_id = fields.Many2one('hr.employee', string="RA")
    date_of_completed_probation = fields.Date(string="Probation complete Date")
    birthday = fields.Date(string="Birthday", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              string="Gender", groups="base.group_user")
    emp_religion = fields.Many2one('kwemp_religion_master', string="Religion")
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    address = fields.Text(string="Address")
    active_display = fields.Char(string="Display")
    primary_skill_id = fields.Many2one('kw_skill_master', string="Primary Skill")
    certification = fields.Char(string="Certification")
    marital_sts = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    refered_by = fields.Char("Referred By", compute="_set_compute", groups="hr.group_hr_manager,kw_employee.group_payroll_manager")
    total_experience_in_year = fields.Integer("Total Experience in Year")
    active_rec = fields.Boolean(string="Active")
    emp_level = fields.Many2one('kw_grade_level', string='Level')
    emp_ph = fields.Char(string="Ph No.")
    emp_mail = fields.Char(string="Email")
    company_id = fields.Many2one('res.company', string='Company')

    @api.multi
    def _set_compute(self):
        for rec in self:
            if rec.id and rec.emp_refered:
                if rec.emp_refered.code == 'employee':
                    rec.refered_by = rec.emp_id.emp_employee_referred.display_name
                elif rec.emp_refered.code == 'consultancy':
                    rec.refered_by = rec.emp_id.emp_consultancy_id.name
                elif rec.emp_refered.code == 'institute':
                    rec.refered_by = rec.emp_id.emp_institute_id.name
                elif rec.emp_refered.code == 'job':
                    rec.refered_by = rec.emp_id.emp_jportal_id.name
                elif rec.emp_refered.code == 'social':
                    rec.refered_by = rec.emp_id.emp_media_id.name
                elif rec.emp_refered.code == 'walkindrive':
                    rec.refered_by = rec.emp_id.emp_reference_walkindrive
                elif rec.emp_refered.code == 'jobfair':
                    rec.refered_by = rec.emp_id.emp_reference_job_fair

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
          
with ed as (SELECT string_agg(name::text,', ') AS education, ed.emp_id
	FROM kwmaster_stream_name AS st, kwemp_educational_qualification  AS ed
	WHERE st.id=ed.stream_id AND ed.course_type != '3'
	GROUP BY ed.emp_id),

ct as (SELECT string_agg(name::text,', ') AS education, ed.emp_id
	FROM kwmaster_stream_name AS st, kwemp_educational_qualification  AS ed
	WHERE st.id=ed.stream_id AND ed.course_type = '3'
	GROUP BY ed.emp_id)

SELECT *,
-- previous_company_experience_display_abbr
CASE when emp.previous_company_exp is not null THEN
concat(div(emp.previous_company_exp, 12)::varchar, 
'.', 
CAST(mod(COALESCE(emp.previous_company_exp,0), 12)::varchar as varchar)) ELSE '0' END AS previous_company_experience_display_abbr,

-- csm_experience_display
CASE WHEN emp.date_of_joining is not null THEN 		
concat(div(emp.csm_exp, 12)::varchar, 
'.', 
CAST(mod(COALESCE(emp.csm_exp,0), 12)::varchar AS varchar)) else '0' END AS csm_experience_display,

-- total_experience_display
concat(div((COALESCE(emp.csm_exp,0) + COALESCE(emp.previous_company_exp,0)), 12)::varchar, 
'.', 
CAST(mod((COALESCE(emp.csm_exp,0) + COALESCE(emp.previous_company_exp,0)), 12)::varchar AS varchar)) AS total_experience_display,

-- total experience in year only
div((COALESCE(emp.csm_exp,0) + COALESCE(emp.previous_company_exp,0)), 12) AS total_experience_in_year

FROM 
(SELECT 
max(hr.id) AS id,
max(hr.id) AS emp_id,
hr.active AS active_rec,
max(hr.employement_type) AS employement_type,
max(hr.emp_role) AS emp_role,
max(hr.emp_category) AS emp_category,
max(hr.job_branch_id) AS job_branch_id,
max(hr.department_id) AS department_id,
max(hr.division) AS division,
max(hr.section) AS section,
max(hr.practise) AS practise,
max(hr.budget_type) AS budget_type,
max(hr.emp_project_id) AS emp_project_id,
max(hr.start_date) AS start_date,
max(hr.end_date) AS end_date,
max(hr.emp_code) AS emp_code,
max(hr.sbu_master_id) AS sbu_master_id, 
max(hr.name) AS name,
max(hr.job_id) AS job_id,
max(hr.date_of_joining) AS date_of_joining,
max(hr.joining_type) AS joining_type,
max(hr.last_working_day) AS date_of_exit,
max(hr.grade) AS grade,
max(hr.emp_band) AS emp_band,
max(hr.level) AS emp_level,
max(hr.location) AS location,
max(hr.company_id) AS company_id,
max(hr.current_ctc) AS current_ctc,
max((SELECT wage FROM hr_contract WHERE hr_contract.employee_id=hr.id ORDER BY id DESC LIMIT 1)) AS contract_ctc,
max(hr.total_experience_display_abbr) AS total_experience_display_abbr,
max(hr.csm_experience_display_abbr) AS csm_experience_display_abbr,
max(hr.emp_refered) AS emp_refered,
max(hr.resource_calendar_id) AS resource_calendar_id,
max(hr.parent_id) AS parent_id,
MAX(hr.date_of_completed_probation) AS date_of_completed_probation,
MAX(hr.birthday) AS birthday,
MAX(hr.gender) AS gender,
MAX(hr.marital_sts) AS marital_sts,
MAX(hr.emp_religion) AS emp_religion,
MAX(hr.blood_group) AS blood_group,
MAX(hr.mobile_phone) AS emp_ph,
MAX(hr.work_email) AS emp_mail,

MAX(hr.primary_skill_id) AS primary_skill_id,
concat_ws(', ',hr.present_addr_street,hr.present_addr_street2,hr.present_addr_city) AS address,
array_to_string((SELECT array_agg(DISTINCT h.name) FROM kwemp_work_experience AS h WHERE h.emp_id = hr.id GROUP BY h.emp_id),', ', '') AS previous_company_display,

(SELECT 
SUM(date_part('year', AGE(x.effective_to, x.effective_from)) * 12 + date_part('month', AGE(x.effective_to, x.effective_from)))::numeric FROM kwemp_work_experience AS x WHERE x.emp_id = hr.id GROUP BY x.emp_id )  AS previous_company_exp,


CASE WHEN hr.date_of_joining is not null THEN
(date_part('year', AGE(CURRENT_DATE, hr.date_of_joining)) * 12 + date_part('month', AGE(CURRENT_DATE, hr.date_of_joining)))::numeric ELSE 0 END  AS csm_exp, 

CASE WHEN hr.active is true THEN 'Active' ELSE 'Inactive' END AS active_display,
string_agg(DISTINCT ed.education::text,', ') AS edu_qualification,
string_agg(DISTINCT ct.education::text,', ') AS certification
FROM hr_employee AS hr
LEFT JOIN kwemp_work_experience  AS kw on hr.id=kw.emp_id
LEFT JOIN ed on ed.emp_id=hr.id
LEFT JOIN ct on ct.emp_id=hr.id
GROUP BY hr.id) AS emp
          )"""
        # concat(h.name,', ',h.designation_name)
        # print("tracker query===========================================================================",query)
        self.env.cr.execute(query)


class AccountFiscalPeriod(models.Model):
    _inherit = 'account.fiscalyear'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self._context
        # print("ctx===========", ctx)
        if 'order_display' in ctx:
            order = ctx['order_display']
        # print("ctx order===========", order)

        res = super(AccountFiscalPeriod, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res


class kw_MIS_employee_report(models.TransientModel):
    _name = "mis_emp_reports_wizard"
    _description = "wizard Financial year"

    def get_fiscal_year(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    fiscalyr = fields.Many2one('account.fiscalyear', string="Financial Year", default=get_fiscal_year)
    types = fields.Selection([('all', 'All'), ('fy', 'Financial Year')], 'Filter Records', default='all')

    def get_employee_report(self):
        tree_view_id = self.env.ref('kw_employee_info_system.kw_mis_manager_employee_list_tree').id
        action = {
            'name': 'MIS For Manager',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.mis.report',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'target': 'main',
            'domain': [('employement_type.code', '!=', 'O')],
            'context': {'manager': True, 'search_default_active_employees': 1},
            'view_id': tree_view_id
        }

        if self.types == 'fy':
            domain = ['|',
                      '&', ('active_rec', '=', True), ('date_of_joining', '<=', self.fiscalyr.date_stop),
                      '&', ('active_rec', '=', False),
                      '&', ('date_of_exit', '>=', self.fiscalyr.date_start), ('date_of_exit', '<=', self.fiscalyr.date_stop)]

            action['name'] = f'MIS For Manager ({self.fiscalyr.name})'
            action['domain'] = domain

        return action
