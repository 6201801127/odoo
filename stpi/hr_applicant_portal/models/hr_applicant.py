# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request


class HrJob(models.Model):
    _inherit = "hr.job"

    applicant_ref_id = fields.Char("Reference No.", copy=False)
    fee_required = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')
         ], string='Application Fee Required?')


class HRApplicant(models.Model):
    _inherit = "hr.applicant"

    applicant_ref_id = fields.Char("Reference No.", copy=False)
    is_applicable_fee = fields.Selection([("Yes", "Yes"),
                                        ("No", "No")], string="Is Fee Applicable", copy=False, default="No")
    applicable_fee = fields.Float("Applicable Fee (If Yes)", copy=False)
    profile_image = fields.Binary("Profile Image", copy=False)
    other_documents = fields.Binary("Other Document", copy=False)
    other_documents_filename = fields.Char("Other Document Filename")
    signature = fields.Binary("Signature", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('applicant_ref_id', 'New') == 'New':
            vals['applicant_ref_id'] = self.env['ir.sequence'].next_by_code('hr.applicant') or 'New'
        result = super(HRApplicant, self).create(vals)
        return result
