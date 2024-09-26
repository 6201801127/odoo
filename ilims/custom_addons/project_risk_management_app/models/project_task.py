from odoo import fields, models, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class Task(models.Model):
    _inherit = 'project.task'

    # compute for risk incident smart button
    def _risk_incident_count(self):
        task_obj = self.env['project.task']
        for rec in self:
            rec.risk_incident_count = task_obj.search_count(
                [('project_id', 'in', rec.project_id.ids), ('incident_type', '=', 'task'),
                 ('parent_id', '=', rec.id)])

    risk_incident_count = fields.Integer(compute='_risk_incident_count', track_visibility='always')
    incident_type = fields.Selection([('project', 'Project'), ('task', 'Task')], size=1, readonly=True, string="Type",
                                     track_visibility='always')

    risk_incident = fields.Boolean('Task Incident?', readonly=1)
    risk_line = fields.Char('Risk Line', track_visibility='always')
    # original_task = fields.Many2one('project.task', string='Original Task', track_visibility='always')
    incident_photo = fields.Binary("Incident Photo", track_visibility='always')
    risk_lines_ids = fields.One2many('task.risk.line', 'task_id', string="Risk Register", track_visibility='always')
    project_id = fields.Many2one('project.project', 'Project', required=True, track_visibility='always')
    is_from_project = fields.Boolean('From Project?')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Project Name', readonly=True, copy=False,
                                          check_company=True,
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                          help="The analytic account related to a sales order.")
    incident_timesheet_ids = fields.One2many('account.analytic.line', 'incident_id', 'Timesheet')


    # @api.onchange('stage_id')
    # def _onchange_stage_id(self):
    #     print('=============]]]]]]]]]]]', 'changed stage')
    #     users_obj = self.env['res.users']
    #     notification_ids = []
    #     if self.user_id:
    #         notification_ids.append((0, 0, {
    #                 'res_partner_id': self.user_id.partner_id.id,
    #                 'notification_type': 'inbox'
    #             }))
    #     if self.project_id and self.project_id.stakeholder_ids:
    #         for lines in self.project_id.stakeholder_ids:
    #             user = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
    #             notification_ids.append((0, 0, {
    #                     'res_partner_id': user.partner_id.id,
    #                     'notification_type': 'inbox'}))
    #     message = 'Project Task stage has benn changed By ' + str(self.env.user.name)
    #     print(']]]]]]]]]]]]]]]]]]]',notification_ids)
    #
    #         # Notification to the user for closer of chnage request
    #
    #     #channel_odoo_bot_users = '%s' % (self.user_id.name)
    #     channel_obj = self.env['mail.channel']
    #     channel_id = channel_obj.search([('name', '=', self.env.user.name)])
    #     for notification_id in notification_ids:
    #         channel_id.message_notify(body=message, message_type='notification',subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,notification_ids=notification_id)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            record.analytic_account_id = False
            if record.project_id:
                record.analytic_account_id = record.project_id.analytic_account_id

    # smart button in project
    def open_risk_incident_task(self):
        xml_id = 'project_risk_management_app.view_risk_incident_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'project_risk_management_app.view_risk_incident_menu'
        # xml_id = 't20_core.view_analytic_code_budget_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Risk Incident'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'project.task',
            'domain': [('project_id', 'in', self.project_id.ids), ('incident_type', '=', 'task'),
                       ('parent_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.project_id.id, 'default_parent_id': self.id,
                        'default_incident_type': 'task'}
        }

    @api.model
    def create(self, vals):
        res = super(Task, self).create(vals)
        if res.risk_incident:
            user_list, notification_ids = '', []
            if res.project_id.user_id:
                user_list += res.project_id.user_id.partner_id.email + "," or res.project_id.user_id.login + ","
            if res.project_id.program_manager_id:
                user_list += res.project_id.program_manager_id.partner_id.email + "," \
                             or res.project_id.program_manager_id.login + ","
            if res.user_id.id != self.env.user.id:
                user_list += res.user_id.partner_id.email or res.user_id.login
            if res.user_id:
                action_id = self.env.ref('project_risk_management_app.action_risk_incident').id
                params = "web#id=%s&view_type=form&model=project.task&action=%s" % (res.id, action_id)
                incident_url = str(params)
                template = self.env.ref('project_risk_management_app.risk_incident_created_email')
                if template:
                    values = template.generate_email(res.id,
                                                     ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = user_list
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html'].replace('_incident_url', incident_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        return res

    def write(self, vals):
        rec = super(Task, self).write(vals)
        if 'stage_id' in vals:
            if self.risk_incident is True and self.stage_id:
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
                    action_id = self.env.ref('project_risk_management_app.action_risk_incident').id
                    params = "web#id=%s&view_type=form&model=project.task&action=%s" % (self.id, action_id)
                    incident_url = str(params)
                    template = self.env.ref('project_risk_management_app.risk_incident_updated_email')
                    if template:
                        values = template.generate_email(self.id,
                                                         ['subject', 'email_to', 'email_from', 'body_html'])
                        values['email_to'] = user_list
                        values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                        # values['email_cc'] = followers_list
                        values['body_html'] = values['body_html'].replace('_incident_url', incident_url)
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
                    if self.stage_id.is_closed is True:
                        self.message_post(body="Risk Incident has been Done.",
                                          message_type='notification', author_id=self.env.user.partner_id.id,
                                          notification_ids=notification_ids, notify_by_email=False)
        return rec

    # reminder's before deadline
    def create_activity_as_reminder(self):
        task_obj = self.env['project.task']
        today_date = datetime.now().date()
        days_7before = today_date + timedelta(weeks=1)
        day_1before = today_date + timedelta(days=1)
        task_7days = task_obj.search(
            [('date_deadline', '=', days_7before.strftime('%Y-%m-%d')), ('risk_incident', '=', True)])
        task_1day = task_obj.search(
            [('date_deadline', '=', day_1before.strftime('%Y-%m-%d')), ('risk_incident', '=', True)])
        task_today = task_obj.search(
            [('date_deadline', '=', today_date.strftime('%Y-%m-%d')), ('risk_incident', '=', True)])
        if task_7days:
            for task in task_7days:
                activity_dict = {
                    'res_model': 'project.task',
                    'res_model_id': self.env.ref('project.model_project_task').id,
                    'res_id': task.id,
                    'activity_type_id': self.env.ref('project_risk_management_app.complete_task_before_deadline').id,
                    'date_deadline': task.date_deadline,
                    'summary': 'Reminder to Complete before Deadline',
                    'user_id': task.user_id.id
                }
                self.env['mail.activity'].create(activity_dict)
        if task_1day:
            for task in task_1day:
                activity_dict = {
                    'res_model': 'project.task',
                    'res_model_id': self.env.ref('project.model_project_task').id,
                    'res_id': task.id,
                    'activity_type_id': self.env.ref('project_risk_management_app.complete_task_before_deadline').id,
                    'date_deadline': task.date_deadline,
                    'summary': 'Reminder to Complete before Deadline',
                    'user_id': task.user_id.id
                }
                self.env['mail.activity'].create(activity_dict)
        if task_today:
            for task in task_today:
                activity_dict = {
                    'res_model': 'project.task',
                    'res_model_id': self.env.ref('project.model_project_task').id,
                    'res_id': task.id,
                    'activity_type_id': self.env.ref('project_risk_management_app.complete_task_before_deadline').id,
                    'date_deadline': task.date_deadline,
                    'summary': 'Reminder to Complete before Deadline',
                    'user_id': task.user_id.id
                }
                self.env['mail.activity'].create(activity_dict)

    def risk_activity_reminder(self):
        project_task = self.env['project.task'].search([('risk_incident', '=', True)])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in project_task:
            activity = mail_activity_obj.search(
                [('res_id', '=', record.id), ('res_model', '=', 'project.task'),
                 ('activity_type_id', '=',
                  self.env.ref('gts_project_stages.incident_assigned_activity').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        template = self.env.ref('project_risk_management_app.risk_activity_email_reminder')
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('project.action_view_all_task').id
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
                            body="Reminder to Close Activity for Risk Incident (" + str(record.name) + ")",
                            message_type='notification', subtype_xmlid='mail.mt_comment',
                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                            notify_by_email=False)

    # @api.depends('timesheet_ids.unit_amount', 'incident_timesheet_ids.unit_amount')
    # def _compute_effective_hours(self):
    #     for task in self:
    #         if task.risk_incident is True:
    #             task.effective_hours = round(sum(task.incident_timesheet_ids.mapped('unit_amount')), 2)
    #         elif task.is_issue is False and task.risk_incident is False:
    #             task.effective_hours = round(sum(task.timesheet_ids.mapped('unit_amount')), 2)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    incident_id = fields.Many2one('project.task', 'Risk Incident')
