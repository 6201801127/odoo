from odoo import models,fields,api

class FileTrackeWizard(models.TransientModel):
    _name = 'file.tracker.wizard'
    _description = 'File Tracker Wizard'

    report_of = fields.Selection([('File','File'),
                                  ('Correspondence','Correspondence'),
                                  ('Both','Both'),
                                  ],string="Report On", default='Both')
    search_through = fields.Selection([('Employee','Employee'),
                                  ('Branch','Branch'),
                                  ('Job','Job'),
                                  ('Department','Department'),
                                  ('All','All'),
                                  ],string="Search Via", default='Employee')
    details = fields.Char('Number/Name')
    date_range = fields.Many2one('date.range', string='Date Range')
    job_id = fields.Many2one('hr.job', string='Functional Designation')
    action_taken = fields.Selection([('correspondence_created', 'Correspondence Created'),
                                     ('file_created', 'File Creates'),
                                     ('correspondence_forwarded', 'Correspondence Forwarded'),
                                     ('file_forwarded', 'File Forwarded'),
                                     ('correspondence_transferred', 'Correspondence Transferred'),
                                     ('file_transferred', 'File Transferred'),
                                     ('correspondence_pulled', 'Correspondence Pulled'),
                                     ('file_pulled', 'File Pulled'),
                                     ('assigned_to_file', 'Assigned To File'),
                                     ('file_closed', 'File Closed'),
                                     ('file_repoened', 'File Reopened'),
                                     ('all', 'All')
                                     ], string='Action Taken', default='all')

    # start : 28-feb-2022 required fields to generate report
        # start : left side fields
    file_name = fields.Char("File Name")
    file_number = fields.Char("File Number")
    department_id = fields.Many2one('hr.department','Division',domain=[('parent_id','=',False)])
    subdivision_id = fields.Many2one('hr.department','Sub Division')
    subject_id = fields.Many2one('code.subject','Subject')
    branch_id = fields.Many2one('res.branch', string='Center')
        # end : left side fields
        
        # start : right side fields
    action_id = fields.Many2one('smart_office.file.stage','Action',domain=[('use_on_report','=',True)])
    employee_id = fields.Many2one('hr.employee','Action By')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    # pending_with = fields.Selection(string='Pending With',selection=[('shelf', 'Shelf'), ('inbox', 'Inbox')])
    status = fields.Selection(string='Status',selection=[('shelf', 'Shelf'),
                                                         ('in_progress', 'In Progress'),
                                                         ('pending_close', 'Pending For Closure'),
                                                         ('pending_reopen', 'Pending For Reopen'),
                                                         ('closed', 'Closed'),
                                                         ('closed_part', 'Merged')])
    pending_employee_id = fields.Many2one('hr.employee','Current Owner')

        # end : right side fields

    @api.onchange('date_range')
    def get_dates(self):
        for rec in self:
            rec.from_date = rec.date_range.date_start
            rec.to_date = rec.date_range.date_end

    # end : 28-feb-2022 required fields to generate report
    # @api.onchange('pending_with')
    # def validate_pending_employee(self):
    #     if self.pending_with and self.pending_with != 'inbox':
    #             self.pending_employee_id = False
    #     else:
    #         self.pending_employee_id = False

    @api.onchange('status')
    def validate_pending_employee(self):
        if self.status and self.status != 'in_progress':
            self.pending_employee_id = False
        else:
            self.pending_employee_id = False

    @api.onchange('department_id')
    def set_division(self):
        if self.department_id:
            if self.subdivision_id and self.subdivision_id.parent_id != self.department_id:
                self.subdivision_id = False
        else:
            self.division_id = False

    @api.onchange('subdivision_id')
    def set_subject(self):
        self.subject_id = False

    @api.multi
    def confirm_report(self):
        domain = []
        if not self.env.user.has_group('muk_dms.group_dms_manager'):
            current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
            emp_department_id = current_employee.department_id
            if current_employee.department_id.parent_id:
                emp_department_id = current_employee.department_id.parent_id
            domain += [('current_owner_id.employee_ids','child_of',current_employee.id),('department_id','=',emp_department_id.id)]
            
        if self.file_name:
            domain+=[('folder_name','ilike',self.file_name)]
        if self.file_number:
            domain+=[('number','ilike',self.file_number)]
        if self.department_id:
            domain+=[('department_id','=',self.department_id.id)]
        if self.subdivision_id:
            domain+=[('division_id','=',self.subdivision_id.id)]
        if self.subject_id:
            domain+=[('subject','=',self.subject_id.id)]
        if self.branch_id:
            domain+=[('branch_id','=',self.branch_id.id)]

        join_query = '''select fm.id from folder_master fm
                      inner join smart_office_file_tracking sft
                      on sft.file_id = fm.id
                      where '''

        query_to_be_executed = False
        and_condition_next = False

        if self.action_id:
            query_to_be_executed = True
            join_query += f'sft.action_stage_id={self.action_id.id}'
            and_condition_next = True
            # domain+=[('tracking_ids.action_stage_id','in',[self.action_id.id])]
        if self.employee_id:
            # domain+=[('tracking_ids.action_by_user_id','in',[self.employee_id.user_id.id])]
            query_to_be_executed = True
            custom_query = f'action_by_user_id={self.employee_id.user_id.id}'
            if and_condition_next:
                join_query += f' and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True
        if self.from_date and self.to_date:
            query_to_be_executed = True
            custom_query = f"sft.action_date >= '{self.from_date.strftime('%Y-%m-%d')}' and sft.action_date <= '{self.to_date.strftime('%Y-%m-%d')}'"
            if and_condition_next:
                join_query += f' and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True
            # domain+=[('tracking_ids.action_date','>=',self.from_date),('tracking_ids.action_date','<=',self.to_date)]

        elif self.from_date:
            query_to_be_executed = True
            custom_query = f"sft.action_date >= '{self.from_date.strftime('%Y-%m-%d')}'"
            if and_condition_next:
                join_query += f' and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True
            # domain+=[('tracking_ids.action_date','>=',self.from_date)]

        elif self.to_date:
            query_to_be_executed = True
            custom_query = f"sft.action_date <= '{self.to_date.strftime('%Y-%m-%d')}'"
            if and_condition_next:
                join_query += f'and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True
        if query_to_be_executed:
            # print("join_query is-------->",join_query)
            self._cr.execute(join_query)
            query_data = self._cr.fetchall()
            # print("query data is-------->",query_data)
            domain+=[('id','in',[data[0] for data in query_data])]
            # domain+=[('tracking_ids.action_date','<=',self.to_date)]

        # if self.pending_with:
        #     if self.pending_with == 'shelf':
        #         domain+=[('is_on_shelf','=',True)]

        #     elif self.pending_with == 'inbox':
        #         domain+=[('state','=','in_progress'),('is_on_shelf','=',False)]
        #         if self.pending_employee_id:
        #             domain+=[('current_owner_id','=',self.pending_employee_id.user_id.id)]
        if self.status:
            ''' shelf
                in_progress
                pending_close
                pending_reopen
                closed
                closed_part
            '''
            domain+=[('state','=',self.status)]
        if self.pending_employee_id:
            domain+=[('current_owner_id','=',self.pending_employee_id.user_id.id)]

        # print("final domain is-------->",domain)
        tree_view_id = self.env.ref('smart_office.view_folder_master_inbox_all_subordinate_tree').id
        form_view_id = self.env.ref('smart_office.foldermaster_form_view').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'File Tracking Report',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'folder.master',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': domain,
            'target':'self',
            'context':{'create':False,'edit':False,'delete':False,'duplicate':False}
        }

class CorrespondenceTrackeWizard(models.TransientModel):
    _name = 'correspondence.tracker.wizard'
    _description = 'Correspondence Tracker Wizard'

    # left side
    subject = fields.Char("Subject")
    letter_number = fields.Char('Serial Number')
    # sender_name = fields.Char("Sender")
    branch_id = fields.Many2one('res.branch', 'Center')
    file_attached = fields.Selection([('yes','Yes'),('no','No')],string="Attached to File ?") 
    file_number = fields.Char("File Number")
    current_owner_id = fields.Many2one('res.users', 'Current Owner')
    # right side
    action_id = fields.Many2one('smart_office.correspondence.stage','Action', domain=[('code','not in',['cc','CC'])])
    employee_id = fields.Many2one('hr.employee','Action By')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')

    @api.multi
    def view_correspondence_tracker_report(self):
        # print("method called for corres tracker")

        domain = []
        if not self.env.user.has_group('muk_dms.group_dms_manager'):
            current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
            domain += ['|','|',('previous_owner_emp','child_of',current_employee.id),('last_owner_id.employee_ids','child_of',current_employee.id),('current_owner_id.employee_ids','child_of',current_employee.id)]
            
        if self.subject: 
            domain+=[('subject','ilike',self.subject)]

        if self.letter_number:
            domain+=[('letter_number','ilike',self.letter_number)]

        if self.branch_id:
            domain+=[('branch_id','=',self.branch_id.id)]

        if self.file_attached:
            if self.file_attached == 'yes':
                domain+=[('folder_id','!=',False)]
                if self.file_number:
                    domain+=[('folder_id.number','ilike',self.file_number)]
            if self.file_attached == 'no':
                domain+=[('folder_id','=',False)]
                if self.current_owner_id:
                    domain+=[('current_owner_id','=',self.current_owner_id.id)]

        join_query = '''select corres.id from muk_dms_file corres
                      inner join smart_office_correspondence_tracking soct
                      on soct.correspondence_id = corres.id
                      where '''

        query_to_be_executed = False
        and_condition_next = False

        if self.action_id:
            query_to_be_executed = True
            join_query += f'soct.action_stage_id={self.action_id.id}'
            and_condition_next = True
            
        if self.employee_id:
            query_to_be_executed = True
            custom_query = f'action_by_user_id={self.employee_id.user_id.id}'
            if and_condition_next:
                join_query += f' and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True

        if self.from_date and self.to_date:
            query_to_be_executed = True
            custom_query = f"soct.action_date >= '{self.from_date.strftime('%Y-%m-%d')}' and soct.action_date <= '{self.to_date.strftime('%Y-%m-%d')}'"
            if and_condition_next:
                join_query += f' and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True

        elif self.from_date:
            query_to_be_executed = True
            custom_query = f"soct.action_date >= '{self.from_date.strftime('%Y-%m-%d')}'"
            if and_condition_next:
                join_query += f' and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True

        elif self.to_date:
            query_to_be_executed = True
            custom_query = f"soct.action_date <= '{self.to_date.strftime('%Y-%m-%d')}'"
            if and_condition_next:
                join_query += f'and {custom_query}'
            else:
                join_query += custom_query
                and_condition_next = True

        if query_to_be_executed:
            # print("join_query is-------->",join_query)
            self._cr.execute(join_query)
            query_data = self._cr.fetchall()
            # print("query data is-------->",query_data)
            domain+=[('id','in',[data[0] for data in query_data])]

        # print("final domain is-------->",domain)
        tree_view_id = self.env.ref('smart_office.view_muk_dms_file_tracker_tree').id
        form_view_id = self.env.ref('muk_dms.view_dms_file_form').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'Correspondence Tracking Report',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'muk_dms.file',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': domain,
            'target':'self',
            'context':{'create':False,'edit':False,'delete':False,'duplicate':False}
        }
