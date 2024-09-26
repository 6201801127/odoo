from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta ,time

class ExtendEffortHourWizard(models.TransientModel):
    _name = "extend_effort_hour"
    _description = "Ticket"


    effort_hour = fields.Float(string="Effort Hour" )
    extend_effort_hour = fields.Float(string="Extend Effort Hour",required=True)
    comment = fields.Text(string='Comment',required=True)
    extend_task_id = fields.Many2one('kw_task_management', default=lambda self: self.env.context.get('active_id'),
                                     string='Extend Task Id')

    @api.constrains('extend_effort_hour')
    def _validation_for_extend_effort_hour(self):
        if not self.extend_effort_hour:
            raise ValidationError("Please select an Extend Effort Hour.")

    @api.multi
    def extend_hour_btn(self):
        task_management_record = self.env['kw_task_management'].browse(self.env.context.get('active_id'))
        task_management_record.write({
            'estimated_hour': task_management_record.estimated_hour + self.extend_effort_hour,
            'extend_effort_hour_bool': True,
            'extend_effort_comment': self.comment,
            'actual_ticket_hour':self.effort_hour,
            'extended_hour':self.extend_effort_hour

        })
        template_id = self.env.ref('task_management.task_management_extend_task_email_template')
        effort_hour_extended_by = self.env.user.employee_ids
        effort_hour_extended_by_name = self.env.user.employee_ids.display_name
        email_from = effort_hour_extended_by.work_email
        mail_to = self.extend_task_id.assigned_to.work_email
        mail_cc = ','.join(self.extend_task_id.notify_to.mapped('work_email'))

        # print(p)
        template_id.with_context(email_from=email_from, email_to=mail_to,email_cc=mail_cc,effort_hour_extended_by=effort_hour_extended_by_name,extend_hr=self.extend_effort_hour).sudo().send_mail(
            self.id, notif_layout="kwantify_theme.csm_mail_notification_light"
        )
        return {'type': 'ir.actions.act_window_close'}