from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
from datetime import date, datetime
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta

state_selection = [('completed', 'Completed'), ('inprogress', 'In-progress')]


class kw_wfh_deliverables(models.Model):
    _name = 'kw_wfh_deliverables'
    _description = "WFH Deliverables"
    _rec_name = 'ref_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('ref_no')
    @api.multi
    def _compute_btn_response(self):
        for record in self:
            if self.env.user.has_group('kw_wfh.group_kw_wfh_user'):
                manager_context = self.env.context.get('report_view_loaded')
                if record.state == 'assigned' and record.env.uid == record.employee_id.user_id.id:
                    record.show_response_btn = True
                if manager_context != True:
                    record.emp_task = True

    @api.model
    def _get_time(self):
        """ Return list of time from 00:00:00 AM to 23:59:59 at interval of 15 minutes """
        dt = datetime.now()
        start_loop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=59, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p')))
        return time_list

    wfh_record_id = fields.Many2one('kw_wfh', string='WFH Record ID')
    ref_no = fields.Char(string="Ref No", required=True, default="New", readonly="1", track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    task_title = fields.Char('Task Title', required=True)
    task_desc = fields.Text('Remarks', required=True)
    status = fields.Selection(string='Task Status', selection=state_selection, required=True)
    comment = fields.Text('Comment')
    submission_date = fields.Date(string='Task Submission Date', required=True)
    start_time = fields.Selection(string='From Time', selection='_get_time', required=True)
    end_time = fields.Selection(string='To Time', selection='_get_time', required=True)
    state = fields.Selection(
        [('draft', 'Inprogress'),
         ('submitted', 'Submitted'), ], string='Status', default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        """Create reference no for the Task record"""
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        vals['employee_id'] = emp.id
        if vals.get('ref_no', 'New') == 'New':
            vals['ref_no'] = self.env['ir.sequence'].next_by_code('kw_wfh_deliverables') or '/'
        return super(kw_wfh_deliverables, self).create(vals)

    @api.constrains('start_time', 'end_time')
    def check_date_between(self):
        if self.start_time > self.end_time:
            raise ValidationError("End Time should be greater than Start Time.")

    def close_wfh_task(self):
        self.write({'state': 'closed'})
        self.env.user.notify_success("Task closed Successfully.")

    def reopen_wfh_task(self):
        self.write({'state': 'assigned'})
        self.env.user.notify_success("Task closed Successfully.")

    def submit_task(self):
        """ Change the state to submitted """
        return self.write({'state': 'submitted'})
