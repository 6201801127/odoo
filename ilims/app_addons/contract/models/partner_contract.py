from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class PartnerContract(models.Model):
    _name = 'partner.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'subject'
    _description = 'Contract'

    @api.depends('related_project', 'related_project.stakeholder_ids')
    def _compute_stakeholders_list(self):
        for record in self:
            partner_list = []
            if record.related_project and record.related_project.stakeholder_ids:
                for lines in record.related_project.stakeholder_ids:
                    if lines.status is True and lines.partner_id:
                        partner_list.append(lines.partner_id.id)
            record.stakeholders_ids = [(6, 0, [partner for partner in partner_list])]

    subject = fields.Char('Contract Subject', tracking=True)
    description = fields.Text('Contract Description', tracking=True)
    initiated_date = fields.Date('Initiated Date', default=fields.Datetime.now, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner', tracking=True)
    stakeholders_ids = fields.Many2many('res.partner', 'Stakeholders', compute='_compute_stakeholders_list')
    point_of_contact_from_client_id = fields.Many2one('res.partner', 'POC External', tracking=True)
    point_of_contact_from_us_id = fields.Many2one('res.partner', 'POC Internal', tracking=True)
    attach_draft_contract = fields.Binary('Attach Unsigned Contract', compute='_attachment_draft_contract',
                                          inverse='_set_draft_filename', copy=False, tracking=True)
    attach_draft_contract_filename = fields.Char('Attach Draft Contract',
                                          inverse='_set_draft_filename', copy=False, tracking=True)
    start_date = fields.Date('Contract Start Date', tracking=True)
    end_date = fields.Date('Contract End Date', tracking=True)
    contract_approved_by_client = fields.Many2one('res.partner', 'Approved by Client', tracking=True)
    contract_approved_by_ourside = fields.Many2one('res.partner', 'Approved by', tracking=True)
    attach_sign_contract = fields.Binary('Attach Signed Contract', compute='_attachment_sign_contract',
                                        inverse='_set_sign_filename', copy=False, tracking=True)
    attach_sign_contract_filename = fields.Char('Attach Signed Contract',
                                        inverse='_set_sign_filename', copy=False, tracking=True)
    related_project = fields.Many2one('project.project', 'Project', tracking=True)
    closure_reason = fields.Text('Closure Reason', tracking=True)
    closure_rejection_reason = fields.Text('Closure Rejection Reason', tracking=True)
    rejection_reason = fields.Text('Rejection Reason', tracking=True)
    contract_closed_by = fields.Many2one('res.users', 'Closed by', tracking=True)
    contract_requested_by = fields.Many2one('res.users', 'Approval Requested by', tracking=True)
    closure_requested_by = fields.Many2one('res.users', 'Requested to Close by', tracking=True)
    closure_rejected_by = fields.Many2one('res.users', 'Closure Rejected by', tracking=True)
    contract_rejected_by = fields.Many2one('res.users', 'Contract Rejected by', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('unsigned', 'Unsigned'),
        ('signed', 'Signed'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', tracking=True, group_expand='_expand_states')
    user_id = fields.Many2one('res.users', "User", default=lambda self: self.env.uid, tracking=True)
    draft_attachment_id = fields.Many2one('ir.attachment', tracking=True)
    sign_attachment_id = fields.Many2one('ir.attachment', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    is_request_to_close = fields.Boolean('Is Request to Close?')
    is_rejected = fields.Boolean('Is Rejected?')
    ir_attachment_ids = fields.One2many('ir.attachment', 'contract_id', 'Attachments', tracking=True)
    attach_unsigned_ids = fields.One2many('ir.attachment', 'unsigned_contract_id', 'Attached Unsigned Contracts', tracking=True)
    attach_signed_ids = fields.One2many('ir.attachment', 'signed_contract_id', 'Attached Signed Contracts', tracking=True)
    color = fields.Integer(string='Color Index', tracking=True)
    is_from_project = fields.Boolean('From Project')
    has_contract_create_group = fields.Boolean('Has contract create group', compute='_compute_contract_create')
    contract_rejection_ids = fields.One2many('contract.rejection.history', 'contract_id', 'Contract Rejection History')
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    approval_due_date = fields.Date('Approval Due Date', tracking=True)
    closure_due_date = fields.Date('Closure Due Date', tracking=True)
    activity_reminder_days = fields.Integer('Activity Days')
    close_activity_reminder_days = fields.Integer('Close Activity Days')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('related_project.allowed_user_ids', 'related_project.privacy_visibility')
    def _compute_allowed_user_ids(self):
        for task in self:
            portal_users = task.allowed_user_ids.filtered('share')
            internal_users = task.allowed_user_ids - portal_users
            if task.related_project.privacy_visibility == 'followers':
                task.allowed_user_ids |= task.related_project.allowed_internal_user_ids
                task.allowed_user_ids -= portal_users
            elif task.related_project.privacy_visibility == 'portal':
                task.allowed_user_ids |= task.related_project.allowed_portal_user_ids
            if task.related_project.privacy_visibility != 'portal':
                task.allowed_user_ids -= portal_users
            elif task.related_project.privacy_visibility != 'followers':
                task.allowed_user_ids -= internal_users

    @api.onchange('related_project')
    def onchange_related_project(self):
        if self.related_project:
            self.partner_id = self.related_project.partner_id.id

    @api.depends('related_project', 'related_project.stakeholder_ids')
    def _compute_contract_create(self):
        for record in self:
            record.has_contract_create_group = False
            if self.env.user.partner_id.id in record.stakeholders_ids.ids and self.env.user.has_group(
                    'contract.group_contract_creator'):
                record.has_contract_create_group = True

    @api.depends('attach_draft_contract')
    def _attachment_draft_contract(self):
        for data in self:
            val = data.draft_attachment_id.datas
            data.attach_draft_contract = val

    def _set_draft_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_draft_contract_filename or '',
            'datas': self.attach_draft_contract or '',
            'store_fname': self.attach_draft_contract_filename or '',
            'type': 'binary',
            'res_model': "partner.contract",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.draft_attachment_id = attachment.id

    @api.depends('attach_sign_contract')
    def _attachment_sign_contract(self):
        for data in self:
            val = data.sign_attachment_id.datas
            data.attach_sign_contract = val

    def _set_sign_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_sign_contract_filename or '',
            'datas': self.attach_sign_contract or '',
            'store_fname': self.attach_sign_contract_filename or '',
            'type': 'binary',
            'res_model': "partner.contract",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.sign_attachment_id = attachment.id

    def _attach_draft_contract_history(self):
        if self.attach_draft_contract:
            self.env['ir.attachment'].create(
                {'res_model': 'partner.contract', 'res_id': self._origin.id,
                 'name': self.attach_draft_contract_filename,
                 'datas': self.attach_draft_contract, 'unsigned_contract_id': self.id})

    def _attach_sign_contract_history(self):
        if self.attach_sign_contract:
            self.env['ir.attachment'].create(
                {'res_model': 'partner.contract', 'res_id': self._origin.id,
                 'name': self.attach_sign_contract_filename,
                 'datas': self.attach_sign_contract, 'signed_contract_id': self.id})

    @api.model
    def create(self, vals):
        rec = super(PartnerContract, self).create(vals)
        rec._attach_draft_contract_history()
        rec._attach_sign_contract_history()
        if rec.ir_attachment_ids:
            for lines in rec.ir_attachment_ids:
                lines.update({'res_model': 'partner.contract', 'res_id': rec.id})
            for lines in rec.attach_unsigned_ids:
                lines.update({'res_model': 'partner.contract', 'res_id': rec.id})
            for lines in rec.attach_signed_ids:
                lines.update({'res_model': 'partner.contract', 'res_id': rec.id})
        partner_list = []
        if rec.point_of_contact_from_client_id:
            partner_list.append(rec.point_of_contact_from_client_id.id)
        if rec.point_of_contact_from_us_id:
            partner_list.append(rec.point_of_contact_from_us_id.id)
        if rec.related_project:
            if rec.related_project.program_manager_id:
                partner_list.append(rec.related_project.program_manager_id.partner_id.id)
            if rec.related_project.user_id:
                partner_list.append(rec.related_project.user_id.partner_id.id)
        new_list = list(set(partner_list))
        rec.message_subscribe(partner_ids=new_list)
        return rec

    def write(self, vals):
        rec = super(PartnerContract, self).write(vals)
        if 'attach_draft_contract' in vals:
            self._attach_draft_contract_history()
        if 'attach_sign_contract' in vals:
            self._attach_sign_contract_history()
        if self.point_of_contact_from_client_id:
            self.message_subscribe(partner_ids=[self.point_of_contact_from_client_id.id])
        if self.point_of_contact_from_us_id:
            self.message_subscribe(partner_ids=[self.point_of_contact_from_us_id.id])
        return rec

    def button_approve(self):
        users_obj = self.env['res.users']
        user_list, notification_ids = '', []
        for user in users_obj.search([]):
            if user.has_group('contract.group_contract_approver'):
                if user.partner_id.email:
                    user_list += user.partner_id.email + ","
                else:
                    user_list += user.login + ","
                notification_ids.append((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'}))
        if self.contract_requested_by:
            if self.contract_requested_by.partner_id.email:
                user_list += self.contract_requested_by.partner_id.email + ","
            else:
                user_list += self.contract_requested_by.login + ","
            notification_ids.append((0, 0, {
                'res_partner_id': self.contract_requested_by.partner_id.id,
                'notification_type': 'inbox'}))
        action_id = self.env.ref('contract.view_partner_contract_form').id
        params = "web#id=%s&view_type=form&model=partner.contract&action=%s" % (self.id, action_id)
        contract_url = str(params)
        template = self.env.ref('contract.approved_email_template_contract')
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = user_list
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity = self.env['mail.activity'].search([('res_id', '=', self.id), ('res_model', '=', 'partner.contract'),
                                                     ('activity_type_id', '=',
                                                      self.env.ref('contract.contract_ask_for_approval').id)])
        message = 'Contract has been Approved by ' + str(self.env.user.partner_id.name)
        for rec in activity:
            rec._action_done(feedback=message, attachment_ids=False)
        self.message_post(body="Contract has been Approved by " + str(self.env.user.name),
                          message_type='notification', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids, notify_by_email=False)
        self.write({'contract_approved_by_ourside': self.env.user.partner_id.id, 'state': 'approved'})

    def button_send_by_email(self):
        self.ensure_one()
        template = self.env.ref('contract.email_template_send_contract')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='partner.contract',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            default_attachment_ids=[(4, self.draft_attachment_id.id)],
            force_email=True
        )
        self.write({'state': 'unsigned'})
        return {
            'name': ('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def button_signed(self):
        if not self.attach_sign_contract:
            raise ValidationError(_("Please attach Signed Contract!"))
        self.write({'state': 'signed'})

    def button_approve_to_close(self):
        user_list, notification_ids = '', []
        if self.closure_requested_by:
            if self.closure_requested_by.partner_id.email:
                user_list += self.closure_requested_by.partner_id.email + ","
            else:
                user_list += self.closure_requested_by.login + ","
            notification_ids.append((0, 0, {
                'res_partner_id': self.closure_requested_by.partner_id.id,
                'notification_type': 'inbox'}))
        if self.related_project.user_id != self.closure_requested_by:
            if self.related_project.user_id.partner_id.email:
                user_list += self.related_project.user_id.partner_id.email + ","
            else:
                user_list += self.related_project.user_id.login + ","
            notification_ids.append((0, 0, {
                'res_partner_id': self.related_project.user_id.partner_id.id,
                'notification_type': 'inbox'}))
        if self.message_follower_ids:
            for followers in self.message_follower_ids:
                if followers.partner_id.email not in user_list:
                    user_list += followers.partner_id.email + ","
                    notification_ids.append((0, 0, {
                        'res_partner_id': followers.partner_id.id,
                        'notification_type': 'inbox'}))
        action_id = self.env.ref('contract.view_partner_contract_form').id
        params = "web#id=%s&view_type=form&model=partner.contract&action=%s" % (self.id, action_id)
        contract_url = str(params)
        template = self.env.ref('contract.request_contract_closed_email')
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = user_list
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity = self.env['mail.activity'].search([('res_id', '=', self.id),
                                                     ('res_model', '=', 'partner.contract'),
                                                     ('activity_type_id', '=',
                                                      self.env.ref(
                                                          'contract.contract_requested_to_close').id)])
        message = "Contract Requested to Close has been Approved and Closed by " + str(
            self.closure_rejected_by.name)
        for rec in activity:
            rec._action_done(feedback=message, attachment_ids=False)
        self.message_post(body="Contract Requested to Close has been Approved by " + str(self.env.user.name),
                          message_type='notification', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids, notify_by_email=False)
        self.write({'contract_closed_by': self.env.uid, 'is_rejected': False, 'state': 'closed'})

    def send_contract_reminder_email(self):
        contract_obj = self.env['partner.contract']
        today_date = datetime.now().date()
        dates_list = []
        dt_1month_before = today_date + relativedelta(months=1)
        dt_15days_before = today_date + relativedelta(days=15)
        dt_1week_before = today_date + timedelta(weeks=1)
        dt_6days_left = today_date + timedelta(days=6)
        dates_list.append({'date': dt_6days_left, 'subject': '6 days left for your contract to get expire'})
        dt_5days_left = today_date + timedelta(days=5)
        dates_list.append({'date': dt_5days_left, 'subject': '5 days left for your contract to get expire'})
        dt_4days_left = today_date + timedelta(days=4)
        dates_list.append({'date': dt_4days_left, 'subject': '4 days left for your contract to get expire'})
        dt_3days_left = today_date + timedelta(days=3)
        dates_list.append({'date': dt_3days_left, 'subject': '3 days left for your contract to get expire'})
        dt_2days_left = today_date + timedelta(days=2)
        dates_list.append({'date': dt_2days_left, 'subject': '2 days left for your contract to get expire'})
        dt_1days_left = today_date + timedelta(days=1)
        dates_list.append({'date': dt_1days_left, 'subject': '1 day left for your contract to get expire'})

        contract_1month = contract_obj.search([('end_date', '=', dt_1month_before.strftime('%Y-%m-%d')),
                                               ('state', '=', 'signed')])
        contract_15days = contract_obj.search([('end_date', '=', dt_15days_before.strftime('%Y-%m-%d')),
                                               ('state', '=', 'signed')])
        contract_1week = contract_obj.search([('end_date', '=', dt_1week_before.strftime('%Y-%m-%d')),
                                              ('state', '=', 'signed')])
        contract_expired = contract_obj.search([('end_date', '=', today_date.strftime('%Y-%m-%d')),
                                                ('state', '=', 'signed')])
        # templates
        template_1month = self.env.ref('contract.mail_template_contract_1month_left')
        template_15days = self.env.ref('contract.mail_template_contract_15days_left')
        template_1week = self.env.ref('contract.mail_template_contract_1week_left')
        template_daily = self.env.ref('contract.mail_template_contract_daily')
        template_expired = self.env.ref('contract.mail_template_contract_expired')
        if contract_1month:
            for contract in contract_1month:
                if template_1month:
                    values = template_1month.generate_email(contract.id,
                                                            ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = contract.partner_id.email
                    values['email_from'] = 'admin'
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        if contract_15days:
            for contract in contract_15days:
                if template_1month:
                    values = template_15days.generate_email(contract.id,
                                                            ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = contract.partner_id.email
                    values['email_from'] = 'admin'
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        if contract_1week:
            for contract in contract_1week:
                if template_1week:
                    values = template_1week.generate_email(contract.id,
                                                           ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = contract.partner_id.email
                    values['email_from'] = 'admin'
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        for rec in dates_list:
            contract_daily = contract_obj.search([('end_date', '=', rec.get('date')), ('state', '=', 'signed')])
            if contract_daily:
                for contract in contract_daily:
                    if template_daily:
                        values = template_daily.generate_email(contract.id,
                                                               ['subject', 'email_to', 'email_from', 'body_html'])
                        values['email_to'] = contract.partner_id.email
                        values['email_from'] = 'admin'
                        values['body_html'] = values['body_html']
                        values['subject'] = rec.get('subject')
                        mail = self.env['mail.mail'].create(values)
                        try:
                            mail.send()
                        except Exception:
                            pass
        if contract_expired:
            for contract in contract_expired:
                if template_expired:
                    values = template_expired.generate_email(contract.id,
                                                             ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = contract.partner_id.email
                    values['email_from'] = 'admin'
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass

    @api.onchange('start_date', 'end_date')
    def _onchange_start_end_date(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('End date should be greater than the start date.'))

    def contract_activity_reminder(self):
        contract = self.env['partner.contract'].search([])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in contract:
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'partner.contract'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('contract.contract_ask_for_approval').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.related_project.outgoing_email:
                        notification_ids = []
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        template = self.env.ref('contract.contract_approval_activity_email_reminder')
                        action_id = self.env.ref('contract.view_partner_contract_form').id
                        params = str(base_url) + "web#id=%s&view_type=form&model=partner.contract&action=%s" % \
                                                 (record.id, action_id)
                        contract_url = str(params)
                        if template:
                            values = template.generate_email(record.id,
                                                                    ['subject', 'email_to', 'email_from',
                                                                     'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.related_project.outgoing_email
                            values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
                            mail = self.env['mail.mail'].create(values)
                            try:
                                mail.send()
                            except Exception:
                                pass
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        record.message_post(body="Reminder to Close Activity for Contract ("+str(record.subject)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'partner.contract'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('contract.contract_requested_to_close').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.close_activity_reminder_days and record.related_project.outgoing_email:
                        notification_ids = []
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        template = self.env.ref('contract.contract_approval_activity_email_reminder')
                        action_id = self.env.ref('contract.view_partner_contract_form').id
                        params = str(base_url) + "web#id=%s&view_type=form&model=partner.contract&action=%s" % \
                                                 (record.id, action_id)
                        contract_url = str(params)
                        if template:
                            values = template.generate_email(record.id,
                                                                    ['subject', 'email_to', 'email_from',
                                                                     'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.related_project.outgoing_email
                            values['body_html'] = values['body_html'].replace('_contract_url', contract_url)
                            mail = self.env['mail.mail'].create(values)
                            try:
                                mail.send()
                            except Exception:
                                pass
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        record.message_post(body="Reminder to Close Activity for Contract ("+str(record.subject)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)


class ContractRejectionHistory(models.Model):
    _name = 'contract.rejection.history'
    _order = 'create_date desc'

    contract_id = fields.Many2one('partner.contract', 'Contract')
    rejected_by = fields.Many2one('res.users', 'Rejected by')
    reason = fields.Text('Reason')


# class MailComposer(models.TransientModel):
#     _inherit = 'mail.compose.message'
#
#     def action_send_mail(self):
#         rec = super(MailComposer, self).action_send_mail()
#         if self.env.context.get('active_model') == 'partner.contract':
#             contract = self.env['partner.contract'].search([('id', '=', self.env.context.get('active_id'))])
#             if contract:
#                 contract.write({'state': 'unsigned'})
#         return rec


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    contract_id = fields.Many2one('partner.contract', 'Contract')
    unsigned_contract_id = fields.Many2one('partner.contract', 'Unsigned Contract')
    signed_contract_id = fields.Many2one('partner.contract', 'Signed Contract')
