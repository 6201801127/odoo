import string
from odoo import models, fields, api
from datetime import date,datetime
from odoo.exceptions import ValidationError
from odoo.addons.kw_utility_tools import kw_validations
from lxml import etree


class kw_employee_grievance(models.Model):
    _name        = 'kw.grievance'
    _description = 'Grievance'
    _rec_name    = 'grievance_code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee
        
    @api.depends('employee_id')
    def _show_grievance(self):
        for record in self:
            if record.employee_id.user_id.has_group('kw_grievance.griev_user') and record.state == 'draft':
                record.show_grievance = True
            # elif self.env.user.has_group('kw_grievance.kw_griev_manager_group') and record.state == 'receive' and record.cmd_forward_boolean == False:
            #     record.show_grievance = True
            else:
                record.show_grievance = False
                
 
            
    # @api.depends('employee_id')
    # def check_spoc_user(self):
    #     print('2222222222222')
    #     for rec in self:
    #         print('rec=====',rec)
    #         if self.env.user.employee_ids.id in rec.grievance_type_id.concerned_person_ids.ids:
    #         print('1111111111')
    #         rec.spoc_user = True
        
    @api.depends('employee_id')
    def _check_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
            # else:
            #     record.check_user = False
            # print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
            if self.env.user.has_group('kw_grievance.griev_spoc_committee_group') and self.env.user.employee_ids.id in record.grievance_type_id.concerned_person_ids.ids and record.state=='apply':
                # print('1111111111111111')
                record.check_spoc_user = True
            # else:
            #     record.check_spoc_user = False
            # if self.env.user.has_group('kw_grievance.kw_griev_manager_group'):
            #     record.check_manger_user = True
            # else:
            #     record.check_manger_user = False
            # if self.env.user.has_group('kw_grievance.griev_section_officer'):
            #     record.check_so_user = True
            # else:
            #     record.check_so_user = False
            # print(self.env.user.employee_ids.id,record.grievance_type_id.concerned_person_ids.ids,'========')
            if self.env.user.employee_ids.id in record.grievance_type_id.concerned_person_ids.ids:
                # print('1111111111')
                record.spoc_user = True

                  
    @api.depends('state')    
    def _compute_so_section(self):
        for record in self:
            if record.so_verify_boolean == True or record.so_forward_boolean == True or record.so_update_boolean == True:
                record.show_so_section=True
            else:
                record.show_so_section=False
            
    grievance_code = fields.Char(string="Grievance No.")
    employee_id = fields.Many2one('hr.employee',string="Employee name",default=get_employee)
    grievance_type_id = fields.Many2one('kw.grievance.type', string="Grievance Type",tracking=True)
    grievance_sub_categories=fields.Char(string="Grievance Category")
    # anonymous = fields.Boolean(string='Anonymous')    
    subject = fields.Char(string="Subject",)
    description = fields.Text(string="Description")
    uploaded_doc = fields.Binary(attachment=True, help="Only .jpeg, .png, .pdf, .mp3, .mp4 format are allowed. Maximum file size is 10 MB")
    spoc_user = fields.Boolean(compute ="_check_user")
    file_name = fields.Char()
    state = fields.Selection([('draft', 'Draft'),
                              ('apply', 'Applied'),
                              ('in_progress', 'In Progress'),
                              ('resolve', 'Resolved'), ],
                               string='Status',default='draft',track_visibility='always')
    cc_remark  = fields.Html('CC Report')
    cc_document = fields.Binary(attachment=True,help="Only .jpeg, .png, .pdf, .mp3, .mp4 format are allowed. Maximum file size is 10 MB")
    cc_file_name = fields.Char()
    commandant_remark = fields.Text('Remark')
    so_remark = fields.Html('SO Report')
    so_document = fields.Binary(string="Upload File",attachment=True,help="Only .jpeg, .png, .pdf, .mp3, .mp4 format are allowed. Maximum file size is 10 MB")
    so_file_name = fields.Char()
    so_verify_boolean = fields.Boolean()
    cc_verify_button = fields.Boolean()
    # emp_branch = fields.Char(related="employee_id.job_branch_id",string="Current Office")
    cc_action_taken_by =  fields.Many2one('hr.employee',tracking=True)
    cmd_action_taken_by =  fields.Many2one('hr.employee',tracking=True)
    so_action_taken_by =  fields.Many2one('hr.employee',tracking=True)
    
    department = fields.Char(related="employee_id.department_id.name",string="Department")
    designation  = fields.Char(related="employee_id.job_id.name",string="Designation")
    # unit  = fields.Selection(related="employee_id.unit",string="Unit",store=True)
    # cmd_forward_boolean = fields.Boolean()
    check_user = fields.Boolean(compute="_check_user")
    check_spoc_user = fields.Boolean(compute="_check_user")
    check_manger_user = fields.Boolean(compute="_check_user")
    # check_so_user = fields.Boolean(compute="_check_user")
    forwarded_section_id = fields.Many2one('hr.department',string="Forwarded Section") 
    # forwarded_section = fields.Many2one('kw.grievance.type',string="Forwarded Section")
    show_grievance = fields.Boolean(compute="_show_grievance")
    cc_action_taken_on = fields.Datetime()
    so_action_taken_on = fields.Datetime()
    cmd_action_taken_on = fields.Datetime()
    
    # case_type = fields.Selection([('minor', 'Minor'),('major', 'Major')],default='minor')
    forward_remark = fields.Text()
    forwarded_by =  fields.Many2one('hr.employee',string="Action Taken By",track_visibility='always')
    forwarded_on = fields.Datetime('Action Taken On')
    
    show_approve_option = fields.Boolean(compute="_show_forward_option")
    show_forward_option = fields.Boolean(compute="_show_forward_option")
    
    # pending_at = fields.Char(compute='_compute_pending_at',string='Action To Be Taken By')
    sort = fields.Integer(compute='_compute_sort', store=True)
    
    so_update_boolean  = fields.Boolean()
    
    forward_section = fields.Many2one('hr.department')
    forward_section_done_by = fields.Many2one('hr.employee',tracking=True)
    forward_action_taken_on = fields.Datetime()
    so_forward_boolean = fields.Boolean()
    
    show_so_section = fields.Boolean(compute='_compute_so_section')
    fo_creation_section_id = fields.Many2one('hr.department')

    remark = fields.Text(string="Remark")
    action_log_ids      = fields.One2many('kw_apply_grievance_action_log','apply_grievance_id',string='Action Logs')

      
    @api.constrains('so_document','uploaded_doc','cc_document')
    def validate_document_attach(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf','audio/mp3', 'video/mp4']
        for record in self:

            kw_validations.validate_file_mimetype(record.so_document,allowed_file_list)
            kw_validations.validate_file_size(record.so_document,10)
            
            kw_validations.validate_file_mimetype(record.uploaded_doc,allowed_file_list)
            kw_validations.validate_file_size(record.uploaded_doc,10)
             
            kw_validations.validate_file_mimetype(record.cc_document,allowed_file_list)
            kw_validations.validate_file_size(record.cc_document,10)
    
    # @api.onchange('grievance_type_id','case_type')
    # def onchange_grievance_type_id(self):
    #     for rec in self:
    #         rec.forwarded_section_id = False
    #         if rec.grievance_type_id:
    #             grievance_type = self.env['kw.grievance.type'].sudo().search([('name','=',rec.grievance_type_id.name)])
    #             return {'domain': {'forwarded_section_id': [('id','=',grievance_type.department_id.id)]}}
               
    # def forward_grievance(self):
    #     if not self.forwarded_section_id:
    #         raise ValidationError("Forward User is Required")
    #     self.write({'state':'in_progress',
    #                 'cmd_forward_boolean':True,
    #                 'forwarded_by': self.env.user.employee_ids.id,
    #                 'forwarded_on': datetime.today()
    #                 })
    #     self.mail_firing(forward=True)  
    #     if self.forwarded_section_id.so_user_ids:         
    #         for rec in self.forwarded_section_id.so_user_ids:
    #             self.activity_schedule('kw_grievance.mail_act_grievance_forward',date_deadline=date.today(),user_id=rec.id)
    #         self.activity_unlink(['kw_grievance.mail_act_grievance_submit'])
    #     self.env.user.notify_info(message='Application is forwarded sucessfully')
      
                  

    @api.model
    def create(self, vals):
        vals['grievance_code'] = self.env['ir.sequence'].next_by_code('grievance_management') or '/'
        res = super(kw_employee_grievance, self).create(vals)
        return res

    def apply_grievance(self):
        if self.employee_id:
            self.write({'state':'apply'})

        # spoc_committee_users = self.env.ref('kw_grievance.griev_spoc_committee_group').users
        # emails = self.grievance_type_id.concerned_person_ids.mapped('work_email')
        emails = ','.join(self.grievance_type_id.concerned_person_ids.mapped('work_email'))
        # print('employee mail>>>>',emails)
        mail_template = self.env.ref('kw_grievance.grievance_applied_mail_template')   
        mail_template.with_context(dept_name='Team', emails=emails).send_mail(
            self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        # if self.employee_id:
        #     self.write({'state': 'in_progress',
        #                 'cmd_forward_boolean': False
        #         })
            # self.mail_firing
            # if self.grievance_type_id.department_id.so_user_ids:
            #     for rec in self.grievance_type_id.department_id.so_user_ids:
            #         self.activity_schedule('kw_grievance.mail_act_grievance_forward',
            #                     date_deadline=date.today(),user_id=rec.id)
        # else:
            # self.state = 'apply'
            # if self.employee_id.parent_id.user_id:
            #     self.activity_schedule('kw_grievance.mail_act_grievance_apply',date_deadline=date.today(),user_id=self.employee_id.parent_id.user_id.id)
            # self.mail_firing(apply=True)

    def grievance_inprgress_button(self):
        form_view_id = self.env.ref('kw_grievance.inprogress_remark_form_view').id
        action = {
            'name': 'Remark',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_id': self.id,
            'view_id'   : False,
            'res_model' : 'kw.grievance',
            'type'      : 'ir.actions.act_window',
            'target'    : 'new',
            'views'     : [(form_view_id, 'form')],
            }
        return action

    @api.multi
    def grievance_inprgress(self):
        remark = self.remark.strip()
        if self.remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        self.write({'state': 'in_progress',
                    'approver_id': False,
                    'remark': False,
                    'action_datetime':datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark,'state': 'In Progress'}]]
                    })
        

    def grievance_resolve_button(self):
        form_view_id = self.env.ref('kw_grievance.resolve_remark_form_view').id
        action = {
            'name': 'Remark',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_id': self.id,
            'view_id'   : False,
            'res_model' : 'kw.grievance',
            'type'      : 'ir.actions.act_window',
            'target'    : 'new',
            'views'     : [(form_view_id, 'form')],
            }
        return action

    @api.multi
    def grievance_resolve(self):
        remark = self.remark.strip()
        if remark == '':
            raise ValidationError("White space(s) not allowed in first place.")
        self.write({'state': 'resolve',
                    'approver_id': False,
                    'remark': False,                  
                    'action_datetime':datetime.now(),
                    'action_log_ids': [[0, 0, {'remark': remark,'state': 'Resolved'}]]
                    })
        template = self.env.ref('kw_grievance.grievance_resolve_mail_to_user_template')
        template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('take_action'):
          
             # spoc_committee_users = self.env.ref('kw_grievance.griev_spoc_committee_group').users
        # emails = self.grievance_type_id.concerned_person_ids.mapped('work_email')
            # spoc_committee_users = self.grievance_type_id.concerned_person_ids.id
            # print("########",spoc_committee_users)

            if self.env.user.has_group('kw_grievance.griev_spoc_committee_group'):
                #   if spoc_committee_users:
                # print('1111111111111111')
                args += [('state', 'in', ['apply','in_progress'])]
                # print(args)
                
            # elif self.env.user.has_group('kw_grievance.kw_griev_manager_group'):
            #     args += [('state','in',['in_progress',])]

            # elif self.env.user.has_group('kw_grievance.griev_section_officer'):
            #     args += [('state','in',['in_progress'])]
            else:
                args += [('state', 'in', ['draft'])]
               
        return super(kw_employee_grievance, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.depends('state')
    def _compute_sort(self):
        sort_order = {
                'draft': 1,
                'apply': 2,
                'in_progress':3,
                'resolve': 4,        
            }
        for record in self:
            record.sort = sort_order.get(record.state)
             
        
    def btn_open_view(self):
        form_view_id = self.env.ref('kw_grievance.kw_emp_grievance_form_view').id
        for rec in self:
            action = {
            'type': 'ir.actions.act_window',
            'name': 'Grievance',
            'view_mode': 'form',
            'res_model': 'kw.grievance',
            'views': [(form_view_id, 'form')],
            'target': 'self',
            'res_id':rec.id,
            'flags'     : {'mode': 'edit', 'create': False, },
        }
        return action

class GrievlevelConfig(models.Model):
    _name = "griev_level_configuration"
    
    level = fields.Integer()
    name = fields.Char()