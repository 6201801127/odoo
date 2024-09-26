
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools.mimetypes import guess_mimetype
import base64
import re

# start : merged from employee_document_inherit
class DocMaster(models.Model):
    _name = 'hr.employee.document.master'
    _description = 'Employee Doc Master'

    name = fields.Char('Name / नाम')
    description = fields.Char('Description / विवरण')
class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    # start : merged from employee_document_inherit
    name = fields.Many2one('hr.employee.document.master', string='Document Name / दस्तावेज़ का नाम',required=True)

    @api.onchange('name')
    def get_desc_f_n(self):
        for rec in self:
            if rec.name:
                rec.description = rec.name.description
    # end : merged from employee_document_inherit
    # def mail_reminder(self):
    #     """Sending document expiry notification to employees."""

    #     now = datetime.now() + timedelta(days=1)
    #     date_now = now.date()
    #     match = self.search([])
    #     for i in match:
    #         if i.expiry_date:
    #             exp_date = fields.Date.from_string(i.expiry_date) - timedelta(days=7)
    #             if date_now >= exp_date:
    #                 mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + "is going to expire on " + \
    #                                str(i.expiry_date) + ". Please renew it before expiry date"
    #                 main_content = {
    #                     'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
    #                     'author_id': self.env.user.partner_id.id,
    #                     'body_html': mail_content,
    #                     'email_to': i.employee_ref.work_email,
    #                 }
    #                 self.env['mail.mail'].create(main_content).send()
                    

    # @api.constrains('expiry_date')
    # def check_expr_date(self):
    #     for each in self:
    #         if each.expiry_date:
    #             exp_date = fields.Date.from_string(each.expiry_date)
    #             if exp_date < date.today():
    #                 raise Warning('Your Document Is Expired.')

    number = fields.Char(string='Document Number / दस्तावेज़ संख्या', required=True, copy=False, help='You can give your'
                                                                                 'Document number.',tracking=True)
    description = fields.Text(string='Description / विवरण', copy=False ,tracking=True)
    expiry_date = fields.Date(string='Expiry Date / समाप्ति तिथि', copy=False ,tracking=True)
    employee_ref = fields.Many2one('hr.employee','Employee ref / कर्मचारी' ,tracking=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'employee_attachment_rel',
        'employee_id', 'attachment_id',
        string='Attachments / संलग्नक',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    issue_date = fields.Date(string='Issue Date / जारी करने की तिथि', default=fields.Date.today, copy=False,tracking=True)

    @api.constrains('description')
    @api.onchange('description')	
    def _onchange_description(self):
        for rec in self:
            if rec.description and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.description)):
                raise ValidationError("Description should be an alphabet")
            if rec.description:
                if len(rec.description) > 500:
                    raise ValidationError('Number of characters must not exceed 500')

    @api.constrains('issue_date')
    @api.onchange('issue_date')
    def _onchange_issue_date(self):
        date_of_issue = self.issue_date
        if self.issue_date:
            if self.issue_date < date.today() or self.issue_date > date.today():
                raise ValidationError("Document issue date should not be less than current date.")
        
    @api.constrains('expiry_date')
    @api.onchange('expiry_date')
    def _onchange_expiry_date(self):
        if self.expiry_date:
            if self.expiry_date < date.today():
                raise ValidationError("Document expiry date should be either current date or future date")
            
    @api.constrains('number')
    @api.onchange('number')
    def _onchange_number(self):
        if self.number:
            check_alnum = self.number.isalnum() if self.number else True
            if check_alnum == False :
                raise ValidationError("Document number should be alphanumeric")
            
    @api.constrains('attachment_ids')
    def _check_attachment_ids(self):
        if self.attachment_ids:
            print("Attachement==================",self.attachment_ids)
            pass
        else:
            raise ValidationError(_('Please Upload your attachment.'))
        
    @api.constrains('attachment_ids')
    @api.onchange('attachment_ids')
    def _check_uploaded_document(self):
        allowed_file_list = ['application/pdf']
        for rec in self:
            if rec.attachment_ids.datas:
                acp_size = ((len(rec.attachment_ids.datas) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(rec.attachment_ids.datas), default='application/pdf')
                # if str(mimetype) not in allowed_file_list:
                #     raise ValidationError("Only PDF format is allowed")
                if acp_size > 2:
                    raise ValidationError("Document allowed size less than 2MB")

# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'

#     @api.multi
#     def _document_count(self):
#         for each in self:
#             document_ids = self.env['hr.employee.document'].sudo().search([('employee_ref', '=', each.id)])
#             each.document_count = len(document_ids)

#     @api.multi
#     def document_view(self):
#         self.ensure_one()
#         domain = [
#             ('employee_ref', '=', self.id)]
#         return {
#             'name': _('Documents'),
#             'domain': domain,
#             'res_model': 'hr.employee.document',
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'view_mode': 'tree,form',
#             'view_type': 'form',
#             'help': _('''<p class="oe_view_nocontent_create">
#                            Click to Create for New Documents
#                         </p>'''),
#             'limit': 80,
#             'context': "{'default_employee_ref': '%s'}" % self.id
#         }

#     document_count = fields.Integer(compute='_document_count', string='# Documents')

#
# class HrEmployeeAttachment(models.Model):
#     _inherit = 'ir.attachment'
#
#     doc_attach_rel = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
#                                       string="Attachment", invisible=1)
