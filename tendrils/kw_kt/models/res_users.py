from odoo import models, fields, api
import pytz
from datetime import datetime,timedelta


class Users(models.Model):
    _inherit = 'res.users'

    def get_department(self):
        return self.employee_ids and self.employee_ids.department_id and self.employee_ids.department_id.id or False