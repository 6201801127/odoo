from odoo import api, fields, models, tools, _


class Project(models.Model):
    _inherit = 'project.project'

    def open_tickets(self):
        tree_view_id = self.env.ref('gts_ticket_management.support_tickets_view_tree').id
        form_view_id = self.env.ref('gts_ticket_management.support_ticket_view_form').id
        kanban_view_id = self.env.ref('gts_ticket_management.support_ticket_view_kanban').id
        return {
            'name': _('Tickets'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban')],
            'res_model': 'support.ticket',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_partner_name': self.partner_id.name, 'default_partner_email': self.partner_email,
                        'default_is_from_project': True}
        }

    def _get_ticket_count(self):
        ticket_obj = self.env['support.ticket']
        for record in self:
            record.ticket_count = ticket_obj.search_count([('project_id', '=', record.id)])

    ticket_count = fields.Integer(compute='_get_ticket_count')
