from odoo import models, fields, api
from odoo import tools


class LocationWiseReport(models.Model):
    _name = "location_wise_report"
    _description = "Location Wise Report Of Employees"
    _auto = False

    location_id = fields.Many2one('kw_res_branch', string="Location")
    total_employee = fields.Integer('Total Present')
   
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT row_number() over() AS id, 
            job_branch_id as location_id,
            COUNT(*) as total_employee 
            FROM hr_employee
            where active = true
            GROUP BY location_id 
            
        )"""
        self.env.cr.execute(query)
