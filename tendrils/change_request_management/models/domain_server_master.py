"""
Module Name: KwDomainServerConfiguration

Description: This module contains a model for managing server domain configurations for change requests in Kwantify.
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import datetime



class KwDomainServerConfiguration(models.Model):
    """
    Model class for CR server domain Configuration in Kwantify.
    """
    _name = "kw_cr_domain_server_configuration"
    _description = "CR server domain Configuration"
    _rec_name = "domain_name"

    def check_expiry_status(self):
        today = datetime.datetime.now().date()
        ten_days_to_come = today + datetime.timedelta(days=10)
        thirty_days_to_come = today + datetime.timedelta(days=30)
        for rec in self:
            # print('today >>> ', rec.expiry_date, today, ten_days_to_come, thirty_days_to_come)
            if rec.expiry_date and today < rec.expiry_date < ten_days_to_come:
                rec.expiry_status = 'c'
            elif rec.expiry_date and today < rec.expiry_date < thirty_days_to_come:
                rec.expiry_status = 'b'
            elif rec.expiry_date and today >= rec.expiry_date:
                rec.expiry_status = 'a'


    domain_name = fields.Char(string="Domain Name", required=True)
    client_type = fields.Selection(string="Client Type", selection=[('Active', 'Active'), ('Passive', 'Passive')])
    project_id = fields.Many2one('project.project', string="Project Name")
    project_code = fields.Char(string="Project Code", related="project_id.code")
    client_name = fields.Char(string="Client Name")
    registaration_date = fields.Date(string="Registration Date")
    renewal_date = fields.Date(string="Renewal Date")
    registration_at = fields.Many2one('registration_master_config', string="Registration At")
    domain_status = fields.Selection(string="Domain Status", selection=[('Active', 'Active'), ('Expired', 'Expired')])
    server_name_id = fields.Many2one('kw_cr_server_configuration', string="Server Name")
    mail_server = fields.Char(string="Mail Server")
    contact_type = fields.Selection(string="Contact Type", selection=[('Existing', 'Existing'), ('New', 'New')])
    contact_person = fields.Many2one('hr.employee')
    expiry_date = fields.Date(string="Expiry Date")
    expiry_status = fields.Char(string="Expiry Status", compute="check_expiry_status")
    valid_upto = fields.Date(string="Valid Upto")
    sub_domain = fields.One2many('kw_cr_sub_domains', 'domain_id', substring="Sub Domain")
    domain_serv_bill_ids = fields.One2many('kw_domain_bill', 'domain_server_bill_id', string="Domain Billing")
    reg_contact_person = fields.Char(string="Contact Person", related="registration_at.reg_contact_person")
    reg_address = fields.Text(string="Address", related="registration_at.reg_address")
    reg_telephone = fields.Char(strung="Telephone", related="registration_at.reg_telephone")
    reg_mobile_no = fields.Char(string="Mobile No", related="registration_at.reg_mobile_no")
    reg_company = fields.Char(string="Company", related="registration_at.reg_company")

    @api.multi
    def check_domain_bill_details(self):
        form_view_id = self.env.ref('change_request_management.kw_domain_bill_details_form').id
        tree_view_id = self.env.ref('change_request_management.kw_domain_bill_details_list').id
        return {
            'name': 'Bill Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'kw_domain_bill_details',
            'target': 'self',
            'domain': [('domain_name', '=', self.domain_name), ('client_name', '=', self.client_name)],
        }

    # @api.constrains('sub_domain', 'domain_name')
    # def validation_defects(self):
    #     if not self.sub_domain.ids:
    #         raise ValidationError("Warning! Enter at least One Sub domain Details.")

    # @api.constrains('domain_name', 'domain_serv_bill_ids')
    # def get_billing_details_domain(self):
    #     if not self.domain_serv_bill_ids.ids:
    #         raise ValidationError("Warning! Enter at least One Bill details.")
        # if self.domain_name:
        #     print(self.domain_serv_bill_ids,"=================================domain=======")
        # if self.domain_serv_bill_ids:

    @api.onchange('expiry_date')
    def _onchange_expiry_date(self):
        if self.expiry_date:
            self.valid_upto = self.expiry_date
            self.renewal_date = self.valid_upto - datetime.timedelta(days=1)


class KwCRSubDomain(models.Model):
    """
    Model class for CR Sub Domain in Kwantify.
    """
    _name = "kw_cr_sub_domains"
    _description = "CR Sub Domain"
    _rec_name = "type_id"

    name = fields.Char(string="Value")
    domain_id = fields.Many2one('kw_cr_domain_server_configuration')
    type_id = fields.Many2one('kw_domain_dns_type_master', substring="Sub Domain")


class kwDomainRegistrationConfig(models.Model):
    """
    Model class for CR Registration Configuration.
    """
    _name = "registration_master_config"
    _description = "CR Registration configuration"
    _rec_name = "registration_name"

    registration_name = fields.Char(string="Registration Name")
    registration_code = fields.Char(string="Code")
    reg_contact_person = fields.Char(string="Contact Person")
    reg_address = fields.Text(string="Address")
    reg_telephone = fields.Char(strung="Telephone")
    reg_mobile_no = fields.Char(string="Mobile No")
    reg_company = fields.Char(string="Company")
