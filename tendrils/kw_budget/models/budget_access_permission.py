from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BudgetAccessPermission(models.Model):
    _name = 'kw_budget_access_permission'
    _description = "Budget Access Permission"
    _rec_name = 'name'

    name = fields.Selection([('approver', 'Approver'), ('finance', 'Finance'), ('manager', 'Manager'), ('cfo', 'CFO')], required=True, string="Group Name")
    employee_ids = fields.Many2many('hr.employee','kw_budget_access_rel','employee_id','budget_dept_id',string="Employees", required=True)

    @api.constrains('name')
    def _check_duplicate_department_id(self):
        for record in self:
            duplicate_records = self.search([('name', '=', record.name)]) - self
            if duplicate_records:
                raise ValidationError("Duplicate  Group name is not allowed!")

    @api.model
    def _update_group_users(self):
        finance_group = []
        approver_group = []
        manager_group = []
        cfo_group = []
        data = self.env['kw_budget_access_permission'].search([])
        for rec in data:
            if rec.name == 'finance':
                for employee_id in rec.employee_ids:
                    finance_group.append(employee_id.user_id.id)
            if rec.name == 'approver':
                for employee_id in rec.employee_ids:
                    approver_group.append(employee_id.user_id.id)
            if rec.name == 'manager':
                for employee_id in rec.employee_ids:
                    manager_group.append(employee_id.user_id.id)
            if rec.name == 'cfo':
                for employee_id in rec.employee_ids:
                    cfo_group.append(employee_id.user_id.id)
        group_finance_kw_budget = self.env.ref('kw_budget.group_finance_kw_budget').sudo()
        group_approver_kw_budget = self.env.ref('kw_budget.group_approver_kw_budget').sudo()
        group_manager_kw_budget = self.env.ref('kw_budget.group_manager_kw_budget').sudo()
        group_cfo_kw_budget = self.env.ref('kw_budget.group_cfo_kw_budget').sudo()
        group_finance_kw_budget.write({'users': [(6, 0, finance_group)]})
        group_approver_kw_budget.write({'users': [(6, 0, approver_group)]})
        group_manager_kw_budget.write({'users': [(6, 0, manager_group)]})
        group_cfo_kw_budget.write({'users': [(6, 0, cfo_group)]})

    @api.model
    def create(self, vals):
        record = super(BudgetAccessPermission, self).create(vals)
        self._update_group_users()
        return record

    @api.multi
    def write(self, vals):
        res = super(BudgetAccessPermission, self).write(vals)
        self._update_group_users()
        return res