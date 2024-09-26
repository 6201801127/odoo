from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    fetch_key = fields.Char('#Key')
