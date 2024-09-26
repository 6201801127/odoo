from odoo import models, fields, api

class PortletMaster(models.Model):
    _name = "portlet_master"
    _description = "Portlet Master"

    name = fields.Char(string="Name", required=True, size=50, help="Only 50 character allowed")
    portlet_code = fields.Char("code", required=True, size=50, help="Only 50 character allowed")