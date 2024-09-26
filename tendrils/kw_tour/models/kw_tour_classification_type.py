# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourClassificationType(models.Model):
    _name = "kw_tour_classification_type"
    _description = "Allowance Configuration"

    name = fields.Char('Name', required=True)
    expense_ids = fields.One2many('kw_tour_classification_expense', 'classification_id', 'Expenses')
    description = fields.Text("Description")

    @api.constrains('name', 'expense_ids')
    def _check_expenses(self):
        ''' Validate expenses with currency not duplicate.'''
        regex = re.compile(r"[@_!#$%^&*()|<>?/\}{~:]")
        for clsfctn in self:

            if regex.search(clsfctn.name) != None:
                raise ValidationError("Special characters are not allowed in allowance name.")

            record = self.env['kw_tour_classification_type'].search([]) - self
            for info in record:
                if info.name.lower() == clsfctn.name.lower():
                    raise ValidationError(f"The classification type {clsfctn.name} already exists.Please try a different one.")

            for expense in clsfctn.expense_ids:

                same_expenses = clsfctn.expense_ids.filtered(lambda r: r.expense_type_id == expense.expense_type_id) - expense
                employee_grade_ids = same_expenses.mapped("employee_grade_id")

                duplicate_employee_grade = expense.employee_grade_id & employee_grade_ids
                if duplicate_employee_grade:
                    raise ValidationError("Duplicate employee grade(s) for expense type are not allowed")

    @api.model
    def create(self, values):
        result = super(TourClassificationType, self).create(values)
        self.env.user.notify_success("Tour classification type created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourClassificationType, self).write(values)
        self.env.user.notify_success("Tour classification type updated successfully.")
        return result
