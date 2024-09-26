from odoo import models, fields


class AdvancerequestActionLog(models.Model):
    _name = 'kw_advance_request_action_log'
    _description = "Advance Request Action Logs"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    tour_id = fields.Many2one('kw_tour', 'Apply Tour', required=True, ondelete="cascade")

    employee_id = fields.Many2one('hr.employee', "Action Taken By",
                                  default=_default_employee, required=True, ondelete='restrict', index=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    amount = fields.Float("Amount Requested", required=True)
    disbursed_amount = fields.Float("Amount Disbursed", required=True)
    total_amount_paid = fields.Float("Total Amount Paid", required=True)
    exchange_rate = fields.Float(string="Exchange Rate", required=True)
    remark = fields.Text("Remark", required=True)
