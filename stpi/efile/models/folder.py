from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
import requests
import json
from odoo.exceptions import UserError

class FolderMaster(models.Model):
    _name = 'folder.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'folder.master'
    _rec_name ='number'

    folder_name = fields.Char(string = 'File Name',track_visibility='always')
    old_file_number = fields.Char(string = 'Old File Number',track_visibility='always')


    current_owner_id = fields.Many2one('res.users', 'Current Owner',track_visibility='always')
    last_owner_id = fields.Many2one('res.users', 'Last Owner',track_visibility='always')

    branch_id = fields.Many2one('res.branch', 'Branch')
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job')

    sec_owner = fields.Many2many('res.users', string='Secondary Owners',track_visibility='always')

    previous_owner = fields.Many2many('res.users', string='Previous/Current Owners',track_visibility='always')

    date = fields.Date(string='Date', default = fields.Date.today(),track_visibility='always')
    subject = fields.Many2one('code.subject', string='Subject',track_visibility='always')
    tags = fields.Many2many('muk_dms.tag', string='Tags',track_visibility='always')
    number = fields.Char(string = 'Number',track_visibility='always')
    status = fields.Selection([('normal', 'Normal'),
                               ('important', 'Important'),
                               ('urgent', 'Urgent')
                               ], string='Status',track_visibility='always')
    sequence = fields.Integer(string = 'Sequence')
    previous_reference = fields.Text('Previous Reference')
    later_reference = fields.Text('Later Reference')
    first_doc_id = fields.Integer(string = 'First Doc Id')
    document_ids = fields.Char(string = 'PHP Letter ids')
    assignment_id = fields.Char(string = 'Assignment ID')
    type = fields.Many2many('folder.type', string = "Type",track_visibility='always')
    description = fields.Text(string = 'Description',track_visibility='always')
    file_ids = fields.One2many('muk_dms.file','folder_id', string = 'Files',track_visibility='always')
    document_dispatch = fields.One2many('dispatch.document','folder_id', string = 'Document Dispatch',track_visibility='always')


    file_ids_m2m = fields.Many2many('muk_dms.file', string = 'Reference',track_visibility='always')
    notesheet_url = fields.Text()
    iframe_dashboard = fields.Text()
    folder_track_ids = fields.One2many('folder.tracking.information', 'create_let_id', string = "Files")
    my_view = fields.Text()
    my_dash = fields.Html('My Dash Html')
    dashboard_view = fields.Many2one('ir.ui.view')
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('closed', 'Closed')
         ], required=True, default='draft', string='Status',track_visibility='always')
    # green_ids = fields.Many2many('green.sheets','folder_id', string = 'Green Sheets')


    @api.model
    def create(self, vals):
        res = super(FolderMaster, self).create(vals)
        print('============================self.env.user.id===============================', self.env.user.id)
        print('============================current_owner_id===============================', self.current_owner_id.id)

        vals['last_owner_id'] = self.env.user.id
        vals['current_owner_id'] = self.env.user.id
        res.current_owner_id = self.env.user.id
        res.last_owner_id = self.env.user.id
        print('============================self.env.user.id new===============================', self.env.user.id)
        print('============================current_owner_id new===============================', res.current_owner_id.id)

        name = ''
        count = 0
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        res.branch_id = current_employee.branch_id.id
        res.department_id = current_employee.department_id.id
        res.job_id = current_employee.job_id.id
        sur_usr = current_employee.branch_id.name
        d_id = current_employee.department_id.stpi_doc_id
        fy = self.env['date.range'].search(
            [('type_id.name', '=', 'Fiscal Year'), ('date_start', '<=', datetime.now().date()),
             ('date_end', '>=', datetime.now().date())], limit=1)
        files = self.env['folder.master'].search(
            [('create_date', '>=', fy.date_start), ('create_date', '<=', fy.date_end), ('department_id', '=', current_employee.department_id.id), ('branch_id', '=', current_employee.branch_id.id), ('subject', '=', res.subject.id)])
        for file in files:
            count += 1
        name = (res.subject.code) + '(' + str(count) + ')/' + str(d_id) + '/' + str(sur_usr) + '/' + str(
                fy.name)
        res.number = str(name)
        self.env['file.tracker.report'].create({
            'name': str(res.folder_name),
            'number': str(res.number),
            'type': 'File',
            'created_by': str(current_employee.user_id.name),
            'created_by_dept': str(current_employee.department_id.name),
            'created_by_jobpos': str(current_employee.job_id.name),
            'created_by_branch': str(current_employee.branch_id.name),
            'create_date': datetime.now().date(),
            'action_taken': 'file_created',
            'remarks': res.description,
            'details': "File created on {}".format(datetime.now().date())
        })
        res.sudo().create_file()
        return res

    @api.multi
    def create_file(self):
        for res in self:
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            print('====================CUrrent Employee====================', current_employee)
            seq = self.env['ir.sequence'].next_by_code('folder.master')
            res.sequence = int(seq)
            print('=======================assign_name========================',res.folder_name)
            print('=======================assign_no========================',res.sequence)
            print('=======================assign_date========================',res.date)
            print('=======================assign_subject========================',res.subject.subject)
            print('=======================rremarks========================',res.description)
            print('=======================created_by========================',res.current_owner_id)
            print('=======================wing_id========================',res.department_id.id)
            print('=======================designation_id========================',res.job_id.id)
            print('=======================document_ids========================',res.document_ids)
            data = {
                        'assign_name': res.folder_name,
                        'assign_no': res.sequence,
                        'assign_date': res.date,
                        'assign_subject': (res.subject.subject),
                        'remarks': res.description,
                        'created_by': res.current_owner_id.id,
                        'doc_flow_id': 0,
                        'wing_id': res.department_id.id,
                        'section_id': 0,
                        'designation_id': res.job_id.id,
                        'document_ids': res.document_ids,
                    }
            req = requests.post('http://206.189.129.190/STPI/www/web-service/add-assignment/', data=data,
                                json=None)
            try:
                pastebin_url = req.text
                print('============Patebin url=================', pastebin_url)
                dictionary = json.loads(pastebin_url)
                print('=================str(res.current_owner_id.id)===========================',str(res.current_owner_id.id))
                res.notesheet_url = str(dictionary["response"][0]['notesheet'])
                s = str(dictionary["response"][0]['notesheet'])
                print('=====================notesheet url==========================',s)
                print(s.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
                d = (s.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
                res.assignment_id = (d.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
                print('===============================res.assignment_id-----------',res.assignment_id)
                req.raise_for_status()
                status = req.status_code
                if int(status) in (204, 404):
                    response = False
                else:
                    response = req.json()
                current_employee = self.env['hr.employee'].search([('user_id', '=', res.current_owner_id.id)], limit=1)
                print('==================================current employee==========================',
                      current_employee.name)
                print('==================================current employee id==========================',
                      current_employee.id)
                print('==================================current employee job id==========================',
                      current_employee.job_id.name)
                print('==================================current employee department_id id==========================',
                      current_employee.department_id.name)
                print('==================================current employee branch id==========================',
                      current_employee.branch_id.name)
                print('==================================current employee user id==========================',
                      current_employee.user_id.name)
                return (status, response)
            except Exception as e:
                print('=============Error==========',e)


    @api.multi
    def deal_with_file(self):
        for rec in self:
            rec.iframe_dashboard = str(rec.notesheet_url) + str('?type=STPI&user_id=') + str(rec.env.user.id)
            print('================================================', rec.iframe_dashboard)
            if rec.iframe_dashboard:
                rec.write({'state': 'in_progress'})
                total_iframe = rec.iframe_dashboard.replace('800', '100%').replace('"600"', '"100%"').replace(
                    'allowtransparency', '')
                file_ids = rec.env['see.file'].sudo().search([])
                for id in file_ids:
                    id.unlink()
                html = '''
                        <html>
                        <body>
                        <iframe marginheight="0" marginwidth="0" frameborder = "0" 
                        src="{0}" width="100%" height="1000"/>
                        </body>
                        </html>
                        '''.format(total_iframe)
                rec.env['see.file'].sudo().create({
                    "my_url":rec.iframe_dashboard,
                    "my_url_text":html
                })
                return  {
                    'name': 'Notesheet',
                    'view_type': 'form',
                    'view_mode': 'kanban',
                    'res_model': 'see.file',
                    'type': 'ir.actions.act_window',
                    'view_id': self.env.ref('smart_office.see_file_view1_kanban').id
                }
            else:
                raise UserError(_('URL not defined'))


    @api.multi
    @api.depends('number')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.number:
                name = record.number
            else:
                count = 0
                current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                sur_usr = current_employee.branch_id.name
                d_id = current_employee.department_id.stpi_doc_id
                fy = self.env['date.range'].search(
                    [('type_id.name', '=', 'Fiscal Year'), ('date_start', '<=', datetime.now().date()),
                     ('date_end', '>=', datetime.now().date())], limit=1)
                files = self.env['muk_dms.file'].search(
                    [('create_date', '>=', fy.date_start), ('create_date', '<=', fy.date_end)])
                for file in files:
                    count += 1
                if self.subject:
                    name = (self.subject.code) + '(' + str(count) + ')/' + str(d_id) + '/' + str(sur_usr) + '/' + str(
                        fy.name)
                else:
                    name = 'File'
            res.append((record.id, name))
        return res


    @api.multi
    def tracker_view_file(self):
        for rec in self:
            views_domain = []
            dmn = self.env['file.tracker.report'].search(['|', ('name', '=', rec.folder_name), ('number', '=', rec.number)])
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



    @api.multi
    def button_submit(self):
        for rec in self:
            rec.write({'state': 'in_progress'})

    @api.multi
    def button_close(self):
        for rec in self:
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.env['file.tracker.report'].create({
                'name': str(rec.folder_name),
                'number': str(rec.number),
                'type': 'File',
                'closed_by': str(current_employee.user_id.name),
                'closed_by_dept': str(current_employee.department_id.name),
                'closed_by_jobpos': str(current_employee.job_id.name),
                'closed_by_branch': str(current_employee.branch_id.name),
                'close_date': datetime.now().date(),
                'action_taken': 'file_closed',
                'remarks': rec.description,
                'details': "File closed on {}".format(datetime.now().date())
            })

            my_current_employee = self.env['hr.employee'].search([('user_id', '=', rec.current_owner_id.id)], limit=1)
            print('==============================to_designation_id=============================', my_current_employee.job_id.id)
            print('==============================to_user_id=============================', my_current_employee.user_id.id)
            print('==============================remarks=============================', rec.description)
            print('==============================to_designation_ids=============================', my_current_employee.job_id.id)
            print('==============================to_user_ids=============================', my_current_employee.user_id.id)
            print('==============================user_id=============================', my_current_employee.user_id.id)
            print('==============================assignment_id=============================', rec.assignment_id)
            data = {
                'is_action_taken': 'C',
                'assignment_flag': 1,
                'to_designation_id': my_current_employee.job_id.id,
                'to_user_id': my_current_employee.user_id.id,
                'remarks': rec.description,
                'to_designation_ids': my_current_employee.job_id.id,
                'to_user_ids': my_current_employee.user_id.id,
                'user_id': my_current_employee.user_id.id,
                'assignment_id': rec.assignment_id,
            }

            req = requests.post('http://206.189.129.190/STPI/www/web-service/forward-correspondence/', data=data,
                                json=None)
            try:
                print('=====================================================', req)
                pastebin_url = req.text
                dictionary = json.loads(pastebin_url)
                print('===========================pastebin_url==========================', pastebin_url)
                print('===========================dictionary==========================', dictionary)
            except Exception as e:
                print('=============Error==========', e)

            rec.write({'state': 'closed'})

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.env['file.tracker.report'].create({
                'name': str(rec.folder_name),
                'number': str(rec.number),
                'type': 'File',
                'repoen_by': str(current_employee.user_id.name),
                'repoen_by_dept': str(current_employee.department_id.name),
                'repoen_by_jobpos': str(current_employee.job_id.name),
                'repoen_by_branch': str(current_employee.branch_id.name),
                'repoen_date': datetime.now().date(),
                'action_taken': 'file_repoened',
                'remarks': rec.description,
                'details': "File repoen on {}".format(datetime.now().date())
            })
            my_current_employee = self.env['hr.employee'].search([('user_id', '=', rec.current_owner_id.id)], limit=1)
            print('==============================assignment_id=============================', rec.assignment_id)
            # print('==============================my_current_employee=============================', my_current_employee)
            print('==============================current user=============================', my_current_employee.user_id.id)
            data = {
                'user_id': my_current_employee.user_id.id,
                'assignment_id': rec.assignment_id,
            }

            req = requests.post('http://206.189.129.190/STPI/www/web-service/reopen-files', data=data,
                                json=None)
            try:
                print('=====================================================', req)
                pastebin_url = req.text
                dictionary = json.loads(pastebin_url)
                print('===========================pastebin_url==========================', pastebin_url)
                print('===========================dictionary==========================', dictionary)
            except Exception as e:
                print('=============Error==========', e)

            rec.write({'state': 'draft'})



    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.sudo().button_reset_to_draft()
    @api.multi
    def action_refuse(self):
        for rec in self:
            rec.sudo().button_reset_to_draft()




class FolderType(models.Model):
    _name = 'folder.type'
    _description = 'Folder Type'

    name = fields.Char(string = 'Name')

class SubjectMainHeads(models.Model):
    _name = 'code.subject'
    _description = 'Code Subject'
    _rec_name = 'subject'

    code = fields.Char(string='Code')
    subject = fields.Char(string = 'Subject')
