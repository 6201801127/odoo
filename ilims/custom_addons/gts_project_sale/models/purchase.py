from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Project Name')
    is_from_project = fields.Boolean('From Project')

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        partner_list = []
        if res.analytic_account_id:
            project = self.env['project.project'].search([('analytic_account_id', '=', res.analytic_account_id.id)],
                                                         limit=1)
            if project and project.program_manager_id:
                partner_list.append(project.program_manager_id.partner_id.id)
            if project and project.user_id:
                partner_list.append(project.user_id.partner_id.id)
        new_list = list(set(partner_list))
        res.message_subscribe(partner_ids=new_list)
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


