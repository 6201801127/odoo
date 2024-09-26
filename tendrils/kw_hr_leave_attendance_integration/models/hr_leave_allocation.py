# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    
# Create By: T Ketaki Debadrashini, On -11th Sep 2020                          #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta


# COMP_OFF_LEAVE_TYPE_ALIAS = 'CMP'

class KwHRLeaveAllocationRequest(models.Model):
    _inherit = 'hr.leave.allocation'

    # comp_off_date   = fields.Boolean(string='Is Comp Off Applied',)

    attendance_id = fields.Many2one('kw_daily_employee_attendance', string="Attendance Date")
    attendance_date = fields.Date('Attendance Date', related="attendance_id.attendance_recorded_date")
    check_in_time = fields.Char('Office In', related="attendance_id.check_in_time")
    check_out_time = fields.Char('Office Out', related="attendance_id.check_out_time")
    worked_hours = fields.Float('Worked Hour (in hrs)', related='attendance_id.worked_hours')
    # check_out       = fields.Datetime('Office Out', related="attendance_id.check_out")

    comp_off_allocation = fields.Selection(string="Request For", selection=[('1', 'Full Day'), ('0.5', 'Half Day')])

    employee_name = fields.Char('Employee Name', related="employee_id.name")

    @api.constrains('comp_off_allocation')
    def validate_allocations(self):
        config_param = self.env['ir.config_parameter'].sudo()
        half_day = float(config_param.get_param('kw_hr_leaves.half_day'))
        full_day = float(config_param.get_param('kw_hr_leaves.full_day'))
        for record in self:
            if record.holiday_status_id.is_comp_off and record.comp_off_allocation and record.attendance_id:
                if record.comp_off_allocation == '1' and record.attendance_id.worked_hours < full_day:
                    raise ValidationError(f"Less than {full_day} hours can not apply for Full Day.")
                elif record.comp_off_allocation == '0.5' and record.attendance_id.worked_hours < half_day:
                    raise ValidationError(f"Less than {half_day} hours can not apply for Half Day.")

    @api.onchange('comp_off_allocation')
    def _onchange_comp_off_allocation(self):
        self.number_of_days = float(self.comp_off_allocation) if self.comp_off_allocation else 0

    @api.constrains('comp_off_allocation', 'holiday_status_id', 'number_of_days')
    def validate_comp_off_days(self):
        for record in self:
            if record.holiday_status_id.is_comp_off and not (record.comp_off_allocation or record.number_of_days):
                raise ValidationError("Please select comp off request days.")

    @api.multi
    def apply_comp_off(self):
        # print("off day entries")
        """validate the comp off apply form and create record for leave allocation request
        """
        # print(self.comp_off_allocation)
        if self.attendance_id and self.state == 'refuse':
            self.write({'state':'confirm'})
        if self.comp_off_allocation and self.holiday_status_id and self.attendance_id and self.number_of_days \
                and self.notes and self.holiday_type and self.employee_id:
            if self.employee_id.parent_id:
                self.second_approver_id = self.employee_id.parent_id.id

                """send mail to RA"""
                template = self.env.ref('kw_hr_leave_attendance_integration.kw_comp_off_apply_mail')
                template.send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                raise ValidationError("Please configure your reporting authority details and try again.")

        else:
            if not self.employee_id:
                raise ValidationError("Please select employee.")
            elif not (self.number_of_days or self.comp_off_allocation):
                raise ValidationError("Please select comp off request days.")
            elif not (self.notes):
                raise ValidationError("Please enter the reason")
            else:
                raise ValidationError("Please enter all the required fields and try again.")

        if self.employee_id:
            active_cycle = self.env['kw_leave_cycle_master'].search(
                [('branch_id', '=', self.employee_id.job_branch_id.id if self.employee_id.job_branch_id else False),
                 ('cycle_id', '!=', False), ('active', '=', True)], limit=1)

            if active_cycle:
                if self.holiday_status_id.is_comp_off and self.attendance_id:
                    attendance_date = self.attendance_id.attendance_recorded_date
                    validity_days = self.holiday_status_id.validity_days if self.holiday_status_id.validity_days > 0 else 180
                    validity_end_date = attendance_date + timedelta(days=validity_days)
                    self.write({'validity_start_date': attendance_date,
                                'validity_end_date': validity_end_date,
                                'leave_cycle_id': active_cycle.id,
                                'cycle_period': active_cycle.cycle_period})

    @api.multi
    def action_off_day_entry_refused_apply_window(self):
        
        # print("off day entries")
        self.ensure_one()
        # self.write({'state':'confirm'})
        holiday_status_id = self.env['hr.leave.type'].search([('is_comp_off', '=', True)])

        if holiday_status_id:
            view_id = self.env.ref('kw_hr_leave_attendance_integration.view_off_day_entries_apply_form').id

            return {
                'name': 'Apply Comp Off',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.leave.allocation',
                'res_id': self.id,
                'target': 'new',
                'view_type': 'form',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'flags': {'action_buttons': False, 'mode': 'edit', 'toolbar': False, },
                'context': {'create': False,
                            'default_name': f'Allocation request for date {self.attendance_id.attendance_recorded_date}',
                            'default_holiday_status_id': holiday_status_id.id,
                            'default_attendance_id': self.attendance_id.id,
                            'default_holiday_type': 'employee',
                            'default_employee_id': self.attendance_id.employee_id.id}
            }

        else:
            raise ValidationError(
                "Comp Off leave type does not exist in the system.\n Please create a comp off leave type and try again.")

