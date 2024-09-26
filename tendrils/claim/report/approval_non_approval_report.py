"""
    This module provides functionality related to approval and non-approval reports.
"""
from odoo import models, fields, api, tools
from datetime import date, datetime, time

class approval_non_approval_report(models.Model):
    """
    approval_non_approval_report class

    This class represents approval and non-approval reports.

    """
    _name = 'approval_non_approval_report'
    _auto = False

    code = fields.Char()
    employee_id = fields.Many2one('hr.employee',string='Employee',)
    department_id = fields.Many2one('hr.department')
    division = fields.Many2one('hr.department')
    category_id = fields.Many2one('kw_advance_claim_category',string='Category',)
    amount = fields.Float('Amount')
    action_taken_by = fields.Many2one('hr.employee',string='Action Taken By',)
    ceo_other_approval = fields.Char()
    claim_id = fields.Many2one('kw_claim')




    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE or REPLACE VIEW {self._table} AS (
                WITH CEO_Employees AS (
                    SELECT id
                    FROM hr_employee
                    WHERE parent_id IS NULL
                      AND job_id IN (SELECT id FROM hr_job WHERE name = 'Chief Executive Officer')
                )

                SELECT
                    ROW_NUMBER() OVER () AS id,
                    c.code,
                    c.employee_id,
                    c.department_id,
                    c.division,
                    c.category_id,
                    c.amount,
                    l.action_taken_by,
                    CASE
                        WHEN l.state IN ('Approved', 'Auto Approved') AND l.action_taken_by IN (SELECT id FROM CEO_Employees) AND c.state IN ('approved','verified', 'disbursed') THEN 'BY CEO'
                        WHEN l.state IN ('Approved', 'Auto Approved') AND c.state IN ('approved','verified', 'disbursed') THEN 'BY OTHER'
                        ELSE NULL
                    END AS ceo_other_approval,
                    c.id as claim_id
                FROM
                    kw_claim c
                JOIN
                    claim_log_details l ON c.id = l.claim_id
                WHERE
                    l.state IN ('Approved', 'Auto Approved') AND c.state IN ('approved','verified','disbursed')
            )
        """)

    def action_button_view_form(self):
        view_id = self.env.ref('claim.kw_claim_view_form').id
        return {
            'name': 'Claim',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_claim',
            'view_id': view_id,
            'res_id': self.claim_id.id,
            'target': 'self',
            'context': {'edit': False, 'create': False, 'delete': False}
        }