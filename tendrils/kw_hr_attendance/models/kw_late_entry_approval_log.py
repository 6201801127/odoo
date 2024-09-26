# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE


class LateEntryApprovalLog(models.Model):
    _name = "kw_late_entry_approval_log"
    _description = "Late Entry Approval Log"
    _rec_name = 'action_taken_by'

    daily_attendance_id = fields.Many2one('kw_daily_employee_attendance', string="Daily Attendance Id",
                                          ondelete='cascade', required=True)
    forward_to = fields.Many2one('hr.employee', string="Forwarded To", ondelete='cascade')

    authority_remark = fields.Text(string='Remark')
    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By", ondelete='cascade')
    state = fields.Selection(string="Action Status",
                             selection=[('3', 'Forward'), ('1', 'LateWPC'), ('2', 'LateWOPC')])  # #LateWOPC  LateWPC


# #class to take action for the late entry request, Created By : T Ketaki Debadarshini, On : 10-Aug-2020
class LateEntryAction(models.Model):
    _name = "kw_late_entry_take_action"
    _description = "Attendance Late Entry Take Action"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'id desc'

    daily_attendance_id = fields.Many2one('kw_daily_employee_attendance', string="Attendance Id")
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    le_forward_to = fields.Many2one(string='Late Entry Forwarded To', comodel_name='hr.employee', )

    attendance_recorded_date = fields.Date(string='Attendance Date', )

    shift_in = fields.Char(string="Shift In Time", related="daily_attendance_id.shift_in")
    check_in_time = fields.Char(string="Check In", related="daily_attendance_id.check_in_time")
    check_out_time = fields.Char(string="Check Out", related="daily_attendance_id.check_out_time")
    late_entry_reason = fields.Text(string='Late Entry Reason', related="daily_attendance_id.late_entry_reason", )
    le_state = fields.Selection(string="Late Entry Status", related="daily_attendance_id.le_state", )
    le_action_status = fields.Selection(string="Late Entry Action Status",
                                        related="daily_attendance_id.le_action_status")
    le_approval_log_ids = fields.One2many(string='Approval Logs', related="daily_attendance_id.le_approval_log_ids")

    @api.model_cr
    def init(self):
        # IN_STATUS_LE=2, IN_STATUS_EXTRA_LE=3
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            
            SELECT id,id as daily_attendance_id,employee_id,attendance_recorded_date,le_forward_to, le_state          
            FROM kw_daily_employee_attendance 
            WHERE check_in_status IN ('{IN_STATUS_LE}','{IN_STATUS_EXTRA_LE}') 
            AND le_state IN ('1','3')

            )"""
        # print("Late entry query",query)
        self.env.cr.execute(query)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # ids = []
        # if self.env.user.has_group('kw_eos.group_kw_eos_manager'):
        #     print("EOS MANAGER")
        #     query = "select id from kw_late_entry_take_action"
        #     self._cr.execute(query)
        #     ids = self._cr.fetchall()
        #     args += [('id', 'in', ids)]

        # else:
        query = f"select a.id from kw_late_entry_take_action a join hr_employee as b on a.le_forward_to = b.id where b.user_id =  {self.env.user.id}"
        self._cr.execute(query)
        ids = self._cr.fetchall()
        args += [('id', 'in', ids)]

        return super(LateEntryAction, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                    access_rights_uid=access_rights_uid)


class LateEntryRAChangeAction(models.TransientModel):
    _name = "kw_late_entry_ra_change_action"
    _description = "Attendance Late Entry RA Change Action"

    employee_id = fields.Many2one('hr.employee',string='Employee')
    updated_ra = fields.Many2one('hr.employee',string='New RA')
    update_from_date = fields.Date(string='From Date')

    
    def update_le_pending_at(self):
        le_data = self.env['kw_daily_employee_attendance'].sudo().search([('check_in_status','in',['2','3']),('employee_id','=',self.employee_id.id),('attendance_recorded_date','>=',self.update_from_date)])
        if le_data:
            for rec in le_data:
                rec.sudo().write({
                    'le_forward_to':self.updated_ra.id,
                })
                