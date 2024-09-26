from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError, MissingError, AccessDenied
from datetime import date, datetime, timedelta


class ChangeRequest(models.Model):
    _name = 'change.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Change Request"
    _order = 'id desc'

    project_id = fields.Many2one('project.project', 'CR Project', track_visibility='always')
    cr_no = fields.Char('CR No.', tracking=True)
    name = fields.Char('CR Name', tracking=True)
    cr_date = fields.Date('CR Date', tracking=True)
    requested_by = fields.Many2one('res.partner', 'Requested by', tracking=True, default=False)
    approved_by = fields.Many2one('res.partner', 'Approved by', tracking=True)
    verified_by = fields.Many2one('res.partner', 'Verified by', tracking=True)
    attach_cr_document = fields.Binary('Attach CR Document', compute='_attachment_cr_document',
                                       inverse='_set_cr_document_filename', copy=False, track_visibility='always')
    attach_cr_document_filename = fields.Char('Attach CR Document', track_visibility='always')
    cr_document_attachment_id = fields.Many2one('ir.attachment', track_visibility='always')
    stakeholder_ids = fields.Many2many('res.partner', 'Stakeholders', compute='_get_stakeholder_project')
    cr_category = fields.Many2one('cr.category', string="CR Category", tracking=True)
    cr_reason = fields.Text('CR Reason', tracking=True)
    severity = fields.Selection([
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
    ], string='Severity', tracking=True)
    description = fields.Html('Description', tracking=True)
    planned_hours = fields.Float('Planned Hours', tracking=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.uid)
    task_id = fields.Many2one('project.task', 'Task', tracking=True)
    impact_on_project = fields.Text('CR Impact on Project', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        # ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, group_expand='_expand_states')
    closure_reason = fields.Text('Closure Reason', tracking=True)
    cr_closure_requested_by = fields.Many2one('res.users', 'Closure Requested by', tracking=True)
    cr_closed_by = fields.Many2one('res.users', 'Closed by', tracking=True)
    closure_rejected_reason = fields.Text('Closure Rejected Reason', tracking=True)
    rejected_reason = fields.Text('Rejected Reason', tracking=True)
    cr_rejected_by = fields.Many2one('res.users', 'Rejected by', tracking=True)
    cr_closure_rejected_by = fields.Many2one('res.users', 'Closure Rejected by', tracking=True)
    validated_by = fields.Many2one('res.users', 'Validated by', tracking=True) #need to remove
    cancelled_by = fields.Many2one('res.users', 'Cancelled by', tracking=True)
    ir_attachment_ids = fields.One2many('ir.attachment', 'change_request_id', 'Documents')
    is_request_to_close = fields.Boolean('Is Request to Close?')
    is_closure_rejected = fields.Boolean('Is Closure Rejected?')
    is_from_project = fields.Boolean('From Project')
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    approval_due_date = fields.Date('Approval Due Date', tracking=True)
    closure_due_date = fields.Date('Closure Due Date', tracking=True)
    cr_cost = fields.Float('CR Cost')
    activity_reminder_days = fields.Integer('Activity Days')
    close_activity_reminder_days = fields.Integer('Close Activity Days')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

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

    @api.depends('attach_cr_document')
    def _attachment_cr_document(self):
        for data in self:
            val = data.cr_document_attachment_id.datas
            data.attach_cr_document = val

    def _set_cr_document_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_cr_document_filename or '',
            'datas': self.attach_cr_document or '',
            'store_fname': self.attach_cr_document_filename or '',
            'type': 'binary',
            'res_model': "change.request",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.cr_document_attachment_id = attachment.id

    @api.depends('project_id', 'project_id.stakeholder_ids')
    def _get_stakeholder_project(self):
        for record in self:
            stakeholders_list, p_user = [], []
            if record.project_id and record.project_id.stakeholder_ids:
                for lines in record.project_id.stakeholder_ids:
                    if lines.status is True:
                        stakeholders_list.append(lines.partner_id)
                    user = self.env['res.users'].search([('partner_id', '=', lines.partner_id.id)], limit=1)
                    if user:
                        if user.id == self.env.user.id:
                            p_user.append(lines.partner_id.id)
            if self.env.user.has_group('gts_project_stages.group_project_manager_new'):
                self.stakeholder_ids = [(6, 0, [stakeholder.id for stakeholder in stakeholders_list])]
            else:
                record.stakeholder_ids = [(6, 0, p_user)]

    def action_verify(self):
        user_list, notification_ids = '', []
        if self.requested_by.id != self.env.user.partner_id.id:
            user_list += self.requested_by.email + ", "
            notification_ids.append((0, 0, {
                'res_partner_id': self.requested_by.id,
                'notification_type': 'inbox'}))
        if self.project_id.user_id:
            user_list += self.project_id.user_id.partner_id.email + ", "
            notification_ids.append((0, 0, {
                'res_partner_id': self.project_id.user_id.partner_id.id,
                'notification_type': 'inbox'}))
        if self.project_id.program_manager_id:
            user_list += self.project_id.program_manager_id.partner_id.email + ", "
            notification_ids.append((0, 0, {
                'res_partner_id': self.project_id.program_manager_id.partner_id.id,
                'notification_type': 'inbox'}))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('gts_change_request.action_change_request_view').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (self.id, action_id)
        cr_url = str(params)
        template = self.env.ref('gts_change_request.change_request_verified_email')
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = user_list
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        self.message_post(body="Change Request has been Verified",
                          message_type='notification', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids, notify_by_email=False)
        self.write({'verified_by': self.env.user.partner_id.id, 'state': 'verified'})

    def button_approved(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('gts_change_request.action_change_request_view').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (self.id, action_id)
        cr_url = str(params)
        template = self.env.ref('gts_change_request.change_request_approved_email')
        user_list = ''
        if self.requested_by.email:
            user_list += self.requested_by.email + ", "
        if self.project_id.user_id:
            user_list += self.project_id.user_id.partner_id.email + ", "
        if self.project_id.program_manager_id:
            user_list += self.project_id.program_manager_id.partner_id.email + ", "
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
            values['email_to'] = user_list
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity = self.env['mail.activity'].search([('res_id', '=', self.id), ('res_model', '=', 'change.request'),
                                                     ('activity_type_id', '=',
                                                      self.env.ref('gts_change_request.approve_change_request').id)])
        message = 'Change Request has been Approved by ' + str(self.env.user.name)
        for rec in activity:
            rec._action_done(feedback=message, attachment_ids=False)
        notification_ids = []
        for record in self:
            if record.project_id.user_id:
                notification_ids.append((0, 0, {
                    'res_partner_id': record.project_id.user_id.partner_id.id,
                    'notification_type': 'inbox'}))
            if record.project_id.program_manager_id:
                notification_ids.append((0, 0, {
                    'res_partner_id': record.project_id.program_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
            if record.requested_by:
                notification_ids.append((0, 0, {
                    'res_partner_id': record.requested_by.id,
                    'notification_type': 'inbox'}))
        self.message_post(body="Change Request has been Approved by " + str(self.env.user.name),
                          message_type='notification', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids, notify_by_email=False)
        self.write({'approved_by': self.env.user.partner_id.id, 'state': 'approved'})

    def button_approve_close(self):
        user_list, requested_by = '', ''
        notification_ids = []
        if self.cr_closure_requested_by:
            requested_by += self.cr_closure_requested_by.partner_id.email + "," \
                            or self.cr_closure_requested_by.login + ","
            notification_ids.append((0, 0, {
                'res_partner_id': self.cr_closure_requested_by.partner_id.id,
                'notification_type': 'inbox'
            }))
        if self.requested_by:
            requested_by += self.requested_by.email + ","
            notification_ids.append((0, 0, {
                'res_partner_id': self.requested_by.id,
                'notification_type': 'inbox'
            }))
        if self.project_id.user_id:
            notification_ids.append((0, 0, {
                'res_partner_id': self.project_id.user_id.partner_id.id,
                'notification_type': 'inbox'}))
        if self.project_id.program_manager_id:
            notification_ids.append((0, 0, {
                'res_partner_id': self.project_id.program_manager_id.partner_id.id,
                'notification_type': 'inbox'}))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('gts_change_request.action_change_request_view').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (self.id, action_id)
        cr_url = str(params)
        template = self.env.ref('gts_change_request.request_cr_closed_email')
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = requested_by
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        activity = self.env['mail.activity'].search([('res_id', '=', self.id), ('res_model', '=', 'change.request'),
                                                     ('activity_type_id', '=', self.env.ref(
                                                         'gts_change_request.requested_to_close_change_request').id)])
        message = 'Change Request has been Approved by ' + str(self.env.user.name) + ' and Closed Successfully'
        for rec in activity:
            rec._action_done(feedback=message, attachment_ids=False)
        self.message_post(body="Change Request Closure has been Approved by " + str(self.env.user.name),
                          message_type='notification', author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids, notify_by_email=False)
        self.write({'is_request_to_close': False, 'is_closure_rejected': False, 'cr_closed_by': self.env.uid,
                    'state': 'closed'})

    @api.model
    def create(self, vals):
        res = super(ChangeRequest, self).create(vals)
        # if 'planned_hours' in vals:
        #     if vals['planned_hours'] == 0.0:
        #         raise ValidationError(_('Planned hours should be greater then Zero.'))
        if res.ir_attachment_ids:
            for lines in res.ir_attachment_ids:
                lines.update({'res_model': 'change.request', 'res_id': res.id})
        partner_list = []
        if res.project_id:
            if res.project_id.program_manager_id:
                partner_list.append(res.project_id.program_manager_id.partner_id.id)
            if res.project_id.user_id:
                partner_list.append(res.project_id.user_id.partner_id.id)
        new_list = list(set(partner_list))
        res.message_subscribe(partner_ids=new_list)
        res.is_from_project = True
        return res

    # def write(self, vals):
    #     rec = super(ChangeRequest, self).write(vals)
    #     if self.planned_hours == 0.0:
    #         raise ValidationError(_('Planned hours should be greater then Zero.'))
    #     return rec

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        model_id = self.env['ir.model'].search([('model', '=', 'change.request')], limit=1)
        if model_id:
            server = self.env['fetchmail.server'].search([('object_id', '=', model_id.id)], limit=1)
            if server and server.fetch_key:
                if server.fetch_key in msg_dict.get('subject'):
                    return super(ChangeRequest, self).message_new(msg_dict, custom_values=None)

    def activity_reminder(self):
        change_request = self.env['change.request'].search([])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in change_request:
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'change.request'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('gts_change_request.approve_change_request').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('gts_change_request.action_change_request_view').id
                        params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (
                        record.id, action_id)
                        cr_url = str(params)
                        budget_template = self.env.ref('gts_change_request.approval_activity_email_reminder')
                        if budget_template:
                            values = budget_template.generate_email(record.id,
                                                                    ['subject', 'email_to', 'email_from',
                                                                     'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.project_id.outgoing_email
                            values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
                            mail = self.env['mail.mail'].create(values)
                            try:
                                mail.send()
                            except Exception:
                                pass
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        record.message_post(body="Reminder to Close Activity for Change Request ("+str(record.name)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'change.request'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('gts_change_request.requested_to_close_change_request').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.close_activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('gts_change_request.action_change_request_view').id
                        params = str(base_url) + "/web#id=%s&view_type=form&model=change.request&action=%s" % (
                        record.id, action_id)
                        cr_url = str(params)
                        budget_template = self.env.ref('gts_change_request.approval_activity_email_reminder')
                        if budget_template:
                            values = budget_template.generate_email(record.id,
                                                                    ['subject', 'email_to', 'email_from',
                                                                     'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.project_id.outgoing_email
                            values['body_html'] = values['body_html'].replace('_cr_url', cr_url)
                            mail = self.env['mail.mail'].create(values)
                            try:
                                mail.send()
                            except Exception:
                                pass
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        record.message_post(body="Reminder to Close Activity for Change Request ("+str(record.name)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user_id.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    change_request_id = fields.Many2one('change.request', 'Change Request')
