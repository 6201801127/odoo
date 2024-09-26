from odoo import _, api, fields, models, tools
from odoo.osv import expression
from email.utils import getaddresses
from datetime import date, timedelta
# from odoo.exceptions import UserError
import random
import secrets
from ast import literal_eval
from odoo.tools.mimetypes import guess_mimetype
import base64
from odoo.exceptions import ValidationError


class WhistleBlowingTicket(models.Model):
    _name = 'kw_whistle_blowing'
    _description = 'Whistle Blowing Ticket'
    _rec_name = 'number'
    _order = 'priority desc, number desc'
    _mail_post_access = "read"
    _inherit = ['mail.activity.mixin', 'portal.mixin', 'mail.thread']

    def _get_default_stage_id(self):
        return self.env['grievance.ticket.stage'].search([], limit=1).id

    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee

    active = fields.Boolean(default=True)
    done_date = fields.Date()
    number = fields.Char(string='Grievance number', default="New",
                         readonly=True)
    name = fields.Char(string='Grievance Name')
    remarks_for_inprogress = fields.Text(string="In-progress Remarks", track_visibility='onchange')
    remarks_for_done = fields.Text('Close Remarks', track_visibility='onchange')
    remarks_for_awaiting = fields.Text('Awaiting Remarks', track_visibility='onchange')
    remarks_for_cancelled = fields.Text('Rejected Remarks', track_visibility='onchange')
    request = fields.Selection([('self', 'Self'), ('others', 'Others')], string="Request For", default='self')
    request_bool = fields.Boolean('fixed', compute='_compute_request')
    category_id = fields.Many2one('grievance.ticket.team',
                                  string='Category', required=True, domain=[('code', '=', 'WB')])
    sub_category = fields.Many2one(string="Sub Category", comodel_name='grievance.ticket.subcategory', required=True)
    attachment_type = fields.Selection(
        [('none', 'None'), ('attachment', 'Attachment'), ('url', 'URL'), ('video', 'Video'), ('audio', 'Audio')],
        default='none', tracking=True)
    attachment = fields.Binary(string='Attachment', attachment=True)
    url_attachment = fields.Text(string="Upload Attachment URL", tracking=True)
    video_attachment = fields.Binary(string='Upload Video', attachment=True, tracking=True)
    audio_attachment = fields.Binary(string='Upload Audio', attachment=True, tracking=True)
    file_name = fields.Char(string="File Name")
    duration = fields.Float(string='Resolution Duration')
    ticket_duration = fields.Float(string='Request Duration')
    hold_ticket_duration = fields.Float(string='Hold Duration')
    grievance_description = fields.Text('Description')
    word_limit = fields.Integer(string="Limit", default=100)
    user_id = fields.Many2one(
        'res.users',
        string='Assigned SPOC',
        track_visibility="onchange",
        index=True
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        related='team_id.user_ids',
        string='Users')
    approver_user_ids = fields.Many2many(
        comodel_name='res.users',
        column1='ticket_id',
        column2='user_id',
        relation='whistleblowing_user_approver_rel',
        string='New Users')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['grievance.ticket.stage'].search([])
        return stage_ids

    stage_id = fields.Many2one(
        'grievance.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id,
        track_visibility='onchange',
    )
    code = fields.Char(related='stage_id.code')
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char()
    partner_email = fields.Char()
    users_email = fields.Char(related="users_id.work_email", string='Employee Email', required=True)
    users_phone = fields.Char(related="users_id.mobile_phone",string='Employee Mobile', required=True)
    users_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True, readonly=True,
                               default=get_employee)
    emp_dept = fields.Char(related="users_id.department_id.name", string='Department', required=True)
    emp_desig = fields.Char(related="users_id.job_id.name", string='Designation ', required=True)
    forward_reason = fields.Text('Re-Assing remarks')
    last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now,
    )
    assigned_date = fields.Datetime(string='Assigned Date')
    closed_date = fields.Datetime(string='Closed Date')
    closed = fields.Boolean(related='stage_id.closed')
    unattended = fields.Boolean(related='stage_id.unattended', store=True)
    tag_ids = fields.Many2many('grievance.ticket.tag')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('kw_whistle_blowing')
    )
    channel_id = fields.Many2one(
        'grievance.ticket.channel',
        string='Channel',
        help='Channel indicates where the source of a ticket'
             'comes from (it could be a phone call, an email...)',
    )
    team_id = fields.Many2one('grievance.ticket.team')
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
    is_assign_ticket = fields.Boolean(compute="is_assign_ticket_check_compute")
    raised_by = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True,readonly=True, default=get_employee)

    @api.depends('user_id')
    def is_assign_ticket_check_compute(self):
        for record in self:
            if record.user_id.id:
                if self.env.user.has_group('kw_grievance_new.group_grievance_manager'):
                    record.is_assign_ticket = True
                elif record.user_id.id == self.env.user.id:
                    record.is_assign_ticket = True
                else:
                    record.is_assign_ticket = False

    @api.constrains('attachment')
    def _check_uploaded_document(self):
        allowed_file_list = ['application/pdf']
        if self.attachment:
            acp_size = ((len(self.attachment) * 3 / 4) / 1024) / 1024
            mimetype = guess_mimetype(base64.b64decode(self.attachment), default='application/pdf')
            if acp_size > 4:
                raise ValidationError("PDF Size Can't Exceed 4MB")

    @api.multi
    def name_get(self):
        result = []
        for ticket in self:
            name = "[%s] %s" % (ticket.number, ticket.category_id.name.name)
            result.append((ticket.id, name))
        return result

    @api.onchange('grievance_description')
    def _check_case_description(self):
        if self.grievance_description:
            self.word_limit = 500 - len(self.grievance_description)

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

    def assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def _compute_access_url(self):
        super(WhistleBlowingTicket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/grievance/%s' % (ticket.id)

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
        return self._notify_get_action_link('view')

    @api.multi
    def _notify_get_groups(self, message, groups):
        groups = super(WhistleBlowingTicket, self)._notify_get_groups(message, groups)
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
        if vals.get('number', 'New') == 'New':
            vals["number"] = self._prepare_ticket_number(vals)

        if vals.get("partner_id") and ("partner_name" not in vals or "partner_email" not in vals):
            partner = self.env["res.partner"].browse(vals["partner_id"])
            vals.setdefault("partner_name", partner.name)
            vals.setdefault("partner_email", partner.email)

        if self.env.context.get('fetchmail_cron_running') and not vals.get('channel_id'):
            vals['channel_id'] = self.env.ref('kw_grievance_new.grievance_ticket_channel_email').id
        res = super().create(vals)

        # Check if mail to the user has to be sent
        if (vals.get('partner_id') or vals.get('partner_email')) and res:
            res.send_partner_mail()
            if res.partner_id:
                res.message_subscribe(partner_ids=res.partner_id.ids)
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super(WhistleBlowingTicket, self).copy(default)
        return res

    @api.multi
    def write(self, vals):
        for ticket in self:
            now = fields.Datetime.now()
            if vals.get('stage_id'):
                stage_obj = self.env['grievance.ticket.stage'].browse(
                    [vals['stage_id']])
                vals['last_stage_update'] = now
                if stage_obj.closed:
                    vals['closed_date'] = now
            if vals.get('user_id'):
                vals['assigned_date'] = now

        return super(WhistleBlowingTicket, self).write(vals)

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_context(force_company=values["company_id"])
        return seq.next_by_code("whistleblow.ticket.sequence") or "/"

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(WhistleBlowingTicket, self)._track_template(tracking)
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
        data = self.category_id.sub_category_ids
        sub_category_data = []
        for rec in data:
            sub_category_data.append(rec.sub_category_id.id)
        return {'domain': {'sub_category': [('id', 'in', sub_category_data)]}}
    
    @api.depends('request')
    def _compute_request(self):
        for record in self:
            record.request_bool = record.request == 'self'
       
       
    @api.onchange('request')
    def _onchange_request(self):
        if self.request == 'others':
            self.users_id = False
            self.users_email = False
            self.emp_dept = False
            self.emp_desig = False
        else:
            employee = self.get_employee()
            if employee:
                self.users_id = employee.id
                self.users_email = employee.work_email
                self.emp_dept = employee.department_id.name
                self.emp_desig = employee.job_id.name

    def accept_ticket(self):
        stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'IP')], limit=1)
        self.stage_id = stage.id

    def assign_spoc_action(self):
        return {
            'name': self.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': "whistle.incident.wizard",
            'view_id': self.env.ref('kw_grievance_new.whistle_incident_wizard_form_view').id,
            # 'context': {'default_team_id': cat_id.id},
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def btn_take_action_view(self):
        form_view_id = self.env.ref('kw_grievance_new.kw_whistle_blowing_view_form').id
        for rec in self:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Grievance Take Action',
                'view_mode': 'form',
                'res_model': 'kw_whistle_blowing',
                'views': [(form_view_id, 'form')],
                'target': 'self',
                'res_id': rec.id,
                # 'flags'     : {'mode': 'edit', 'create': False, },
                'context': {'delete': False, 'edit': False, 'create': False},
            }
        return action

    def raise_whistleblowing_action(self):
        team_id = []
        random_team = 0
        team_member = []
        random_team_member = 0
        team = self.env['grievance.ticket.team'].sudo().search([('random_assign', '=', True)])
        for x in team:
            # print(x.code, x.name)
            if x.code == self.category_id.code:
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
        if random_team:
            self.team_id = random_team
            self.user_id = random_team_member



        admin = self.env['res.users'].sudo().search([])
        manager = admin.filtered(lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)

        if self.request == 'self':
            # res config user
            param = self.env['ir.config_parameter'].sudo()
            mail_group = literal_eval(param.get_param('kw_grievance_new.mail_to_users'))
            mail_to = []
            if mail_group:
                emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                mail_to += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
            email = ",".join(mail_to) or ''
            email_cc = ','.join(manager.mapped('email'))
            template = self.env.ref('kw_grievance_new.create_email_template_for_whistleblowing_ticket')
            email_cc = ','.join(manager.mapped('email'))

            template.with_context(email_to=self.users_email, email_cc=email, names=self.users_id.name).send_mail(
                self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            if random_team_member:
                template2 = self.env.ref('kw_grievance_new.email_template_assigned_whistle_ticket')
                template2.with_context(to_name=self.user_id.name, email_to=self.user_id.email,
                                    email_cc=email_cc).send_mail(
                    self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'N')], limit=1)
            self.stage_id = stage.id
        else:
            stage = self.env['grievance.ticket.stage'].sudo().search([('code', '=', 'N')], limit=1)
            self.stage_id = stage.id

    def grievance_ticket_auto_assign(self):
        data = self.env['kw_whistle_blowing'].sudo().search([('stage_id', 'in', [1, 2])])
        for rec in data:
            if rec.assigned_date and rec.create_date:
                cron_date = rec.assigned_date + timedelta(days=rec.category_id.escalation_days)
                if cron_date:
                    if date.today() >= cron_date.date() and rec.stage_id.id in [2, 1]:
                        random_emp_data = self.env['grievance.ticket.team'].sudo().search([('id', '=', rec.team_id.id)],
                                                                                          limit=1)
                        # lv2_emp = random.choice(random_emp_data.second_level_ids.ids)
                        lv2_emp = secrets.choice(random_emp_data.second_level_ids.ids)
                        rec.user_id = lv2_emp
                        rec.stage_id = 2
                        template = self.env.ref('kw_grievance_new.email_template_reassigned_ticket_grievance')
                        email_to = rec.user_id.email
                        to_name = rec.user_id.name
                        admin = self.env['res.users'].sudo().search([])
                        manager = admin.filtered(
                            lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
                        cc_email = ','.join(manager.mapped('email'))
                        template.with_context(email_to=email_to, to_name=to_name).send_mail(rec.id,
                                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            elif rec.create_date:
                if rec.create_date and not rec.assigned_date and rec.stage_id.id == 1:
                    cron_date = rec.create_date + timedelta(days=rec.category_id.escalation_days)
                    if cron_date:
                        if date.today() >= cron_date.date():
                            random_emp_data = self.env['grievance.ticket.team'].sudo().search(
                                [('name', '=', rec.category_id.name.id)], limit=1)
                            # lv2_emp = random.choice(random_emp_data.user_ids.ids)
                            lv2_emp = secrets.choice(random_emp_data.user_ids.ids)
                            rec.team_id = random_emp_data.id
                            rec.user_id = lv2_emp
                            rec.stage_id = 2
                            template = self.env.ref('kw_grievance_new.email_template_reassigned_ticket_grievance')
                            email_to = rec.user_id.email
                            to_name = rec.user_id.name
                            admin = self.env['res.users'].sudo().search([])
                            manager = admin.filtered(
                                lambda user: user.has_group('kw_grievance_new.group_grievance_manager') == True)
                            cc_email = ','.join(manager.mapped('email'))
                            template.with_context(email_to=email_to, to_name=to_name).send_mail(rec.id,
                                                                                                notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('take_action'):
            if self.env.user.has_group('kw_grievance_new.group_grievance_manager'):
                # print('---------------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>----------------1')
                args += [('stage_id', 'in', ['New', 'In Progress', 'Hold', 'Closed'])]
                # print(args)
            elif self.env.user.has_group('kw_grievance_new.group_grievance_user'):
                # print('---------------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>----------------2')
                args += [('stage_id', 'in', ['New', 'In Progress', 'Hold']), ('user_id', '=', self.env.user.id)]
                # print(args)
            else:
                # print('else runed------------->>>>>>>')
                args += [('stage_id', 'in', ['In Progress', 'Hold']), ('user_id', '=', self.env.user.id)]
                # print(args)
        return super(WhistleBlowingTicket, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                    access_rights_uid=access_rights_uid)

    @api.onchange('category_id')
    def get_category_id(self):
        # print('------------------------------------->>>>>>>>>')
        return {'domain': {'category_id': [('code', '=', 'WB')]}}