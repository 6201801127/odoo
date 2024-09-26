from odoo import fields,api,models
import math
from datetime import datetime, timedelta
from pytz import timezone, UTC


class LateComingReport(models.Model):
    _name="reimbursement.model.report"
    _description="Reimbursement Report"
    _rec_name = "reimbursement_type_id"

    reimbursement_sequence = fields.Char('Reimbursement number', track_visibility='always')
    name = fields.Selection([
        ('lunch', 'Lunch Subsidy'),
        ('telephone', 'Telephone Reimbursement'),
        ('mobile', 'Mobile Reimbursement'),
        ('medical', 'Medical Reimbursement'),
        ('tuition_fee', 'Tuition Fee claim'),
        ('briefcase', 'Briefcase Reimbursement'),
        ('quarterly', 'Newspaper Reimbursements'),
    ], string='Reimbursement Type', store=True, track_visibility='always')
    reimbursement_type_id = fields.Many2one('reimbursement.type','Reimbursement Type',track_visibility='always')

    employee_id = fields.Many2one('hr.employee', store=True, track_visibility='always', string='Requested By')
    job_id = fields.Many2one('hr.job', string='Functional Designation', store=True, track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Branch', store=True, track_visibility='always')
    department_id = fields.Many2one('hr.department', string='Department', store=True, track_visibility='always')
    claimed_amount = fields.Float(string='Claimed Amount', track_visibility='always')
    net_amount = fields.Float(string='Eligible Amount', track_visibility='always')
    working_days = fields.Char(string='Number of days: ', track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('waiting_for_approval', 'Submitted'), ('forwarded', 'Forwarded'),
                              ('approved', 'Approved'), ('rejected', 'Rejected')
                              ], string='Status')

    
#     emp_name = fields.Char(string="Employee Name")
#     emp_id = fields.Many2one('hr.employee',string="Employee")
#     dept_id = fields.Many2one('hr.department',string="Department")
#
#     check_in = fields.Datetime(string="Check In")
#     check_out = fields.Datetime(string="Check Out")
#
#
#     duty_hr = fields.Float(string="Duty Hours")
#     actual_duty_hr = fields.Float(string="Actual Duty Hours")
#     late_coming_min = fields.Float(string="Late Coming Min")
#     roster_id = fields.Many2one('hr.attendance.roster',string="Roster")
#
# #     branch_id = fields.Many2one('res.branch',string= 'Branch')
#
    def get_late_coming_report(self):
        return self.env['reimbursement.model.report'].search([])

#
#     @api.model
#     def value_to_html(self, value):
#         sign = math.copysign(1.0, value)
#         hours, minutes = divmod(abs(value) * 60, 60)
#         minutes = round(minutes)
#         if minutes == 60:
#             minutes = 0
#             hours += 1
#         return '%02d:%02d' % (sign * hours, minutes)
#
#     def get_time_without_tz(self, time):
#         ret_time = time + timedelta(hours=5, minutes=30)
#         return datetime.strftime(ret_time, '%d-%m-%Y %H:%M:%S')
#
#     @api.multi
#     def name_get(self,roster_id):
#         name = ''
#         for record in roster_id:
#             name = (str(record.employee_id.name) + '-' + str(record.shift_id.name))
#         return name