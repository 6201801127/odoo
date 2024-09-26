# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.fields import Datetime
from datetime import date, datetime, timedelta
import html2text


class Task(models.Model):
    _inherit = 'project.task'

    sequence_name = fields.Char(string="Sequence", readonly=True, tracking=True)
    is_issue = fields.Boolean('Is Issue?')
    is_from_project = fields.Boolean('From Project')
    issue_priority = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], string='Priority', tracking=True)
    date = fields.Date('Date', default=fields.Datetime.now, tracking=True)
    resolved_date = fields.Date('Resolved on Date', compute='_compute_resolved_date', tracking=True)
    resolved_date1 = fields.Date('Resolved Date')
    issue_timesheet_ids = fields.One2many('account.analytic.line', 'issue_id', 'Timesheet')

    @api.model
    def message_new(self, msg, custom_values=None):
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'email_from': msg.get('from'),
            'planned_hours': 0.0,
            'partner_id': msg.get('author_id'),
        }
        defaults.update(custom_values)
        model_id = self.env['ir.model'].search([('model', '=', 'project.task')], limit=1)
        if model_id:
            server = self.env['fetchmail.server'].search([('object_id', '=', model_id.id)], limit=1)
            if server and server.fetch_key:
                if server.fetch_key in msg.get('subject'):
                    alias = self.env['mail.alias'].search([('alias_model_id', '=', 'project.task')], limit=1)
                    if alias:
                        create_context['default_project_id'] = alias.alias_parent_thread_id
                        create_context['default_is_issue'] = True
                        task = super(Task, self.with_context(create_context)).message_new(msg, custom_values=defaults)
                        email_list = task.email_split(msg)
                        partner_ids = [p.id for p in
                                       self.env['mail.thread']._mail_find_partner_from_emails(email_list, records=task,
                                                                                              force_create=False) if p]
                        task.message_subscribe(partner_ids)
                        return task

    @api.model
    def create(self, vals):
        if vals.get('sequence_name', _('New')) == _('New'):
            if self.env.context.get('default_is_issue') is True:
                vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.task') or _('New')
        res = super(Task, self).create(vals)
        if res.is_issue:
            followers_list = ''
            if res.message_follower_ids:
                for record in res.message_follower_ids:
                    followers_list += record.partner_id.email + ","
            action_id = self.env.ref('bi_project_issue_sequence.action_task_issue').id
            params = "web#id=%s&view_type=form&model=project.task&action=%s" % (res.id, action_id)
            issue_url = str(params)
            if res.partner_id:
                template = self.env.ref('bi_project_issue_sequence.issue_created_email_to_customer')
                if template:
                    values = template.generate_email(res.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = res.partner_id.email
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
            user_list, notification_ids = '', []
            if res.project_id.user_id:
                user_list += res.project_id.user_id.partner_id.email + "," or res.project_id.user_id.login + ","
            if res.project_id.program_manager_id:
                user_list += res.project_id.program_manager_id.partner_id.email + "," \
                             or res.project_id.program_manager_id.login + ","
            if res.user_id.id != self.env.user.id:
                user_list += res.user_id.partner_id.email or res.user_id.login
            if res.user_id:
                template = self.env.ref('bi_project_issue_sequence.issue_created_email_assigned_to')
                if template:
                    values = template.generate_email(res.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = user_list
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    # values['email_cc'] = followers_list
                    values['body_html'] = values['body_html'].replace('_issue_url', issue_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        return res

    def get_text_sanitised(self, text):
        ''' Remove HTML tags from Text '''
        sanitized_text = ''
        h = html2text.HTML2Text()
        # Ignore converting links from HTML
        h.ignore_links = True
        if text:
            sanitized_text = h.handle(text)
            sanitized_text = sanitized_text.replace('\n', '   ')[:32765]
        return sanitized_text

    def write(self, vals):
        rec = super(Task, self).write(vals)
        users_obj = self.env['res.users']
        if 'stage_id' in vals:
            if self.is_issue is True and self.stage_id:
                followers_list = ''
                if self.message_follower_ids:
                    for record in self.message_follower_ids:
                        user = users_obj.search([('partner_id', '=', record.partner_id.id)], limit=1)
                        if user:
                            followers_list += user.login + ","
                action_id = self.env.ref('bi_project_issue_sequence.action_task_issue').id
                params = "web#id=%s&view_type=form&model=project.task&action=%s" % (self.id, action_id)
                issue_url = str(params)
                if self.partner_id:
                    template = self.env.ref('bi_project_issue_sequence.issue_updated_email_to_customer')
                    if template:
                        values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
                        values['email_to'] = self.partner_id.email
                        values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                        values['body_html'] = values['body_html']
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                user_list, notification_ids = '', []
                if self.project_id.user_id:
                    user_list += self.project_id.user_id.partner_id.email + "," or self.project_id.user_id.login + ","
                    notification_ids.append((0, 0, {
                        'res_partner_id': self.project_id.user_id.partner_id.id,
                        'notification_type': 'inbox'}))
                if self.project_id.program_manager_id:
                    user_list += self.project_id.program_manager_id.partner_id.email + "," \
                                 or self.project_id.program_manager_id.login + ","
                    notification_ids.append((0, 0, {
                        'res_partner_id': self.project_id.program_manager_id.partner_id.id,
                        'notification_type': 'inbox'}))
                if self.user_id.id != self.env.user.id:
                    user_list += self.user_id.partner_id.email or self.user_id.login
                if self.user_id:
                    template = self.env.ref('bi_project_issue_sequence.issue_updated_email_assigned_to')
                    if template:
                        values = template.generate_email(self.id,
                                                         ['subject', 'email_to', 'email_from', 'body_html'])
                        values['email_to'] = user_list
                        values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                        # values['email_cc'] = followers_list
                        values['body_html'] = values['body_html'].replace('_issue_url', issue_url)
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                    if self.stage_id.is_closed is True:
                        self.message_post(body="Issue has been Done.",
                                          message_type='notification', author_id=self.env.user.partner_id.id,
                                          notification_ids=notification_ids, notify_by_email=False)
        return rec

    @api.depends('stage_id')
    def _compute_resolved_date(self):
        for record in self:
            if record.stage_id.is_closed is True and record.is_issue is True:
                record.resolved_date = Datetime.now()
                record.resolved_date1 = Datetime.now()
            elif record.resolved_date1 and record.is_issue is True:
                record.resolved_date = record.resolved_date1
            else:
                record.resolved_date = False
                record.resolved_date1 = False

    def issue_activity_reminder(self):
        project_task = self.env['project.task'].search([('is_issue', '=', True)])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in project_task:
            activity = mail_activity_obj.search(
                [('res_id', '=', record.id), ('res_model', '=', 'project.task'),
                 ('activity_type_id', '=',
                  self.env.ref('gts_project_stages.issue_assigned_activity').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        template = self.env.ref('bi_project_issue_sequence.issue_activity_email_reminder')
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('project_risk_management_app.action_risk_incident').id
                        params = str(
                            base_url) + "/web#id=%s&view_type=form&model=project.task&action=%s" % (
                            record.id, action_id)
                        task_url = str(params)
                        if template:
                            values = template.generate_email(record.id,
                                                             ['subject', 'email_to', 'email_from',
                                                              'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.project_id.outgoing_email
                            values['body_html'] = values['body_html'].replace('_task_url', task_url)
                            mail = self.env['mail.mail'].create(values)
                            try:
                                mail.send()
                            except Exception:
                                pass
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        record.message_post(
                            body="Reminder to Close Activity for Issue (" + str(record.name) + ")",
                            message_type='notification', subtype_xmlid='mail.mt_comment',
                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                            notify_by_email=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    issue_id = fields.Many2one('project.task', 'Issue')
