from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from odoo.addons import decimal_precision as dp


class Contract(models.Model):
    _inherit = 'hr.contract'

    bank_account = fields.Char('Bank Account Number')
    personal_bank_name = fields.Char('Bank Account Name')