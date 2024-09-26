from datetime import datetime, date #, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

class FolderMaster(models.Model):
    _name = 'folder.master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'File'
    _rec_name = 'number'
    _order = "action_time desc,write_date desc"

    @api.model
    def _get_emp_department_id(self):
        current_emp = self.env.user.employee_ids[0:1]
        if current_emp and current_emp.department_id:
            if current_emp.department_id.parent_id:
                return current_emp.department_id.parent_id.id
            else:
                return current_emp.department_id.id
    @api.model
    def _get_emp_division_id(self):
        current_emp = self.env.user.employee_ids[0:1]
        if current_emp and current_emp.department_id:
            if current_emp.department_id.parent_id:
                return current_emp.department_id.id
            else:
                return False

    folder_name = fields.Char(string="File Name",track_visibility='always')
    old_file_number = fields.Char(string='Old File Number',track_visibility='always')
    current_owner_id = fields.Many2one('res.users', 'Current Owner',track_visibility='always',default=lambda self: self.env.user)
    # is_current_owner = fields.Boolean(string='Current Owner ?',compute="compute_current_user",search="_search_correspondence_text")
    is_current_owner = fields.Boolean(string='Current Owner ?',compute="compute_current_user")
    last_owner_id = fields.Many2one('res.users', 'Last Owner',track_visibility='always',default=lambda self: self.env.user)

    branch_id = fields.Many2one('res.branch', 'Center')
    department_id = fields.Many2one('hr.department', 'Division',domain=[('parent_id','=',False)],required=True,default=_get_emp_department_id)
    division_id = fields.Many2one('hr.department', 'Sub Division',required=True,default=_get_emp_division_id)
    job_id = fields.Many2one('hr.job', 'Job')
    sec_owner = fields.Many2many('res.users', string='Secondary Owners',track_visibility='always')
    previous_owner = fields.Many2many('res.users', string='Previous Owners',track_visibility='always')

    date = fields.Date(string='Date', default = fields.Date.today(),track_visibility='always')
    subject = fields.Many2one('code.subject', string='Subject',track_visibility='always')
    tags = fields.Many2many('muk_dms.tag', string='Tags',track_visibility='always')
    number = fields.Char(string='File Number',track_visibility='always')
    is_current_user = fields.Boolean(string='Is Current User')
    status = fields.Selection([('normal', 'Normal'),
                               ('important', 'Important'),
                               ('urgent', 'Urgent')
                               ], string='Status',track_visibility='always')
    sequence = fields.Integer(string='Sequence')
    previous_reference = fields.Text('Previous Reference')
    later_reference = fields.Text('Later Reference')
    first_doc_id = fields.Integer(string='First Doc Id')
    document_ids = fields.Char(string='PHP Letter ids')
    assignment_id = fields.Char(string='Assignment ID')
    type = fields.Many2many('folder.type', string= "Type",track_visibility='always')
    description = fields.Text(string='Description',track_visibility='always')
    file_ids = fields.One2many('muk_dms.file','folder_id', string='Files',track_visibility='always',domain=lambda self:['|','|',('last_owner_id', '=', self._uid),('previous_owner_emp.user_id','in',[self._uid]),('current_owner_id', '=', self._uid)])
    
    document_dispatch = fields.One2many('dispatch.document','folder_id', string='Document Dispatch',track_visibility='always',domain=lambda self:[('secondary_employee_ids','in',self.env.user.employee_ids.ids)])

    basic_version = fields.Float('Basic Version')
    version = fields.Many2one('folder.master', string='Version', track_visibility='always')
    previousversion = fields.Many2one('folder.master', string='Previous  Version', track_visibility='always')
    # part_file_ids = fields.Many2many('folder.master', string='Part Files')
    forwarded_by_employee_id = fields.Many2one("hr.employee","Forwarded From",track_visibility='onchange')
    forwarded_to_employee_id = fields.Many2one("hr.employee","Forwarded To",track_visibility='onchange')
    forwarded_date = fields.Date("Forwarded Date",track_visibility='onchange')

    file_ids_m2m = fields.Many2many('muk_dms.file', string='Reference',track_visibility='always')
    notesheet_url = fields.Text()
    # iframe_dashboard = fields.Text()
    # folder_track_ids = fields.One2many('folder.tracking.information', 'create_let_id', string= "Files")
    my_view = fields.Text()
    my_dash = fields.Html('My Dash Html')
    dashboard_view = fields.Many2one('ir.ui.view')
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('shelf','Shelf'),
                              ('pending_close', 'Pending For Closure'),
                              ('pending_reopen', 'Pending For Reopen'),
                              ('closed', 'Closed'),
                              ('closed_part', 'Merged')
                             ], required=True, default='draft', string='Status',track_visibility='always')
    # green_ids = fields.Many2many('green.sheets','folder_id', string='Green Sheets')
    file_mode = fields.Selection([('inbox','Inbox'),('own_shelf','Own Shelf')],string="File At",required=True,default="inbox")
    noting_ids = fields.One2many('smart_office.noting','folder_id',string='Notings',domain=lambda self:[('state','=','submitted'),('secondary_employee_ids','in',self.env.user.employee_ids.ids)])
    tracking_ids = fields.One2many('smart_office.file.tracking','file_id',string='Trackings')
    
    is_on_shelf = fields.Boolean("On Shelf ?")
    # file_currently_with = fields.Char("Currently With",compute="_compute_file_currently_with")
    same_department = fields.Boolean("Same Department ?",compute="compute_if_same_department")
    no_of_part_files = fields.Integer("No. Of Part Files",compute="_compute_no_of_part_file",help="No. of part files for current user")
    is_on_approver_group = fields.Boolean("Is on File Close/Reopen Group ?",compute="_compute_if_on_approver_group")

    incoming_source = fields.Selection(selection=[('self','File Created'),
                                                 ('forward','Forwarded'),
                                                #  ('sent_back','Sent Back'),
                                                 ('pull_shelf','Pulled from Shelf'),
                                                 ('pull_own_shelf','Pulled from Own Shelf'),
                                                 ('pull_inbox','Pulled from Others Inbox'),
                                                 ('transfer','Transferred'),
                                                 ('file_reopen','File Reopened')],string="Action Type")
    action_by_uid = fields.Many2one('res.users','Action By')
    action_time = fields.Datetime('Date & Time')
    action_date = fields.Date("Action Date")

    closed_by_uid = fields.Many2one('res.users','Closed By')
    closed_date = fields.Date('Closed On ')
    closed_time = fields.Datetime('Closed On')

    reopen_request_user = fields.Many2one("res.users","Requested By")
    close_reopen_date = fields.Date("Request On")
    close_reopen_time = fields.Datetime("Request On ")

    part_created_by = fields.Many2one('res.users','Created By ')
    part_created_on = fields.Datetime('Created On')

    part_merged_by = fields.Many2one('res.users','Merged By')
    part_merged_on = fields.Datetime('Merged On')

    search_correspondence = fields.Char("Text")

    put_in_own_shelf_date = fields.Date("Put in Shelf Date")
    put_in_own_shelf_time = fields.Datetime("Put in Shelf Time")

    # @api.multi
    # def _compute_file_currently_with(self):
    #     for file in self:
    #         if file.is_on_shelf:
    #             file.file_currently_with = "Shelf"
    #         elif file.state in ['in_progress','pending_close']:
    #             file.file_currently_with = "Inbox"
    #         elif file.state in ['pending_reopen','closed','closed_part']:    
    #             file.file_currently_with = "Closed"
    @api.multi
    def _compute_if_on_approver_group(self):
        for folder in self:
            folder.is_on_approver_group = self.env.user.has_group('smart_office.smart_office_file_close_approver')

    @api.multi
    def _compute_no_of_part_file(self):
        part_files = self.search([('version', 'in', self.ids),('state','=','in_progress'),('is_on_shelf','=',False),('current_owner_id','=',self._uid)])
        for folder in self:
            folder.no_of_part_files = len(part_files.filtered(lambda r:r.version == folder))

    @api.onchange('department_id')
    def set_division(self):
        if self.department_id:
            if self.division_id and self.division_id.parent_id != self.department_id:
                self.division_id = False
        else:
            self.division_id = False

    @api.onchange('division_id')
    def set_subject(self):
        self.subject = False

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        emp_department_id = current_employee and current_employee.department_id and current_employee.department_id.id or 0
        emp_parent_department_id = current_employee and current_employee.department_id and current_employee.department_id.parent_id and current_employee.department_id.parent_id.id or 0
        
        if 'filter_shelf_department' in self._context:
            args += ['&','&',('state','=','shelf'),
                            '|',('department_id','=',emp_department_id),('department_id','=',emp_parent_department_id),
                        ('is_on_shelf','=',True)
                    ]

        if 'filter_department' in self._context:
            args += [('department_id','=',emp_department_id)]
            
        if "filter_subordinates" in self._context:
            args+= [('current_owner_id.employee_ids', 'child_of', self.env.user.employee_ids.ids)]

        if "filter_allowed_branches" in self._context:
            args+= [('branch_id','in',self.env.user.branch_ids.ids)]
        return super(FolderMaster, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        emp_department_id = current_employee and current_employee.department_id and current_employee.department_id.id or 0
        emp_parent_department_id = current_employee and current_employee.department_id and current_employee.department_id.parent_id and current_employee.department_id.parent_id.id or 0
        if 'filter_shelf_department' in self._context:
            domain += ['&','&',('state','=','in_progress'),
                            '|',('department_id','=',emp_department_id),('department_id','=',emp_parent_department_id),
                        ('is_on_shelf','=',True)
                    ]
        if 'filter_department' in self._context:
            domain += [('department_id','=',emp_department_id)]
            
        if "filter_subordinates" in self._context:
            domain += [('current_owner_id.employee_ids', 'child_of', self.env.user.employee_ids.ids)]

        if "filter_allowed_branches" in self._context:
            domain += [('branch_id','in',self.env.user.branch_ids.ids)]

        return super(FolderMaster, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        # print("Received domain is--->",domain)
        changed_domain = []
        for dom in domain:
            if dom[0] == 'search_correspondence':
                # custom_domain = ['|','|','|',['file_ids.pdf_text','ilike',dom[2]],['noting_ids.subject','ilike',dom[2]],['noting_ids.plain_text','ilike',dom[2]],['noting_ids.comment_ids.plain_text','ilike',dom[2]]]
                # # domain[index] = custom_domain
                # for element in custom_domain:
                #     changed_domain.append(element)

                import lucene
                from java.util import Arrays
                from java.nio.file import Paths
                from org.apache.lucene.analysis import CharArraySet
                from org.apache.lucene.analysis.standard import StandardAnalyzer
                from org.apache.lucene.analysis.en import EnglishAnalyzer
                from org.apache.lucene.analysis.hi import HindiAnalyzer
                from org.apache.lucene.index import DirectoryReader
                from org.apache.lucene.store import SimpleFSDirectory
                from org.apache.lucene.search import IndexSearcher
                from org.apache.lucene.queryparser.classic import QueryParser

                vm_env = lucene.getVMEnv()
                if not vm_env:
                    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
                else:
                    # vm_env = lucene.getVMEnv()
                    vm_env.attachCurrentThread()

                index_directory = self.env.ref('smart_office.smart_office_lucene_index_directory').value
                # print("indexing system parameter--->",index_directory)

                store = SimpleFSDirectory(Paths.get(index_directory))
                searcher = IndexSearcher(DirectoryReader.open(store))

                hindi_stop_words = list(HindiAnalyzer().getStopwordSet())
                english_stop_words = list(EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

                stopWords = Arrays.asList(hindi_stop_words + english_stop_words)
                custom_stop_set =  CharArraySet(stopWords, True)

                analyzer = StandardAnalyzer(custom_stop_set)
                lucene_query = ' AND '.join(dom[2].split())

                print("lucene query ---->",lucene_query)
                query = QueryParser("data", analyzer).parse(lucene_query) 
                topDocs = searcher.search(query,100000)
                print(f"Total {topDocs.totalHits.value} docs matched.",)

                # doc_ids = [doc.doc for doc in topDocs.scoreDocs]
                noting_ids = []
                comment_ids = []
                correspondence_ids = []
                
                for doc in topDocs.scoreDocs:
                    print(f"doc ID : {doc.doc} score : {doc.score} ")
                    s_doc = searcher.doc(doc.doc)
                    dict_doc = dict((field.name(), field.stringValue()) for field in s_doc.getFields() if field.name() != 'data')
                    if int(dict_doc.get('note_id','0')) > 0:
                        noting_ids.append(int(dict_doc['note_id']))

                    if int(dict_doc.get('comment_id','0')):
                        comment_ids.append(int(dict_doc['comment_id']))

                    if int(dict_doc.get('correspondence_id','0')):
                        correspondence_ids.append(int(dict_doc['correspondence_id']))
                print(f"noting ids are--->{noting_ids} comment ids----> {comment_ids} correspondence ids ---> {correspondence_ids}")
                
                # print('doc_ids---->',doc_ids)
                # filtered_noting = self.env['smart_office.noting'].search([('index_id','!=',False),('index_id','in',doc_ids),('secondary_employee_ids','in',self.env.user.employee_ids.ids)])
                filtered_noting = self.env['smart_office.noting'].search([('id','in',noting_ids),('secondary_employee_ids','in',self.env.user.employee_ids.ids)])
                # print("filtere noting--->",filtered_noting)
                # filtered_comment = self.env['smart_office.comment'].search([('index_id','!=',False),('index_id','in',doc_ids),('secondary_employee_ids','in',self.env.user.employee_ids.ids)])
                filtered_comment = self.env['smart_office.comment'].search([('id','in',comment_ids),('secondary_employee_ids','in',self.env.user.employee_ids.ids)])
                # print("filtered comments--->",filtered_comment)
                # filtered_correspondences = self.env['muk_dms.file'].search([('index_id','!=',False),('index_id','in',doc_ids),'|','|',('last_owner_id', '=', self._uid),('previous_owner_emp.user_id','in',[self._uid]),('current_owner_id', '=', self._uid)])
                filtered_correspondences = self.env['muk_dms.file'].search([('id','in',correspondence_ids),'|','|',('last_owner_id', '=', self._uid),('previous_owner_emp.user_id','in',[self._uid]),('current_owner_id', '=', self._uid)])
                # print("filtered correspondence---->",filtered_correspondences)
                # custom_domain = ['|',['noting_ids.index_id','in',doc_ids],['noting_ids.comment_ids.index_id','in',doc_ids]]
                custom_domain = ['|','|',['file_ids.id','in',filtered_correspondences.ids],['noting_ids.id','in',filtered_noting.ids],['noting_ids.comment_ids.id','in',filtered_comment.ids]]
                for element in custom_domain:
                    changed_domain.append(element)
                store.close()
                
            else:
                changed_domain.append(dom)
        domain = changed_domain
        print("Changed domain is--->",domain)
        res = super(FolderMaster,self).search_read(domain, fields, offset, limit, order)
        return res

    @api.multi
    def compute_current_user(self):
        for folder in self:
            folder.is_current_owner = folder.current_owner_id == self.env.user

    @api.multi
    def compute_if_same_department(self):
        employee = self.env.user.employee_ids and self.env.user.employee_ids[0] or False
        for folder in self:
            if employee and employee.department_id:
                if employee.department_id == folder.department_id:
                    folder.same_department = True
                if employee.department_id.parent_id and employee.department_id.parent_id == folder.department_id:
                    folder.same_department = True
            
    # @api.multi
    # def view_tracking_info(self):
    #     tree_view_id = self.env.ref('smart_office.view_dispatch_letter_tracking_tree').id
    #     form_view_id = self.env.ref('smart_office.view_dispatch_letter_tracking_form').id
    #     return {
    #             'model': 'ir.actions.act_window',
    #             'name': 'Tracking Informations',
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form,tree',
    #             'res_model': 'dispatch.letter.tracking',
    #             'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #             'domain': [('folder_id', '=', self.id)],
    #         }

    @api.multi
    def action_download_notings(self):
        return {
            'type':'ir.actions.act_url',
            'url':f"/efile_notings/{self.id}/{self._uid}",
            'target':'/self'
        }

    @api.multi
    def action_download_correspondences(self):
        return {
            'type':'ir.actions.act_url',
            'url':f"/efile_correspondences/{self.id}/{self._uid}",
            'target':'/self'
        }

    @api.multi
    def action_download_dispatch_letters(self):
        return {
            'type':'ir.actions.act_url',
            'url':f"/efile_dispatch_letters/{self.id}/{self._uid}",
            'target':'/self'
        }
        
    @api.multi
    def action_download_file(self):
        return {
            'type':'ir.actions.act_url',
            'url':f"/efile_file_download/{self.id}/{self._uid}",
            'target':'/self'
        }

    @api.model
    def create(self, vals):
        current_user = self.env.user
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        vals['branch_id'] = current_user.default_branch_id.id
        vals['job_id'] = current_employee.job_id.id
        res = super(FolderMaster, self).create(vals)
       
        # name = ''
        # count = 0

        # res.department_id = current_employee.department_id.id
        # file format : STPI/Branch Code/Division Code/Subdivision Code/Subject Code/Serial Number/Current Year/ Part 1
        # unique count fiscal year & division & sub-division & branch & subject 
        if not vals.get('number'):
            company_code = 'STPI' #self.env.user.company_id.name
            branch_code = current_user.default_branch_id.code
            division_code = res.department_id.stpi_doc_id
            subdivision_code = res.division_id.stpi_doc_id
            subject_code = res.subject.code
            if not division_code:
                raise ValidationError("Division code is not available.Please contact your administrator.")
            if not subdivision_code:
                raise ValidationError("Sub-division code is not available.Please contact your administrator.")

            fy = self.env['date.range'].search([
                ('type_id.name', '=', 'Fiscal Year'), ('date_start', '<=', datetime.now().date()),
                ('date_end', '>=', datetime.now().date())
                ], limit=1)
            if not fy:
                raise ValidationError("Financial year is not properly configured.Please contact to your administrator.")
            financial_year_name = fy.name.replace('FY ','').replace('fy ','')

            files_count = self.search_count([
                ('create_date', '>=', fy.date_start), ('create_date', '<=', fy.date_end),
                ('department_id', '=', res.department_id.id),('division_id','=',res.division_id.id),
                ('branch_id', '=', current_user.default_branch_id.id), ('subject', '=', res.subject.id)
                ]) 
            
            res.number = f'{company_code}/{branch_code}/{division_code}/{subdivision_code}/{subject_code}/{financial_year_name}/{files_count}'

        # self.env['file.tracker.report'].create({
        #     'name': str(res.folder_name),
        #     'number': str(res.number),
        #     'type': 'File',
        #     'created_by': str(current_employee.user_id.name),
        #     'created_by_dept': str(current_employee.department_id.name),
        #     'created_by_jobpos': str(current_employee.job_id.name),
        #     'created_by_branch': str(current_employee.branch_id.name),
        #     'create_date': datetime.now().date(),
        #     'action_taken': 'file_created',
        #     'remarks': res.description,
        #     'details': f"File created on {date.today()}" #.format(datetime.now().date())
        # })
        if not self._context.get('no_log_record'):
            # start : Add tracking information of file_created to new model 28-December-2021
            self.env['smart_office.file.tracking'].create({
                'file_id':res.id,
                'action_stage_id':self.env.ref('smart_office.file_stage_file_created').id,
                'remark':res.description
            })
            # end : Add tracking information of file_created to new model 28-December-2021
        # res.sudo().create_file()
        seq = self.env['ir.sequence'].next_by_code('folder.master')
        res.sequence = int(seq)
        # self.env.user.notify_success("File created successfully.")
        return res

    def is_current_user(self):
        for rec in self:
            if rec.env.user.id == rec.current_owner_id.id:
                rec.is_current_user = True
            else:
                rec.is_current_user = False

    @api.multi
    def deal_with_file(self):
        for rec in self:
            # rec.iframe_dashboard = str(rec.notesheet_url) + str('?type=STPI&user_id=') + str(rec.env.user.id)
            action_id = self.env.ref('smart_office.action_folder_master_incoming_my_inbox_window').id
            menu_id = self.env.ref('smart_office.menu_folder_master_incoming_my_inbox').id
            api_url = self.env.ref('smart_office.smart_office_api_system_parameter').sudo()
            # rec.iframe_dashboard = f"""{api_url.value}?file_id={rec.id}&action_id={action_id}&menu_id={menu_id}&user_id={self.env.uid}&session_id={request.httprequest.cookies.get('session_id','')}"""
            iframe_url = f"""{api_url.value}?file_id={rec.id}&action_id={action_id}&menu_id={menu_id}&user_id={self.env.uid}&session_id={request.httprequest.cookies.get('session_id','')}"""
            # print("Iframe dashboard is",rec.iframe_dashboard)
            # if rec.iframe_dashboard:
                # rec.write({'state': 'in_progress'})
                # total_iframe = rec.iframe_dashboard.replace('800', '100%').replace('"600"', '"100%"').replace(
                #     'allowtransparency', '')
            file_ids = rec.env['see.file'].sudo().search([])
            # for id in file_ids:
            #     id.unlink()
            if file_ids:
                file_ids.unlink()

            notesheet_view_html = f'''
                    <html>
                        <body>
                            <iframe id="efile_frame" is="x-frame-bypass" marginheight="0" marginwidth="0" frameborder="0" 
                            src="{iframe_url}" style="width:100%; height:calc(100vh - 150px)"/>
                        </body>
                    </html>
                    '''

            rec.env['see.file'].sudo().create({"my_url":iframe_url,
                                                    "my_url_text":notesheet_view_html
                                                    })
            return  {
                'name': 'Notesheet',
                'view_type': 'form',
                'view_mode': 'kanban',
                'res_model': 'see.file',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('smart_office.see_file_view1_kanban').id
            }
            # else:
            #     raise UserError(_('URL not defined'))

    # @api.multi
    # @api.depends('number')
    # def name_get(self):
    #     res = []
    #     name = ''
    #     for record in self:
    #         if record.number and record.folder_name:
    #             name = str(record.number) + ' - ' + str(record.folder_name)
    #         else:
    #             count = 0
    #             current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #             user_branch_code = current_employee.branch_id.name
    #             d_id = current_employee.department_id.stpi_doc_id
    #             fy = self.env['date.range'].search(
    #                 [('type_id.name', '=', 'Fiscal Year'), ('date_start', '<=', datetime.now().date()),
    #                  ('date_end', '>=', datetime.now().date())], limit=1)
    #             files = self.env['muk_dms.file'].search(
    #                 [('create_date', '>=', fy.date_start), ('create_date', '<=', fy.date_end)])
    #             for file in files:
    #                 count += 1
    #             if self.subject:
    #                 name = (self.subject.code) + '(' + str(count) + ')/' + str(d_id) + '/' + str(user_branch_code) + '/' + str(
    #                     fy.name) + ' - ' + str(record.folder_name)
    #             else:
    #                 name = 'File'
    #         res.append((record.id, name))
    #     return res

    @api.multi
    def tracker_view_file(self):
        # for rec in self:
        #     views_domain = []
        #     dmn = self.env['file.tracker.report'].search([('number', '=', rec.number)])
        #     for id in dmn:
        #         views_domain.append(id.id)
        #     return {
        #         'name': 'File Tracking Report',
        #         'view_type': 'form',
        #         'view_mode': 'tree',
        #         'res_model': 'file.tracker.report',
        #         'type': 'ir.actions.act_window',
        #         'target': 'current',
        #         'domain': [('id', 'in', views_domain)]
        #     }
        # for rec in self:
        #     views_domain = []
        #     dmn = self.env['file.tracker.report'].search([('number', '=', rec.number)])
        #     for id in dmn:
        #         views_domain.append(id.id)
            return {
                'name': 'File Tracking Report',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'smart_office.file.tracking',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('file_id', '=', self.id)]
            }
    
    @api.multi
    def view_part_files(self):
        return {
            'name': 'Part Files',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id' : self.env.ref('smart_office.view_folder_master_view_part_tree').id,
            'res_model': 'folder.master',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('version', '=', self.ids[0]),('state','=','closed_part')]
        }

    @api.multi
    def button_part_file(self):
        if self.version:
            raise ValidationError("Can't create a part file from a part file. Please try with a different file.")
            
        return {
                'name'      : 'Create Part File',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   :  self.env.ref("smart_office.view_smart_office_part_file_form").id,
                'res_model' : 'smart_office.part.file',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {'default_folder_id':self.id},
                }

    # @api.multi
    # def button_merge_file(self):
    #     for rec in self:
    #         pass

    @api.multi
    def button_submit(self):
        self.write({'state':'in_progress',
                    'incoming_source':'self',
                    'action_by_uid':self._uid,
                    'action_time':datetime.now(),
                    'action_date':datetime.now().date(),
                    'date':datetime.now().date()})
        self.env.user.notify_success("File saved successfully.")

    @api.multi
    def button_close_part(self):
        for rec in self:
            rec.write({'state': 'closed_part',
                        'part_merged_by':self._uid,
                        'part_merged_on':datetime.now(),
                    })

    @api.multi
    def button_close(self):
        return {
                'name'      : 'Close File',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_close_file_form').id,
                'res_model' : 'smart_office.close.file',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_cancel_file_close(self):
        return {
                'name'      : 'Cancel Close File',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_close_file_cancel_form').id,
                'res_model' : 'smart_office.close.file.cancel',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_approve_file_close(self):
        return {
                'name'      : 'File Close Approve',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_close_file_approve_form').id,
                'res_model' : 'smart_office.close.file.approve',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_reject_file_close(self):
        return {
                'name'      : 'File Close Reject',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_close_file_reject_form').id,
                'res_model' : 'smart_office.close.file.reject',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_submit_file_reopen(self):
        return {
                'name'      : 'File Reopen',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_reopen_file_form').id,
                'res_model' : 'smart_office.reopen.file',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_cancel_file_reopen(self):
        return {
                'name'      : 'File Reopen Cancel',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_reopen_file_cancel_form').id,
                'res_model' : 'smart_office.reopen.file.cancel',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_approve_file_reopen(self):
        return {
                'name'      : 'File Reopen Approve',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_reopen_file_approve_form').id,
                'res_model' : 'smart_office.reopen.file.approve',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_reject_file_reopen(self):
        return {
                'name'      : 'File Reopen Reject',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('smart_office.view_smart_office_reopen_file_reject_form').id,
                'res_model' : 'smart_office.reopen.file.reject',
                'type'      : 'ir.actions.act_window',
                'target'    : 'new',
                'context'   : {"default_folder_id":self.id}
                }

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.sudo().action_submit_file_reopen()
            
    @api.multi
    def action_refuse(self):
        for rec in self:
            rec.sudo().action_submit_file_reopen()

class FolderType(models.Model):
    _name = 'folder.type'
    _description = 'Folder Type'

    name = fields.Char('Name',required=True)
    code = fields.Char('Code')

    @api.model
    def create(self,vals):
        res = super(FolderType,self).create(vals)
        self.env.user.notify_success("Type Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(FolderType, self).write(vals)
        self.env.user.notify_success("Type Saved Successfully.")
        return res


class SubjectMainHeads(models.Model):
    _name = 'code.subject'
    _description = 'Code Subject'
    _rec_name = 'subject'

    code = fields.Char(string='Code',required=True)
    subject = fields.Char(string='Subject',required=True)
    division_id = fields.Many2one('hr.department', 'Division',domain=[('parent_id','=',False)],required=True)
    division_code = fields.Char(string="Division Code",related="division_id.stpi_doc_id")
    sub_division_id = fields.Many2one('hr.department', 'Sub Division',required=True)
    sub_division_code = fields.Char(string="Sub Division Code",related="sub_division_id.stpi_doc_id")

    @api.onchange('division_id')
    def onchange_division_id(self):
        if self.division_id:
            self.sub_division_id = False

    # @api.constrains('code')
    # def validate_code(self):
    #     for subject in self:
    #         if not subject.code.isnumeric():
    #             raise ValidationError("Code Must Be Integers.")
    
    @api.model
    def create(self,vals):
        res = super(SubjectMainHeads,self).create(vals)
        self.env.user.notify_success("Subject Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SubjectMainHeads, self).write(vals)
        self.env.user.notify_success("Subject Saved Successfully.")
        return res
