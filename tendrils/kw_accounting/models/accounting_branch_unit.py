from odoo import models, fields, api
from odoo.http import request


class KwBranchUnitInherit(models.Model):
    _inherit = 'accounting.branch.unit'

    company_id = fields.Many2one('res.company',string="Company")         

