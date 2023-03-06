from odoo import models,fields,api

class BloodGroup(models.Model):
    _name='blood.group'
    _description='Blood Group'

    name = fields.Char('Name')
    class_id =fields.Many2one('class.class')

class Class(models.Model):
    _name='class.class'
    _description='Blood Group'

    name = fields.Char('Name')
 