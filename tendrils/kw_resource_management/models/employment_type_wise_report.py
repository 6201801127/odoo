from odoo import models, fields, api
from odoo import tools


class EmploymentTypeWiseReport(models.Model):
    _name = "employment_type_wise_report"
    _description = "Employment Type Wise Report"
    _auto = False

    type_of_employment = fields.Many2one('kwemp_employment_type', string="Employement Type")
    total_employee = fields.Integer('Count')
   
    @api.model_cr   
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        query = f""" CREATE or REPLACE VIEW {self._table} as (
           
       
         SELECT row_number() over() AS id, 
            employement_type as type_of_employment,
            count(*) as total_employee
            FROM hr_employee        
            group by type_of_employment

             )"""
        self.env.cr.execute(query)


        