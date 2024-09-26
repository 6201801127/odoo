from odoo import models, fields, api
from odoo.exceptions import  ValidationError

class ProfileAppraisalDetails(models.Model):
    _name='appraisal_details_docs'
    _description = 'Appraisal Details'
    _rec_name = "period_id"



    profile_id = fields.Many2one('kw_emp_profile',ondelete="cascade")
    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    appraisal_doc_attach = fields.Binary(string='Increment Letter')
    file_name = fields.Char()
    increment_id = fields.Many2one('shared_increment_promotion')