# -*- coding: utf-8 -*-
#########################
# Modification History :
# 04-Aug-2020 : method added for employee timezone wise current date, By : T Ketaki Debadarshini
# 08-Mar-2021 : method added for current date color code in employee, By : Gouranga

#########################

import pytz
from odoo import models, fields, api
from datetime import date, datetime, timedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    attendance_mode_ids = fields.Many2many('kw_attendance_mode_master', string="Attendance mode")
    no_attendance = fields.Boolean(string='No Attendance')
    # branch_id               = fields.Many2one('kw_res_branch', string="Branch/SBU", related="user_id.branch_id")
    branch_id = fields.Char(string="Branch/SBU", related="user_id.branch_id.alias")
    attendance_mode = fields.Char("Attendance Mode Display", compute="get_attendance_mode")
    # branch_location         = fields.Many2one('kw_location_master', string="Location",related="branch_id.location",store=True)

    kw_attendance_ids = fields.One2many(
        string='Daily Attendance Details',
        comodel_name='kw_daily_employee_attendance',
        inverse_name='employee_id',
    )

    roaster_group_ids = fields.One2many('kw_roaster_group_config', 'group_head_id', string="Roaster Groups")

    shift_change_log_ids = fields.One2many(comodel_name='kw_attendance_shift_log', inverse_name='employee_id')

    def default_effective_from(self):
        return self.date_of_joining if self.date_of_joining else self.create_date.date()

    effective_from = fields.Date(string='Effective From')  # ,default=default_effective_from

    today_attendance_status = fields.Selection(string="Attendance Status",
                                               selection=[('present', 'Present'), ('absent', 'Absent'),
                                                          ('leave', 'On Leave'), ('tour', 'On Tour'), ('wfh', 'WFH'),
                                                          ('local_visit', 'Local Visit')],
                                               compute="_compute_today_attendance_status")

    @api.model
    def get_attendance_mode(self):
        for emp in self:
            if emp.no_attendance:
                emp.attendance_mode = "No Attendance"
            else:
                attendance = emp.attendance_mode_ids.mapped('name')
                emp.attendance_mode = ', '.join(attendance)

    # last_attendance_log_id = fields.Many2one('hr.attendance', compute='_compute_last_attendance_log_id',)

    # @api.depends('kw_attendance_log_ids')
    # def _compute_last_attendance_id(self):
    #     for employee in self:
    #         employee.last_attendance_id = self.env['hr.attendance'].search([
    #             ('employee_id', '=', employee.id),
    #         ], limit=1)

    @api.onchange("no_attendance")
    def _change_attendance_status(self):
        for record in self:
            if record.no_attendance:
                record.attendance_mode_ids = False

    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """

        shift_log = self.env['kw_attendance_shift_log']
        for record in self:
            if 'resource_calendar_id' in values:
                vals = {}
                last_record = shift_log.search([('employee_id', '=', record.id)], order='id asc')
                effective_date = date.today()
                if 'effective_from' in values:
                    if values['effective_from']:
                        effective_date = datetime.strptime(str(values['effective_from']), '%Y-%m-%d')
                elif record.effective_from:
                    effective_date = record.effective_from

                if not last_record:
                    shift_log.create({
                        'effective_from': record.create_date.date(),
                        'effective_to': effective_date - timedelta(days=1),
                        'shift_id': record.resource_calendar_id.id or False,
                        'employee_id': record.id
                    })
                else:
                    last_record[-1].write({
                        'effective_to': effective_date - timedelta(days=1)
                    })

                shift_log.create({
                    'effective_from': effective_date,
                    'shift_id': values['resource_calendar_id'],
                    'employee_id': record.id
                })

            if 'effective_from' in values:
                if values['effective_from']:
                    shift_records = shift_log.search([('employee_id', '=', record.id)])
                    if shift_records:
                        shift_records[-2].write({
                            'effective_to': datetime.strptime(str(values['effective_from']), '%Y-%m-%d') - timedelta(days=1)
                        })
                        shift_records[-1].write({
                            'effective_from': values['effective_from'],
                        })

        result = super(HrEmployee, self).write(values)

        return result

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """

        result = super(HrEmployee, self).create(values)

        return result

    @api.multi
    def get_employee_tz_today(self):
        """get current day/date as per the employee timezone

            returns datetime object with timezone
        """
        self.ensure_one()
        emp_tz = self.tz or self.resource_calendar_id.tz or 'UTC'
        emp_timezone = pytz.timezone(emp_tz)
        today = datetime.now().astimezone(emp_timezone)

        return today

    # added on 11 march 2021(gouranga) to calculate the current day status of employee
    @api.multi
    def _compute_today_attendance_status(self):
        current_date = date.today()
        attendance_data = self.env['kw_daily_employee_attendance'].sudo().search(
            [('employee_id', 'in', self.ids), ('attendance_recorded_date', '=', current_date)])

        for employee in self:
            status = 'absent'
            today_attendance = attendance_data.filtered(
                lambda r: r.employee_id == employee and r.attendance_recorded_date == current_date)

            if today_attendance:
                if today_attendance.is_on_tour:
                    status = 'tour'

                if today_attendance.leave_day_value > 0:
                    status = 'leave'

                if today_attendance.check_in:
                    status = 'present'

                if today_attendance.check_in and today_attendance.work_mode =='0':
                    status = 'wfh'

                if today_attendance.check_in and today_attendance.local_visit_status in ('1','2','3'):
                    status = 'local_visit'

            employee.today_attendance_status = status

    @api.multi
    def view_attendance_report(self):
        tree_view_id = self.env.ref('kw_hr_attendance.view_kw_daily_employee_attendance_tree').id
        form_view_id = self.env.ref('kw_hr_attendance.view_kw_daily_employee_attendance_form').id

        _action = {
            'name': 'Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_daily_employee_attendance',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'flags': {'action_buttons': True, 'mode': 'edit'},
            'domain': [('employee_id', '=', self.ids[0])],
            'context': {'search_default_employee_id': [self.ids[0]], 'search_default_last_30_days_attendance': 1}
        }

        return _action
