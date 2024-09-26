from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from odoo.addons import decimal_precision as dp

class HRACityMaster(models.Model):
    _name = 'city_wise_hra_config_master'
    _description = 'IT Declaration HRA Configuration'



    # base_branch_id = fields.Many2one('kw_res_branch')
    city = fields.Char("City")
    hra_percentage = fields.Float(string='HRA Percentage')
