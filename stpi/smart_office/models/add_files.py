from odoo import models, api, fields,_
# from odoo.exceptions import ValidationError

class AddFiles(models.Model):
    _inherit = "muk_dms.directory"
    _description = "Add Files"

    # @api.multi
    # def unlink(self):
    #     # for rec in self:
    #     #     if rec.id == self.env.ref('smart_office.smart_office_directory').id or \
    #     #             rec.id == self.env.ref('smart_office.smart_office_directory_root').id:
    #     #         raise ValidationError(_('\"Incoming Files\" and \"Root Directory\" directory cannot be deleted!'))
    #     return super(AddFiles, self).unlink()

    doc_file_date = fields.Date('File Date', default=fields.Date.context_today)
    doc_type_of_file = fields.Text('Type of File')
    doc_file_status = fields.Selection([('normal', 'Normal'),
                                        ('important', 'Important'),
                                        ('urgent', 'Urgent')], default='normal')
    doc_subject_matter = fields.Text('Subject Matter')
    department_id = fields.Many2one('hr.department', 'Department')
    job_position_id = fields.Many2one('hr.job', 'Job Position')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    # doc_file_preview = fields.Binary()


    @api.model
    def create(self, vals):
        if self._context.get('smart_office', False):
            vals['parent_directory'] = self.env.ref('smart_office.smart_office_directory_root').id
            vals['inherit_groups'] = True
        return super(AddFiles, self).create(vals)


    def save_record(self):
        # self.doc_file_preview = self.files[0].content
        return {
            'name': 'Incoming Files',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'muk_dms.directory',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'context': {'tree_view_ref': 'smart_office.view_add_files_incoming_tree'},
        }
        

    def deal_with_file(self):
        return {
            'name': 'Files',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'muk_dms.directory',
            'type': 'ir.actions.act_window',
            # 'target': 'main',
            'res_id': self.id,
            'context': {'form_view_ref': 'smart_office.view_add_files_doc_form_incoming'},
        }
        

    note_log_ids = fields.One2many('muk.note.log', 'note_file_id')
    correspondence_log_ids = fields.One2many('muk.note.log', 'correspondence_file_id')

    # action group
    file_action = fields.Selection([('forward', 'Forward'),
                                    ('closed', 'Closed')], default='forward')
    designation_id = fields.Many2one('muk.designation', 'Designation')
    doc_remarks = fields.Text('Remarks')
    # doc_name = fields.Many2one('muk_dms.directory', 'Name')

    # @api.onchange('doc_name')
    # def compute_doc_name_details(self):
    #     pass

    def print_merged_report(self):
        return self.env['ir.actions.report']._get_report_from_name(
            'smart_office.merged_report_template').report_action(self.id)

    # def get_merged_report_data(self):
    #     pdf_report = self.doc_file_preview

    #     #get pdf to image
    #     import base64

    #     blob = base64.decodebytes(pdf_report)
    #     import subprocess

    #     subprocess.call(['chmod', '0777', 'byte.pdf'])

    #     text_file = open('byte.pdf', 'wb')
    #     text_file.write(blob)
    #     text_file.close()

    #     import os
    #     import tempfile
    #     from pdf2image import convert_from_path

    #     filename = 'byte.pdf'
    #     subprocess.call(['chmod', '0777', filename])
    #     with tempfile.TemporaryDirectory() as path:
    #         images_from_path = convert_from_path(filename, output_folder=path, last_page=1, first_page=0)

    #     base_filename = os.path.splitext(os.path.basename(filename))[0] + '.jpg'

    #     # save_dir = '/opt'
    #     subprocess.call(['chmod', '0777', base_filename])
    #     for page in images_from_path:
    #         page.save(base_filename, 'JPEG')

    #     import base64

    #     with open(base_filename, "rb") as imageFile:
    #         str = base64.b64encode(imageFile.read())

    #     notes = []
    #     for nt in self.note_log_ids:
    #         notes.append(nt.name)

    #     corres = []
    #     for cr in self.correspondence_log_ids:
    #         corres.append(cr.name)

    #     return {'image': str, 'notes': notes, 'corres': corres}


class NoteLog(models.Model):
    _name = "muk.note.log"
    _description = "Note Log"

    name = fields.Html('Note: ')
    note_file_id = fields.Many2one('muk_dms.directory')
    correspondence_file_id = fields.Many2one('muk_dms.directory')

    file_id = fields.Many2one('muk_dms.file')
    type = fields.Selection([('green', 'Green'),
                             ('correspondence', 'Correspondence')])

class Designation(models.Model):
    _name = "muk.designation"
    _description = "Designation"

    name = fields.Char('Name')