# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ticket_count = fields.Integer("Tickets", compute='_compute_ticket_count')

    def _compute_ticket_count(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])
        groups = self.env['support.ticket'].read_group(
            [('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id'],
        )
        self.ticket_count = 0
        for group in groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.ticket_count += group['partner_id_count']
                partner = partner.parent_id

    def action_open_support_ticket(self):
        action = self.env["ir.actions.actions"]._for_xml_id("gts_ticket_management.support_ticket_action_main_tree")
        action['context'] = {}
        action['domain'] = [('partner_id', 'child_of', self.ids)]
        return action
