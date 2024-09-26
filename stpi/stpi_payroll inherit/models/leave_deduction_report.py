from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class LeaveDeductionReport(models.Model):
    _name = 'leave.deduction.report'
    _description = 'Leave Deduction Report'


    employee_id = fields.Many2one('hr.employee', 'Employee')
    leave_type_id = fields.Many2one('hr.leave.type')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    total_days = fields.Integer('Total (Days)')
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), 
                                ('04', 'April'), ('05', 'May'), ('06', 'June'), 
                                ('07', 'July'), ('08', 'August'), ('09', 'September'), 
                                ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month')
    deduction_days = fields.Integer('Deduction (Days)')
    pending_deduction_days = fields.Integer('Pending Deduction (Days)')
    payslip_id = fields.Many2one('hr.payslip')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    def count_leave_days(self, relative_from, relative_to, from_date, to_date):
        leave_lis = [from_date + relativedelta(days=r) for r in range((to_date-from_date).days + 1)]
        filt_leave_lis = list(filter(lambda x: relative_from <= x <= relative_to, leave_lis))
        return len(filt_leave_lis)


    @api.multi
    def action_payslip_done(self):
        res = super().action_payslip_done()
        for payslip in self:
            relative_from = (payslip.date_from - relativedelta(months=1)).replace(day=26)
            relative_to = payslip.date_from.replace(day=25)
            hpl_leave_type_id = self.env['hr.leave.type'].sudo().search([('leave_type.code', '=', 'Half Pay Leave')])
            ccl_leave_type_id = self.env['hr.leave.type'].sudo().search([('leave_type.code', '=', 'Child Care Leave')])
            if sum(payslip.line_ids.filtered(lambda x: x.code == 'HPL').mapped('total')) != 0:
                hpl_recs = self.env['hr.leave'].sudo().get_employee_leave_detail('HPL', payslip.employee_id.id, relative_from, relative_to)
                vals = {}
                total_leave_deduct = len(hpl_recs.get('days'))
                remain_leave = total_leave_deduct

                for hpl_rec in sorted(hpl_recs.get('leave_records'), key=lambda x: x.request_date_from):
                    leave_count = self.count_leave_days(relative_from, relative_to, hpl_rec.request_date_from, hpl_rec.request_date_to)
                    temp_leave_deduct = min(leave_count, hpl_rec.no_of_days_display_half)
                    remain_leave -= temp_leave_deduct
                    vals.update({
                        'payslip_id': payslip.id,
                        'employee_id': hpl_rec.employee_id.id,
                        'leave_type_id': hpl_leave_type_id.id,
                        'from_date': hpl_rec.request_date_from,
                        'to_date': hpl_rec.request_date_to,
                        'total_days': hpl_rec.no_of_days_display_half,
                        'month': payslip.date_to.strftime('%m'),
                        'deduction_days': temp_leave_deduct,
                        # 'pending_deduction_days': remain_leave if remain_leave > 0 else abs(temp_leave_deduct - hpl_rec.no_of_days_display_half)
                    })
                    self.env['leave.deduction.report'].sudo().create(vals)
            if sum(payslip.line_ids.filtered(lambda x: x.code == 'CCLD').mapped('total')) != 0:
                ccl_recs = self.env['hr.leave'].sudo().get_employee_leave_detail('CCL', payslip.employee_id.id, relative_from, relative_to)
                vals = {}
                total_leave_deduct = len(ccl_recs.get('days'))
                remain_leave = total_leave_deduct

                for ccl_rec in sorted(ccl_recs.get('leave_records'), key=lambda x: x.request_date_from):
                    leave_count = self.count_leave_days(relative_from, relative_to, ccl_rec.request_date_from, ccl_rec.request_date_to)
                    temp_leave_deduct = min(leave_count, ccl_rec.no_of_days_display_half)
                    remain_leave -= temp_leave_deduct
                    vals.update({
                        'payslip_id': payslip.id,
                        'employee_id': ccl_rec.employee_id.id,
                        'leave_type_id': ccl_leave_type_id.id,
                        'from_date': ccl_rec.request_date_from,
                        'to_date': ccl_rec.request_date_to,
                        'total_days': ccl_rec.no_of_days_display_half,
                        'month': payslip.date_to.strftime('%m'),
                        'deduction_days': temp_leave_deduct,
                        # 'pending_deduction_days': remain_leave if remain_leave > 0 else abs(temp_leave_deduct - ccl_rec.no_of_days_display_half)
                    })
                    self.env['leave.deduction.report'].sudo().create(vals)
        return res
