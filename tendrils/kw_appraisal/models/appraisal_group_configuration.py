from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AppraisalAccessPermission(models.Model):
    _name = 'appraisal_group_configuration'
    _description = "Group Configuration"
    _rec_name = 'name'

    name = fields.Selection([('manager', 'Manager'), ('increment_promotion', 'Increment & Promotion'), ('iaa', 'IAA'),('chro','CHRO'),('ceo','CEO')], required=True, string="Group Name")
    employee_ids = fields.Many2many('hr.employee','kw_appraisal_access_rel','employee_id','appraisal_group_id',string="Employees", required=True)

    @api.onchange('name')
    def _get_users(self):
        self.employee_ids = False
        if self.name:
            if self.name == 'manager':
                group = self.env.ref('kw_appraisal.group_appraisal_manager')
                if group:
                    users = group.users
                    employee_ids = []
                    for user in users:
                        if user.employee_ids:
                            employee_ids.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, employee_ids)]
            if self.name == 'increment_promotion':
                group = self.env.ref('kw_appraisal.group_appraisal_increment_promotion')
                if group:
                    users = group.users
                    increment_promotion = []
                    for user in users:
                        if user.employee_ids:
                            increment_promotion.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, increment_promotion)]
            if self.name == 'iaa':
                group = self.env.ref('kw_appraisal.group_appraisal_iaa')
                if group:
                    users = group.users
                    iaa = []
                    for user in users:
                        if user.employee_ids:
                            iaa.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, iaa)]
            if self.name == 'chro':
                group = self.env.ref('kw_appraisal.group_appraisal_chro')
                if group:
                    users = group.users
                    chro = []
                    for user in users:
                        if user.employee_ids:
                            chro.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, chro)]
            if self.name == 'ceo':
                group = self.env.ref('kw_appraisal.group_appraisal_ceo')
                if group:
                    users = group.users
                    ceo = []
                    for user in users:
                        if user.employee_ids:
                            ceo.append(user.employee_ids.id)
                    self.employee_ids = [(6, 0, ceo)]
            

               


    @api.constrains('name')
    def _check_duplicate_department_id(self):
        for record in self:
            duplicate_records = self.search([('name', '=', record.name)]) - self
            if duplicate_records:
                raise ValidationError("Duplicate  Group name is not allowed!")

    @api.model
    def _update_group_users(self):
        manager_group = []
        increment_promotion_group = []
        iaa_group = []
        chro_group = []
        ceo_group = []
        data = self.env['appraisal_group_configuration'].search([])
        for rec in data:
            if rec.name == 'manager':
                for employee_id in rec.employee_ids:
                    manager_group.append(employee_id.user_id.id)
            if rec.name == 'increment_promotion':
                for employee_id in rec.employee_ids:
                    increment_promotion_group.append(employee_id.user_id.id)
            if rec.name == 'iaa':
                for employee_id in rec.employee_ids:
                    iaa_group.append(employee_id.user_id.id)
            if rec.name == 'chro':
                for employee_id in rec.employee_ids:
                    chro_group.append(employee_id.user_id.id)
            if rec.name == 'ceo':
                for employee_id in rec.employee_ids:
                    ceo_group.append(employee_id.user_id.id)
        group_manager_kw_appraisal = self.env.ref('kw_appraisal.group_appraisal_manager').sudo()
        group_increment_promotion_kw_appraisal = self.env.ref('kw_appraisal.group_appraisal_increment_promotion').sudo()
        group_iaa_kw_appraisal = self.env.ref('kw_appraisal.group_appraisal_iaa').sudo()
        group_chro_kw_appraisal = self.env.ref('kw_appraisal.group_appraisal_chro').sudo()
        group_ceo_kw_appraisal = self.env.ref('kw_appraisal.group_appraisal_ceo').sudo()


        group_manager_kw_appraisal.write({'users': [(6, 0, manager_group)]})
        group_increment_promotion_kw_appraisal.write({'users': [(6, 0, increment_promotion_group)]})
        group_iaa_kw_appraisal.write({'users': [(6, 0, iaa_group)]})
        group_chro_kw_appraisal.write({'users': [(6, 0, chro_group)]})
        group_ceo_kw_appraisal.write({'users': [(6, 0, ceo_group)]})

    


    @api.model
    def create(self, vals):
        record = super(AppraisalAccessPermission, self).create(vals)
        self._update_group_users()
        return record

    @api.multi
    def write(self, vals):
        res = super(AppraisalAccessPermission, self).write(vals)
        self._update_group_users()
        return res