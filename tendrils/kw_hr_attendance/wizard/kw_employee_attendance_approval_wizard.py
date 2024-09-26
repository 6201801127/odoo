# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmpAttendanceAprrovalWizard(models.TransientModel):
    _name        = 'kw_employee_attendance_approval_wizard'
    _description = 'Employee Attendance Approval Wizard'

    @api.model
    def default_get(self, fields):
        res             = super(EmpAttendanceAprrovalWizard, self).default_get(fields)
        active_ids      = self.env.context.get('active_ids', [])
        # print(active_ids)
        
        res.update({
                'attendance_request_ids': active_ids,
            })
        return res

    remark                  = fields.Text(string='Authority Remark',required=True)
    action_type             = fields.Char(string="Action Type")
    
    attendance_request_ids  = fields.Many2many(
        string='Application Request',
        comodel_name='kw_employee_apply_attendance',
        relation='kw_employee_attendance_approval_wizard_rel',
        column1='request_id',
        column2='approval_id',
    )    
    
    # #late entry without paycut
    @api.multi
    def approve_attendance_request(self):
        return self.save_action_details('approve') 

    # #late entry with paycut
    @api.multi
    def reject_attendance_request(self):        
        return self.save_action_details('reject')   

    @api.multi
    def save_action_details(self,action_type):
        self.ensure_one()
        context         = dict(self._context or {})
        active_ids      = context.get('active_ids', [])
        # attendance_request_ids  = self.env['kw_daily_employee_attendance'].browse(active_ids)

        if self.action_type == 'cancel':
            state = '6'
        if self.action_type == 'reject' or action_type == 'reject':
            state = '5'
        elif self.action_type == 'approve' or action_type == 'approve':
            state = '3'  # '4' if self.env.user.has_group('hr_attendance.group_hr_attendance_manager') else '3'

        self.attendance_request_ids.write(
            {'authority_remark': self.remark,
             'action_taken_by': self.env.user.employee_ids.id,
             'state': state,
             'action_taken_on': datetime.now()})
        # print(self.attendance_request_ids,self.remark)
        for attendance_request_rec in self.attendance_request_ids:
            if (self.action_type == 'approve' or action_type == 'approve') and state == '3':
                attendance_request_rec.create_daily_attendance()
                # mail template for attendance request approved
                template = self.env.ref('kw_hr_attendance.kw_attendance_request_approved_email_template')
                self.env['mail.template'].browse(template.id).send_mail(attendance_request_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            if (self.action_type == 'reject' or action_type == 'reject') and state == '5':
                template = self.env.ref('kw_hr_attendance.kw_attendance_request_rejected_email_template')
                self.env['mail.template'].browse(template.id).send_mail(attendance_request_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        return {'type': 'ir.actions.act_window_close'}
