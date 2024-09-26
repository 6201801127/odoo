from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CvskillsApilog(models.Model):
    _name = 'cv_skills_api_log'
    _description = 'Recruitment CV Parser API Log'
    _rec_name = 'status'
    _order = 'id desc'

    payload = fields.Text(string="Payload")
    response = fields.Text(string="Response")
    ocr = fields.Text(string='OCR')
    status = fields.Char(string='Status')