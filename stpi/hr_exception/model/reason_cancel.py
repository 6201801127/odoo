from odoo import api, models, fields, _


class ReasonCacel(models.Model):
    _inherit = "approvals.list"


    @api.multi
    def approve(self):
        res = super(ReasonCacel, self).approve()
        rc = {
            'name': 'Reason',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('hr_exception.view_reason_wizard').id,
            'res_model': 'reason.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': self.resource_ref._name,
                'default_res_id': self.resource_ref.id,
                'default_action_taken': 'approve'}
        }
        return rc

    @api.multi
    def reject(self):
        res = super(ReasonCacel, self).reject()
        rc = {
            'name': 'Reason',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('hr_exception.view_reason_wizard').id,
            'res_model': 'reason.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': self.resource_ref._name,
                'default_res_id': self.resource_ref.id,
                'default_action_taken': 'reject'}
        }
        return rc