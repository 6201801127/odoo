from odoo import models, fields, api
import requests, json
from odoo.exceptions import ValidationError
from collections import defaultdict



class TourTreasuryBudget(models.Model):
    _name = "kw_tour_treasury_budget"
    _description = "Tour Treasury Budget"
    _rec_name= "department_id"
    # _order = "budget_amount desc"

    # budget_head_id = fields.Many2one('kw_tour_budget_head', 'Budget Head')
    fiscal_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always')
    budget_amount = fields.Float('Budget Amount')
    spent_amount = fields.Float('Spent Amount', compute='calculate_remaining_amount')
    remaining_amount = fields.Float('Remaining Amount', compute='calculate_remaining_amount')
    department_id = fields.Many2one('hr.department', string="Department")
    tour_ids = fields.One2many('kw_tour', 'treasury_budget_id', string='Tours')
    settlement_ids = fields.One2many('kw_tour_settlement', 'treasury_budget_id', string='Settlements')
    company_id = fields.Many2one('res.company', string="Company", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  related='company_id.currency_id', readonly=True)


    @api.constrains('department_id')
    def _check_duplicate(self):
        if self.department_id:
            duplicate_data = self.env['kw_tour_treasury_budget'].sudo().search([('company_id','=',self.company_id.id), ('department_id','=',self.department_id.id), ('fiscal_year_id', '=', self.fiscal_year_id.id)]) - self
            if duplicate_data:
                raise ValidationError("Department Name already exist for this company.")

    @api.multi
    @api.depends('budget_amount', 'tour_ids', 'tour_ids.total_budget_expense', 'spent_amount', 'settlement_ids', 'settlement_ids.total_budget_expense')
    def calculate_remaining_amount(self):
        for record in self:
            record.spent_amount = sum(record.tour_ids.mapped('total_budget_expense')) + sum(record.settlement_ids.mapped('total_budget_expense'))
            record.remaining_amount = record.budget_amount - record.spent_amount


    def create_update_treasury_budget(self):
        tour_treasury_budget = self.env['kw_tour_treasury_budget'].sudo()
        budget_config = self.env['tour_budget_account_config'].sudo().search([('budget_type', '=', 'treasury_budget')],
                                                                             limit=1)
        treasury_account_codes = budget_config.account_code_ids.ids
        treasury_budget_data = self.env['kw_revenue_budget_line'].sudo().search(
            [('account_code_id', 'in', treasury_account_codes), ('state', '=', 'validate')])

        data_dict = {}

        for rec in treasury_budget_data:
            if rec.revenue_budget_id and (
                    rec.revenue_budget_id.budget_section or rec.revenue_budget_id.budget_division or rec.revenue_budget_id.budget_dept):
                budget_type = None
                if rec.revenue_budget_id.budget_section:
                    budget_type = rec.revenue_budget_id.budget_section
                elif rec.revenue_budget_id.budget_division:
                    budget_type = rec.revenue_budget_id.budget_division
                elif rec.revenue_budget_id.budget_dept:
                    budget_type = rec.revenue_budget_id.budget_dept
                if rec.revenue_budget_id.id not in data_dict:
                    data_dict[rec.revenue_budget_id.id] = {
                        'budget_type': budget_type.id,
                        'total_amount': 0,
                        'fiscal_year_id': None,
                        'company_id': None
                    }
                if rec.revenue_budget_id.id in data_dict and data_dict[rec.revenue_budget_id.id]['budget_type'] == budget_type.id and data_dict[rec.revenue_budget_id.id]['fiscal_year_id'] == rec.revenue_budget_id.fiscal_year_id.id and data_dict[rec.revenue_budget_id.id]['company_id'] == rec.revenue_budget_id.create_uid.employee_ids.company_id.id:
                    data_dict[rec.revenue_budget_id.id]['total_amount'] += rec.total_amount
                else:
                    data_dict[rec.revenue_budget_id.id]['budget_type'] = budget_type.id
                    data_dict[rec.revenue_budget_id.id]['total_amount'] = rec.total_amount
                    data_dict[rec.revenue_budget_id.id]['fiscal_year_id'] = rec.revenue_budget_id.fiscal_year_id.id
                    data_dict[rec.revenue_budget_id.id]['company_id'] = rec.revenue_budget_id.create_uid.employee_ids.company_id.id
        for recc in data_dict:
            data = tour_treasury_budget.search([
                ('fiscal_year_id', '=', data_dict[recc]['fiscal_year_id']),
                ('department_id', '=', data_dict[recc]['budget_type']),
                ('company_id', '=', data_dict[recc]['company_id'])
            ])
            if data:
                data.update({
                    'budget_amount': data_dict[recc]['total_amount']
                })
            else:
                tour_treasury_budget.create({
                    'company_id': data_dict[recc]['company_id'],
                    'fiscal_year_id': data_dict[recc]['fiscal_year_id'],
                    'department_id': data_dict[recc]['budget_type'],
                    'budget_amount': data_dict[recc]['total_amount']
                    })