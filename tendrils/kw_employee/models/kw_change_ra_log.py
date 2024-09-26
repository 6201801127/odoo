# -*- coding: utf-8 -*-
from odoo import fields, models, api


class kw_change_ra_log(models.TransientModel):
    _name = 'kw_change_ra_log'
    _description = 'Change of Reporting Authority'

    ra_rel_id = fields.Many2one('kw_change_ra_relation')
    emp_name = fields.Many2one('hr.employee', string="Employee Name")
    emp_code = fields.Char(related='emp_name.emp_code', string='Employee Code')
    emp_designation = fields.Char(related='emp_name.job_id.name', string="Designation")
    emp_parent = fields.Char(related='emp_name.parent_id.name', string="Existing RA")
    new_ra_id = fields.Many2one('hr.employee', string='New RA')
    new_ra_designation = fields.Char(related='new_ra_id.job_id.name', string="New RA Designation")

    new_ra_gender = fields.Char(compute='_compute_new_ra_gender', store=True)

    @api.depends('new_ra_id')
    def _compute_new_ra_gender(self):
        for record in self:
            if record.new_ra_id.id != False:
                if record.new_ra_id.gender == 'male':
                    record.new_ra_gender = 'he'
                else:
                    record.new_ra_gender = 'she'
