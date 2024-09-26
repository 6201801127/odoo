# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AttendanceCopyShiftFixedHolidays(models.TransientModel):
    _name           = 'kw_attendance_copy_shift_fixed_holidays'
    _description    = 'Attendance Copy Shift Fixed Holiday(s)'

    year = fields.Char(string='Year', required=True)
    branch_id = fields.Many2one(string='Branch', comodel_name='kw_res_branch', required = True)
    shift_id = fields.Many2one(string='Shift', comodel_name='resource.calendar', required = True)
    copy_shift_id = fields.Many2one(string='Copy To', comodel_name='resource.calendar',required = True)
    global_leave_ids = fields.Many2many(string='Holidays',
                                        comodel_name='resource.calendar.leaves',
                                        relation='copy_fixed_holiday_wizard_resource_calendar_leaves_rel',
                                        column1='copy_wizard_id',
                                        column2='calendar_leaves_id'
                                        )
    excluded_public_holidays_ids = fields.Many2many(
        string='Exclude Branch Holidays',
        comodel_name='hr.holidays.public.line',
        relation='copy_fixed_holiday_wizard_public_holiday_line_rel',
        column1='copy_wizard_id',
        column2='public_holiday_id'
    )

    @api.onchange('branch_id')
    def set_shift_id(self):
        if self.branch_id:
            if self.shift_id and self.shift_id.branch_id != self.branch_id:
                self.shift_id = False
            if self.copy_shift_id and self.copy_shift_id.branch_id != self.branch_id:
                self.copy_shift_id = False
        else:
            self.shift_id = False
            self.copy_shift_id = False

    @api.onchange('shift_id', 'year')
    def set_leave_ids(self):
        ids = []
        exclude_ids = []
        if self.shift_id and self.year:
            shift_leave_ids = self.shift_id.global_leave_ids.filtered(
                lambda r: r.start_date != False and str(r.start_date.year) == self.year and r.holiday_type == '2')
            ids = shift_leave_ids.ids

            exclude_holidays = self.shift_id.excluded_public_holidays_ids.filtered(lambda r: str(r.date.year) == self.year)
            exclude_ids = exclude_holidays.ids
        self.global_leave_ids = [[6,0,ids]]
        self.excluded_public_holidays_ids = [[6,0,exclude_ids]]

        if self.copy_shift_id and self.copy_shift_id == self.shift_id:
            self.copy_shift_id = False

    @api.multi
    def create_shift_with_fixed_holidays(self):
        # shift_leave_data = self.shift_id.global_leave_ids.filtered(lambda r:r.start_date != False and str(r.start_date.year) == self.year and r.holiday_type == '2')
        # if not shift_leave_data:
        #     raise ValidationError(f"No fixed holidays found in shift {self.shift_id.name}")
        if not self.global_leave_ids:
            raise ValidationError(f"No fixed holidays found in shift {self.shift_id.name}")
        
        if self.copy_shift_id:
            leave_to_create = []
            for leave in self.global_leave_ids:
                leave_exists = self.copy_shift_id.global_leave_ids.filtered(
                    lambda r: r.start_date == leave.start_date and r.name != False and r.name.lower()==leave.name.lower())
                if not leave_exists or self.shift_id == self.copy_shift_id:
                    leave_to_create.append([0, 0, {
                        'name'          : leave.name,
                        'start_date'    : leave.start_date,
                        'day'           : leave.day,
                        'holiday_type'  : leave.holiday_type,
                        'date_from'     : leave.date_from,
                        'date_to'       : leave.date_to,
                        # 'time_type'   : leave.time_type,
                        # 'resource_id' : leave.resource_id and leave.resource_id.id or False,
                    }])

            if leave_to_create:
                self.copy_shift_id.global_leave_ids = leave_to_create

            if self.excluded_public_holidays_ids:
                all_holidays = self.copy_shift_id.excluded_public_holidays_ids | self.excluded_public_holidays_ids
                self.copy_shift_id.excluded_public_holidays_ids = [[6,0,all_holidays.ids]]
        # else:
        #     self.env['resource.calendar'].create({
        #         'name': f'Copy of {self.shift_id.name}',
        #         'branch_id':self.branch_id.id,
        #         'tz': self.shift_id.tz,
        #         'global_leave_ids': [[0,0,{
        #             'name'          : leave.name,
        #             'start_date'    : leave.start_date,
        #             'day'           : leave.day,
        #             'holiday_type'  : leave.holiday_type,
        #             'date_from'     : leave.date_from,
        #             'date_to'       : leave.date_to,
        #             # 'time_type'   : leave.time_type,
        #             # 'resource_id' : leave.resource_id and leave.resource_id.id or False,
        #         }]for leave in self.global_leave_ids],
        #     })
        return {'type': 'ir.actions.act_window_close'}
