from odoo import models,fields, api

class CRMStages(models.Model):
    _inherit = 'crm.stage'

    code = fields.Char(string="Code")
    active = fields.Boolean(string="Active",default=True)