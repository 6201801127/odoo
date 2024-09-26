from odoo import models, fields, api
# from kw_utility_tools import kw_validations
from odoo.addons.kw_utility_tools import kw_validations


class kwemp_identity_docs(models.Model):
    _name = 'kwemp_identity_docs'

    """##integration with DMS"""
    _inherit = [
        'kwemp_identity_docs',
        'kw_dms.hr_emp.integration',
    ]

    content_file = fields.Binary(required=True, string="Upload Document")

    @api.constrains('content_file')
    def validate_identity_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']

        for rec in self:
            kw_validations.validate_file_mimetype(rec.content_file, allowed_file_list)
            kw_validations.validate_file_size(rec.content_file, 4)
