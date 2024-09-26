from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class FileWizard(models.Model):
    _name = 'folder.wizard'
    _description = 'Wizard of File Forward'
    _rec_name = 'user'

    department = fields.Many2one('hr.department', string="Department")
    jobposition = fields.Many2one('hr.job', string="Functional Designation Old")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    # employee = fields.Many2one('hr.employee', string='Employee', domain="[('user_id', '!=', uid)]")
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related='employee.user_id', string='User')
    remarks = fields.Text('Remarks')

    defid = fields.Many2one('folder.master', invisible=1)
    sec_own_ids = fields.One2many('secondary.folder.owner', 'sec_own_id')

    @api.onchange('department','job_post_id')
    def _onchange_user(self):
        for rec in self:
            if rec.department.id and not rec.job_post_id.id:
                return {'domain': {'employee': [('department_id', '=', rec.department.id)]}}
            elif rec.job_post_id.id and not rec.department.id:
                return {'domain': {'employee': [('job_title', '=', rec.job_post_id.id)]}}
            elif rec.job_post_id.id and rec.department.id:
                return {'domain': {'employee': [('job_title', '=', rec.job_post_id.id),('department_id', '=', rec.department.id)]}}
            # elif (not rec.jobposition.id) and (not rec.department.id):
            #     return {'domain': {'employee': [('job_id', '=', rec.jobposition.id),('department_id', '=', rec.department.id)]}}
            # else:
            #     return {'domain': {'employee': [('id', '!=', 0)]}}

    @api.onchange('employee')
    def _onchange_emp_get_eve(self):
        for rec in self:
            if not rec.department.id:
                rec.department = rec.employee.department_id.id
            if not rec.job_post_id.id:
                rec.job_post_id = rec.employee.job_title.id
    
    @api.multi
    def confirm_button(self):
        current_user = self.env.user
        current_employee  = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        for rec in self:
            if not rec.user:
                raise UserError(_(f"{rec.employee.name} is not linked with any user.Hence the file can't be forwarded to him."))
            else:
                if rec.defid.current_owner_id == current_user:
                    notings = rec.defid.noting_ids.search([('folder_id','=',rec.defid.id)])
                    if notings:
                        notings.write({'secondary_employee_ids':[[4,rec.employee.id]]})
                        draft_noting = notings.filtered(lambda r:r.state == 'draft' and r.employee_id == current_employee)
                        if draft_noting:
                            draft_noting.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                            # start : Add tracking information of file_forwarded to new model 28-December-2021
                            # self.env['smart_office.file.tracking'].create({
                            #     'file_id':rec.defid.id,
                            #     'action_stage_id':self.env.ref('smart_office.file_stage_noting_added').id,
                            #     'remark':rec.remarks,
                            # })
                            # end : Add tracking information of correspondence_attached to new model 28-December-2021

                        comments = self.env['smart_office.comment'].search([('noting_id','in',notings.ids)])
                        draft_comment = comments.filtered(lambda r: r.employee_id == current_employee and  r.state=='draft')
                        if comments:
                            comments.write({'secondary_employee_ids':[[4,rec.employee.id]]})
                        if draft_comment:
                            draft_comment.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                                # start : Add tracking information of file_forwarded to new model 28-December-2021
                                # self.env['smart_office.file.tracking'].create({
                                #     'file_id':rec.defid.id,
                                #     'action_stage_id':self.env.ref('smart_office.file_stage_comment_added').id,
                                #     'remark':rec.remarks,
                                # })
                                # end : Add tracking information of correspondence_attached to new model 28-December-2021
                        if not draft_noting and not draft_comment:
                            latest_note = notings.filtered(lambda r:r.is_last_sequence == True)[-1:]
                            new_comment = latest_note.comment_ids.create({'noting_id':latest_note.id,'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                            new_comment.secondary_employee_ids = [[4,rec.employee.id]]
                    
                    dispatch_documents = rec.defid.document_dispatch
                    if dispatch_documents:
                        dispatch_documents.write({'secondary_employee_ids':[[4,rec.employee.id]]})
                        not_forwarded = dispatch_documents.filtered(lambda r: not r.forwarded)
                        if not_forwarded:
                            not_forwarded.write({'forwarded':True})
                        
                    # rec.defid.file_ids_m2m = [[6,0,rec.defid.file_ids.ids]]
                    # file_count = 0
                    # sec_own = []
                    # previous_owner = []
                    # previous_owner.append(rec.defid.current_owner_id.id)

                    # rec.defid.previous_owner = [(4, rec.defid.current_owner_id.id)]
                    # rec.defid.sec_owner = [(4, rec.defid.current_owner_id.id)]
                    # rec.defid.last_owner_id = rec.env.user.id
                    # rec.defid.current_owner_id = rec.user.id
                    # rec.defid.forwarded_by_employee_id = current_employee.id
                    # rec.defid.forwarded_to_employee_id = rec.employee.id
                    # rec.defid.forwarded_date = datetime.now().date()
                    
                    rec.defid.write({
                        'file_ids_m2m': [[6,0,rec.defid.file_ids.ids]],
                        'previous_owner': [(4, rec.defid.current_owner_id.id)],
                        'sec_owner': [(4, rec.defid.current_owner_id.id)],

                        'incoming_source':'forward',
                        'action_by_uid':self._uid,
                        'action_time':datetime.now(),
                        'action_date':datetime.now().date(),
                        'file_mode': 'inbox',
                        'forwarded_date':datetime.now().date(),
                        'forwarded_to_employee_id':rec.employee.id,
                        'forwarded_by_employee_id': current_employee.id,
                        'current_owner_id': rec.user.id,
                        'last_owner_id':current_user.id,
                    })

                    # self.env['folder.tracking.information'].create({
                    #     'create_let_id': rec.defid.id,
                    #     'forwarded_date': datetime.now().date(),
                    #     'forwarded_to_user': rec.user.id,
                    #     'forwarded_to_dept': rec.department.id,
                    #     'job_post_id': rec.job_post_id.id,
                    #     'forwarded_by': rec.env.uid,
                    #     'remarks': rec.remarks
                    # })
                    # start : Add tracking information of file_forwarded to new model 28-December-2021
                    self.env['smart_office.file.tracking'].create({
                        'file_id':rec.defid.id,
                        'action_stage_id':self.env.ref('smart_office.file_stage_file_forwarded').id,
                        'action_to_user_id':rec.employee.user_id.id,
                        'remark':rec.remarks,
                    })
                    # end : Add tracking information of file_forwarded to new model 28-December-2021

                    # f_details = ""
                    # if file_count == 0:
                    #     f_details = "File forwarded with no correspondence"
                    # elif file_count == 1:
                    #     f_details = "File forwarded with single correspondence"
                    # elif file_count > 1:
                    #     f_details = "File forwarded with multiple Correspondence"

                    # self.env['file.tracker.report'].create({
                    #     'name': str(rec.defid.folder_name),
                    #     'number': str(rec.defid.number),
                    #     'type': 'File',
                    #     'forwarded_by': str(current_employee.user_id.name),
                    #     'forwarded_by_dept': str(current_employee.department_id.name),
                    #     'forwarded_by_jobpos': str(current_employee.job_id.name),
                    #     'forwarded_by_branch': str(current_employee.branch_id.name),
                    #     'forwarded_date': datetime.now().date(),
                    #     'forwarded_to_user': str(rec.user.name),
                    #     'forwarded_to_dept': str(rec.department.name),
                    #     'forwarded_to_branch': str(rec.user.branch_id.name),
                    #     'job_pos': str(rec.job_post_id.name),
                    #     'action_taken': 'file_forwarded',
                    #     'remarks': rec.remarks,
                    #     'details': f_details
                    # })
                    # sec_own = []
                    # previous_owner = []
                    for file in rec.defid.file_ids:
                        # file_count+=1
                        file.write({'last_owner_id': rec.env.user.id,
                                    'responsible_user_id': rec.env.user.id,
                                    'current_owner_id': rec.user.id,
                                    'previous_owner': [(4, rec.env.user.id)],
                                    'previous_owner_emp': [(4,rec.employee.id)],
                                    'sec_owner': [(6, 0, rec.sec_own_ids.mapped('employee.user_id').ids)]})
                        # for line in rec.sec_own_ids:
                        #     sec_own.append(line.employee.user_id.id)

                        # self.env['file.tracking.information'].create({
                        #     'create_let_id': file.id,
                        #     'forwarded_date': datetime.now().date(),
                        #     'forwarded_to_user': rec.user.id,
                        #     'forwarded_to_dept': rec.department.id,
                        #     'job_post_id': rec.job_post_id.id,
                        #     'forwarded_by':rec.env.uid,
                        #     'remarks': rec.remarks
                        # })

                        # self.env['file.tracker.report'].create({
                        #     'name': str(file.name),
                        #     'number': str(file.letter_number),
                        #     'type': 'Correspondence',
                        #     'forwarded_by': str(current_employee.user_id.name),
                        #     'forwarded_by_dept': str(current_employee.department_id.name),
                        #     'forwarded_by_jobpos': str(current_employee.job_id.name),
                        #     'forwarded_by_branch': str(current_employee.branch_id.name),
                        #     'forwarded_date': datetime.now().date(),
                        #     'forwarded_to_user': str(rec.user.name),
                        #     'forwarded_to_dept': str(rec.department.name),
                        #     'job_pos': str(rec.job_post_id.name),
                        #     'forwarded_to_branch': str(rec.user.branch_id.name),
                        #     'action_taken': 'correspondence_forwarded',
                        #     'remarks': rec.remarks,
                        #     'details': "Correspondence Forwarded through File {}".format(rec.defid.number)
                        # })
                    rec.defid.write({'state': 'in_progress'})
                else:
                    raise ValidationError("You are not the current owner of the file.Hence you can't forward this file.")
                    
            self.env.user.notify_success("File forwarded successfully.")
            
            return {
                'name'      : 'My Inbox',
                'view_mode' : 'tree,form',
                'view_type' : 'form',
                'view_id'   : False,
                'views'     : [(self.env.ref("smart_office.foldermaster_tree_view1").id, 'tree'),(self.env.ref("smart_office.foldermaster_form_view").id, 'form')],
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    : [('current_owner_id','=', self._uid),('is_on_shelf','=',False),('state','not in',['draft','closed','closed_part'])],
                'context'   : {"create":False,"delete":False},
                }

class SecondaryOwners(models.Model):
    _name = 'secondary.folder.owner'
    _description = 'Secondary Owners'

    sec_own_id = fields.Many2one('folder.wizard')
    department = fields.Many2one('hr.department', string = "Department")
    jobposition = fields.Many2one('hr.job', string = "Job position")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related = 'employee.user_id', string='User')

    @api.onchange('department','job_post_id')
    def _onchange_user(self):
        for rec in self:
            if rec.department.id and not rec.job_post_id.id:
                return {'domain': {'employee': [('department_id', '=', rec.department.id)]}}
            elif rec.job_post_id.id and not rec.department.id:
                return {'domain': {'employee': [('job_title', '=', rec.job_post_id.id)]}}
            elif rec.job_post_id.id and rec.department.id:
                return {'domain': {'employee': [('job_title', '=', rec.job_post_id.id),('department_id', '=', rec.department.id)]}}
            # else:
            #     return {'domain': {'employee': ['|', ('job_id', '=', rec.jobposition.id),('department_id', '=', rec.department.id)]}}
            else:
                return {'domain': {'employee': [('id', '!=', 0)]}}
