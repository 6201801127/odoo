from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StarlightMigrationLog(models.Model):
    _name = 'starlight_migration_log'
    _description = 'Starlight Migration Log'

    migration_sequence = fields.Char(string='S.No')
    employee_id = fields.Char(string='Forwarded By')
    migrated_rnr_id = fields.Many2one(comodel_name='reward_and_recognition', string='Starlight Id')
    migrated_on = fields.Date(string='Migrated On')
    migrated_to = fields.Date(string='Migrated To')
    migrated_state = fields.Selection(
        [('sbu', 'Draft'), ('nominate', 'Nominated'), ('award', 'Awarded'),
         ('finalise', 'Published'), ('reject', 'Rejected')],string='Migrated State')
    migration_remark = fields.Char(string='Migrated Remark')
    nominee_id = fields.Many2one('hr.employee', string="Nominee", track_visibility='onchange', compute='nominee_details')
    department_id = fields.Many2one('hr.department', string="Department", compute='nominee_details')
    division = fields.Many2one('hr.department', string="Division", compute='nominee_details')
    section = fields.Many2one('hr.department', string="Practice", compute='nominee_details')
    practise = fields.Many2one('hr.department', string="Section", compute='nominee_details')
    job_id = fields.Many2one('hr.job', string="Designation", compute='nominee_details')
    location = fields.Many2one('kw_res_branch', string="Work Location", compute='nominee_details')

    @api.depends('migrated_rnr_id')
    def nominee_details(self):
        for rec in self:
            rec.nominee_id = rec.migrated_rnr_id.employee_id.id
            rec.department_id = rec.migrated_rnr_id.employee_id.department_id.id
            rec.division = rec.migrated_rnr_id.employee_id.division.id
            rec.section = rec.migrated_rnr_id.employee_id.section.id
            rec.practise = rec.migrated_rnr_id.employee_id.practise.id
            rec.job_id = rec.migrated_rnr_id.employee_id.job_id.id
            rec.location = rec.migrated_rnr_id.employee_id.job_branch_id.id