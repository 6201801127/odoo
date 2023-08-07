# *******************************************************************************************************************
#  File Name             :   bsscl_tour_travel_expense_details.py
#  Description           :   This is a master model which is used to keep all records related to medical expense
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   18-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import models, fields

class TourtravelExpenseDetails(models.Model):
    _name = 'bsscl.tour.travel.expense.details'
    _description = "Tour Travel Expense Details"

    tour_id = fields.Many2one(string='Tour / यात्रा', required=True, comodel_name='bsscl.tour', ondelete='cascade', )
    tour_settlement_id = fields.Many2one(string='Tour / यात्रा', required=True, comodel_name='tour.settlement', ondelete='cascade', )
    expense_type_id = fields.Many2one("bsscl.tour.expense.type", string="Expense Type / व्यय प्रकार", required=True)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency Type / मुद्रा प्रकार",
                                       required=True, domain=[('name', 'in', ['INR', 'USD'])])
    amount = fields.Float("Amount / मात्रा", required=True)