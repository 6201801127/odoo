from odoo import fields, models,api
from datetime import datetime
from odoo.exceptions import ValidationError


class AutomationConfig(models.Model):
    _name = 'automation_group_config'
    _description = 'Automation Group Configuration'

    def get_testing_team(self):
        project_data = []
        bug_life_cycle_confs = self.env['kw_bug_life_cycle_conf'].sudo().search([])
        for rec in bug_life_cycle_confs:
            for recc in rec.user_ids:
                if recc.user_type == 'Tester':
                    project_data.append(recc.employee_id.id)
        return [('id', '=', project_data)]

    testing_team_ids = fields.Many2many('hr.employee',string="Automation Team", domain=get_testing_team, required=True)

    @api.model
    def create(self, vals):
        record = super(AutomationConfig, self).create(vals)
        record.assign_employees_to_group()
        return record

    def write(self, vals):
        res = super(AutomationConfig, self).write(vals)
        self.assign_employees_to_group()
        return res

    @api.model
    def assign_employees_to_group(self):
        automation_group = self.env.ref('kw_bug_life_cycle.group_automation_bug_life_cycle')
        current_team_members = self.testing_team_ids.mapped('user_id')
        existing_group_members = automation_group.users

        new_members_to_add = current_team_members - existing_group_members
        if new_members_to_add:
            automation_group.sudo().write({
                'users': [(4, user.id) for user in new_members_to_add]
            })

        members_to_remove = existing_group_members - current_team_members
        if members_to_remove:
            automation_group.sudo().write({
                'users': [(3, user.id) for user in members_to_remove]
            })