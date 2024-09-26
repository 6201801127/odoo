from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta


class HrItRule(models.Model):
    _name = 'hr.itrule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'IT Rule'
    _rec_name = 'name'

    deduction_id = fields.Text(string='Deduction')
    code = fields.Char('Code')
    name = fields.Char('IT Rule Section')
    rebate = fields.Float('Rebate')

    @api.constrains('name', 'code')
    def validate_name_code(self):
        for rec in self:
            record = self.env['hr.itrule'].sudo().search([('name', '=', rec.name)]) - self
            if record:
                raise ValidationError(f"{record.name} Already Exist.")
            code_rec = self.env['hr.itrule'].sudo().search([('code', '=', rec.code)]) - self
            if code_rec:
                raise ValidationError(f"{code_rec.code} Already Exist.")