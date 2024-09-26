# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from kw_utility_tools import kw_validations

import re
from odoo.addons.kw_utility_tools import kw_validations, kw_whatsapp_integration


class kw_announcement(models.Model):
    _name = 'kw_announcement'
    _description = "Announcements"
    _rec_name = 'headline'

    category_id = fields.Many2one('kw_announcement_category', string="Category", required=True,
                                  domain="[('id','in',permitted_cat_ids)]")

    def _default_current_user_grp(self):
        cat_list = self._get_permitted_categories()
        return cat_list

    permitted_cat_ids = fields.Many2many(compute='_compute_current_user_grps', string="User Group Ids",
                                         default=_default_current_user_grp, comodel_name='kw_announcement_category', )

    headline = fields.Char(string='Headline', required=True)
    upload_image = fields.Binary(string=u'Upload Image', attachment=True, )

    start_date = fields.Date(string=u'Start Date', default=fields.Date.context_today, required=True)
    expire_date = fields.Date(string=u'Expire Date', default=fields.Date.context_today, required=True)

    company_partner_id = fields.Many2one('res.partner', "Company Partner",
                                         default=lambda self: self.env.user.company_id.partner_id.id)
    broadcast_location = fields.Many2many('res.partner', string=u'Select Location',
                                          domain="[('parent_id', '=', company_partner_id)]")

    broadcasting_group = fields.Many2many('kw_announcement_groups', string='Select Groups')
    # broadcasting_group = fields.Many2many('res.groups', string='Select Groups')
    description = fields.Html(string='Description')
    is_expired = fields.Boolean(string=u'Is Expired', )
    state = fields.Selection([('draft', 'Draft'), ('published', 'Published')], string='Status', default='draft')

    enable_comment = fields.Boolean(related='category_id.enable_comment')
    enable_location = fields.Boolean(related='category_id.is_location_specific')

    no_of_comment = fields.Integer(compute='_compute_comments', string="Number of Comments", help='Number of Comments.')
    comments_ids = fields.One2many(string=u'Comments', comodel_name='kw_announcement_comments',
                                   inverse_name='announcement_id', )
    color = fields.Integer("Color Index", compute="change_color_on_kanban")

    send_mail_option = fields.Boolean(string=u'Send Mail', default=False)

    """ start : added on 31st Dec 2019, By : T Ketaki debadarshini"""
    send_whatsapp_msg = fields.Boolean(string=u'Send WhatsApp Notification', default=False)
    upload_doc = fields.Binary(string=u'Upload Document', attachment=True, )
    file_name = fields.Char(string='Document Name')
    whatsapp_template = fields.Many2one('kw_whatsapp_template', "WhatsApp Template",
                                        domain="[('model_id.model', '=', 'kw_announcement')]",
                                        ondelete='restrict')
    whatsapp_message = fields.Text(string='Message', related='whatsapp_template.message', readonly=True, store=False)
    """ end : added on 31st Dec 2019, By : T Ketaki debadarshini"""

    """ start : added on 12th Aug 2020, By : Salma Swalahin"""
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    coming_to_office = fields.Selection([('yes', 'Will come'), ('no', 'Will not come')], string='Report to Office',
                                        default='no')
    office_time = fields.Selection(string='Time', selection='_get_time_list')
    category_code = fields.Char(related='category_id.alias')
    """ end : added on 12th Aug 2020, By : Salma Swalahin"""
    contact_ids = fields.Many2many('res.partner', ondelete='cascade')
    active = fields.Boolean(string="Active", default=True)
    
    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=30, second=0, microsecond=0)

        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+30))
            time_list.append((start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p')))
        return time_list

    @api.onchange('category_id')
    def _get_data(self):
        for res in self:
            return {'domain': {'employee_id': [('parent_id', 'in', self.env.user.employee_ids.ids)]}}

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            emp = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))]).name
            if vals.get('coming_to_office') == 'yes':
                time = datetime.strptime(vals.get('office_time'), '%H:%M:%S').strftime('%I:%M %p')
                vals['headline'] = emp + " will come to office by " + time + "."
            elif vals.get('coming_to_office') == 'no':
                vals['headline'] = emp + " will not come to office today."
        new_record = super(kw_announcement, self).create(vals)
        self.env.user.notify_success(message='Announcement created successfully')
        return new_record

    @api.depends('company_partner_id')
    def change_location_domain(self):
        return {'domain': {'broadcast_location': [('parent_id', '=', self.company_partner_id.id)], }}

    @api.depends('state')
    def change_color_on_kanban(self):
        """
        this method is used to change color index base on fee status
        ----------------------------------------
        :return: index of color for kanban view    """
        for record in self:
            color = 0
            if record.state == 'draft':
                color = 3
            elif record.state == 'published':
                color = 0
            record.color = color

    @api.constrains('start_date', 'expire_date')
    def validate_date(self):
        current_date = str(datetime.now().date())
        for record in self:
            if str(record.expire_date) < current_date:
                raise ValidationError("The expire date should not be less than current date.")
            if record.expire_date < record.start_date:
                raise ValidationError("The expire date should be equal or greater than start date.")

    @api.constrains('broadcast_location')
    def validate_location(self):
        for record in self:
            if record.enable_location and not record.broadcast_location:
                raise ValidationError("Please select at least one location")

    """ validate category , permitted category announcement is only applicable"""
    @api.constrains('category_id')
    def _validate_category(self):
        for record in self:
            if self.env.user.has_group('kw_announcement.group_kw_announcement_manager') or self.env.user.id == SUPERUSER_ID:
                pass
            elif record.category_id.assigned_groups not in self.env.user.groups_id and self.env.user.has_group('kw_announcement.group_kw_announcement_publisher'):
                raise ValidationError(
                    "You are not allowed to create announcement against category " + record.category_id.name)

    @api.constrains('upload_image')
    def _check_uploaded_image(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if self.upload_image:
            kw_validations.validate_file_mimetype(self.upload_image, allowed_file_list)
            kw_validations.validate_file_size(self.upload_image, 5)

    @api.constrains('upload_doc')
    def _check_uploaded_document(self):
        allowed_file_list = ['application/pdf']
        if self.upload_doc:
            kw_validations.validate_file_mimetype(self.upload_doc, allowed_file_list)
            kw_validations.validate_file_size(self.upload_doc, 20)

    @api.constrains('whatsapp_template')
    def validate_whatsapp_template(self):
        for record in self:
            if record.send_whatsapp_msg and not record.whatsapp_template:
                raise ValidationError("Please select whatsApp template")

    @api.multi
    def return_to_draft(self):
        self.state = 'draft'

    """ send mail if the option is selected so and change the status"""
    @api.multi
    def publish(self):
        self.state = 'published'
        attachement_id = 0
        if self.upload_doc and (self.send_mail_option or self.send_whatsapp_msg):
            sql_query = '''
                SELECT id  FROM ir_attachment
                WHERE res_model ='{res_model}' and res_id ={res_id} and name ='{name}' ;
            '''.format(
                res_model='kw_announcement', res_id=self.id, name='upload_doc'
            )

            self.env.cr.execute(sql_query, [])
            for val in self.env.cr.fetchall():
                attachement_id = val[0]

            if attachement_id:
                attachment_data = self.env['ir.attachment'].browse([attachement_id])
                attachment_data.generate_access_token()

                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                doc_url = '%s/web/content/%s?access_token=%s' % (
                    base_url, attachment_data.id, attachment_data.access_token)
                # print(doc_url)
        if self.send_mail_option:
            template = self.env.ref('kw_announcement.kw_announcement_email_template')
            email_to = self.get_announcement_email_to()
            list_email_to = list(email_to.split(","))
            if list_email_to:
                for to in list_email_to:
                    if template:
                        mail_values = {
                            'email_to': to
                        }
                        template.write(mail_values)
                        template_data = self.env['mail.template'].browse(template.id)
                        """ send attachment if any"""
                        if self.upload_doc and attachement_id:
                            template_data.attachment_ids = [(6, 0, [attachement_id])]
                        template_data.send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)

        """ send whatsapp notification for news letter"""
        if self.send_whatsapp_msg and self.whatsapp_template and self.upload_doc:
            if self.whatsapp_template.name == 'announcements' and doc_url:
                whatsapp_message = self.whatsapp_template.message  #
                self.sendwhatsAppmessage(whatsapp_message, doc_url)
        # self.env.user.notify_success(message=self.headline +' <i class="fa fa-folder"></i>'+'<br>
        # Announcement has published by ' +'<br>'+ str(self.env.user.name_get()[0][1]) +'.
        # <i class="fa fa-user"></i>')

    # @api.depends('comments_ids')
    @api.multi
    def _compute_comments(self):
        for record in self:
            record.no_of_comment = len(record.comments_ids)

    @api.multi
    def _compute_current_user_grps(self):
        self.cur_user_grp_ids = self._get_permitted_categories()

    @api.multi
    def get_announcement_email_to(self):

        email_list = []
        emp_list = []
        employee_model = self.env['hr.employee']

        if self.enable_location:
            emp_list = employee_model.search(
                [('work_location_id', 'in', [loc.id for loc in self.broadcast_location]),
                 ('work_email', '!=', False)])
        else:
            if len(self.broadcasting_group) > 0:
                # for grp_rec in
                emp_list = employee_model.search(
                    [('user_id', 'in', [user.id for user in self.broadcasting_group.users]),
                     ('work_email', '!=', False)])
            elif not self.contact_ids:
                emp_list = employee_model.search([('work_email', '!=', False)])

        if emp_list:
            email_list = [emp.work_email for emp in emp_list if emp.work_email]
        if self.contact_ids:
            email_list.extend([to.email for to in self.contact_ids if to.email])

        # print(",".join(email_list))
        return ",".join(email_list)

    def _get_permitted_categories(self):
        category_list = self.env['kw_announcement_category'].search([])
        if self.env.user.has_group('kw_announcement.group_kw_announcement_manager') or self.env.user.id == SUPERUSER_ID:
            cat_list = [cat_rec.id for cat_rec in category_list]
        else:
            cat_list = [cat_rec.id for cat_rec in category_list if cat_rec.assigned_groups in self.env.user.groups_id]
        return cat_list

    @api.multi
    def sendwhatsAppmessage(self, whatsapp_message, doc_url):
        employee_model = self.env['hr.employee']

        if self.enable_location:
            employee_rec = employee_model.search(
                [('work_location_id', 'in', [loc.id for loc in self.broadcast_location])], )
        else:
            if len(self.broadcasting_group) > 0:
                employee_rec = employee_model.search(
                    [('user_id', 'in', [user.id for user in self.broadcasting_group.users])], )
            else:
                employee_rec = employee_model.search([])

        if employee_rec:
            kw_whatsapp_message_log_model = self.env['kw_whatsapp_message_log']
            kw_whatsapp_message_log_data = []
            for employee in employee_rec:
                if employee.whatsapp_no:
                    # print(whatsapp_message)
                    try:
                        message = whatsapp_message.format(url=doc_url, name=employee.name)
                        mobile_no = '+91' + employee.whatsapp_no
                        kw_whatsapp_message_log_data.append({'mobile_no': mobile_no, 'message': message})
                    except Exception as e:
                        raise Warning("Some error occurred while sending whatsApp notification: %s" % str(e))

            if len(kw_whatsapp_message_log_data) > 0:
                kw_whatsapp_message_log_model.create(kw_whatsapp_message_log_data)


    @api.constrains('contact_ids','broadcasting_group','send_mail_option','send_whatsapp_msg')
    def _check_sender_list(self):
        for record in self:
            # if record.category_id.alias != 'new_joinee':
            if record.send_mail_option or record.send_whatsapp_msg:
                if len(record.broadcasting_group) == 0 and len(record.contact_ids) == 0:
                    raise ValidationError('Please add audience or contacts.')
