"""
This module provides functionality related to approval and non-approval reports.
"""
from odoo import models, fields, api, tools
from datetime import date, datetime, time

class category_sub_category_report(models.Model):
    """
    This class defines the category_sub_category_report model for generating reports on categories and sub-categories.
    """
    _name = 'category_sub_category_report'
    _auto = False

    employee_id = fields.Many2one('hr.employee',string='Employee',)
    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job',string = 'Designation')
    amount = fields.Float('Amount')
    state = fields.Char('State')
    month = fields.Integer()
    year = fields.Integer()
    category_id = fields.Many2one('kw_advance_claim_category',string='Category',)
    sub_category_ids = fields.Many2one('kw_advance_claim_type')



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
        SELECT 
            ROW_NUMBER() OVER () AS id,
            sc.employee_id AS employee_id,
            sc.department_id AS department_id,
            sc.amount AS amount,
            sc.job_id AS job_id,
            sc.state AS state,
            sc.month AS month,
            sc.year AS year,
            sc.category_id AS category_id,
            (SELECT claim_category_id FROM sub_category_item_amount_config WHERE claim_id = sc.id) AS sub_category_ids
                            
            FROM
                kw_claim sc
            WHERE 
                state = 'disbursed'
           
         )""" % (self._table))