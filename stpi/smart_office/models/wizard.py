from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

# class CreateFile(models.TransientModel):
#     _name = "wizard.create.file"
#     _description = "Create wizard file"

#     doc_name = fields.Many2one('muk_dms.directory', 'Name')
#     doc_subject_matter = fields.Text('Subject Matter')
#     doc_file_date = fields.Date('File Date') #, default=fields.Date.context_today)
#     doc_type_of_file = fields.Many2many('muk_dms.tag', 'muk_dms_tag_wiz_rel', 'f1', 'f2')
#     doc_file_status = fields.Selection([('normal', 'Normal'),
#                                         ('important', 'Important'),
#                                         ('urgent', 'Urgent')], default='normal')
#     reference_letter_ids = fields.Many2many('muk_dms.file', 'wizard_create_file_muk_file_rel', 'f1', 'f2', 'Reference')
#     department_id = fields.Many2one('hr.department', 'Department')
#     job_position_id = fields.Many2one('hr.job', 'Job Position')

#     employee_id = fields.Many2one('hr.employee', 'Employee')

#     def save_record(self):
#         # if not self.employee_id.user_id:
#         #     raise ValidationError(_('Please set related user of %s employee selected' % self.employee_id.name))
#         # if self.doc_name.id != self.env.ref('smart_office.smart_office_directory').id:
#         #     raise ValidationError(_('Already Created File for this letter!'))
#         self.doc_name.write(dict(
#             doc_file_date=self.doc_file_date,
#             doc_type_of_file=self.doc_type_of_file,
#             doc_file_status=self.doc_file_status,
#             doc_subject_matter=self.doc_subject_matter,
#             files=[(4, self.reference_letter_ids[0].id)],
#             doc_file_preview=self.reference_letter_ids[0]
#         ))
#         for file in self.reference_letter_ids:
#             file.directory = self.doc_name.id
#         self.env['muk.letter.tracker'].create(dict(
#             type='create',
#             # from_id=False,
#             to_id=self.env.user.id,
#             letter_id=self._context.get('letter_id')
#         ))
#         return {
#             'type': 'ir.actions.act_window_close'
#         }
    
#     @api.onchange('employee_id')
#     def set_job_employee_id_domain(self):
#         set_dom = []
#         if self.job_position_id:
#             set_dom.append(('job_position_id', '=', self.job_position_id.id))
#         if self.department_id:
#             set_dom.append(('department_id', '=', self.department_id.id))
#         record = self.env['hr.employee'].search(set_dom)

#         return {'domain': {'employee_id': [('id', 'in', record.ids)]}}

#     @api.onchange('doc_name')
#     def set_value_doc_name(self):
#         return {'domain': {'doc_name': [('id', '!=', self.env.ref('smart_office.smart_office_directory').id)]}}

#     @api.onchange('doc_name')
#     def compute_wizard_details(self):
#         if self.doc_name:
#             self.doc_type_of_file = [(6, 0, self.doc_name.tags.ids)]
#             self.doc_file_date = str(self.doc_name.create_date)
#             self.doc_file_status = self.doc_name.doc_file_status
#             self.doc_subject_matter = self.doc_name.doc_subject_matter
#             self.employee_id = self.env['hr.employee'].search([('user_id', '=', self.doc_name.create_uid.id)], limit=1).id

# class ForwardFile(models.TransientModel):
#     _name = "wizard.forward.file"
#     _description = "Forward File"

#     department_id = fields.Many2one('hr.department', 'Department')
#     job_position_id = fields.Many2one('hr.job', 'Job Position')

#     employee_id = fields.Many2one('hr.employee', 'Employee')

#     @api.onchange('employee_id')
#     def set_job_employee_id_domain(self):
#         set_dom = []
#         if self.job_position_id:
#             set_dom.append(('job_position_id', '=', self.job_position_id.id))
#         if self.department_id:
#             set_dom.append(('department_id', '=', self.department_id.id))
#         record = self.env['hr.employee'].search(set_dom)

#         return {'domain': {'employee_id': [('id', 'in', record.ids)]}}

#     def save_record(self):
#         current_owner_id = self.env['muk_dms.file'].browse(self._context.get('letter_id')).current_owner_id
#         # if not self.employee_id.user_id:
#         if self.env.user.id != current_owner_id.id:
#             raise ValidationError(_('Current user is not the current owner of the file!'))
#         self.env['muk.letter.tracker'].create(dict(
#             type='forward',
#             from_id=self.env.user.id,
#             to_id=self.employee_id.user_id.id,
#             letter_id=self._context.get('letter_id')
#         ))
#         return {
#             'type': 'ir.actions.act_window_close'
#         }

# class FileTracker(models.Model):
#     _name = "muk.letter.tracker"
#     _description = "Letter Tracker"

#     type = fields.Selection([('create', 'Create'), ('forward', 'Forward')])
#     from_id = fields.Many2one('res.users', 'From')
#     to_id = fields.Many2one('res.users', 'To')

#     letter_id = fields.Many2one('muk_dms.file')

#     @api.model
#     def create(self, vals):
#         res = super(FileTracker, self).create(vals)
#         res.letter_id.current_owner_id = res.to_id.id
#         return res


