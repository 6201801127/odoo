from odoo import fields, models,api
from datetime import datetime
from odoo.exceptions import ValidationError


class KwModuleAccessPermission(models.Model):
    _name = 'kw_module_access_permission'
    _description = 'Kw Module Access Permission'
    _rec_name = 'project_id'

    _sql_constraints = [
        ('uniq_project_id','unique(project_id)','Project must be unique!')
    ]

    def get_emp_project(self):
        project_data = []
        bug_life_cycle_confs = self.env['kw_bug_life_cycle_conf'].sudo().search([])
        for rec in bug_life_cycle_confs:
            for recc in rec.user_ids:
                if recc.user_type == 'Test Lead':
                    if self.env.user.id == recc.employee_id.user_id.id:
                        project_data.append(rec.id)
        return [('id', '=', project_data)]


    project_id = fields.Many2one('kw_bug_life_cycle_conf',string="Project Name", domain=get_emp_project, required=True)
    module_access_ids = fields.One2many('module_access', 'module_access_id', string='Module Access Permission')
    has_module_access_ids = fields.Boolean(string="Has Module Access Records?", compute="_compute_has_module_access_ids", store=True)

    @api.depends('module_access_ids')
    def _compute_has_module_access_ids(self):
        for record in self:
            record.has_module_access_ids = bool(record.module_access_ids)

    @api.onchange('project_id')
    def nullify_module_access_details(self):
        self.module_access_ids = False

    @api.multi
    def write(self, vals):
        if 'project_id' in vals:
            raise ValidationError('You cannot change Project Name.')
        return super(KwModuleAccessPermission, self).write(vals)

class ModuleAccess(models.Model):
    _name = 'module_access'
    _description = 'Module Access'

    module_access_id = fields.Many2one('kw_module_access_permission')
    project_id = fields.Integer(related='module_access_id.project_id.project_id.id')
    module_id = fields.Many2one('bug_module_master',string="Global Link", required=True)
    test_case_update_perm = fields.Boolean(string="Test Case Write Permission")
    test_case_execution_perm = fields.Boolean(string="Test Case Execution Permission")
    last_updated_by = fields.Char(string="Last Updated By", readonly=True)
    last_updated_on = fields.Datetime(string="Last Updated Date", readonly=True)
    is_module_used_tcw = fields.Boolean(string="Is Module Used?", compute="_compute_is_module_used")

    @api.depends('module_id', 'module_access_id.project_id')
    def _compute_is_module_used(self):
        for record in self:
            if record.module_id and record.module_access_id.project_id:
                used_in_upload = self.env['kw_test_case_upload'].sudo().search([
                    ('module_id', '=', record.module_id.id),
                    ('project_id', '=', record.module_access_id.project_id.id)
                ])
                if used_in_upload:
                    for rec in used_in_upload:
                        if rec.data_line_ids:
                            record.is_module_used_tcw = True

    @api.model
    def create(self, vals):
        vals['last_updated_by'] = self.env.user.name
        vals['last_updated_on'] = datetime.now()
        return super(ModuleAccess, self).create(vals)

    @api.model
    def write(self, vals):
        vals['last_updated_by'] = self.env.user.name
        vals['last_updated_on'] = datetime.now()
        return super(ModuleAccess, self).write(vals)

    @api.onchange('test_case_execution_perm','test_case_update_perm')
    def get_value(self):
        if self.test_case_execution_perm == True:
            self.test_case_update_perm = True

    @api.onchange('project_id')
    def get_module_id(self):
        self.module_id = False
        if self.project_id:
            existing_module_ids = self.module_access_id.module_access_ids.mapped('module_id.id')
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', self.project_id)]).id
            dataa = self.env['bug_module_master'].sudo().search([('project_id', '=', data)]).mapped('id')
            return {'domain': {'module_id': [('id', 'in', dataa),('id','not in',existing_module_ids)]}}
        else:
            return {'domain': {'module_id': [('id', 'in', [])]}}
