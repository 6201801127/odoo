from odoo import models, fields, api,_
from datetime import date,datetime,timedelta
from odoo.exceptions import ValidationError
import re
import base64
from odoo.tools.mimetypes import guess_mimetype

# from odoo.addons.kw_utility_tools import kw_validations


class BssclGrievance(models.Model):
    _name = 'bsscl.grievance'
    _description = 'Grievance'
    _rec_name = 'grievance_code'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee

    # @api.depends('employee_id')
    # def _show_grievance(self):
    #     for record in self:
    #         if record.employee_id.user_id.has_group('bsscl_grievance.griev_user') and record.state in ['draft']:
    #             record.show_grievance = True
    #         elif self.env.user.has_group('bsscl_employee.commissioner_id') and record.state == 'receive' and record.cmd_forward_boolean == False:
    #             record.show_grievance = True
    #         else:
    #             record.show_grievance = False


    
    grievance_code = fields.Char(string="Grievance No.(शिकायत संख्या")
    employee_id = fields.Many2one('hr.employee',string="Employee name(कर्मचारी का नाम)",default=get_employee)
    grievance_type_id = fields.Many2one('bsscl.grievance.type',string="Grievance Type (शिकायत प्रकार)",tracking=True)
    subject = fields.Char(string="Subject (विषय)",size=100)
    description = fields.Text(string="Description(विवरण)")
    uploaded_doc = fields.Binary(attachment=True, store=True, help="Only .jpeg, .png, .pdf, .mp3, .mp4 format are allowed. Maximum file size is 10 MB")
   
    file_name = fields.Char()
    state = fields.Selection([('draft', 'Draft'),
                              ('apply', 'Applied'),                       
                              ('verify', 'Verified'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ('reset','Reset')
                              ], string='State(स्थति)',default='draft',tracking=True)
    cc_remark  = fields.Text('Manager Remarks/प्रबंधक टिप्पणी')
    cc_document = fields.Binary(attachment=True,help="Only .jpeg, .png, .pdf, .mp3, .mp4 format are allowed. Maximum file size is 10 MB")
    cc_file_name = fields.Char()
    commandant_remark = fields.Text('Commissioner Remark/(आयुक्त टिप्पणी)')
   
    cc_verify_button = fields.Boolean()
    emp_branch = fields.Char(related="employee_id.current_office_id.name",string="Current Office /(वर्तमान कार्यालय)", store=True)

    cc_action_taken_by =  fields.Many2one('hr.employee',tracking=True)
    cmd_action_taken_by =  fields.Many2one('hr.employee',tracking=True)

    
    department = fields.Char(related="employee_id.department_id.name",string="Department (विभाग)", store=True)
    designation  = fields.Char(related="employee_id.job_id.name",string="Designation (पद)", store=True)
    cmd_forward_boolean = fields.Boolean()
    check_user = fields.Boolean(compute="_check_user")
    # check_cc_user = fields.Boolean(compute="_check_user")
    # check_cmd_user = fields.Boolean(compute="_check_user")
    # check_so_user = fields.Boolean(compute="_check_user")
  
    # show_grievance = fields.Boolean(compute="_show_grievance")
    applied_on = fields.Datetime(tracking=True)
    applied_by = fields.Many2one('hr.employee',string="Applied By",tracking=True)
    cc_action_taken_on = fields.Datetime(tracking=True)
    cmd_action_taken_on = fields.Datetime(tracking=True)
    
    forward_remark = fields.Text()
    forwarded_by =  fields.Many2one('hr.employee',string="Action Taken By",tracking=True)
    forwarded_on = fields.Datetime('Action Taken On',tracking=True)
    
    show_approve_option = fields.Boolean(compute="_show_forward_option")
    
    pending_at = fields.Char(compute='_compute_pending_at',string='Action To Be Taken By/(द्वारा की गई कार्रवाई)')
    sort = fields.Integer(compute='_compute_sort', store=True)
    
    
    forward_section_done_by = fields.Many2one('hr.employee',tracking=True)
    forward_action_taken_on = fields.Datetime()
    rej_reas = fields.Char('Rejection Reason/Rejection')

   
    
    @api.constrains('subject')
    @api.onchange('subject')	
    def _check_subject(self):
        for rec in self:
            if rec.subject and not re.match(r'^[A-Za-z\s]*$',str(rec.subject)):
                raise ValidationError(_("Subject should be an alphabet"))
            
    @api.constrains('description')
    @api.onchange('description')	
    def _onchange_description(self):
        for rec in self:
            if rec.description and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.description)):
                raise ValidationError("Description should be an alphabet")
            if rec.description:
                if len(rec.description) > 500:
                    raise ValidationError('Number of characters must not exceed 500')
                
    @api.constrains('uploaded_doc')
    def check_uploaded_document(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        for record in self:
            # for rec in record.uploaded_doc:
                if record.uploaded_doc:
                    acp_size = ((len(record.uploaded_doc) *3/4) /1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.uploaded_doc))        
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only .jpeg, .jpg, .png, .pdf, .doc, .docx format are allowed.")
                    if acp_size > 2:
                        raise ValidationError("Maximum file size is 2 MB / अधिकतम फ़ाइल आकार 2 एमबी है")
                    

    


    @api.depends('state')
    def _compute_pending_at(self):
        for record in self:
            if record.state == 'draft':
                record.pending_at = 'Grievance is not Applied'
            if record.state == 'apply':
                record.pending_at = record.employee_id.parent_id.name
          
            else:
                record.pending_at = '--'

    @api.model
    def create(self, vals):
        vals['grievance_code'] = self.env['ir.sequence'].next_by_code('grievance_management') or '/'
        res = super(BssclGrievance, self).create(vals)
        return res

    def apply_grievance(self):
        self.applied_on = datetime.today()
        self.applied_by = self.env.user.employee_ids.id
        self.state = 'apply'
            

    def submit_grievance(self):
        if not self.cc_remark:
            raise ValidationError("Please Fill Manager Remark")
        else:
            for record in self:
                record.write({'state':'approve',
                            'cc_verify_button':True,
                            'cc_action_taken_by': self.env.user.employee_ids.id,
                            'cc_action_taken_on': datetime.today()
                            })
               


    def btn_open_view(self):
        form_view_id = self.env.ref('bsscl_grievance.bsscl_emp_grievance_form_view').id
        for rec in self:
            action = {
            'type': 'ir.actions.act_window',
            'name': 'Grievance',
            'view_mode': 'form',
            'res_model': 'bsscl.grievance',
            'views': [(form_view_id, 'form')],
            'target': 'self',
            'res_id':rec.id,
            'flags'     : {'mode': 'edit', 'create': False, },
        }
        return action

                        
    @api.depends('employee_id')
    def _show_forward_option(self):
        for record in self:
           
            if self.env.user.has_group('bsscl_employee.commissioner_id') and record.state == 'verify':
                record.show_approve_option = True
            else:
                record.show_approve_option = False

    @api.depends('state')
    def _compute_sort(self):
        sort_order = {
                'draft': 1,
                'apply': 2,
                'receive': 3,
                'in_progress':4,
                'verify':5,
                'approve':6,
                'reject': 7,
            }
        for record in self:
            record.sort = sort_order.get(record.state)

    @api.depends('employee_id')
    def _check_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
                print("++++++++++++++++++++++")
            else:
                record.check_user = False
                print("check user not=====================")

            # if self.env.user.has_group('bsscl_employee.deputy_com_id'):
            #         record.check_cc_user = True
            # else:
            #     record.check_cc_user = False
            # if self.env.user.has_group('bsscl_employee.commissioner_id'):
            #     record.check_cmd_user = True
            # else:
            #     record.check_cmd_user = False
           

     # for one level approval
            
    # def approve_grievance(self):
    #     # if self.fo_creation_section_id and self.commandant_remark : 
        
    #     if not self.commandant_remark:
    #         raise ValidationError("Commisioner Final Remark is Required")
    #     self.write({'state':'approve',
    #                 'cmd_action_taken_by': self.env.user.employee_ids.id,
    #                 'cmd_action_taken_on': datetime.today()
    #                 })


         
    # def reject_grievance(self):
    #     if not self.commandant_remark:
    #         raise ValidationError("Commisioner Remark is Required")
    #     self.write({
    #         'state': 'reject',
    #         'cmd_action_taken_by': self.env.user.employee_ids.id
    #     })

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context.get('take_action'):
    #         ids = []
    #         if self.env.user.has_group('bsscl_employee.deputy_com_id'):
    #             args += [('state', 'in', ['apply']),('employee_id.parent_id.user_id', '=', self.env.user.id)]
                
    #         elif self.env.user.has_group('bsscl_employee.commissioner_id'):
    #             args += [('employee_id.current_office_id.id', 'in', self.env.user.branch_ids.ids),('state','in',['verify'])]

    #         else:
    #             args += [('state', 'in', ['draft'])]
               
    #     return super(BssclGrievance, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)