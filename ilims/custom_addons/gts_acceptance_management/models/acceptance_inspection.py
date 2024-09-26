from odoo import _, api, exceptions, fields, models
from odoo.tools import formatLang
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class AcceptanceInspection(models.Model):
    _name = "acceptance.inspection"
    _description = "Acceptance Inspection"
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

    name = fields.Char(string="Number", required=True, default="/", readonly=True, copy=False,
                       tracking=True)
    date = fields.Date(string="Date", required=True, readonly=True, copy=False, tracking=True,
                       default=fields.Datetime.now)
    object_id = fields.Reference(string="Reference", selection="object_selection_values", readonly=True,
                                 tracking=True, ondelete="set null")
    product_id = fields.Many2one(comodel_name="product.product", compute="_compute_product_id", store=True,
                                 tracking=True, help="Product associated with the inspection")
    qty = fields.Float(string="Quantity", readonly=True, tracking=True, default=1.0)
    check_list = fields.Many2one(comodel_name="acceptance.checklist", string="Acceptance Criteria", readonly=True,
                                 tracking=True)
    inspection_lines = fields.One2many(comodel_name="acceptance.inspection.line", inverse_name="inspection_id",
                                       string="Inspection lines", tracking=True)
    internal_notes = fields.Text(string="Internal notes", tracking=True)
    external_notes = fields.Text(string="External notes", tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("ready", "Ready"),
        ("waiting_for_approval", "Waiting for Approval"),
        ("success", "Accepted"),
        ("failed", "Not Accepted"),
    ], string="State", readonly=True, default="draft", tracking=True, group_expand='_expand_states')
    success = fields.Boolean(compute="_compute_success", string="Success",
                             help="This field will be marked if all criteria have succeeded.", store=True)
    auto_generated = fields.Boolean(string="Auto-generated", readonly=True, copy=False, tracking=True,
                                    help="If an inspection is auto-generated, it can be canceled but not removed.")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True, tracking=True,
                                 states={"draft": [("readonly", False)]}, default=lambda self: self.env.company)
    user = fields.Many2one(comodel_name="res.users", string="Responsible", tracking=True, readonly=True,
                           default=False)
    project_id = fields.Many2one('project.project', string='Project', tracking=True)
    project_stage_id = fields.Many2one('project.task.type', 'Project Stage')
    subject = fields.Char('Acceptance Subject', readonly=True, tracking=True)
    project_acceptance_definition = fields.Text('Description', readonly=True, tracking=True)
    deliverables_ids = fields.One2many('acceptance.inspection.deliverables', 'acceptance_inspection_id',
                                       'Deliverables and Acceptance Criteria', readonly=True, tracking=True)
    assurance_activity_ids = fields.One2many('acceptance.inspection.assurance', 'acceptance_inspection_id',
                                             'Deliverables and Acceptance Criteria', readonly=True,
                                             tracking=True)
    color = fields.Integer(string='Color Index', compute='_get_default_color')
    is_from_project = fields.Boolean('From Project')
    stakeholders_ids = fields.Many2many('res.users', compute='_compute_get_stakeholders')
    acceptance_ch = fields.Char('Set Acceptance Checklist')
    rejection_reason = fields.Char('Rejection Reason', tracking=True)
    acceptance_rejected_by = fields.Many2one('res.users', 'Rejected by', tracking=True)
    acceptance_approved_by = fields.Many2one('res.users', 'Approved by', tracking=True)
    acceptance_requested_by = fields.Many2one('res.users', 'Approval Requested by', tracking=True)
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    due_date = fields.Date('Approval Due Date', tracking=True)
    activity_reminder_days = fields.Integer('Activity Days')

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

    @api.depends('project_id', 'project_id.stakeholder_ids')
    def _compute_get_stakeholders(self):
        users_obj = self.env['res.users']
        for record in self:
            partner_list, users, p_user = [], [], []
            if record.project_id and record.project_id.stakeholder_ids:
                for lines in record.project_id.stakeholder_ids:
                    if lines.status is True and lines.partner_id:
                        partner_list.append(lines.partner_id.id)
                        users = users_obj.search([('partner_id', 'in', partner_list)])
                        if users:
                            for user in users:
                                if user.id == self.env.user.id:
                                    p_user.append(user.id)
            if self.env.user.has_group('gts_project_stages.group_project_manager_new'):
                record.stakeholders_ids = [(6, 0, [user.id for user in users])]
            else:
                record.stakeholders_ids = [(6, 0, p_user)]

    @api.depends('state')
    def _get_default_color(self):
        for rec in self:
            if rec.state == 'success':
                rec.color = 10
            elif rec.state == 'failed':
                rec.color = 1
            else:
                rec.color = 0

    @api.model_create_multi
    def create(self, val_list):
        for vals in val_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("acceptance.inspection")
        rec = super(AcceptanceInspection, self).create(val_list)
        partner_list = []
        if rec.project_id:
            if rec.project_id.program_manager_id:
                partner_list.append(rec.project_id.program_manager_id.partner_id.id)
            if rec.project_id.user_id:
                partner_list.append(rec.project_id.user_id.partner_id.id)
        new_list = list(set(partner_list))
        rec.message_subscribe(partner_ids=new_list)
        rec.is_from_project = True
        return rec

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
        for inspection in self:
            if not inspection.check_list:
                raise exceptions.UserError(_("You must first set the Acceptance Criteria."))
            # if any(lines.deadline is False for lines in inspection.inspection_lines):
            #     raise exceptions.UserError(_("Add Deadline in Acceptances before marking as Todo!"))
        self.write({"state": "ready"})

    # def submit_for_approval(self):
    #     users_obj = self.env['res.users']
    #     if not self.check_list:
    #         raise exceptions.UserError(_("You must first set the Acceptance Checklist!"))
    #     users_list = ''
    #     for user in users_obj.search([]):
    #         if user.has_group('project.group_project_manager'):
    #             users_list += user.login + ","
    #     if self.project_id.program_manager_id:
    #         users_list += self.project_id.program_manager_id.login + ","
    #     if self.project_id and self.project_id.user_id:
    #         action_id = self.env.ref('gts_acceptance_management.action_acceptance_inspection').id
    #         params = "web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (self.id, action_id)
    #         inspection_url = str(params)
    #         template = self.env.ref('gts_acceptance_management.acceptance_submit_for_approval')
    #         if template:
    #             values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
    #             values['email_to'] = users_list
    #             values['email_from'] = self.env.user.login
    #             values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #             mail = self.env['mail.mail'].create(values)
    #             try:
    #                 mail.send()
    #             except Exception:
    #                 pass
    #         self.write({"state": "waiting_for_approval"})

    # def button_approve(self):
    #     users_obj = self.env['res.users']
    #     action_id = self.env.ref('gts_acceptance_management.action_acceptance_inspection').id
    #     params = "web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (self.id, action_id)
    #     inspection_url = str(params)
    #     template = self.env.ref('gts_acceptance_management.acceptance_approved_manager')
    #     if template:
    #         values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
    #         values['email_to'] = self.user.login
    #         values['email_from'] = self.env.user.login
    #         values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #         mail = self.env['mail.mail'].create(values)
    #         try:
    #             mail.send()
    #         except Exception:
    #             pass
    #     user_list = ''
    #     for user in users_obj:
    #         if user.has_group('gts_acceptance_management.group_acceptance_manager'):
    #             user_list += user.login + ","
    #     template = self.env.ref('gts_acceptance_management.acceptance_check_list_ready_for_evaluation_email')
    #     if template:
    #         values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
    #         values['email_to'] = user_list
    #         values['email_from'] = self.env.user.login
    #         values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #         mail = self.env['mail.mail'].create(values)
    #         try:
    #             mail.send()
    #         except Exception:
    #             pass
    #     self.write({"state": "approved", "acceptance_approved_by": self.env.user})

    def button_approve(self):
        for inspection in self:
            user_list, notification_ids = "", []
            if inspection.acceptance_requested_by:
                user_list += inspection.acceptance_requested_by.partner_id.email + ", " or inspection.acceptance_requested_by.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': inspection.acceptance_requested_by.partner_id.id,
                    'notification_type': 'inbox'}))
            if inspection.user:
                user_list += inspection.user.partner_id.email + ", " or inspection.user.login + ", "
                notification_ids.append((0, 0, {
                    'res_partner_id': inspection.user.partner_id.id,
                    'notification_type': 'inbox'}))
            action_id = self.env.ref('gts_acceptance_management.action_acceptance_inspection').id
            params = "web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (inspection.id, action_id)
            inspection_url = str(params)
            template = self.env.ref('gts_acceptance_management.acceptance_check_list_evaluation_confirmed_email')
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
                [('res_id', '=', self.id), ('res_model', '=', 'acceptance.inspection'),
                 ('activity_type_id', '=',
                  self.env.ref('gts_acceptance_management.acceptance_requested_for_approval').id)])
            message = 'Acceptance is Approved by ' + str(self.env.user.name)
            if activity:
                for rec in activity:
                    rec._action_done(feedback=message)
            self.message_post(body="Acceptance has been Accepted",
                              message_type='notification', author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids, notify_by_email=False)
            inspection.state = "success"
            # if inspection.success:
            #     inspection.state = "success"
            # else:
            #     inspection.state = "failed"

    # def action_approve(self):
    #     users_obj = self.env['res.users'].search([])
    #     for inspection in self:
    #         if inspection.success:
    #             inspection.state = "success"
    #         else:
    #             inspection.state = "failed"
    #         user_list = ''
    #         for user in users_obj:
    #             if user.has_group('gts_acceptance_management.group_acceptance_manager'):
    #                 if user.id != self.env.user.id:
    #                     user_list += user.login + ","
    #         action_id = self.env.ref('gts_acceptance_management.action_acceptance_inspection').id
    #         params = "web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (inspection.id, action_id)
    #         inspection_url = str(params)
    #         template = self.env.ref('gts_acceptance_management.acceptance_check_list_evaluation_approved_email')
    #         if template:
    #             values = template.generate_email(inspection.id,
    #                                              ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
    #             values['email_to'] = inspection.user.login
    #             values['email_from'] = self.env.user.login
    #             values['email_cc'] = user_list
    #             values['body_html'] = values['body_html'].replace('_inspection_url', inspection_url)
    #             mail = self.env['mail.mail'].create(values)
    #             try:
    #                 mail.send()
    #             except Exception:
    #                 pass
    #         activity = self.env['mail.activity'].search(
    #             [('res_id', '=', inspection.id), ('res_model', '=', 'acceptance.inspection'),
    #              ('activity_type_id', '=',
    #               self.env.ref('gts_acceptance_management.activity_acceptance_waiting_for_approval').id)])
    #         message = 'Acceptance Check List is Approved by ' + str(self.env.user.name)
    #         if activity:
    #             for rec in activity:
    #                 rec._action_done(feedback=message, attachment_ids=False)

    # def action_cancel(self):
    #     users_obj = self.env['res.users'].search([])
    #     user_list = ''
    #     for user in users_obj:
    #         if user.has_group('gts_acceptance_management.group_acceptance_manager'):
    #             if user.id != self.env.user.id:
    #                 user_list += user.login + ","
    #     action_id = self.env.ref('gts_acceptance_management.action_acceptance_inspection').id
    #     params = "web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (self.id, action_id)
    #     inspection_url = str(params)
    #     template = self.env.ref('gts_acceptance_management.acceptance_check_list_evaluation_cancel_email')
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
    #         [('res_id', '=', self.id), ('res_model', '=', 'acceptance.inspection'),
    #          ('activity_type_id', '=',
    #           self.env.ref('gts_acceptance_management.activity_acceptance_waiting_for_approval').id)])
    #     message = 'Acceptance Check List is Cancelled by ' + str(self.env.user.name)
    #     if activity:
    #         for rec in activity:
    #             rec._action_done(feedback=message, attachment_ids=False)
    #     self.write({"state": "canceled"})

    def set_check_list(self, trigger_line, force_fill=False):
        for inspection in self:
            header = self._prepare_inspection_header(inspection.object_id, trigger_line)
            del header["state"]  # don't change current status
            del header["auto_generated"]  # don't change auto_generated flag
            del header["user"]  # don't change current user
            inspection.write(header)
            inspection.inspection_lines.unlink()
            inspection.inspection_lines = inspection._prepare_inspection_lines(
                trigger_line.check_list, force_fill=force_fill
            )

    def _make_inspection(self, object_ref, trigger_line):
        """Overridable hook method for creating inspection from check_list.
        :param object_ref: Object instance
        :param trigger_line: Trigger line instance
        :return: Inspection object
        """
        inspection = self.create(
            self._prepare_inspection_header(object_ref, trigger_line)
        )
        inspection.set_check_list(trigger_line)
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
            "state": "approved",
            "check_list": trigger_line.check_list.id,
            "user": trigger_line.user.id,
            "auto_generated": True,
        }

    def _prepare_inspection_lines(self, check_list, force_fill=False):
        new_data = []
        for line in check_list.check_list_lines:
            data = self._prepare_inspection_line(
                check_list, line, fill=check_list.fill_correct_values or force_fill
            )
            new_data.append((0, 0, data))
        return new_data

    def _prepare_inspection_line(self, check_list, line, fill=None):
        data = {
            "name": line.name,
            "check_list_line": line.id,
            "notes": line.notes,
            "min_value": line.min_value,
            "max_value": line.max_value,
            "check_list_uom_id": line.uom_id.id,
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

    def acceptance_activity_reminder(self):
        acceptance = self.env['acceptance.inspection'].search([])
        mail_activity_obj = self.env['mail.activity']
        today_date = datetime.now().date()
        for record in acceptance:
            activity = mail_activity_obj.search([('res_id', '=', record.id), ('res_model', '=', 'acceptance.inspection'),
                                                 ('activity_type_id', '=',
                                                  self.env.ref('gts_acceptance_management.acceptance_requested_for_approval').id)])
            if activity:
                for rec in activity:
                    diff_date = rec.date_deadline - today_date
                    if diff_date.days <= record.activity_reminder_days and record.project_id.outgoing_email:
                        notification_ids = []
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        template = self.env.ref('gts_acceptance_management.acceptance_approval_activity_email_reminder')
                        action_id = self.env.ref('gts_acceptance_management.acceptance_inspection_form_view').id
                        params = str(base_url) + "/web#id=%s&view_type=form&model=acceptance.inspection&action=%s" % (
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
                        record.message_post(body="Reminder to Close Activity for Acceptance ("+str(record.subject)+")",
                                            message_type='notification', subtype_xmlid='mail.mt_comment',
                                            author_id=record.user.partner_id.id, notification_ids=notification_ids,
                                            notify_by_email=False)


class AcceptanceInspectionLine(models.Model):
    _name = "acceptance.inspection.line"
    _description = "Acceptance Inspection Line"

    # @api.depends(
    #     "question_type",
    #     "uom_id",
    #     "check_list_uom_id",
    #     "max_value",
    #     "min_value",
    #     "quantitative_value",
    #     "qualitative_value",
    #     "possible_ql_values",
    # )
    # def _compute_acceptance_check_list_check(self):
    #     for l in self:
    #         if l.question_type == "qualitative":
    #             l.success = l.qualitative_value.ok
    #         else:
    #             if l.uom_id.id == l.check_list_uom_id.id:
    #                 amount = l.quantitative_value
    #             else:
    #                 amount = self.env["uom.uom"]._compute_quantity(
    #                     l.quantitative_value, l.check_list_uom_id.id
    #                 )
    #             l.success = l.max_value >= amount >= l.min_value
    #
    # @api.depends(
    #     "possible_ql_values", "min_value", "max_value", "check_list_uom_id", "question_type"
    # )
    # def _compute_valid_values(self):
    #     for l in self:
    #         if l.question_type == "qualitative":
    #             answers = []
    #             # l.valid_values = ", ".join(
    #             #     [x.name for x in l.possible_ql_values if x.ok]
    #             # )
    #             for x in l.possible_ql_values:
    #                 if x.ok:
    #                     answers += [x.name + ' (' + str(x.weightage) + ')']
    #                     l.valid_values = ', '.join(answers)
    #         else:
    #             l.valid_values = "{} ~ {}".format(
    #                 formatLang(self.env, l.min_value),
    #                 formatLang(self.env, l.max_value),
    #             )
    #             if self.env.ref("uom.group_uom") in self.env.user.groups_id:
    #                 l.valid_values += " %s" % l.check_list_uom_id.name

    inspection_id = fields.Many2one(comodel_name="acceptance.inspection", string="Inspection", ondelete="cascade")
    name = fields.Char(string="Criteria Line", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", related="inspection_id.product_id", store=True)
    subject = fields.Char(related='inspection_id.subject', string='Subject')
    check_list_line = fields.Many2one(comodel_name="acceptance.checklist.question", string="Acceptance Criteria", readonly=True)
    possible_ql_values = fields.Many2many(comodel_name="acceptance.checklist.que.value", string="Answers")
    quantitative_value = fields.Float(string="Quantitative Value", digits="Acceptance Control",
                                      help="Value of the result for a quantitative acceptance.")
    qualitative_value = fields.Many2one(comodel_name="acceptance.checklist.que.value", string="Qualitative Value",
                                        help="Value of the result for a qualitative acceptance.",
                                        domain="[('id', 'in', possible_ql_values)]")
    notes = fields.Text(string="Notes")
    min_value = fields.Float(string="Min", digits="Acceptance Control", readonly=True,
                             help="Minimum valid value for a quantitative acceptance.")
    max_value = fields.Float(string="Max", digits="Acceptance Control", readonly=True,
                             help="Maximum valid value for a quantitative acceptance.")
    check_list_uom_id = fields.Many2one(comodel_name="uom.uom", string="Check List UoM", readonly=True,
                                  help="UoM for minimum and maximum values for a quantitative " "Acceptance.")
    check_list_uom_category = fields.Many2one(comodel_name="uom.category", related="check_list_uom_id.category_id", store=True)
    uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", domain="[('category_id', '=', check_list_uom_category)]",
                             help="UoM of the inspection value for a quantitative acceptance.")
    question_type = fields.Selection([
        ("qualitative", "Qualitative"),
        ("quantitative", "Quantitative")
    ], string="Acceptance Type", readonly=True)
    valid_values = fields.Char(string="Valid Values", store=True)
    # valid_values = fields.Char(string="Valid Values", store=True, compute="_compute_valid_values")
    # success = fields.Boolean(compute="_compute_acceptance_check_list_check", string="Success?", store=True)
    success = fields.Boolean(string="Success?", store=True)
    deadline = fields.Date('Deadline')
    remarks = fields.Text('Remarks')
    weightage = fields.Integer('Weightage')
    allowed_user_ids = fields.Many2many('res.users', string="Visible to", groups='project.group_project_manager',
                                        compute='_compute_allowed_user_ids', store=True, readonly=False, copy=False)
    criteria_status = fields.Selection([
        ('done', 'Done'),
        ('partially_done', 'Partially Done'),
        ('not_done', 'Not Done'),
        ('accepted', 'Accepted'),
        ('not_accepted', 'Not Accepted')
    ], string='Status')

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

    def write(self, vals):
        prev_criteria = self.name or ''
        prev_remarks = self.remarks or ''
        prev_status = dict(self._fields['criteria_status'].selection).get(self.criteria_status)
        rec = super(AcceptanceInspectionLine, self).write(vals)
        message_body = """<b>Acceptance Criteria</b><br/>"""
        if prev_criteria == self.name or '':
            message_body += """• Criteria Line: {prev_criteria} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {name} <br/>""".format(
                prev_criteria=prev_criteria, name=self.name or ''
            )
        else:
            message_body += """<span style='color:red;'>• Criteria Line: {prev_criteria} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {name} </span><br/>""".format(
                prev_criteria=prev_criteria, name=self.name or ''
            )
        if prev_remarks == self.remarks or '':
            message_body += """• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}<br/>""".format(
                prev_remarks=prev_remarks, remarks=self.remarks or ''
            )
        else:
            message_body += """<span style='color:red;'>• Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}</span><br/>""".format(
                prev_remarks=prev_remarks, remarks=self.remarks or ''
            )
        if prev_status == dict(self._fields['criteria_status'].selection).get(self.criteria_status):
            message_body += """• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}<br/>""".format(
                prev_status=prev_status,
                status=dict(self._fields['criteria_status'].selection).get(self.criteria_status)
            )
        else:
            message_body += """<span style='color:red;'>• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}</span>""".format(
                prev_status=prev_status,
                status=dict(self._fields['criteria_status'].selection).get(self.criteria_status)
            )
        # message_body = """<b>Acceptance Criteria</b><br/>
        #                 • Criteria Line: {prev_criteria} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {name} <br/>
        #                 • Remarks: {prev_remarks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {remarks}<br/>
        #                 • Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}"""\
        #     .format(prev_criteria=prev_criteria, name=self.name or '',
        #             prev_remarks=prev_remarks, remarks=self.remarks or '',
        #             prev_status=prev_status,
        #             status=dict(self._fields['criteria_status'].selection).get(self.criteria_status))
        if self.inspection_id:
            self.inspection_id.message_post(body=message_body)
        return rec


class AcceptanceInspectionDeliverables(models.Model):
    _name = 'acceptance.inspection.deliverables'

    acceptance_inspection_id = fields.Many2one('acceptance.inspection', 'Acceptance Inspection')
    deliverables = fields.Char('Deliverables')
    remarks = fields.Char('Remarks')
    accept_criteria_situation = fields.Char('Acceptable Criteria/Acceptable Situation')


class AcceptanceInspectionAssurance(models.Model):
    _name = 'acceptance.inspection.assurance'

    acceptance_inspection_id = fields.Many2one('acceptance.inspection', 'Acceptance Inspection')
    activity_name = fields.Char('Activity Name')
    remarks = fields.Char('Remarks')
    resource = fields.Char('Resource')
