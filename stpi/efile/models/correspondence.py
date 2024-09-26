from odoo import models, api, fields,_
from datetime import datetime, date, timedelta
import requests
import json
from PyPDF2 import PdfFileMerger, PdfFileReader
from odoo.exceptions import UserError

class CorrespondenceMaster(models.Model):
    _name = "correspondence.master"
    _description = "Add Document/Correspondence"

    #Owners List
    current_owner_id = fields.Many2one('res.users', 'Current Owner')
    last_owner_id = fields.Many2one('res.users', 'Last Owner')
    secondary_owner_ids = fields.Many2many('res.users', string='Secondary Owners')
    previous_owner_emp = fields.Many2many('hr.employee', string='Previous/Current Owners')

    # Document Dispatch
    dispatch_id = fields.Many2one('dispatch.document')

    # Letter Information
    document_type = fields.Selection([('letter', 'Letter'),
                                      ('document', 'Document')], default='document')

    # Header Information
    content = fields.Binary(string='Content')
    pdf_file = fields.Binary(related='content')
    name = fields.Char(string='Name')
    correspondence_number = fields.Char('Correspondence Number')

    category = fields.Many2one('efile.category')
    tags = fields.Many2one('efile.tags')

    sender_type = fields.Many2one('doc.sender.type', ' Sender Type')
    delivery_mode = fields.Many2one('doc.delivery.mode', 'Delivery Mode')
    language_of_letter = fields.Many2one('doc.letter.language', 'Correspondence Language')
    letter_type = fields.Many2one('doc.letter.type', 'Correspondence Type')
    sender_type_related = fields.Char(related='sender_type.name')
    delivery_mode_related = fields.Char(related='delivery_mode.name')
    language_of_letter_related = fields.Char(related='language_of_letter.name')
    letter_type_related = fields.Char(related='letter_type.name')
    other_st = fields.Char('Other (Sender Type)')
    other_dm = fields.Char('Other (Delivery Mode)')
    other_lol = fields.Char('Other (Correspondence Language')
    other_lt = fields.Char('Other (Correspondence Type)')

    #PHP Information
    php_letter_id = fields.Char('PHP Letter ID')

    # File Details
    file_id = fields.Many2one('file.master', string="File Assigned")

    # Sender Information
    sender_ministry = fields.Many2one('doc.sender.minstry', "Ministry")
    sender_department = fields.Many2one('doc.sender.department', "Department")
    sender_name = fields.Char("Name")
    sender_designation = fields.Many2one('doc.sender.designation', "Designation")
    sender_organisation = fields.Char("Organisation")
    sender_address = fields.Many2one('doc.sender.address', "Address")
    sender_address_text = fields.Text("Sender Address")
    sender_city = fields.Many2one('res.city', string="City")
    sender_state = fields.Many2one('res.country.state', string="State")
    sender_country = fields.Many2one('res.country', string="Country")
    sender_pincode = fields.Char("Pin Code")
    sender_landline = fields.Char("Landline")
    sender_mobile = fields.Char("Mobile")
    sender_fax = fields.Char("FAX")
    sender_email = fields.Char("Email")
    sender_enclosures = fields.Char("Enclosure")
    sender_remarks = fields.Char("Remarks")


    @api.model
    def create(self, vals):
        res = super(CorrespondenceMaster, self).create(vals)
        if not res.dispatch_id:
            # print('============================self.env.user.id===============================',self.env.user.id)
            # print('============================current_owner_id===============================',self.env.user.id)
            vals['last_owner_id'] = res.env.user.id
            vals['current_owner_id'] = res.env.user.id
            res.last_owner_id = res.env.user.id
            res.current_owner_id = res.env.user.id
            # print('============================res.last_owner_id===============================', res.last_owner_id)
            # print('============================res.current_owner_id===============================', res.current_owner_id)

            seq = self.env['ir.sequence'].next_by_code('correspondence.master')
            date = datetime.now().date()
            sequence = str(date.strftime('%Y%m%d')) + '/' + str(seq)
            res.correspondence_number = sequence

            # Calling API
            current_employee = self.env['hr.employee'].search([('user_id', '=', res.env.user.id)], limit=1)
            enclosure_details = str(res.sender_enclosures) + ' *****' + str(res.name)
            data = {
                'document_type': res.document_type,
                'name': int(seq),
                'enclosure_details': enclosure_details,
                'user_id': current_employee.user_id.id,
                'attachment[]': res.content
            }
            # print('==============================name=============================', int(seq))
            # print('==============================enclosure_details=============================', enclosure_details)
            # print('==============================user_id=============================', current_employee.user_id.id)
            # print('==============================res.content=============================', res.content)
            req = requests.post('http://206.189.129.190/STPI/www/web-service/add-letter/', data=data,
                                json=None)
            try:
                print('=====================================================', req)
                pastebin_url = req.text
                print('===========================pastebin_url==========================', pastebin_url)
                dictionary = json.loads(pastebin_url)
                res.php_letter_id = str(dictionary["response"]["letterData"]["id"])
            except Exception as e:
                print('=============Error==========', e)

            # Report
            self.env['file.tracker.report'].create({
                'name': str(res.name),
                'number': str(res.correspondence_number),
                'type': 'Correspondence',
                'created_by': str(current_employee.user_id.name),
                'created_by_dept': str(current_employee.department_id.name),
                'created_by_jobpos': str(current_employee.job_id.name),
                'created_by_branch': str(current_employee.branch_id.name),
                'create_date': datetime.now().date(),
                'action_taken': 'correspondence_created',
                'remarks': res.sender_remarks,
                'details': "Correspondence created on {}".format(datetime.now().date())
            })
            # print('==================================current employee==========================', current_employee.name)
            # print('==================================current employee id==========================',
            #       current_employee.id)
            # print('==================================current employee job id==========================',
            #       current_employee.job_id.name)
            # print('==================================current employee department_id id==========================',
            #       current_employee.department_id.name)
            # print('==================================current employee branch id==========================',
            #       current_employee.branch_id.name)
            #
            return res
        else:
            # print('============================self.env.user.id===============================', self.env.user.id)
            # print('============================dispatch_id.current_user_id===============================', res.dispatch_id.current_user_id.id)
            vals['responsible_user_id'] = res.dispatch_id.current_user_id.id
            vals['last_owner_id'] = res.dispatch_id.current_user_id.id
            vals['current_owner_id'] = res.dispatch_id.current_user_id.id
            vals['create_uid'] = res.dispatch_id.current_user_id.id
            vals['write_uid'] = res.dispatch_id.current_user_id.id
            res.responsible_user_id = res.dispatch_id.current_user_id.id
            res.last_owner_id = res.dispatch_id.current_user_id.id
            res.current_owner_id = res.dispatch_id.current_user_id.id
            res.create_uid = res.dispatch_id.current_user_id.id
            res.write_uid = res.dispatch_id.current_user_id.id

            seq = self.env['ir.sequence'].next_by_code('correspondence.master')
            date = datetime.now().date()
            sequence = str(date.strftime('%Y%m%d')) + '/' + str(seq)
            res.correspondence_number = sequence

            current_employee = self.env['hr.employee'].search([('user_id', '=', res.dispatch_id.current_user_id.id)], limit=1)
            enclosure_details = str(res.sender_enclosures) + ' *****' + str(res.name)
            data = {
                'document_type': res.document_type,
                'name': int(seq),
                'enclosure_details': enclosure_details,
                'user_id': current_employee.user_id.id,
                'attachment[]': res.content
            }
            # print('==============================name=============================', int(seq))
            # print('==============================enclosure_details=============================', enclosure_details)
            # print('==============================user_id=============================', current_employee.user_id.id)
            # print('==============================res.content=============================', res.content)
            req = requests.post('http://206.189.129.190/STPI/www/web-service/add-letter/', data=data,
                                json=None)
            try:
                print('=====================================================', req)
                pastebin_url = req.text
                print('===========================pastebin_url==========================', pastebin_url)
                dictionary = json.loads(pastebin_url)
                res.php_letter_id = str(dictionary["response"]["letterData"]["id"])
            except Exception as e:
                print('=============Error==========', e)

            self.env['file.tracker.report'].create({
                'name': str(res.name),
                'number': str(res.correspondence_number),
                'type': 'Correspondence',
                'created_by': str(current_employee.user_id.name),
                'created_by_dept': str(current_employee.department_id.name),
                'created_by_jobpos': str(current_employee.job_id.name),
                'created_by_branch': str(current_employee.branch_id.name),
                'create_date': datetime.now().date(),
                'action_taken': 'correspondence_created',
                'remarks': res.sender_remarks,
                'details': "Correspondence created on {}".format(datetime.now().date())
            })

            # current_employee = self.env['hr.employee'].search([('user_id', '=', res.current_owner_id.id)], limit=1)
            # print('==================================current employee==========================', current_employee.name)
            # print('==================================current employee id==========================', current_employee.id)
            # print('==================================current employee job id==========================', current_employee.job_id.name)
            # print('==================================current employee department_id id==========================', current_employee.department_id.name)
            # print('==================================current employee branch id==========================', current_employee.branch_id.name)
            return res



    @api.multi
    def action_view_file(self):
        form_view = self.env.ref('efile.foldermaster_form_view')
        tree_view = self.env.ref('efile.foldermaster_tree_view1')
        value = {
            'domain': str([('id', '=', self.folder_id.id)]),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'folder.master',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': self.file_id.id,
            'target': 'current',
            'nodestroy': True
        }
        return value



    @api.multi
    def tracker_view_letter(self):
        for rec in self:
            views_domain = []
            dmn = self.env['file.tracker.report'].search(['|', ('name', '=', rec.name), ('number', '=', rec.correspondence_number)])
            for id in dmn:
                views_domain.append(id.id)
            return {
                'name': 'File Tracking Report',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'file.tracker.report',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', views_domain)]
            }



    @api.onchange('sender_ministry')
    def change_sender_minstry(self):
        if self.sender_ministry == False:
            self.sender_address = False
        else:
            return {'domain': {'sender_address': [('minstry', '=', self.sender_ministry.id)]}}



    @api.onchange('sender_address')
    @api.constrains('sender_address')
    def change_sender_address(self):
        for rec in self:
            if rec.sender_address:
                rec.sender_address_text = rec.sender_address.name


    def efile_create_file(self):
        files = [(6, 0, self.ids)]
        return {
            # 'name': 'Print Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'muk_dms.directory',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'form_view_ref': 'efile.view_add_files_doc_form',
                        'default_files': files},
        }




    @api.onchange('doc_receive_m2o')
    @api.constrains('doc_receive_m2o')
    def get_doc_receive(self):
        for rec in self:
            rec.doc_type_m2o = False
            if rec.doc_receive_m2o.name == 'Private':
                rec.doc_recieve_from = 'private'
            elif rec.doc_receive_m2o.name == 'Government':
                rec.doc_recieve_from = 'govt'
            else:
                rec.doc_recieve_from = ''

    @api.onchange('doc_type_m2o')
    @api.constrains('doc_type_m2o')
    def get_doc_type(self):
        for rec in self:
            if rec.doc_type_m2o.name == 'Organisation':
                rec.doc_type = 'organization'
            elif rec.doc_type_m2o.name == 'Individual':
                rec.doc_type = 'individual'
            elif rec.doc_type_m2o.name == 'Central':
                rec.doc_type = 'central'
            elif rec.doc_type_m2o.name == 'State':
                rec.doc_type = 'state'
            else:
                rec.doc_type = ''



class Organisation(models.Model):
    _name = "muk.doc.organisation"
    _description = "Organisation"

    name = fields.Char('Organisation Name')


class Sender(models.Model):
    _name = "muk.doc.sender"
    _description = "("

    name = fields.Char('Organisation Name')


class Department(models.Model):
    _name = "muk.doc.department"
    _description = "Department"

    name = fields.Char('Organisation Name')


class DocReceive(models.Model):
    _name = 'doc.rf'
    _description='Doc Receive From'

    name = fields.Char('Doc Receive From')


class DocType(models.Model):
    _name = 'doc.type'
    _description='Doc Receive From'

    name = fields.Char('Doc Type')
    doc_receive_id = fields.Many2one('doc.rf')


class SenderType(models.Model):
    _name = 'doc.sender.type'
    _description='Sender Type'

    name = fields.Char('Name')


class DeliveryMode(models.Model):
    _name = 'doc.delivery.mode'
    _description='Delivery Mode'

    name = fields.Char('Name')


class LanguageLetter(models.Model):
    _name = 'doc.letter.language'
    _description='Language of Letter'

    name = fields.Char('Name')


class LetterType(models.Model):
    _name = 'doc.letter.type'
    _description='Letter Type'

    name = fields.Char('Name')



class SenderMinistry(models.Model):
    _name = 'doc.sender.minstry'
    _description='Sender Minstry'

    name = fields.Char('Name')


class SenderDepartment(models.Model):
    _name = 'doc.sender.department'
    _description='Sender Department'

    name = fields.Char('Department Name')

class SenderDesignation(models.Model):
    _name = 'doc.sender.designation'
    _description='Sender Designation'

    name = fields.Char('Department Name')

class SenderAddress(models.Model):
    _name = 'doc.sender.address'
    _description='Sender Address'
    _rec_name='minstry'

    minstry = fields.Many2one('doc.sender.minstry')
    name = fields.Char('Address')

class EFileCategory(models.Model):
    _name = 'efile.category'
    _description='eFile Cetegory'

    name = fields.Char('Name')

class EFileTags(models.Model):
    _name = 'efile.tags'
    _description='EFile Tags'

    name = fields.Char('Name')

