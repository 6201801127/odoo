from odoo import api, fields, models, tools, _
import calendar
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError


class ChequeRequests(models.Model):
    _name = "cheque.requests"
    _description = "Cheque Requests"


    employee_id = fields.Many2one('hr.employee')
    identify_id = fields.Char(string='Identification Number')
    name = fields.Char(string='Employee Name')
    birthday = fields.Date('Date of Birth', groups="hr.group_hr_user")
    job_id = fields.Many2one('hr.job', 'Job Position')
    department_id = fields.Many2one('hr.department', 'Department')
    gender = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ], groups="hr.group_hr_user", default="male")

    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft')
    amount = fields.Integer('Amount')
    approve_date = fields.Date('Approve Date')

    @api.multi
    def unlink(self):
        for tour in self:
            if tour.state != 'draft':
                raise UserError(
                    'You cannot delete a Cheque Request which is not in draft state')
        return super(ChequeRequests, self).unlink()

    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.write({'state': 'to_approve'})

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved', 'approve_date': fields.Date.today()})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})
