# -*- coding: utf-8 -*-

from odoo import models, fields, api,_




class EmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    name = fields.Many2one('hr.employee.document.master', string='Document Name')

    @api.onchange('name')
    def get_desc_f_n(self):
        for rec in self:
            if rec.name.description:
                rec.description = rec.name.description



class DocMaster(models.Model):
    _name = 'hr.employee.document.master'
    _description = 'Employee Doc Master'

    name = fields.Char('Name')
    description = fields.Char('Description')
