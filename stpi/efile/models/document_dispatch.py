from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
import base64
import requests
import json


class DispatchDocument(models.Model):
    _name = 'dispatch.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Dispatch Document'
    _rec_name = 'name'

    name = fields.Float('Number')
    cooespondence_ids = fields.Many2many('muk_dms.file', string='Correspondence', track_visibility='always')
    current_user_id = fields.Many2one('res.users', track_visibility='always')
    branch_id = fields.Many2one('res.branch', 'Branch', track_visibility='always')
    department_id = fields.Many2one('hr.department', 'Department', track_visibility='always')
    job_id = fields.Many2one('hr.job', 'Job Position', track_visibility='always')
    created_on = fields.Date(string='Date', default = fields.Date.today(), track_visibility='always')
    select_template = fields.Many2one('select.template.html', track_visibility='always')
    template_html = fields.Html('Template', track_visibility='always')
    basic_version = fields.Float('Basic Version')
    print_heading = fields.Char('Heading')
    dispatch_mode_ids = fields.One2many('dispatch.document.mode','dispatch_id',string='Dispatch Mode')

    version = fields.Many2one('dispatch.document', string='Version', track_visibility='always')
    previousversion = fields.Many2one('dispatch.document', string='Previous  Version', track_visibility='always')

    folder_id = fields.Many2one('folder.master', string="File", track_visibility='always')
    dispatch_mode = fields.Selection(
        [('hand_to_hand', 'Hand to Hand'),('email', 'Email'), ('fax', 'Fax'), ('splmess', 'Spl. Messenger'), ('post', 'Post')
         ], string='Dispatch Mode', track_visibility='always')
    enter_mode = fields.Char('Enter Mode of Dispatch')
    state = fields.Selection(
        [('draft', 'Draft'),('obsolete', 'Obsolete'), ('reject', 'Reject'), ('ready_for_dispatched', 'Ready for Dispatch'), ('dispatched', 'Dispatched')
         ], required=True, default='draft', string='Status', track_visibility='always')



    @api.multi
    def button_edit(self):
        for rec in self:
            cout = 0
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            dis_name = self.env['dispatch.document'].sudo().search([('folder_id', '=', self.folder_id.id),('basic_version', '=', self.basic_version)])
            m_name = self.env['dispatch.document'].sudo().search([('folder_id', '=', self.folder_id.id)])
            for ct in m_name:
                cout+=1
            if cout <1:
                name = 1
            else:
                name = rec.name
            dd = self.env['dispatch.document'].create({
                'name': name + 0.001,
                'basic_version': int(rec.name),
                'previousversion': rec.id,
                'dispatch_mode': rec.dispatch_mode,
                'template_html': rec.template_html,
                'select_template': rec.select_template.id,
                'current_user_id': current_employee.user_id.id,
                'department_id': current_employee.department_id.id,
                'job_id': current_employee.job_id.id,
                'branch_id': current_employee.branch_id.id,
                'created_on': datetime.now().date(),
                'folder_id': rec.folder_id.id,
                'state': 'draft',
                'cooespondence_ids': rec.cooespondence_ids.ids,
            })
            dd.version = dd.id
            # rec.sudo().button_obsellete()
            form_view = self.env.ref('smart_office.document_dispatch_form_view')
            tree_view = self.env.ref('smart_office.dispatch_document_tree_view1')
            value = {
                'domain': str([('id', '=', dd.id)]),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'dispatch.document',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': dd.id,
                'target': 'new',
                'nodestroy': True
            }
            return value


    @api.multi
    def button_obsellete(self):
        for rec in self:
            rec.write({'state': 'obsolete'})

    @api.multi
    def button_ready_for_dispatch(self):
        for rec in self:
            dis_name = self.env['dispatch.document'].sudo().search([('id', '!=', rec.id),('folder_id', '=', rec.folder_id.id),('basic_version', '=', rec.basic_version)])
            for dd in dis_name:
                dd.sudo().button_obsellete()
            rec.write({'state': 'ready_for_dispatched'})



    @api.multi
    def print_dispatch_document(self):
        return self.env.ref('smart_office.dispatch_document_status_print').report_action(self)


    def action_create_correspondence(self):
        pdf = self.env.ref('smart_office.dispatch_document_status_print').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        directory = self.env['muk_dms.directory'].sudo().search([('name', '=', 'Incoming Files')], limit=1)
        print('============my usr id======================',self.current_user_id.id)
        file = self.env['muk_dms.file'].create({
            'dispatch_id': self.id,
            'name': str(self.print_heading) + '-' + str(self.folder_id.folder_name) + '-' + str(self.name) + '.pdf',
            'content': b64_pdf,
            'directory': directory.id,
            'write_uid': self.current_user_id.id,
            'create_uid': self.current_user_id.id,
            'responsible_user_id': self.current_user_id.id,
            'current_owner_id': self.current_user_id.id,
            'last_owner_id': self.current_user_id.id,
            'sender_enclosures': "Enclosure Details" + ' *****' + str(self.print_heading) + '-' + str(self.folder_id.folder_name) + '-' + str(self.name) + '.pdf'
        })
        print('===============================mp===============================', file.id)
        self.folder_id.file_ids = [(4, file.id)]
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.current_user_id.id)], limit=1)
        folder = self.env['file.tracker.report'].create({
            'name': str(file.name),
            'type': 'Correspondence',
            'assigned_by': str(current_employee.user_id.name),
            'assigned_by_dept': str(current_employee.department_id.name),
            'assigned_by_jobpos': str(current_employee.job_id.name),
            'assigned_by_branch': str(current_employee.branch_id.name),
            'assigned_date': datetime.now().date(),
            'action_taken': 'assigned_to_file',
            'remarks': self.template_html,
            'details': "Correspondence attached to file {}".format(self.folder_id.folder_name)
        })
        self.folder_id.document_ids = str(self.folder_id.document_ids) + ',' + str(file.php_letter_id)
        data = {
            'assign_name': self.folder_id.folder_name,
            'assign_no': self.folder_id.sequence,
            'assign_date': self.folder_id.date,
            'assign_subject': (self.folder_id.subject.subject),
            'remarks': self.folder_id.description,
            'created_by': self.folder_id.current_owner_id.id,
            'doc_flow_id': 0,
            'wing_id': self.folder_id.department_id.id,
            'section_id': 0,
            'designation_id': self.folder_id.job_id.id,
            'document_ids': self.folder_id.document_ids,
        }
        req = requests.post('http://206.189.129.190/STPI/www/web-service/add-assignment/', data=data,
                            json=None)
        try:
            pastebin_url = req.text
            print('============Patebin url=================', pastebin_url)
            dictionary = json.loads(pastebin_url)
        except Exception as e:
            print('=============Error==========', e)



    @api.multi
    def button_dispatch(self):
        for rec in self:
            rec.sudo().action_create_correspondence()
            rec.write({'state': 'dispatched'})

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'reject'})


class DispatchDocumentMode(models.Model):
    _name = 'dispatch.document.mode'
    _description = 'Dispatch Document'

    dispatch_id = fields.Many2one('dispatch.document', string='Dispatch Document')
    dispatch_mode = fields.Selection(
        [('hand_to_hand', 'Hand to Hand'),('email', 'Email'), ('fax', 'Fax'), ('splmess', 'Spl. Messenger'), ('post', 'Post')
         ], string='Dispatch Mode', track_visibility='always')
    enter_mode = fields.Char('Dispatch Details')
    dispatch_number = fields.Char('Dispatch Number')