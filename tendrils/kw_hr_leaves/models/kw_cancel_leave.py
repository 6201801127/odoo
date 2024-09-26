# -*- coding: utf-8 -*-

from datetime import datetime,date, timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.kw_hr_leaves.models.kw_leave_approval_log import STS_PENDING,STS_APPROVE,STS_REJECT,STS_FORWARD

class CancelLeave(models.Model):

    _name           = 'kw_cancel_leave'
    _description    = "Leave Cancel After Approval"

    _rec_name       = 'approved_leave_id'
    
    @api.model
    def _get_domain(self):
        return [('state','=','validate'),('employee_id','=',self.env.user.employee_ids.id)]


    approved_leave_id            = fields.Many2one('hr.leave', string="Approved Leave", required=True ,  domain=_get_domain)
    name                         = fields.Char(string='Leave Type',related='approved_leave_id.holiday_status_id.name')
    description                  = fields.Text('Reason of Cancellation',size=500,required=True) 
    comment                      = fields.Text(string='Comments By Manager' ,size=500) 

    check_parent                 = fields.Boolean(string="Check Parent", compute='_compute_parent')
    status                       = fields.Selection([('apply', 'Applied'),('forward', 'Forwarded'),('approve', 'Approved'),('reject', 'Rejected')],string="Status" , default='apply')
    duration                     = fields.Float(string='Duration', related= 'approved_leave_id.number_of_days_display')
    from_day                     = fields.Date(string="From", related= 'approved_leave_id.request_date_from')
    from_half_day                = fields.Selection([('am', '  First Half'),('pm', '  Second Half')],string="Half day", related= 'approved_leave_id.request_date_from_period')
    to_day                       = fields.Date(string="To", related= 'approved_leave_id.request_date_to')
    to_half_day                  = fields.Selection([('am', '  First Half'),('pm', '  Second Half')],string="Half day", related= 'approved_leave_id.request_date_to_period')
    request_unit_half            = fields.Boolean(string="From Half day", related= 'approved_leave_id.request_unit_half')
    request_unit_half_to_period  = fields.Boolean(string="To Half day", related= 'approved_leave_id.request_unit_half_to_period')
    reason                       = fields.Text( related= 'approved_leave_id.name')
    approved_leave_emp_id        = fields.Many2one( related= 'approved_leave_id.employee_id')
    department                   = fields.Char(string="Department",related="approved_leave_id.employee_id.department_id.name")
    division                     = fields.Char(string="Division",related="approved_leave_id.employee_id.division.name")
    section                      = fields.Char(string="Section",related="approved_leave_id.employee_id.section.name")
    designation                  = fields.Char(string="Designation",related="approved_leave_id.employee_id.job_id.name")
    leave_approval_log_ids       = fields.One2many(string='Leave Approval Logs',comodel_name='kw_leave_approval_log',inverse_name='leave_id',related='approved_leave_id.approval_log_ids')   
    approval_log_ids             = fields.One2many(string='Cancellation Approval Logs',comodel_name='kw_leave_approval_log',inverse_name='cancel_leave_id')    
    action_taken_on              = fields.Date(string="Action Taken On")
    
    @api.model
    def _get_forward_employees(self):
        active_id    = self._context.get('active_id',False)
        active_model = self._context.get('active_model',False)
        if active_id and active_model == 'kw_cancel_leave':
            cancel_leave = self.env['kw_cancel_leave'].browse(active_id)
            employee = self.env.user.employee_ids
            domain   = [('user_id','!=',False)]
            if cancel_leave:
                leave_id = self.env['hr.leave'].browse(cancel_leave.approved_leave_id.id if cancel_leave.approved_leave_id else False)
                if leave_id and leave_id.employee_id:
                    employee += leave_id.employee_id
                    domain.append(('id', 'not in', employee.ids))
        else:
            domain = []
        return domain
    
    approver_id                 = fields.Many2one('hr.employee',string="Approver")
    forward_to                  = fields.Many2one('hr.employee',string="Forward To",domain=_get_forward_employees)
    remark                      = fields.Text(string="Remark")
    forward_request             = fields.Boolean(string='Forward Request')

    _sql_constraints = [
        ('leave_uniq', 'CHECK(1=1)',
         'The cancellation request for the selected leave already exists.'),
    ]


    @api.constrains('approved_leave_id')
    def validate_approved_leave_id(self):
        for record in self:
            cancel_leaves = self.env['kw_cancel_leave'].search([('approved_leave_id','=',record.approved_leave_id.id)]) - record
            cancel_leaves = cancel_leaves.filtered(lambda res:res.status in ['apply','forward','approve'])
            if cancel_leaves:
                raise ValidationError("The leave you choosed is already in apply or approve state.")

    # @api.multi
    # def _compute_parent(self):
    #     current_user= self.env.user
    #     for record in self:
    #         user= record.create_uid
    #         employee= self.env['hr.employee'].search([('user_id','=',user.id)],limit=1)
    #         ra = employee and employee.parent_id or False
    #         record.check_parent = True if ra and ra.user_id and ra.user_id.id == current_user.id else False

    @api.multi
    def _compute_parent(self):
        for record in self:
            eos_con = self._context.get('hr_eos_leave_cancel')
            if eos_con:
                record.check_parent = True
            elif record.approver_id and not eos_con:
                record.check_parent = True if record.approver_id.user_id and record.approver_id.user_id.id == self._uid else False
            else:
                record.check_parent = False

    @api.model
    def create(self, values):
        res         = super(CancelLeave, self).create(values)

        config_param            = self.env['ir.config_parameter'].sudo()
        escallate_on_leave      = config_param.get_param('kw_hr_leaves.on_leave')

        payroll_date, end_date, _ = self.env['kw_daily_employee_attendance'].sudo()._get_recompute_date_range_configs(end_date=datetime.today().date())
        # print(payroll_date,end_date)

        # if res.approved_leave_id.request_date_from < payroll_date:
        #     raise ValidationError(f"You are not allowed to cancel the leave after the payroll process.")

        ra_id                   = res.approved_leave_id.employee_id.parent_id #.id if res.approved_leave_id.employee_id.parent_id else False
        try:
            ##call the attendance leave approval update method        
            if ra_id and escallate_on_leave:
                daily_attendance = self.env['kw_daily_employee_attendance'].sudo()
                on_leave    = daily_attendance.search([('attendance_recorded_date', '=', datetime.now().date()),('employee_id', '=', ra_id.id),('leave_day_value', '>', 0)])
                #print(on_leave_tour)
                if on_leave:
                    parent_on_leave    = daily_attendance.search([('attendance_recorded_date', '=', datetime.now().date()),('employee_id', '=', ra_id.parent_id.id),('leave_day_value', '>', 0)])
                    ra_id              = ra_id.parent_id  if not parent_on_leave and ra_id.parent_id else ra_id
                   
        except Exception as e:
            #print(str(e))
            pass
        #print(ra_id)
        
        res.write({'approver_id':ra_id.id if ra_id else False})
        
        self.env['kw_leave_approval_log'].create_approval_log(False,False,res,res.approver_id,'Cancellation Request',self.env.user.employee_ids.id,STS_PENDING)

        template    = self.env.ref('kw_hr_leaves.kw_hr_leave_cancel_apply_mail')   
        template.send_mail(res.id , notif_layout="kwantify_theme.csm_mail_notification_light")
        return res

    @api.multi
    def create_cancel(self):
        return

    @api.multi
    def action_approve(self):
        self.write({
            'status' : 'approve',
            'comment' : self.remark,
            'action_taken_on' : date.today(),
        })
        
        self.remark = False
        self.approved_leave_id.state='cancel'
        self.approved_leave_id.first_approver_id=False
        self.approved_leave_id.second_approver_id=False   
        self.approved_leave_id.activity_update()

        # leave_rec       = self.approved_leave_id
        # print(leave_rec)
        # print(self.approved_leave_id.related_comp_aloc_ids)
        # # print(self.env['hr_leave_comp_off_allocation_rel'].sudo().search([('leave_id','=',leave_rec)]))
        # if leave_rec.holiday_status_id.is_comp_off and leave_rec.related_comp_aloc_ids:
        #     no_of_days  = leave_rec.number_of_days
        #     print(leave_rec.related_comp_aloc_ids)
        #     print(len(leave_rec.related_comp_aloc_ids))
            
        # #     #self.approved_leave_id.related_comp_aloc_ids.write({})  
        # # print(tuple(leave_rec.ids)) 
        # # print('(%s)'%tuple(leave_rec.ids)[0]) 
       
        # print(sdfsdfd)    

        try:
            ##call the attendance leave cancellation method
            self.env['kw_daily_employee_attendance'].attendance_leave_cancellation_update(self.approved_leave_id)

            #### Remove from resource calendar
            resource_calender = self.env['resource.calendar.leaves'].search(([('holiday_id','=',self.approved_leave_id.id)]))
            resource_calender.sudo().unlink()

            ## check if comp-off has been cancelled then update the comp off taken info and log
            # print("Related record inside cancel ",self.approved_leave_id.related_comp_aloc_ids)
            # allocated_total_quantity = self.approved_leave_id.number_of_days
            # print(allocated_total_quantity)
            # for allocations in self.approved_leave_id.related_comp_aloc_ids:
            #     leave_compoff = self.env['hr_leave_comp_off_allocation_rel'].sudo().search([('comp_off_allocation_id','=',allocations.id)])
            #     print(leave_compoff)           
            
        except Exception as e:
            # print(str(e))
            pass 

        self.env['kw_leave_approval_log'].create_approval_log(False,False,self,False,self.comment,self.approver_id.id,STS_APPROVE)

        template  = self.env.ref('kw_hr_leaves.kw_hr_leave_cancel_approve_mail')   
        template.send_mail(self.id , notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.multi
    def action_reject(self):
        self.write({
            'status' : 'reject',
            'comment' : self.remark,
            'action_taken_on' : date.today(),
        })

        self.remark = False
        self.env['kw_leave_approval_log'].create_approval_log(False,False,self,False,self.comment,self.approver_id.id,STS_REJECT)

        template  = self.env.ref('kw_hr_leaves.kw_hr_leave_cancel_reject_mail')   
        template.send_mail(self.id , notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.multi
    def action_forward(self):
        taken_by = self.approver_id
        self.write({
            'status':'forward',
            'approver_id':self.forward_to.id if self.forward_to else False,
            'forward_request':False,
            'comment':self.remark,
            'action_taken_on' : date.today(),
        })

        self.env['kw_leave_approval_log'].create_approval_log(False,False,self,self.approver_id,self.comment,taken_by.id,STS_FORWARD)
        
        self.remark = False
        self.forward_to = False

        template  = self.env.ref('kw_hr_leaves.kw_hr_leave_cancel_forward_mail')   
        template.with_context(taken_by=taken_by.name if taken_by else self.env.user.name).send_mail(self.id , notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.multi
    def leave_cancel_take_action(self):
        self.ensure_one()
        form_view_id = self.env.ref("kw_hr_leaves.kw_cancel_leave_approval_form").id
        return  {
            'name'      : 'Take Action',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'kw_cancel_leave',
            'view_mode' : 'form',
            'view_type' : 'form',
            'target'    : 'new',
            'res_id'    :  self.ids[0],
            'view_id'   : form_view_id,
            'context'   : {"btn_hide":0},
        }