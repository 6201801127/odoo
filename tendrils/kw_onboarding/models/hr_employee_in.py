# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class hr_employee_in(models.Model):
    _inherit = 'hr.employee'

    mrf_reference_no = fields.Char("MRF reference", compute='_get_mrf_reference')

    @api.depends('onboarding_id')
    def _get_mrf_reference(self):
        for rec in self:
            rec.mrf_reference_no = rec.onboarding_id.reference_no


#     state = fields.Selection(
#         [('1', 'Profile Created'), ('2', 'Environment Mapping'), ('3', 'Environment Config'), ('4', 'Approved')],
#         required=True, default='1')

#     @api.multi
#     def button_take_action(self):
#         # for rec in self:
#         #     rec.write({'state': '2'})
#         return True

class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    kw_enrollment_id = fields.Many2one('kwonboard_enrollment', string="Enrollment Ref#")
