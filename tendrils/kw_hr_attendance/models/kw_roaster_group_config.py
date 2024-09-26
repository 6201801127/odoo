# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class RoasterGroupConfig(models.Model):
    _name = 'kw_roaster_group_config'
    _description = 'Roster Group Configuration'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Group Name', required=True)
    group_head_id = fields.Many2one(string='Group Head', comodel_name='hr.employee', ondelete='restrict', required=True)

    group_member_ids = fields.Many2many(
        string='Group Members',
        comodel_name='hr.employee',
        relation='hr_employee_roaster_group_config_rel',
        column1='employee_id',
        column2='group_id',
    )

    @api.multi
    @api.constrains('name')
    def group_name_validation(self):
        for record in self:
            record._check_name()
            if not (re.match('^[ a-zA-Z0-9()]+$', record.name)):
                raise ValidationError("Group Name input accepts only alphanumeric values.")

    def _check_name(self):
        if self.search_count([('name', '=', self.name), ('id', '!=', self.id)]):
            raise ValidationError("Group Name already exists. Please change the group name.")

    @api.constrains('group_head_id', 'group_member_ids')
    def _check_group_member(self):
        for group in self:
            if group.group_head_id and not group.group_member_ids:
                raise ValidationError("Please add at least one group member.")

    # @api.model
    # def create(self, vals):
    #     new_record = super(RoasterGroupConfig, self).write(vals)
    #     self.env.user.notify_success(message='Roaster Group Configuration created successfully.')
    #     return new_record

    @api.model
    def create(self, values):
        result = super(RoasterGroupConfig, self).create(values)
        group_head_user_id = result.group_head_id.user_id
        if group_head_user_id and not group_head_user_id.has_group('kw_hr_attendance.group_hr_attendance_roaster'):
            roaster_group = self.env.ref('kw_hr_attendance.group_hr_attendance_roaster')
            roaster_group.write({'users': [(4, group_head_user_id.id)]})
        return result

    @api.multi
    def write(self, values):
        if 'group_head_id' in values:
            roaster_group = self.env.ref('kw_hr_attendance.group_hr_attendance_roaster')
            group_head_employee = self.env['hr.employee'].browse(values['group_head_id'])
            if group_head_employee.user_id and not group_head_employee.user_id.has_group('kw_hr_attendance.group_hr_attendance_roaster'):
                roaster_group.write({'users': [(4, group_head_employee.user_id.id)]})

            for group in self:
                if group.group_head_id and group.group_head_id.user_id:
                    existing_groups = self.env['kw_roaster_group_config'].search([('group_head_id', '=', group.group_head_id.id)]) - self
                    if not existing_groups:
                        roaster_group.write({'users': [(3, group.group_head_id.user_id.id)]})
        result = super(RoasterGroupConfig, self).write(values)
        return result
