from odoo import models, fields, api
from odoo.addons.kw_accounting.models.chart_of_accounts import state_list

class StateGSTIN(models.Model):
    _name = 'state_gstin'
    _description = "State GSTIN"

    state_name = fields.Selection(state_list,string="State")
    gstin_no = fields.Char(string="GSTIN")

    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.state_name +' ('+ rec.gstin_no +')')   
            result.append((rec.id, name))
        return result