"""
Module for Custom Odoo Models and Utilities.

This module contains custom models, fields, and utilities for various functionalities in Odoo.

"""
from odoo import _, api, fields, models, tools
from odoo.osv import expression
from email.utils import getaddresses
from datetime import datetime, date
from odoo.exceptions import UserError
import random
import secrets
from ast import literal_eval
import datetime

class HelpdeskTicket(models.Model):
    """
    This class represents the model for managing helpdesk tickets in Odoo.
    """
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _rec_name = 'number'
    _order = 'priority desc, number desc'
    _mail_post_access = "read"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def _get_default_stage_id(self):
        """Get the default stage ID for new tickets."""
        return self.env['helpdesk.ticket.stage'].search([], limit=1).id

    active = fields.Boolean(default=True)
    done_date = fields.Date()
    number = fields.Char(string='Ticket number', default="New",
                         readonly=True)
    name = fields.Char(string='Issue Name', required=True)
    remarks_for_inprogress = fields.Text(string="In-progress Remarks", track_visibility='onchange')
    remarks_for_done = fields.Text('Done Remarks', track_visibility='onchange')
    remarks_for_awaiting = fields.Text('Awaiting Remarks', track_visibility='onchange')
    remarks_for_cancelled = fields.Text('Cancelled Remarks', track_visibility='onchange')
    request = fields.Selection([('self', 'Self'), ('others', 'Others')], string="Request For", default='self')
    request_bool = fields.Boolean('fixed', compute='_compute_request')
    call_type_id = fields.Many2one(comodel_name="helpdesk.calltype.master", string="Call Type", required=True)
    category_id = fields.Many2one('helpdesk.ticket.category',
                                  string='Category', required=True)
    sub_category = fields.Many2one(string="Sub Category", comodel_name='helpdesk.ticket.subcategory', required=True)
    attachment = fields.Binary('Attachment')
    # task_timer = fields.Boolean()
    # is_user_working = fields.Boolean(string='Is Current User Working') #compute='_compute_is_user_working'
    duration = fields.Float(string='Resolution Duration')
    ticket_duration = fields.Float(string='Request Duration')
    hold_ticket_duration = fields.Float(string='Hold Duration')
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        'res.users',
        string='Team Members',
        track_visibility="onchange",
        index=True
    )

    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')

    approver_user_ids = fields.Many2many(
        comodel_name='res.users',
        column1 ='ticket_id',
        column2 ='user_id',
        relation='ticket_user_approver_rel',
        string='New Users')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['helpdesk.ticket.stage'].search([])
        return stage_ids

    stage_id = fields.Many2one(
        'helpdesk.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )
    code = fields.Char(related='stage_id.code')
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char()
    partner_email = fields.Char()
    users_email = fields.Char(string='Employee Email', required=True)
    users_id = fields.Many2one(comodel_name='res.users', string='Employee', required=True)
    forward_reason = fields.Text('Re-Assing remarks')
    # user_id = fields.Many2one('res.users')

    last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now,
    )
    assigned_date = fields.Datetime(string='Assigned Date')
    closed_date = fields.Datetime(string='Closed Date')
    closed = fields.Boolean(related='stage_id.closed')
    unattended = fields.Boolean(related='stage_id.unattended', store=True)
    tag_ids = fields.Many2many('helpdesk.ticket.tag')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
    )
    channel_id = fields.Many2one(
        'helpdesk.ticket.channel',
        string='Channel',
        help='Channel indicates where the source of a ticket'
             'comes from (it could be a phone call, an email...)',
    )

    team_id = fields.Many2one('helpdesk.ticket.team')
    priority = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Very High')),
    ], string='Priority', default='1')
    color = fields.Integer(string='Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Default'),
        ('done', 'Ready for next stage'),
        ('blocked', 'Blocked')], string='Kanban State')

    # sequence = fields.Integer(
    #     string='Sequence', index=True, default=10,
    #     help="Gives the sequence order when displaying a list of tickets.")
    is_assign_ticket = fields.Boolean(compute="is_assign_ticket_check_compute")
    ticket_end_date = fields.Boolean(string="Close Date")

    def invisible_re_open_ticket(self):
        data = self.env['helpdesk.ticket'].sudo().search([('stage_id.name', '=', 'Done')])
        for rec in data:
            if rec.closed_date:
                ex_date = rec.closed_date + datetime.timedelta(days=3)
                # print(ex_date.date())
                # print(date.today())
                if date.today() >= ex_date.date():
                    # print(date.today() >= ex_date.date())
                    rec.ticket_end_date = True
                else:
                    rec.ticket_end_date = False


    @api.depends('user_id')
    def is_assign_ticket_check_compute(self):
        for record in self:
            if record.user_id.id:
                if self.env.user.has_group('helpdesk_mgmt.group_helpdesk_manager'):
                    record.is_assign_ticket = True
                elif self.env.user.has_group('helpdesk_mgmt.group_helpdesk_officer'):
                    record.is_assign_ticket = True
                elif record.user_id.id == self.env.user.id:
                    record.is_assign_ticket = True
                else:
                    record.is_assign_ticket = False

    @api.multi
    def name_get(self):
        result = []
        for ticket in self:
            name = "[%s] %s" % (ticket.number, ticket.name)
            result.append((ticket.id, name))
        return result

    @api.model
    def _name_search(
            self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('number', operator, name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = domain[1:]
        ticket_ids = self._search(
            expression.AND([domain, args]), limit=limit,
            access_rights_uid=name_get_uid)
        return self.browse(ticket_ids).name_get()

    # def send_user_mail(self):
    #     self.env.ref('helpdesk_mgmt.assignment_email_template'). \
    #         send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light", force_send=True)

    # def send_partner_mail(self):
    #     self.env.ref('helpdesk_mgmt.created_ticket_template'). \
    #         send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light", force_send=True)

    def assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def _compute_access_url(self):
        super(HelpdeskTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/ticket/%s' % (ticket.id)

    def partner_can_access(self):
        if not self.partner_id:
            return False
        user = self.env['res.users'].sudo().search([
            ('partner_id', '=', self.partner_id.id)])
        if not user:
            return False
        if not self.sudo(user.id).check_access_rights('read', raise_exception=False):
            return False
        else:
            return True

    def get_access_link(self):
        # _notify_get_action_link is not callable from email template
        return self._notify_get_action_link('view')

    @api.multi
    def _notify_get_groups(self, message, groups):
        groups = super(HelpdeskTicket, self)._notify_get_groups(message, groups)
        self.ensure_one()
        for group_name, group_method, group_data in groups:
            if group_name == 'portal':
                group_data['has_button_access'] = True
        return groups

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    @api.onchange('users_id')
    def _onchange_users_id(self):
        if self.users_id:
            self.users_email = self.users_id.email

    @api.multi
    @api.onchange('team_id', 'user_id')
    def _onchange_dominion_user_id(self):
        if self.user_id:
            if self.user_id and self.user_ids and \
                    self.user_id not in self.user_ids:
                self.update({
                    'user_id': False
                })
                return {'domain': {'user_id': []}}
        if self.team_id:
            return {'domain': {'user_id': [('id', 'in', self.user_ids.ids)]}}
        else:
            return {'employee_idsdomain': {'user_id': []}}

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    @api.model
    def create(self, vals):
        cat_id = vals.get('category_id')
        cat_master = self.env['helpdesk.ticket.category'].sudo().search([('id','=',cat_id)],limit=1)
        team_rec =cat_master.team
        team_id = []
        random_team = 0
        team_member = []
        random_team_member = 0
        team = self.env['helpdesk.ticket.team'].sudo().search([('random_assign', '=', True)])
        for x in team:
            if x == team_rec:
                team_id.append(x.id)
            else:
                pass
        if len(team_id) > 0:
            # random_team += random.choice(team_id)
            random_team += secrets.choice(team_id)
        member = team.search([('id', '=', random_team)])
        for x in member.user_ids:
            team_member.append(x.id)
        if len(team_member) > 0:
            # random_team_member += random.choice(team_member)
            random_team_member += secrets.choice(team_member)
        if vals.get('number', 'New') == 'New':
            vals["number"] = self._prepare_ticket_number(vals)

        if vals.get("partner_id") and ("partner_name" not in vals or "partner_email" not in vals):
            partner = self.env["res.partner"].browse(vals["partner_id"])
            vals.setdefault("partner_name", partner.name)
            vals.setdefault("partner_email", partner.email)

        if self.env.context.get('fetchmail_cron_running') and not vals.get('channel_id'):
            vals['channel_id'] = self.env.ref('helpdesk_mgmt.helpdesk_ticket_channel_email').id

        if random_team:
            vals["team_id"] = random_team
            vals["user_id"] = random_team_member
        res = super().create(vals)

        # Check if mail to the user has to be sent
        if (vals.get('partner_id') or vals.get('partner_email')) and res:
            res.send_partner_mail()
            if res.partner_id:
                res.message_subscribe(partner_ids=res.partner_id.ids)

        admin = self.env['res.users'].sudo().search([])
        manager = admin.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager') == True)

        # res config user
        param = self.env['ir.config_parameter'].sudo()
        mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user') or '[]')
        mail_to = []
        if mail_group:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
        email = ",".join(mail_to) or ''

        template = self.env.ref('helpdesk_mgmt.create_email_template_for_ticket')
        email_cc = ','.join(manager.mapped('email'))

        template.with_context(email_from=res.users_email, email_to=email, names=res.users_id.name, email_cc=email).send_mail(
            res.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        if random_team_member:
            template2 = self.env.ref('helpdesk_mgmt.email_template_assigned_ticket')
            template2.with_context(to_name=res.user_id.name, email_to=res.user_id.email, email_from=email_cc, email_cc=email).send_mail(
                res.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super(HelpdeskTicket, self).copy(default)
        return res

    @api.multi
    def write(self, vals):
        for ticket in self:
            now = fields.Datetime.now()
            if vals.get('stage_id'):
                stage_obj = self.env['helpdesk.ticket.stage'].browse(
                    [vals['stage_id']])
                vals['last_stage_update'] = now
                if stage_obj.closed:
                    vals['closed_date'] = now
            if vals.get('user_id'):
                vals['assigned_date'] = now

        return super(HelpdeskTicket, self).write(vals)

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_context(force_company=values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(HelpdeskTicket, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value = tracking[test_task.id]
        if "stage_id" in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id,
                               {"composition_mode": "mass_mail"})

        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': msg.get('body'),
            'partner_id': msg.get('author_id')
        }
        res = getaddresses([msg.get('from', '')])
        if res:
            defaults['partner_name'] = res[0][0]
            defaults['partner_email'] = res[0][1]
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        partner_ids = [p for p in ticket._find_partner_from_emails(email_list, force_create=False) if p]
        ticket.message_subscribe(partner_ids)
        return ticket

    @api.multi
    def message_update(self, msg, update_vals=None):
        """ Override message_update to subscribe partners """
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        partner_ids = [p for p in self._find_partner_from_emails(email_list, force_create=False) if p]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients()

        for ticket in self:
            reason = _('Partner Email') \
                if ticket.partner_id and ticket.partner_id.email \
                else _('Partner Id')

            if ticket.partner_id and ticket.partner_id.email:
                ticket._message_add_suggested_recipient(
                    recipients,
                    partner=ticket.partner_id,
                    reason=reason
                )
            elif ticket.partner_email:
                ticket._message_add_suggested_recipient(
                    recipients,
                    email=ticket.partner_email,
                    reason=reason
                )
        return recipients

    @api.onchange('category_id')
    def onchange_category_id(self):
        for rec in self:
            cat_id = {'domain': {'sub_category': [('category_code_id', '=', rec.category_id.id)]}}
            assign_cat = self.env['helpdesk.ticket.subcategory'].search([('category_code_id', '=', self.category_id.id)])
            if assign_cat:
                # rec.sub_category = random.choice(assign_cat)
                rec.sub_category = secrets.choice(assign_cat)
            return cat_id
    @api.depends('request')
    def _compute_request(self):
        for rec in self:
            if rec.request == 'self':
                rec.request_bool = True
            elif rec.request == 'others':
                rec.request_bool = True
            else:
                rec.request_bool = False

    @api.onchange('request', )
    def _onchange_request(self):
        if self.request == 'others':
            self.users_id = False
            self.users_email = False
        else:
            user = self.env['res.users'].search([('name', '=', self.env.user.name)], limit=1)
            self.users_id = user

    @api.model
    def get_timer_state(self, args):
        help_tckt = self.search([('id', '=', args)])
        return [help_tckt.stage_id.name, help_tckt.duration]

    @api.model
    def save_timer_time(self, args):
        if self:
            for rec in self:
                help_tckt = rec.search([('id', '=', args[0])])
                help_tckt.duration = args[1]
        else:
            help_tckt = self.search([('id', '=', args[0])])
            # print(args[1])
            help_tckt.duration = args[1]
        return help_tckt.duration

    @api.model
    def save_new_timer_time(self, args):
        if self:
            for rec in self:
                help_tckt = rec.search([('id', '=', args[0])])
                help_tckt.ticket_duration = args[1]
        else:
            help_tckt = self.search([('id', '=', args[0])])
            help_tckt.ticket_duration = args[1]

    @api.model
    def get_timer_state_new(self, args):
        help_tckt = self.search([('id', '=', args)])
        return [help_tckt.stage_id.name, help_tckt.ticket_duration]

    @api.model
    def save_hold_timer_time(self, args):
        if self:
            for rec in self:
                help_tckt = rec.search([('id', '=', args[0])])
                help_tckt.hold_ticket_duration = args[1]
        else:
            help_tckt = self.search([('id', '=', args[0])])
            help_tckt.hold_ticket_duration = args[1]

    @api.model
    def get_timer_state_hold(self, args):
        help_tckt = self.search([('id', '=', args)])
        return [help_tckt.stage_id.name, help_tckt.hold_ticket_duration]

    def action_re_open(self):
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('code', '=', 'N')], limit=1)
        self.stage_id = stage.id

    def update_timer_from_cron(self):
        self_rec = self.env['helpdesk.ticket'].sudo().search([('stage_id.name', '=', 'New')])
        user = self.env['res.users'].sudo().search([])
        # manager = user.filtered(lambda user: user.has_group('helpdesk_mgmt.group_helpdesk_manager') == True)
        # employee_email = self.env.user
        # to_email = ','.join(manager.mapped('email'))
        # user_name = ','.join(manager.mapped('name'))
        # res config user
        param = self.env['ir.config_parameter'].sudo()
        mail_group = literal_eval(param.get_param('helpdesk_mgmt.mail_to_user') or '[]')
        mail_to = []
        if mail_group:
            emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
            mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email = ",".join(mail_to) or ''
            user_name = ','.join(emp.mapped('name'))

        if self_rec:
            for rec in self_rec:
                if not rec.user_id:
                    template = self.env.ref('helpdesk_mgmt.email_template_for_timer')
                    template.with_context(email_to=email,names=user_name).send_mail(rec.id,
                                                                                    notif_layout="kwantify_theme.csm_mail_notification_light")

    def archive_ticket_from_cron(self):
        self_rec = self.env['helpdesk.ticket'].sudo().search([('stage_id.name', '=', 'Done')])
        # print('self_rec', self_rec)
        if self_rec:
            for rec in self_rec:
                if rec.done_date:
                    # print('done_date', rec.done_date, date.today(), date.today().day - rec.done_date.day)
                    if (date.today() - rec.done_date).days + 1 >= 3:
                        rec.active = False

    def accept_ticket(self):
        stage = self.env['helpdesk.ticket.stage'].sudo().search([('code', '=', 'IP')], limit=1)
        self.stage_id = stage.id
