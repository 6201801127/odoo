# *******************************************************************************************************************
#  File Name             :   expense_type.py
#  Description           :   This is a master model which is used to keep all recorde related to expense type in BSSCL
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import models, fields, api, _ 

class BssclExpenseTypeMaster(models.Model):
    _name = "bsscl.tour.expense.type"
    _description = "Tour Expense type model"
    _rec_name='name'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have expense type with the same name ! / आपके पास समान नाम वाला व्यय प्रकार नहीं हो सकता!'),
        ('code_uniq', 'UNIQUE (code)',  'You can not have expense type code with the same name ! / आपके पास समान नाम वाला व्यय प्रकार कोड नहीं हो सकता!')
    ]
    name = fields.Char(string='Expense Type / व्यय प्रकार', required=True)
    code = fields.Char(string="Code / संहिता", required=True)
    description = fields.Text(string="Description / विवरण")
    active = fields.Boolean(string='Active / सक्रिय', default=True)