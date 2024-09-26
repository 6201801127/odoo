from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import calendar

class FyWiseBudgetPlan(models.Model):
    _name = 'fy_wise_budget_plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "FY Wise Budget Plan"
    _rec_name = 'fy_work_order_id'
    _sql_constraints = [
        ('order_name_uniq', 'unique(fy_work_order_id)', 'Order already exist.'),
    ]

    fy_work_order_id = fields.Many2one('kw_project_budget_master_data', string="WorkOrder", track_visibility='onchange')
    fy_wo_code = fields.Char(string="Work Order Code", track_visibility='onchange')
    fy_account_line_ids = fields.One2many('fy_wise_budget_allocate_line', 'fy_budget_allocation_id',
                                          track_visibility='onchange')
    fy_client_name = fields.Char(string="Client")
    fy_order_name = fields.Char(string="Order Name")
    fy_order_value = fields.Float(string="Order Value")
    fy_order_date = fields.Date(string="Order Date")
    fy_plan_year = fields.Many2one("account.fiscalyear", string="Fiscal Year")
    state = fields.Selection([('draft', 'Draft'),('applied', 'Applied'), ('approved', 'Approved')], default='draft',
                             string='Status', track_visibility="alaways")
    pro_commencement_month = fields.Many2one("account.fiscalyear", string="Project Commencement [Year]", store=True)
    pro_month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], string="Project Commencement [Month]")
    tot_project_duration = fields.Integer(string="Total Project Duration [As Per Contract]")

    @api.constrains('tot_project_duration', 'fy_account_line_ids')
    def _check_project_duration(self):
        for record in self:
            if record.tot_project_duration < 0:
                raise ValidationError('Project duration cannot be negative.')
            budget_planned_sums = {}
            budget_amount = {}
            for line in record.fy_account_line_ids:
                account_subhead_name = line.account_sub_head_id.name
                if account_subhead_name in budget_planned_sums:
                    budget_planned_sums[account_subhead_name] += line.budget_to_be_planned
                    budget_amount[account_subhead_name] = line.budget_amount
                else:
                    budget_planned_sums[account_subhead_name] = line.budget_to_be_planned
                    budget_amount[account_subhead_name] = line.budget_amount

            for key in budget_amount:
                if key in budget_planned_sums:
                    if budget_amount[key] < budget_planned_sums[key]:
                        raise ValidationError('Planned amount must not exceed the available balance.')




    @api.onchange('tot_project_duration')
    def _onchange_tot_project_duration(self):
        if self.pro_commencement_month and self.pro_month and self.tot_project_duration:
            fiscal_year_start = self.pro_commencement_month.date_start
            fiscal_year_end = self.pro_commencement_month.date_stop
            fiscal_year_start_year = fiscal_year_start.year
            fiscal_year_end_year = fiscal_year_end.year
            if self.pro_month >= 4:
                start_year = fiscal_year_start_year
            else:
                start_year = fiscal_year_end_year
            start_date = datetime(start_year, self.pro_month, 1)
            start_datee = start_date.date()
            end_date = self._add_months(start_date, self.tot_project_duration)
            end_datee = end_date.date()
            start_fiscal_year = self.env['account.fiscalyear'].search(
                [('date_start', '<=', start_datee), ('date_stop', '>=', start_datee)], limit=1)
            end_fiscal_year = self.env['account.fiscalyear'].search(
                [('date_start', '<=', end_datee), ('date_stop', '>=', end_datee)], limit=1)
            if end_fiscal_year:
                current_value = self._origin.tot_project_duration if self._origin else 0
                if self.tot_project_duration < current_value and self.fy_account_line_ids:
                    raise ValidationError('project duration cannot be less than the Previous value.')
            else:
                raise ValidationError('Please Add Fiscal Year to create budget.')

    @api.onchange('fy_work_order_id')
    def get_data(self):
        if self.fy_work_order_id:
            or_date = self.fy_work_order_id.crm_lead_id.date_open
            self.fy_wo_code = self.fy_work_order_id.wo_code
            self.fy_client_name = self.fy_work_order_id.crm_lead_id.client_name
            self.fy_order_name = self.fy_work_order_id.wo_name
            self.fy_order_value = self.fy_work_order_id.order_value
            self.fy_order_date = or_date.date() if or_date else False
            fiscal_year = self.env['account.fiscalyear'].search([('date_start', '<=', self.fy_order_date), ('date_stop', '>=', self.fy_order_date)], limit=1)
            self.fy_plan_year = fiscal_year
            self.pro_commencement_month = fiscal_year.id

    def _add_months(self, dt, months):
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day)

    def action_add_budget_plan(self):
        if self.pro_commencement_month and self.pro_month and self.tot_project_duration:
            # Store existing budget_to_be_planned values
            existing_budget_to_be_planned = {}
            for line in self.fy_account_line_ids:
                key = (line.fiscal_year.id, line.group_head_id.id, line.group_name_id.id,
                       line.account_head_id.id, line.account_sub_head_id.id)
                existing_budget_to_be_planned[key] = line.budget_to_be_planned

            self.fy_account_line_ids = False
            fiscal_year_start = self.pro_commencement_month.date_start
            fiscal_year_end = self.pro_commencement_month.date_stop
            fiscal_year_start_year = fiscal_year_start.year
            fiscal_year_end_year = fiscal_year_end.year
            if self.pro_month >= 4:
                start_year = fiscal_year_start_year
            else:
                start_year = fiscal_year_end_year
            start_date = datetime(start_year, self.pro_month, 1)
            start_datee = start_date.date()
            end_date = self._add_months(start_date, self.tot_project_duration)
            end_datee = end_date.date()
            start_fiscal_year = self.env['account.fiscalyear'].search(
                [('date_start', '<=', start_datee), ('date_stop', '>=', start_datee)], limit=1)
            end_fiscal_year = self.env['account.fiscalyear'].search(
                [('date_start', '<=', end_datee), ('date_stop', '>=', end_datee)], limit=1)
            if end_fiscal_year:
                data = self.env['account.fiscalyear'].sudo().search([('date_start', '>=', start_fiscal_year.date_start), ('date_stop', '<=', end_fiscal_year.date_stop)])
                line = []
                for rec in data:
                    for record in self.fy_work_order_id.project_budget_ids:
                        key = (rec.id, record.group_head_id.id, record.group_name.id,
                               record.account_head_id.id, record.account_sub_head_id.id)
                        budget_to_be_planned = existing_budget_to_be_planned.get(key, 0.0)
                        line.append((0, 0, {
                            'fiscal_year': rec.id,
                            'fy_budget_allocation_id': self.id,
                            'group_head_id':record.group_head_id.id,
                            'group_name_id':record.group_name.id,
                            'account_head_id':record.account_head_id.id,
                            'account_sub_head_id':record.account_sub_head_id.id,
                            'budget_amount':record.budget_amount,
                            'budget_to_be_planned': budget_to_be_planned,
                        }))
                self.fy_account_line_ids = line
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Add Plan Successfully.',
                        'img_url':  '/web/static/src/img/smile.svg',
                        'type': 'rainbow_man',
                    }
                }
            else:
                raise ValidationError('Please Add Fiscal Year to create budget.')


    def applied_fy_budget(self):
        self.state = 'applied'

    def approved_fy_budget(self):
        self.state = 'approved'

    def update_budget_amount_details(self):
        existing_lines = {
            (line.group_head_id.id, line.group_name_id.id, line.account_head_id.id, line.account_sub_head_id.id): line
            for line in self.fy_account_line_ids
        }

        new_lines = []
        for record in self.fy_work_order_id.project_budget_ids:
            key = (record.group_head_id.id, record.group_name.id, record.account_head_id.id, record.account_sub_head_id.id)
            if key in existing_lines:
                existing_lines[key].budget_amount = record.budget_amount
            else:
                new_lines.append((0, 0, {
                    'fiscal_year': self.fy_plan_year.id,
                    'fy_budget_allocation_id': self.id,
                    'group_head_id': record.group_head_id.id,
                    'group_name_id': record.group_name.id,
                    'account_head_id': record.account_head_id.id,
                    'account_sub_head_id': record.account_sub_head_id.id,
                    'budget_amount': record.budget_amount,
                }))

        if new_lines:
            self.fy_account_line_ids = new_lines
            self.action_add_budget_plan()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Budget Synced Successfully.',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }




class FyWiseBudgetAllocateLine(models.Model):
    _name = 'fy_wise_budget_allocate_line'
    _description = "FY Wise Budget Allocate Line"

    fiscal_year = fields.Many2one('account.fiscalyear', string="Financial Year")
    fy_budget_allocation_id = fields.Many2one('fy_wise_budget_plan')
    group_head_id = fields.Many2one('account.account.type', string='Group Head')
    group_name_id = fields.Many2one('account.group.name', string='Group Name')
    account_head_id = fields.Many2one('account.head', string="Account Head")
    account_sub_head_id = fields.Many2one("account.sub.head", string="Account Sub Head")
    budget_amount = fields.Float('Budget Amount')
    compute_char_data = fields.Char(compute='get_data', store=False)
    budget_to_be_planned = fields.Float('Budget to Be Planned')
    # resource_budget_id = fields.Many2one('kw_resource_budget', string="Resource Budget")


    def get_data(self):
        for rec in self:
            account_head_id = rec.account_head_id.name or ''
            account_sub_head_id = rec.account_sub_head_id.name or ''
            budget_amount = str(rec.budget_amount) or ''
            rec.compute_char_data = '  |  '.join(filter(None, [account_head_id, account_sub_head_id, budget_amount]))

    @api.onchange('budget_to_be_planned')
    def validate_budget_to_be_planned(self):
        if self.budget_to_be_planned > self.budget_amount:
            raise ValidationError('The planned budget amount cannot exceed the available budget balance.')



