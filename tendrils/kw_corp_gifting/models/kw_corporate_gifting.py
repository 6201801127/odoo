# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CorporateGifting(models.Model):
    _name='kw_corporate_gifting'
    _description="Corporate Gifting"
    _rec_name = "occasion_id"


    occasion_id = fields.Many2one('kw_occasion_master', string='Occasion')
    year = fields.Char('Year')
    gifting_guest_lines = fields.One2many('kw_corporate_gifting_guest_line','gift_id',string="Guest Details")

class CorporateGiftingLine(models.Model):
    _name='kw_corporate_gifting_guest_line'
    _description="Corporate Gifting Guest"

    occasion_id = fields.Many2one('kw_occasion_master', string='Occasion')
    guest_id = fields.Many2one('res.partner',string="Guest Name", domain=[('is_guest','=', True)])
    year = fields.Char('Year')
    sbu = fields.Many2one('kw_corp_sbu_master',string='SBU',)
    state_id = fields.Many2one('res.country.state', related='guest_id.state_id',string="State", readonly=1)
    category = fields.Many2one('kw_corp_category_master',string='Category')
    tag = fields.Many2one('kw_corp_tag_master',string='Tag')
    gift_id = fields.Many2one('kw_corporate_gifting',string="Gift Id")
    designation = fields.Char(related='guest_id.function',string='Designation', readonly=1)
    organisation = fields.Many2one('kw_corp_organization_master',related='guest_id.organisation',string='Organisation', readonly=1)
    address = fields.Char(related='guest_id.address',string='Address', readonly=1)
    tel = fields.Char('Tel',related='guest_id.phone', readonly=1)
    delivery_at = fields.Char('Delivery at')
    location = fields.Char(related='guest_id.street2',string='Location',)
    gift_details = fields.Many2one('kw_corp_gift_master',string='Gift Details')
    delivered_by = fields.Many2one('kw_corp_delivery_master',string="Delivery By")
    created_on = fields.Date('Date',default=fields.Date.context_today)

    @api.onchange('guest_id')
    def onchange_guest_id(self):
        for rec in self:
            rec.state_id = self.guest_id.state_id.id
            rec.designation = self.guest_id.function
            rec.organisation = self.guest_id.organisation.id
            rec.address = self.guest_id.street if self.guest_id.street else ""+" "+self.guest_id.street2 if self.guest_id.street2 else ""+" "+self.guest_id.city if self.guest_id.city else ""+" "+self.guest_id.state_id.name if self.guest_id.state_id else ""+" "+self.guest_id.zip if self.guest_id.zip else ""+" "+self.guest_id.country_id.name if self.guest_id.country_id else ""
            rec.tel = self.guest_id.phone
            rec.location = self.guest_id.street2
            rec.delivered_by = self.guest_id.delivery_boy.id

    @api.model
    def create(self, values):
        res = super(CorporateGiftingLine, self).create(values)
        if values.get('delivered_by'):
            res.guest_id.write({'delivery_boy': values.get('delivered_by')})
        return res