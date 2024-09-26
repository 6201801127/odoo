import string
from odoo import fields, models, api
import json
import requests
# from datetime import datetime, date
from dateutil import relativedelta

import calendar
import datetime


class KwPayrollAttendanceLog(models.Model):
    _name = 'kw_attendance_log'
    _description = 'Kwantify attendance Log'
    _rec_name = "create_date"

    request_params = fields.Text()
    response_result = fields.Text()
