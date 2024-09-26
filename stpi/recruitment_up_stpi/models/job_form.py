from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime

class RecruitmentRoster(models.Model):
    _name = "recruitment.roster"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Recruitment Roster"
    _rec_name = 'name'

    @api.onchange('job_id')
    def get_roster_line_item(self):
        return {'domain': {'roster_line_item': [('job_id', '=', self.job_id.id), ('employee_id', '=', False)]}}



    name = fields.Char(string="Name",track_visibility='always')
    job_id = fields.Many2one('hr.job', string='Job Position')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    position_number = fields.Integer('Position Number')
    sc = fields.Boolean('SC')
    st = fields.Boolean('ST')
    general = fields.Boolean('General')
