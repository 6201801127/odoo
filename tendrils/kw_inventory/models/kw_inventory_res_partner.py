# import re
# from datetime import date
# from odoo.exceptions import ValidationError
from odoo import models, fields, api


class kw_res_partner(models.Model):
    _inherit = "res.partner"

    # company_type = fields.Selection(string='Company Type',
    #     selection=[('person', 'Individual'), ('company', 'Company'),('Proprietorship','Proprietorship'),('Partnership','Partnership')],
    #     compute='_compute_company_type', inverse='_write_company_type')
    business_operation = fields.Selection(
        string='Registration Type',
        selection=[('1', 'Only in India'), ('2', 'Other Countries')]
    )
    pan = fields.Char(string="PAN")
    average_turnover = fields.Char(string="Average Turnover")
    employee_strength = fields.Char(string="Employee Strength")
    msme_reg_no = fields.Char(string="MSME Regd No.")
    epf_reg_no = fields.Char(string="EPF Regd No.")
    esi_reg_no = fields.Char(string="ESI Regd No.")
    labour_license_no = fields.Char(string="Labour License No.")
    partnership_year = fields.Char(string="Partnership Year in Business")
    tan = fields.Char(string="TAN")

    director_name = fields.Char(string="Director Full Name")
    director_designation = fields.Char(string="Director Designation")
    director_email = fields.Char(string="Director Email")
    director_mobile = fields.Char(string="Director Mobile No")
    director_alternative_no = fields.Char(string="Director Alternative No.")

    first_key_person_name = fields.Char(string="First Key Person Full Name")
    first_key_person_designation = fields.Char(string="First Key Person Designation")
    first_key_person_email = fields.Char(string="First Key Person Email")
    first_key_person_mobile = fields.Char(string="First Key Person Mobile No")
    first_key_person_alternative_no = fields.Char(string="First Key Person Alternative No.")
    same_as_director = fields.Boolean(string="Same as Promoter/Director")

    second_key_person_name = fields.Char(string="Second Key Person Full Name")
    second_key_person_designation = fields.Char(string="Second Key Person Designation")
    second_key_person_email = fields.Char(string="Second Key Person Email")
    second_key_person_mobile = fields.Char(string="Second Key Person Mobile No")
    second_key_person_alternative_no = fields.Char(string="Second Key Person Alternative No.")
    same_as_first_key_person = fields.Boolean(string="Same as First Key Person")

    pan_doc = fields.Binary(string="PAN Doc")
    gst_doc = fields.Binary(string="GST Doc")
    tan_doc = fields.Binary(string="TAN Doc")
    reg_no_doc = fields.Binary(string="Registration No Doc")
    bank_account_doc = fields.Binary(string="Bank Account Doc")

    @api.onchange('same_as_director')
    def _onchange_same_as_director(self):
        for record in self:
            if record.same_as_director:
                record.first_key_person_name = record.director_name
                record.first_key_person_designation = record.director_designation
                record.first_key_person_email = record.director_email
                record.first_key_person_mobile = record.director_mobile
                record.first_key_person_alternative_no = record.director_alternative_no
            else:
                record.first_key_person_name = False
                record.first_key_person_designation = False
                record.first_key_person_email = False
                record.first_key_person_mobile = False
                record.first_key_person_alternative_no = False

    @api.onchange('same_as_first_key_person')
    def _onchange_same_as_first_key_person(self):
        for record in self:
            if record.same_as_first_key_person:
                record.second_key_person_name = record.first_key_person_name
                record.second_key_person_designation = record.first_key_person_designation
                record.second_key_person_email = record.first_key_person_email
                record.second_key_person_mobile = record.first_key_person_mobile
                record.second_key_person_alternative_no = record.first_key_person_alternative_no
            else:
                record.second_key_person_name = False
                record.second_key_person_designation = False
                record.second_key_person_email = False
                record.second_key_person_mobile = False
                record.second_key_person_alternative_no = False

    # @api.depends('is_company')
    # def _compute_company_type(self):
    #     for partner in self:
    #         partner.company_type = 'company' if partner.is_company else 'person'


class kw_res_partner_bank(models.Model):
    _inherit = "res.partner.bank"

    ifsc_code = fields.Char(related='bank_id.bic')
    addr = fields.Char(related="bank_id.street2")


class kw_res_bank(models.Model):
    _inherit = "res.bank"

    bic = fields.Char('Bank Identifier Code(IFSC Code)', index=True, help="Sometimes called BIC or Swift.")
