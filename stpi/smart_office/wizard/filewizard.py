from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class FileWizard(models.Model):
    _name = 'file.wizard'
    _description = 'Wizard of correspondence forward'
    _rec_name = 'user'

    department = fields.Many2one('hr.department', string="Department")
    jobposition = fields.Many2one('hr.job', string="Job Position")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related='employee.user_id', string='User')
    remarks = fields.Text('Remarks')
    defid = fields.Many2one('muk_dms.file','Correspondence', invisible=1)
    sec_own_ids = fields.One2many('secondary.file.owner', 'sec_own_id')

    @api.onchange('department','job_post_id')
    def _onchange_user(self):
        args = [('user_id','!=',self._uid)]
        if self.department:
            args += [('department_id', '=', self.department.id)]
        if self.job_post_id:
            args += [('job_title', '=', self.job_post_id.id)]
        return {'domain': {'employee': args}}

    @api.onchange('employee')
    def set_related_emp_data(self):
        self.department = self.mapped('employee.department_id')
        self.job_post_id = self.mapped('employee.job_title')
                
    @api.multi
    def confirm_button(self):
        for res in self:
            if res.user.id == False:
                raise UserError(_("%s is not configured to owned this file") % res.employee.name)
            else:
                if res.defid.current_owner_id.id == res.env.user.id:
                    current_employee = self.env['hr.employee'].search([('user_id', '=', res.defid.current_owner_id.id)], limit=1)
                    # sec_own = []
                    # previous_owner = []
                    # previous_owner.append(res.defid.current_owner_id.id)
                    # Previous owner append
                    transfer_to_emp = res.env['hr.employee'].search([('user_id', '=', res.defid.current_owner_id.id)], limit=1)
                    res.defid.write({'previous_owner_emp': [(4, transfer_to_emp.id)],
                                     'forward_from_id': self._uid,
                                     'forward_to_id': res.employee.user_id.id,
                                     'last_owner_id': res.defid.current_owner_id.id,
                                     'current_owner_id': res.user.id,
                                     'responsible_user_id': res.user.id,
                                     'forwarded_date': datetime.now().date(),
                                     'incoming_source': 'forward',
                                     'action_by_uid': self._uid,
                                     'action_time': fields.Datetime.now(),
                                     'action_date': fields.Date.today()})

                    self.env['smart_office.correspondence.tracking'].create({
                        'correspondence_id': self._context.get('active_id'),
                        'action_stage_id': self.env.ref('smart_office.corres_stage_forwarded').id,
                        'action_to_user_id': self.employee.user_id.id,
                        'remark':res.remarks
                    })
                    self.env['userwise.correspondence.tracking'].create({
                        'correspondence_id': self._context.get('active_id'),
                        'action_stage_id': self.env.ref('smart_office.userwise_corres_forward_by_someone').id,
                        'user_id': self.employee.user_id.id,
                        'remark': res.remarks
                    })
                    self.env['userwise.correspondence.tracking'].create({
                        'correspondence_id': self._context.get('active_id'),
                        'action_stage_id': self.env.ref('smart_office.userwise_corres_forward_to_someone').id,
                        'action_to_user_id': self.employee.user_id.id,
                        'remark': res.remarks
                    })

                    # Secondary Owner id created
                    # res.defid.write({'sec_owner': [(4, line.employee.user_id.id)],
                    #                  'previous_owner': [(4, line.employee.user_id.id)]})
                    for index,cc_employee in enumerate(res.sec_own_ids.mapped('employee') - res.employee):
                        copied_correspondence = res.defid.with_context(no_serial_generation=True,no_log_record=True).copy()
                        # print("copied_correspondence",copied_correspondence)
                        # print("index is",copied_correspondence)
                        copied_correspondence.write({
                            # 'name':f'{res.defid.name}({index})',
                            # 'incoming_source':'cc',
                            'incoming_source':'forward',
                            'sec_owner':[(6,0,[])],
                            'previous_owner':[(6,0,[])],
                            'previous_owner_emp':[(6,0,[])],
                            'forward_from_id':self._uid,
                            'forward_to_id':cc_employee.user_id.id,
                            'current_owner_id':cc_employee.user_id.id,
                            'last_owner_id':cc_employee.user_id.id,
                            'responsible_user_id':cc_employee.user_id.id,
                            'forwarded_date':datetime.now().date(),
                            'action_by_uid':self._uid,
                            'action_time':fields.Datetime.now(),
                            'action_date':fields.Date.today(),
                            'parent_correspondence_id':res.defid.id,
                            'tracking_info_ids':[[0,0,{
                                    'action_date':track_log.action_date  ,
                                    'action_time': track_log.action_time ,
                                    'action_by_user_id':track_log.action_by_user_id.id ,
                                    'action_stage_id':track_log.action_stage_id.id ,
                                    'current_owner_id':track_log.current_owner_id and track_log.current_owner_id.id or False,
                                    'action_to_user_id': track_log.action_to_user_id and  track_log.action_to_user_id.id or False,
                                    'remark':track_log.remark or ''}] for track_log in res.defid.tracking_info_ids],

                            'userwise_tracking_ids':[[0,0,{
                                'action_date': log_record.action_date,
                                'action_time': log_record.action_time,
                                'action_by_user_id': log_record.action_by_user_id.id,
                                'action_stage_id': log_record.action_stage_id.id,
                                'user_id': log_record.user_id and log_record.user_id.id or False,
                                'action_to_user_id': log_record.action_to_user_id and log_record.action_to_user_id.id or False,
                                'remark': log_record.remark,
                                'visible_user_ids': [[6,0,log_record.visible_user_ids.ids]],
                            }] for log_record in res.defid.userwise_tracking_ids],
                        })
                        self.env['smart_office.correspondence.tracking'].create({
                            'correspondence_id': copied_correspondence.id,
                            'action_stage_id': self.env.ref('smart_office.corres_stage_cc_forwarded').id,
                            'action_to_user_id': cc_employee.user_id.id,
                            'remark':res.remarks
                        })
                        self.env['userwise.correspondence.tracking'].create({
                            'correspondence_id': copied_correspondence.id,
                            'action_stage_id': self.env.ref('smart_office.userwise_corres_cc_by_someone').id,
                            'user_id': self._uid,
                            'action_to_user_id':cc_employee.user_id.id,
                            'remark': res.remarks
                        })
                       
                    # sec_own.append(line.employee.user_id.id)
                    # res.defid.sec_owner = [(6,0,sec_own)]
                    # res.env['file.tracking.information'].create({
                    #     'create_let_id': res.defid.id,
                    #     'forwarded_date': datetime.now().date(),
                    #     'forwarded_to_user': res.user.id,
                    #     'forwarded_to_dept': res.department.id,
                    #     'job_post_id': res.job_post_id.id,
                    #     'forwarded_by':res.env.uid,
                    #     'remarks':res.remarks
                    # })
                    # res.env['file.tracker.report'].create({
                    #     'name': str(res.defid.name),
                    #     'number': str(res.defid.letter_number),
                    #     'type': 'Correspondence',
                    #     'forwarded_by': str(current_employee.user_id.name),
                    #     'forwarded_by_dept': str(current_employee.department_id.name),
                    #     'forwarded_by_jobpos': str(current_employee.job_id.name),
                    #     'forwarded_by_branch': str(current_employee.branch_id.name),
                    #     'forwarded_date': datetime.now().date(),
                    #     'forwarded_to_user': str(res.user.name),
                    #     'forwarded_to_dept': str(res.department.name),
                    #     'job_pos': str(res.job_post_id.name),
                    #     'forwarded_to_branch': str(res.user.branch_id.name),
                    #     'action_taken': 'correspondence_forwarded',
                    #     'remarks': res.remarks,
                    #     'details': 'Correspondence Forwarded'
                    # })
                    
                else:
                    raise ValidationError("You are not able to forward this file, as you are not the Primary owner of this file")
                
        add_correspondence = self._context.get('action_location') == 'add_correspondence'
        # Return to 'Add Correspondences' or 'My Inbox' according to action context
        self.env.user.notify_success("Correspondence forwarded successfully.")
        return {
                'name'      : 'Add Correspondences' if add_correspondence else 'My Inbox',
                'view_mode' : 'tree,kanban,graph,pivot,form',
                'view_type' : 'form',
                'view_id'   :  False,
                'res_model' : 'muk_dms.file',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    : [('current_owner_id', '=', self._uid),('folder_id', '=', False)],
                'context'   : {'action_location':'add_correspondence'} if add_correspondence else {"create":False,"action_location":"inbox"},
                }

class SecondaryOwners(models.Model):
    _name = 'secondary.file.owner'
    _description = 'Secondary Owners'

    sec_own_id = fields.Many2one('file.wizard',"File Wizard")

    employee = fields.Many2one('hr.employee','Employee')
    department = fields.Many2one('hr.department',"Department")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')

    jobposition = fields.Many2one('hr.job',"Job position")
    user = fields.Many2one('res.users','User', related='employee.user_id')

    @api.onchange('employee')
    def set_related_data(self):
        self.department = self.mapped('employee.department_id')
        self.job_post_id = self.mapped('employee.job_title')
        self.jobposition = self.mapped('employee.job_id')

    @api.onchange('department','job_post_id')
    def _onchange_user(self):
        args = [('user_id','!=',self._uid)]
        if self.department:
            args += [('department_id', '=', self.department.id)]
        if self.job_post_id:
            args += [('job_title', '=', self.job_post_id.id)]
            
        return {'domain': {'employee': args}}
