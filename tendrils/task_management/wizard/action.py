from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta ,time
from datetime import timedelta
import pytz
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class ReportWizard(models.TransientModel):
    _name = "report_wizard"
    _description = "Ticket"

    def _default_actual_hour(self):
        return fields.Datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    actual_hour = fields.Datetime(string="Actual Hour", default=_default_actual_hour)
    start_time = fields.Datetime(string="Start Time")
    pause_time = fields.Datetime(string="Pause Time")
    comment = fields.Text(string='Comment')

    project_id = fields.Many2one('project.project', string="Project",
                                 default=lambda self: self.env.context.get('current_proj'), readonly=1)
    prject_category_id = fields.Many2one('kw_project_category_master', string='Category Name',
                                         domain=[('code', '=', 'PW')])
    parent_task_id = fields.Many2one('project.task', string="Activity")
    task_id = fields.Many2one('project.task', string="Task")
    time_spent = fields.Float(string="Time Spent", default=0.0)
    date_of = fields.Date(string="Date", default=date.today())
    stage_of = fields.Selection([('Complete', 'Gracefully Closed'), ('Reject', 'Reject')], string="Status",
                                default='Complete')

    assign_task_id = fields.Many2one('kw_task_management', default=lambda self: self.env.context.get('active_id'),
                                     string='Assign Task Id')
    reopen_bool = fields.Boolean(string="Do you want to create a new task in case of rejection?")

    @api.multi
    def btn_confirm(self):
        task_record = self.env['kw_task_management'].browse(self.env.context.get('active_id'))
        actual_hour = datetime.now()

        if self._context.get('current_btn') == 'stop_task':

            last_log = task_record.sr_task_log_ids[-1]
            duration = last_log._duration(last_log.start_datetime, self.actual_hour)
            # print('duration 1 >>>> ', duration)
            last_log.write({
                'end_datetime': self.actual_hour,
                'task_duration': duration,
                # 'action': 'Stopped',
            })
            task_record = last_log.task_sr_management_id
            duration = sum([r.task_duration for r in task_record.sr_task_log_ids if r.action != 'Paused'])
#             print('duration 2 >>>> ', duration, last_log.task_duration)
            task_record.write({
                'end_datetime_task': self.actual_hour,
                'store_stop_time': self.actual_hour,
                'task_duration': duration + 0.01,
                'stage': self.env.context.get('stage'),
                'comment': self.comment,
                'sr_task_log_ids': [(0, 0, {
                    'start_datetime': self.actual_hour,
                    'stage_comments': self.comment,
                    'action': 'Stopped',
                })]
            })
            # timesheet_record = self.env['account.analytic.line'].create(
            #             {'employee_id': self.env.user.employee_ids.id,
            #              'date': self.date_of,
            #              'prject_category_id': self.prject_category_id.id,
            #              'project_id': self.project_id.id,
            #              'parent_task_id': self.parent_task_id.id,
            #              'task_id': self.task_id.id,
            #              'unit_amount': self.time_spent,
            #              'name': self.comment})

            template_id = self.env.ref('task_management.task_management_closed_task_email_template')
            closed_by = self.env.user.employee_ids
            closed_by_name = closed_by.display_name
            email_from = closed_by.work_email
            mail_to = self.assign_task_id.task_raised_by.work_email
            mail_cc = ','.join(self.assign_task_id.notify_to.mapped('work_email'))
            template_id.with_context(email_from=email_from,
                                     email_to=mail_to,
                                     email_cc=mail_cc,
                                     closed_by=closed_by_name).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        elif self._context.get('current_btn') == 'acknowledge':
            if self.stage_of == 'Complete':
                template_id = self.env.ref('task_management.task_management_complete_task_email_template')
                acknowledge_by = self.env.user.employee_ids
                acknowledge_by_name = self.env.user.employee_ids.display_name
                email_from = acknowledge_by.work_email
                mail_to = self.assign_task_id.assigned_to.work_email
                mail_cc = ','.join(self.assign_task_id.notify_to.mapped('work_email'))
                template_id.with_context(email_from=email_from,
                                         email_to=mail_to,
                                         email_cc=mail_cc,
                                         acknowledge_by=acknowledge_by_name, mail_for='Complete').sudo().send_mail(
                    self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                task_record.write({
                    'ack_comment': self.comment,
                    'stage': 'Complete'
                })

            else:
                template_id = self.env.ref('task_management.task_management_complete_task_email_template')
                acknowledge_by = self.env.user.employee_ids
                acknowledge_by_name = self.env.user.employee_ids.display_name
                # print(acknowledge_by_name, "acknowledge_by_name==========")
                email_from = acknowledge_by.work_email
                mail_to = self.assign_task_id.assigned_to.work_email
                mail_cc = ','.join(self.assign_task_id.notify_to.mapped('work_email'))
                template_id.with_context(email_from=email_from,
                                         email_to=mail_to,
                                         email_cc=mail_cc,
                                         acknowledge_by=acknowledge_by_name,
                                         mail_for='Reject').sudo().send_mail(self.id,
                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")
                task_record.write({
                    'reject_comment': self.comment,
                    'stage': 'Reject'
                })
                if self.reopen_bool == True:
                    view_id = self.env.ref("task_management.sr_tasks_management_form").id
                    action = {
                        'name': 'Reject',
                        'type': 'ir.actions.act_window',
                        'res_model': 'kw_task_management',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'view_id': view_id,
                        'target': 'main',

                    }
                    return action
        elif self._context.get('current_btn') == 'pause':
            last_log = task_record.sr_task_log_ids[-1]
            last_log.write({'end_datetime': self.actual_hour,})
            task_record.write({
                'reported_pause_bool': True,
                'store_pause_time': self.actual_hour,
                'sr_task_log_ids': [(0, 0, {
                    'start_datetime': self.actual_hour,
                    'end_datetime': self.pause_time,
                    'stage_comments': self.comment,
                    'action': 'Paused',
                })]
            })

        elif self._context.get('current_btn') == 'resume':
            if task_record.sr_task_log_ids:
                last_log = task_record.sr_task_log_ids[-1]
                last_log.write({
                    'end_datetime': self.actual_hour,
                })
                task_record.write({
                    'reported_pause_bool': False,
                    'store_resume_end_time': self.actual_hour,
                    'sr_task_log_ids': [[0, 0, {
                        'start_datetime': self.actual_hour,
                        'stage_comments': self.comment,
                        'action': 'Resumed',
                        'task_sr_management_id': task_record.id,
                    }]]
                })

        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('prject_category_id')
    def project_category_data(self):
        user_data = self.env.user.employee_ids
        if not self.prject_category_id:
            domain = {}
            self.parent_task_id = False
            self.task_id = False
            task_domain = [('id', '=', 0)]
            parent_task_domain = [('id', '=', 0)]
        elif self.prject_category_id and self.prject_category_id.mapped_to == 'Project':
            tasks = self.env['project.task'].sudo().search(
                [('mapped_to', 'in', user_data.department_id.ids),
                 ('project_id', '=', self.project_id.id),
                 ('prject_category_id', '=', self.prject_category_id.id),
                 ('assigned_employee_id.user_id', '=', self.env.user.id),
                 ('task_status', 'not in', ['Completed'])])
            task_domain = [('id', 'in', tasks.ids)]
            parent_task_domain = [('id', 'in', tasks.mapped('parent_id').ids)]
            domain = {'domain': {'parent_task_id': parent_task_domain, 'task_id': task_domain}}
        return domain