# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourCity(models.Model):
    _name = "kw_tour_city"
    _description = "Tour City"
    _order = "name asc"

    country_id = fields.Many2one("res.country", "Country", required=True)
    name = fields.Char(string='City Name', required=True)
    ha_eligible = fields.Boolean("Eligible For Hardship Allowance")
    expense_type_id = fields.Many2one("kw_tour_expense_type", "Expense Type")
    eligibility_percent = fields.Integer("Percentage Of Eligibility")

    classification_type_id = fields.Many2one("kw_tour_classification_type", "Classification Type", required=True)
    expense_ids = fields.One2many("kw_tour_classification_expense",
                                  related="classification_type_id.expense_ids", string="Expenses")

    expense_domain_ids = fields.Many2many('kw_tour_expense_type', string="Expense Domains",
                                          compute="set_expense_domains")

    company_id = fields.Many2one('res.company', string="Company")

    @api.depends('classification_type_id', 'classification_type_id.expense_ids')
    def set_expense_domains(self):
        for city in self:
            if not city.classification_type_id:
                city.expense_domain_ids = False
            else:
                expenses = city.mapped('classification_type_id.expense_ids.expense_type_id')
                city.expense_domain_ids = [[6,0,expenses.ids]]

    @api.constrains('name')
    def validate_tour_city(self):
        regex = re.compile(r"[@_!#$%^&*()|<>?/\}{~:]")
        for city in self:
            if regex.search(city.name) != None:
                raise ValidationError(
                    "Special characters are not allowed in City name.")
            record = self.env['kw_tour_city'].search([]) - city
            for info in record:
                if info.name.lower() == city.name.lower() and info.company_id.id == city.company_id.id:
                    raise ValidationError(f"Tour City {city.name} already exists for this company.")

    @api.onchange('ha_eligible')
    def _onchange_expense_percentage(self):
        if not self.ha_eligible:
            self.expense_type_id = self.eligibility_percent = False

    @api.constrains("ha_eligible", "eligibility_percent")
    def validate_experience(self):
        for city in self:
            if city.ha_eligible and not (1 <= city.eligibility_percent <= 100):
                raise ValidationError("Percentage of eligibility must be between 1 to 100.")

    @api.model
    def create(self, values):
        result = super(TourCity, self).create(values)
        self.env.user.notify_success("Tour city configuration created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(TourCity, self).write(values)
        self.env.user.notify_success("Tour city configuration updated successfully.")
        return result
