# -*- coding: utf-8 -*-
# Part of Geotechnosoft. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    support_ticket_target_closed = fields.Float(string='Target Tickets to Close', default=1)
    support_ticket_target_rating = fields.Float(string='Target Customer Rating', default=100)
    support_ticket_target_success = fields.Float(string='Target Success Rate', default=100)

    _sql_constraints = [
        ('target_closed_not_zero', 'CHECK(support_ticket_target_closed > 0)', 'You cannot have negative targets'),
        ('target_rating_not_zero', 'CHECK(support_ticket_target_rating > 0)', 'You cannot have negative targets'),
        ('target_success_not_zero', 'CHECK(support_ticket_target_success > 0)', 'You cannot have negative targets'),
    ]

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        support_ticket_fields = [
            'support_ticket_target_closed',
            'support_ticket_target_rating',
            'support_ticket_target_success',
        ]
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(support_ticket_fields)
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(support_ticket_fields)
        return init_res

    @api.model
    def create(self, vals):
        rec = super(ResUsers, self).create(vals)
        if rec:
            if rec.has_group('gts_groups.group_helpdesk_management_can_create') and not rec.has_group(
                    'gts_ticket_management.group_support_ticket_user'):
                raise ValidationError(_(
                    'Cannot give access of ticket creation until user has access to Support Ticket User or Support Ticket Manager'))
        return rec

    def write(self, vals):
        rec = super(ResUsers, self).write(vals)
        for record in self:
            if record.has_group('gts_groups.group_helpdesk_management_can_create') and not record.has_group(
                    'gts_ticket_management.group_support_ticket_user'):
                raise ValidationError(_(
                    'Cannot give access of ticket creation until user has access to Support Ticket User or Support Ticket Manager'))
        return rec
