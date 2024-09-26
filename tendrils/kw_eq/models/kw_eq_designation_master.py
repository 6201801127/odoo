# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DesignationMaster(models.Model):
    _name = 'kw_eq_designation_master'
    _description = 'Designation configuration'
    _order = "functional_category,designation_id"

    functional_category = fields.Selection(string="Functional Category",selection=[('1', 'Software Consultancy'),('2', 'IT Infra Consultancy'),('3', 'Social Media Consultancy')])
    designation_id = fields.Many2one('hr.job',string="Designation")
    section = fields.Selection([('1', 'Section 1'),('2', 'Section 2'),('3', 'Section 3')])
