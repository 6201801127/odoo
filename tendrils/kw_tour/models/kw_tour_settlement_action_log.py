from odoo import models, fields, api


class TourSettlementActionLog(models.Model):
    _name = 'kw_tour_settlement_action_log'
    _description = "Tour Settlement Action Logs"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    settlement_id = fields.Many2one('kw_tour_settlement', 'Settlement', required=True, ondelete="cascade")
    employee_id = fields.Many2one('hr.employee', "Action Taken By",
                                  default=_default_employee, required=False, ondelete='restrict', index=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    state = fields.Char("State", required=True)
    remark = fields.Text("Remark", required=True)
