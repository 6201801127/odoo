# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.kw_hr_leaves.models.kw_leave_approval_log import STS_APPROVE,STS_REJECT,STS_CANCEL,STS_FORWARD,STS_HOLD
import base64

class LeaveTakeActionWizard(models.TransientModel):
    _name        = 'kw_leave_take_action_wizard'
    _description = 'Leave Take Action Wizard'


    @api.model
    def default_get(self, fields):
        res             = super(LeaveTakeActionWizard, self).default_get(fields)       
        active_id       = self.env.context.get('active_id', False)
        
        res.update({'leave_request_id': active_id, })   
        if active_id:
            leave_request = self.env['hr.leave'].browse(active_id)
            res.update({'number_of_days': leave_request.number_of_days ,'request_date_from': leave_request.request_date_from, 
            'request_date_from_period': leave_request.request_date_from_period ,'request_date_to': leave_request.request_date_to, 
            'request_date_to_period': leave_request.request_date_to_period, 'request_unit_half': leave_request.request_unit_half,
            'request_unit_half_to_period': leave_request.request_unit_half_to_period,'medical_doc': leave_request.medical_doc})  
        return res
    
    @api.model
    def _get_forward_employees(self):
        employee                 = self.env.user.employee_ids
        domain                   = [('user_id','!=',False)]
        domain.append(('id', 'not in', employee.ids))
        return domain
    


    leave_request_id             = fields.Many2one('hr.leave',string="Leave Request")
    employee_id                  = fields.Many2one('hr.employee',string="Employee",related="leave_request_id.employee_id")
    holiday_status_id            = fields.Many2one('hr.leave.type',string="Leave Type",related="leave_request_id.holiday_status_id")

    leave_code                  = fields.Char('Leave Code',related="holiday_status_id.leave_code")

    medical_doc                 = fields.Binary(string='Document',attachment=True)

    state                       = fields.Selection(string="Leave Status",related="leave_request_id.state")

    number_of_days               = fields.Float('Number of Days')
    request_date_from            = fields.Date(string="From")
    request_date_from_period     = fields.Selection([('am', '  First Half'),('pm', '  Second Half')],string="Half day")
    request_date_to              = fields.Date(string="To")
    request_date_to_period       = fields.Selection([('am', '  First Half'),('pm', '  Second Half')],string="Half day")
    request_unit_half            = fields.Boolean(string="Half day")
    request_unit_half_to_period  = fields.Boolean(string="Half day")
    
    leave_reason                 = fields.Text(string="Reason",related="leave_request_id.name")
    authority_remark             = fields.Text(string='Authority Remark')
    forward_request              = fields.Boolean(string='Forward Request',)
    forwarded_to                 = fields.Many2one('hr.employee',string='Forward To',domain=_get_forward_employees)
    action_type                  = fields.Char('Action Type',)

   
   
    @api.constrains('authority_remark')
    def validate_reason(self):
        for record in self:
            if record.authority_remark and re.match("^[a-zA-Z0-9/\s\+-.()]+$", record.authority_remark) == None:
                raise ValidationError("Please remove special characters from remark")  

    
    @api.multi
    def leave_request_approve(self):
        self.action_type = 'approve'
        return self.leave_request_take_action() 

    
    @api.multi
    def leave_request_reject(self):
        self.action_type = 'reject'
        return self.leave_request_take_action() 
            
    @api.multi
    def leave_request_hold(self):
        self.action_type = 'hold'
        return self.leave_request_take_action()     

    
    @api.multi
    def leave_request_forward(self):
        self.action_type = 'forward'
        return self.leave_request_take_action() 


    @api.multi
    def leave_request_take_action(self):
        """method to update late entry reason"""
        self.ensure_one()
        # context         = dict(self._context or {})
       
        # print(self.action_type)
        # active_ids      = context.get('active_ids', [])
        
        # print(ddfg) ,,STS_CANCEL,
        # pending_at  = False
        state       = False
        forwarded_to    = False
        if self.action_type == 'approve':
            state       = STS_APPROVE
            
            self.leave_request_id.write({'authority_remark':self.authority_remark})
            self.leave_request_id.action_approve()
        elif self.action_type == 'reject':
            state       = STS_REJECT
            self.leave_request_id.write({'authority_remark':self.authority_remark})
            self.leave_request_id.action_refuse()
            
        elif self.action_type == 'forward':
            state        = STS_FORWARD
            forwarded_to = self.forwarded_to
            self.leave_request_id.action_forward(self.authority_remark,forwarded_to)

        elif self.action_type == 'hold':        
            state       = STS_HOLD
            self.leave_request_id.write({'authority_remark':self.authority_remark})
            self.leave_request_id.hold_leave()
            
        # elif self.action_type == 'cancel':  
        #     """action cancel """         
        #     self.leave_request_id.write({'authority_remark':self.authority_remark})

        #     self.leave_request_id.write({
        #         'state': 'cancel',
        #         'first_approver_id': False,
        #         'second_approver_id': False,
        #     })

        #     linked_requests = holiday.mapped('linked_request_ids')
        #     for linked_request in linked_requests:
        #         linked_request.action_draft()
        #     linked_requests.unlink()
        #     self.activity_update()
        if self.action_type != 'cancel':
            self.env['kw_leave_approval_log'].create_approval_log(False,self.leave_request_id,False,
            forwarded_to,self.authority_remark,self.env.user.employee_ids.id,state)

        return {'type': 'ir.actions.act_window_close'}





    # # @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
    # #               'request_date_from', 'request_date_to','request_date_to_period','request_unit_half_to_period',
    # #               'employee_id')

    # @api.onchange('from_half_day','from_day', 'to_day','to_half_day','request_unit_half_to_period')
    # def _onchange_request_parameters(self):
    #     if not self.request_date_from:
    #         self.date_from = False
    #         return

    #     # if self.request_unit_half or self.request_unit_hours:
    #     #     self.request_date_to = self.request_date_from

    #     if not self.request_date_to:
    #         self.date_to = False
    #         return

    #     domain = [('calendar_id', '=', self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
    #     attendances = self.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

    #     # find first attendance coming after first_day
    #     attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()), attendances[0])
    #     # find last attendance coming before last_day
    #     attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()), attendances[-1])

    #     if self.request_unit_half:
    #         if self.request_date_from_period == 'am':
    #             hour_from = float_to_time(attendance_from.hour_from)
    #             hour_to = float_to_time(attendance_from.hour_to)
    #         else:
    #             hour_from = float_to_time(attendance_to.hour_from)
    #             hour_to = float_to_time(attendance_to.hour_to)
    #     elif self.request_unit_hours:
    #         # This hack is related to the definition of the field, basically we convert
    #         # the negative integer into .5 floats
    #         hour_from = float_to_time(abs(self.request_hour_from) - 0.5 if self.request_hour_from < 0 else self.request_hour_from)
    #         hour_to = float_to_time(abs(self.request_hour_to) - 0.5 if self.request_hour_to < 0 else self.request_hour_to)
    #     elif self.request_unit_custom:
    #         hour_from = self.date_from.time()
    #         hour_to = self.date_to.time()
    #     else:
    #         hour_from = float_to_time(attendance_from.hour_from)
    #         hour_to = float_to_time(attendance_to.hour_to)

    #     tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
    #     self.date_from = timezone(tz).localize(datetime.combine(self.request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
    #     self.date_to = timezone(tz).localize(datetime.combine(self.request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)
    #     self._onchange_leave_dates()

    
   

    