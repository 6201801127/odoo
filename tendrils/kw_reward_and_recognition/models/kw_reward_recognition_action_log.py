from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RewardRecognitionActionLog(models.Model):
    _name = 'reward_recognition_action_log'
    _description = 'STARLIGHT'

    action_taken_by = fields.Char(string='Action Taken By')
    action_taken_on = fields.Char(string='Action Taken On')
    state = fields.Selection(
        [('sbu', 'Draft'), ('nominate', 'Nominated'), ('review', 'Scrutinized'), ('award', 'Awarded'),
         ('finalise', 'Published'), ('reject', 'Rejected')])
    action_remark = fields.Char(string='Remark')
    rnr_id = fields.Many2one(comodel_name='reward_and_recognition')
