from odoo import models, fields, api


class kw_handbook_types(models.Model):
    _name = "kw_handbook_type"
    _description = "A model to manage employee handbook type"
    _rec_name = "name"
    _order = "sort_no asc"

    name = fields.Char('Name', required=True)
    code = fields.Char(string="Code", required=True)
    # sequence = fields.Integer(string="Sequence", default=10, required=True, help="Gives the sequence order of types.")
    emp_id = fields.Many2many('hr.employee', string='Employee Name')
    sort_no=fields.Integer("Sequence")

    @api.model
    def create(self, vals):
        record = super(kw_handbook_types, self).create(vals)
        if record:
            self.env.user.notify_success(message='Handbook Type created successfully.')
        else:
            self.env.user.notify_danger(message='Handbook Type creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_handbook_types, self).write(vals)
        if res:
            self.env.user.notify_success(message='Handbook Type updated successfully.')
        else:
            self.env.user.notify_danger(message='Handbook Type update failed.')
        return res

    @api.multi
    def officer_group_access(self):
        officer_group = self.env.ref('kw_handbook.groups_handbook_officer')

        handbook_records = self.env['kw_handbook_type'].sudo().search([])
        handbook_users = handbook_records.mapped('emp_id.user_id')

        users_to_add = handbook_users - officer_group.users
        for user in users_to_add:
            # print(user,"user--------------------------")
            officer_group.sudo().write({'users': [(4, user.id)]})

        users_to_remove = officer_group.users - handbook_users
        for user in users_to_remove:
            officer_group.sudo().write({'users': [(3, user.id)]})
