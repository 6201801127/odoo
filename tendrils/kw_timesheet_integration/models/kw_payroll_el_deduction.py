from odoo import api, fields, models, _
from odoo.exceptions import UserError


class kw_payroll_el_deduction(models.TransientModel):
    _name = 'el_deduction'
    _description = 'Approve EL Deduction'

    def _get_insurance_data(self):
        payroll_details_ids = self.env.context.get('selected_active_ids')
        res = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('id','in',payroll_details_ids),('timesheet_el_deduct_in_day','>',0),('el_deducted','=',False)])
        return res

    payroll_details_ids = fields.Many2many('kw_payroll_monthly_attendance_report', default=_get_insurance_data, string="Attendance Details")

    @api.multi
    def approve_el_deduction_btn(self):
        if self.payroll_details_ids:            
            for payroll in self.payroll_details_ids:
                # print(payroll.employee_id.id,payroll.timesheet_el_deduct_in_day)
                self.env['hr.leave.allocation'].lapse_el_timesheet_integration(payroll.employee_id.id,'EL',payroll.timesheet_el_deduct_in_day)
                payroll.write({'el_deducted':True})
            self.env.user.notify_success(message='EL has been deducted successfully!.')

            
