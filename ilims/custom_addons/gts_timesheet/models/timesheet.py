from odoo import api, fields, models, _


class Task(models.Model):
    _inherit = 'project.task'

    @api.depends('timesheet_ids.unit_amount', 'issue_timesheet_ids.unit_amount', 'incident_timesheet_ids.unit_amount')
    def _compute_effective_hours(self):
        for task in self:
            if task.risk_incident is True:
                task.effective_hours = round(sum(task.incident_timesheet_ids.mapped('unit_amount')), 2)
            if task.is_issue is True:
                task.effective_hours = round(sum(task.issue_timesheet_ids.mapped('unit_amount')), 2)
            elif task.is_issue is False and task.risk_incident is False:
                task.effective_hours = round(sum(task.timesheet_ids.mapped('unit_amount')), 2)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    issue_id = fields.Many2one('project.task', 'Issue')
    ticket_id = fields.Many2one('support.ticket', 'Ticket')
