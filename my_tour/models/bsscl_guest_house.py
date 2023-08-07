# *******************************************************************************************************************
#  File Name             :   bsscl_guest_house.py
#  Description           :   This is a master model which is used to keep all records related to guest house
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import models, fields, api


class TourGuesthouseMaster(models.Model):
    _name = 'bsscl.guest.house'
    _description = "Tour Guest House"
    _rec_name='name'

    country_id = fields.Many2one("res.country", "Country Name / देश नाम", required=True)
    name = fields.Char('Guest House Name / अतिथि गृह नाम', required=True)
    address = fields.Text("Address / पता")
    active = fields.Boolean(default=True)