# *******************************************************************************************************************
#  File Name             :   bsscl_tour_da.py
#  Description           :   This is a master model which is used to keep all Tour DA Category
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
import re
from odoo import models, fields, api


class TourDaCategory(models.Model):
    _name = "bsscl.tour_da"
    _description = "Tour DA Category"
    _rec_name ='name'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have DA Category with the same name ! / आपके पास समान नाम वाली डीए श्रेणी नहीं हो सकती!'),
    ]
    name = fields.Char('DA Category / डीए श्रेणी', required=True)
    percentage = fields.Integer('Percentage / प्रतिशतता', required=True)