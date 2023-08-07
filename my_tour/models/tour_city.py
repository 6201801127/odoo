# *******************************************************************************************************************
#  File Name             :   tour_city.py
#  Description           :   This is a master model which is used to keep all records related to tour city
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# ******************************************************************************************************************

import re
from odoo import models, fields, api


class TourCity(models.Model):
    _name = "bsscl.tour.city"
    _description = "Tour City"
    _order = "name asc"
    _rec_name='name'

    country_id = fields.Many2one("res.country", "Country / देश", required=True)
    name = fields.Char(string='City Name / शहर का नाम', required=True)
    ha_eligible = fields.Boolean("Eligible For Hardship Allowance / कठिनाई भत्ता के लिए पात्र")
    eligibility_percent = fields.Integer("Percentage Of Eligibility / पात्रता का प्रतिशत")
