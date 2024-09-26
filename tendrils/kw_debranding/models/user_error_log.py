from odoo import models, fields, api


class UserErrorLog(models.Model):
    _name = "user_error_log"
    _description = "Stores Error Log"
    _order = "id desc"

    employee_id = fields.Many2one('hr.employee',string="Name")
    payload = fields.Char(string="Payload")
    status = fields.Char("Status")
    