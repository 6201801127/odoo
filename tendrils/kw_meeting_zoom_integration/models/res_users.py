from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # zoom_id = fields.One2many(string='User', comodel_name='kw_zoom_users', inverse_name='user_id', )
    zoom_id = fields.Many2one('kw_zoom_users', string='User')
    zoom_acc_id = fields.Char(related='zoom_id.zoom_id',string='Zoom ID')

    def update_branches_user(self):
        users = self.env['res.users'].search([('branch_ids', '=', False)])
        if users:
            for user in users:
                if user.branch_id:
                    user.write({'branch_ids': [(6, 0, [user.branch_id.id])]})
        return True
