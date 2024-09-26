# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class SBUBenchResource(models.Model):
    _name = 'project_time_management'
    _description = 'SBU Bench Resource'
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    end_date = fields.Date(string='Contract End Date')
    emp_project_id = fields.Many2one('crm.lead', string="Order Name/Code")
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    employement_type = fields.Many2one('kwemp_employment_type', string="Employment/Contract Type")
    order_name = fields.Char(related='employee_id.emp_project_id.name', string='Order Name')
    order_code = fields.Char(related='employee_id.emp_project_id.code', string='Order Code')
    expired_value = fields.Char("Status")
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
    select row_number() over() as id,
            id as employee_id,
            date_of_joining as date_of_joining,
            job_id as designation,
            end_date as end_date,
            job_branch_id as job_branch_id,
            emp_project_id as emp_project_id,
            vendor_id as vendor_id,
            current_date as current_date,
            employement_type as employement_type,
        case
            when end_date < current_date then 'expired'
            when end_date BETWEEN (select current_date) AND (select current_date + 30) then 'to_be_expired'
            else 'no_change'
            end as expired_value
            
        from hr_employee where active = true and 
        emp_role = (select id from kwmaster_role_name where code = 'R') and employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
         )""" % (self._table))

    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.applied_eos = True if resignation else False
