# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kw_employee_inherit(models.Model):
    _inherit = 'hr.employee'

    project_id      = fields.One2many(string='Project Name',comodel_name='project.project',inverse_name='emp_id',ondelete='restrict')
    tagged_project  = fields.Char('Tagged Project',compute='_compute_tagged_project_name')
    project_manager_name = fields.Char('Project Manager',compute='_compute_tagged_project_name')

    def _compute_tagged_project_name(self):
        for record in self:
            tagged_project = ''
            project_manager_name = ''
            data = self.env['kw_project_resource_tagging'].sudo().search([('emp_id','=',record.id)])
            for project_records in data:
                if project_records.project_id.name:
                    tagged_project += project_records.project_id.name +', '
                    record.tagged_project = tagged_project.rstrip(', ')
                if project_records.project_id.emp_id.name: 
                    project_manager_name += project_records.project_id.emp_id.name +', '
                    record.project_manager_name = project_manager_name.rstrip(', ')
