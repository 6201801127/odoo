# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.modules import get_module_resource
import base64
from PIL import Image
from odoo.tools.mimetypes import guess_mimetype


class kw_onboarding_handbook(models.Model):
    _name = "kw_onboarding_handbook"
    _description = "Policy Documents"
    _rec_name = "title"
    _order = "id desc"

    location = fields.Selection([('0', 'Select Location')], default='0')
    category = fields.Many2one('kw_onboarding_handbook_category')
    title = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description", required=True)
    attachment = fields.Binary(string='Attachment', attachment=True)
    expires_on = fields.Date(string="Expires on")
    count_downloads = fields.Integer()
    icon = fields.Binary(string="Upload Icon")
    display_description = fields.Text(string='Description', compute='_compute_display_description')
    active = fields.Boolean(default=True,
                            help="The active field allows you to hide the employee handbook without removing it.")
    document_type = fields.Selection([('handbook', 'HR Processes'),
                                      ('business_rule', 'Business Processes'),
                                      ('finance_process', 'Finance Processes'),
                                      ('department_structure', 'Dep.Structure,CDP & JD'),
                                      ('software_development', 'Delivery Processes'),
                                      ('it_policies_processes', 'IT Policies & Processes'),
                                      ('admin_processes', 'Admin Processes')
                                      ], string="Document Type")
    handbook_type_id = fields.Many2one('kw_handbook_type', string="Document Type")
    handbook_type_code = fields.Char(related="handbook_type_id.code")
    posted_on = fields.Date(string="Posted on")
    revised_on = fields.Date(string="Revised Date")
    auth_login = fields.Boolean("View After Login")
    already_seen_boolean = fields.Boolean('Handbook Read', compute='_compute_check_read')
    category_count = fields.Text(string='Count Category', compute='_compute_count_category')
    user_ids = fields.Many2many('res.users', string='Users')
    view_access = fields.Selection([('All', 'All'), ('Specific', 'Specific'),('company_specific', 'Company Specific')], string='Visible to', default='All')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    company_ids = fields.Many2many('res.company', string='Company')
    email_to = fields.Boolean(string='Email Notify')
    starting_page_num = fields.Integer(string='Start Page')
    ending_page_num = fields.Integer(string='End Page')

    @api.onchange('view_access')
    def onchange_view_access(self):
        if self.view_access == 'All':
            self.employee_ids = False
            self.company_ids = False
        if self.view_access == 'Specific': 
            self.company_ids = False
        if self.view_access == 'company_specific': 
            self.employee_ids = False


    def _compute_check_read(self):
        for record in self:
            record.already_seen_boolean = False
            if self.env.user in record.user_ids:
                record.already_seen_boolean = True

    # Function to Display the attachment of handbook  :Start
    @api.multi
    def get_stock_file(self):
        form_view_id = self.env.ref("kw_handbook.kw_onboarding_attachment_form").id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_onboarding_handbook',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
        }

    @api.multi
    def get_stock_file_template(self):
        form_view_id = self.env.ref("kw_handbook.kw_onboarding_attachment_form_template").id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_onboarding_handbook',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'flags': {'mode': 'readonly'},

        }

    def yes_understand(self):
        self.sudo().update({
            'user_ids': [(4, self.env.user.id)]
        })
        current_employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        existing_handbook = current_employee.handbook_info_details_ids.filtered(lambda r: r.handbook_id == self.id)
        if not existing_handbook:
            current_employee.handbook_info_details_ids = [[0, 0, {
                'employee_id': current_employee.id,
                'handbook_id': self.id,
                'handbook_type_id': self.handbook_type_id.id,
            }]]
        handbook_auth_login = self.env['kw_onboarding_handbook'].sudo().search([('auth_login', '=', True)])
        handbook_understood = self.env['kw_handbook'].sudo().search([('employee_id', '=', current_employee.id),
                                                                     ('handbook_id', 'in', handbook_auth_login.ids)])
        handbook_auth_login -= handbook_understood.mapped('handbook_id')

        kanban_view_id = self.env.ref('kw_handbook.kw_handbook_kanban_view').id
        # tree_view_id = self.env.ref('kw_handbook.kw_handbook_tree_view').id
        # form_view_id = self.env.ref('kw_handbook.kw_handbook_form_view').id
        return {
            'name': 'Employee Handbook',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_onboarding_handbook',
            'view_type': 'form',
            'view_mode': 'kanban',
            'views': [(kanban_view_id, 'kanban')],
            'context': {'create': False, 'edit': False, 'import': False},
            'target': 'main',
            'domain': [('id', 'in', handbook_auth_login.ids)],
        }

    # def skip_document(self):
    #     return {'type': 'ir.actions.act_window_close'}

    # Function to Display the attachment of handbook  :End
    # @api.constrains('expires_on')
    # def check_expires(self):
    #     current_date = str(datetime.now().date())
    #     for record in self:
    #         if record.expires_on:
    #             if str(record.expires_on) < current_date:
    #                 raise ValidationError("Expire date should be greater than current date")

    @api.constrains('title')
    def check_title(self):
        exists_title = self.env['kw_onboarding_handbook'].search([('title', '=', self.title), ('id', '!=', self.id)])
        if exists_title:
            raise ValueError('Exists ! Already a Handbook Title exists in this name')

    @api.model
    def get_default_image(self):
        icon = False
        img_path = get_module_resource('kw_handbook', 'static/img', 'no_icon_image.jpg')
        if img_path:
            with open(img_path, 'rb') as f:
                icon = f.read()
        return base64.b64encode(icon)

    @api.model
    def create(self, vals):
        if not vals.get('icon'):
            vals['icon'] = self.get_default_image()

        record = super(kw_onboarding_handbook, self).create(vals)

        if record.email_to is True:
            log = self.env['kw_policy_document_log'].sudo().search([('get_handbook_id', '=', record.id)])
            if not log:
                self.env['kw_policy_document_log'].sudo().create({'get_handbook_id': record.id,
                                                                  'active': True})

        if record:
            self.env.user.notify_success(message='Handbook created successfully.')
        else:
            self.env.user.notify_danger(message='Handbook creation failed.')
        return record

    @api.multi
    def write(self, vals):
        # print("=====================", vals)
        handbook_type_id = self.handbook_type_id.code
        handbook_type = self.check_officer_access(handbook_type_id)

        res = super(kw_onboarding_handbook, self).write(vals)
        if self.email_to is True:
            log = self.env['kw_policy_document_log'].sudo().search([('get_handbook_id', '=', self.id)])
            if not log:
                log.create({'get_handbook_id': self.id,
                            'active': True})

        if not self.icon:
            self.icon = self.get_default_image()
        if res:
            self.env.user.notify_success(message='Handbook updated successfully.')
        else:
            self.env.user.notify_danger(message='Handbook update failed.')
        return res

    @api.multi
    def handbook_send_weekly_mail(self):
        log_data = self.env['kw_policy_document_log'].sudo().search([])
        all_handbooks = log_data.filtered(lambda x: x.get_handbook_id.view_access == 'All')
        specific_handbooks = log_data.filtered(lambda x: x.get_handbook_id.view_access == 'Specific')
        if all_handbooks.exists():
            mail_to_all = ','.join(
                self.env['hr.employee'].search([('active', '=', True), ('employement_type.code', '!=', 'O')]).mapped('work_email'))
            # total_mail = len(mail_to_all)
            # group_size = 60
            # for i in range(0, total_mail, group_size):
            #     group = mail_to_all[i:i+group_size]
            #     print(group,"group=================================================")
            db_name = self._cr.dbname
            handbook_view = self.env.ref('kw_handbook.kw_handbook_form_view').id
            action_id = self.env.ref("kw_handbook.kw_handbook_actions_window").id
            template_id = self.env.ref('kw_handbook.kw_onboarding_handbook_mail_template')
            template_id.with_context(email_to=mail_to_all, records=all_handbooks, db_name=db_name, view=handbook_view,
                                     action_id=action_id
                                     ).send_mail(all_handbooks[0].id,
                                                 notif_layout="kwantify_theme.csm_mail_notification_light")
            all_handbooks.write({'active': False})

    @api.constrains('icon')
    def check_icon(self):
        icon_type = ['image/jpeg', 'image/jpg', 'image/png']
        if self.icon:
            mimetype = guess_mimetype(base64.b64decode(self.icon))
            if str(mimetype) not in icon_type:
                raise ValidationError("Unsupported file format ! allowed file formats are .jpg , .jpeg , .png ")
            elif ((len(self.icon) * 3 / 4) / 1024) / 1024 > 0.5:
                raise ValidationError("Maximum file size should be less than 500 kb.")

    @api.constrains('title')
    def check_name(self):
        exists_name = self.env['kw_onboarding_handbook'].search(
            [('title', '=', self.title), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("The category name" + '"' + self.title + '"' + " already exists.")

    @api.depends('description')
    def _compute_display_description(self):
        for rec in self:
            rec.display_description = (rec.description[:90] + '...') if len(rec.description) > 80 else rec.description

    @api.depends('category')
    def _compute_count_category(self):
        for rec in self:
            if rec:
                rec.category_count = self.search_count([('handbook_type_id', '=', rec.handbook_type_id.id)])
                # print(("-----",rec.category_count))

    @api.model
    def default_get(self, fields):
        res = super(kw_onboarding_handbook, self).default_get(fields)
        type_code = self.env.context.get('default_handbook_type_id')
        handbook_type = self.check_officer_access(type_code)
        res['handbook_type_id'] = handbook_type.id
        return res
    
    def check_officer_access(self, type_code):
        # type_code = self.env.context.get('default_handbook_type_id')
        # print("self.env.context >>> ",type_code, self.env.context)
        handbook_type = self.env['kw_handbook_type'].sudo().search([('code', '=', type_code)])
        # print("handbook_type >>>> ", handbook_type, self.env.user.employee_ids , handbook_type.emp_id)
        if self.env.user.has_group('kw_handbook.groups_handbook_officer'):
            if (not handbook_type.emp_id.exists()) or \
                    (handbook_type.emp_id.exists() and self.env.user.employee_ids not in handbook_type.emp_id):
                raise Warning(f"You are not allowed to manage {handbook_type.name} documents.")
        return handbook_type


class kw_handbook(models.Model):
    _name = "kw_handbook"
    _description = "kw_handbook"
    _rec_name = 'handbook_id'

    title = fields.Char(string="Title", related='handbook_id.title', store=True)
    # category = fields.Many2one('kw_onboarding_handbook_category')
    document_type = fields.Selection(selection=[('handbook', 'Handbook'),
                                                ('business_rule', 'Business Rule'),
                                                ('department_structure', 'Dep.Structure,CDP & JD'),
                                                ('software_development', 'Software Development Process')
                                                ], string="Document Type")
    handbook_type_id = fields.Many2one('kw_handbook_type', string="Document Type")
    understood = fields.Boolean("Read and Understood", default=True)
    date = fields.Date(string="Date", default=date.today())
    # content_file = fields.Binary(string = "Upload Document")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    handbook_id = fields.Many2one('kw_onboarding_handbook', string="Title")

    @api.model
    def _get_employee_handbook_url(self, user_id):
        emp_handbook_url = f"/employee-handbook"
        return emp_handbook_url


class KwPolicyDocumentLog(models.Model):
    _name = "kw_policy_document_log"
    _description = "Policy Documents"

    active = fields.Boolean("Active")
    get_handbook_id = fields.Many2one('kw_onboarding_handbook')
    handbook_id = fields.Integer(related='get_handbook_id.id', string="Handbook Id")
