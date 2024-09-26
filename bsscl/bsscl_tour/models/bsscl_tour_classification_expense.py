# -*- coding: utf-8 -*-
# *******************************************************************************************************************
#  File Name             :   bsscl_tour_classification_expense.py
#  Description           :   This is a master model 
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import models, fields


class TourClassificationExpense(models.Model):
    _name = "bsscl.tour.classification.expense"
    _description = "Tour Classification Expense"
    _rec_name = "expense_type_id"

    expense_type_id = fields.Many2one("bsscl.tour.expense.type", string="Expense Type / व्यय प्रकार", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency Type / मुद्रा प्रकार",
                                       required=True, domain=[('name', 'in', ['INR', 'USD'])])
    amount = fields.Float("Amount / मात्रा", required=True)
    tour_allowance_id = fields.Many2one(comodel_name="bsscl.tour.allowance",string="Tour Allowance / भ्रमण भत्ता")