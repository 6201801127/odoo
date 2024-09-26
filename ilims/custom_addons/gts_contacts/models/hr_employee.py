
from odoo import fields,models,api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    role_responsibility = fields.Html(string='Rolls & Responsibility' , groups="hr.group_hr_user")
