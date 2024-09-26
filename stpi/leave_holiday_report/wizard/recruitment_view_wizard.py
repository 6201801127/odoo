from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
import datetime
from odoo.tools import float_utils
from collections import defaultdict
from pytz import utc


class WizardLateComing(models.TransientModel):
    _name = 'leave.holiday.wizard'
    _description = 'Holiday Leave'
    

    # def _default_employee(self):
    #     return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _default_from_date(self):
        epoch_year = date.today().year
        year_start = date(epoch_year, 1, 1)
        return year_start

    def _default_to_date(self):
        epoch_year = date.today().year
        year_end = date(epoch_year, 12, 31)
        return year_end

    @api.model
    def _get_branch(self):
        return self.env.user.default_branch_id
    
    report_of = fields.Selection([('leave','Leave Holiday'),
                                  ],string="Report On", default='leave')
    # employee_id = fields.Many2one('hr.employee','Requested By', default=_default_employee)
    from_date = fields.Date(string='From Date', default=_default_from_date)
    to_date = fields.Date(string='To Date', default=_default_to_date)
    branch_ids = fields.Many2many('res.branch', string='Branches', default=_get_branch)


    @api.multi
    def confirm_report(self):
        for rec in self:
            my_id = []
            dr = self.env['resource.calendar.leaves.report'].search([('branch_id', 'in', rec.branch_ids.ids)])
            for lines in dr:
                lines.unlink()
            dr_b = self.env['resource.calendar.leaves'].search([('calendar_id.branch_id', 'in', rec.branch_ids.ids)])
            for emp in dr_b:
                if rec.from_date and emp.date and rec.to_date and rec.from_date <= emp.date <= rec.to_date:
                    month = ''
                    if str(emp.date.month) == '1':
                        month = 'January'
                    elif str(emp.date.month) == '2':
                        month = 'February'
                    elif str(emp.date.month) == '3':
                        month = 'March'
                    elif str(emp.date.month) == '4':
                        month = 'April'
                    elif str(emp.date.month) == '5':
                        month = 'May'
                    elif str(emp.date.month) == '6':
                        month = 'June'
                    elif str(emp.date.month) == '7':
                        month = 'July'
                    elif str(emp.date.month) == '8':
                        month = 'August'
                    elif str(emp.date.month) == '9':
                        month = 'September'
                    elif str(emp.date.month) == '10':
                        month = 'October'
                    elif str(emp.date.month) == '11':
                        month = 'November'
                    elif str(emp.date.month) == '12':
                        month = 'December'
                    else:
                        month = ''
                    cr = self.env['resource.calendar.leaves.report'].create({
                        'name': emp.name,
                        'date': emp.date,
                        'branch_id': emp.calendar_id.branch_id.id,
                        'holiday_id': emp.calendar_id.id,
                        'month': month,
                        'holiday_type': emp.holiday_type,
                    })
                    my_id.append(cr.id)
            return {
                'name': 'Leave Holiday Report',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'resource.calendar.leaves.report',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [
                    ('branch_id', 'in', rec.branch_ids.ids),
                    ('id', 'in', my_id),
                ],
                'context': {
                                'search_default_is_not_sat_sun': 1,
                            }
                }


    #
    # @api.multi
    # def confirm_existing_report(self):
    #     for rec in self:
    #         dr = self.env['resource.calendar.leaves.report'].search([('branch_id', 'in', rec.branch_ids.ids)])
    #         for lines in dr:
    #             lines.unlink()
    #         emp_ids = self.env['hr.employee'].search([('branch_id', 'in', rec.branch_ids.ids)])
    #         for employees in emp_ids:
    #             for emp in employees.resource_calendar_id.global_leave_ids:
    #                 if rec.from_date <= emp.date <= rec.to_date:
    #                     month = ''
    #                     if str(emp.date.month) == '1':
    #                         month = 'January'
    #                     elif str(emp.date.month) == '2':
    #                         month = 'February'
    #                     elif str(emp.date.month) == '3':
    #                         month = 'March'
    #                     elif str(emp.date.month) == '4':
    #                         month = 'April'
    #                     elif str(emp.date.month) == '5':
    #                         month = 'May'
    #                     elif str(emp.date.month) == '6':
    #                         month = 'June'
    #                     elif str(emp.date.month) == '7':
    #                         month = 'July'
    #                     elif str(emp.date.month) == '8':
    #                         month = 'August'
    #                     elif str(emp.date.month) == '9':
    #                         month = 'September'
    #                     elif str(emp.date.month) == '10':
    #                         month = 'October'
    #                     elif str(emp.date.month) == '11':
    #                         month = 'November'
    #                     elif str(emp.date.month) == '12':
    #                         month = 'December'
    #                     else:
    #                         month = ''
    #                     cr = self.env['resource.calendar.leaves.report'].create({
    #                         'employee_id': rec.employee_id.id,
    #                         'name': emp.name,
    #                         'date': emp.date,
    #                         'branch_id': emp.calendar_id.branch_id.id,
    #                         'holiday_id': emp.calendar_id.id,
    #                         'month': month,
    #                     })
    #
    #     return {
    #         'name': 'Leave Holiday Report',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'resource.calendar.leaves.report',
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'domain': [('branch_id', 'in', self.branch_ids.ids)],
    #     }
