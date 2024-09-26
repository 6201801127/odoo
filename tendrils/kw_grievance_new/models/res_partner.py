from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    grievance_ticket_ids = fields.One2many(
        comodel_name="grievance.ticket",
        inverse_name="partner_id",
        string="Related Grievance",
    )

    grievance_ticket_count = fields.Integer(
        compute="_compute_grievance_ticket_count", string="Grievance count"
    )

    grievance_ticket_active_count = fields.Integer(
        compute="_compute_grievance_ticket_count", string="Grievance active count"
    )

    grievance_ticket_count_string = fields.Char(
        compute="_compute_grievance_ticket_count", string="Grievances"
    )

    def _compute_grievance_ticket_count(self):
        for record in self:
            ticket_ids = self.env["grievance.ticket"].search(
                [("partner_id", "child_of", record.id)]
            )
            record.grievance_ticket_count = len(ticket_ids)
            record.grievance_ticket_active_count = len(
                ticket_ids.filtered(lambda ticket: not ticket.stage_id.closed)
            )
            count_active = record.grievance_ticket_active_count
            count = record.grievance_ticket_count
            record.grievance_ticket_count_string = (
                "{} / {}".format(count_active, count)
            )

    def action_view_grievance_tickets(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "grievance.ticket",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            "context": self.env.context,
        }
