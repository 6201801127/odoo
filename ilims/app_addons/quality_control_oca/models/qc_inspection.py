# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools import formatLang
from odoo.exceptions import Warning, UserError, AccessError
from datetime import date, datetime, timedelta


class QcInspection(models.Model):
    _name = "qc.inspection"
    _description = "Quality Control Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends("inspection_lines", "inspection_lines.success")
    def _compute_success(self):
        for i in self:
            i.success = all([x.success for x in i.inspection_lines])

    def object_selection_values(self):
        """
        Overridable method for adding more object models to an inspection.
        :return: A list with the selection's possible values.
        """
        return [("product.product", "Product")]

    @api.depends("object_id")
    def _compute_product_id(self):
        for i in self:
            if i.object_id and i.object_id._name == "product.product":
                i.product_id = i.object_id
            else:
                i.product_id = False

    name = fields.Char(string="Inspection Number", required=True, default="/", readonly=True, copy=False,
                       tracking=True)
    date = fields.Date(string="Date", required=True, readonly=True, copy=False, tracking=True,
                       default=fields.Datetime.now, states={"draft": [("readonly", False)], "ready": [("readonly", False)],
                                                            "waiting": [("readonly", False)],
                                                            "rejected": [("readonly", False)]})
    object_id = fields.Reference(string="Reference", selection="object_selection_values", readonly=True,
                                 tracking=True, states={"draft": [("readonly", False)]},
                                 ondelete="set null")
    product_id = fields.Many2one(comodel_name="product.product", compute="_compute_product_id", store=True,
                                 tracking=True, help="Product associated with the inspection")
    qty = fields.Float(string="Quantity", readonly=True, tracking=True,
                       states={"draft": [("readonly", False)], "ready": [("readonly", False)]}, default=1.0)
    test = fields.Many2one(comodel_name="qc.test",
                           states={"draft": [("readonly", False)], "ready": [("readonly", False)]},
                           string="Quality Test", readonly=True, tracking=True)
    inspection_lines = fields.One2many(comodel_name="qc.inspection.line", inverse_name="inspection_id",
                                       string="Inspection lines", tracking=True)
    internal_notes = fields.Text(string="Internal notes", tracking=True)
    external_notes = fields.Text(string="External notes", tracking=True,
                                 states={"success": [("readonly", True)], "failed": [("readonly", True)]})
    state = fields.Selection([
        ("draft", "Draft"),
        ("ready", "Ready"),
        ("waiting", "Waiting for Approval"),
        ("rejected", "Rejected"),
        ("audit_in_progress", "Audit in Progress"),
        ("success", "Quality Success"),
        ("failed", "Quality Failed"),
    ], string="State", readonly=True, default="draft", tracking=True, group_expand='_expand_states')
    success = fields.Boolean(compute="_compute_success", string="Success",
                             help="This field will be marked if all tests have succeeded.", store=True, tracking=True)
    auto_generated = fields.Boolean(string="Auto-generated", readonly=True, copy=False, tracking=True,
                                    help="If an inspection is auto-generated, it can be canceled but not removed.")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True, tracking=True,
                                 states={"draft": [("readonly", False)]}, default=lambda self: self.env.company)
    user = fields.Many2one(comodel_name="res.users", string="Auditor", tracking=True, default=False)
    project_id = fields.Many2one('project.project', string='Project', tracking=True)
    project_stage_id = fields.Many2one('project.task.type', 'Project Stage', tracking=True)
    subject = fields.Char('Quality Subject', tracking=True)
    project_quality_definition = fields.Char('Project Quality Definition', readonly=True, tracking=True,
                                             states={"draft": [("readonly", False)], "ready": [("readonly", False)],
                                                     "waiting": [("readonly", False)], "rejected": [("readonly", False)]})
    deliverables_ids = fields.One2many('qc.inspection.deliverables', 'qc_inspection_id',
                                       'Deliverables and Acceptance Criteria', tracking=True)
    assurance_activity_ids = fields.One2many('qc.inspection.assurance', 'qc_inspection_id',
                                             'Deliverables and Acceptance Criteria', tracking=True)
    attach_qc_plan = fields.Binary('Attach Quality Plan', compute='_attachment_qc_plan', tracking=True,
                                   inverse='_set_qc_plan_filename', copy=False)
    attach_qc_plan_filename = fields.Char('Attach Quality Plan Filename', copy=False, tracking=True)
    plan_attachment_id = fields.Many2one('ir.attachment', tracking=True)
    attach_qc_report = fields.Binary('Attach Quality Report', compute='_attachment_qc_report',
                                     inverse='_set_qc_report_filename', copy=False, tracking=True)
    color = fields.Integer(string='Color Index', compute='_get_default_color')
    attach_qc_report_filename = fields.Char('Attach Quality Report Filename', copy=False, tracking=True)
    report_attachment_id = fields.Many2one('ir.attachment', tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Highest')
    ], 'Priority', required=True, default='0', tracking=True)
    is_from_project = fields.Boolean('From Project', tracking=True)
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    due_date = fields.Date('Approval Due Date', tracking=True)
    stakeholders_ids = fields.Many2many('res.users', compute='_compute_get_stakeholders')
    rejection_reason = fields.Char('Rejection Reason', tracking=True)
    quality_rejected_by = fields.Many2one('res.users', 'Rejected by', tracking=True)
    quality_approved_by = fields.Many2one('res.users', 'Approved by', tracking=True)
    quality_requested_by = fields.Many2one('res.users', 'Approval Requested by', tracking=True)
    activity_reminder_days = fields.Integer('Activity Days')
    inspection_team_id = fields.Many2one('qc.inspection.team', string='Inspection Team')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('project_id', 'project_id.stakeholder_ids')
    def _compute_get_stakeholders(self):
        users_obj = self.env['res.users']
        for record in self:
            partner_list, users, p_user = [], [], []
            if record.project_id and record.project_id.stakeholder_ids:
                for lines in record.project_id.stakeholder_ids:
                    if lines.status is True and lines.partner_id:
                        partner_list.append(lines.partner_id.id)
                        users = users_obj.search([('partner_id', 'in', partner_list),
                                                  ('groups_id', 'in', self.env.ref('gts_groups.group_quality_control_auditor').id)])
                        if users:
                            for user in users:
                                if user.id == self.env.user.id:
                                    p_user.append(user.id)
            if self.env.user.has_group('gts_project_stages.group_project_manager_new'):
                record.stakeholders_ids = [(6, 0, [user.id for user in users])]
            else:
                record.stakeholders_ids = [(6, 0, p_user)]

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

    @api.depends('state')
    def _get_default_color(self):
        for rec in self:
            if rec.state == 'success':
                rec.color = 10
            elif rec.state == 'failed':
                rec.color = 1
            else:
                rec.color = 0

    @api.depends('attach_qc_plan')
    def _attachment_qc_plan(self):
        for data in self:
            val = data.plan_attachment_id.datas
            data.attach_qc_plan = val

    def _set_qc_plan_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_qc_plan_filename or '',
            'datas': self.attach_qc_plan or '',
            'store_fname': self.attach_qc_plan_filename or '',
            'type': 'binary',
            'res_model': "qc.inspection",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.plan_attachment_id = attachment.id

    @api.depends('attach_qc_report')
    def _attachment_qc_report(self):
        for data in self:
            val = data.report_attachment_id.datas
            data.attach_qc_report = val

    def _set_qc_report_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_qc_report_filename or '',
            'datas': self.attach_qc_report or '',
            'store_fname': self.attach_qc_report_filename or '',
            'type': 'binary',
            'res_model': "qc.inspection",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.report_attachment_id = attachment.id

    @api.model_create_multi
    def create(self, val_list):
        for vals in val_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("qc.inspection")
        rec = super(QcInspection, self).create(val_list)
        partner_list = []
        if rec.project_id:
            if rec.project_id.program_manager_id:
                partner_list.append(rec.project_id.program_manager_id.partner_id.id)
            if rec.project_id.user_id:
                partner_list.append(rec.project_id.user_id.partner_id.id)
        new_list = list(set(partner_list))
        notification_ids = []
        if new_list:
            rec.message_subscribe(partner_ids=new_list)
            rec.message_post(partner_ids=new_list, body="Invited you to follow Quality Inspection")
            for partner in new_list:
                notification_ids.append((0, 0, {
                    'res_partner_id': partner,
                    'notification_type': 'inbox'}))
            rec.message_post(body="Invited you to follow Quality Inspection", message_type='notification',
                              subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids, notify_by_email=False)
        notification_ids = []
        # if rec.user:
        #     notification_ids.append((0, 0, {
        #         'res_partner_id': rec.user.partner_id.id,
        #         'notification_type': 'inbox'}))
        #     rec.message_post(body="Quality Inspection Assigned to you", message_type='notification',
        #                      subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
        #                      notification_ids=notification_ids)
        #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #     action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
        #     params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (rec.id, action_id)
        #     inspection_url = str(params)
        #     template = self.env.ref('quality_control_oca.quality_test_assigned_to_auditor')
        #     if template:
        #         values = template.generate_email(rec.id, ['subject', 'email_to', 'email_from', 'body_html'])
        #         values['email_to'] = rec.user.partner_id.email or rec.user.login
        #         values['email_from'] = self.env.user.partner_id.email or self.env.user.login
        #         values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
        #         mail = self.env['mail.mail'].create(values)
        #         try:
        #             mail.send()
        #         except Exception:
        #             pass
        rec.is_from_project = True
        return rec

    # def write(self, vals):
    #     rec = super(QcInspection, self).write(vals)
    #     notification_ids = []
    #     if 'user' in vals:
    #         notification_ids.append((0, 0, {
    #             'res_partner_id': self.user.partner_id.id,
    #             'notification_type': 'inbox'}))
    #         self.message_post(body="Quality Inspection Assigned to you", message_type='notification',
    #                          subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
    #                          notification_ids=notification_ids)
    #         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
    #         params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (self.id, action_id)
    #         inspection_url = str(params)
    #         template = self.env.ref('quality_control_oca.quality_test_assigned_to_auditor')
    #         if template:
    #             values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
    #             values['email_to'] = self.user.partner_id.email or self.user.login
    #             values['email_from'] = self.env.user.partner_id.email or self.env.user.login
    #             values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #             mail = self.env['mail.mail'].create(values)
    #             try:
    #                 mail.send()
    #             except Exception:
    #                 pass
    #     return rec

    def unlink(self):
        for inspection in self:
            if inspection.auto_generated:
                raise exceptions.UserError(
                    _("You cannot remove an auto-generated inspection.")
                )
            if inspection.state != "draft":
                raise exceptions.UserError(
                    _("You cannot remove an inspection that is not in draft state.")
                )
        return super().unlink()

    # def action_draft(self):
    #     self.write({"state": "draft"})

    def action_todo(self):
        users_obj = self.env['res.users'].search([])
        for inspection in self:
            if not inspection.test and not inspection.attach_qc_plan:
                raise exceptions.UserError(_("You must first set the Quality Test and attach the Quality Plan!"))
            if not inspection.test and inspection.attach_qc_plan:
                raise exceptions.UserError(_("You must first set the Quality Test to perform."))
            if not inspection.attach_qc_plan and inspection.test:
                raise exceptions.UserError(_("You must first attach the Quality Plan"))
            if any(lines.deadline is False for lines in inspection.inspection_lines):
                raise exceptions.UserError(_("Add Deadline in Questions before marking as Todo!"))
            # user_list = ''
            # for user in users_obj:
            #     if user.has_group('quality_control_oca.group_quality_control_manager'):
            #         user_list += user.partner_id.email + "," or user.login + ", "
            # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
            # params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (inspection.id, action_id)
            # inspection_url = str(params)
            # template = self.env.ref('quality_control_oca.quality_test_ready_for_evaluation_email')
            # if template:
            #     values = template.generate_email(inspection.id, ['subject', 'email_to', 'email_from', 'body_html'])
            #     values['email_to'] = user_list
            #     values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            #     values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
            #     mail = self.env['mail.mail'].create(values)
            #     try:
            #         mail.send()
            #     except Exception:
            #         pass
        self.write({"state": "ready"})

    # def action_confirm(self):
    #     users_obj = self.env['res.users'].search([])
    #     for inspection in self:
    #         for line in inspection.inspection_lines:
    #             if line.question_type == "qualitative" and not line.qualitative_value:
    #                 raise exceptions.UserError(_("You should provide answers for all the qualitative questions!"))
    #             if line.question_type != "qualitative" and not line.uom_id:
    #                 raise exceptions.UserError(_("You should provide a unit of measure for quantitative questions."))
    #             if not inspection.attach_qc_report:
    #                 raise exceptions.UserError(_("Please attach Quality Report!"))
    #         if inspection.success:
    #             inspection.state = "success"
    #             user_list = ''
    #             for user in users_obj:
    #                 if user.has_group('quality_control_oca.group_quality_control_manager'):
    #                     user_list += user.login + ","
    #             action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
    #             params = "web#id=%s&view_type=form&model=qc.inspection&action=%s" % (inspection.id, action_id)
    #             inspection_url = str(params)
    #             template = self.env.ref('quality_control_oca.quality_test_evaluation_confirmed_email')
    #             if template:
    #                 values = template.generate_email(inspection.id, ['subject', 'email_to', 'email_from', 'body_html'])
    #                 values['email_to'] = user_list
    #                 values['email_from'] = self.env.user.login
    #                 values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #                 mail = self.env['mail.mail'].create(values)
    #                 try:
    #                     mail.send()
    #                 except Exception:
    #                     pass
    #         else:
    #             if not inspection.due_date:
    #                 raise exceptions.UserError(_("Please enter due date!"))
    #             inspection.state = "waiting"
    #             user_list = ''
    #             for user in users_obj:
    #                 if user.has_group('quality_control_oca.group_quality_control_manager'):
    #                     user_list += user.login + ","
    #             action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
    #             params = "web#id=%s&view_type=form&model=qc.inspection&action=%s" % (inspection.id, action_id)
    #             inspection_url = str(params)
    #             template = self.env.ref('quality_control_oca.quality_test_evaluation_waiting_approval_email')
    #             if template:
    #                 values = template.generate_email(inspection.id, ['subject', 'email_to', 'email_from', 'body_html'])
    #                 values['email_to'] = user_list
    #                 values['email_from'] = self.env.user.login
    #                 values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #                 mail = self.env['mail.mail'].create(values)
    #                 try:
    #                     mail.send()
    #                 except Exception:
    #                     pass
    #             for user in users_obj:
    #                 if user.has_group('quality_control_oca.group_quality_control_manager'):
    #                     activity_dict = {
    #                         'res_model': 'qc.inspection',
    #                         'res_model_id': self.env.ref('quality_control_oca.model_qc_inspection').id,
    #                         'res_id': inspection.id,
    #                         'activity_type_id': self.env.ref('quality_control_oca.activity_quality_waiting_for_approval').id,
    #                         'date_deadline': inspection.due_date,
    #                         'summary': 'Quality Test Waiting for Approval',
    #                         'user_id': user.id
    #                     }
    #                     self.env['mail.activity'].create(activity_dict)

    def action_approve(self):
        users_obj = self.env['res.users'].search([])
        for inspection in self:
            inspection.state = 'audit_in_progress'
            # if inspection.success:
            #     inspection.state = "success"
            # else:
            #     inspection.state = "failed"
            user_list = ""
            notification_ids = []
            if self.quality_requested_by.id == self.user.id:
                user_list += self.user.partner_id.email + ", " or self.user.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.user.partner_id.id,
                    'notification_type': 'inbox'}))
            else:
                user_list += self.user.partner_id.email + ", " or self.user.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.user.partner_id.id,
                    'notification_type': 'inbox'}))
                user_list += self.quality_requested_by.partner_id.email + ", " or self.quality_requested_by.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': self.quality_requested_by.partner_id.id,
                    'notification_type': 'inbox'}))
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
            params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (inspection.id, action_id)
            inspection_url = str(params)
            template = self.env.ref('quality_control_oca.quality_test_evaluation_approved_email')
            if template:
                values = template.generate_email(inspection.id, ['subject', 'email_to', 'email_from', 'body_html'])
                values['email_to'] = user_list
                values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
            activity = self.env['mail.activity'].search(
                [('res_id', '=', inspection.id), ('res_model', '=', 'qc.inspection'),
                 ('activity_type_id', '=',
                  self.env.ref('quality_control_oca.activity_quality_waiting_for_approval').id)])
            message = 'Quality Inspection is Approved by ' + str(self.env.user.name)
            if activity:
                for rec in activity:
                    rec._action_done(feedback=message, attachment_ids=False)
            self.message_post(body="Quality Inspection Approved",
                              message_type='notification', author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids, notify_by_email=False)
            notification_ids = []
            if inspection.user:
                notification_ids.append((0, 0, {
                    'res_partner_id': inspection.user.partner_id.id,
                    'notification_type': 'inbox'}))
                inspection.message_post(body="Quality Inspection Assigned to you", message_type='notification',
                                 subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
                                 notification_ids=notification_ids, notify_by_email=False)
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
                params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (inspection.id, action_id)
                inspection_url = str(params)
                template = self.env.ref('quality_control_oca.quality_test_assigned_to_auditor')
                if template:
                    values = template.generate_email(inspection.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = inspection.user.partner_id.email or inspection.user.login
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass

    def action_close(self):
        for inspection in self:
            for line in inspection.inspection_lines:
                if line.question_type == "qualitative" and not line.qualitative_value:
                    raise UserError(_("You should provide answers for all the qualitative questions!"))
                if line.question_type != "qualitative" and not line.uom_id:
                    raise UserError(
                        _("You should provide a unit of measure for quantitative questions."))
            if inspection.success:
                inspection.state = "success"
            else:
                inspection.state = "failed"

    # def action_cancel(self):
    #     users_obj = self.env['res.users'].search([])
    #     user_list = ''
    #     for user in users_obj:
    #         if user.has_group('quality_control_oca.group_quality_control_manager'):
    #             if user.id != self.env.user.id:
    #                 user_list += user.login + ","
    #     action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
    #     params = "web#id=%s&view_type=form&model=qc.inspection&action=%s" % (self.id, action_id)
    #     inspection_url = str(params)
    #     template = self.env.ref('quality_control_oca.quality_test_evaluation_cancel_email')
    #     if template:
    #         values = template.generate_email(self.id,
    #                                          ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
    #         values['email_to'] = self.user.login
    #         values['email_from'] = self.env.user.login
    #         values['email_cc'] = user_list
    #         values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #         mail = self.env['mail.mail'].create(values)
    #         try:
    #             mail.send()
    #         except Exception:
    #             pass
    #     activity = self.env['mail.activity'].search(
    #         [('res_id', '=', self.id), ('res_model', '=', 'qc.inspection'),
    #          ('activity_type_id', '=',
    #           self.env.ref('quality_control_oca.activity_quality_waiting_for_approval').id)])
    #     message = 'Quality Test is Cancelled by ' + str(self.env.user.name)
    #     if activity:
    #         for rec in activity:
    #             rec._action_done(feedback=message, attachment_ids=False)
    #     self.write({"state": "canceled"})

    def set_test(self, trigger_line, force_fill=False):
        for inspection in self:
            header = self._prepare_inspection_header(inspection.object_id, trigger_line)
            del header["state"]  # don't change current status
            del header["auto_generated"]  # don't change auto_generated flag
            del header["user"]  # don't change current user
            inspection.write(header)
            inspection.inspection_lines.unlink()
            inspection.inspection_lines = inspection._prepare_inspection_lines(
                trigger_line.test, force_fill=force_fill
            )

    def _make_inspection(self, object_ref, trigger_line):
        """Overridable hook method for creating inspection from test.
        :param object_ref: Object instance
        :param trigger_line: Trigger line instance
        :return: Inspection object
        """
        inspection = self.create(
            self._prepare_inspection_header(object_ref, trigger_line)
        )
        inspection.set_test(trigger_line)
        return inspection

    def _prepare_inspection_header(self, object_ref, trigger_line):
        """Overridable hook method for preparing inspection header.
        :param object_ref: Object instance
        :param trigger_line: Trigger line instance
        :return: List of values for creating the inspection
        """
        return {
            "object_id": object_ref
                         and "{},{}".format(object_ref._name, object_ref.id)
                         or False,
            "state": "ready",
            "test": trigger_line.test.id,
            "user": trigger_line.user.id,
            "auto_generated": True,
        }

    def _prepare_inspection_lines(self, test, force_fill=False):
        new_data = []
        for line in test.test_lines:
            data = self._prepare_inspection_line(
                test, line, fill=test.fill_correct_values or force_fill
            )
            new_data.append((0, 0, data))
        return new_data

    def _prepare_inspection_line(self, test, line, fill=None):
        data = {
            "name": line.name,
            "test_line": line.id,
            "notes": line.notes,
            "min_value": line.min_value,
            "max_value": line.max_value,
            "test_uom_id": line.uom_id.id,
            "uom_id": line.uom_id.id,
            "question_type": line.type,
            "possible_ql_values": [x.id for x in line.ql_values],
        }
        if fill:
            if line.type == "qualitative":
                # Fill with the first correct value found
                for value in line.ql_values:
                    if value.ok:
                        data["qualitative_value"] = value.id
                        break
            else:
                # Fill with a value inside the interval
                data["quantitative_value"] = (line.min_value + line.max_value) * 0.5
        return data

    def qc_activity_reminder(self):
        qc_inspection = self.env['qc.inspection'].search([])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in qc_inspection:
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'qc.inspection'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('quality_control_oca.activity_quality_waiting_for_approval').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        template = self.env.ref('quality_control_oca.qc_approval_activity_email_reminder')
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        action_id = self.env.ref('quality_control_oca.action_qc_inspection').id
                        params = str(base_url) + "/web#id=%s&view_type=form&model=qc.inspection&action=%s" % (
                            record.id, action_id)
                        inspection_url = str(params)
                        if template:
                            values = template.generate_email(record.id,['subject', 'email_to', 'email_from',
                                                                        'body_html'])
                            values['email_to'] = rec.user_id.partner_id.email or rec.user_id.login
                            values['email_from'] = record.project_id.outgoing_email
                            values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
                            mail = self.env['mail.mail'].create(values)
                            try:
                                mail.send()
                            except Exception:
                                pass
                        notification_ids.append((0, 0, {
                            'res_partner_id': rec.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        record.message_post(body="Reminder to Close Activity for Quality ("+str(record.name)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)


class QcInspectionLine(models.Model):
    _name = "qc.inspection.line"
    _description = "Quality control inspection line"

    @api.depends(
        "question_type",
        "uom_id",
        "test_uom_id",
        "max_value",
        "min_value",
        "quantitative_value",
        "qualitative_value",
        "possible_ql_values",
    )
    def _compute_quality_test_check(self):
        for l in self:
            if l.question_type == "qualitative":
                l.success = l.qualitative_value.ok
            else:
                if l.uom_id.id == l.test_uom_id.id:
                    amount = l.quantitative_value
                else:
                    amount = self.env["uom.uom"]._compute_quantity(
                        l.quantitative_value, l.test_uom_id.id
                    )
                l.success = l.max_value >= amount >= l.min_value

    @api.depends(
        "possible_ql_values", "min_value", "max_value", "test_uom_id", "question_type"
    )
    def _compute_valid_values(self):
        for l in self:
            if l.question_type == "qualitative":
                answers = []
                # l.valid_values = ", ".join(
                #     [x.name for x in l.possible_ql_values if x.ok]
                # )
                for x in l.possible_ql_values:
                    if x.ok:
                        answers += [x.name + ' (' + str(x.weightage) + ')']
                        l.valid_values = ', '.join(answers)
            else:
                l.valid_values = "{} ~ {}".format(
                    formatLang(self.env, l.min_value),
                    formatLang(self.env, l.max_value),
                )
                if self.env.ref("uom.group_uom") in self.env.user.groups_id:
                    l.valid_values += " %s" % l.test_uom_id.name

    inspection_id = fields.Many2one(comodel_name="qc.inspection", string="Inspection", ondelete="cascade", tracking=True)
    name = fields.Char(string="Question", readonly=True, tracking=True)
    product_id = fields.Many2one(comodel_name="product.product", related="inspection_id.product_id", store=True, tracking=True)
    test_line = fields.Many2one(comodel_name="qc.test.question", string="Test question", readonly=True, tracking=True)
    possible_ql_values = fields.Many2many(comodel_name="qc.test.question.value", string="Answers", tracking=True)
    quantitative_value = fields.Float(string="Quantitative Value", digits="Quality Control",
                                      help="Value of the result for a quantitative question.", tracking=True)
    qualitative_value = fields.Many2one(comodel_name="qc.test.question.value", string="Qualitative Value",
                                        help="Value of the result for a qualitative question.",
                                        domain="[('id', 'in', possible_ql_values)]" , tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    min_value = fields.Float(string="Min", digits="Quality Control", readonly=True,
                             help="Minimum valid value for a quantitative question.", tracking=True)
    max_value = fields.Float(string="Max", digits="Quality Control", readonly=True,
                             help="Maximum valid value for a quantitative question.", tracking=True)
    test_uom_id = fields.Many2one(comodel_name="uom.uom", string="Test UoM", readonly=True,
                                  help="UoM for minimum and maximum values for a quantitative " "question.", tracking=True)
    test_uom_category = fields.Many2one(comodel_name="uom.category", related="test_uom_id.category_id", store=True, tracking=True)
    uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", domain="[('category_id', '=', test_uom_category)]",
                             help="UoM of the inspection value for a quantitative question.", tracking=True)
    question_type = fields.Selection([
        ("qualitative", "Qualitative"),
        ("quantitative", "Quantitative")
    ], string="Question Type", readonly=True, tracking=True)
    valid_values = fields.Char(string="Valid Values", store=True, compute="_compute_valid_values", tracking=True)
    success = fields.Boolean(compute="_compute_quality_test_check", string="Success?", store=True, tracking=True)
    deadline = fields.Date('Deadline', tracking=True)
    remarks = fields.Text('Remarks', tracking=True)
    weightage = fields.Float('Weightage', tracking=True)
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)

    def write(self, vals):
        prev_name = self.name
        prev_question_type = dict(self._fields['question_type'].selection).get(self.question_type)
        prev_quantitative_value = self.quantitative_value
        prev_qualitative_value = self.qualitative_value.name or ''
        prev_valid_values = self.valid_values
        prev_weightage = self.weightage
        prev_deadline = self.deadline or 'Null'
        prev_remarks = self.remarks or 'Empty'
        prev_success = self.success or 'Null'
        rec = super(QcInspectionLine, self).write(vals)
        message_body = """<b>Questions</b><br/>"""
        if prev_name == self.name:
            message_body += """• Question: {prev_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {name} <br/>""".format(
                prev_name=prev_name, name=self.name
            )
        else:
            message_body += """<span style='color:red;'>• Question: {prev_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {name}</span><br/>""".format(
                prev_name=prev_name, name=self.name
            )
        if prev_question_type == dict(self._fields['question_type'].selection).get(self.question_type):
            message_body += """• Question Type: {prev_question_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {question_type}<br/>""".format(
                prev_question_type=prev_question_type,
                question_type=dict(self._fields['question_type'].selection).get(self.question_type)
            )
        else:
            message_body += """<span style='color:red;'>• Question Type: {prev_question_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {question_type}</span><br/>""".format(
                prev_question_type=prev_question_type,
                question_type=dict(self._fields['question_type'].selection).get(self.question_type)
            )
        if prev_qualitative_value == '' and self.qualitative_value.name is False:
            message_body += """• Qualitative Value: {prev_qualitative_value} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {qualitative_value}<br/>""".format(
                prev_qualitative_value=prev_qualitative_value, qualitative_value=self.qualitative_value.name or ''
            )
        else:
            message_body += """<span style='color:red;'>• Qualitative Value: {prev_qualitative_value} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {qualitative_value}</span><br/>""".format(
                prev_qualitative_value=prev_qualitative_value, qualitative_value=self.qualitative_value.name or ''
            )
        if prev_quantitative_value == self.quantitative_value:
            message_body += """• Quantitative Value: {prev_quantitative_value} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {quantitative_value}<br/>""".format(
                prev_quantitative_value=prev_quantitative_value, quantitative_value=self.quantitative_value
            )
        else:
            message_body += """<span style='color:red;'>• Quantitative Value: {prev_quantitative_value} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {quantitative_value}</span><br/>""".format(
                prev_quantitative_value=prev_quantitative_value, quantitative_value=self.quantitative_value
            )
        if prev_valid_values == self.valid_values:
            message_body += """• Valid Values: {prev_valid_values} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {valid_values}<br/>""".format(
                prev_valid_values=prev_valid_values, valid_values=self.valid_values
            )
        else:
            message_body += """<span style='color:red;'>• Valid Values: {prev_valid_values} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {valid_values}</span><br/>""".format(
                prev_valid_values=prev_valid_values, valid_values=self.valid_values
            )
        if prev_weightage == self.weightage:
            message_body += """• Weightage: {prev_weightage} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {weightage}<br/>""".format(
                prev_weightage=prev_weightage, weightage=self.weightage
            )
        else:
            message_body += """<span style='color:red;'>• Weightage: {prev_weightage} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {weightage}</span><br/>""".format(
                prev_weightage=prev_weightage, weightage=self.weightage
            )
        if prev_deadline == self.deadline:
            message_body += """• Deadline: {prev_deadline} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {deadline}<br/>""".format(
                prev_deadline=prev_deadline, deadline=self.deadline or 'Null'
            )
        else:
            message_body += """<span style='color:red;'>• Deadline: {prev_deadline} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {deadline}</span><br/>""".format(
                prev_deadline=prev_deadline, deadline=self.deadline or 'Null'
            )
        if prev_remarks == self.remarks or 'Empty':
            message_body += """• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}<br/>""".format(
                prev_remarks=prev_remarks, remarks=self.remarks or 'Empty'
            )
        else:
            message_body += """<span style='color:red;'>• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}</span><br/>""".format(
                prev_remarks=prev_remarks, remarks=self.remarks or 'Empty'
            )
        if prev_success == self.success or 'Null':
            message_body += """• Success: {prev_success} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {success}""".format(
                prev_success=prev_success, success=self.success or 'Null'
            )
        else:
            message_body += """<span style='color:red;'>• Success: {prev_success} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {success}</span>""".format(
                prev_success=prev_success, success=self.success or 'Null'
            )
        # message_body = """<b>Questions</b><br/>
        #                 • Question: {prev_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {name} <br/>
        #                 • Question Type: {prev_question_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {question_type}<br/>
        #                 • Qualitative Value: {prev_qualitative_value} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {qualitative_value}<br/>
        #                 • Quantitative Value: {prev_quantitative_value} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {quantitative_value}<br/>
        #                 • Valid Values: {prev_valid_values} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {valid_values}<br/>
        #                 • Weightage: {prev_weightage} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {weightage}<br/>
        #                 • Deadline: {prev_deadline} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {deadline}<br/>
        #                 • Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}<br/>
        #                 • Success: {prev_success} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {success}"""\
        #     .format(prev_name=prev_name, name=self.name,
        #             prev_question_type=prev_question_type, question_type=dict(self._fields['question_type'].selection).get(self.question_type),
        #             prev_qualitative_value=prev_qualitative_value, qualitative_value=self.qualitative_value.name or '',
        #             prev_quantitative_value=prev_quantitative_value, quantitative_value=self.quantitative_value,
        #             prev_valid_values=prev_valid_values, valid_values=self.valid_values,
        #             prev_weightage=prev_weightage, weightage=self.weightage,
        #             prev_deadline=prev_deadline, deadline=self.deadline or 'Null',
        #             prev_remarks=prev_remarks, remarks=self.remarks or 'Empty',
        #             prev_success=prev_success , success=self.success or 'Null', )
        self.inspection_id.message_post(body=message_body)
        return rec

    @api.depends('inspection_id.project_id.allowed_user_ids', 'inspection_id.project_id.privacy_visibility')
    def _compute_allowed_user_ids(self):
        for task in self:
            portal_users = task.allowed_user_ids.filtered('share')
            internal_users = task.allowed_user_ids - portal_users
            if task.inspection_id.project_id.privacy_visibility == 'followers':
                task.allowed_user_ids |= task.inspection_id.project_id.allowed_internal_user_ids
                task.allowed_user_ids -= portal_users
            elif task.inspection_id.project_id.privacy_visibility == 'portal':
                task.allowed_user_ids |= task.inspection_id.project_id.allowed_portal_user_ids
            if task.inspection_id.project_id.privacy_visibility != 'portal':
                task.allowed_user_ids -= portal_users
            elif task.inspection_id.project_id.privacy_visibility != 'followers':
                task.allowed_user_ids -= internal_users

    @api.onchange('qualitative_value')
    def _onchange_qualitative_value(self):
        if self.qualitative_value:
            self.weightage = self.qualitative_value.weightage


class QcInspectionDeliverables(models.Model):
    _name = 'qc.inspection.deliverables'

    qc_inspection_id = fields.Many2one('qc.inspection', 'QC Inspection', tracking=True)
    deliverables = fields.Char('Deliverables', tracking=True)
    remarks = fields.Char('Remarks' , tracking=True)
    accept_criteria_situation = fields.Char('Acceptable Criteria/Acceptable Situation', tracking=True)

    def write(self, vals):
        prev_deliverables = self.deliverables
        prev_accept_criteria_situation = self.accept_criteria_situation
        prev_remarks = self.remarks
        rec = super(QcInspectionDeliverables, self).write(vals)
        message_body = """<b>Deliverables and Acceptable Criteria</b><br/>"""
        if prev_deliverables == self.deliverables:
            message_body += """• Deliverables: {prev_deliverables} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {deliverables} <br/>""".format(
                prev_deliverables=prev_deliverables, deliverables=self.deliverables
            )
        else:
            message_body += """<span style='color:red;'>• Deliverables: {prev_deliverables} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {deliverables} </span><br/>""".format(
                prev_deliverables=prev_deliverables, deliverables=self.deliverables
            )
        if prev_accept_criteria_situation == self.accept_criteria_situation:
            message_body += """• Acceptable Criteria/Acceptable Situation: {prev_accept_criteria_situation} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {accept_criteria_situation}<br/>""".format(
                prev_accept_criteria_situation=prev_accept_criteria_situation,
                accept_criteria_situation=self.accept_criteria_situation
            )
        else:
            message_body += """<span style='color:red;'>• Acceptable Criteria/Acceptable Situation: {prev_accept_criteria_situation} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {accept_criteria_situation}</span><br/>""".format(
                prev_accept_criteria_situation=prev_accept_criteria_situation,
                accept_criteria_situation=self.accept_criteria_situation
            )
        if prev_remarks == self.remarks:
            message_body += """• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}""".format(
                prev_remarks=prev_remarks, remarks=self.remarks
            )
        else:
            message_body += """<span style='color:red;'>• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}</span>""".format(
                prev_remarks=prev_remarks, remarks=self.remarks
            )
        # message_body = """<b>Deliverables and Acceptable Criteria</b><br/>
        #                         • Deliverables: {prev_deliverables} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {deliverables} <br/>
        #                         • Acceptable Criteria/Acceptable Situation: {prev_accept_criteria_situation} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {accept_criteria_situation}<br/>
        #                         • Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}""" \
        #     .format(prev_deliverables=prev_deliverables, deliverables=self.deliverables,
        #             prev_accept_criteria_situation=prev_accept_criteria_situation, accept_criteria_situation=self.accept_criteria_situation,
        #             prev_remarks=prev_remarks , remarks=self.remarks)
        self.qc_inspection_id.message_post(body=message_body)
        return rec



class QcInspectionAssurance(models.Model):
    _name = 'qc.inspection.assurance'

    qc_inspection_id = fields.Many2one('qc.inspection', 'QC Inspection', tracking=True)
    activity_name = fields.Char('Activity Name', tracking=True)
    remarks = fields.Char('Remarks', tracking=True)
    resource = fields.Char('Resource', tracking=True)

    def write(self, vals):
        prev_activity_name = self.activity_name
        prev_resource = self.resource
        prev_remarks = self.remarks
        rec = super(QcInspectionAssurance, self).write(vals)
        message_body = """<b>Quality Assurance Activities</b><br/>"""
        if prev_activity_name == self.activity_name:
            message_body += """• Activity Name: {prev_activity_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {activity_name} <br/>""".format(
                prev_activity_name=prev_activity_name, activity_name=self.activity_name
            )
        else:
            message_body += """<span style='color:red;'>• Activity Name: {prev_activity_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {activity_name} </span><br/>""".format(
                prev_activity_name=prev_activity_name, activity_name=self.activity_name
            )
        if prev_resource == self.resource:
            message_body += """• Resource: {prev_resource} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {resource}<br/>""".format(
                prev_resource=prev_resource, resource=self.resource
            )
        else:
            message_body += """<span style='color:red;'>• Resource: {prev_resource} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {resource}</span><br/>""".format(
                prev_resource=prev_resource, resource=self.resource
            )
        if prev_remarks == self.remarks:
            message_body += """• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}""".format(
                prev_remarks=prev_remarks, remarks=self.remarks
            )
        else:
            message_body += """<span style='color:red;'>• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}</span>""".format(
                prev_remarks=prev_remarks, remarks=self.remarks
            )
        # message_body = """<b>Quality Assurance Activities</b><br/>
        #                     • Activity Name: {prev_activity_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {activity_name} <br/>
        #                     • Resource: {prev_resource} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {resource}<br/>
        #                     • Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}""" \
        #     .format(prev_activity_name=prev_activity_name, activity_name=self.activity_name,
        #             prev_resource=prev_resource, resource=self.resource,
        #             prev_remarks=prev_remarks , remarks=self.remarks)
        self.qc_inspection_id.message_post(body=message_body)
        return rec
