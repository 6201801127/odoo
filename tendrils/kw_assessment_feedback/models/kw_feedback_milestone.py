# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import math


class kw_feedback_milestone(models.Model):
    _name = 'kw_feedback_milestone'
    _description = 'Assessment feedback configuration milestone.'
    _rec_name = 'milestone_name'

    milestone_name = fields.Char(string='Milestone Name', required=True,autocomplete="off")
    goal_id = fields.Many2one(
        'kw_feedback_goal_and_milestone', string='Goad Id', ondelete='restrict')
    score = fields.Integer(string='Progress (in %)')
    weightage_id = fields.Many2one(comodel_name='kw_feedback_weightage_master',string='Performance Grade',ondelete='restrict')

    @api.constrains('score')
    def _check_value(self):
        for record in self:
            if record.score > 100 or record.score < 0:
                raise ValidationError(_('Enter Value Between 0-100.'))

    @api.onchange('score')
    def _change_weightage(self):
        weightage_master = self.env['kw_feedback_weightage_master']
        for record in self:
            if record.score:
                weightage_range = weightage_master.search([('from_range','<=',math.ceil(record.score)),('to_range','>=',math.ceil(record.score))])
                record.weightage_id = weightage_range.id
            else:
                record.weightage_id = False