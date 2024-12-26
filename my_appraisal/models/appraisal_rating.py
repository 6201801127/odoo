# *******************************************************************************************************************
#  File Name             :   appraisal_rating.py
#  Description           :   This is a model which is used to configure rating of appraisal
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   10-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import fields, models, api, _ 

class AppraisalGrade(models.Model):
    _name = "appraisal.rating"
    _description = "Appraisal Grade Model"

    from_int = fields.Integer(string='From')
    to_int = fields.Integer(string='To')
    name = fields.Char(string="Name")
