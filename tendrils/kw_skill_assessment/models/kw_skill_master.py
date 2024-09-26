# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_skill_master(models.Model):
    _name = 'kw_skill_master'
    _description = "A master model to create skills."
    _order = 'name'

    name = fields.Char(string="Name", required=True, size=100)
    description = fields.Text(string="Description")
    skill_type = fields.Many2one('kw_skill_type_master', string="Skill Category", required=True)
    # employee_id = fields.Many2many('hr.employee', string='Responsible Person')
    duplicate_skill_ids = fields.Many2many(comodel_name='kw_skill_master',
                                           relation='kw_skill_master_rel',
                                           string='Duplicate Skill',
                                           column1='kw_skill_id',
                                           column2='skill_master_id',
                                           domain=[('active', 'in', [True, False])])

    employee_id = fields.Many2many(comodel_name='hr.employee',
                                   relation='kw_skill_master_hr_employee_rel',
                                   string="Responsible Person",
                                   column1='skill_id',
                                   column2='emp_id')

    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")

    @api.constrains('name')
    def validate_skill_name(self):
        if re.match("^[a-zA-Z0-9 ,./()_+-]+", self.name) == None:
            raise ValidationError("Invalid skill! Please provide a valid skill.")

        record = self.env['kw_skill_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError(f"The skill {self.name} already exists.")

    @api.model
    def create(self, vals):
        # print(vals)
        new_record = super(kw_skill_master, self).create(vals)
        evaluator_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_evaluator')
        employees = new_record.employee_id.mapped('user_id')
        for record in employees:
            if not record.has_group('kw_skill_assessment.group_kw_skill_assessment_evaluator'):
                evaluator_group.sudo().write({
                    'users': [(4, record.id)]
                })

        self.env.user.notify_success(message='Skill created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        current_employee_ids = self.employee_id.ids
        employee = self.env['hr.employee']
        evaluator_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_evaluator')

        res = super(kw_skill_master, self).write(vals)
        updated_employee_ids = self.employee_id.ids
        # print(current_employee_ids)
        # print(updated_employee_ids)
        for current_employee in current_employee_ids:
            if current_employee not in updated_employee_ids:
                current_emp = employee.search([('id', '=', current_employee)]).mapped('user_id')
                if current_emp and current_emp.has_group('kw_skill_assessment.group_kw_skill_assessment_evaluator'):
                    evaluator_group.sudo().write({
                        'users': [(3, current_emp.id, False)]
                    })
        for update_employee in updated_employee_ids:
            if update_employee not in current_employee_ids:
                update_emp = employee.search([('id', '=', update_employee)]).mapped('user_id')
                if update_emp and not update_emp.has_group('kw_skill_assessment.group_kw_skill_assessment_evaluator'):
                    evaluator_group.sudo().write({
                        'users': [(4, update_emp.id)]
                    })
        self.env.user.notify_success(message='Skill updated successfully.')
        return res

    @api.multi
    def unlink(self):
        group_master = self.env['kw_skill_group_master'].search([])
        for record in self:
            for rec in group_master:
                if rec.skills.id == record.id:
                    raise ValidationError(f"{record.name} is used in skill group master. You can't delete.")
            record.active = False
        return True

    @api.multi
    def check_duplicate_skill(self):
        # skill_data = self.env['hr.applicant'].sudo().search([])
        # for rec in skill_data:
        #     for duplicate_skill in self.duplicate_skill_ids:
        #         if duplicate_skill.id in rec.skill_ids.ids:
        #             rec.write({'skill_ids': [(3, duplicate_skill.id)]})
        #             rec.write({'skill_ids': [(4, self.id)]})
        #             correction_data.create({
        #                 'model_id': rec._name,
        #                 'rec_id': rec.id,
        #                 'old_value': duplicate_skill.name,
        #                 'new_value': self.name
        #             })
        correction_data = self.env['kw_skill_correction_log'].sudo()

        # Recruitment Start#

        skill_data = self.env['hr.applicant'].sudo().search([('skill_ids', 'in', self.duplicate_skill_ids.ids)])
        for rec in skill_data:
            for recc in rec.skill_ids:
                if recc.id in self.duplicate_skill_ids.ids:
                    rec.write({'skill_ids': [(3, recc.id),(4, self.id)]})
                    correction_data.create({
                        'model_id': rec._name,
                        'rec_id': rec.id,
                        'old_value': recc.name,
                        'new_value': self.name
                    })

        mrf_data = self.env['kw_recruitment_requisition'].sudo().search(
            [('technology', 'in', self.duplicate_skill_ids.ids)])
        for rec in mrf_data:
            if rec.technology.id in self.duplicate_skill_ids.ids:
                rec.write({'technology': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.technology.name,
                    'new_value': self.name
                })

        manpower_data = self.env['kw_manpower_indent_form'].sudo().search(
            [('technology', 'in', self.duplicate_skill_ids.ids)])
        for rec in manpower_data:
            if rec.technology.id in self.duplicate_skill_ids.ids:
                rec.write({'technology': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.technology.name,
                    'new_value': self.name
                })

        recruitment_calender_data = self.env['kw_recruitment_positions'].sudo().search(
            [('technology', 'in', self.duplicate_skill_ids.ids)])
        for rec in recruitment_calender_data:
            if rec.technology.id in self.duplicate_skill_ids.ids:
                rec.write({'technology': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.technology.name,
                    'new_value': self.name
                })

        # Recruitment End#

        # Skill Assessment Start #
        skill_question_bank_master_data = self.env['kw_skill_question_bank_master'].sudo().search(
            [('skill', 'in', self.duplicate_skill_ids.ids)])
        for rec in skill_question_bank_master_data:
            if rec.skill.id in self.duplicate_skill_ids.ids:
                rec.write({'skill': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.skill.name,
                    'new_value': self.name
                })

        skill_question_config_data = self.env['kw_skill_question_set_config'].sudo().search(
            [('skill', 'in', self.duplicate_skill_ids.ids)])
        for rec in skill_question_config_data:
            if rec.skill.id in self.duplicate_skill_ids.ids:
                rec.write({'skill': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.skill.name,
                    'new_value': self.name
                })

        skill_group_master_data = self.env['kw_skill_group_master'].sudo().search(
            [('skills', 'in', self.duplicate_skill_ids.ids)])
        for rec in skill_group_master_data:
            for recc in rec.skills:
                if recc.id in self.duplicate_skill_ids.ids:
                    rec.write({'skills': [(3, recc.id), (4, self.id)]})
                    correction_data.create({
                        'model_id': rec._name,
                        'rec_id': rec.id,
                        'old_value': recc.name,
                        'new_value': self.name
                    })

        skill_mark_sheet_data = self.env['kw_skill_mark_sheet_table'].sudo().search(
            [('skills_id', 'in', self.duplicate_skill_ids.ids)])
        for rec in skill_mark_sheet_data:
            for recc in rec.skills_id:
                if recc.id in self.duplicate_skill_ids.ids:
                    rec.write({'skills_id': self.id})
                    correction_data.create({
                        'model_id': rec._name,
                        'rec_id': rec.id,
                        'old_value': recc.name,
                        'new_value': self.name
                    })

                    # Skill Assessment End #

        # training start#1
        training_data = self.env['kw_training'].sudo().search([('course_id', 'in', self.duplicate_skill_ids.ids)])
        for rec in training_data:
            if rec.course_id.id in self.duplicate_skill_ids.ids:
                rec.write({'course_id': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.course_id.name,
                    'new_value': self.name
                })
        # training End#

        # Employee Start#
        employee_data = self.env['hr.employee'].sudo().search(
            [('primary_skill_id', 'in', self.duplicate_skill_ids.ids)])
        for rec in employee_data:
            if rec.primary_skill_id.id in self.duplicate_skill_ids.ids:
                rec.write({'primary_skill_id': self.id})
                correction_data.create({
                    'model_id': rec._name,
                    'rec_id': rec.id,
                    'old_value': rec.primary_skill_id.name,
                    'new_value': self.name
                })

        resource_additional_skill_data = self.env['hr.employee'].sudo().search(
            [('skill_id', 'in', self.duplicate_skill_ids.ids)])
        for rec in resource_additional_skill_data:
            for recc in rec.skill_id:
                if recc.id in self.duplicate_skill_ids.ids:
                    rec.write({'skill_id': [(3, recc.id), (4, self.id)]})
                    correction_data.create({
                        'model_id': rec._name,
                        'rec_id': rec.id,
                        'old_value': recc.name,
                        'new_value': self.name
                    })
        self.env.user.notify_success(message='Skill Correction successfully.')


class kw_skill_correction_log(models.Model):
    _name = 'kw_skill_correction_log'
    _description = "Skill Correction Log."

    model_id = fields.Char(string="Model Name")
    rec_id = fields.Integer(string="Record ID")
    old_value = fields.Char(string="Old Value")
    new_value = fields.Char(string="New Value")
