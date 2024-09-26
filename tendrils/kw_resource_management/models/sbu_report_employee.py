from odoo import models, fields, api
from odoo import tools


class SbuReportEmployee(models.Model):
    _name = "hr.employee.sbu.mapped.detail.report"
    _description = "Employee SBU Mapped Report"
    _auto = False

    sbu_id = fields.Many2one('kw_sbu_master', string="SBU")
    sbu_name = fields.Char(string="SBU")
    sbu_type = fields.Selection(
        string='Resource Type',
        selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal'), ('others', 'Others')])
    project_id = fields.Many2one('crm.lead', string="Project")
    project_manager = fields.Many2one('hr.employee', string="Project Manager")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    designation = fields.Many2one('hr.job', string="Employee Designation")
    representative_id = fields.Many2one('hr.employee', string='Representative')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT row_number() over() AS id, 
            hr.sbu_type AS sbu_type,
            hr.sbu_master_id AS sbu_id, 
            cl.id AS project_id,
            pp.emp_id AS project_manager, 
            hr.id AS employee_id,
            hr.job_id AS designation,
            (select representative_id FROM kw_sbu_master where id = hr.sbu_master_id limit 1) AS representative_id,
            (select name FROM kw_sbu_master where id = hr.sbu_master_id limit 1) AS sbu_name
            FROM hr_employee AS hr 
            left join crm_lead AS cl on hr.emp_project_id = cl.id
            left join project_project AS pp on cl.id = pp.crm_id
            WHERE hr.sbu_master_id is not null
        )"""
        # print("tracker quey",query)
        self.env.cr.execute(query)
