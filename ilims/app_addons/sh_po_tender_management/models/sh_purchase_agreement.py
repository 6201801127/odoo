# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import date, datetime


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        super(MailComposeMessage, self).action_send_mail()
        if self.env.context.get('active_model') == 'purchase.agreement' and self.env.context.get('active_id'):
            tender_id = self.env['purchase.agreement'].sudo().browse(self.env.context.get('active_id'))
            if tender_id and self.partner_ids and self.env.company.sh_auto_add_followers:
                tender_id.message_subscribe(self.partner_ids.ids)


class TenderDocument(models.Model):
    _name = 'tender.document'

    tender_id = fields.Many2one('purchase.agreement', string='Tender')
    sh_attachment = fields.Binary(string='Tender Document', attachment=True)
    sh_attachment_id = fields.Many2one('ir.attachment', compute='_compute_attachment_id', string="Attachments",
                                       store=True)
    sh_attachment_name = fields.Char('File Name')

    @api.depends('sh_attachment')
    def _compute_attachment_id(self):
        for document in self:
            attachment_id = self.env['ir.attachment'].search(
                [('res_id', '=', document.id), ('res_model', '=', 'tender.document'),
                 ('res_field', '=', 'sh_attachment')])
            document.sh_attachment_id = attachment_id


class ShPurchaseAgreement(models.Model):
    _name = 'purchase.agreement'
    _description = 'Tender'
    _rec_name = 'name'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin', 'utm.mixin', 'website.published.mixin']
    _order = 'create_date desc'

    @api.depends('project_id', 'project_id.stakeholder_ids')
    def _get_project_stakeholders(self):
        user_obj = self.env['res.users']
        for record in self:
            users_list = []
            if record.project_id and record.project_id.stakeholder_ids:
                for lines in record.project_id.stakeholder_ids:
                    if lines.status is True and lines.type_of_stakeholder.name == 'Internal':
                        user = user_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
                        if user and user.has_group('sh_po_tender_management.sh_purchase_tender_user'):
                            users_list.append(user.id)
            else:
                for user in user_obj.search([]):
                    if user.has_group('sh_po_tender_management.sh_purchase_tender_user'):
                        users_list.append(user.id)
            record.sh_stakeholder_ids = [(6, 0, users_list)]

    name = fields.Char('Name', readonly=True, tracking=True)
    sequence = fields.Char('Sequence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('bid_selection', 'Bid Selection'),
        ('technical_bid', 'Technical Bid Opened'),
        ('technical_bid_published', 'Technical Bid Published'),
        ('financial_bid', 'Financial Bid Opened'),
        ('financial_bid_published', 'Financial Bid Published'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled')
    ], string="State", default='draft', tracking=True)
    rfq_count = fields.Integer("Received Quotations", compute='_compute_rfq_count')
    order_count = fields.Integer("Selected Orders", compute='_compute_order_count')
    sh_purchase_user_id = fields.Many2one('res.users', 'Purchase Representative', tracking=True,
                                          default=lambda self: self.env.user)
    sh_stakeholder_ids = fields.Many2many('res.users', 'Stakeholders', compute='_get_project_stakeholders')
    sh_agreement_type = fields.Many2one(
        'purchase.agreement.type', 'Tender Type', required=True, tracking=True)
    sh_vender_id = fields.Many2one(
        'res.partner', 'Vendor', tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    partner_ids = fields.Many2many(
        'res.partner', string='Vendors', tracking=True)
    user_id = fields.Many2one('res.users', 'User')
    sh_agreement_deadline = fields.Datetime(
        'Tender Submission Deadline', tracking=True)
    sh_order_date = fields.Date('Ordering Date', tracking=True)
    sh_delivery_date = fields.Date('Delivery Date', tracking=True)
    sh_source = fields.Char('Source Document', tracking=True)
    sh_notes = fields.Text("Terms & Conditions", tracking=True)
    sh_purchase_agreement_line_ids = fields.One2many(
        'purchase.agreement.line', 'agreement_id', string='Tender Line')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    compute_custom_boolean = fields.Boolean(compute='_compute_module_boolean')
    website_description = fields.Char('Tender Description')
    project_id = fields.Many2one('project.project', 'Project')
    technical_bid_opening_date = fields.Datetime('Technical Bid Opening Date', tracking=True)
    financial_bid_opening_date = fields.Datetime('Financial Bid Opening Date', tracking=True)
    sh_attachment = fields.Binary(string='Tender Document', attachment=True)
    sh_attachment_id = fields.Many2one('ir.attachment', compute='_compute_attachment_id', string="Attachments",
                                       store=True)
    sh_attachment_name = fields.Char('File Name')
    is_open_tender = fields.Boolean('Is Open Tender?', tracking=True)
    technical_bid_lines = fields.One2many('technical.bid.lines', 'tender_id', string='Technical Bid')
    financial_bid_lines = fields.One2many('financial.bid.lines', 'tender_id', string='Financial Bid')
    color = fields.Integer('Color Index')
    vendor_participated = fields.Char('Vendors Participated', compute='_compute_vendor_participated')
    vendor_participated_count = fields.Integer('Vendor Participated Count', compute='_compute_vendor_participated')
    tender_documents_ids = fields.One2many('tender.document', 'tender_id', string='Tender Documents')
    tender_method_id = fields.Many2one('purchase.agreement.method', string='Tender Method')

    def _compute_vendor_participated(self):
        for record in self:
            vendor_list = ''
            count = 0
            purchases = self.env['purchase.order'].search([('agreement_id', '=', record.id)])
            if purchases:
                vendor_name = []
                for purchase in purchases:
                    if not purchase.partner_id.company_name:
                        vendor_name += [purchase.partner_id.name]
                    if purchase.partner_id.company_name:
                        vendor_name += [purchase.partner_id.name + ' (' + purchase.partner_id.company_name + ')']
                    vendor_list = ', '.join(vendor_name)
                    count += 1
            record.vendor_participated = vendor_list
            record.vendor_participated_count = count

    @api.depends('sh_attachment')
    def _compute_attachment_id(self):
        for document in self:
            attachment_id = self.env['ir.attachment'].search([('res_id', '=', document.id), ('res_model', '=', 'purchase.agreement'), ('res_field', '=', 'sh_attachment')])
            document.sh_attachment_id = attachment_id

    def _compute_module_boolean(self):
        if self:
            for rec in self:
                rec.compute_custom_boolean = False
                portal_module_id = self.env['ir.module.module'].sudo().search(
                    [('name', '=', 'sh_po_tender_portal'), ('state', 'in', ['installed'])], limit=1)
                if portal_module_id:
                    rec.compute_custom_boolean = True

    def _compute_access_url(self):
        super(ShPurchaseAgreement, self)._compute_access_url()
        for tender in self:
            tender.access_url = '/my/tender/%s' % (tender.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Tender', self.name)

    def _compute_rfq_count(self):
        if self:
            for rec in self:
                purchase_orders = self.env['purchase.order'].sudo().search(
                    [('agreement_id', '=', rec.id), ('state', 'in', ['draft']), ('selected_order', '=', False)])
                if purchase_orders:
                    rec.rfq_count = len(purchase_orders.ids)
                else:
                    rec.rfq_count = 0

    def _compute_order_count(self):
        if self:
            for rec in self:
                purchase_orders = self.env['purchase.order'].sudo().search(
                    [('agreement_id', '=', rec.id), ('state', 'in', ['purchase'])])
                # purchase_orders = self.env['purchase.order'].sudo().search(
                #     [('agreement_id', '=', rec.id), ('state', 'not in', ['cancel']), ('selected_order', '=', True)])
                if purchase_orders:
                    rec.order_count = len(purchase_orders.ids)
                else:
                    rec.order_count = 0

    def action_confirm(self):
        if self:
            for rec in self:
                if rec.sequence:
                    rec.name = rec.sequence
                else:
                    seq = self.env['ir.sequence'].next_by_code(
                        'purchase.agreement')
                    rec.name = seq
                    rec.sequence = seq
                rec.state = 'confirm'
                activity = self.env['mail.activity'].search(
                    [('res_id', '=', rec.id), ('res_model', '=', 'purchase.agreement'),
                     ('activity_type_id', '=',
                      self.env.ref('sh_po_tender_management.activity_confirm_tender').id)])
                message = 'Tender Confirmed by ' + str(self.env.user.name)
                if activity:
                    for rec in activity:
                        rec._action_done(feedback=message)

    def action_new_quotation(self):
        if self:
            for rec in self:
                line_ids = []
                current_date = None
                if rec.sh_delivery_date:
                    current_date = rec.sh_delivery_date
                else:
                    current_date = fields.Datetime.now()
                analytic_account = False
                if rec.project_id:
                    analytic_account = rec.project_id.analytic_account_id.id
                for rec_line in rec.sh_purchase_agreement_line_ids:
                    line_vals = {
                        'product_id': rec_line.sh_product_id.id,
                        'name': rec_line.sh_product_id.name,
                        'date_planned': current_date,
                        'product_qty': rec_line.sh_qty,
                        'status': 'draft',
                        'agreement_id': rec.id,
                        'product_uom': rec_line.sh_product_id.uom_id.id,
                        'price_unit': rec_line.sh_price_unit,
                        'account_analytic_id': analytic_account
                    }
                    line_ids.append((0, 0, line_vals))
                return {
                    'name': _('New'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': {'default_agreement_id': rec.id,
                                'default_user_id': rec.sh_purchase_user_id.id,
                                'default_order_line': line_ids,
                                'default_analytic_account_id': analytic_account},
                    'target': 'current'
                }

    def action_validate(self):
        if self:
            for rec in self:
                if self.env.company.sh_auto_add_followers and rec.partner_ids:
                    rec.message_subscribe(rec.partner_ids.ids)
                if self.env.company.sh_portal_user_create and rec.partner_ids:
                    for vendor in rec.partner_ids:
                        user_id = self.env['res.users'].sudo().search([('partner_id','=',vendor.id)],limit=1)
                        if not user_id:
                            portal_wizard_obj = self.env['portal.wizard']
                            created_portal_wizard = portal_wizard_obj.create({})
                            if created_portal_wizard and vendor.email and self.env.user:
                                portal_wizard_user_obj = self.env['portal.wizard.user']
                                wiz_user_vals = {
                                    'wizard_id': created_portal_wizard.id,
                                    'partner_id': vendor.id,
                                    'email': vendor.email,
                                    'in_portal': True,
                                    'user_id': self.env.user.id,
                                    }
                                created_portal_wizard_user = portal_wizard_user_obj.create(wiz_user_vals)
                                if created_portal_wizard_user:
                                    created_portal_wizard.action_apply()
                                    vendor_portal_user_id = self.env['res.users'].sudo().search([('partner_id','=',vendor.id)],limit=1)
                                    if vendor_portal_user_id:
                                        vendor_portal_user_id.is_tendor_vendor = True
                rec.state = 'bid_selection'

    def action_analyze_rfq(self):
        list_id = self.env.ref(
            'sh_po_tender_management.sh_bidline_tree_view').id
        form_id = self.env.ref(
            'sh_po_tender_management.sh_bidline_form_view').id
        pivot_id = self.env.ref(
            'sh_po_tender_management.purchase_order_line_pivot_custom').id
        return {
            'name': _('Tender Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'view_type': 'form',
            'view_mode': 'tree,pivot,form',
            'views': [(list_id, 'tree'), (pivot_id, 'pivot'), (form_id, 'form')],
            'domain': [('agreement_id', '=', self.id), ('state', 'not in', ['cancel']), ('order_id.selected_order', '=', False)],
            'context': {'search_default_groupby_product': 1},
            'target': 'current'
        }

    def action_set_to_draft(self):
        if self:
            for rec in self:
                rec.state = 'draft'

    def action_close(self):
        if self:
            for rec in self:
                rec.state = 'closed'

    def action_cancel(self):
        if self:
            for rec in self:
                rec.state = 'cancel'

    def action_open_technical_bid(self):
        rfqs = self.env['purchase.order'].search([('agreement_id', '=', self.id), ('state', '=', 'draft')])
        if self.technical_bid_opening_date > datetime.now():
            raise ValidationError(_("Tender is still in bid processing, you cannot open technical bid now!"))
        if not rfqs:
            raise ValidationError(_("No Quotation been generated by Vendor yet!"))
        rfq_list = []
        if rfqs:
            for rfq in rfqs:
                rfq_list.append([0, 0, {
                    'tender_id': self.id,
                    'rfq_number': rfq.id,
                    'vendor_id': rfq.partner_id.id,
                    'technical_document': rfq.sh_technical_attachment,
                    'technical_document_name': rfq.sh_technical_attachment_name
                }])
        self.technical_bid_lines = [(5, 0, 0)]
        self.technical_bid_lines = rfq_list
        self.state = 'technical_bid'

    def action_publish_technical_bid(self):
        for lines in self.technical_bid_lines:
            if lines.rfq_number:
                lines.rfq_number.update({'technical_marks': lines.technical_marks})
        user_list = ''
        if self.project_id and self.project_id.user_id.partner_id.email:
            user_list += self.project_id.user_id.partner_id.email + ", "
        elif self.project_id and self.project_id.user_id:
            user_list += self.project_id.user_id.login + ", "
        if self.project_id and self.project_id.program_manager_id.partner_id.email:
            user_list += self.project_id.program_manager_id.partner_id.email + ", "
        elif self.project_id and self.project_id.program_manager_id:
            user_list += self.project_id.program_manager_id.login + ", "
        if self.partner_ids:
            for partner in self.partner_ids:
                if partner.email:
                    user_list += partner.email
        template = self.env.ref('sh_po_tender_management.tender_email_on_technical_marks_publish')
        if template:
            values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
            values['email_to'] = user_list
            values['email_from'] = self.env.user.partner_id.email or self.env.user.login
            values['body_html'] = values['body_html']
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        self.write({'state': 'technical_bid_published'})

    def action_open_financial_bid(self):
        if self.financial_bid_opening_date > datetime.now():
            raise ValidationError(_("You cannot open financial bid before %s", self.financial_bid_opening_date))
        rfqs = self.env['purchase.order'].search([('agreement_id', '=', self.id), ('state', '=', 'draft')])
        rfq_list = []
        if rfqs:
            bid_amount = min(rfqs.mapped('amount_untaxed'))
            for rfq in rfqs:
                financial_marks = 0
                if int(bid_amount) > 0:
                    financial_marks = int(bid_amount) / int(rfq.amount_untaxed) * 30
                rfq_list.append([0, 0, {
                    'tender_id': self.id,
                    'rfq_number': rfq.id,
                    'vendor_id': rfq.partner_id.id,
                    'financial_value': rfq.amount_untaxed,
                    'financial_marks': financial_marks,
                    'financial_document': rfq.sh_financial_attachment,
                    'financial_document_name': rfq.sh_financial_attachment_name
                }])
        self.financial_bid_lines = [(5, 0, 0)]
        self.financial_bid_lines = rfq_list
        self.state = 'financial_bid'

    def action_publish_financial_bid(self):
        if self:
            for rec in self:
                user_list = ''
                if rec.project_id and rec.project_id.user_id.partner_id.email:
                    user_list += rec.project_id.user_id.partner_id.email + ", "
                elif rec.project_id and rec.project_id.user_id:
                    user_list += rec.project_id.user_id.login + ", "
                if rec.project_id and rec.project_id.program_manager_id.partner_id.email:
                    user_list += rec.project_id.program_manager_id.partner_id.email + ", "
                elif rec.project_id and rec.project_id.program_manager_id:
                    user_list += rec.project_id.program_manager_id.login + ", "
                if rec.partner_ids:
                    for partner in rec.partner_ids:
                        if partner.email:
                            user_list += partner.email
                template = self.env.ref('sh_po_tender_management.tender_email_on_financial_marks_publish')
                if template:
                    values = template.generate_email(rec.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = user_list
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
                # purchase_obj = self.env['purchase.order']
                # rfqs = purchase_obj.search([('state', '=', 'draft'), ('agreement_id', '=', rec.id)])
                # if rfqs:
                #     bid_amount = min(rfqs.mapped('amount_untaxed'))
                for lines in rec.financial_bid_lines:
                    if lines.rfq_number:
                        lines.rfq_number.financial_marks = lines.financial_marks
                        lines.rfq_number.total_marks = lines.financial_marks + lines.rfq_number.technical_marks
                # purchase_obj = self.env['purchase.order']
                # rfqs = purchase_obj.search([('state', '=', 'draft'), ('agreement_id', '=', rec.id)])
                # if rfqs:
                #     bid_amount = min(rfqs.mapped('amount_untaxed'))
                #     for rfq in rfqs:
                #         if int(bid_amount) > 0:
                #             rfq.financial_marks = int(bid_amount / rfq.amount_untaxed * 30)
                #         rfq.total_marks = rfq.financial_marks + rfq.technical_marks
                rec.state = 'financial_bid_published'

    def action_send_tender(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference(
            'sh_po_tender_management', 'email_template_edi_purchase_tedner')[1]
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'purchase.agreement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        if self.sh_vender_id:
            ctx.update({
                'default_partner_ids': [(6, 0, self.sh_vender_id.ids)]
            })
        if self.partner_ids:
            ctx.update({
                'default_partner_ids': [(6, 0, self.partner_ids.ids)]
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_view_quote(self):
        tree_view_id = self.env.ref('sh_po_tender_management.sh_bidline_rfq_tree_view').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        return {
            'name': _('Received Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_id': self.id,
            'domain': [('agreement_id', '=', self.id), ('state', 'in', ['draft'])],
            # 'domain': [('agreement_id', '=', self.id), ('selected_order', '=', False), ('state', 'in', ['draft'])],
            'target': 'current',
            'context': {'create': False}
        }

    def action_view_order(self):
        tree_view_id = self.env.ref('purchase.purchase_order_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        return {
            'name': _('Selected Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_id': self.id,
            'domain': [('agreement_id', '=', self.id), ('state', 'in', ['purchase'])],
            # 'domain': [('agreement_id', '=', self.id), ('selected_order', '=', True), ('state', 'not in', ['cancel'])],
            'target': 'current',
            'context': {'create': False}
        }

    @api.constrains('sh_agreement_deadline', 'technical_bid_opening_date', 'financial_bid_opening_date')
    def check_opening_bid_date(self):
        if self.technical_bid_opening_date < self.sh_agreement_deadline:
            raise UserError(_("Technical Bid Opening Date should be greater than Tender Deadline!"))
        if self.financial_bid_opening_date < self.technical_bid_opening_date:
            raise UserError(_("Financial Bid Opening Date should be greater than Technical Bid Opening Date!"))

    @api.model
    def create(self, vals):
        rec = super(ShPurchaseAgreement, self).create(vals)
        if not rec.tender_documents_ids:
            raise ValidationError(_("Attach Tender Document!"))
        if not rec.sh_purchase_agreement_line_ids:
            raise ValidationError(_("Atleast one product must me selected in lines!"))
        user_list_cc = ''
        if rec.project_id:
            if rec.project_id and rec.project_id.user_id.partner_id.email:
                user_list_cc += rec.project_id.user_id.partner_id.email + ", "
            elif rec.project_id and rec.project_id.user_id:
                user_list_cc += rec.project_id.user_id.login + ", "
            if rec.project_id and rec.project_id.program_manager_id.partner_id.email:
                user_list_cc += rec.project_id.program_manager_id.partner_id.email + ", "
            elif rec.project_id and rec.project_id.program_manager_id:
                user_list_cc += rec.project_id.program_manager_id.login + ", "
        bid_managers = self.env['res.users'].search([('groups_id', 'in', self.env.ref('sh_po_tender_management.sh_purchase_tender_manager').id)])
        if bid_managers:
            users_list = ''
            for manager in bid_managers:
                users_list += manager.partner_id.email + ", " or manager.login + ", "
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action_id = self.env.ref('sh_po_tender_management.sh_purchase_agreement_form_view').id
            params = str(base_url) + "web#id=%s&view_type=form&model=purchase.agreement&action=%s" % (rec.id, action_id)
            tender_url = str(params)
            template = self.env.ref('sh_po_tender_management.tender_email_to_project_user')
            if template:
                values = template.generate_email(rec.id, ['subject', 'email_to', 'email_from', 'email_cc', 'body_html'])
                values['email_to'] = users_list
                values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                values['email_cc'] = user_list_cc
                values['body_html'] = values['body_html'].replace('_tender_url', tender_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
        if bid_managers:
            for manager in bid_managers:
                activity_dict = {
                    'res_model': 'purchase.agreement',
                    'res_model_id': self.env.ref('sh_po_tender_management.model_purchase_agreement').id,
                    'res_id': rec.id,
                    'activity_type_id': self.env.ref('sh_po_tender_management.activity_confirm_tender').id,
                    'date_deadline': datetime.now().date(),
                    'summary': 'Confirm Tender',
                    'user_id': manager.id
                }
                self.env['mail.activity'].create(activity_dict)
        return rec

    def write(self, vals):
        rec = super(ShPurchaseAgreement, self).write(vals)
        if not self.tender_documents_ids:
            raise ValidationError(_("Attach Tender Document!"))
        if not self.sh_purchase_agreement_line_ids:
            raise ValidationError(_("Atleast one product must me selected in lines!"))
        if 'project_id' in vals:
            user_list = ''
            if self.project_id and self.project_id.user_id.partner_id.email:
                user_list += self.project_id.user_id.partner_id.email + ", "
            elif self.project_id and self.project_id.user_id:
                user_list += self.project_id.user_id.login + ", "
            if self.project_id and self.project_id.program_manager_id.partner_id.email:
                user_list += self.project_id.program_manager_id.partner_id.email + ", "
            elif self.project_id and self.project_id.program_manager_id:
                user_list += self.project_id.program_manager_id.login + ", "
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action_id = self.env.ref('sh_po_tender_management.sh_purchase_agreement_form_view').id
            params = str(base_url) + "web#id=%s&view_type=form&model=purchase.agreement&action=%s" % (self.id, action_id)
            tender_url = str(params)
            template = self.env.ref('sh_po_tender_management.tender_email_to_project_user')
            if template:
                values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
                values['email_to'] = user_list
                values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                values['body_html'] = values['body_html'].replace('_tender_url', tender_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass
        if 'is_published' in vals:
            if vals.get('is_published') is True:
                user_list = ''
                if self.project_id and self.project_id.user_id.partner_id.email:
                    user_list += self.project_id.user_id.partner_id.email + ", "
                elif self.project_id and self.project_id.user_id:
                    user_list += self.project_id.user_id.login + ", "
                if self.project_id and self.project_id.program_manager_id.partner_id.email:
                    user_list += self.project_id.program_manager_id.partner_id.email + ", "
                elif self.project_id and self.project_id.program_manager_id:
                    user_list += self.project_id.program_manager_id.login + ", "
                if self.partner_ids:
                    for partner in self.partner_ids:
                        if partner.email:
                            user_list += partner.email
                template = self.env.ref('sh_po_tender_management.tender_email_on_publish')
                if template:
                    values = template.generate_email(self.id, ['subject', 'email_to', 'email_from', 'body_html'])
                    values['email_to'] = user_list
                    values['email_from'] = self.env.user.partner_id.email or self.env.user.login
                    values['body_html'] = values['body_html']
                    mail = self.env['mail.mail'].create(values)
                    try:
                        mail.send()
                    except Exception:
                        pass
        return rec


class ShPurchaseAgreementLine(models.Model):
    _name = 'purchase.agreement.line'
    _description = "Tender Line"

    agreement_id = fields.Many2one('purchase.agreement', 'Purchase Tender')
    sh_product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    sh_qty = fields.Float('Quantity', default=1.0)
    sh_ordered_qty = fields.Float(
        'Ordered Quantities', compute='_compute_ordered_qty')
    sh_price_unit = fields.Float('Unit Price')
    company_id = fields.Many2one('res.company', related='agreement_id.company_id',
                                 string='Company', store=True, readonly=True, default=lambda self: self.env.company)

    def write(self, vals):
        prev_sh_product_id = self.sh_product_id.name
        prev_sh_qty = self.sh_qty
        prev_sh_ordered_qty = self.sh_ordered_qty
        prev_sh_price_unit = self.sh_price_unit
        rec = super(ShPurchaseAgreementLine, self).write(vals)
        message_body = """<b>Product</b><br/>"""
        if prev_sh_product_id == self.sh_product_id.name:
            message_body += """• Product: {prev_sh_product_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_product_id} <br/>""".format(
                prev_sh_product_id=prev_sh_product_id, sh_product_id=self.sh_product_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Product: {prev_sh_product_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_product_id}</span><br/>""".format(
                prev_sh_product_id=prev_sh_product_id, sh_product_id=self.sh_product_id.name
            )
        if prev_sh_qty == self.sh_qty:
            message_body += """• Quantity: {prev_sh_qty} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_qty}<br/>""".format(
                prev_sh_qty=prev_sh_qty, sh_qty=self.sh_qty
            )
        else:
            message_body += """<span style='color:red;'>• Quantity: {prev_sh_qty} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_qty}</span><br/>""".format(
                prev_sh_qty=prev_sh_qty, sh_qty=self.sh_qty
            )
        if prev_sh_ordered_qty == self.sh_ordered_qty:
            message_body += """• Ordered Quantities: {prev_sh_ordered_qty} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_ordered_qty}<br/>""".format(
                prev_sh_ordered_qty=prev_sh_ordered_qty, sh_ordered_qty=self.sh_ordered_qty
            )
        else:
            message_body += """<span style='color:red;'>• Ordered Quantities: {prev_sh_ordered_qty} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_ordered_qty}</span><br/>""".format(
                prev_sh_ordered_qty=prev_sh_ordered_qty, sh_ordered_qty=self.sh_ordered_qty
            )
        if prev_sh_price_unit == self.sh_price_unit:
            message_body += """• Unit Price: {prev_sh_price_unit} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_price_unit}""".format(
                prev_sh_price_unit=prev_sh_price_unit, sh_price_unit=self.sh_price_unit
            )
        else:
            message_body += """<span style='color:red;'>• Unit Price: {prev_sh_price_unit} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_price_unit}</span>""".format(
                prev_sh_price_unit=prev_sh_price_unit, sh_price_unit=self.sh_price_unit
            )
        # message_body = """<b>Product</b><br/>
        #                 • Product: {prev_sh_product_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_product_id} <br/>
        #                 • Quantity: {prev_sh_qty} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_qty}<br/>
        #                 • Ordered Quantities: {prev_sh_ordered_qty} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_ordered_qty}<br/>
        #                 • Unit Price: {prev_sh_price_unit} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {sh_price_unit}""" \
        #     .format(prev_sh_product_id=prev_sh_product_id, sh_product_id=self.sh_product_id.name,
        #             prev_sh_qty=prev_sh_qty, sh_qty=self.sh_qty,
        #             prev_sh_ordered_qty=prev_sh_ordered_qty, sh_ordered_qty=self.sh_ordered_qty,
        #             prev_sh_price_unit=prev_sh_price_unit, sh_price_unit=self.sh_price_unit,)
        self.agreement_id.message_post(body=message_body)
        return rec

    def _compute_ordered_qty(self):
        if self:
            for rec in self:
                order_qty = 0.0
                purchase_order_lines = self.env['purchase.order.line'].sudo().search([('product_id', '=', rec.sh_product_id.id), (
                    'agreement_id', '=', rec.agreement_id.id), ('order_id.selected_order', '=', True), ('order_id.state', 'in', ['purchase'])])
                for line in purchase_order_lines:
                    order_qty += line.product_qty
                rec.sh_ordered_qty = order_qty


class TechnicalBidLines(models.Model):
    _name = 'technical.bid.lines'
    _description = 'Technical Bid lines'

    tender_id = fields.Many2one('purchase.agreement', 'Tender')
    rfq_number = fields.Many2one('purchase.order', 'RFQ')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    technical_document = fields.Binary('Download Technical Document')
    technical_document_name = fields.Char('Download Technical Document Filename')
    technical_marks = fields.Integer('Technical Marks')

    def write(self, vals):
        prev_vendor_id = self.vendor_id.name
        prev_technical_document = self.technical_document
        prev_technical_document_name = self.technical_document_name
        prev_technical_marks = self.technical_marks
        rec = super(TechnicalBidLines, self).write(vals)
        message_body = """<b>Technical Bid</b><br/>"""
        if prev_vendor_id == self.vendor_id.name:
            message_body += """• Vendor: {prev_vendor_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {vendor_id}<br/>""".format(
                prev_vendor_id=prev_vendor_id, vendor_id=self.vendor_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Vendor: {prev_vendor_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {vendor_id}</span><br/>""".format(
                prev_vendor_id=prev_vendor_id, vendor_id=self.vendor_id.name
            )
        if prev_technical_document == self.technical_document:
            message_body += """• Download Technical Document Filename: {prev_technical_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_document_name}<br/>""".format(
                prev_technical_document_name=prev_technical_document_name,
                technical_document_name=self.technical_document_name
            )
        else:
            message_body += """<span style='color:red;'>• Download Technical Document Filename: {prev_technical_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_document_name}</span><br/>""".format(
                prev_technical_document_name=prev_technical_document_name,
                technical_document_name=self.technical_document_name
            )
        if prev_technical_marks == self.technical_marks:
            message_body += """• Technical Marks: {prev_technical_marks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_marks}""".format(
                prev_technical_marks=prev_technical_marks, technical_marks=self.technical_marks
            )
        else:
            message_body += """<span style='color:red;'>• Technical Marks: {prev_technical_marks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_marks}</span>""".format(
                prev_technical_marks=prev_technical_marks, technical_marks=self.technical_marks
            )
        # message_body = """<b>Technical Bid</b><br/>
        #                 • RFQ: {prev_rfq_number} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {rfq_number} <br/>
        #                 • Vendor: {prev_vendor_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {vendor_id}<br/>
        #                 • Download Technical Document: {prev_technical_document} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_document}<br/>
        #                 • Download Technical Document Filename: {prev_technical_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_document_name}<br/>
        #                 • Technical Marks: {prev_technical_marks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {technical_marks}""" \
        #     .format(prev_rfq_number=prev_rfq_number, rfq_number=self.rfq_number,
        #             prev_vendor_id=prev_vendor_id, vendor_id=self.vendor_id.name,
        #             prev_technical_document=prev_technical_document, technical_document=self.technical_document,
        #             prev_technical_document_name=prev_technical_document_name, technical_document_name=self.technical_document_name,
        #             prev_technical_marks=prev_technical_marks, technical_marks=self.technical_marks,)
        self.tender_id.message_post(body=message_body)
        return rec


class FinancialBidLines(models.Model):
    _name = 'financial.bid.lines'
    _description = 'Financial Bid lines'

    tender_id = fields.Many2one('purchase.agreement', 'Tender')
    rfq_number = fields.Many2one('purchase.order', 'RFQ')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    financial_marks = fields.Integer('Financial Marks')
    financial_document = fields.Binary('Download Financial Document')
    financial_document_name = fields.Char('Financial Document Name')
    financial_value = fields.Float('Bid Price')

    def write(self, vals):
        prev_rfq_number = self.rfq_number
        prev_vendor_id = self.vendor_id.name
        prev_financial_document = self.financial_document
        prev_financial_document_name = self.financial_document_name
        prev_financial_marks = self.financial_marks
        rec = super(FinancialBidLines, self).write(vals)
        message_body = """<b>Financial Bid</b><br/>"""
        if prev_vendor_id == self.vendor_id.name:
            message_body += """• Vendor: {prev_vendor_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {vendor_id}<br/>""".format(
                prev_vendor_id=prev_vendor_id, vendor_id=self.vendor_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Vendor: {prev_vendor_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {vendor_id}</span><br/>""".format(
                prev_vendor_id=prev_vendor_id, vendor_id=self.vendor_id.name
            )
        if prev_financial_document == self.financial_document:
            message_body += """• Download Financial Document: {prev_financial_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_document_name}<br/>""".format(
                prev_financial_document_name=prev_financial_document_name,
                financial_document_name=self.financial_document_name
            )
        else:
            message_body += """<span style='color:red;'>• Download Financial Document: {prev_financial_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_document_name}</span><br/>""".format(
                prev_financial_document_name=prev_financial_document_name,
                financial_document_name=self.financial_document_name
            )
        if prev_financial_marks == self.financial_marks:
            message_body += """• Financial Marks: {prev_financial_marks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_marks}""".format(
                prev_financial_marks=prev_financial_marks, financial_marks=self.financial_marks
            )
        else:
            message_body += """<span style='color:red;'>• Financial Marks: {prev_financial_marks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_marks}</span>""".format(
                prev_financial_marks=prev_financial_marks, financial_marks=self.financial_marks
            )
        # message_body = """<b>Financial Bid</b><br/>
        #                 • RFQ: {prev_rfq_number} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {rfq_number} <br/>
        #                 • Vendor: {prev_vendor_id} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {vendor_id}<br/>
        #                 • Download Financial Document: {prev_financial_document} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_document}<br/>
        #                 • Financial Document Name: {prev_financial_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_document_name}<br/>
        #                 • Financial Marks: {prev_financial_marks} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {financial_marks}""" \
        #     .format(prev_rfq_number=prev_rfq_number, rfq_number=self.rfq_number,
        #             prev_vendor_id=prev_vendor_id, vendor_id=self.vendor_id.name,
        #             prev_financial_document=prev_financial_document, financial_document=self.financial_document,
        #             prev_financial_document_name=prev_financial_document_name, financial_document_name=self.financial_document_name,
        #             prev_financial_marks=prev_financial_marks, financial_marks=self.financial_marks,)
        self.tender_id.message_post(body=message_body)
        return rec
