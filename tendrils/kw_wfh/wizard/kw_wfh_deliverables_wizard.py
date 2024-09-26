from odoo import models, fields, api
import datetime
from datetime import date, datetime
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

state_selection = [('inprogress', 'Inprogress'), ('completed', 'Completed')]

class kw_wfh_deliverables_wizard(models.Model):
    _name = 'kw_wfh_deliverables_wizard'
    _description = 'kw WFH Deliverables Wizard'

    deliverable_record_id = fields.Many2one('kw_wfh_deliverables', string='Deliverables ID')
    status = fields.Selection(string='Status',selection=state_selection, default='completed',required=True)
    comment = fields.Text('Comment')
    submission_date = fields.Date(string='Task Submission Date')
    start_time = fields.Selection(string='Starting Time', selection='_get_time')
    end_time = fields.Selection(string='End Time', selection='_get_time')

    @api.multi
    def submit_task_response(self):
        """  """
        self.deliverable_record_id.show_response_btn = False
        if self.status == 'inprogress':
            self.deliverable_record_id.sudo().write({'state': 'inprogress','comment': self.comment,'submission_date': self.submission_date,'start_time': self.start_time,'end_time': self.end_time})
        if self.status == 'completed':
            self.deliverable_record_id.sudo().write({'state': 'completed','comment': self.comment,'submission_date': self.submission_date,'start_time': self.start_time,'end_time': self.end_time})
        template_id = self.env.ref('kw_wfh.kw_wfh_deliverable_response_mail_template')
        template_id.send_mail(self.deliverable_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Task Response has been cancelled.")


    @api.model
    def _get_time(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)

        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p')))
        return time_list

