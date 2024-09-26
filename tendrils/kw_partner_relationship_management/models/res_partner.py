# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwResPartner(models.Model):
    _inherit = "res.partner"

    branch_name = fields.Char(string="Branch Name")
    type = fields.Selection(
        selection=[('contact', 'Contact'), ('invoice', 'Invoice address'), ('delivery', 'Shipping address'),
                   ('other', 'Other address'), ('private', 'Private Address'), ('branch', 'Branch address')])
    yoi = fields.Date(string='Year Of Incorporation')
    partner_type_id = fields.Many2one(string='Partner Type', comodel_name='kw_partner_type_master', ondelete='restrict')
    partner_type_alias = fields.Char(string="Alias", related="partner_type_id.alias")
    maf = fields.Selection(string="Manufacturer Authorization Form (MAF)", selection=[('Yes', 'Yes'), ('No', 'No')])
    revenue = fields.Float(string="Revenue", required=False)
    is_partner = fields.Boolean(string='Is a Partner',
                                default=lambda self: self.env.context.get('partner_profile', False))
    # branch_ids = fields.Many2many('kw_res_branch',string='Branch/Branches')
    certification_ids = fields.Many2many('kw_certification_master', string='Certifications (ISO, CMMI and others)')
    geography_of_business = fields.Many2many('res.country', string='Geographies of Business')
    partnership_area = fields.Text(string='What are the perceived synergy areas in this partnership?',
                                   help='Please Specify Geography , Government Connects , Visible Opportunity with near closure , Opportunity Build Synergies.')
    product_services_ids = fields.One2many('kw_partner_master_rel', 'partner_rel_id', string='Product & Services')
    employee_strength = fields.Char(string="Employee Strength")
    pan = fields.Char(string="PAN")
    director_name = fields.Char(string="Director Full Name")
    director_designation = fields.Char(string="Director Designation")
    director_email = fields.Char(string="Director Email")
    director_mobile = fields.Char(string="Director Mobile No")
    director_alternative_no = fields.Char(string="Director Alternative No.")
    same_as_director = fields.Boolean(string="Same as Promoter/Director")

    first_key_person_alternative_no = fields.Char(string="First Key Person Alternative No.")
    same_as_first_key_person = fields.Boolean(string="Same as First Key Person")
    second_key_person_alternative_no = fields.Char(string="Second Key Person Alternative No.")
    first_key_person_name = fields.Char(string="First Key Person Full Name")
    first_key_person_designation = fields.Char(string="First Key Person Designation")
    first_key_person_email = fields.Char(string="First Key Person Email")
    first_key_person_mobile = fields.Char(string="First Key Person Mobile No")

    second_key_person_name = fields.Char(string="Second Key Person Full Name")
    second_key_person_designation = fields.Char(string="Second Key Person Designation")
    second_key_person_email = fields.Char(string="Second Key Person Email")
    second_key_person_mobile = fields.Char(string="Second Key Person Mobile No")

    average_turnover = fields.Char(string="Average Turnover")

    service_offering_ids = fields.Many2many(
        string='Service Offering',
        comodel_name='kw_partner_tech_service_master',
        relation='kw_partner_service_master_res_partner_rel',
        column1='service_id',
        column2='partner_id',
    )

    tech_ids = fields.Many2many(
        string='Technologies',
        comodel_name='kw_partner_tech_service_master',
        relation='kw_partner_tech_master_res_partner_rel',
        column1='tech_id',
        column2='partner_id',
    )

    industy_domain_ids = fields.Many2many(
        string='Industries/Domains',
        comodel_name='res.partner.industry',
    )

    date_of_incorporation = fields.Date(string='Date of Incorporation', )
    incorporation_type = fields.Selection(string='Incorporation Type',
                                          selection=[('1', 'Public Ltd'), ('2', 'Pvt Ltd'), ('3', 'Partnership')])
    """##START : OEM Fields"""
    products_focus_ids = fields.Many2many(
        string='Products to Focus',
        comodel_name='kw_partner_tech_service_master',
        relation='kw_prm_product_master_res_partner_rel',
        column1='product_id',
        column2='partner_id',
    )
    geo_regions_to_focus = fields.Many2many(string='Geo/Regions to Focus',
                                            comodel_name='res.country.state',
                                            relation='kw_prm_geo_focus_res_partner_rel',
                                            column1='state_id',
                                            column2='partner_id',
                                            )
    """##END : OEM Fields"""
    experience_govt_sector = fields.Integer(string="Experience in Govt. Sector (in years)")

    partnership_year = fields.Char(string="Partnership Year in Business")
    msme_reg_no = fields.Char(string="MSME Regd No.")
    epf_reg_no = fields.Char(string="EPF Regd No.")
    esi_reg_no = fields.Char(string="ESI Regd No.")
    labour_license_no = fields.Char(string="Labour License No.")
    tan = fields.Char(string="TAN")

    pan_doc = fields.Binary(string="PAN Doc")
    pan_file_name = fields.Char("PAN File Name")
    gst_doc = fields.Binary(string="GST Doc")
    gst_file_name = fields.Char("GST File Name")
    tan_doc = fields.Binary(string="TAN Doc")
    tan_file_name = fields.Char("TAN File Name")
    reg_no_doc = fields.Binary(string="Registration No Doc")
    reg_file_name = fields.Char("Reg File Name")
    bank_account_doc = fields.Binary(string="Bank Account Doc")
    bank_account_file_name = fields.Char("Bank Account File Name")
    nda = fields.Binary(string="Non-Disclosure Agreement")
    nda_file_name = fields.Char("NDA File Name")
    msa = fields.Binary(string='Mutual Service Agreement')
    msa_file_name = fields.Char("MSA File Name")
    is_nda_uploaded = fields.Char(string="Is NDA Uploaded ?", compute='_check_nda')
    is_decision_making_authority = fields.Boolean(string="Is Decision Making Authority")

    secondary_mail = fields.Char(string="Secondary Email")
    secondary_phone = fields.Char(string="Secondary Phone")

    linked_in_id = fields.Char(string='LinkedIn Id')
    skype_id = fields.Char(string='Skype Id')
    oppertunity_id = fields.Many2many('crm.lead', string="Project/Opportunity")

    service_offering_ids_graph = fields.Char(related='service_offering_ids.name', store=True, string='Service Offering')
    tech_ids_graph = fields.Char(related='tech_ids.name', store=True, string='Technologies')
    industy_domain_ids_graph = fields.Char(related='industy_domain_ids.name', store=True, string='Industries')
    geography_of_business_graph = fields.Char(related='geography_of_business.name', store=True,
                                              string='Area Of Business')
    oppertunity_id_graph = fields.Char(related='oppertunity_id.name', store=True, string='Project/Opportunity')
    oem_partnership_id = fields.Char(string="OEM Partnership ID")
    date_of_partnership = fields.Date(string="Date of Partnership")
    validate_till_date = fields.Date(string="Validate till date")
    partner_portal_link = fields.Char(string="Partner Portal Link")
    partner_login_id = fields.Char(string="Partner Portal Log-In ID")
    vendor_code = fields.Char(string="Vendor Code", )
    contact_designation = fields.Char(string="Designation")
    industry_category_ids = fields.One2many('industry_category_partner_expertise', 'partner_rel_id', string='Industry Category & Expertise')
    nda_signoff_date = fields.Date(string="NDA Signoff Date")
    msi_signoff_date = fields.Date(string="MSI Signoff Date")
    csm_authorized_first_person = fields.Char(string="CSM Authorized Person-1")
    csm_authorized_first_person_email = fields.Char(string="CSM Authorized Person-1 Email")
    csm_authorized_first_person_mobile = fields.Char(string="CSM Authorized Person-1 Mobile")
    csm_authorized_second_person = fields.Char(string="CSM Authorized Person-2")
    csm_authorized_second_person_email = fields.Char(string="CSM Authorized Person-2 Email")
    csm_authorized_second_person_mobile = fields.Char(string="CSM Authorized Person-2 Mobile")
    # oppertunity_id_graph = fields.Char(related='oppertunity_id.name', store=True, string='Project/Oppertunity')

    # @api.model
    # def create(self, vals):
    #     if self.env.context.get('partner_profile', False):
    #         mass_mailing_contact = self.env['mail.mass_mailing.contact'].sudo()
    #         mailing_list_obj = self.env['mail.mass_mailing.list'].sudo().search(
    #             [('name', 'ilike', 'Partner Profiling')])

    #         values = {
    #             'name': vals.get('name'),
    #             'email': vals.get('email'),
    #             'subscription_list_ids': [[0, 0, {
    #                 'list_id': mailing_list_obj.id,
    #             }]]
    #         }

    #         mass_mailing_contact.create(values)

    #     res = super().create(vals)

    #     return res

    # @api.model
    # @api.constrains('revenue')
    # def _check_revenue(self):
    #     if self.env.context.get('partner_profile'):
    #         if self.revenue <= 0:
    #             raise ValidationError("Revenue should be greater than zero")

    @api.multi
    def _check_nda(self):
        for record in self:
            if record.nda:
                record.is_nda_uploaded = 'Yes'
            else:
                record.is_nda_uploaded = 'No'

    @api.multi
    def btn_view_details(self):
        view_id = self.env.ref('kw_partner_relationship_management.view_partner_profiling_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'res_id': self.id,
        }
        return action

    @api.onchange('is_partner')
    def _onchange_is_partner(self):
        for record in self:
            if not record.is_partner:
                record.partner_type_id = False
                record.revenue = 0.0

    @api.onchange('partner_type_id')
    def _onchange_partner_type_id(self):
        for record in self:
            if record.partner_type_id and record.partner_type_id not in ['oem', 'bd']:
                record.date_of_incorporation = False
                record.incorporation_type = False

            if record.partner_type_id and record.partner_type_id not in ['oem']:
                record.products_focus_ids = False
                record.geo_regions_to_focus = False

    # @api.constrains('name')
    # def name_constratints(self):
    #     if not re.findall('[A-Za-z0-9]', self.name):
    #         raise ValidationError("Invalid Company Name")

    @api.multi
    def btn_view_contacts(self):
        tree_view_id = self.env.ref('kw_partner_relationship_management.view_kw_partner_contact_list').id
        form_view_id = self.env.ref('kw_partner_relationship_management.view_kw_partner_contact_form').id
        action = {
            'name': 'Contact Details',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form,tree',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'target': 'self',
            'domain': [('is_partner', '=', True), ('id', 'in', self.child_ids.ids)],
            'context': {'is_partner': False, 'edit': False, 'create': False, 'partner_profile': True,
                        'check_partner': True}
        }
        return action


import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwResPartnerIndustry(models.Model):
    _inherit = 'res.partner.industry'

    _sql_constraints = [
        ('unique_type_name', 'unique(name)', 'The Industry type already exists')
    ]

    # @api.constrains('name')
    # def name_constratints(self):
    #     if not re.findall('[A-Za-z0-9]', self.name):
    #         raise ValidationError("Invalid Industry Name")

    @api.multi
    def unlink(self):
        partner_rec = self.env['res.partner'].sudo().search([('industy_domain_ids', 'in', self.ids)])
        if partner_rec:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        result = super(KwResPartnerIndustry, self).unlink()
        self.env.user.notify_success("Industry record deleted successfully.")
        return result
