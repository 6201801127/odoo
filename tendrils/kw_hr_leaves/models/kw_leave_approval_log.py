# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api

STS_APPROVE,STS_REJECT,STS_CANCEL,STS_FORWARD,STS_HOLD,STS_PENDING = '1','2','3','4','5','6'

class LeaveApprovalLog(models.Model):
    _name           = "kw_leave_approval_log"
    _description    = "Leave Approval Log"
    _rec_name       = 'action_taken_by'

    # approval_for        = fields.Selection(string="Approval For" ,selection=[('1', 'Leave Request'),('2', 'Leave Allocation Request')]) 
    allocation_id       = fields.Many2one('hr.leave.allocation',string="Leave Allocation Id")
    leave_id            = fields.Many2one('hr.leave',string="Leave Id")
    cancel_leave_id     = fields.Many2one('kw_cancel_leave',string="Cancel Leave Id")
    
    pending_at          = fields.Many2one('hr.employee', string="Pending At")  

    authority_remark    = fields.Text(string='Remark')
    action_taken_by     = fields.Many2one('hr.employee', string="Action Taken By",ondelete='cascade')  
    state               = fields.Selection(string="Action Status" ,selection=[(STS_PENDING,'Pending'),(STS_FORWARD,'Forwarded'),(STS_APPROVE, 'Approved'),(STS_REJECT, 'Rejected'),(STS_CANCEL, 'Cancelled'),(STS_HOLD, 'On Hold')]) 


    def create_approval_log(self,allocation_id,leave_id,cancel_leave_id,pending_at,authority_remark,action_taken_by,state):

        self.create({
            'allocation_id':allocation_id.id if allocation_id else False,
            'leave_id':leave_id.id if leave_id else False,
            'cancel_leave_id':cancel_leave_id.id if cancel_leave_id else False,
            'pending_at':pending_at.id if pending_at else False,
            'authority_remark':authority_remark,
            'action_taken_by':action_taken_by,
            'state':state
        })

