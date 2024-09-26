from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EqAccessPermission(models.Model):
    _name = 'kw_eq_access_configuration'
    _description = "Group Configuration"
    _rec_name = 'name'

    name = fields.Selection([('manager', 'Manager'), ('finance', 'Finance'),('user', 'User'),('backlog_user','Backlog user'),('report_manager','Report Manager')], required=True, string="Group Name")
    employee_ids = fields.Many2many('hr.employee','kw_eq_group_access','employee_id','eq_group_id',string="Employees", required=True,domain="[('user_id', '!=', False)]")

    @api.onchange('name')
    def _get_users(self):
        self.employee_ids = False
        if self.name:
            if self.name == 'manager':
                group = self.env.ref('kw_eq.group_eq_manager')
                if group:
                    users = group.users
                    employee_ids = []
                    for user in users:
                        if user.employee_ids:
                            employee_ids.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, employee_ids)]
            if self.name == 'user':
                group = self.env.ref('kw_eq.group_eq')
                if group:
                    users = group.users
                    user_data = []
                    for user in users:
                        if user.employee_ids:
                            user_data.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, user_data)]

            if self.name == 'finance':
                group = self.env.ref('kw_eq.group_eq_finance')
                if group:
                    users = group.users
                    user_data = []
                    for user in users:
                        if user.employee_ids:
                            user_data.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, user_data)]

            if self.name == 'backlog_user':
                group = self.env.ref('kw_eq.group_eq_backlog')
                if group:
                    users = group.users
                    user_data = []
                    for user in users:
                        if user.employee_ids:
                            user_data.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, user_data)]
                    
            if self.name == 'report_manager':
                group = self.env.ref('kw_eq.group_eq_report_manager')
                if group:
                    users = group.users
                    user_data = []
                    for user in users:
                        if user.employee_ids:
                            user_data.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, user_data)]



    @api.constrains('name')
    def _check_duplicate_department_id(self):
        for record in self:
            duplicate_records = self.search([('name', '=', record.name)]) - self
            if duplicate_records:
                raise ValidationError("Duplicate Group name is not allowed!")

    @api.model
    def _update_group_users(self):
        manager_group = []
        user_group = []
        finance_group = []
        backlog_user_group = []
        report_manager_group = []


        data = self.env['kw_eq_access_configuration'].search([])
        for rec in data:
            if rec.name == 'manager':
                for employee_id in rec.employee_ids:
                    manager_group.append(employee_id.user_id.id)
            if rec.name == 'user':
                for employee_id in rec.employee_ids:
                    user_group.append(employee_id.user_id.id)

            if rec.name == 'finance':
                for employee_id in rec.employee_ids:
                    finance_group.append(employee_id.user_id.id)

            if rec.name == 'backlog_user':
                for employee_id in rec.employee_ids:
                    backlog_user_group.append(employee_id.user_id.id)
                    
            if rec.name == 'report_manager':
                for employee_id in rec.employee_ids:
                    report_manager_group.append(employee_id.user_id.id)

        group_manager_kw_eq = self.env.ref('kw_eq.group_eq_manager').sudo()
        group_user_kw_eq = self.env.ref('kw_eq.group_eq').sudo()
        group_user_kw_finance = self.env.ref('kw_eq.group_eq_finance').sudo()
        group_user_kw_eq_backlog = self.env.ref('kw_eq.group_eq_backlog').sudo()
        group_report_manager_kw_eq = self.env.ref('kw_eq.group_eq_report_manager').sudo()



        group_manager_kw_eq.write({'users': [(6, 0, manager_group)]})
        group_user_kw_eq.write({'users': [(6, 0, user_group)]})
        group_user_kw_finance.write({'users': [(6, 0, finance_group)]})
        group_user_kw_eq_backlog.write({'users': [(6, 0, backlog_user_group)]})
        group_report_manager_kw_eq.write({'users': [(6, 0, report_manager_group)]})







    @api.model
    def create(self, vals):
        record = super(EqAccessPermission, self).create(vals)
        self._update_group_users()
        return record

    @api.multi
    def write(self, vals):
        res = super(EqAccessPermission, self).write(vals)
        self._update_group_users()
        return res
