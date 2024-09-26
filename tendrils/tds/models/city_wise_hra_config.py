from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from odoo.addons import decimal_precision as dp


class HRACityMaster(models.Model):
    _name = 'city_wise_hra_config_master'
    _description = 'IT Declaration HRA Configuration'

    base_branch_id = fields.Many2one('kw_res_branch')
    city = fields.Char(related='base_branch_id.city')
    hra_percentage = fields.Float(string='HRA Percentage')


class AmountConfig(models.Model):
    _name = 'tds_amount_config'
    _description = 'IT Declaration Amount Config'

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    enable_actual = fields.Boolean()
