from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
import re
from datetime import date, datetime,timedelta
from dateutil import relativedelta
from kw_utility_tools import kw_validations
from odoo import http
from math import ceil
from math import floor


class EmployeeProfile(models.Model):
    _inherit = "kw_emp_profile"
    
    @api.model
    def add_employees_to_ra(self):
        reporting_authorities = self.env.ref('kw_employee.group_hr_ra').users.ids
        ra_group = self.env.ref('kw_employee.group_hr_ra', False)
        employees_parent = self.env['hr.employee'].sudo().search([]).mapped('parent_id.user_id')
        for rec in employees_parent:
            if rec.id not in reporting_authorities:
                ra_group.sudo().write({'users': [(4, rec.id)]})
