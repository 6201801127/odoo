from odoo import models, fields, api
from odoo.addons.kw_utility_tools import kw_validations


class kwemp_membership_assc(models.Model):
    _name = 'kwemp_membership_assc'

    """##integration with DMS"""
    _inherit = [
        'kwemp_membership_assc',
        'kw_dms.hr_emp.integration',
    ]

    content_file = fields.Binary(required=True, string="Upload Document")

    @api.constrains('content_file')
    def validate_membership_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

        for rec in self:
            kw_validations.validate_file_mimetype(rec.content_file, allowed_file_list)
            kw_validations.validate_file_size(rec.content_file, 4)
