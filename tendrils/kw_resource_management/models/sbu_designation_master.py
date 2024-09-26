from odoo import fields, models, api

class SBUDesignationMaster(models.Model):
    _name="sbu_designation_master"


    name = fields.Char('Name')
    designation_ids = fields.Many2many('hr.job')
