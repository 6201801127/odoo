"""
Module containing the Partner model for extending the res.partner model in Odoo.

This module imports necessary dependencies such as fields and models from Odoo.
The Partner class extends the res.partner model and adds additional fields and functionalities related to partners.

Example:
    This module is used to define the Partner model, which inherits from the res.partner model and adds
    one-to-many relationships with helpdesk tickets.

Usage:
    This module should be imported and used within the Odoo environment for extending partner functionality
    and managing relationships with helpdesk tickets.
"""
from odoo import fields, models


class Partner(models.Model):
    """
    Model class representing partners in the system, inheriting from res.partner.

    This class extends the res.partner model to include additional fields and functionalities.
    """
    _inherit = "res.partner"

    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="partner_id",
        string="Related tickets",
    )

    helpdesk_ticket_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Ticket count"
    )

    helpdesk_ticket_active_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Ticket active count"
    )

    helpdesk_ticket_count_string = fields.Char(
        compute="_compute_helpdesk_ticket_count", string="Tickets"
    )

    def _compute_helpdesk_ticket_count(self):
        for record in self:
            ticket_ids = self.env["helpdesk.ticket"].search(
                [("partner_id", "child_of", record.id)]
            )
            record.helpdesk_ticket_count = len(ticket_ids)
            record.helpdesk_ticket_active_count = len(
                ticket_ids.filtered(lambda ticket: not ticket.stage_id.closed)
            )
            count_active = record.helpdesk_ticket_active_count
            count = record.helpdesk_ticket_count
            record.helpdesk_ticket_count_string = (
                "{} / {}".format(count_active, count)
            )

    def action_view_helpdesk_tickets(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "helpdesk.ticket",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            "context": self.env.context,
        }
