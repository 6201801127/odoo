# -*- coding: utf-8 -*-
"""
Module: Employee Take Action Wizard

Summary:
    This module provides the EmployeeTakeActionWizard class, which represents a transient model for employee actions.

Description:
    The EmployeeTakeActionWizard class defines a transient model used for handling various actions related to employees.
    It includes functionalities for taking actions such as updating employee records or performing specific tasks.
    This class is designed to be used as a wizard for guiding users through the process of taking actions on employees.

"""
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo import models, fields


class EmployeeTakeActionWizard(models.TransientModel):
    """
    Wizard for taking actions on employees.

    This class represents a transient model used for handling various actions related to employees.
    It provides functionalities for guiding users through the process of taking actions on one or multiple employees.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): Description of the model.
        employee_ids (Many2many): Field for selecting employee information.
    """
    _name = "employee_take_action_wizard"
    _description = "Take Wizard"

    employee_ids = fields.Many2many(
        string='Employee Information',
        comodel_name='lk_batch_details',
        default=lambda self: self.env.context.get('current_ids', [(6, 0, [])])
    )

    new_dept_id = fields.Many2one('hr.department', string='New Department',
                                  domain=[('dept_type.code', '=', 'department')])
    new_division_id = fields.Many2one('hr.department', string="New Division", domain="[('parent_id','=',new_dept_id)]")
    increment_pattern = fields.Selection(string="Increment Pattern",
                                         selection=[('Phase Wise', 'Phase Wise'), ('Yearly', 'Yearly')],
                                         default='Phase Wise', required=True)
    traineeship_score = fields.Float(string="Score")
    internship_score = fields.Float(string="Internship Score")
    traineeship_comments_applied = fields.Char(string="L&K Feedback")
    internship_comments_applied = fields.Char(string="L&K Feedback")
    # hide_btn_applied = fields.Boolean(string="hide_btn_applied", default=False)
    rh_check = fields.Boolean(compute="check_boolean_field")
    rh_internship_check = fields.Boolean(compute="check_rh_internship")
    internship_status = fields.Selection(string="internship_status", default="In Progress",
                                         selection=[('In Progress', 'In Progress'), ('Applied', 'Applied'),
                                                    ('Approved', 'Approved'),
                                                    ('Rejected', 'Rejected'),
                                                    ('Payroll Revised', 'Payroll Revised')])
    rh_take_action = fields.Boolean(string='Rh Take Action', compute='_compute_rh_take_action')
    internship_take_action = fields.Boolean(string='Rh Take Action', compute='_compute_internship_take_action')
    remark = fields.Text(string='Remark')
    trainee_date = fields.Date(string='Traineeship Completion Date', default=datetime.today().date())
    training_completion_date = fields.Date(string='Traineeship Completion Date', default=datetime.today().date(), readonly=True)

    @api.onchange('new_dept_id')
    def onchange_new_department(self):
        for rec in self:
            if rec.new_dept_id:
                rec.new_division_id = False

    @api.onchange('traineeship_score')
    def onchange_traineeship_score(self):
        for rec in self:
            if rec.traineeship_score >= 60:
                rec.traineeship_comments_applied = 'Completed'
            elif 50 <= rec.traineeship_score < 60:
                rec.traineeship_comments_applied = 'Hold'
            elif rec.traineeship_score < 50:
                rec.traineeship_comments_applied = 'Close'

    @api.onchange('internship_score')
    def onchange_internship_score(self):
        for rec in self:
            if rec.internship_score >= 60:
                rec.internship_comments_applied = 'Completed'
                # print(rec.internship_comments_applied,"internship_comments_applied===============")
            elif 50 <= rec.internship_score < 60:
                rec.internship_comments_applied = 'Hold'
            elif rec.internship_score < 50:
                rec.internship_comments_applied = 'Close'

    @api.depends('traineeship_comments_applied')
    def check_boolean_field(self):
        for rec in self:
            if self.env.user.has_group('internship_program.group_rh_internship_program'):
                rec.rh_check = True
            else:
                rec.rh_check = False

    @api.depends('internship_comments_applied')
    def check_rh_internship(self):
        for rec in self:
            if self.env.user.has_group('internship_program.group_rh_internship_program'):
                rec.rh_internship_check = True
            else:
                rec.rh_internship_check = False

    @api.depends('employee_ids.traineeship_status')
    def _compute_rh_take_action(self):
        for rec in self:
            employee_statuses = rec.employee_ids.mapped('traineeship_status')
            if 'In Progress' in employee_statuses:
                rec.rh_take_action = True
            else:
                rec.rh_take_action = False

    @api.depends('employee_ids.internship_status')
    def _compute_internship_take_action(self):
        for rec in self:
            internship_statuses = rec.employee_ids.mapped('internship_status')
            if 'In Progress' in internship_statuses:
                rec.internship_take_action = True
            else:
                rec.internship_take_action = False

    def training_completion_btn(self):
        if self.traineeship_comments_applied is False or self.traineeship_score <= 0:
            raise ValidationError("Please give score and comment to apply for traineeship completion.")
        lk_batch_data = self.env['lk_batch'].sudo().search([])
        for employee in self.employee_ids:
            lk_batch_status_data = employee.mapped('traineeship_status')
            if any(status in ['Rejected', 'Approved', 'Applied'] for status in lk_batch_status_data):
                raise ValidationError("Please remove records which are already Applied,Approved or Rejected.")

            for rec in lk_batch_data:
                existing_record = rec.training_completion_details_ids.filtered(lambda r: r.employee_id == employee.employee_id)
                if existing_record:
                    existing_record.write({
                        'new_dept_id': self.new_dept_id.id,
                        'new_division_id': self.new_division_id.id,
                        'increment_pattern': self.increment_pattern,
                        'traineeship_score': self.traineeship_score,
                        'traineeship_comments_applied': self.traineeship_comments_applied,
                        'traineeship_status': 'Applied',
                        'traineeship_applied_date': date.today(),
                    })

    def traineeship_approved_btn(self):
        lk_batch_data = self.env['lk_batch'].sudo().search([])
        for employee in self.employee_ids:
            lk_batch_status_data = employee.mapped('traineeship_status')
            if any(status in ['Rejected', 'Approved'] for status in lk_batch_status_data):
                raise ValidationError("Please remove records which are already Rejected or Approved.")

            for rec in lk_batch_data:
                existing_record = rec.training_completion_details_ids.filtered(lambda r: r.employee_id == employee.employee_id)
                if existing_record:
                    existing_record.write({
                        'traineeship_comments_approved': self.remark,
                        'traineeship_status': 'Approved',
                        'traineeship_complete_check': True,
                        # 'internship_id':rec.id,
                        'lk_payroll': rec.id,
                    })

    def traineeship_rejected_btn(self):
        lk_batch_data = self.env['lk_batch'].sudo().search([])
        for employee in self.employee_ids:
            lk_batch_status_data = employee.mapped('traineeship_status')
            if any(status in ['Rejected', 'Approved'] for status in lk_batch_status_data):
                raise ValidationError("Please remove records which are already approved or rejected.")

            for rec in lk_batch_data:
                existing_record = rec.training_completion_details_ids.filtered(lambda r: r.employee_id == employee.employee_id)
                if existing_record:
                    existing_record.write({
                        'traineeship_comments_approved': self.remark,
                        'traineeship_status': 'Rejected',
                    })

    def traineeship_pay_revies_btn(self):
        for employee in self.employee_ids:
            emp_rec = employee.employee_id
            emp_data = {
                'current_ctc': employee.traineeship_current_ctc,
                'current_basic': employee.traineeship_emp_basic,
                'hra': 40 if not emp_rec.hra > 0 else emp_rec.hra,
                'conveyance': 10 if not emp_rec.conveyance > 0 else emp_rec.conveyance,
                'productivity': employee.traineeship_emp_pb,
                'commitment': employee.traineeship_emp_cb,
                # 'department_id': employee.new_dept_id.id if employee.new_dept_id else '',
                # 'division': employee.new_division_id.id if employee.new_division_id else ''
            }

            # emp_data['hra'] = 40 if not emp_rec.hra > 0 else emp_rec.hra
            # emp_data['conveyance'] = 10 if not emp_rec.conveyance > 0 else emp_rec.conveyance
            # employee.write(emp_data)
            query = f"UPDATE hr_employee SET current_ctc={emp_data['current_ctc']}, current_basic={emp_data['current_basic']}, productivity={emp_data['productivity']}, commitment={emp_data['commitment']}, hra={emp_data['hra']}, conveyance={emp_data['conveyance']} WHERE id={emp_rec.id};"
            self._cr.execute(query)

            contract_record = self.env['hr.contract'].search([('employee_id', '=', emp_rec.id)])
            if contract_record.exists():
                contract_data = {
                    'wage': employee.traineeship_current_ctc,
                    'current_basic': employee.traineeship_emp_basic,
                    'productivity': employee.traineeship_emp_pb,
                    'commitment': employee.traineeship_emp_cb,
                }
                if not contract_record.house_rent_allowance_metro_nonmetro > 0:
                    contract_data['house_rent_allowance_metro_nonmetro'] = 40
                if not contract_record.conveyance > 0:
                    contract_data['conveyance'] = 10
                contract_record.write(contract_data)

            employee.write({'pay_revise_success_bool': True,
                            'traineeship_status': 'Pay Revised',
                            'change_dept_bool': True,
                            'internship_id': employee.batch_id.id})

        self.env.user.notify_success(message='Salary Updated successfully!')

    def training_completion_department_btn(self):
        if self.employee_ids:
            emp_data = {'new_dept_id': self.new_dept_id.id,
                        'new_division_id': self.new_division_id.id,
                        'change_dept_bool': True, }
            # print('emp_data >>> ', emp_data)
            self.employee_ids.write(emp_data)
            today = datetime.now().date()
            query = []
            for emp in self.employee_ids:
                query += [f"UPDATE hr_employee SET department_id={self.new_dept_id.id}, division={self.new_division_id.id}, training_completion_date='{today}' WHERE id={emp.employee_id.id};"]
                record = self.env['kw_emp_sync_log'].sudo().search(
                        [('model_id', '=', 'hr.employee'), ('rec_id', '=', emp.employee_id.id), ('code', '=', 1),
                        ('status', '=', 0)])
                if not record.exists():
                    record.create({'model_id': 'hr.employee', 'rec_id': emp.employee_id.id, 'code': 1, 'status': 0})
                else:
                    pass
             # print("query >>> ", ''.join(query))
            self._cr.execute(''.join(query))

    # def training_completion_date_btn(self):
    #     for rec in self.employee_ids:
    #         employee_data = self.env['hr.employee'].search([('id', '=', rec.employee_id.id)])
    #         # print(rec.employee_id.id,"-----emp===============")
    #         employee_data.sudo().write({'training_completion_date': self.trainee_date})
    #         # print(rec,"--------rec===========",employee_data)

    def internship_completion_btn(self):
        if self.internship_score <= 0.0:
            raise ValidationError("You can't complete the internship program without a score and comments.")
        lk_batch_data = self.env['lk_batch'].sudo().search([])

        for employee in self.employee_ids:
            lk_batch_status_data = employee.mapped('internship_id.internship_completion_details_ids.internship_status')
            lk_batch_traineeship_data = employee.mapped('batch_id.training_completion_details_ids.traineeship_status')

            if any(status in ['Rejected', 'Approved', 'Applied'] for status in lk_batch_status_data
                   if status not in ['Applied', 'Approved', 'Rejected']):
                raise ValidationError("Please remove records which are already applied, approved, or rejected.")
            elif any(status in ['In Progress', 'Rejected', 'Applied'] for status in lk_batch_traineeship_data):
                raise ValidationError("Please remove records which are In Progress in traineeship.")

            for rec in lk_batch_data:
                existing_record = rec.internship_completion_details_ids.filtered(lambda r: r.employee_id == employee.employee_id)
                if existing_record:
                    existing_record.write({
                        'internship_score': self.internship_score,
                        'internship_comments_applied': self.internship_comments_applied,
                        'internship_status': 'Applied',
                    })

    def internship_approved_btn(self):
        if self._context.get('button') == 'internship_approve_button':
            lk_batch_data = self.env['lk_batch'].sudo().search([])
            for employee in self.employee_ids:
                lk_batch_status_data = employee.mapped('internship_status')
                if any(status in ['Rejected', 'Approved', 'In Progress'] for status in lk_batch_status_data):
                    raise ValidationError("Please remove records which are already Rejected or Approved.")

                for rec in lk_batch_data:
                    existing_record = rec.internship_completion_details_ids.filtered(lambda r: r.employee_id == employee.employee_id)
                    if existing_record:
                        existing_record.write({
                            'internship_comments_approved': self.remark,
                            'internship_status': 'Approved',
                            # 'internship_id':rec.id,
                            'lk_payroll_internship': rec.id,
                        })

    def internship_rejected_btn(self):
        if self._context.get('button') == 'internship_rejected_button':
            lk_batch_data = self.env['lk_batch'].sudo().search([])
            for employee in self.employee_ids:
                lk_batch_status_data = employee.mapped('internship_status')
                if any(status in ['Rejected', 'Approved', 'In Progress'] for status in lk_batch_status_data):
                    raise ValidationError("Please remove records which are already approved or rejected.")

                for rec in lk_batch_data:
                    existing_record = rec.internship_completion_details_ids.filtered(lambda r: r.employee_id == employee.employee_id)
                    if existing_record:
                        existing_record.write({
                            'internship_comments_approved': self.remark,
                            'internship_status': 'Rejected',
                        })
