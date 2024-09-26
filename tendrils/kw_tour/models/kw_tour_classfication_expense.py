# -*- coding: utf-8 -*-
from odoo import models, fields


class TourClassificationExpense(models.Model):
    _name = "kw_tour_classification_expense"
    _description = "Tour Classification Expense"
    _rec_name = "expense_type_id"

    classification_id = fields.Many2one("kw_tour_classification_type", string='Classification', required=True,
                                        ondelete="cascade")
    expense_type_id = fields.Many2one("kw_tour_expense_type", string="Expense Type", required=True, domain=[
        ('code', 'not in', ['hardship allowance', 'hardship', 'Hardship'])])
    employee_level_id = fields.Many2many("kw_grade_level", string='Employee Level')
    employee_grade_id = fields.Many2many("kwemp_grade_master", string='Employee Grade')
    currency_type_id = fields.Many2one("res.currency", string="Currency Type",
                                       required=True)
    amount = fields.Integer("Amount", required=True)
