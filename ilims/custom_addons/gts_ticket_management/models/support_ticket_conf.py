# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.

import ast
import datetime

from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.addons.gts_ticket_management.models.support_ticket import TICKET_PRIORITY
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class SupportTeam(models.Model):
    _name = "support.team"
    _inherit = ['mail.alias.mixin', 'mail.thread', 'rating.parent.mixin', 'website.published.mixin']
    _description = "Support Team"
    _order = 'sequence,name'
    _rating_satisfaction_days = False

    _sql_constraints = [('not_portal_show_rating_if_not_use_rating',
                         'check (portal_show_rating = FALSE OR use_rating = TRUE)',
                         'Cannot show ratings in portal if not using them'), ]

    def _default_stage_ids(self):
        default_stage = self.env['support.ticket.stage'].search([('name', '=', _('New'))], limit=1)
        if default_stage:
            return [(4, default_stage.id)]
        return [(0, 0, {'name': _('New'), 'sequence': 0, 'template_id': self.env.ref('gts_ticket_management.new_ticket_request_email_template', raise_if_not_found=False) or None})]

    def _default_domain_member_ids(self):
        return [('groups_id', 'in', self.env.ref('gts_ticket_management.group_support_ticket_user').id)]

    name = fields.Char('Support Team', required=True, translate=True)
    description = fields.Text('About Team', translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sequence = fields.Integer("Sequence", default=10)
    color = fields.Integer('Color Index', default=1)
    stage_ids = fields.Many2many(
        'support.ticket.stage', relation='team_stage_rel', string='Stages',
        default=_default_stage_ids,
        help="Stages the team will use. This team's tickets will only be able to be in these stages.")
    assign_method = fields.Selection([
        ('manual', 'Manually'),
        ('randomly', 'Random'),
        ('balanced', 'Balanced')], string='Assignment Method', default='manual',
        compute='_compute_assign_method', store=True, readonly=False, required=True,
        help='Automatic assignment method for new tickets:\n'
             '\tManually: manual\n'
             '\tRandomly: randomly but everyone gets the same amount\n'
             '\tBalanced: to the person with the least amount of open tickets')
    member_ids = fields.Many2many('res.users', string='Team Members', domain=lambda self: self._default_domain_member_ids())
    visibility_member_ids = fields.Many2many('res.users', 'support_visibility_team', string='Team Visibility', domain=lambda self: self._default_domain_member_ids(),
        help="Team Members to whom this team will be visible. Keep empty for everyone to see this team.")
    ticket_ids = fields.One2many('support.ticket', 'team_id', string='Tickets')

    use_alias = fields.Boolean('Email alias', default=True)
    has_external_mail_server = fields.Boolean(compute='_compute_has_external_mail_server')
    allow_portal_ticket_closing = fields.Boolean('Ticket closing', help="Allow customers to close their tickets")
    use_website_support_form = fields.Boolean('Website Form')
    use_website_support_livechat = fields.Boolean('Live chat',
        help="In Channel: You can create a new ticket by typing /support [ticket title]. You can search ticket by typing /support_search [Keyword1],[Keyword2],.")
    use_website_support_forum = fields.Boolean('Help Center')
    use_website_support_slides = fields.Boolean('Enable eLearning')
    use_support_timesheet = fields.Boolean('Timesheet on Ticket', help="This required to have project module installed.")
    use_support_sale_timesheet = fields.Boolean(
        'Time Reinvoicing', compute='_compute_use_support_sale_timesheet', store=True,
        readonly=False, help="Reinvoice the time spent on ticket through tasks.")
    use_credit_notes = fields.Boolean('Refunds')
    use_coupons = fields.Boolean('Coupons')
    use_product_returns = fields.Boolean('Returns')
    use_product_repairs = fields.Boolean('Repairs')
    use_twitter = fields.Boolean('Twitter')
    use_rating = fields.Boolean('Ratings on tickets')
    portal_show_rating = fields.Boolean(
        'Display Rating on Customer Portal', compute='_compute_portal_show_rating', store=True,
        readonly=False)
    portal_rating_url = fields.Char('URL to Submit an Issue', readonly=True, compute='_compute_portal_rating_url')
    use_sla = fields.Boolean('SLA Policies')
    upcoming_sla_fail_tickets = fields.Integer(string='Upcoming SLA Fail Tickets', compute='_compute_upcoming_sla_fail_tickets')
    unassigned_tickets = fields.Integer(string='Unassigned Tickets', compute='_compute_unassigned_tickets')
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours',
        default=lambda self: self.env.company.resource_calendar_id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    #############################Start#######################################################
    def _compute_website_url(self):
        super(SupportTeam, self)._compute_website_url()
        for team in self:
            team.website_url = "/support/%s" % slug(team)

    @api.onchange('use_website_support_form')
    def _onchange_use_website_support(self):
        if not (self.use_website_support_form) and self.website_published:
            self.is_published = False

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            vals['is_published'] = False
        return super(SupportTeam, self).write(vals)

    def action_view_all_rating(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Redirect to the Website Support Rating Page",
            'target': 'self',
            'url': "/support/rating/"
        }
    #############################END###########################################

    @api.depends('name', 'portal_show_rating')
    def _compute_portal_rating_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for team in self:
            if team.name and team.portal_show_rating and team.id:
                team.portal_rating_url = '%s/support/rating/%s' % (base_url, slug(team))
            else:
                team.portal_rating_url = False

    def _compute_has_external_mail_server(self):
        self.has_external_mail_server = self.env['ir.config_parameter'].sudo().get_param('base_setup.default_external_email_server')

    def _compute_upcoming_sla_fail_tickets(self):
        ticket_data = self.env['support.ticket'].read_group([
            ('team_id', 'in', self.ids),
            ('sla_deadline', '!=', False),
            ('sla_deadline', '<=', fields.Datetime.to_string((datetime.date.today() + relativedelta.relativedelta(days=1)))),
        ], ['team_id'], ['team_id'])
        mapped_data = dict((data['team_id'][0], data['team_id_count']) for data in ticket_data)
        for team in self:
            team.upcoming_sla_fail_tickets = mapped_data.get(team.id, 0)

    def _compute_unassigned_tickets(self):
        ticket_data = self.env['support.ticket'].read_group([('user_id', '=', False), ('team_id', 'in', self.ids), ('stage_id.is_close', '!=', True)], ['team_id'], ['team_id'])
        mapped_data = dict((data['team_id'][0], data['team_id_count']) for data in ticket_data)
        for team in self:
            team.unassigned_tickets = mapped_data.get(team.id, 0)

    @api.depends('use_rating')
    def _compute_portal_show_rating(self):
        without_rating = self.filtered(lambda t: not t.use_rating)
        without_rating.update({'portal_show_rating': False})

    @api.depends('member_ids', 'visibility_member_ids')
    def _compute_assign_method(self):
        with_manual = self.filtered(lambda t: not t.member_ids and not t.visibility_member_ids)
        with_manual.update({'assign_method': 'manual'})

    @api.onchange('use_alias', 'name')
    def _onchange_use_alias(self):
        if not self.use_alias:
            self.alias_name = False

    @api.depends('use_support_timesheet')
    def _compute_use_support_sale_timesheet(self):
        without_timesheet = self.filtered(lambda t: not t.use_support_timesheet)
        without_timesheet.update({'use_support_sale_timesheet': False})

    @api.constrains('assign_method', 'member_ids', 'visibility_member_ids')
    def _check_member_assignation(self):
        if not self.member_ids and not self.visibility_member_ids and self.assign_method != 'manual':
            raise ValidationError(_("You must have team members assigned to change the assignment method."))

    @api.model
    def create(self, vals):
        team = super(SupportTeam, self.with_context(mail_create_nosubscribe=True)).create(vals)
        team.sudo()._check_sla_group()
        team.sudo()._check_modules_to_install()
        # If you plan to add something after this, use a new environment. The one above is no longer valid after the modules install.
        return team

    def write(self, vals):
        result = super(SupportTeam, self).write(vals)
        if 'active' in vals:
            self.with_context(active_test=False).mapped('ticket_ids').write({'active': vals['active']})
        self.sudo()._check_sla_group()
        self.sudo()._check_modules_to_install()
        return result

    def unlink(self):
        stages = self.mapped('stage_ids').filtered(lambda stage: stage.team_ids <= self)
        stages.unlink()
        return super(SupportTeam, self).unlink()

    def _check_sla_group(self):
        for team in self:
            if team.use_sla and not self.user_has_groups('gts_ticket_management.group_use_sla'):
                self.env.ref('gts_ticket_management.group_support_ticket_user').write({'implied_ids': [(4, self.env.ref('gts_ticket_management.group_use_sla').id)]})
            if team.use_sla:
                self.env['support.sla'].with_context(active_test=False).search([('team_id', '=', team.id), ('active', '=', False)]).write({'active': True})
            else:
                self.env['support.sla'].search([('team_id', '=', team.id)]).write({'active': False})
                if not self.search_count([('use_sla', '=', True)]):
                    self.env.ref('gts_ticket_management.group_support_ticket_user').write({'implied_ids': [(3, self.env.ref('gts_ticket_management.group_use_sla').id)]})
                    self.env.ref('gts_ticket_management.group_use_sla').write({'users': [(5, 0, 0)]})

    def _check_modules_to_install(self):
        FIELD_MODULE = {
            'use_website_support_form': 'website_support_form',
        }
        expected = [
            mname
            for fname, mname in FIELD_MODULE.items()
            if any(team[fname] for team in self)
        ]
        modules = self.env['ir.module.module']
        if expected:
            STATES = ('installed', 'to install', 'to upgrade')
            modules = modules.search([('name', 'in', expected)])
            modules = modules.filtered(lambda module: module.state not in STATES)
        for team in self:
            if team.use_rating:
                for stage in team.stage_ids:
                    if stage.is_close and not stage.fold:
                        stage.template_id = self.env.ref('gts_ticket_management.rating_ticket_request_email_template', raise_if_not_found= False)
        if modules:
            modules.button_immediate_install()
        return bool(modules)

    def _alias_get_creation_values(self):
        values = super(SupportTeam, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('support.ticket').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults['team_id'] = self.id
        return values

    @api.model
    def retrieve_dashboard(self):
        domain = [('user_id', '=', self.env.uid)]
        group_fields = ['priority', 'create_date', 'stage_id', 'close_hours']
        list_fields = ['priority', 'create_date', 'stage_id', 'close_hours']
        user_uses_sla = self.user_has_groups('gts_ticket_management.group_use_sla') and\
            bool(self.env['support.team'].search([('use_sla', '=', True), '|', ('member_ids', 'in', self._uid), ('member_ids', '=', False)]))

        if user_uses_sla:
            group_fields.insert(1, 'sla_deadline:year')
            group_fields.insert(2, 'sla_deadline:hour')
            group_fields.insert(3, 'sla_reached_late')
            list_fields.insert(1, 'sla_deadline')
            list_fields.insert(2, 'sla_reached_late')

        SupportTicket = self.env['support.ticket']
        tickets = SupportTicket.search_read(expression.AND([domain, [('stage_id.is_close', '=', False)]]), ['sla_deadline', 'open_hours', 'sla_reached_late', 'priority'])

        result = {
            'support_ticket_target_closed': self.env.user.support_ticket_target_closed,
            'support_ticket_target_rating': self.env.user.support_ticket_target_rating,
            'support_ticket_target_success': self.env.user.support_ticket_target_success,
            'today': {'count': 0, 'rating': 0, 'success': 0},
            '7days': {'count': 0, 'rating': 0, 'success': 0},
            'my_all': {'count': 0, 'hours': 0, 'failed': 0},
            'my_high': {'count': 0, 'hours': 0, 'failed': 0},
            'my_urgent': {'count': 0, 'hours': 0, 'failed': 0},
            'show_demo': not bool(SupportTicket.search([], limit=1)),
            'rating_enable': False,
            'success_rate_enable': user_uses_sla
        }

        def _is_sla_failed(data):
            deadline = data.get('sla_deadline')
            sla_deadline = fields.Datetime.now() > deadline if deadline else False
            return sla_deadline or data.get('sla_reached_late')

        def add_to(ticket, key="my_all"):
            result[key]['count'] += 1
            result[key]['hours'] += ticket['open_hours']
            if _is_sla_failed(ticket):
                result[key]['failed'] += 1

        for ticket in tickets:
            add_to(ticket, 'my_all')
            if ticket['priority'] == '2':
                add_to(ticket, 'my_high')
            if ticket['priority'] == '3':
                add_to(ticket, 'my_urgent')

        dt = fields.Date.today()
        tickets = SupportTicket.read_group(domain + [('stage_id.is_close', '=', True), ('close_date', '>=', dt)], list_fields, group_fields, lazy=False)
        for ticket in tickets:
            result['today']['count'] += ticket['__count']
            if not _is_sla_failed(ticket):
                result['today']['success'] += ticket['__count']

        dt = fields.Datetime.to_string((datetime.date.today() - relativedelta.relativedelta(days=6)))
        tickets = SupportTicket.read_group(domain + [('stage_id.is_close', '=', True), ('close_date', '>=', dt)], list_fields, group_fields, lazy=False)
        for ticket in tickets:
            result['7days']['count'] += ticket['__count']
            if not _is_sla_failed(ticket):
                result['7days']['success'] += ticket['__count']

        result['today']['success'] = (result['today']['success'] * 100) / (result['today']['count'] or 1)
        result['7days']['success'] = (result['7days']['success'] * 100) / (result['7days']['count'] or 1)
        result['my_all']['hours'] = round(result['my_all']['hours'] / (result['my_all']['count'] or 1), 2)
        result['my_high']['hours'] = round(result['my_high']['hours'] / (result['my_high']['count'] or 1), 2)
        result['my_urgent']['hours'] = round(result['my_urgent']['hours'] / (result['my_urgent']['count'] or 1), 2)

        if self.env['support.team'].search([('use_rating', '=', True), '|', ('member_ids', 'in', self._uid), ('member_ids', '=', False)]):
            result['rating_enable'] = True
            # rating of today
            domain = [('user_id', '=', self.env.uid)]
            dt = fields.Date.today()
            tickets = self.env['support.ticket'].search(domain + [('stage_id.is_close', '=', True), ('close_date', '>=', dt)])
            activity = tickets.rating_get_grades()
            total_rating = self._compute_activity_avg(activity)
            total_activity_values = sum(activity.values())
            team_satisfaction = round((total_rating / total_activity_values if total_activity_values else 0), 2) * 5
            if team_satisfaction:
                result['today']['rating'] = team_satisfaction
            dt = fields.Datetime.to_string((datetime.date.today() - relativedelta.relativedelta(days=6)))
            tickets = self.env['support.ticket'].search(domain + [('stage_id.is_close', '=', True), ('close_date', '>=', dt)])
            activity = tickets.rating_get_grades()
            total_rating = self._compute_activity_avg(activity)
            total_activity_values = sum(activity.values())
            team_satisfaction_7days = round((total_rating / total_activity_values if total_activity_values else 0), 2) * 5
            if team_satisfaction_7days:
                result['7days']['rating'] = team_satisfaction_7days
        return result

    def _action_view_rating(self, period=False, only_my_closed=False):
        domain = [('team_id', 'in', self.ids)]
        if period == 'seven_days':
            domain += [('close_date', '>=', fields.Datetime.to_string((datetime.date.today() - relativedelta.relativedelta(days=6))))]
        elif period == 'today':
            domain += [('close_date', '>=', fields.Datetime.to_string(datetime.date.today()))]
        if only_my_closed:
            domain += [('user_id', '=', self._uid), ('stage_id.is_close', '=', True)]
        ticket_ids = self.env['support.ticket'].search(domain).ids
        action = self.env["ir.actions.actions"]._for_xml_id("rating.rating_rating_view")
        action['domain'] = [('res_id', 'in', ticket_ids), ('rating', '!=', -1), ('res_model', '=', 'support.ticket'), ('consumed', '=', True)]
        action['help'] = '<p class="o_view_nocontent_empty_folder">No data yet !</p><p>Create tickets to get statistics.</p>'
        return action

    def action_view_ticket(self):
        action = self.env["ir.actions.actions"]._for_xml_id("gts_ticket_management.support_ticket_action_team")
        action['display_name'] = self.name
        return action

    @api.model
    def action_view_rating_today(self):
        return self.search(['|', ('member_ids', 'in', self._uid), ('member_ids', '=', False)])._action_view_rating(period='today', only_my_closed=True)

    @api.model
    def action_view_rating_7days(self):
        return self.search(['|', ('member_ids', 'in', self._uid), ('member_ids', '=', False)])._action_view_rating(period='seven_days', only_my_closed=True)

    def action_view_all_rating(self):
        return self._action_view_rating()

    @api.model
    def _compute_activity_avg(self, activity):
        great = activity['great'] * 5.00
        okey = activity['okay'] * 3.00
        bad = activity['bad'] * 0.00
        return great + okey + bad

    def _determine_user_to_assign(self):
        result = dict.fromkeys(self.ids, self.env['res.users'])
        for team in self:
            member_ids = sorted(team.member_ids.ids) if team.member_ids else sorted(team.visibility_member_ids.ids)
            if member_ids:
                if team.assign_method == 'randomly':
                    last_assigned_user = self.env['support.ticket'].search([('team_id', '=', team.id)], order='create_date desc, id desc', limit=1).user_id
                    index = 0
                    if last_assigned_user and last_assigned_user.id in member_ids:
                        previous_index = member_ids.index(last_assigned_user.id)
                        index = (previous_index + 1) % len(member_ids)
                    result[team.id] = self.env['res.users'].browse(member_ids[index])
                elif team.assign_method == 'balanced':
                    ticket_count_data = self.env['support.ticket'].read_group([('stage_id.is_close', '=', False), ('user_id', 'in', member_ids), ('team_id', '=', team.id)], ['user_id'], ['user_id'])
                    open_ticket_per_user_map = dict.fromkeys(member_ids, 0)
                    open_ticket_per_user_map.update((item['user_id'][0], item['user_id_count']) for item in ticket_count_data)
                    result[team.id] = self.env['res.users'].browse(min(open_ticket_per_user_map, key=open_ticket_per_user_map.get))
        return result

    def _determine_stage(self):
        result = dict.fromkeys(self.ids, self.env['support.ticket.stage'])
        for team in self:
            result[team.id] = self.env['support.ticket.stage'].search([('team_ids', 'in', team.id)], order='sequence', limit=1)
        return result

    def _get_closing_stage(self):
        closed_stage = self.stage_ids.filtered(lambda stage: stage.is_close)
        if not closed_stage:
            closed_stage = self.stage_ids[-1]
        return closed_stage


class SupportTicketStage(models.Model):
    _name = 'support.ticket.stage'
    _description = 'Support Tickets Stage'
    _order = 'sequence, id'

    def _default_team_ids(self):
        team_id = self.env.context.get('default_team_id')
        if team_id:
            return [(4, team_id, 0)]

    name = fields.Char('Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer('Sequence', default=10)
    is_close = fields.Boolean(
        'Closing Stage',
        help='Tickets in this stage are considered as done. This is used notably when '
             'computing SLAs and KPIs on tickets.')
    fold = fields.Boolean(
        'Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    team_ids = fields.Many2many(
        'support.team', relation='team_stage_rel', string='Team',
        default=_default_team_ids,
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    template_id = fields.Many2one(
        'mail.template', 'Email Template',
        domain="[('model', '=', 'support.ticket')]",
        help="Automated email sent to the ticket's customer when the ticket reaches this stage.")
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')

    def unlink(self):
        stages = self
        default_team_id = self.env.context.get('default_team_id')
        if default_team_id:
            shared_stages = self.filtered(lambda x: len(x.team_ids) > 1 and default_team_id in x.team_ids.ids)
            tickets = self.env['support.ticket'].with_context(active_test=False).search([('team_id', '=', default_team_id), ('stage_id', 'in', self.ids)])
            if shared_stages and not tickets:
                shared_stages.write({'team_ids': [(3, default_team_id)]})
                stages = self.filtered(lambda x: x not in shared_stages)
        return super(SupportTicketStage, stages).unlink()


class SupportSLA(models.Model):
    _name = "support.sla"
    _order = "name"
    _description = "Support Ticket SLA Policies"

    name = fields.Char('SLA Policy Name', required=True, index=True)
    description = fields.Text('SLA Policy Description')
    active = fields.Boolean('Active', default=True)
    team_id = fields.Many2one('support.team', 'Team', required=True)
    target_type = fields.Selection([('stage', 'Reaching Stage'), ('assigning', 'Assigning Ticket')], default='stage', required=True)
    ticket_type_id = fields.Many2one(
        'support.ticket.type', "Ticket Type",
        help="Only apply the SLA to a specific ticket type. If left empty it will apply to all types.")
    tag_ids = fields.Many2many(
        'support.ticket.tag', string='Tags',
        help="Only apply the SLA to tickets with specific tags. If left empty it will apply to all tags.")
    stage_id = fields.Many2one(
        'support.ticket.stage', 'Target Stage',
        help='Minimum stage a ticket needs to reach in order to satisfy this SLA.')
    exclude_stage_ids = fields.Many2many(
        'support.ticket.stage', string='Exclude Stages',
        compute='_compute_exclude_stage_ids', store=True, readonly=False, copy=True,
        domain="[('id', '!=', stage_id.id)]",
        help='The amount of time the ticket spends in this stage will not be taken into account when evaluating the status of the SLA Policy.')
    priority = fields.Selection(
        TICKET_PRIORITY, string='Minimum Priority',
        default='0', required=True,
        help='Tickets under this priority will not be taken into account.')
    company_id = fields.Many2one('res.company', 'Company', related='team_id.company_id', readonly=True, store=True)
    time_days = fields.Integer(
        'Days', default=0, required=True,
        help="Days to reach given stage based on ticket creation date")
    time_hours = fields.Integer(
        'Hours', default=0, inverse='_inverse_time_hours', required=True,
        help="Hours to reach given stage based on ticket creation date")
    time_minutes = fields.Integer(
        'Minutes', default=0, inverse='_inverse_time_minutes', required=True,
        help="Minutes to reach given stage based on ticket creation date")

    @api.depends('target_type')
    def _compute_exclude_stage_ids(self):
        self.update({'exclude_stage_ids': False})

    def _inverse_time_hours(self):
        for sla in self:
            sla.time_hours = max(0, sla.time_hours)
            if sla.time_hours >= 24:
                sla.time_days += sla.time_hours / 24
                sla.time_hours = sla.time_hours % 24

    def _inverse_time_minutes(self):
        for sla in self:
            sla.time_minutes = max(0, sla.time_minutes)
            if sla.time_minutes >= 60:
                sla.time_hours += sla.time_minutes / 60
                sla.time_minutes = sla.time_minutes % 60
