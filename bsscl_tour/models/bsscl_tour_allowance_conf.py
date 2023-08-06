# *******************************************************************************************************************
#  File Name             :   bsscl_tour_allowance_conf.py
#  Description           :   This is a master model which is used to keep all records related to Tour allowance
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
import re
from odoo import models, fields, api


class TourAllowanceConf(models.Model):
    _name = 'bsscl.tour.allowance'
    _description = "BSSCL Tour Allowance"
    _rec_name = 'name'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have allowance name with the same name ! / आपके पास एक ही नाम से अलाउंस नाम नहीं हो सकता है!')
    ]
    
    name = fields.Char(string="Name / नाम")
    description = fields.Text(string="Description / विवरण")
    expense_ids = fields.One2many(comodel_name="bsscl.tour.classification.expense", inverse_name="tour_allowance_id", string="Expenses / खर्च")