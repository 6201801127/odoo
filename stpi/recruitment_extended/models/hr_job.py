from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ApplicantFeesDetails(models.Model):
    _name = 'applicant_fees_details'
    _description = "Applicant fees details"

    job_id = fields.Many2one("hr.job","Job")
    category_ids = fields.Many2many(comodel_name='employee.category',string='Categories')
    amount = fields.Float("Amount")
    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'), ('transgender', 'Transgender')])

class HRJOB(models.Model):
    _inherit = "hr.job"

    fees_applicable = fields.Boolean('Fees Applicable')
    fees_detail_ids =  fields.One2many('applicant_fees_details', 'job_id',string="Fees Details")

    age_required  = fields.Boolean("Age Required")
    min_age  = fields.Integer("Minimum Age")
    max_age = fields.Integer("Maximum Age")

    @api.model
    def create(self, vals):
        is_manager = self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager')
        code = self.env.user.default_branch_id.code
        if not is_manager or is_manager and code.upper().strip() != 'HQ':
            raise ValidationError(_("The requested operation cannot be completed due to security restrictions."
                                    "Please contact your system administrator."))
        return super(HRJOB, self).create(vals)

    @api.onchange('fees_applicable')
    def onchange_fees_applicable(self):
        if not self.fees_applicable:
            self.fees_detail_ids = False

    # rpc method 
    @api.model
    def get_application_fees(self,published_advertisement_id,gender,category_id):
        amount = 0
        print("RPC method called",published_advertisement_id,gender,category_id)

        job_id = self.env['published.advertisement'].browse(int(published_advertisement_id)).job_id
        category = self.env['employee.category'].browse(int(category_id))

        gender_related_fees = job_id.fees_detail_ids.filtered(lambda r:r.gender == gender and category in r.category_ids)

        if not gender_related_fees:
            gender_related_fees = job_id.fees_detail_ids.filtered(lambda r:not r.gender and category in r.category_ids)

        if gender_related_fees:
            amount = gender_related_fees.amount
        return amount
