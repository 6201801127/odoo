from odoo import models, fields, api


class crm_team_inherit(models.Model):
    _inherit = 'crm.team'

    kw_id = fields.Integer("KW ID")


class CRMStage(models.Model):
    _inherit = 'crm.stage'

    code = fields.Char('Code')
