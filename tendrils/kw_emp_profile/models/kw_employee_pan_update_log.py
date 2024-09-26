from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class Employee_pan_log(models.Model):
    _name = 'kw_employee_update_pan_log'
    _description = 'Employee PAN log'

    employee_id = fields.Many2one("hr.employee", string="Employee")
    is_correct = fields.Boolean(string="Correct")
    is_submitted = fields.Boolean(string="Is Submitted?", default=False)
    skips_check = fields.Integer(string="skips", default=0)

    @api.multi
    def write(self, vals):
        super(Employee_pan_log, self).write(vals)


class EmployeeProjectLog(models.Model):
    _name = "kw_emp_profile_employee_project_data"
    _description = "Employee assign project details"
    _auto = False
    _order = "employee_id"
    
    employee_id = fields.Many2one('hr.employee',string='Resource')
    emp_proj_name = fields.Char(string="Project name",)
    emp_proj_manager = fields.Char(string="Project manager")
    emp_proj_start_date = fields.Char(string="Start date")
    duration = fields.Char(string="Duration")
    emp_profile_id = fields.Many2one('kw_emp_profile', string="Profile id")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (

        with project as
		(select prj.name as project_id,
		 prj.code as project_code,
		 rt.emp_id as employee_id,
		 prj.crm_id,
		 prj.emp_id,
         rt.start_date
		 from hr_employee emp
		 left join project_project prj on prj.emp_id = emp.id
		 left join kw_project_resource_tagging rt on rt.project_id=prj.id
		 where prj.active = True and rt.active = True)
			
		    SELECT  row_number() over() AS id,
                    emp.id as employee_id,
                    TO_CHAR(pj.start_date, 'DD-Mon-YYYY') AS emp_proj_start_date,
 					pj.project_id as emp_proj_name,
					(select name from hr_employee where id=pj.emp_id) as emp_proj_manager,
                    CASE
                        WHEN pj.start_date >= emp.date_of_joining THEN
                            CONCAT(EXTRACT(YEAR FROM AGE(NOW(), pj.start_date)), ' year ',
                                EXTRACT(MONTH FROM AGE(NOW(), pj.start_date)), ' months'
                            )
                        ELSE
                            'Not started yet'
                    END AS duration,
                    ep.id AS emp_profile_id
				From hr_employee as emp
				left join project pj on pj.employee_id = emp.id
                left join kw_emp_profile ep on ep.emp_id = emp.id
                where emp.active = True
				group by emp.emp_code,emp.id, emp.sbu_master_id, pj.project_id,  pj.start_date, pj.employee_id, pj.emp_id, ep.id)""" )


class EmployeeReward(models.Model):
    _name = "kw_emp_reward_and_recognition"
    _description = "kw_emp_reward_and_recognition"
    _auto = False
    _order = "employee_id"
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    month = fields.Char(string='Month', )
    year = fields.Char(string='Year',)
    state = fields.Selection([('sbu', 'Draft'), ('nominate', 'Nominated'), ('review', 'Reviewed'), ('award', 'Awarded'),
                              ('finalise', 'Published'), ('reject', 'Rejected')])
    emp_profile_id = fields.Many2one('kw_emp_profile')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT   
            ROW_NUMBER() OVER () as id,
            rr.employee_id as employee_id,
            rr.compute_month as month,
            rr.compute_year as year,
            rr.state as state,
            ep.id as emp_profile_id
        FROM reward_and_recognition rr
        left join kw_emp_profile ep on ep.emp_id = rr.employee_id
        WHERE rr.state in  ('finalise','award')
         )"""
        self.env.cr.execute(query)


class EmployeeAppraisal(models.Model):
    _name = "kw_emp_appraisal_profile"
    _description = "kw_emp_appraisal_profile"
    _auto = False
    _order = "emp_id"
    
    emp_id = fields.Many2one('hr.employee',string="Employee")
    appraisal_year = fields.Char(string="Appraisal Period")
    kra_score = fields.Float(string="KRA Score",)
    score = fields.Float(string="Appraisal Score",)
    emp_profile_id = fields.Many2one('kw_emp_profile')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
           SELECT   
            ROW_NUMBER() OVER () as id,
            ha.emp_id as emp_id,
            ha.appraisal_year as appraisal_year,
            ha.score as score,
            ha.kra_score as kra_score,
            ep.id as emp_profile_id
            FROM hr_appraisal ha
            left join kw_emp_profile ep on ep.emp_id = ha.emp_id
            where ha.state= (select id from hr_appraisal_stages where sequence=6)

         )"""
        self.env.cr.execute(query)


class EmployeeAssessmentPeriodic(models.Model):
    _name = "kw_profile_assessment_periodic"
    _description = "kw_profile_assessment_periodic"
    _auto = False
    _order = "employee_id"
    
    employee_id = fields.Many2one('hr.employee', string='Employee',)
    period_id = fields.Many2one('kw_feedback_assessment_period',)
    total_score = fields.Float(string='Avg. Score (in %)',)
    suggestion_remark = fields.Text(string='Suggestion')
    feedback_status = fields.Selection(string='Status',
                                       selection=[('0', 'Not Scheduled'), ('1', 'Scheduled'), ('2', 'Draft'),
                                                  ('3', 'Completed'), ('4', 'Sent for Approval'), ('5', 'Approved'),
                                                  ('6', 'Published')])
    empl_profile_id = fields.Many2one('kw_emp_profile')
     
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
          SELECT   
            ROW_NUMBER() OVER () as id,
            fd.assessee_id as employee_id,
            fd.period_id as period_id,
            fd.total_score as total_score,
            fd.suggestion_remark as suggestion_remark,
            fd.feedback_status as feedback_status,
            ep.id as empl_profile_id
        FROM kw_feedback_details fd
        left join kw_feedback_assessment fa on fa.id = fd.assessment_tagging_id
        left join kw_emp_profile ep on ep.emp_id = fd.assessee_id
        where fa.assessment_type = 'periodic' and fd.feedback_status = '6'
        )"""
        self.env.cr.execute(query)


class EmployeeAssessmentProbationary(models.Model):
    _name = "kw_profile_assessment_probatinary"
    _description = "kw_profile_assessment_probatinary"
    _auto = False
    _order = "employee_id"
    
    employee_id = fields.Many2one('hr.employee', string='Employee',)
    period_id = fields.Many2one('kw_feedback_assessment_period',)
    total_score = fields.Float(string='Avg. Score (in %)',)
    suggestion_remark = fields.Text(string='Suggestion')
    feedback_status = fields.Selection(string='Status',
                                       selection=[('0', 'Not Scheduled'), ('1', 'Scheduled'), ('2', 'Draft'),
                                                  ('3', 'Completed'), ('4', 'Sent for Approval'), ('5', 'Approved'),
                                                  ('6', 'Published')])
    empl_profile_id = fields.Many2one('kw_emp_profile')
     
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
          SELECT   
            ROW_NUMBER() OVER () as id,
            fd.assessee_id as employee_id,
            fd.period_id as period_id,
            fd.total_score as total_score,
            fd.suggestion_remark as suggestion_remark,
            fd.feedback_status as feedback_status,
            ep.id as empl_profile_id
        FROM kw_feedback_details fd
        left join kw_feedback_assessment fa on fa.id = fd.assessment_tagging_id
        left join kw_emp_profile ep on ep.emp_id = fd.assessee_id
        where fa.assessment_type = 'probationary' and fd.feedback_status = '6'
        )"""
        self.env.cr.execute(query)

    @api.multi
    def action_download_emp_prob(self):
        for rec in self:
            if self._context.get('button') == 'Probation':
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/download_emp_probatinary_update_doc/{rec.employee_id.id}',
                    'target': 'self',
                }


class EmployeeHistorydata(models.Model):
    _name = "kw_emp_history_update"
    _description = "kw_emp_history_update"
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee', )
    start_date = fields.Char(string="Start Date")
    dept_id = fields.Many2one('hr.department', string="Department")
    deg_id = fields.Many2one('hr.job', string='Designation')
    emp_ra_id = fields.Many2one('hr.employee', related="employee_id.parent_id")
    empl_profile_id = fields.Many2one('kw_emp_profile')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
           SELECT   
            ROW_NUMBER() OVER () as id,
			ph.emp_id  as employee_id,
            ph.start_date as start_date,
            ph.dept_id as dept_id,
            ph.deg_ig as deg_id,
            ep.id as empl_profile_id
        FROM kw_emp_history ph
        left join kw_emp_profile ep on ep.emp_id = ph.emp_id
        )"""
        self.env.cr.execute(query)
