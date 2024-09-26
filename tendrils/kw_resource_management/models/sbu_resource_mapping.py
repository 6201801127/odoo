# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class SBUResourceTagging(models.Model):
    _name = 'sbu_resource_mapping'
    _description = 'SBU Resource Mapping'
    _auto = False
    _order = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string='Date of Joining')
    emp_role = fields.Many2one('kwmaster_role_name', string='Employee Role')
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    category_kw_id = fields.Integer(related='employee_id.emp_category.kw_id')
    sbu_name = fields.Char(string='SBU')
    sbu_type = fields.Selection(string='Resource Type',selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT  row_number() over() as id,
            hr.id as employee_id,
            hr.job_id as designation,
            hr.name as name,
            hr.date_of_joining as date_of_joining,
            hr.emp_role as emp_role,
            hr.emp_category as emp_category,
            hr.employement_type as employement_type,
            hr.job_branch_id as job_branch_id,
            hr.sbu_type as sbu_type,
            (select name from kw_sbu_master where id =hr.sbu_master_id) as sbu_name
            from hr_employee as hr 
            join hr_department as hrd on hrd.id= hr.department_id
            where hr.active =true and hrd.code='BSS'
            and hr.sbu_master_id is not null and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
        )""" % (self._table))

    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.applied_eos = True if resignation else False


class SBUMappingWizard(models.TransientModel):
    _name = "sbu_mapping_wizard"
    _description = "SBU Wizard"

    @api.model
    def default_get(self, fields):
        res = super(SBUMappingWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        # print(self.env.context)

        res.update({
            'employee_ids': active_ids,
        })

        return res

    employee_ids = fields.Many2many(
        string='Employee Info',
        comodel_name='sbu_resource_mapping',
        relation='sbu_mapping_employee_rel',
        column1='wizard_id',
        column2='sbu_mapping_id',
    )
    sbu_master_id = fields.Many2one('kw_sbu_master', string='SBU')

    def update_sbu_mapping_of_employee(self):
        query = ''
        for record in self.employee_ids:
            query += f"update hr_employee set sbu_master_id = {self.sbu_master_id.id} where id = {record.employee_id.id};"

        if len(query) > 0:
            self._cr.execute(query)
