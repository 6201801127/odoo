from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError

class EmployeePayslip(models.Model):
    _name = "employee.payslip"
    _description = "employee payslip"

    name = fields.Char(string="Name of The Employee",
                         required=True,
                         help="Please enter employee name")
    age = fields.Char(string="Age")
    payment_amount = fields.Monetary("Payment Amount")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.user.company_id.currency_id)

