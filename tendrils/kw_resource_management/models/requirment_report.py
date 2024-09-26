from odoo import models, fields, api
from odoo import tools


class RequirmentReportApplicant(models.Model):
    _name = "requirment_report_applicants"
    _description = "Recruitment MRF report"
    _auto = False
    
    type_project=fields.Selection(string='Requirment type',selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')])
    code=fields.Char('MRF code')
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Pending'),
                              ('hold', 'Hold'), ('revise', 'Revise'),
                              ('forward', 'Forwarded'), ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ], string='MRF Status')
    dept=fields.Many2one('hr.department',string="Department")
    project = fields.Many2one('crm.lead', string='Project')
    skill = fields.Text('Skill (Technology)')
    job_position = fields.Many2one('hr.job', string="Designation")
    experience = fields.Char(string="Experience")
    resource = fields.Selection(string='Hiring Type',
                                selection=[('new', 'New'), ('replacement', 'Replacement')])
    employee_id = fields.Many2one('hr.employee', string='Replacement of') 
    no_of_resource = fields.Integer('Offered position')
    date_of_joining = fields.Date(string='Joining Date')
    branch_id = fields.Many2one('kw_recruitment_location', string='Location')
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT row_number() over() AS id, 
            hr.type_project AS type_project,
            hr.code AS code, 
            hr.state AS state,
            d.id AS dept,
            cl.id AS project,
            hr.skill_set AS skill,
            j.id AS job_position,
            
            hr.max_exp_year AS experience,
            hr.resource AS resource,
			h.hr_employee_id AS employee_id,
            hr.no_of_resource AS no_of_resource,
            hr.date_of_joining AS date_of_joining,
            kl.kw_recruitment_location_id as branch_id
            FROM kw_recruitment_requisition AS hr 
            left join hr_job AS j on hr.job_position = j.id
            left join crm_lead AS cl on hr.project = cl.id
            left join hr_department AS d on hr.dept_name = d.id
            left join hr_employee_kw_recruitment_requisition_rel AS h on h.kw_recruitment_requisition_id =hr.id
            left join kw_recruitment_location_kw_recruitment_requisition_rel AS kl on kl.kw_recruitment_requisition_id=hr.id
        )"""
        self.env.cr.execute(query)
    
    
     
     