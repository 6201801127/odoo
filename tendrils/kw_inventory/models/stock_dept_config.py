from odoo import api, fields, models


class StockDeptConfiguration(models.Model):
    _name = "stock_dept_configuration"
    _description = "stock_dept_configuration"
    _rec_name = 'name'

    # department_id = fields.Many2one('hr.department', string="Department",track_visibility='always')
    branch_id = fields.Many2one('kw_res_branch', string='Branch', track_visibility='always')
    employee_ids = fields.Many2many(string='Employee Name', comodel_name='hr.employee', relation='stock_dept_emp_rel',
                                    column1='stock_dept_id', column2='emp_id', track_visibility='always')
    name = fields.Char(string="Name", track_visibility='always')
    active = fields.Boolean(string='Active', default=True, track_visibility='always')

    @api.model
    def create(self, vals):
        if 'employee_ids' in vals and vals['employee_ids'][0][2]:
            store_manager_group = self.env.ref('kw_inventory.group_store_manager', False)
            store_manager = self.env['hr.employee'].sudo().browse(vals['employee_ids'][0][2])
            for user in store_manager.mapped('user_id'):
                store_manager_group.sudo().write({'users': [(4, user.id)]})
            self.env.user.notify_success("Users added to the Store Manager group")
        res = super(StockDeptConfiguration, self).create(vals)
        self.env.user.notify_success(message='Department configuration created successfully.')
        return res

    @api.multi
    def write(self, vals):
        employee = self.env['hr.employee']
        if 'employee_ids' in vals and vals['employee_ids'][0][2]:
            store_manager_group = self.env.ref('kw_inventory.group_store_manager', False)
            store_manager = employee.sudo().browse(vals['employee_ids'][0][2])
            remove_users_access_ids = self.employee_ids if store_manager.ids != self.employee_ids.ids else False
            if remove_users_access_ids:
                if len(store_manager.ids) > len(self.employee_ids.ids):
                    for user in store_manager.mapped('user_id'):
                        store_manager_group.sudo().write({'users': [(4, user.id)]})
                    self.env.user.notify_success("Users added to the Store Manager group")
                        
                if len(store_manager.ids) < len(self.employee_ids.ids):
                    access_removed_users = list(set(self.employee_ids.mapped('user_id').ids) - set(store_manager.mapped('user_id').ids))
                    for user in access_removed_users:
                        store_manager_group.sudo().write({'users': [(3, user)]})
                    self.env.user.notify_success("Users Removed from the Store Manager group")

        res = super(StockDeptConfiguration, self).write(vals)
        self.env.user.notify_success(message='Department configuration has been updated successfully.')
        return res