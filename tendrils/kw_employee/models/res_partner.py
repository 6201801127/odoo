# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner_in(models.Model):
    _inherit = "res.partner"

    office_prefix = fields.Char(string=u'Office Prefix', help=u"Prefix for Employee Code", max="10")

    kw_location_id = fields.Integer(string='Tendrils Location ID')
    kw_office_id = fields.Integer(string='Tendrils Office Co-ordinate ID')

    def _get_name(self):
        """ Utility method to allow name_get to be overridden without re-browse the partner """
        partner = self
        name = partner.name or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])[
                            'type']['selection'])[partner.type]
            if not partner.is_company:
                name = "%s, %s" % (
                    partner.commercial_company_name or partner.parent_id.name, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        if self._context.get('show_city_country'):
            city = partner.city or ""
            country = partner.country_id.name if partner.country_id else ""
            name = city+"\n"+country if any([city,country]) else name
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name
