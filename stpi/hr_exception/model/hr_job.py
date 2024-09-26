from odoo import api, models, fields


class ExceptionRule(models.Model):
    _inherit = 'exception.rule'

    rule_group = fields.Selection(
        selection_add=[('hr_job', 'Hr Job')],
    )
    model = fields.Selection(
        selection_add=[
            ('hr.job', 'Hr Job'),
            ('job.position.budget', 'Hr Budget'),
        ])

class HrJobException(models.Model):
    _inherit = ['hr.job', 'base.exception']
    _name = 'hr.job'
    _order = 'main_exception_id asc,name desc'

    rule_group = fields.Selection(
        selection_add=[('hr_job', 'Hr Job')],
        default='hr_job',
    )

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'budget')])
        order_set.test_exceptions()
        return True


    @api.constrains('ignore_exception', 'budget_id', 'state')
    def hr_job_check_exception(self):
        if self.state == 'open':
            self._check_exception()

    @api.onchange('budget_id')
    def onchange_ignore_exception(self):
        if self.state == 'open':
            self.ignore_exception = False

    @api.multi
    def approve_budget(self):
        if self.detect_exceptions():

            return self._popup_exceptions()
        else:
            return super(HrJobException, self).approve_budget()

    @api.multi
    def set_open(self):
        res = super(HrJobException, self).set_open()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({
            'ignore_exception': False,
        })
        return res

    def _hr_job_get_lines(self):
        self.ensure_one()
        return self.budget_id

    @api.model
    def _get_popup_action(self):
        # print("----------------------------_get_popup_action")
        action = self.env.ref('hr_exception.action_hr_job_exception_confirm')
        return action


class JobPositionBudget(models.Model):
    _inherit = ['job.position.budget', 'base.exception']
    _name = 'job.position.budget'
    _order = 'main_exception_id asc'

    rule_group = fields.Selection(
        selection_add=[('job_budget_line', 'Hr Budget')],
        default='job_budget_line',
    )


class Approvalslist(models.Model):
    _inherit = "approvals.list"

    @api.multi
    def approve(self):
        res = super(Approvalslist, self).approve()
        if res:
            # print("----------------------self.model_id.model", self.model_id.model)
            if self.model_id.model == 'hr.job':
                self.resource_ref.approve_budget()
        return res