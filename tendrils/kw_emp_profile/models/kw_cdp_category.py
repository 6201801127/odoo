from odoo import models, fields, api
from odoo.exceptions import ValidationError


class hr_job_cdp_category(models.Model):
    _name = "hr_job_cdp_category_master"
    _description = "hr job cdp category"
    _rec_name = "name"

    name = fields.Char(string="Name", required="True")
    designations = fields.Many2many('hr.job', 'job_cdp_category_master_rel', string='Designations', required="True")
