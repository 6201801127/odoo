import string
from odoo import fields, models, api
import json
import requests
# from datetime import datetime, date
from dateutil import relativedelta

import calendar
import datetime

class KwPayrollLog(models.Model):
    _name = 'kw_payroll_log'
    _description = 'Kwantify Payroll Log'
    _rec_name = "create_date"

    
    request_params = fields.Text()
    response_result = fields.Text()
   