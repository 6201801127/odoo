# -*- coding: utf-8 -*-
#########################
    #Modification History :   
    # 14-Sep-2020 : provision for le reason option update, By : T Ketaki Debadarshini
   
#########################
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.kw_hr_leaves.models.kw_leave_approval_log import STS_APPROVE,STS_REJECT,STS_CANCEL,STS_FORWARD

from datetime import datetime , date, timedelta

class LeaveAprrovalWizard(models.TransientModel):
    _name        = 'kw_leave_approval_wizard'
    _description = 'Leave Approval Wizard'


    @api.model
    def default_get(self, fields):
        res             = super(LeaveAprrovalWizard, self).default_get(fields)       
        active_id       = self.env.context.get('active_id', False)
        
        res.update({'leave_allocation_request_id': active_id, })   
        if active_id:     
            allocation_request = self.env['hr.leave.allocation'].browse(active_id)
            res.update({'number_of_days': allocation_request.number_of_days,'attendance_id': allocation_request.attendance_id.id if allocation_request.attendance_id else False,'comp_off_allocation': allocation_request.comp_off_allocation })  
            

        return res
    
    @api.model
    def _get_forward_employees(self):
        allocation_id = self._context.get('active_id',False)
        employee            = self.env.user.employee_ids
        domain              = [('user_id','!=',False)]
        if allocation_id:
            allocation_request = self.env['hr.leave.allocation'].browse(allocation_id)
            if allocation_request and allocation_request.employee_id:
                employee += allocation_request.employee_id
                domain.append(('id', 'not in', employee.ids))
        return domain
    
    # leave_request_id        = fields.Many2one('kw_daily_employee_attendance',string="Employee")
    

    leave_allocation_request_id  = fields.Many2one('hr.leave.allocation',string="Allocation Request")
    employee_id                  = fields.Many2one('hr.employee',string="Employee",related="leave_allocation_request_id.employee_id")
    holiday_status_id            = fields.Many2one('hr.leave.type',string="Leave Type",related="leave_allocation_request_id.holiday_status_id")

    number_of_days               = fields.Float('Number of Days')
    allocation_reason            = fields.Text(string="Reason",related="leave_allocation_request_id.notes")
    """comp offf related fields"""
    comp_off_allocation          = fields.Selection(string="Request For",selection=[('1', 'Full Day'),('0.5', 'Half Day')] )
    attendance_id                = fields.Many2one('kw_daily_employee_attendance',string="Attendance Date")
    attendance_date              = fields.Date('Attendance Date', related="attendance_id.attendance_recorded_date")
    check_in_time                = fields.Char('Office In', related="attendance_id.check_in_time")
    check_out_time               = fields.Char('Office Out', related="attendance_id.check_out_time")
    worked_hours                 = fields.Float(related='attendance_id.worked_hours')

    
    authority_remark        = fields.Text(string='Authority Remark')
    forward_request         = fields.Boolean(string='Forward Request',)
    forwarded_to            = fields.Many2one('hr.employee',string='Forward To',domain=_get_forward_employees)

    action_type             = fields.Char('Action Type',)
    project_name            = fields.Char('Project Name/Activity',related='leave_allocation_request_id.project_name')

    @api.onchange('comp_off_allocation')
    def _onchange_comp_off_allocation(self):
        if self.holiday_status_id.is_comp_off == True and self.comp_off_allocation:
            self.number_of_days = float(self.comp_off_allocation)

    @api.constrains('comp_off_allocation','number_of_days')
    def validate_comp_off_days(self):
        for record in self:
            if record.holiday_status_id.leave_code  == True and not (record.comp_off_allocation or record.number_of_days):
                raise ValidationError("Please select comp off request days.")
   
    @api.constrains('authority_remark')
    def validate_reason(self):
        for record in self:
            if record.authority_remark and re.match("^[a-zA-Z0-9/\s\+-.()]+$", record.authority_remark) == None:
                raise ValidationError("Please remove special characters from remark")  

    
    @api.multi
    def allocation_request_approve(self):
        self.action_type = 'approve'
        return self.allocation_request_take_action() 

    
    @api.multi
    def allocation_request_reject(self):
        self.action_type = 'reject'
        return self.allocation_request_take_action()     

    
    @api.multi
    def allocation_request_forward(self):
        self.action_type = 'forward'
        return self.allocation_request_take_action() 

    @api.multi
    def allocation_request_cancel(self):        
        return self.allocation_request_take_action() 


    @api.multi
    def allocation_request_take_action(self):
        """method to update late entry reason"""
        self.ensure_one()
        context         = dict(self._context or {})
       
        # print(self.action_type)
        # active_ids      = context.get('active_ids', [])
        
        # print(ddfg) ,,STS_CANCEL,
        # pending_at  = False
        state           = False
        forwarded_to    = False
        if self.action_type == 'approve':
            state       = STS_APPROVE
            
            self.leave_allocation_request_id.action_approve()

            update_data_vals        = {'authority_remark':self.authority_remark,'comp_off_allocation':self.comp_off_allocation,'number_of_days':float(self.comp_off_allocation) if self.comp_off_allocation else 0}
            # if self.holiday_status_id.is_comp_off :
            #     validity_days       = self.holiday_status_id.validity_days if self.holiday_status_id.validity_days and self.holiday_status_id.validity_days > 0 else 180
                
            #     update_data_vals.update({'validity_start_date':date.today(),'validity_end_date':date.today() + timedelta(days=validity_days)})

            self.leave_allocation_request_id.sudo().write(update_data_vals)

            """send mail to Employee"""
            template    = self.env.ref('kw_hr_leave_attendance_integration.kw_comp_off_approval_mail')   
            template.send_mail(self.leave_allocation_request_id.id , notif_layout="kwantify_theme.csm_mail_notification_light")
            
        elif self.action_type == 'reject':
            state       = STS_REJECT
            self.leave_allocation_request_id.action_refuse()
            self.leave_allocation_request_id.sudo().write({'authority_remark':self.authority_remark})

            """send mail to Employee"""
            template    = self.env.ref('kw_hr_leave_attendance_integration.kw_comp_off_reject_mail')   
            template.send_mail(self.leave_allocation_request_id.id , notif_layout="kwantify_theme.csm_mail_notification_light")

        elif self.action_type == 'forward':
            taken_by = self.leave_allocation_request_id.second_approver_id
            state        = STS_FORWARD
            forwarded_to = self.forwarded_to
            self.leave_allocation_request_id.action_forward(self.authority_remark,forwarded_to)

            """send mail to Employee"""
            template    = self.env.ref('kw_hr_leave_attendance_integration.kw_comp_off_forwarrd_mail')   
            template.with_context(taken_by=taken_by.name if taken_by else self.env.user.name).send_mail(self.leave_allocation_request_id.id , notif_layout="kwantify_theme.csm_mail_notification_light")
        
        elif self.action_type == 'cancel':  
            """action cancel """         
            self.leave_allocation_request_id.sudo().write({'authority_remark':self.authority_remark})

            self.leave_allocation_request_id.sudo().write({
                'state': 'cancel',
                'first_approver_id': False,
                'second_approver_id': False,
            })

            linked_requests = self.leave_allocation_request_id.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            linked_requests.unlink()
            self.leave_allocation_request_id.activity_update()


        if self.action_type != 'cancel':
            self.env['kw_leave_approval_log'].create_approval_log(self.leave_allocation_request_id,False,False,forwarded_to,self.authority_remark,self.env.user.employee_ids.id,state)
        
        return {'type': 'ir.actions.act_window_close'}
    
   

    