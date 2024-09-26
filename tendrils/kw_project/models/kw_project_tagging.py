# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import date


class kw_project_resource_tagging(models.Model):
    _name = 'kw_project_resource_tagging'
    _description = 'Resource tagging'
    _rec_name = 'designation'

    kw_id = fields.Integer(string='KW ID')
    designation_id = fields.Many2one('hr.job', string='Designation ID')
    designation = fields.Char(string='Designation')
    emp_id = fields.Many2one('hr.employee', string='Employee')
    project_id = fields.Many2one('project.project', string='Project Name',ondelete='cascade',required=True)
    start_date = fields.Date("Start Date")
    end_date = fields.Date('End Date')
    active = fields.Boolean('Status', default=True)
    reporting_id = fields.Many2one('hr.employee', string='Reporting')
    # Related fields
    # skill_ids     = fields.Many2many(related='emp_id.skill_id',string='Skill')
    project_manager = fields.Char(related='project_id.emp_id.name', string='Project Manager')
    project_name = fields.Char(related='project_id.name', string='Project Name')

    # @api.model
    # def create(self, vals):
    #     res = super(kw_project_resource_tagging, self).create(vals)
    #     update_query = f"UPDATE project_project SET emp_id = (select emp_id from kw_project_resource_tagging where reporting_id is null and project_id = {res.project_id.id}) where id = {res.project_id.id}"
    #     self._cr.execute(update_query)
    #     return res
