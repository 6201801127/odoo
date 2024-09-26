# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourBudgetHead(models.Model):
    _name = "kw_tour_budget_head"
    _description = "Tour Budget Head"

    tour_type = fields.Selection([
        ('Project', 'Project'),
        ('Other', 'Other')
    ], string='Tour Type')
    name = fields.Char("Account Head")
    code = fields.Char("Code")
    kw_id = fields.Integer('KW ID')

    @api.model
    def create(self, values):
        result = super(TourBudgetHead, self).create(values)
        self.env.user.notify_success("Budget head created successfully.")
        return result

    @api.multi
    def write(self, values):
        result = super(TourBudgetHead, self).write(values)
        self.env.user.notify_success("Budget head updated successfully.")
        return result
