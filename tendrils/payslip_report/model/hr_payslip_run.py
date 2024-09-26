from odoo import api, fields, models, tools, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    allow_download = fields.Boolean(string='Allow Download')

    #     branch_id = fields.Many2one('res.branch',string="Branch",default=lambda self: self.env['res.users']._get_default_branch())

    @api.multi
    def cancel_payslip_run(self):
        #         print"We are in new inherited button method"
        for slip in self.slip_ids:
            if slip.state == 'draft':
                slip.compute_sheet()
                slip.action_payslip_done()
        return self.write({'state': 'close'})

    # @api.multi
    # def show_payroll_register_report(self):
    #     for payslip in self:
    #         val = {
    #             'name': 'Payroll Register',
    #             'view_type': 'pivot',
    #             'view_mode': 'pivot',
    #             'res_model': 'hr.payslip.line',
    #             'view_id':self.env.ref('payslip_report.hr_payslip_line_pivot_view').id,
    #             'domain': [
    #                         ('slip_id', 'in', payslip.slip_ids.ids),
    #                         ],
    #             'type': 'ir.actions.act_window',
    #             'target':'new',
    #             }
    #         return val
