from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class employee_previous_occupation(models.Model):
    _inherit = 'employee.previous.occupation'
    _description = 'employee.previous.occupation'

    last_employer = fields.Char(string = 'Last Employer')
    organization_type = fields.Many2one('organization.type', string = "Organisation Type")
    reason_for_leaving = fields.Char(string = 'Reason for Leaving')
    last_drawn_salary = fields.Monetary(string = 'Last Drawn Salary')
    currency_id = fields.Many2one('res.currency')
    service_period = fields.Char(string = 'Service period', compute = 'service_period_count')
    attachment = fields.Binary(string="Attachment",attachment=True)
    c_attachment_filename = fields.Char(string="Attachment Filename")
    remarks = fields.Text(string='Remarks')


    @api.constrains('from_date','to_date')
    @api.onchange('from_date','to_date')
    def onchange_date(self):
        for record in self:
            if record.from_date and record.to_date and record.from_date > record.to_date:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))

    @api.depends('from_date', 'to_date')
    def service_period_count(self):
        if self.from_date and self.to_date:
            r = relativedelta(self.to_date, self.from_date)
            self.service_period = ("{0} years, {1} months, {2} days".format(r.years, r.months, r.days))


    @api.constrains('ref_phone')
    @api.onchange('ref_phone')
    def _check_ref_phone(self):
        for rec in self:
            if rec.ref_phone and not rec.ref_phone.isnumeric():
                raise ValidationError(_("Phone number must be a number - Previous Occupation"))
            if rec.ref_phone and len(rec.ref_phone) != 10:
                raise ValidationError(_("Please enter correct phone number - Previous Occupation."
                                        "It must be of 10 digits"))


class OrganizationType(models.Model):
    _name = 'organization.type'
    _description = "Organization Type"

    name = fields.Char(string = 'Name')
