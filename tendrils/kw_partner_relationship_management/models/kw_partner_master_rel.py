# -*- coding: utf-8 -*-
# ##############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.      
# Create By: Asish Kumar Nayak, On -1st Oct 2020                          #
# ##############################################################################
import re
from odoo import models, fields, api, _


class KwPartnerMasterRel(models.Model):
    _name = 'kw_partner_master_rel'
    _description = 'Maintaining relation between partner and master'

    product_category = fields.Many2one('kw_product_category_master', string='Product Category',
                                       domain="[('active','=',True)]", ondelete='restrict')
    prduct_id = fields.Many2many('kw_product_master', string='Product', domain="[('active','=',True)]")
    sell_in = fields.Many2many('res.partner.industry', string='Sell in (Industry / Sector)',
                               domain="[('active','=',True)]")
    major_client = fields.Many2many('kw_client_master', string='Major clients', domain="[('active','=',True)]")
    additional_info = fields.Text(string='Additional Info',
                                  help="Please provide any additional information that would assist us to know your company better.")
    partner_rel_id = fields.Many2one('res.partner', string='Partner rel Id', ondelete='restrict')


class industry_category_partner_expertise(models.Model):
    _name= 'industry_category_partner_expertise'
    _description = "Industry Category wise Partner's Expertise"

    sell_in = fields.Many2one('res.partner.industry', string='Sell in (Industry / Sector)',
                               domain="[('active','=',True)]")
    additional_info = fields.Text(string='Additional Info',
                                  help="Please provide any additional information that would assist us to know your company better.")
    partner_rel_id = fields.Many2one('res.partner', string='Partner rel Id', ondelete='restrict')
