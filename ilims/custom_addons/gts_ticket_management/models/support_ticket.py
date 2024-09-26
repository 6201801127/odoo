# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from datetime import timedelta
from random import randint
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.exceptions import AccessError
from bs4 import BeautifulSoup as bs

TICKET_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]


class SupportTicketTag(models.Model):
    _name = 'support.ticket.tag'
    _description = 'Support Ticket Tagss'
    _order = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class SupportTicketType(models.Model):
    _name = 'support.ticket.type'
    _description = 'Support Ticket Type'
    _order = 'sequence'

    name = fields.Char('Type', required=True, translate=True)
    sequence = fields.Integer(default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists !"),
    ]


class SupportSLAStatus(models.Model):
    _name = 'support.sla.status'
    _description = "Support Ticket SLA Status"
    _table = 'support_sla_status'
    _order = 'deadline ASC, sla_stage_id'
    _rec_name = 'sla_id'

    ticket_id = fields.Many2one('support.ticket', string='Ticket', required=True, ondelete='cascade', index=True)
    sla_id = fields.Many2one('support.sla', required=True, ondelete='cascade')
    sla_stage_id = fields.Many2one('support.ticket.stage', related='sla_id.stage_id', store=True)  # need to be stored for the search in `_sla_reach`
    target_type = fields.Selection(related='sla_id.target_type', store=True)
    deadline = fields.Datetime("Deadline", compute='_compute_deadline', compute_sudo=True, store=True)
    reached_datetime = fields.Datetime("Reached Date", help="Datetime at which the SLA stage was reached for the first time")
    status = fields.Selection([('failed', 'Failed'), ('reached', 'Reached'), ('ongoing', 'Ongoing')], string="Status", compute='_compute_status', compute_sudo=True, search='_search_status')
    color = fields.Integer("Color Index", compute='_compute_color')
    exceeded_days = fields.Float("Excedeed Working Days", compute='_compute_exceeded_days', compute_sudo=True, store=True, help="Working days exceeded for reached SLAs compared with deadline. Positive number means the SLA was eached after the deadline.")

    @api.depends('ticket_id.create_date', 'sla_id', 'ticket_id.stage_id')
    def _compute_deadline(self):
        for status in self:
            if (status.deadline and status.reached_datetime) or (status.deadline and status.target_type == 'stage' and not status.sla_id.exclude_stage_ids) or (status.status == 'failed'):
                continue
            if status.target_type == 'assigning' and status.sla_stage_id == status.ticket_id.stage_id:
                deadline = fields.Datetime.now()
            elif status.target_type == 'assigning' and status.sla_stage_id:
                status.deadline = False
                continue
            else:
                deadline = status.ticket_id.create_date
            working_calendar = status.ticket_id.team_id.resource_calendar_id
            if not working_calendar:
                status.deadline = deadline
                continue

            if status.target_type == 'stage' and status.sla_id.exclude_stage_ids:
                if status.ticket_id.stage_id in status.sla_id.exclude_stage_ids:
                    status.deadline = False
                    continue

            time_days = status.sla_id.time_days
            if time_days and (status.sla_id.target_type == 'stage' or status.sla_id.target_type == 'assigning' and not status.sla_id.stage_id):
                deadline = working_calendar.plan_days(time_days + 1, deadline, compute_leaves=True)
                create_dt = status.ticket_id.create_date
                deadline = deadline.replace(hour=create_dt.hour, minute=create_dt.minute, second=create_dt.second, microsecond=create_dt.microsecond)
            elif time_days and status.target_type == 'assigning' and status.sla_stage_id == status.ticket_id.stage_id:
                deadline = working_calendar.plan_days(time_days + 1, deadline, compute_leaves=True)
                reached_stage_dt = fields.Datetime.now()
                deadline = deadline.replace(hour=reached_stage_dt.hour, minute=reached_stage_dt.minute, second=reached_stage_dt.second, microsecond=reached_stage_dt.microsecond)

            sla_hours = status.sla_id.time_hours + (status.sla_id.time_minutes / 60)

            if status.target_type == 'stage' and status.sla_id.exclude_stage_ids:
                sla_hours += status._get_freezed_hours(working_calendar)
                deadline_for_working_cal = working_calendar.plan_hours(0, deadline)
                if deadline_for_working_cal and deadline.day < deadline_for_working_cal.day:
                    deadline = deadline.replace(hour=0, minute=0, second=0, microsecond=0)
            status.deadline = working_calendar.plan_hours(sla_hours, deadline, compute_leaves=True)

    @api.depends('deadline', 'reached_datetime')
    def _compute_status(self):
        for status in self:
            if status.reached_datetime and status.deadline:
                status.status = 'reached' if status.reached_datetime < status.deadline else 'failed'
            else:
                status.status = 'ongoing' if not status.deadline or status.deadline > fields.Datetime.now() else 'failed'

    @api.model
    def _search_status(self, operator, value):
        datetime_now = fields.Datetime.now()
        positive_domain = {
            'failed': ['|', '&', ('reached_datetime', '=', True), ('deadline', '<=', 'reached_datetime'), '&', ('reached_datetime', '=', False), ('deadline', '<=', fields.Datetime.to_string(datetime_now))],
            'reached': ['&', ('reached_datetime', '=', True), ('reached_datetime', '<', 'deadline')],
            'ongoing': ['&', ('reached_datetime', '=', False), ('deadline', '<=', fields.Datetime.to_string(datetime_now))]
        }
        if not isinstance(value, list):
            value = [value]
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domains_to_keep = [dom for key, dom in positive_domain if key not in value]
            return expression.OR(domains_to_keep)
        else:
            return expression.OR(positive_domain[value_item] for value_item in value)

    @api.depends('status')
    def _compute_color(self):
        for status in self:
            if status.status == 'failed':
                status.color = 1
            elif status.status == 'reached':
                status.color = 10
            else:
                status.color = 0

    @api.depends('deadline', 'reached_datetime')
    def _compute_exceeded_days(self):
        for status in self:
            if status.reached_datetime and status.deadline and status.ticket_id.team_id.resource_calendar_id:
                if status.reached_datetime <= status.deadline:
                    start_dt = status.reached_datetime
                    end_dt = status.deadline
                    factor = -1
                else:
                    start_dt = status.deadline
                    end_dt = status.reached_datetime
                    factor = 1
                duration_data = status.ticket_id.team_id.resource_calendar_id.get_work_duration_data(start_dt, end_dt, compute_leaves=True)
                status.exceeded_days = duration_data['days'] * factor
            else:
                status.exceeded_days = False

    def _get_freezed_hours(self, working_calendar):
        self.ensure_one()
        hours_freezed = 0

        field_stage = self.env['ir.model.fields']._get(self.ticket_id._name, "stage_id")
        freeze_stages = self.sla_id.exclude_stage_ids.ids
        tracking_lines = self.ticket_id.message_ids.tracking_value_ids.filtered(lambda tv: tv.field == field_stage).sorted(key="create_date")

        if not tracking_lines:
            return 0

        old_time = self.ticket_id.create_date
        for tracking_line in tracking_lines:
            if tracking_line.old_value_integer in freeze_stages:
                hours_freezed += working_calendar.get_work_hours_count(old_time, tracking_line.create_date)
            old_time = tracking_line.create_date
        if tracking_lines[-1].new_value_integer in freeze_stages:
            hours_freezed += working_calendar.get_work_hours_count(old_time, fields.Datetime.now())
        return hours_freezed


class SupportTicket(models.Model):
    _name = 'support.ticket'
    _description = 'Support  Ticket'
    _order = 'priority desc, id desc'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'utm.mixin', 'rating.mixin', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields):
        result = super(SupportTicket, self).default_get(fields)
        if result.get('team_id') and fields:
            team = self.env['support.team'].browse(result['team_id'])
            if 'user_id' in fields and 'user_id' not in result:  # if no user given, deduce it from the team
                result['user_id'] = team._determine_user_to_assign()[team.id].id
            if 'stage_id' in fields and 'stage_id' not in result:  # if no stage given, deduce it from the team
                result['stage_id'] = team._determine_stage()[team.id].id
        return result

    def _default_team_id(self):
        team_id = self.env['support.team'].search([('member_ids', 'in', self.env.uid)], limit=1).id
        if not team_id:
            team_id = self.env['support.team'].search([], limit=1).id
        return team_id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if self.env.context.get('default_team_id'):
            search_domain = ['|', ('team_ids', 'in', self.env.context['default_team_id'])] + search_domain

        return stages.search(search_domain, order=order)

    name = fields.Char(string='Subject', required=True, index=True)
    team_id = fields.Many2one('support.team', string='Support Team', default=_default_team_id, index=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    ticket_type_id = fields.Many2one('support.ticket.type', string="Ticket Type")
    tag_ids = fields.Many2many('support.ticket.tag', string='Tags')
    company_id = fields.Many2one(related='team_id.company_id', string='Company', store=True, readonly=True)
    color = fields.Integer(string='Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Column Status', tracking=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_user_ids')
    # user_id = fields.Many2one(
    #     'res.users', string='Assigned to', compute='_compute_user_and_stage_ids', store=True,
    #     readonly=False, tracking=True,
    #     domain=lambda self: [('groups_id', 'in', self.env.ref('gts_ticket_management.group_support_ticket_user').id)])
    user_id = fields.Many2one(
        'res.users', string='Assigned to', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_ticket_count = fields.Integer('Number of closed tickets from the same partner', compute='_compute_partner_ticket_count')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string="Number of Attachments")
    is_self_assigned = fields.Boolean("Am I assigned", compute='_compute_is_self_assigned')
    is_assgined_to_manager = fields.Boolean("Assigned to manager", compute='_compute_is_assigned_to_manager')
    partner_name = fields.Char(string='Customer Name', compute='_compute_partner_info', store=True, readonly=False)
    partner_email = fields.Char(string='Customer Email', compute='_compute_partner_info', store=True, readonly=False)
    closed_by_partner = fields.Boolean('Closed by Partner', readonly=True, help="If checked, this means the ticket was closed through the customer portal by the customer.")
    email = fields.Char(related='partner_email', string='Email on Customer', readonly=False)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    stage_id = fields.Many2one(
        'support.ticket.stage', string='Stage', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, ondelete='restrict', tracking=True, group_expand='_read_group_stage_ids',
        copy=False, index=True, domain="[('team_ids', '=', team_id)]")
    date_last_stage_update = fields.Datetime("Last Stage Update", copy=False, readonly=True)
    assign_date = fields.Datetime("First assignment date")
    assign_hours = fields.Integer("Time to first assignment (hours)", compute='_compute_assign_hours', store=True, help="This duration is based on the working calendar of the team")
    close_date = fields.Datetime("Close date", copy=False)
    close_hours = fields.Integer("Time to close (hours)", compute='_compute_close_hours', store=True, help="This duration is based on the working calendar of the team")
    open_hours = fields.Integer("Open Time (hours)", compute='_compute_open_hours', search='_search_open_hours', help="This duration is not based on the working calendar of the team")
    sla_ids = fields.Many2many('support.sla', 'support_sla_status', 'ticket_id', 'sla_id', string="SLAs", copy=False)
    sla_status_ids = fields.One2many('support.sla.status', 'ticket_id', string="SLA Status")
    sla_reached_late = fields.Boolean("Has SLA reached late", compute='_compute_sla_reached_late', compute_sudo=True, store=True)
    sla_deadline = fields.Datetime("SLA Deadline", compute='_compute_sla_deadline', compute_sudo=True, store=True, help="The closest deadline of all SLA applied on this ticket")
    sla_fail = fields.Boolean("Failed SLA Policy", compute='_compute_sla_fail', search='_search_sla_fail')
    sla_success = fields.Boolean("Success SLA Policy", compute='_compute_sla_success', search='_search_sla_success')

    use_credit_notes = fields.Boolean(related='team_id.use_credit_notes', string='Use Credit Notes')
    use_coupons = fields.Boolean(related='team_id.use_coupons', string='Use Coupons')
    use_product_returns = fields.Boolean(related='team_id.use_product_returns', string='Use Returns')
    use_product_repairs = fields.Boolean(related='team_id.use_product_repairs', string='Use Repairs')

    website_message_ids = fields.One2many(domain=lambda self: [('model', '=', self._name), ('message_type', 'in', ['email', 'comment'])])
    project_id = fields.Many2one('project.project', 'Project')
    is_from_project = fields.Boolean('From Project')
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', 'Timesheets')
    stakeholder_employee_ids = fields.Many2many('hr.employee', 'Stakeholders', compute='_compute_get_stakeholders')
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    project_stakeholder_ids = fields.Many2many('res.users', 'Stakeholders', compute='_get_project_stakeholders')
    date_deadline = fields.Date('Deadline', tracking=True)
    activity_reminder_days = fields.Integer('Activity Days')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            if record.project_id:
                record.partner_id = record.project_id.partner_id.id
                record.partner_email = record.project_id.partner_id.email

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

    @api.depends('project_id.allowed_user_ids', 'project_id.privacy_visibility')
    def _compute_allowed_user_ids(self):
        for task in self:
            portal_users = task.allowed_user_ids.filtered('share')
            internal_users = task.allowed_user_ids - portal_users
            if task.project_id.privacy_visibility == 'followers':
                task.allowed_user_ids |= task.project_id.allowed_internal_user_ids
                task.allowed_user_ids -= portal_users
            elif task.project_id.privacy_visibility == 'portal':
                task.allowed_user_ids |= task.project_id.allowed_portal_user_ids
            if task.project_id.privacy_visibility != 'portal':
                task.allowed_user_ids -= portal_users
            elif task.project_id.privacy_visibility != 'followers':
                task.allowed_user_ids -= internal_users

    @api.depends('project_id', 'project_id.stakeholder_ids', 'project_id.stakeholder_ids.status',
                 'project_id.stakeholder_ids.partner_id')
    def _compute_get_stakeholders(self):
        users_obj = self.env['res.users']
        employee_obj = self.env['hr.employee']
        stakeholder_employee_list = []
        if self.project_id and self.project_id.stakeholder_ids:
            for lines in self.project_id.stakeholder_ids:
                if lines.status is True:
                    user = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                    if user:
                        employee = employee_obj.search([('user_id', '=', user.id)], limit=1)
                        if employee:
                            stakeholder_employee_list.append(employee.id)
        self.stakeholder_employee_ids = [(6, 0, [id for id in stakeholder_employee_list])]

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.depends('team_id')
    def _compute_domain_user_ids(self):
        users_obj = self.env['res.users']
        for task in self:
            users_list = []
            if task.project_id and task.project_id.stakeholder_ids:
                for lines in task.project_id.stakeholder_ids:
                    if lines.status is True:
                        stakeholder = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        users_list.append(stakeholder.id)
            if task.team_id and task.team_id.visibility_member_ids:
                support_ticket_manager = self.env['res.users'].search([('groups_id', 'in', self.env.ref('gts_ticket_management.group_support_ticket_manager').id)])
                if support_ticket_manager:
                    for manager in support_ticket_manager:
                        users_list.append(manager.id)
                if task.team_id.visibility_member_ids:
                    for member in task.team_id.visibility_member_ids:
                        users_list.append(member.id)
                task.domain_user_ids = [(6, 0, [user for user in set(users_list)])]
            else:
                support_ticket_users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('gts_ticket_management.group_support_ticket_user').id)])
                if support_ticket_users:
                    for users in support_ticket_users:
                        users_list.append(users.id)
                task.domain_user_ids = [(6, 0, [user for user in set(users_list)])]

    def _compute_access_url(self):
        super(SupportTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/ticket/%s' % ticket.id

    def _compute_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'support.ticket'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = { res['res_id']: res['res_id_count'] for res in read_group_res }
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    @api.depends('sla_status_ids.deadline', 'sla_status_ids.reached_datetime')
    def _compute_sla_reached_late(self):
        mapping = {}
        if self.ids:
            self.env.cr.execute("""
                SELECT ticket_id, COUNT(id) AS reached_late_count
                FROM support_sla_status
                WHERE ticket_id IN %s AND deadline < reached_datetime
                GROUP BY ticket_id
            """, (tuple(self.ids),))
            mapping = dict(self.env.cr.fetchall())

        for ticket in self:
            ticket.sla_reached_late = mapping.get(ticket.id, 0) > 0

    @api.depends('sla_status_ids.deadline', 'sla_status_ids.reached_datetime')
    def _compute_sla_deadline(self):
        for ticket in self:
            deadline = False
            status_not_reached = ticket.sla_status_ids.filtered(lambda status: not status.reached_datetime and status.deadline)
            ticket.sla_deadline = min(status_not_reached.mapped('deadline')) if status_not_reached else deadline

    @api.depends('sla_deadline', 'sla_reached_late')
    def _compute_sla_fail(self):
        now = fields.Datetime.now()
        for ticket in self:
            if ticket.sla_deadline:
                ticket.sla_fail = (ticket.sla_deadline < now) or ticket.sla_reached_late
            else:
                ticket.sla_fail = ticket.sla_reached_late

    @api.model
    def _search_sla_fail(self, operator, value):
        datetime_now = fields.Datetime.now()
        if (value and operator in expression.NEGATIVE_TERM_OPERATORS) or (not value and operator not in expression.NEGATIVE_TERM_OPERATORS):  # is not failed
            return ['&', ('sla_reached_late', '=', False), '|', ('sla_deadline', '=', False), ('sla_deadline', '>=', datetime_now)]
        return ['|', ('sla_reached_late', '=', True), ('sla_deadline', '<', datetime_now)]  # is failed

    @api.depends('sla_deadline', 'sla_reached_late')
    def _compute_sla_success(self):
        now = fields.Datetime.now()
        for ticket in self:
            ticket.sla_success = (ticket.sla_deadline and ticket.sla_deadline > now)

    @api.model
    def _search_sla_success(self, operator, value):
        datetime_now = fields.Datetime.now()
        if (value and operator in expression.NEGATIVE_TERM_OPERATORS) or (not value and operator not in expression.NEGATIVE_TERM_OPERATORS):  # is failed
            return [[('sla_status_ids.reached_datetime', '>', datetime_now), ('sla_reached_late', '!=', False)]]
        return [('sla_status_ids.reached_datetime', '<', datetime_now), ('sla_reached_late', '=', False)]  # is success

    @api.depends('user_id')
    def _compute_is_self_assigned(self):
        for ticket in self:
            ticket.is_self_assigned = self.env.user == ticket.user_id

    @api.depends('user_id')
    def _compute_is_assigned_to_manager(self):
        for ticket in self:
            ticket.is_assgined_to_manager = False
            if ticket.user_id.has_group('gts_project_stages.group_project_manager_new'):
                ticket.is_assgined_to_manager = True

    @api.depends('team_id')
    def _compute_user_and_stage_ids(self):
        for ticket in self.filtered(lambda ticket: ticket.team_id):
            if not ticket.user_id:
                ticket.user_id = ticket.team_id._determine_user_to_assign()[ticket.team_id.id]
            if not ticket.stage_id or ticket.stage_id not in ticket.team_id.stage_ids:
                ticket.stage_id = ticket.team_id._determine_stage()[ticket.team_id.id]

    @api.depends('partner_id')
    def _compute_partner_info(self):
        for ticket in self:
            if ticket.partner_id:
                ticket.partner_name = ticket.partner_id.name
                ticket.partner_email = ticket.partner_id.email

    @api.depends('partner_id')
    def _compute_partner_ticket_count(self):
        data = self.env['support.ticket'].read_group([
            ('partner_id', 'in', self.mapped('partner_id').ids),
            ('stage_id.is_close', '=', False)
        ], ['partner_id'], ['partner_id'], lazy=False)
        ticket_per_partner_map = dict((item['partner_id'][0], item['__count']) for item in data)
        for ticket in self:
            ticket.partner_ticket_count = ticket_per_partner_map.get(ticket.partner_id.id, 0)

    @api.depends('assign_date')
    def _compute_assign_hours(self):
        for ticket in self:
            create_date = fields.Datetime.from_string(ticket.create_date)
            if create_date and ticket.assign_date and ticket.team_id.resource_calendar_id:
                duration_data = ticket.team_id.resource_calendar_id.get_work_duration_data(create_date, fields.Datetime.from_string(ticket.assign_date), compute_leaves=True)
                ticket.assign_hours = duration_data['hours']
            else:
                ticket.assign_hours = False

    @api.depends('create_date', 'close_date')
    def _compute_close_hours(self):
        for ticket in self:
            create_date = fields.Datetime.from_string(ticket.create_date)
            if create_date and ticket.close_date:
                duration_data = ticket.team_id.resource_calendar_id.get_work_duration_data(create_date, fields.Datetime.from_string(ticket.close_date), compute_leaves=True)
                ticket.close_hours = duration_data['hours']
            else:
                ticket.close_hours = False

    @api.depends('close_hours')
    def _compute_open_hours(self):
        for ticket in self:
            if ticket.create_date:
                if ticket.close_date:
                    time_difference = ticket.close_date - fields.Datetime.from_string(ticket.create_date)
                else:
                    time_difference = fields.Datetime.now() - fields.Datetime.from_string(ticket.create_date)
                ticket.open_hours = (time_difference.seconds) / 3600 + time_difference.days * 24
            else:
                ticket.open_hours = 0

    @api.model
    def _search_open_hours(self, operator, value):
        dt = fields.Datetime.now() - relativedelta.relativedelta(hours=value)

        d1, d2 = False, False
        if operator in ['<', '<=', '>', '>=']:
            d1 = ['&', ('close_date', '=', False), ('create_date', expression.TERM_OPERATORS_NEGATION[operator], dt)]
            d2 = ['&', ('close_date', '!=', False), ('close_hours', operator, value)]
        elif operator in ['=', '!=']:
            subdomain = ['&', ('create_date', '>=', dt.replace(minute=0, second=0, microsecond=0)), ('create_date', '<=', dt.replace(minute=59, second=59, microsecond=99))]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                subdomain = expression.distribute_not(subdomain)
            d1 = expression.AND([[('close_date', '=', False)], subdomain])
            d2 = ['&', ('close_date', '!=', False), ('close_hours', operator, value)]
        return expression.OR([d1, d2])

    def name_get(self):
        result = []
        for ticket in self:
            result.append((ticket.id, "%s (#%d)" % (ticket.name, ticket._origin.id)))
        return result
        
    @api.model
    def create_action(self, action_ref, title, search_view_ref):
        action = self.env["ir.actions.actions"]._for_xml_id(action_ref)
        if title:
            action['display_name'] = title
        if search_view_ref:
            action['search_view_id'] = self.env.ref(search_view_ref).read()[0]
        action['views'] = [(False, view) for view in action['view_mode'].split(",")]
        
        return {'action': action}

    @api.model_create_multi
    def create(self, list_value):
        now = fields.Datetime.now()
        print(list_value)
        users_obj = self.env['res.users']
        teams = self.env['support.team'].browse([vals['team_id'] for vals in list_value if vals.get('team_id')])
        team_default_map = dict.fromkeys(teams.ids, dict())
        for team in teams:
            team_default_map[team.id] = {
                'stage_id': team._determine_stage()[team.id].id,
                'user_id': team._determine_user_to_assign()[team.id].id
            }
        for vals in list_value:
            if 'partner_name' in vals and 'partner_email' in vals and 'partner_id' not in vals:
                try:
                    vals['partner_id'] = self.env['res.partner'].find_or_create(
                        tools.formataddr((vals['partner_name'], vals['partner_email']))
                    ).id
                except UnicodeEncodeError:
                    vals['partner_id'] = self.env['res.partner'].create({
                        'name': vals['partner_name'],
                        'email': vals['partner_email'],
                    }).id
        partners = self.env['res.partner'].browse([vals['partner_id'] for vals in list_value if 'partner_id' in vals and vals.get('partner_id') and 'partner_email' not in vals])
        partner_email_map = {partner.id: partner.email for partner in partners}
        partner_name_map = {partner.id: partner.name for partner in partners}
        for vals in list_value:
            if vals.get('team_id'):
                team_default = team_default_map[vals['team_id']]
                if 'stage_id' not in vals:
                    vals['stage_id'] = team_default['stage_id']
                if 'user_id' not in vals:
                    vals['user_id'] = team_default['user_id']
                if vals.get('user_id'):
                    vals['assign_date'] = fields.Datetime.now()
                    vals['assign_hours'] = 0
            if vals.get('partner_id') in partner_email_map:
                vals['partner_email'] = partner_email_map.get(vals['partner_id'])
            if vals.get('partner_id') in partner_name_map:
                vals['partner_name'] = partner_name_map.get(vals['partner_id'])
            if vals.get('stage_id'):
                vals['date_last_stage_update'] = now
        tickets = super(SupportTicket, self).create(list_value)
        if tickets.date_deadline < datetime.now().date():
            raise UserError(_("Deadline cannot be less then today's date!"))
        partner_list = []
        if tickets.project_id:
            if tickets.project_id.program_manager_id:
                partner_list.append(tickets.project_id.program_manager_id.partner_id.id)
            if tickets.project_id.user_id:
                partner_list.append(tickets.project_id.user_id.partner_id.id)
        new_list = list(set(partner_list))
        tickets.message_subscribe(partner_ids=new_list)
        for ticket in tickets:
            # if ticket.partner_id:
            #     ticket.message_subscribe(partner_ids=ticket.partner_id.ids)
            ticket._portal_ensure_token()
        tickets.sudo()._sla_apply()
        # notification email
        stakeholder_list = ''
        # if tickets.project_id and tickets.project_id.stakeholder_ids:
        #     for record in tickets.project_id.stakeholder_ids:
        #         user = users_obj.search([('partner_id', '=', record.partner_id.id)], limit=1)
        #         if user:
        #             stakeholder_list += user.login + ","
        if tickets.message_follower_ids:
            for follower in tickets.message_follower_ids:
                stakeholder_list += follower.partner_id.email + ","
        action_id = self.env.ref('gts_ticket_management.support_ticket_action_main_tree').id
        params = "web#id=%s&view_type=form&model=support.ticket&action=%s" % (tickets.id, action_id)
        ticket_url = str(params)
        if stakeholder_list and tickets.user_id:
            template = self.env.ref('gts_ticket_management.ticket_created_email_assignedto_stakeholder')
            if template:
                values = template.generate_email(tickets.id, ['subject', 'email_to', 'email_from', 'body_html'])
                values['email_to'] = tickets.user_id.login + "," + stakeholder_list
                values['email_from'] = self.env.user.partner_id.email or self.env.user.login

                values['body_html'] = values['body_html'].replace('_ticket_url', ticket_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
        if tickets.user_id:
            activity_dict = {
                'res_model': 'support.ticket',
                'res_model_id': self.env.ref('gts_ticket_management.model_support_ticket').id,
                'res_id': tickets.id,
                'activity_type_id': self.env.ref('gts_ticket_management.ticket_assigned_activity').id,
                'date_deadline': tickets.date_deadline,
                'summary': "Ticket Assinged",
                'user_id': tickets.user_id.id
            }
            self.env['mail.activity'].create(activity_dict)
        partner_list = []
        if tickets.project_id:
            if tickets.project_id.program_manager_id:
                partner_list.append(tickets.project_id.program_manager_id.partner_id.id)
            if tickets.project_id.user_id:
                partner_list.append(tickets.project_id.user_id.partner_id.id)
        new_list = list(set(partner_list))
        tickets.message_subscribe(partner_ids=new_list)
        tickets.is_from_project = True
        return tickets

    def write(self, vals):
        assigned_tickets = closed_tickets = self.browse()
        if vals.get('user_id'):
            assigned_tickets = self.filtered(lambda ticket: not ticket.assign_date)
        if vals.get('stage_id'):
            if self.env['support.ticket.stage'].browse(vals.get('stage_id')).is_close:
                closed_tickets = self.filtered(lambda ticket: not ticket.close_date)
            else:
                vals['closed_by_partner'] = False
        now = fields.Datetime.now()
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = now
        res = super(SupportTicket, self - assigned_tickets - closed_tickets).write(vals)
        res &= super(SupportTicket, assigned_tickets - closed_tickets).write(dict(vals, **{
            'assign_date': now,
        }))
        res &= super(SupportTicket, closed_tickets - assigned_tickets).write(dict(vals, **{
            'close_date': now,
        }))
        res &= super(SupportTicket, assigned_tickets & closed_tickets).write(dict(vals, **{
            'assign_date': now,
            'close_date': now,
        }))

        if vals.get('partner_id'):
            self.message_subscribe([vals['partner_id']])
        sla_triggers = self._sla_reset_trigger()
        if any(field_name in sla_triggers for field_name in vals.keys()):
            self.sudo()._sla_apply(keep_reached=True)
        if 'stage_id' in vals:
            self.sudo()._sla_reach(vals['stage_id'])
        if 'stage_id' in vals or 'user_id' in vals:
            self.filtered(lambda ticket: ticket.user_id).sudo()._sla_assigning_reach()
        if self.date_deadline:
            if self.date_deadline < datetime.now().date():
                raise UserError(_("Deadline cannot be less then today's date!"))
        # notification email
        users_obj = self.env['res.users']
        if 'stage_id' in vals:
            stakeholder_list = ''
            if self.project_id and self.project_id.stakeholder_ids:
                for record in self.project_id.stakeholder_ids:
                    user = users_obj.search([('partner_id', '=', record.partner_id.id)], limit=1)
                    if user:
                        stakeholder_list += user.login + ","
            action_id = self.env.ref('gts_ticket_management.support_ticket_action_main_tree').id
            params = "web#id=%s&view_type=form&model=support.ticket&action=%s" % (self.id, action_id)
            ticket_url = str(params)
            if self.stage_id.is_close is False and self.partner_id:
                template = self.env.ref('gts_ticket_management.ticket_updated_notification_email_customer')
                if template:
                    values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = self.partner_id.email or self.partner_email
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
            if stakeholder_list:
                template = self.env.ref('gts_ticket_management.ticket_updated_to_stakeholder')
                if template:
                    values = template.generate_email(self.id,
                                                     ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
                    values['email_to'] = self.user_id.partner_id.email or self.user_id.login
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['email_cc'] = stakeholder_list
                    values['body_html'] = values['body_html'].replace('_ticket_url', ticket_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        if 'user_id' in vals:
            activity_dict = {
                'res_model': 'support.ticket',
                'res_model_id': self.env.ref('gts_ticket_management.model_support_ticket').id,
                'res_id': self.id,
                'activity_type_id': self.env.ref('gts_ticket_management.ticket_assigned_activity').id,
                'date_deadline': self.date_deadline,
                'summary': "Ticket Assinged",
                'user_id': vals.get('user_id')
            }
            self.env['mail.activity'].create(activity_dict)
        return res

    @api.model
    def _sla_reset_trigger(self):
        return ['team_id', 'priority', 'ticket_type_id', 'tag_ids']

    def _sla_apply(self, keep_reached=False):
        sla_per_tickets = self._sla_find()
        sla_status_value_list = []
        for tickets, slas in sla_per_tickets.items():
            sla_status_value_list += tickets._sla_generate_status_values(slas, keep_reached=keep_reached)
        sla_status_to_remove = self.mapped('sla_status_ids')
        if keep_reached:
            sla_status_to_remove = sla_status_to_remove.filtered(lambda status: not status.reached_datetime)
        if sla_status_value_list:
            sla_status_to_remove.with_context(norecompute=True)
        sla_status_to_remove.unlink()
        return self.env['support.sla.status'].create(sla_status_value_list)

    def _sla_find(self):
        tickets_map = {}
        sla_domain_map = {}
        def _generate_key(ticket):
            fields_list = self._sla_reset_trigger()
            key = list()
            for field_name in fields_list:
                if ticket._fields[field_name].type == 'many2one':
                    key.append(ticket[field_name].id)
                else:
                    key.append(ticket[field_name])
            return tuple(key)
        for ticket in self:
            if ticket.team_id.use_sla:
                key = _generate_key(ticket)
                tickets_map.setdefault(key, self.env['support.ticket'])
                tickets_map[key] |= ticket
                if key not in sla_domain_map:
                    sla_domain_map[key] = [
                        ('team_id', '=', ticket.team_id.id), ('priority', '<=', ticket.priority),
                        '|',
                            '&', ('stage_id.sequence', '>=', ticket.stage_id.sequence),
                        ('target_type', '=', 'stage'),
                            ('target_type', '=', 'assigning'),
                        '|', ('ticket_type_id', '=', ticket.ticket_type_id.id), ('ticket_type_id', '=', False)]
        result = {}
        for key, tickets in tickets_map.items():
            domain = sla_domain_map[key]
            slas = self.env['support.sla'].search(domain)
            result[tickets] = slas.filtered(lambda s: s.tag_ids <= tickets.tag_ids)  # SLA to apply on ticket subset
        return result

    def _sla_generate_status_values(self, slas, keep_reached=False):
        status_to_keep = dict.fromkeys(self.ids, list())
        if keep_reached:
            for ticket in self:
                for status in ticket.sla_status_ids:
                    if status.reached_datetime:
                        status_to_keep[ticket.id].append(status.sla_id.id)
        result = []
        for ticket in self:
            for sla in slas:
                if not (keep_reached and sla.id in status_to_keep[ticket.id]):
                    if sla.target_type == 'stage' and ticket.stage_id == sla.stage_id:
                        reached_datetime = fields.Datetime.now()
                    elif sla.target_type == 'assigning' and (not sla.stage_id or ticket.stage_id == sla.stage_id) and ticket.user_id:
                        reached_datetime = fields.Datetime.now()
                    else:
                        reached_datetime = False
                    result.append({
                        'ticket_id': ticket.id,
                        'sla_id': sla.id,
                        'reached_datetime': reached_datetime
                    })

        return result

    def _sla_assigning_reach(self):
        self.env['support.sla.status'].search([
            ('ticket_id', 'in', self.ids),
            ('reached_datetime', '=', False),
            ('deadline', '!=', False),
            ('target_type', '=', 'assigning')
        ]).write({'reached_datetime': fields.Datetime.now()})

    def _sla_reach(self, stage_id):
        stage = self.env['support.ticket.stage'].browse(stage_id)
        stages = self.env['support.ticket.stage'].search([('sequence', '<=', stage.sequence),
                                                          ('team_ids', 'in', self.mapped('team_id').ids)])
        self.env['support.sla.status'].search([
            ('ticket_id', 'in', self.ids),
            ('sla_stage_id', 'in', stages.ids),
            ('reached_datetime', '=', False),
            ('target_type', '=', 'stage')
        ]).write({'reached_datetime': fields.Datetime.now()})
        self.env['support.sla.status'].search([
            ('ticket_id', 'in', self.ids),
            ('sla_stage_id', '!=', False),
            ('reached_datetime', '=', False),
            ('target_type', '=', 'assigning')
        ])._compute_deadline()

    def assign_ticket_to_self(self):
        self.ensure_one()
        self.user_id = self.env.user
        users_obj = self.env['res.users']
        stakeholder_list = ''
        if self.project_id and self.project_id.stakeholder_ids:
            for record in self.project_id.stakeholder_ids:
                user = users_obj.search([('partner_id', '=', record.partner_id.id)], limit=1)
                if user:
                    stakeholder_list += user.login + ","
        action_id = self.env.ref('gts_ticket_management.support_ticket_action_main_tree').id
        params = "web#id=%s&view_type=form&model=support.ticket&action=%s" % (self.id, action_id)
        ticket_url = str(params)
        template = self.env.ref('gts_ticket_management.ticket_assigned_tome_email')
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = stakeholder_list
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_ticket_url', ticket_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass

    def open_customer_tickets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Tickets'),
            'res_model': 'support.ticket',
            'view_mode': 'kanban,tree,form,pivot,graph',
            'context': {'search_default_is_open': True, 'search_default_partner_id': self.partner_id.id}
        }

    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        return action

    def _message_get_suggested_recipients(self):
        recipients = super(SupportTicket, self)._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id and ticket.partner_id.email:
                    ticket._message_add_suggested_recipient(recipients, partner=ticket.partner_id, reason=_('Customer'))
                elif ticket.partner_email:
                    ticket._message_add_suggested_recipient(recipients, email=ticket.partner_email, reason=_('Customer Email'))
        except AccessError:
            pass
        return recipients

    def _ticket_email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        return [
            x for x in email_list
            if x.split('@')[0] not in self.mapped('team_id.alias_name')
        ]

    # @api.model
    # def message_new(self, msg, custom_values=None):
    #     values = dict(custom_values or {}, partner_email=msg.get('from'), partner_id=msg.get('author_id'))
    #     ticket = super(SupportTicket, self).message_new(msg, custom_values=values)
    #     partner_ids = [x.id for x in self.env['mail.thread']._mail_find_partner_from_emails(self._ticket_email_split(msg), records=ticket) if x]
    #     customer_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(tools.email_split(values['partner_email']), records=ticket) if p]
    #     partner_ids += customer_ids
    #     if customer_ids and not values.get('partner_id'):
    #         ticket.partner_id = customer_ids[0]
    #     if partner_ids:
    #         ticket.message_subscribe(partner_ids)
    #     return ticket

    def message_update(self, msg, update_vals=None):
        partner_ids = [x.id for x in self.env['mail.thread']._mail_find_partner_from_emails(self._ticket_email_split(msg), records=self) if x]
        if partner_ids:
            self.message_subscribe(partner_ids)
        return super(SupportTicket, self).message_update(msg, update_vals=update_vals)

    def _message_post_after_hook(self, message, msg_vals):
        if self.partner_email and self.partner_id and not self.partner_id.email:
            self.partner_id.email = self.partner_email

        if self.partner_email and not self.partner_id:
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.partner_email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('partner_email', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(SupportTicket, self)._message_post_after_hook(message, msg_vals)

    def _track_template(self, changes):
        res = super(SupportTicket, self)._track_template(changes)
        ticket = self[0]
        if 'stage_id' in changes and ticket.stage_id.template_id:
            res['stage_id'] = (ticket.stage_id.template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            }
        )
        return res

    def _creation_subtype(self):
        return self.env.ref('gts_ticket_management.mt_ticket_new')

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values:
            return self.env.ref('gts_ticket_management.mt_ticket_stage')
        return super(SupportTicket, self)._track_subtype(init_values)

    # def _notify_get_groups(self, msg_vals=None):
    #     groups = super(SupportTicket, self)._notify_get_groups(msg_vals=msg_vals)
    #
    #     self.ensure_one()
    #     for group_name, group_method, group_data in groups:
    #         if group_name != 'customer':
    #             group_data['has_button_access'] = True
    #
    #     if self.user_id:
    #         return groups
    #
    #     take_action = self._notify_get_action_link('assign')
    #     support_ticket_actions = [{'url': take_action, 'title': _('Assign to me')}]
    #     support_ticket_user_group_id = self.env.ref('gts_ticket_management.group_support_ticket_user').id
    #     new_groups = [(
    #         'group_support_ticket_user',
    #         lambda pdata: pdata['type'] == 'user' and support_ticket_user_group_id in pdata['groups'],
    #         {'actions': support_ticket_actions}
    #     )]
    #     return new_groups + groups

    def _notify_get_reply_to(self, default=None, records=None, company=None, doc_names=None):
        aliases = self.mapped('team_id').sudo()._notify_get_reply_to(default=default, records=None, company=company, doc_names=None)
        res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(super(SupportTicket, leftover)._notify_get_reply_to(default=default, records=None, company=company, doc_names=doc_names))
        return res

    def rating_apply(self, rate, token=None, feedback=None, subtype_xmlid=None):
        return super(SupportTicket, self).rating_apply(rate, token=token, feedback=feedback, subtype_xmlid="gts_ticket_management.mt_ticket_rated")

    def _rating_get_parent_field_name(self):
        return 'team_id'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        model_id = self.env['ir.model'].search([('model', '=', 'support.ticket')], limit=1)
        if model_id:
            server = self.env['fetchmail.server'].search([('object_id', '=', model_id.id)], limit=1)
            if server and server.fetch_key:
                if server.fetch_key in msg_dict.get('subject'):
                    msg_description = ''
                    if msg_dict.get('body'):
                        msg_body = """""" + msg_dict.get('body') + """"""
                        soup_body = bs(msg_body)
                        text_body = soup_body.find_all()
                        msg_description = text_body[0].text
                    values = dict(custom_values or {}, description=msg_description)
                    return super(SupportTicket, self).message_new(msg_dict, custom_values=values)

    def ticket_activity_reminder(self):
        tickets = self.env['support.ticket'].search([])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in tickets:
            activity = mail_activity_obj.search(
                [('res_id', '=', record.id), ('res_model', '=', 'support.ticket'),
                 ('activity_type_id', '=',
                  self.env.ref('gts_ticket_management.ticket_assigned_activity').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        template = self.env.ref('gts_ticket_management.issue_activity_email_reminder')
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('gts_ticket_management.support_ticket_action_main_my').id
                        params = str(
                            base_url) + "/web#id=%s&view_type=form&model=support.ticket&action=%s" % (
                            record.id, action_id)
                        ticket_url = str(params)
                        if template:
                            values = template.generate_email(record.id,
                                                             ['subject', 'email_to', 'email_from',
                                                              'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.project_id.outgoing_email
                            values['body_html'] = values['body_html'].replace('_ticket_url', ticket_url)
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


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    ticket_id = fields.Many2one('support.ticket', 'Ticket')

    def write(self, vals):
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
            message_body += """<span style='color:red;'>• Date: {prev_date} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {date}</span><br/>""".format(
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
        #                 • Actual Hours: {prev_actual_hours} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {actual_amount}""" \
        #     .format(prev_date=prev_date, date=self.date,
        #             prev_employee=prev_employee, employee=self.employee_id.name,
        #             prev_name=prev_name, description=self.name or '',
        #             prev_estimated_hours=prev_estimated_hours, estimated_hours=self.estimated_hours,
        #             prev_actual_hours=prev_actual_hours, actual_amount=self.unit_amount)
        if self.ticket_id:
            self.ticket_id.message_post(body=message_body)
        return rec
