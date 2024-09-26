from odoo import api, fields, models, tools, _
import calendar
import datetime
from dateutil.relativedelta import relativedelta

class BirthdayCheck(models.Model):
    _inherit = "hr.employee"

    is_previous_month = fields.Boolean(compute="_check_previous_month", store=True)
    is_current_month = fields.Boolean(compute="_check_current_month", store=True)
    is_next_month = fields.Boolean(compute="_check_next_month", store=True)
    cheque_requested = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no', string='Cheque Requested')

    @api.depends('birthday')
    def _check_previous_month(self):
        for rec in self:
            month = (datetime.datetime.now().replace(day=1) - relativedelta(months=1)).strftime("%m")
            if rec.birthday:
                bday_month = rec.birthday.strftime("%m")
                if month == bday_month:
                    rec.is_previous_month = True
                else:
                    rec.is_previous_month = False

    @api.depends('birthday')
    def _check_current_month(self):
        for rec in self:
            month = datetime.datetime.now().strftime("%m")
            if rec.birthday:
                bday_month = rec.birthday.strftime("%m")
                if month == bday_month:
                    rec.is_current_month = True
                else:
                    rec.is_current_month = False


    @api.depends('birthday')
    def _check_next_month(self):
        for rec in self:
            month = (datetime.datetime.now().replace(day=1)+ relativedelta(months=1)).strftime("%m")
            if rec.birthday:
                bday_month = rec.birthday.strftime("%m")
                if month == bday_month:
                    rec.is_next_month = True
                else:
                    rec.is_next_month = False



    def birthday_check_cron(self):
        emp_records = self.env['hr.employee'].search([])
        for rec in emp_records:
            today = datetime.date.today()
            if rec.birthday:
                # if (today - rec.birthday).days >30:
                    # rec.cheque_requested = 'no'
                if today.month == 12 and today.day == 31:
                    rec.cheque_requested = 'no'
                    print('jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj',rec.cheque_requested)