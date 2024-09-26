from datetime import datetime
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class kw_employee_social_image(models.Model):
    _name = 'kw_update_employee_certification'
    _description = 'Update Employee Certification Survey'
    _rec_name = 'emp_id'

    emp_id = fields.Many2one('hr.employee', string='Employee Name', required=True)
    no_of_skip = fields.Integer(string='No of Skips', default=0)
    skip_date = fields.Date('Skip Date')
    profile_updated = fields.Selection(string='Profile Updated', selection=[('skip', 'No'), ('updated', 'Yes')],
                                       default="skip")
    active = fields.Boolean(default=True)

    @api.model
    def _get_employee_certfication_url(self, user_id):
        certification_url = f"/employee_certification/update/{user_id.employee_ids[0].id}"
        return certification_url
