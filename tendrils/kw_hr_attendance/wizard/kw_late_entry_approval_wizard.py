# -*- coding: utf-8 -*-
#########################
# Modification History :
# 20-Aug-2020 : provision for le reason option update, By : T Ketaki Debadarshini

#########################
import re
import base64
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.kw_utility_tools import kw_helpers

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_EARLY_ENTRY, IN_STATUS_ON_TIME, \
    IN_STATUS_LE, IN_STATUS_EXTRA_LE, LATE_WPC, LATE_WOPC


class LateEntryAprrovalWizard(models.TransientModel):
    _name = 'kw_late_entry_approval_wizard'
    _description = 'Late Entry Approval Wizard'

    @api.model
    def default_get(self, fields):
        res = super(LateEntryAprrovalWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        # print(self.env.context)
        if len(active_ids) == 1:
            res.update({
                'daily_attendance_id': active_ids[0] if active_ids else False,
                'daily_attendance_ids': [],
            })
        else:
            res.update({
                'daily_attendance_id': False,
                'daily_attendance_ids': active_ids,
            })

        return res

    @api.model
    def _get_employee(self):
        daily_attendance_id = self._context.get('active_id', False)
        employee = self.env.user.employee_ids
        domain = [('user_id', '!=', False)]
        if daily_attendance_id:
            attendance_id = self.env['kw_daily_employee_attendance'].browse(daily_attendance_id)
            if attendance_id and attendance_id.employee_id:
                employee += attendance_id.employee_id
                domain.append(('id', 'not in', employee.ids))
        return domain

    daily_attendance_id = fields.Many2one('kw_daily_employee_attendance', string="Employee", readonly=True)
    attendance_recorded_date = fields.Date(string="Date", related="daily_attendance_id.attendance_recorded_date")
    shift_in_time = fields.Char(string="Office Time", related="daily_attendance_id.shift_in")
    check_in = fields.Char(string="Office In", related="daily_attendance_id.check_in_time")
    check_out = fields.Char(string="Office Out", related="daily_attendance_id.check_out_time")

    # in_time                 = fields.Char(string="In Time",compute="_compute_last_late_entries") #
    late_entry_reason = fields.Text(string="Late Entry Reason", related="daily_attendance_id.late_entry_reason")

    daily_attendance_ids = fields.Many2many('kw_daily_employee_attendance', string="Attendance Ids")

    # le_action               = fields.Selection(string="Late Entry Action Status" ,selection=[('3','Forward'),('1', 'LateWPC'), ('2', 'LateWOPC'),],required=True)
    remark = fields.Text(string='Authority Remark')
    forward_to = fields.Many2one('hr.employee', string="Forwarded To", ondelete='cascade', domain=_get_employee)

    forward_late_entry = fields.Boolean(string="Forward Late Entry")

    last_le_ids = fields.Many2many('kw_daily_employee_attendance',
                                   string='Last 7 late entry details', compute="_compute_last_late_entries")
    action_type = fields.Char(string="Action Type")
    le_reason = fields.Text(string="Enter Late Entry Reason")

    @api.depends('daily_attendance_id')
    def _compute_last_late_entries(self):
        for rec in self:
            if rec.daily_attendance_id:
                rec.last_le_ids = self.env['kw_daily_employee_attendance'].search(
                    [('employee_id', '=', rec.daily_attendance_id.employee_id.id),
                     ('attendance_recorded_date', '<', rec.daily_attendance_id.attendance_recorded_date),
                     ('check_in_status', 'in', [IN_STATUS_LE, IN_STATUS_EXTRA_LE])], limit=7).ids

    @api.constrains('le_reason')
    def validate_reason(self):
        for record in self:
            if record.le_reason and re.match("^[a-zA-Z0-9/\s\+-.()]+$", record.le_reason) == None:
                raise ValidationError("Please remove special characters from late entry reason")

    # #late entry without paycut

    @api.multi
    def late_entry_wdout_paycut(self):
        return self.late_entry_take_action('LateWOPC')

    # #late entry with paycut

    @api.multi
    def late_entry_wd_paycut(self):
        return self.late_entry_take_action('LateWPC')

        # #late entry forward

    @api.multi
    def late_entry_forward(self):
        return self.late_entry_take_action('forward')

    @api.multi
    def late_entry_update_reason(self):
        """method to update late entry reason"""
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        attendance_ids = self.env['kw_daily_employee_attendance'].browse(active_ids)

        if attendance_ids:
            attendance_ids.write({'late_entry_reason': self.le_reason, 'le_state': '1'})

            # Call mail template when late entry state is 'Applied'
            for attendance_rec in attendance_ids:
                if attendance_rec.le_state == '1':
                    template = self.env.ref('kw_hr_attendance.kw_late_entry_apply_email_template')
                    encrypted_attendance_id = kw_helpers.encrypt_msg(str(attendance_rec.id))
                    encoded_attendance_id = base64.b64encode(encrypted_attendance_id).decode('utf8')

                    self.env['mail.template'].browse(template.id).with_context(
                        attendance_id=encoded_attendance_id).send_mail(attendance_rec.id,
                                                                       notif_layout="kwantify_theme.csm_mail_notification_light")

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def late_entry_take_action(self, action_type):
        """method to take actions like forward,approve,reject"""
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        attendance_ids = self.env['kw_daily_employee_attendance'].browse(active_ids)
        attendance_late_date_rec=attendance_ids.mapped('attendance_recorded_date')
        current_date = date.today()
        # #authenticate /validate the action user
        # print(self.authority_status)
        all_authorities = attendance_ids.mapped('le_forward_to')

        if all_authorities:
            # distinct_authorities = set(all_authorities)

            if all_authorities not in self.env.user.employee_ids or (
            attendance_ids.filtered(lambda rec: rec.le_state not in ['1', '3'])) or (
            attendance_ids.filtered(lambda rec: rec.check_in_status not in [IN_STATUS_LE, IN_STATUS_EXTRA_LE])):
                raise ValidationError("You are not authorized to take action for the selected request !")
        else:
            raise ValidationError("You are not authorized to take action for the selected request !")

        le_state = LATE_WPC

        if action_type == 'LateWOPC':
            le_state = LATE_WOPC
        elif action_type == 'forward':
            le_state = '3'

        # create approval log and  update the attendance model  'forward'
        temp_date_from = current_date.replace(day=26)
        date_from = temp_date_from - relativedelta(months=1)
        non_approval_entries = list(filter(lambda date: date < date_from,attendance_late_date_rec))
     
        if non_approval_entries:
            raise ValidationError("You Can't Take Action Against Previous Month Late Entry Records.Kindly Approve Records For Current Month Only")
        
        log_records = []
        for attendance_id in active_ids:
            log_records.append({'daily_attendance_id': attendance_id,
                                'forward_to': self.forward_to.id if self.forward_late_entry else False,
                                'authority_remark': self.remark, 'action_taken_by': self.env.user.employee_ids.id,
                                'state': le_state})
        # print(log_records)
        if log_records:
            self.env['kw_late_entry_approval_log'].create(log_records)

        update_res = {'le_authority_remark': self.remark,
                      'le_action_taken_by': self.env.user.employee_ids.id,
                      'le_state': '3' if self.forward_late_entry else '2',
                    #   'le_action_status': LATE_WPC if self.forward_late_entry else le_state,
                      'le_action_status': LATE_WOPC if le_state == LATE_WOPC else LATE_WPC,
                      'le_action_taken_on': datetime.now()}

        if action_type == 'forward':
            del update_res['le_action_status']
            update_res.update(
                {'le_forward_to': self.forward_to.id,
                 'le_forward_reason': self.remark,
                 'le_authority_remark': ''})

        attendance_ids.write(update_res)

        # Edited By: Surya Prasad Tripathy
        for record in attendance_ids:
            # Call mail template when late entry state is 'Granted'
            if record.le_state == '2':
                template = self.env.ref('kw_hr_attendance.kw_late_entry_approve_email_template')
                self.env['mail.template'].browse(template.id).send_mail(record.id,
                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")

            # Call mail template when late entry state is 'Forwarded'
            if record.le_state == '3':
                template = self.env.ref('kw_hr_attendance.kw_late_entry_forwaded_email_template')
                self.env['mail.template'].browse(template.id).send_mail(record.id,
                                                                        notif_layout="kwantify_theme.csm_mail_notification_light")

        # Log the payment in the chatter
        # for attendance_rec in attendance_ids:
        #     attendance_rec.message_post(body=body)       

        return {'type': 'ir.actions.act_window_close'}
