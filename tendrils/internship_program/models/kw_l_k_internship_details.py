"""
Module: Learning and Knowledge Internship Details

Model for managing training and internship details.
"""

from datetime import date, datetime
from odoo import models, fields, api


class LearningAndKnowledgeInternship(models.Model):
    """    Model representing training and internship details.

    """
    _name = 'lk_batch_internship'
    _description = 'Training and Internship Details'
    _rec_name = 'name'

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    name = fields.Char(string="Name")
    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year',
                                        default=_default_financial_yr, required=True)
    date_of_joining = fields.Date(string="Date of Joining")

    internship_completion_details_ids = fields.One2many('lk_batch_details', 'internship_id',
                                                        string="Internship Details")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string='Status')

    def check_employee_data(self):
        pass
