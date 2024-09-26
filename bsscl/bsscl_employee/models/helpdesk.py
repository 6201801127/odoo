from odoo import _, api, fields, models, tools
from datetime import datetime, date
from odoo.exceptions import ValidationError,AccessError
import re
import base64
from odoo.tools.mimetypes import guess_mimetype

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _rec_name = 'number'
    _order = 'priority desc, number desc'
    _mail_post_access = "read"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee

    employee_id = fields.Many2one('hr.employee', 'Employee / कर्मचारी', ondelete='cascade', required=True)

    
    number = fields.Char(string='Ticket number / टिकट संख्या', copy=False, default=lambda self: _('New / नया'),
                         readonly=True)
    name = fields.Char(string='Issue Name / जारी करने का नाम', required=True)
    request = fields.Selection([('self', 'Self'), ('others', 'Others')], string="Request For / अनुरोध ", default='self')
    call_type_id = fields.Many2one(comodel_name="helpdesk.calltype.master", string="Call Type / कॉल प्रकार", required=True)
    category_id = fields.Many2one('helpdesk.ticket.category',
                                  string='Category / वर्ग', required=True)
    sub_category = fields.Many2one(string="Sub Category / उप श्रेणी", comodel_name='helpdesk.ticket.subcategory', required=True)
    attachment = fields.Binary(string='Attachment / अटैचमेंट')
    description = fields.Text(string="Description / विवरण",required=True)
    users_email = fields.Char(string='Employee Email / कर्मचारी ईमेल')
    file_name = fields.Char()
    reason = fields.Char(string='Reason / कारण')
    status  = fields.Selection([('draft', 'Draft / प्रारूप'),('applied', 'Applied / लागू'),('approved', 'Approved / अनुमत'),('confirm', 'Confirmed / पुष्टि'),('cancel','Cancelled / रद्द'),('reject', 'Rejected / अस्वीकृत')],string="Status / स्थति",tracking=True)
    priority = fields.Selection(selection=[
        ('0', _('Low')),
        ('1', _('Medium')),
        ('2', _('High')),
        ('3', _('Very High')),
    ], string='Priority / प्राथमिकता', default='1')

#(wagisha) while selecting employee email will be selected default 
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.users_email = self.employee_id.work_email

#(wagisha) for Description validation               
    @api.constrains('description')
    @api.onchange('description')          
    def _check_description_validation(self):
        for rec in self:
            if rec.description:
                if not (re.match('^[ a-zA-Z0-9,-]+$', rec.description)):
                    raise ValidationError("Description should be in alphanumeric only")
                if len(rec.description)>500:
                    raise ValidationError("Description should not be greater than 500")
                
#(wagisha) while selecting Request For Employee will be selcted
    @api.onchange('request', )
    def _onchange_request(self):
        if self.request == 'others':
            self.employee_id = False
            self.users_email = False
        else:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            self.employee_id = employee

#(wagisha) while selecting category its sub category also coming
    @api.onchange('category_id')
    def onchange_category_id(self):
        for rec in self:
            select_sub_category = {'domain': {'sub_category': [('category_code_id', '=', rec.category_id.id)]}}
            return select_sub_category


#(wagisha) for attachment file validation       
    @api.constrains('attachment')
    @api.onchange('attachment')
    def _check_document_upload(self):
        for rec in self:
            allowed_file = ['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/msword']
            if rec.attachment:
                app_size = ((len(rec.attachment) * 3/4) / 1024) / 1024
                if app_size > 2:
                    raise ValidationError("Document allowed size less than 2MB")
                mimetype = guess_mimetype(base64.b64decode(rec.attachment))
                if str(mimetype) not in allowed_file:
                    raise ValidationError("Only PDF/docx format is allowed")

#(wagisha) for Issue Name validation               
    @api.constrains('name')
    @api.onchange('name')          
    def _check_name_validation(self):
        for rec in self:
            if rec.name:
                if not (re.match('^[ a-zA-Z]+$', rec.name)):
                    raise ValidationError("Issue Name should be alphabets")

#(wagisha) while clicking on Save button it will goes in draft
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket')
        helpdesk_status = super(HelpdeskTicket, self).create(vals)
        helpdesk_status.status = 'draft'
        return helpdesk_status
    
#(wagisha)for apply button
    def apply_btn(self):
        self.status = 'applied'

#(wagisha)for approve button                       
    def approve_btn(self):
        self.status = 'approved'

#(wagisha)for cancel button
    def cancel_btn(self):
        self.status = 'cancel'

#(wagisha)for reject button
    def reject_btn(self):
        if not self.reason:
            raise ValidationError("Please fill the reason")
        self.status = 'reject'

#(wagisha)for confirm button
    def confirm_btn(self):
        self.status = 'confirm'

    class HelpdeskCalltypeMaster(models.Model):

        _name = 'helpdesk.calltype.master'
        _description = 'Helpdesk call type Master'
        _rec_name = 'call_name'

        call_name = fields.Char(string='Name / नाम')

    class HelpdeskCategory(models.Model):
        _name = 'helpdesk.ticket.category'
        _description = 'Helpdesk Ticket Category'

        name = fields.Char(string='Name / नाम', required=True)
        category_code = fields.Char(string='Code / कोड',required=True)

    class HelpdeskSubcategory(models.Model):
        _name = 'helpdesk.ticket.subcategory'
        _description = 'Helpdesk Ticket Sub Category'

        name = fields.Char(string='Name / नाम', required=True)
        category_code_id = fields.Many2one(string="Category / वर्ग",comodel_name='helpdesk.ticket.category',required=True)
