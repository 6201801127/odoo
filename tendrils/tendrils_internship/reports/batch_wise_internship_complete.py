from odoo import models, fields, api, tools

class BatchWiseInternship(models.Model):
    _name = "batch_wise_internship"
    _description = "Batch Wise Internship Report"
    _auto = False
    _order = 'id'

    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year')
    batch_name = fields.Char(string="Batch Name")
    start_date = fields.Date(string='Start Date')
    close_date = fields.Date(string='Close Date')
    batch_stage = fields.Selection([
        ('Draft', 'Draft'), 
        ('Start', 'Start'),
        ('Complete', 'Complete')
    ], string="Stage", default='Draft')
    intern_name = fields.Char(string='Interns')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""
        CREATE OR REPLACE VIEW {self._table} AS (
        SELECT
                row_number() OVER () AS id,
                ltb.financial_year_id AS financial_year_id,
                ltb.batch_name AS batch_name,
                ltb.start_date AS start_date,
                ltb.close_date AS close_date,
                ltb.batch_stage AS batch_stage,
                STRING_AGG(ti.intern_name, ', ') AS intern_name
            FROM lk_training_batch ltb
            LEFT JOIN lk_training_batch_tendrils_internship_rel tbr 
                ON tbr.lk_training_batch_id = ltb.id
            LEFT JOIN tendrils_internship ti 
                ON ti.id = tbr.tendrils_internship_id
            WHERE ltb.batch_stage = 'Complete'
            GROUP BY
                ltb.financial_year_id,
                ltb.batch_name,
                ltb.start_date,
                ltb.close_date,
                ltb.batch_stage
            ORDER BY id

        )
        """
        self.env.cr.execute(query)
