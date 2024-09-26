from odoo import models, fields, api
from odoo import tools
from datetime import date, datetime


class WsMisEmployee(models.Model):
    _name = "hr.employee.workstation.mis.report"
    _description = "Employee Work Station MIS Report"
    _auto = False
    _order = 'name asc'

    emp_id = fields.Many2one('hr.employee')
    emp_code = fields.Char(string="Emp. Code")
    name = fields.Char(string="Name")
    job_branch_id = fields.Many2one('kw_res_branch', string="Work Location")
    department_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practise")
    practise = fields.Many2one('hr.department', string="Section")
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],
                                   string="Budget Type")
    emp_project_id = fields.Many2one('crm.lead', string="Project Name")
    start_date = fields.Date(string="Contract Start Date")
    end_date = fields.Date(string="Contract End Date")
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU")
    sbu = fields.Char(related='sbu_master_id.name', string="SBU Name")
    representative_id = fields.Many2one('hr.employee', string="Representative")
    job_id = fields.Many2one('hr.job', string="Designation")
    location = fields.Char(string="Work Mode")
    parent_id = fields.Many2one('hr.employee', string="RA")
    ws_name = fields.Char(string="Workstation", size=100)
    ws_branch_id = fields.Many2one('kw_res_branch', string="Branch", )
    ws_branch_unit_id = fields.Many2one('kw_res_branch_unit', string='WS Unit',
                                        domain="[('branch_id', '=', branch_id)]")
    ws_workstation_type = fields.Many2one('kw_workstation_type', string="WS Type")
    infrastructure = fields.Many2one('kw_workstation_infrastructure', string="WS Infra",
                                     domain="[('branch_unit_id','=', branch_unit_id)]")
    project_tagged = fields.Char(string="Project Tagged")
    project_manager = fields.Char(string="Project Manager")
    date_of_joining = fields.Date(string="Date of Joining")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            with ws AS (SELECT ws.name AS ws_name,
                ws.branch_id AS ws_branch_id,
                ws.branch_unit_id AS ws_branch_unit_id,
                ws.infrastructure AS infrastructure,
                ws.workstation_type AS ws_workstation_type,
                ws_rel.eid AS emp_id
                FROM kw_workstation_master AS ws
                JOIN kw_workstation_hr_employee_rel AS ws_rel ON ws.id=ws_rel.wid),
                
                projtag AS (SELECT pt.emp_id, pt.project_id, pt.start_date, pt.end_date, pt.active, pp.name, concat(he.name, '(',he.emp_code, ')') AS project_manager
                    FROM kw_project_resource_tagging pt
                    LEFT JOIN project_project pp ON pp.id=pt.project_id AND pp.active=true
                    LEFT JOIN hr_employee he ON he.id=pp.emp_id AND he.active=true
                    WHERE pt.active=true AND pt.emp_id IS NOT NULL)
            
            SELECT
                hr.id AS id,
                hr.emp_code AS emp_code,
                hr.date_of_joining AS date_of_joining,
                hr.name AS name,
                hr.job_branch_id AS job_branch_id,
                hr.department_id AS department_id,
                hr.division AS division,
                hr.section AS section,
                hr.practise AS practise,
                CASE WHEN hr.budget_type='treasury' THEN 'Treasury' WHEN hr.budget_type='project' THEN 'Project' ELSE 'NA' END AS budget_type,
                hr.emp_project_id AS emp_project_id,
                hr.start_date AS start_date,
                hr.end_date AS end_date,
                hr.sbu_master_id AS sbu_master_id,
                (select representative_id from kw_sbu_master where id = hr.sbu_master_id) AS representative_id,
                hr.job_id AS job_id,
                CASE WHEN hr.location='wfa' THEN 'WFA' ELSE INITCAP(hr.location) END AS location,
                hr.parent_id AS parent_id,
                max(ws.ws_name) AS ws_name,
                max(ws.ws_branch_id) AS ws_branch_id,
                max(ws.ws_branch_unit_id) AS ws_branch_unit_id,
                max(ws.infrastructure) AS infrastructure,
                max(ws.ws_workstation_type) AS ws_workstation_type,
                max(ws.emp_id) AS emp_id,
                string_agg(DISTINCT projtag.name::text,', ') AS project_tagged,
                string_agg(DISTINCT projtag.project_manager::text,', ') AS project_manager
                FROM hr_employee AS hr
                LEFT JOIN ws on hr.id=ws.emp_id
                LEFT JOIN projtag ON projtag.emp_id=hr.id
                WHERE hr.active=true AND hr.employement_type != 5
                GROUP BY hr.id
                ORDER BY hr.name asc)"""
        self.env.cr.execute(query)
