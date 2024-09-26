from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re

class EmployeeProfileReport(models.Model):
    _name = "employee.profile.report"
    _description = "Employee Profile Report"

    employee_id  = fields.Char(string='Name')
    requested_by = fields.Char(string='Requested By')
    approved_by = fields.Char(string='Approved By')
    designation  = fields.Char(string='Designation')
    department  = fields.Char(string='Department')
    branch_id  = fields.Char(string='Branch')
    date = fields.Date(string='Requested Date')
    approved_date = fields.Date(string='Approved Date')
    field_n = fields.Char(string='Field')
    old_value = fields.Char(string='Old Value')
    new_value = fields.Char(string='New Value')
