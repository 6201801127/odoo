# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourExpenseType(models.Model):
    _name = "kw_tour_expense_type"
    _description = "Tour Expense Type"

    name = fields.Char('Expense Type', required=True)
    code = fields.Char("Code", required=True)
    description = fields.Text("Description")
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_tour_expense_type(self):
        regex = re.compile(r"[@_!#$%^&*()|<>?/\}{~:]")
        for expense_type in self:
            if regex.search(expense_type.name) != None:
                raise ValidationError(
                    "Special characters are not allowed in expense type.")
            record = self.env['kw_tour_expense_type'].search([]) - expense_type
            for info in record:
                if info.name.lower() == expense_type.name.lower():
                    raise ValidationError(
                        f"The Expense type {expense_type.name} already exists.")

    @api.model
    def create(self, values):
        result = super(TourExpenseType, self).create(values)
        self.env.user.notify_success("Tour expense type created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourExpenseType, self).write(values)
        self.env.user.notify_success("Tour expense type updated successfully.")
        return result
