
# -*- coding: utf-8 -*-\
import base64,re
from odoo import models, fields, api
from datetime import datetime,timedelta, date
from odoo.exceptions import UserError,ValidationError
from odoo.tools.mimetypes import guess_mimetype



class ExitTransferManagement(models.Model):
    _name = 'exit.transfer.management'
    _description = 'Exit Transfer Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee
    
    @api.onchange('employee_id')	
    def _onchange_exit_master(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        if self.env.user.has_group("bsscl_employee.group_hr_ra"):
           return {'domain': {'exit_type': [('user_type', '=','hr')]}}
        else:
            return {'domain':  {'exit_type': [('user_type', '=','user')],
                                'employee_id': [('id', 'in',employee.ids)]}}     

    @api.depends("employee_id")
    def get_des_and_id(self):
        for rec in self:
            if rec.employee_id:
                rec.job_id = rec.employee_id.job_id.id
                rec.branch_id = rec.employee_id.current_office_id.id
                rec.department_id = rec.employee_id.department_id.id

    name = fields.Char(tracking=True)
    employee_id = fields.Many2one("hr.employee", string="Employee Name / कर्मचारी का नाम",tracking=True ,default = get_employee)
    job_id = fields.Many2one("hr.job", string="Designation / पद", compute="get_des_and_id", store=True,copy=False,tracking=True)
    branch_id = fields.Many2one("res.branch", string="Current Office / वर्तमान कार्यालय", compute="get_des_and_id", store=True,copy=False,tracking=True)
    to_branch_id = fields.Many2one("res.branch", string="To Office / अगला कार्यालय", store=True,copy=False,tracking=True)
    department_id = fields.Many2one("hr.department", string="Department / विभाग", compute="get_des_and_id", store=True,copy=False,tracking=True)
    exit_reason = fields.Text("Exit Reason / बाहर निकलने का कारण",tracking=True)
    date = fields.Date('Current Date / आज की तारीख',default=fields.Date.context_today,tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Document / दस्तावेज़",
                                      help="Employee can submit any documents which supports their explanation")
    exit_date = fields.Date('Exit Date / बाहर निकलने की तारीख',track_visibility=True)
    # exit_type = fields.Selection([("Suspended", "Suspended"),
    #     ("Resigned", "Resigned"),
    #     ("Contract Expired ", "Contract Expired "),
    #     ("technical resignation","Technical Resignation"),
    #     ("Superannuation", "Superannuation"),
    #     ("Deceased","Deceased"),
    #     ("Terminated","Terminated"),
    #     ("Absconding","Absconding"),
    #     ("Transferred","Transferred"),
    #     ("deputation","Deputation"),
    # ],string='Type of Exit / निकास का प्रकार',tracking=True)
    exit_type = fields.Many2one("exit.master",string='Type of Exit / निकास का प्रकार',tracking=True)

    # reg_type = fields.Selection([
    #     ("internal","Internal"),
    #     ("external","External"),
    #     ("deputation","Deputation")
    # ],string='Resignation Type / इस्तीफे का प्रकार',tracking=True)

    # transferred_req = fields.Selection([
    #     ("yes","Yes"),
    #     ("no","No")
    # ],string='Transferred Required / तबादला आवश्यक है',tracking=True)

    state = fields.Selection([("draft", "Draft"),
        ("verify", "Verify"),
        ("send_for_approval", "Approval Waiting"),
        ("complete", "Completed"),
        ("cancel","Cancelled")
    ],string='Status / स्थति', copy=False, default='draft', required=True, readonly=True,tracking=True)

    cc_remark  = fields.Text('Deputy Commissioner Remark/उपायुक्त टिप्पणी',tracking=True)
    cc_document = fields.Binary(attachment=True,tracking=True)
    # cc_file_name = fields.Char()
    commandant_remark = fields.Text('Manager Remark / प्रबंधक टिप्पणी',tracking=True)
    # cc_action_taken_by =  fields.Many2one('hr.employee',tracking=True)
    cmd_action_taken_by =  fields.Many2one('hr.employee',tracking=True)
    # cc_action_taken_on = fields.Datetime(tracking=True)
    cmd_action_taken_on = fields.Datetime(tracking=True)
    # check_user = fields.Boolean(compute="_check_user")
    # check_cc_user = fields.Boolean(compute="_check_user")
    # check_cmd_user = fields.Boolean(compute="_check_user")
    cc_verify_button = fields.Boolean(default=False)
    # show_approve_option = fields.Boolean(compute="_show_forward_option")

    transfer_allowance = fields.Selection([("yes", "Yes"),
        ("no", "No")
    ],string='Transfer Allowance Required / स्थानांतरण भत्ता आवश्यक', copy=False,tracking=True)
    # hide_dcom_cancel = fields.Boolean(default=False, compute="_onchange_cancel_button")
    # hide_ccom_cancel = fields.Boolean(default=False, compute="_onchange_cancel_button")
    check_valid_user = fields.Boolean(default=False, compute="_check_user")
    check_manager = fields.Boolean(default=False, compute="_oncheck_manager")
    check_user = fields.Boolean(default=False, compute="_oncheck_manager")

    @api.onchange('employee_id')	
    def _onchange_employee_id(self):
        for rec in self:   
            if rec.employee_id.id == self.env.user.id:
                rec.check_user = True

    @api.depends('state')	
    def _oncheck_manager(self):
        for record in self:            
            if record.employee_id.parent_id.user_id.id == self.env.user.id:
                record.check_manager = True     
                record.check_user = False      
            elif record.employee_id.user_id.id == self.env.user.id:
                record.check_user = True
                record.check_manager = False
            else:
                record.check_manager = False
                record.check_user = False
          

    # @api.depends('state')	
    # def _onchange_cancel_button(self):
    #     for record in self:            
    #         if self.env.user.has_group('bsscl_employee.deputy_com_id') and record.state == 'send_for_approval':
    #             record.hide_dcom_cancel = True
    #         else:
    #             record.hide_dcom_cancel = False
    #         if self.env.user.has_group('bsscl_employee.commissioner_id') and record.state == 'complete':
    #             record.hide_ccom_cancel = True
    #         else:
    #             record.hide_ccom_cancel = False
    #         if record.employee_id.user_id.id == self.env.user.id or record.employee_id.parent_id.user_id.id == self.env.user.id :
    #             record.check_valid_user = True
    #         else:
    #             record.check_valid_user = False

    @api.depends('employee_id')
    def _check_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.user.id or record.employee_id.parent_id.user_id.id == self.env.user.id or self.env.user.has_group('bsscl_employee.group_hr_ra'):
                record.check_valid_user = True
            else:
                record.check_valid_user = False
            # if self.env.user.has_group('bsscl_employee.deputy_com_id'):
            #     record.check_cc_user = True
            # else:
            #     record.check_cc_user = False
            # if self.env.user.has_group('bsscl_employee.commissioner_id'):
            #     record.check_cmd_user = True
            # else:
            #     record.check_cmd_user = False

    # @api.depends('employee_id')
    # def _show_forward_option(self):
    #     for record in self:
    #         if self.env.user.has_group('bsscl_employee.commissioner_id') and record.state == 'send_for_approval':
    #             record.show_approve_option = True
    #         else:
    #             record.show_approve_option = False


    @api.constrains('exit_reason')
    @api.onchange('exit_reason')	
    def _onchange_exit_reason(self):
        for rec in self:            
            if rec.exit_reason and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.exit_reason)):
                raise ValidationError("Exit Reason should be in alphabets / बाहर निकलने का कारण अक्षरों में होना चाहिए")
          
    @api.constrains('commandant_remark')
    @api.onchange('commandant_remark')	
    def _onchange_commandant_remark(self):
        for rec in self:            
            if rec.commandant_remark and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.commandant_remark)):
                raise ValidationError("Manager Remark should be in alphabets / प्रबंधक टिप्पणी अक्षरों में होना चाहिए")
    
    @api.constrains('exit_date')
    @api.onchange('exit_date')	
    def _onchange_exit_date(self):
        today = date.today()
        for rec in self:            
            if rec.exit_date and rec.exit_date < today:
                raise ValidationError("Exit Date must be today or greater than today / निकास तिथि आज या आज से अधिक होनी चाहिए")
            
    # @api.constrains('exit_type')
    # @api.onchange('exit_type')	
    # def _onchange_exit_type(self):
    #     for rec in self:            
    #         if rec.employee_id and rec.exit_type:
    #             record = self.env['exit.transfer.management'].sudo().search([('employee_id', '=', rec.employee_id.id),('state','=','complete')]).mapped('exit_type')
    #             if 'Resigned' in record:                           
    #                 raise ValidationError("Employee has already Resigned / कर्मचारी पहले ही इस्तीफा दे चुका है")

    @api.model
    def create(self, vals):
        res = super(ExitTransferManagement, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('exit.transfer.management')
        sequence = 'Exit Management - ' + str(seq)
        res.name = sequence
        return res


    def button_cancel(self):
        self.update({"state":"cancel"})

    def button_verify(self):
        # for rec in self:            
        #     if rec.employee_id and rec.exit_type:
        #         record = self.env['exit.transfer.management'].sudo().search([('employee_id', '=', rec.employee_id.id),('state','=','complete')]).mapped('exit_type')
        #         if 'Resigned' in record:                           
        #             raise ValidationError("Employee has already Resigned / कर्मचारी पहले ही इस्तीफा दे चुका है")
        self.update({"state":"send_for_approval"})
        

    def button_complete(self):
        for rec in self:
            # if rec.employee_id and rec.exit_type:
            #     record = self.env['exit.transfer.management'].sudo().search([('employee_id', '=', rec.employee_id.id),('state','=','complete')]).mapped('exit_type')
            #     if 'Resigned' in record:                           
            #         raise ValidationError("Employee has already Resigned / कर्मचारी पहले ही इस्तीफा दे चुका है")
            if rec.commandant_remark:
                action_taken = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
                rec.update({'state':'complete',
                            'cmd_action_taken_by':action_taken.id,
                            'cmd_action_taken_on':datetime.now()})
            else:
                raise ValidationError("Please fill Manager Remark  / कृपया प्रबंधक टिप्पणी भरें")
            
    def button_complete1(self):
        action_taken = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        for rec in self:
            rec.update({'state':'complete',
                        'commandant_remark':'Updated by HR',
                        'cmd_action_taken_by':action_taken.id,
                        'cmd_action_taken_on':datetime.now()})



    @api.constrains('attachment_ids')
    def check_uploaded_document(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        for record in self:
            for rec in record.attachment_ids:
                if rec.datas:
                    acp_size = ((len(rec.datas) *3/4) /1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(rec.datas), default='application/pdf')        
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only .jpeg, .jpg, .png, .pdf, .doc, .docx format are allowed. / केवल .jpeg, .jpg, .png, .pdf, .doc, .docx प्रारूप की अनुमति है। ")
                    if acp_size > 2:
                        raise ValidationError("Maximum file size is 2 MB / अधिकतम फ़ाइल आकार 2 एमबी है")
                    