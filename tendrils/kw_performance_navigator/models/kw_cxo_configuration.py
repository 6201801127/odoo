from odoo import models, fields, api, tools
from odoo.exceptions import  ValidationError


class AppraisalCxoConfiguration(models.Model):
    _name = 'appraisal_cxo_configuration'
    _description = "CXO Configuration"
    _rec_name = 'name'

    name = fields.Selection([('all', 'CSM Tech'), ('other', 'Other')], required=True, string="View Access")
    department_id=fields.Many2many("hr.department",String='Departments')
    employee_id=fields.Many2one('hr.employee',string="CXO Name", required=True)


class KwPeformanceNavigatorAccessPermission(models.Model):
    _name = 'kw_performance_navigator_access_configuration'
    _description = "Group Configuration"
    _rec_name = 'name'

    name = fields.Selection([('cxo', 'CXO'),('user', 'User')], required=True, string="Group Name")
    employee_ids = fields.Many2many('hr.employee','kw_pn_group_access','employee_id','pn_group_id',string="Employees", required=True,domain="[('user_id', '!=', False)]")

    @api.onchange('name')
    def _get_users(self):
        self.employee_ids = False
        if self.name:
            if self.name == 'cxo':
                group = self.env.ref('kw_performance_navigator.group_performance_navigator_cxo')
                if group:
                    users = group.users
                    employee_ids = []
                    for user in users:
                        if user.employee_ids:
                            employee_ids.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, employee_ids)]
            if self.name == 'user':
                group = self.env.ref('kw_performance_navigator.group_performance_navigator_user')
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
        cxo_group = []
        user_group = []
        data = self.env['kw_performance_navigator_access_configuration'].search([])
        for rec in data:
            if rec.name == 'cxo':
                for employee_id in rec.employee_ids:
                    cxo_group.append(employee_id.user_id.id)
            if rec.name == 'user':
                for employee_id in rec.employee_ids:
                    user_group.append(employee_id.user_id.id)


        group_manager_kw_pn = self.env.ref('kw_performance_navigator.group_performance_navigator_cxo').sudo()
        group_user_kw_pn = self.env.ref('kw_performance_navigator.group_performance_navigator_user').sudo()


        group_manager_kw_pn.write({'users': [(6, 0, cxo_group)]})
        group_user_kw_pn.write({'users': [(6, 0, user_group)]})


    @api.model
    def create(self, vals):
        record = super(KwPeformanceNavigatorAccessPermission, self).create(vals)
        self._update_group_users()
        return record

    @api.multi
    def write(self, vals):
        res = super(KwPeformanceNavigatorAccessPermission, self).write(vals)
        self._update_group_users()
        return res