from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools.translate import _


class Project(models.Model):
    _inherit = 'project.project'

    def open_contracts(self):
        tree_view_id = self.env.ref('contract.view_partner_contract_tree').id
        form_view_id = self.env.ref('contract.view_partner_contract_form').id
        kanban_view_id = self.env.ref('contract.view_partner_contract_kanban').id
        pivot_view_id = self.env.ref('contract.view_partner_contract_pivot').id
        return {
            'name': _('Contract'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'partner.contract',
            'domain': [('related_project', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_related_project': self.id, 'default_partner_id': self.partner_id.id,
                        'default_is_from_project': True}
        }

    def _get_contract_count(self):
        contract = self.env['partner.contract']
        for record in self:
            record.contract_count = contract.search_count([('related_project', '=', record.id)])

    contract_count = fields.Integer(compute='_get_contract_count', tracking=True)
