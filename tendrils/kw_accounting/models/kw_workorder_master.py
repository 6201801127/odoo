from odoo import models, fields, api, _
from datetime import date


class KwSalesWorkOrderMasterConfiguration(models.Model):
    
    _name = "kw_sales_workorder_master"
    _description = "Kw Sales WorkOrder Master Configuration"
    _rec_name = 'workorder_code'
    
    
    kw_wo_id = fields.Integer("Tendrils Workorder ID")
    workorder_code = fields.Char("WO Code")
    workorder_name = fields.Char("WO Name")
    wo_issue_date = fields.Date("WO Issue Date")
    account_manager_id = fields.Many2one('hr.employee',"Account Manager")
    wo_status = fields.Integer("WO Status")
    kw_wo_client_id = fields.Integer("WO Client ID")
    
    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.workorder_code +' - '+ rec.workorder_name )   
            result.append((rec.id, name))
        return result