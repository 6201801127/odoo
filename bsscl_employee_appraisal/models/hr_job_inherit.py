# *******************************************************************************************************************
#  File Name             :   hr_job_inherit.py
#  Description           :   This is a model which is used to inherit hr job 
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   10-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import models, fields, api, _ 

class HrJobInherit(models.Model):
    _inherit ="hr.job"

    template_id = fields.Many2one(comodel_name="appraisal.template")