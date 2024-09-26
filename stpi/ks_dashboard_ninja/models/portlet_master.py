from odoo import models, fields, api

class PortletMaster(models.Model):
    _name = "portlet_master"
    _description = "Portlet Master"

    name = fields.Char(string="Name", required=True)
    portlet_code = fields.Char("code", required=True)