import os
import base64
# import shutil
import logging
from os import system
import tempfile
from datetime import datetime,date
from PyPDF2 import PdfFileReader

from odoo import models, api, fields ,_
from odoo.addons.muk_utils.tools import file
from odoo.exceptions import ValidationError
logging.getLogger("pdfminer").setLevel(logging.WARNING)

class AddLetter(models.Model):
    _inherit = "muk_dms.file"
    _rec_name = "name"
    _description = "Add Document/Letter"
    _order = "action_time desc"

    current_owner_id = fields.Many2one('res.users', 'Current Owner',default=lambda self:self._uid)
    last_owner_id = fields.Many2one('res.users', 'Last Owner')
    subject = fields.Char("Subject",required=True)

    sec_owner = fields.Many2many('res.users', string='Secondary Owners')
    # srch_id = fields.Many2many('res.users', string='My Search')
    dispatch_id = fields.Many2one('dispatch.document')
    previous_owner = fields.Many2many('res.users', string='Owners')
    previous_owner_emp = fields.Many2many('hr.employee', string='Previous Owners')
    parent_correspondence_id = fields.Many2one('muk_dms.file','Parent')

    # content_binary = fields.Binary(string="Content Binary",attachment=True,prefetch=False,invisible=True)
    content_binary = fields.Binary(string="Content Binary",attachment=True,prefetch=False,invisible=True)

    # Letter Information
    responsible_user_id = fields.Many2one('res.users', default=lambda self:self.env.user.id)
    document_type = fields.Selection([('letter', 'Letter'),('document', 'Document')], default='document')

    sender_type = fields.Many2one('doc.sender.type',' Sender Type')
    delivery_mode = fields.Many2one('doc.delivery.mode', 'Delivery Mode')
    language_of_letter = fields.Many2one('doc.letter.language', 'Language')
    letter_type = fields.Many2one('doc.letter.type', 'Type')
    letter_date = fields.Date('Letter Date')
    php_letter_id = fields.Char('PHP Letter ID')

    doc_enclosure = fields.Selection([('book', 'Book'),
                                     ('service_book', 'Service Book'),
                                     ('cd_dvd', 'CD or DVD')])
    doc_enclosure_detail = fields.Text('Enclosure Details')

    # pdf_file = fields.Binary(string="Content PDF",compute="_compute_pdf_from_binary",store=True,attachment=True)
    pdf_file = fields.Binary(string="Content PDF",store=True,attachment=True)

    # pdf_total_page = fields.Integer("PDF Total Page",compute="_compute_pdf_from_binary",store=True)
    pdf_total_page = fields.Integer("PDF Total Page",store=True)
    # other_extension_converted_to_pdf = fields.Boolean(string="Other Extension Converted ?",compute="_compute_pdf_from_binary",store=True,help="Becomes true if file is successfully converted")
    other_extension_converted_to_pdf = fields.Boolean(string="Other Extension Converted ?",store=True,help="Becomes true if file is successfully converted")

    folder_id = fields.Many2one('folder.master', string="File Number")
    branch_id = fields.Many2one('res.branch', 'Center')

    letter_number = fields.Char('Serial Number')
    letter_no = fields.Char('Letter Number')

    sender_type_related = fields.Char(related='sender_type.name')
    delivery_mode_related = fields.Char(related='delivery_mode.name')
    language_of_letter_related = fields.Char(related='language_of_letter.name')
    letter_type_related = fields.Char(related='letter_type.name')
    other_st = fields.Char('Other (Sender Type)')
    other_dm = fields.Char('Other (Delivery Mode)')
    other_lol = fields.Char('Other (Correspondence Language')
    other_lt = fields.Char('Other (Correspondence Type)')

    # Receipt Information
    doc_receive_m2o = fields.Many2one('doc.rf', string='Doc receive from')
    doc_recieve_from = fields.Selection([('private', 'Private'),
                                         ('govt', 'Government')], default='private')
    doc_type_m2o = fields.Many2one('doc.type', string='Doc Type')
    doc_type = fields.Selection([('organization', 'Organization'),
                                 ('individual', 'Individual'),
                                 ('state', 'State'),
                                 ('central', 'Central')], default='organization')

    doc_organisation_id = fields.Many2one('muk.doc.organisation', 'Organisation')
    doc_sender_id = fields.Many2one('muk.doc.sender', 'Sender Name')
    reciept_mode = fields.Selection([('hand_to_hand', 'Hand to Hand'),
                                     ('email', 'Email'),
                                     ('post', 'Post'),
                                     ('fax', 'Fax'),
                                     ('spl_mess', 'Spl. Messenger')], default='post')
    doc_reciept_date = fields.Date('Inward Received Date', default=fields.Date.context_today)
    doc_subject = fields.Char('Subject')
    doc_remark = fields.Text('Remark')
    doc_state = fields.Many2one('res.country.state', 'State')
    doc_department_id = fields.Many2one('muk.doc.department', 'Department')
    doc_letter_details = fields.Text('Correspondence Details')
    file_holder = fields.Many2one('res.users', string = "File holder")

    sender_ministry = fields.Many2one('doc.sender.minstry',"Ministry")
    sender_department = fields.Many2one('doc.sender.department',"Department")
    sender_name = fields.Char("Sender Name")
    sender_designation = fields.Many2one('doc.sender.designation',"Designation")
    sender_organisation = fields.Char("Organisation")
    sender_address = fields.Many2one('doc.sender.address',"Address")
    sender_address_text = fields.Char("Sender Address",related="sender_address.name")

    sender_city = fields.Many2one('res.city', string="City")
    sender_state = fields.Many2one('res.country.state', string="State")
    sender_country = fields.Many2one('res.country', string="Country",default=lambda self:self.env['res.country'].search([('code','=','IN')],limit=1))
    sender_pincode = fields.Char("Pin Code")
    sender_landline = fields.Char("Landline")
    sender_mobile = fields.Char("Mobile")
    sender_fax = fields.Char("FAX")
    sender_email = fields.Char("Email")
    sender_enclosures = fields.Char("Enclosure")
    sender_remarks = fields.Char("Remarks")

    reference_ids = fields.Many2many('muk_dms.file', 'muk_dms_file_rel', 'field1', 'field2', 'Reference Correspondence', domain="[('id', '!=', id)]")

    forward_from_id = fields.Many2one('res.users', 'Forwarded From',track_visibility='onchange')
    forward_to_id = fields.Many2one('res.users', 'Forwarded To',track_visibility='onchange')
    forwarded_date = fields.Date("Forwarded Date",track_visibility='onchange')

    attach_to_file_date = fields.Date("Attached To File Date",track_visibility='onchange')
    attach_to_file_time = fields.Datetime("Attached To File Time",track_visibility='onchange')
    
    is_removable = fields.Boolean('Removable ?',compute="_compute_if_removable")
    is_current_user = fields.Boolean("Current Owner ?",compute="_compute_current_owner")
    can_preview_attachment = fields.Boolean("Can Preview Attachment ?",compute="_compute_current_owner")
    
    tracking_info_ids = fields.One2many('smart_office.correspondence.tracking', 'correspondence_id', string="Tracking Info")

    userwise_tracking_ids = fields.One2many('userwise.correspondence.tracking','correspondence_id',string="Userwise Tracking")

    remarks = fields.Char('Remarks')

    incoming_source = fields.Selection(selection=[('create','Created'),
                                                 ('cc','CC'),
                                                 ('forward','Forwarded'),
                                                 ('transfer','Transferred'),
                                                 ('pull_inbox','Pulled to Inbox'),
                                                #  ('send_back','Send Back')
                                                 ],string="Action Type")
    action_by_uid = fields.Many2one('res.users','Action By')
    action_time = fields.Datetime('Date & Time')
    action_date = fields.Date("Action Date")

    pdf_text = fields.Text("Extracted Text")
    is_extracted = fields.Boolean("Extracted ?",help="Becomes true once extraction is completed.")
    # index_id = fields.Integer("Lucene Index ID")
    is_indexed = fields.Boolean("Indexed ?",help="Becomes true once indexing is completed.")
    # backup_store_date = fields.Date("Backup Stored Date")
    
    @api.multi
    def convert_or_assign_pdf_file(self):
        corres = self
        if self.content_binary and self.extension:
            temporary_files = []

            corres_store_file_desc, corres_store_path = tempfile.mkstemp(suffix=f'.{corres.extension}', prefix=f'correspondence{corres.id}.tmp.')
            os.close(corres_store_file_desc)
            temporary_files.append(corres_store_path)

            tempfile_name = corres_store_path.rsplit('.',1)[0]
            corres_converted_path = f'{tempfile_name}.pdf'

            total_page = 0

            try:
                conversion_flag = 1
                
                if corres.extension != 'pdf': # convert other documents to pdf.
                    """ to convert office formats to pdf following applications are required
                        1.unoconv 0.7
                        2.python 3.6.9
                        3.LibreOffice 6.0.7.3 """
                    conversion_flag = 0

                    with open(corres_store_path, 'wb') as file_pointer:
                        file_pointer.write(base64.b64decode(corres.content))

                    system(f'unoconv -f pdf {corres_store_path}')

                    temporary_files.append(corres_converted_path)

                    conversion_flag = 1
                else:
                    corres_converted_file_desc, corres_converted_path = tempfile.mkstemp(suffix='.pdf', prefix=f'correspondence{corres.id}.tmp.')
                    os.close(corres_converted_file_desc)
                    temporary_files.append(corres_converted_path)

                    with open(corres_converted_path, 'wb') as file_pointer:
                        file_pointer.write(base64.b64decode(corres.content))

            except Exception as e:
                print(e)

            if conversion_flag == 1: # correspondence has converted to valid file
                corres.pdf_file = base64.b64encode(open(corres_converted_path, "rb") .read())
                corres.other_extension_converted_to_pdf = True

                pdf = PdfFileReader(open(corres_converted_path, 'rb'),strict=False)
                total_page = pdf.getNumPages()

            else:
                corres.pdf_file = False
                corres.other_extension_converted_to_pdf = False


            corres.pdf_total_page = total_page

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)

    @api.multi
    def action_preview_correspondence(self):
        if not self.other_extension_converted_to_pdf:
            self.convert_or_assign_pdf_file()

    # @api.model
    # def restore_correspondence_data(self):
    #     # print("restore_correspondence_data method called")
    #     table = 'muk_dms_file_backup'
    #     self._cr.execute(f'''select id,pdf_file,content_binary from {table}
    #     ''')
    #     data = self._cr.fetchall()
    #     # print("data is--->",data)
    #     for id,pdf_file,content_binary in data:
    #         correspondence = self.browse(id)
    #         if correspondence:
    #             correspondence.write({'pdf_file':pdf_file.tobytes(),'content_binary':content_binary.tobytes(),'other_extension_converted_to_pdf':True})

    # start: overriden from muk_dms module
    @api.constrains('name', 'doc_reciept_date', 'letter_date')
    def _check_name(self):
        for record in self:
            if not file.check_name(record.name):
                raise ValidationError(_("The file name is invalid."))
            if record.doc_reciept_date and record.doc_reciept_date > fields.Date.today():
                raise ValidationError(_("The received date can not be a future date."))
            if record.letter_date and record.letter_date > record.doc_reciept_date:
                raise ValidationError(_("The letter date can not be greater than received date."))
    # end : overriden from muk_dms module

    # start: overriden from muk_dms module
    @api.onchange('category')
    def _change_category(self):
        pass
    # end : overriden from muk_dms module

    @api.constrains('content_binary')
    def validate_file_size(self):
        for correspondence in self:
            if correspondence.content_binary:

                file_size = (len(correspondence.content_binary) * 3 / 4)
                file_size_mb = (file_size / 1024) / 1024

                if file_size_mb > 40.00:
                    raise ValidationError("Please upload file upto size 40 MB")

    @api.model
    def extract_text_from_pdf(self):
        try:
            import cv2
            import pdfplumber
            import pytesseract
            import numpy as np
            from pdf2image import convert_from_path

        except ImportError:
            raise ValidationError("libraries are not available.")
        not_extracted_correspondences = self.search([('pdf_file','!=',False),('is_extracted','=',False),('folder_id','!=',False)])
        # print("not extracted correspondences are-->",not_extracted_correspondences)
        temporary_files = []
        for correspondence in not_extracted_correspondences:
            correspondence_file_desc, correspondence_store_path = tempfile.mkstemp(suffix='.pdf', prefix=f'extract_corres{correspondence.id}.tmp.')
            os.close(correspondence_file_desc)
            temporary_files.append(correspondence_store_path)

            with open(correspondence_store_path, 'wb') as file_pointer:
                file_pointer.write(base64.b64decode(correspondence.pdf_file))

            # physical file of correspondence is ready 
            # tesseract_config = "-l Devanagari+eng --psm 6"
            tesseract_config = "-l eng"

            pdf_text = ''
            try:
                with pdfplumber.open(correspondence_store_path) as pdf:
                    for index,page in enumerate(pdf.pages,start=1):
                        # page_text = ' '.join(page.extract_text().split())
                        page_text = ''
                        if not page_text:
                            print(f"pdfplumber detected no text for correspondence id {correspondence.id}")
                            # page may have scanned contents, apply tesseract
                            page_image = convert_from_path(correspondence_store_path,350,first_page=index,last_page=index,strict=False)[0]
                            page_image_path = f'{tempfile.gettempdir()}/correspondence_{correspondence.id}_page_{index}.jpg'
                            page_image.save(page_image_path, 'JPEG')
                            # image is stored in page_image_path
                            temporary_files.append(page_image_path)
                            # print("page image path is--->",page_image_path)
                            # Read image using opencv
                            page_image = cv2.imread(page_image_path)
                            page_image = cv2.resize(page_image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
                            page_image = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)

                            # Apply dilation and erosion to remove some noise
                            kernel = np.ones((1, 1), np.uint8)
                            page_image = cv2.dilate(page_image, kernel, iterations=1)
                            page_image = cv2.erode(page_image, kernel, iterations=1)

                            # Apply blur to smooth out the edges
                            page_image = cv2.GaussianBlur(page_image, (5, 5), 0)

                            # Apply threshold to get image with only b&w (binarization)
                            page_image = cv2.threshold(page_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                            tesseract_text = pytesseract.image_to_string(page_image,config=tesseract_config)

                            # tesseract_text = pytesseract.image_to_string(cv2.imread(page_image_path),config=tesseract_config)
                            page_text = ' '.join(tesseract_text.split())

                        pdf_text += f' {page_text}' if pdf_text else page_text

                correspondence.write({'pdf_text': pdf_text,'is_extracted': True})
            except Exception:
                continue

        # # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)
    
    @api.model
    def index_correspondences(self):
        unindexed_correspondences = self.search([('is_indexed','=',False),('pdf_text','!=',False),('is_extracted','=',True)])
        if unindexed_correspondences:
            try:
                print("Processing indexing with lucene...")
                import lucene
                from java.util import Arrays
                from java.nio.file import Paths

                from org.apache.lucene.analysis import CharArraySet
                from org.apache.lucene.analysis.standard import StandardAnalyzer
                from org.apache.lucene.analysis.en import EnglishAnalyzer
                from org.apache.lucene.analysis.hi import HindiAnalyzer
                from org.apache.lucene.document import Document,Field
                from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
                from org.apache.lucene.document import Document, Field,TextField
                from org.apache.lucene.index import  IndexWriter, IndexWriterConfig, DirectoryReader
                from org.apache.lucene.store import SimpleFSDirectory

                vm_env = lucene.getVMEnv()
                if not vm_env:
                    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
                else:
                    # vm_env = lucene.getVMEnv()
                    vm_env.attachCurrentThread()

                index_directory = self.env.ref('smart_office.smart_office_lucene_index_directory').value
                # print("indexing system parameter--->",index_directory)

                store = SimpleFSDirectory(Paths.get(index_directory))
                writer = None
                # try:
                hindi_stop_words = list(HindiAnalyzer().getStopwordSet())
                english_stop_words = list(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

                stopWords = Arrays.asList(hindi_stop_words + english_stop_words)
                custom_stop_set =  CharArraySet(stopWords, True)

                analyzer = StandardAnalyzer(custom_stop_set)
                analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
                config = IndexWriterConfig(analyzer)

                config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
                # config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

                writer = IndexWriter(store, config)
                index_reader = DirectoryReader.open(writer)
                # total_docs = index_reader.numDocs()
                # print("Initially count of documents....",total_docs)
                print(f"indexing {len(unindexed_correspondences)} notings with lucene.....")

                for correspondence in unindexed_correspondences:
                    doc = Document()
                    doc.add(Field("data", correspondence.pdf_text, TextField.TYPE_STORED))
                    doc.add(Field("correspondence_id", correspondence.id, TextField.TYPE_STORED))
                    writer.addDocument(doc)
                    # correspondence.index_id = index + total_docs
                    correspondence.is_indexed = True

                writer.close()
                store.close()

            except Exception as e:
                print("exception is---->",e)

    @api.multi
    def _compute_current_owner(self):
        for correspondence in self:
            correspondence.is_current_user = correspondence.current_owner_id == self.env.user
            if correspondence.current_owner_id == self.env.user or correspondence.last_owner_id == self.env.user or self.env.user in correspondence.previous_owner_emp.mapped('user_id'):
                correspondence.can_preview_attachment = True

    @api.onchange('name')
    def get_directory_name(self):
        for rec in self:
            directory = self.env['muk_dms.directory'].search([('name', '=', 'Incoming Files')], limit=1)
            rec.directory = directory.id
 
    @api.model
    def create(self, vals):
        temporary_files = []
        if 'content' in vals:
            extension = file.guess_extension(vals['name'])
            if extension == 'pdf':
                corres_store_file_desc, corres_store_path = tempfile.mkstemp(suffix=f".{extension}", prefix=f"correspondence{datetime.now().strftime('%d-%b-%y-%H-%M-%S')}.tmp.")
                os.close(corres_store_file_desc)
                temporary_files.append(corres_store_path)
                
                with open(corres_store_path, 'wb') as file_pointer:
                    file_pointer.write(base64.b64decode(vals['content']))

                pdf = PdfFileReader(open(corres_store_path, 'rb'),strict=False)
                vals['pdf_total_page'] = pdf.getNumPages()

                vals['pdf_file'] = vals['content']

                vals['other_extension_converted_to_pdf'] = True
                
            else:
                vals['pdf_file'] = False
                vals['pdf_total_page'] = 0
                vals['other_extension_converted_to_pdf'] = False

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)

        directory = self.env['muk_dms.directory'].sudo().search([('name', '=', 'Incoming Files')], limit=1)
        vals['directory'] = directory.id
        vals['action_by_uid'] = self._uid
        vals['action_time'] = fields.Datetime.now()
        vals['action_date'] = fields.Date.today()
        vals['branch_id'] = self.env.user.default_branch_id.id

        if not vals.get('dispatch_id',False):
            vals['responsible_user_id'] = self.env.user.id
            vals['last_owner_id'] = self.env.user.id
            vals['current_owner_id'] = self.env.user.id
            vals['incoming_source'] = 'create'

            if not self._context.get('no_serial_generation'):
                current_date = fields.Date.today()
                seq_center_code = self.env.user.default_branch_id.code
                recs = self.search([('doc_reciept_date', '>=', current_date.replace(day=1, month=1)),
                                    ('doc_reciept_date', '<=', current_date.replace(day=31, month=12)),
                                    ('create_uid.default_branch_id', '=', self.env.user.default_branch_id.id)])
                padded_seq_number = str(len(recs) + 1).zfill(5)
                vals['letter_number'] = f"{seq_center_code}/{current_date.strftime('%Y')}/{padded_seq_number}"

        res = super(AddLetter, self).create(vals)

        if res.content:
            correspondence_backup_store_path = f'correspondence_backup'
            if not os.path.exists(correspondence_backup_store_path):
                os.makedirs(correspondence_backup_store_path)

            # current_date_backup_path = f'{correspondence_backup_store_path}/{date.today().strftime("%d-%b-%Y")}/{res.id}'
            current_date_backup_path = f'{correspondence_backup_store_path}/{date.today().strftime("%d-%b-%Y")}'
            if not os.path.exists(current_date_backup_path):
                os.makedirs(current_date_backup_path)
            
            backup_file_name = f'{current_date_backup_path}/{res.id}_{res.letter_number.replace("/","-")}.{res.extension}'
            with open(backup_file_name, 'wb') as fp:
                fp.write(base64.b64decode(res.content))

            # res.backup_store_date = date.today()

        if not self._context.get('no_log_record'):

            self.env['smart_office.correspondence.tracking'].create({
                'correspondence_id': res.id,
                'action_stage_id': self.env.ref('smart_office.corres_stage_created').id,
                'remark': res.sender_remarks
            })
            self.env['userwise.correspondence.tracking'].create({
                'correspondence_id': res.id,
                'action_stage_id': self.env.ref('smart_office.userwise_corres_create_self').id,
                'user_id': self.env.user.id,
                'remark': res.sender_remarks
            })
            self.env.user.notify_success("Correspondence created successfully.")
            
        # if self._context.get('smart_office_incoming_letter', False):
        #     self.env['muk.letter.tracker'].create(dict(
        #         type='create',
        #         # from_id=False,
        #         to_id=self.env.user.id,
        #         letter_id=res.id
        #     ))
            # res.directory.doc_file_preview = res.content

        return res

    @api.multi
    def write(self, vals):
        temporary_files = []
        if 'content' in vals:
            file_name = 'name' in vals and vals['name'] or self[0].name
            extension = file.guess_extension(file_name)
            # print("extension in write",extension)
            if extension == 'pdf':
                corres_store_file_desc, corres_store_path = tempfile.mkstemp(suffix=f".{extension}", prefix=f"correspondence{datetime.now().strftime('%d-%b-%y-%H-%M-%S')}.tmp.")
                os.close(corres_store_file_desc)
                temporary_files.append(corres_store_path)
                
                with open(corres_store_path, 'wb') as file_pointer:
                    file_pointer.write(base64.b64decode(vals['content']))

                pdf = PdfFileReader(open(corres_store_path, 'rb'),strict=False)
                vals['pdf_total_page'] = pdf.getNumPages()

                vals['pdf_file'] = vals['content']

                vals['other_extension_converted_to_pdf'] = True
                # print("PDF total page is-->",vals['pdf_total_page'])
            else:
                vals['pdf_file'] = False
                vals['pdf_total_page'] = 0
                vals['other_extension_converted_to_pdf'] = False

            correspondence_backup_store_path = f'correspondence_backup'
            if not os.path.exists(correspondence_backup_store_path):
                os.makedirs(correspondence_backup_store_path)
            
            current_date_backup_path = f'{correspondence_backup_store_path}/{date.today().strftime("%d-%b-%Y")}'
            if not os.path.exists(current_date_backup_path):
                os.makedirs(current_date_backup_path)
            
            backup_file_name = f'{current_date_backup_path}/{self[0].id}_{self[0].letter_number.replace("/","-")}.{extension}'
            with open(backup_file_name, 'wb') as fp:
                fp.write(base64.b64decode(vals['content']))

            # backup_store_date = self[0].backup_store_date
            # if backup_store_date:
            #     backup_date_path = f'{correspondence_backup_store_path}/{backup_store_date.strftime("%d-%b-%Y")}/{self.ids[0]}'
            #     shutil.rmtree(backup_date_path, ignore_errors=False)
            # backup_path = f'{correspondence_backup_store_path}/{backup_store_date.strftime("%d-%b-%Y")}/{self.ids[0]}'
                # if os.path.isdir(backup_path):
                    # delete path
            # new_store_path = f'{correspondence_backup_store_path}/{date.today().strftime("%d-%b-%Y")}/{self.ids[0]}/{self.ids[0]}_{self[0].letter_number.replace("/","-")}.{extension}'
            # with open(backup_file_name, 'wb') as fp:
            #     fp.write(base64.b64decode(res.content))

            # res.backup_store_date = date.today()
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)
        res = super(AddLetter, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.forwarded_date:
                raise ValidationError(_('You cannot delete a forwarded correspondence.'))
        res = super().unlink()
        return res

    @api.multi
    def _compute_if_removable(self):
        for correspondence in self:
            if not correspondence.dispatch_id and correspondence.folder_id and correspondence not in correspondence.folder_id.file_ids_m2m:
                correspondence.is_removable = True
    
    @api.multi
    def open_popup(self):
        return {'name': 'Remarks',
                'view_type': 'form',
                'views': [(self.env.ref('smart_office.view_popup_remark_form').id, 'form')],
                'view_id': self.env.ref('smart_office.view_popup_remark_form').id,
                'res_model': 'muk_dms.file',
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
        }
    
    @api.multi
    def remove_from_file(self):
        
        self.env['smart_office.correspondence.tracking'].create({
            'correspondence_id': self.id,
            'action_stage_id': self.env.ref('smart_office.corres_stage_file_removed').id,
            'remark': self.remarks
        })
        self.folder_id = False
        self.env.user.notify_success("Correspondence removed successfully.")

    @api.onchange('sender_country')
    def set_state_domain(self):
        domain = [('id','=',False)]
        if self.sender_country:
            domain = [('country_id','=',self.sender_country.id)]
            if self.sender_state and self.sender_state.country_id != self.sender_country:
                self.sender_state = False
        else:
            self.sender_state = False
        return {'domain':{'sender_state':domain}}

    @api.onchange('sender_state')
    def set_city_domain(self):
        domain = [('id','=',0)]
        if self.sender_state:
            domain = [('state_id','=',self.sender_state.id)]
            if self.sender_city and self.sender_city.state_id != self.sender_state:
                self.sender_city = False
        else:
            self.sender_city = False
        return {'domain':{'sender_city':domain}}

    @api.multi
    def action_view_file(self):
        form_view = self.env.ref('smart_office.foldermaster_form_view')
        tree_view = self.env.ref('smart_office.foldermaster_tree_view1')
        return {
            'domain': str([('id', '=', self.folder_id.id)]),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'folder.master',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': self.folder_id.id,
            'target': 'current',
            'nodestroy': True
        }

    @api.multi
    def tracker_view_letter(self):
        return {
            'name': 'Tracking Info',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'smart_office.correspondence.tracking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('correspondence_id', '=', self.id)]
        }

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        # emp_department_id = current_employee and current_employee.department_id and current_employee.department_id.id or 0

        if "filter_subordinates" in self._context:
            args+= [('current_owner_id.employee_ids', 'child_of', self.env.user.employee_ids.ids)]
        return super(AddLetter, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

    @api.onchange('sender_ministry')
    def change_sender_minstry(self):
        if not self.sender_ministry or (self.sender_address and self.sender_address.minstry != self.sender_ministry):
            self.sender_address = False
        
        return {'domain': {'sender_address': [('minstry', '=', self.sender_ministry and self.sender_ministry.id or False)]}}


    def smart_office_create_file(self):
        files = [(6, 0, self.ids)]
        return {
            # 'name': 'Print Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'muk_dms.directory',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'form_view_ref': 'smart_office.view_add_files_doc_form',
                        'default_files': files},
        }

    @api.onchange('doc_receive_m2o')
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

    @api.model
    def create(self,vals):
        res = super(SenderType,self).create(vals)
        self.env.user.notify_success("Sender Type Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SenderType, self).write(vals)
        self.env.user.notify_success("Sender Type Saved Successfully.")
        return res

class DeliveryMode(models.Model):
    _name = 'doc.delivery.mode'
    _description='Delivery Mode'

    name = fields.Char('Name')

    @api.model
    def create(self,vals):
        res = super(DeliveryMode,self).create(vals)
        self.env.user.notify_success("Delivery Mode Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(DeliveryMode, self).write(vals)
        self.env.user.notify_success("Delivery Mode Saved Successfully.")
        return res

class LanguageLetter(models.Model):
    _name = 'doc.letter.language'
    _description='Language of Letter'

    name = fields.Char('Name')

    @api.model
    def create(self,vals):
        res = super(LanguageLetter,self).create(vals)
        self.env.user.notify_success("Language Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(LanguageLetter, self).write(vals)
        self.env.user.notify_success("Language Saved Successfully.")
        return res

class LetterType(models.Model):
    _name = 'doc.letter.type'
    _description='Letter Type'

    name = fields.Char('Name')

    @api.model
    def create(self,vals):
        res = super(LetterType,self).create(vals)
        self.env.user.notify_success("Type Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(LetterType, self).write(vals)
        self.env.user.notify_success("Type Saved Successfully.")
        return res

class SenderMinistry(models.Model):
    _name = 'doc.sender.minstry'
    _description='Sender Minstry'

    name = fields.Char('Name')

    @api.model
    def create(self,vals):
        res = super(SenderMinistry,self).create(vals)
        self.env.user.notify_success("Ministry Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SenderMinistry, self).write(vals)
        self.env.user.notify_success("Ministry Saved Successfully.")
        return res

class SenderDepartment(models.Model):
    _name = 'doc.sender.department'
    _description='Sender Department'

    name = fields.Char('Department Name')

    @api.model
    def create(self,vals):
        res = super(SenderDepartment,self).create(vals)
        self.env.user.notify_success("Department Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SenderDepartment, self).write(vals)
        self.env.user.notify_success("Department Saved Successfully.")
        return res

class SenderDesignation(models.Model):
    _name = 'doc.sender.designation'
    _description='Sender Designation'

    name = fields.Char('Department Name')

    @api.model
    def create(self,vals):
        res = super(SenderDesignation,self).create(vals)
        self.env.user.notify_success("Designation Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SenderDesignation, self).write(vals)
        self.env.user.notify_success("Designation Saved Successfully.")
        return res

class SenderAddress(models.Model):
    _name = 'doc.sender.address'
    _description='Sender Address'

    minstry = fields.Many2one('doc.sender.minstry')
    name = fields.Char('Address')

    @api.model
    def create(self,vals):
        res = super(SenderAddress,self).create(vals)
        self.env.user.notify_success("Address Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SenderAddress, self).write(vals)
        self.env.user.notify_success("Address Saved Successfully.")
        return res