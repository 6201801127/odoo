from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, AccessError, MissingError, AccessDenied
from datetime import date, datetime, timedelta


class Project(models.Model):
    _name = 'project.project'
    _description = "Project"
    _inherit = ['project.project', 'mail.activity.mixin']

    @api.depends('stakeholder_ids', 'stakeholder_ids.partner_id', 'stakeholder_ids.status')
    def _get_program_manager_domain(self):
        user_obj = self.env['res.users'].search([])
        for record in self:
            partner_list = []
            for lines in record.stakeholder_ids:
                if lines.status is True:
                    user = user_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                    if user and user.has_group('gts_project_stages.group_program_manager'):
                        partner_list.append(user.id)
            record.program_manager_ids = [(6, 0, partner_list)]

    @api.depends('stakeholder_ids', 'stakeholder_ids.partner_id', 'stakeholder_ids.status')
    def _get_project_manager_domain(self):
        user_obj = self.env['res.users'].search([])
        for record in self:
            partner_list = []
            for lines in record.stakeholder_ids:
                if lines.status is True:
                    partner_list.append(lines.partner_id.id)
            users = user_obj.search([('partner_id', 'in', partner_list)])
            record.user_ids = [(6, 0, [user.id for user in users])]

    stage_id = fields.Many2one('project.stage', string='Stage', index=True, tracking=True, readonly=True,
                               copy=False, compute='_compute_stage_id', group_expand='_read_group_stage_ids',
                               ondelete='restrict', store=True,
                               domain="['|', ('user_id', '=', False), ('user_id', '=', user_id)]")
    start_date = fields.Date(string='Start Date', index=True, copy=False, tracking=True)
    end_date = fields.Date(string='End Date', index=True, copy=False, tracking=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city_id = fields.Many2one('res.state.city', 'City')
    sub_city_id = fields.Many2one('res.state.city', 'Sub City')
    woreda_id = fields.Many2one('res.location', 'Woreda')
    kabele_id = fields.Many2one('res.location', 'Kabele')
    state_id = fields.Many2one('res.country.state', 'Region')
    zip = fields.Char('Zip')
    country_id = fields.Many2one('res.country', 'Country', default=lambda self: self._get_default_country())
    program_manager_id = fields.Many2one('res.users', 'Program Manager', tracking=True)
    user_ids = fields.Many2many('res.users', string='Project Manager', compute='_get_project_manager_domain')
    program_manager_ids = fields.Many2many('res.users', string='Program Managers', compute='_get_program_manager_domain')
    privacy_visibility = fields.Selection([
        ('followers', 'Invited internal users'),
        ('employees', 'All internal users'),
        ('portal', 'Invited portal users and all internal users'),
    ],
        string='Visibility', required=True,
        default='followers',
        help="Defines the visibility of the tasks of the project:\n"
             "- Invited internal users: employees may only see the followed project and tasks.\n"
             "- All internal users: employees may see all project and tasks.\n"
             "- Invited portal and all internal users: employees may see everything."
             "   Portal users may see project and tasks followed by\n"
             "   them or by someone of their company.")
    allowed_internal_user_ids = fields.Many2many('res.users', 'project_allowed_internal_users_rel',
                                                 string="Allowed Internal Users", default=False,
                                                 domain=[('share', '=', False)])
    outgoing_email = fields.Char('Outgoing Email')


    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'ET')], limit=1)
        return country.id

    @api.depends('user_id')
    def _compute_stage_id(self):
        for project in self:
            if not project.stage_id:
                project.stage_id = project._stage_find(domain=[('fold', '=', False)]).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        user_id = self._context.get('default_user_id')
        if user_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('user_id', '=', False), ('user_id', '=', user_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('user_id', '=', False)]
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _stage_find(self, user_id=False, domain=None, order=''):
        user_ids = set()
        if user_id:
            user_ids.add(user_id)
        for project in self:
            if project.user_id:
                user_ids.add(project.user_id.id)
        # generate the domain
        if user_ids:
            search_domain = ['|', ('user_id', '=', False), ('user_id', 'in', list(user_ids))]
        else:
            search_domain = [('user_id', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.stage'].search(search_domain, order=order, limit=1)

    @api.model
    def create(self, vals):
        rec = super(Project, self).create(vals)
        if self.env.user.has_group('project.group_project_manager_new'):
            if vals['user_id'] != self.env.uid:
                raise ValidationError(_('You cannot create project for another user'))
        return rec

    def write(self, vals):
        rec = super(Project, self).write(vals)
        if self.env.user.has_group('project.group_project_manager_new'):
            if self.user_id.id != self.env.uid:
                raise ValidationError(_('You cannot assign project for another user'))
        return rec

    @api.onchange('start_date', 'end_date')
    def _onchange_start_end_date(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('End date should be greater than the start date.'))

    @api.onchange('partner_id', 'partner_id.street', 'partner_id.street2', 'partner_id.woreda_id',
                  'partner_id.kabele_id', 'partner_id.sub_city_id', 'partner_id.city_id', 'partner_id.state_id',
                  'partner_id.zip', 'partner_id.country_id')
    def onchange_partner_id(self):
        if self.partner_id and not self.partner_id.parent_id:
            self.street = self.partner_id.street
            self.street2 = self.partner_id.street2
            self.woreda_id = self.partner_id.woreda_id.id
            self.kabele_id = self.partner_id.kabele_id.id
            self.sub_city_id = self.partner_id.sub_city_id.id
            self.city_id = self.partner_id.city_id.id
            self.state_id = self.partner_id.state_id.id
            self.zip = self.partner_id.zip
            self.country_id = self.partner_id.country_id.id
        if self.partner_id and self.partner_id.parent_id:
            self.street = self.partner_id.parent_id.street
            self.street2 = self.partner_id.parent_id.street2
            self.woreda_id = self.partner_id.parent_id.woreda_id.id
            self.kabele_id = self.partner_id.parent_id.kabele_id.id
            self.sub_city_id = self.partner_id.parent_id.sub_city_id.id
            self.city_id = self.partner_id.parent_id.city_id.id
            self.state_id = self.partner_id.parent_id.state_id.id
            self.zip = self.partner_id.parent_id.zip
            self.country_id = self.partner_id.parent_id.country_id.id

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """
        Subscribe to all existing active tasks when subscribing to a project
        And add the portal user subscribed to allowed portal users
        """
        res = super(Project, self).message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids)
        project_subtypes = self.env['mail.message.subtype'].browse(subtype_ids) if subtype_ids else None
        task_subtypes = (project_subtypes.mapped('parent_id') | project_subtypes.filtered(lambda sub: sub.internal or sub.default)).ids if project_subtypes else None
        if not subtype_ids or task_subtypes:
            self.mapped('tasks').message_subscribe(
                partner_ids=None, channel_ids=None, subtype_ids=task_subtypes)
        if partner_ids:
            all_users = self.env['res.partner'].browse(partner_ids).user_ids
            portal_users = all_users.filtered('share')
            internal_users = all_users - portal_users
            self.allowed_portal_user_ids |= portal_users
            self.allowed_internal_user_ids |= internal_users
        return res

    def message_unsubscribe(self, partner_ids=None, channel_ids=None):
        """ Unsubscribe from all tasks when unsubscribing from a project """
        self.mapped('tasks').message_unsubscribe(partner_ids=None, channel_ids=None)
        return super(Project, self).message_unsubscribe(partner_ids=partner_ids, channel_ids=channel_ids)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_stakeholder_ids = fields.Many2many('res.users', 'Stakeholders', compute='_get_project_stakeholders')
    user_id = fields.Many2one('res.users', string='Assigned to', default=False, index=True, tracking=True)
    allowed_user_ids = fields.Many2many('res.users', string="Visible to",
                                        groups='project.group_project_manager,gts_project_stages.group_project_manager_new',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    activity_reminder_days = fields.Integer('Activity Reminder')

    @api.depends('project_id', 'project_id.stakeholder_ids', 'project_id.stakeholder_ids.status',
                 'project_id.stakeholder_ids.partner_id')
    def _get_project_stakeholders(self):
        users_obj = self.env['res.users']
        for record in self:
            users_list, p_user = [], []
            if record.project_id and record.project_id.stakeholder_ids:
                for lines in record.project_id.stakeholder_ids:
                    if lines.status is True:
                        user = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        if user:
                            users_list.append(user.id)
                            if user.id == self.env.user.id:
                                p_user.append(user.id)
            if self.env.user.has_group('gts_project_stages.group_project_manager_new'):
                record.project_stakeholder_ids = [(6, 0, [rec for rec in users_list])]
            else:
                record.project_stakeholder_ids = [(6, 0, p_user)]

    @api.model_create_multi
    def create(self, vals_list):
        rec = super(ProjectTask, self).create(vals_list)
        if rec.message_follower_ids:
            for record in rec.message_follower_ids:
                rec.message_unsubscribe(partner_ids=[record.partner_id.id])
        partner_ids = []
        if rec.user_id:
            partner_ids.append(self.env.user.partner_id.id)
        if rec.project_id:
            if rec.project_id.program_manager_id:
                partner_ids.append(rec.project_id.program_manager_id.partner_id.id)
            if rec.project_id.user_id:
                partner_ids.append(rec.project_id.user_id.partner_id.id)
        msg_body = ''
        if rec.risk_incident is True:
            msg_body = "Invited you to follow the Risk Incident"
        elif rec.is_issue is True:
            msg_body = "Invited you to follow the Issue"
        elif rec.risk_incident is False and rec.is_issue is False:
            msg_body = "Invited you to follow the Task"
        if partner_ids:
            new_list = list(set(partner_ids))
            rec.message_subscribe(partner_ids=new_list)
            rec.message_post(partner_ids=new_list, body=msg_body)
        if rec.user_id:
            rec.message_post(partner_ids=[rec.user_id.partner_id.id],
                             body="Dear " + str(rec.user_id.name) + ", " + str(rec.name) + ", "
                                  + str(rec.project_id.name) + " has been assigned to you.",
                             message_type='email', email_from=rec.project_id.outgoing_email)
            if rec.risk_incident is True:
                msg = 'Risk Incident assigned'
                activity_id = self.env.ref('gts_project_stages.incident_assigned_activity').id
            elif rec.is_issue is True:
                msg = 'Issue is Assigned'
                activity_id = self.env.ref('gts_project_stages.issue_assigned_activity').id
            else:
                msg = 'Task Assigned'
                activity_id = self.env.ref('gts_project_stages.task_assigned_activity').id
            activity_dict = {
                'res_model': 'project.task',
                'res_model_id': self.env.ref('project.model_project_task').id,
                'res_id': rec.id,
                'activity_type_id': activity_id,
                'date_deadline': rec.date_deadline,
                'summary': msg,
                'user_id': rec.user_id.id
            }
            self.env['mail.activity'].create(activity_dict)
        rec.is_from_project = True
        return rec

    def write(self, vals):
        rec = super(ProjectTask, self).write(vals)
        if 'user_id' in vals:
            self.message_post(partner_ids=[self.user_id.partner_id.id],
                              body="Dear " + str(self.user_id.name) + ", " + str(self.name) + ", "
                                   + str(self.project_id.name) + " has been assigned to you.",
                              message_type='email', email_from=self.project_id.outgoing_email)
            if self.risk_incident is True:
                msg = 'Risk Incident assigned'
                activity_id = self.env.ref('gts_project_stages.incident_assigned_activity').id
            elif self.is_issue is True:
                msg = 'Issue is Assigned'
                activity_id = self.env.ref('gts_project_stages.issue_assigned_activity').id
            else:
                msg = 'Task Assigned'
                activity_id = self.env.ref('gts_project_stages.task_assigned_activity').id
            activity_dict = {
                'res_model': 'project.task',
                'res_model_id': self.env.ref('project.model_project_task').id,
                'res_id': self.id,
                'activity_type_id': activity_id,
                'date_deadline': self.date_deadline,
                'summary': msg,
                'user_id': vals.get('user_id')
            }
            self.env['mail.activity'].create(activity_dict)
        return rec

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """
        Add the users subscribed to allowed portal users
        """
        res = super(ProjectTask, self).message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids)
        if partner_ids:
            new_allowed_users = self.env['res.partner'].browse(partner_ids).user_ids.filtered('share')
            tasks = self.filtered(lambda task: task.project_id.privacy_visibility == 'portal')
            tasks.sudo().write({'allowed_user_ids': [(4, user.id) for user in new_allowed_users]})
        return res

    @api.constrains('date_deadline')
    def _check_date_deadline(self):
        for record in self:
            if record.date_deadline:
                if record.date_deadline < datetime.now().date():
                    raise UserError(_("Deadline cannot be less then today's date!"))

    # @api.model
    # def create(self, vals):
    #     rec = super(ProjectTask, self).create(vals)
    #     if self.env.user.has_group('project.group_project_user'):
    #         if vals['user_id'] != self.env.uid:
    #             raise ValidationError(_('You cannot assign task to another user'))
    #     if vals['planned_hours'] == 0.0:
    #         raise ValidationError(_('Planned hours should be greater then Zero.'))
    #     return rec
    #
    # def write(self, vals):
    #     rec = super(ProjectTask, self).write(vals)
    #     if self.env.user.has_group('project.group_project_user'):
    #         if self.user_id.id != self.env.uid:
    #             raise ValidationError(_('You cannot assign task to another user'))
    #     if self.planned_hours == 0.0:
    #         raise ValidationError(_('Planned hours should be greater then Zero.'))
    #     return rec

    @api.onchange('date_deadline')
    def onchange_date_deadline(self):
        if self.date_deadline and self.project_id:
            if self.project_id.start_date and self.project_id.end_date:
                if self.date_deadline < self.project_id.start_date or self.date_deadline > self.project_id.end_date:
                    raise ValidationError(_('Task Deadline should be between %s to %s.' % (
                    self.project_id.start_date.strftime("%d-%b-%Y"), self.project_id.end_date.strftime("%d-%b-%Y"))))

    def task_activity_reminder(self):
        project_task = self.env['project.task'].search([('is_issue', '=', False), ('risk_incident', '=', False)])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in project_task:
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'project.task'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('gts_project_stages.task_assigned_activity').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        template = self.env.ref('gts_project_stages.task_activity_email_reminder')
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('project.action_view_all_task').id
                        params = str(base_url) + "/web#id=%s&view_type=form&model=project.task&action=%s" % (
                            record.id, action_id)
                        task_url = str(params)
                        if template:
                            values = template.generate_email(record.id,['subject', 'email_to', 'email_from',
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
                        record.message_post(body="Reminder to Close Activity for Task ("+str(record.name)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    estimated_hours = fields.Float("Estimated Hour", digits=(16, 2), group_operator="sum")

    def write(self, vals):
        if self.env.context.get('params'):
            if self.env.context.get('params').get('model') == 'project.task':
                prev_date = self.date
                prev_employee = self.employee_id.name
                prev_name = self.name or ''
                prev_estimated_hours = self.estimated_hours
                prev_actual_hours = self.unit_amount
                rec = super(AccountAnalyticLine, self).write(vals)
                message_body = """<b>Timesheet</b><br/>"""
                if prev_date == self.date:
                    message_body += """• Date: {prev_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date} <br/>""".format(
                        prev_date=prev_date, date=self.date
                    )
                else:
                    message_body += """<span style='color:red;'>• Date: {prev_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date} </span><br/>""".format(
                        prev_date=prev_date, date=self.date
                    )
                if prev_employee == self.employee_id.name:
                    message_body += """• Employee: {prev_employee} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {employee}<br/>""".format(
                        prev_employee=prev_employee, employee=self.employee_id.name
                    )
                else:
                    message_body += """<span style='color:red;'>• Employee: {prev_employee} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {employee}</span><br/>""".format(
                        prev_employee=prev_employee, employee=self.employee_id.name
                    )
                if prev_name == self.name or '':
                    message_body += """• Description: {prev_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}<br/>""".format(
                        prev_name=prev_name, description=self.name or ''
                    )
                else:
                    message_body += """<span style='color:red;'>• Description: {prev_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}</span><br/>""".format(
                        prev_name=prev_name, description=self.name or ''
                    )
                if prev_estimated_hours == self.estimated_hours:
                    message_body += """• Estimated Hours: {prev_estimated_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {estimated_hours}<br/>""".format(
                        prev_estimated_hours=prev_estimated_hours, estimated_hours=self.estimated_hours
                    )
                else:
                    message_body += """<span style='color:red;'>• Estimated Hours: {prev_estimated_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {estimated_hours}</span><br/>""".format(
                        prev_estimated_hours=prev_estimated_hours, estimated_hours=self.estimated_hours
                    )
                if prev_actual_hours == self.unit_amount:
                    message_body += """• Actual Hours: {prev_actual_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {actual_amount}""".format(
                        prev_actual_hours=prev_actual_hours, actual_amount=self.unit_amount
                    )
                else:
                    message_body += """<span style='color:red;'>• Actual Hours: {prev_actual_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {actual_amount}</span>""".format(
                        prev_actual_hours=prev_actual_hours, actual_amount=self.unit_amount
                    )
                # message_body = """<b>Timesheet</b><br/>
                #                 • Date: {prev_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date} <br/>
                #                 • Employee: {prev_employee} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {employee}<br/>
                #                 • Description: {prev_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}<br/>
                #                 • Estimated Hours: {prev_estimated_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {estimated_hours}<br/>
                #                 • Actual Hours: {prev_actual_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {actual_amount}"""\
                #     .format(prev_date=prev_date, date=self.date,
                #             prev_employee=prev_employee, employee=self.employee_id.name,
                #             prev_name=prev_name, description=self.name or '',
                #             prev_estimated_hours=prev_estimated_hours, estimated_hours=self.estimated_hours,
                #             prev_actual_hours=prev_actual_hours, actual_amount=self.unit_amount)
                if self.issue_id:
                    self.issue_id.message_post(body=message_body)
                if self.task_id:
                    self.task_id.message_post(body=message_body)
                if self.incident_id:
                    self.incident_id.message_post(body=message_body)
                return rec
            else:
                return super(AccountAnalyticLine, self).write(vals)
        else:
            return super(AccountAnalyticLine, self).write(vals)
