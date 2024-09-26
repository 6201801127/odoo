# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TourBudgetAccountConfig(models.Model):
    _name = "tour_budget_account_config"
    _description = "budget account code for tour "

    budget_type = fields.Selection([('project_budget', 'Project Budget'), ('treasury_budget', 'Treasury Budget')])
    account_code_ids = fields.Many2many('account.account', string='Account Code')