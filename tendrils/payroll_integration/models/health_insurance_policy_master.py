from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime


class HealthInsurancePolicyMaster(models.Model):
    _name = 'health_insurance_policy_master'
    _description = 'Health Insurance Policy Master'
    _rec_name = 'policy_number'

    policy_number = fields.Char(string="Policy Number")
    policy_type = fields.Selection([('health', 'Health'), ('accidental', 'Accidental')], string='Policy Type')
    vendor_name = fields.Char(string="Vendor Name")
    sum_assured_amount = fields.Char(string="Sum Assured Amount")
    validity_upto = fields.Date(string="Validity Upto")
    spoc_contact = fields.One2many('health_insurance_policy_spoc','policy_id',string="SPOC Contact")
    toll_free_number = fields.Char(string="Toll Free Number")
    claim_form_attachment = fields.Binary(string="Claim Form", attachment=True)
    file_name = fields.Char("File Name", track_visibility='onchange')
    benefits = fields.Html(string="Benefits")
    attachment_id = fields.Char(
        compute='_compute_attachment_id', string="Attachments")

    def _compute_attachment_id(self):
        for policy in self:
            attachment_id = self.env['ir.attachment'].search(
                [('res_id', '=', policy.id), ('res_model', '=', 'health_insurance_policy_master'), ('res_field', '=', 'claim_form_attachment')]).id
            policy.attachment_id = attachment_id

class HealthInsurancePolicySPOC(models.Model):
    _name = 'health_insurance_policy_spoc'
    _description = 'Health Insurance Policy SPOC Contacts'

    policy_id = fields.Many2one('health_insurance_policy_master',string="Policy Master")
    spoc_name = fields.Char(string="Name")
    spoc_contact_no = fields.Char(string="Contact No")
