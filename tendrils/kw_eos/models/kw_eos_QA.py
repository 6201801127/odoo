# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import pdb

class EOSQA(models.Model):
    _name = "kw_eos_qa"
    _description = "EOS Question Answers"
    _order = 'id'

    code = fields.Char('Code')
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char('Questions')
    question_type = fields.Selection([('sub', 'Subjective'), ('obj', 'Objective')], default='', string='Question Type')
    answers_sub = fields.Char('Answers')
    answers_obj = fields.Selection([('A', 'A'), ('B', 'B')], default='', string='Answers')
    eos_id = fields.Many2one('kw_end_of_service', string="EOS Ref#")