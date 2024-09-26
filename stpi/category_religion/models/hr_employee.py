# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class Religion(models.Model):
    _name = 'employee.religion'
    _description = 'Employee Religion'
    _rec_name ='name'

    name = fields.Char('Religion')


class Category(models.Model):
    _name = 'employee.category'
    _description = 'Employee category'
    _rec_name = 'name'

    name = fields.Char('Category')

class relativ_type(models.Model):
    _name = 'relative.type'
    _description = 'Relative Description'

    name = fields.Char('Name')
    gender = fields.Selection(
        [('Male', 'Male'), ('Female', 'Female')])


class EmployeeBranch(models.Model):
    _inherit = 'hr.employee'

    # track_visibility = 'onchange' added in existing fields.
    branch_id = fields.Many2one('res.branch', string='Center', store=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', track_visibility='onchange')
    job_id = fields.Many2one('hr.job', track_visibility='onchange', string="Post")
    parent_id = fields.Many2one('hr.employee', track_visibility='onchange')
    manager = fields.Boolean(track_visibility='onchange')

