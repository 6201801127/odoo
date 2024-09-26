from odoo import models, fields, api, tools
from datetime import date, datetime, time


class kw_employee_profile_skills(models.Model):
    _name = 'kw_employee_profile_skills'
    _description = "A model to store the skills of employees."
    _auto = False


    primary_skill_id = fields.Many2one('kw_skill_master', string='Primary Skill')
    secondary_skill_id = fields.Many2one('kw_skill_master',string='Secondary Skill' )
    tertiary_skill_id = fields.Many2one('kw_skill_master',string='Tertiarry Skill')
    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    profile_id = fields.Many2one('kw_emp_profile', string="Profile ID")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
        SELECT   
            ph.id as id,
            ph.emp_id  as employee_id,
            ep.id AS profile_id,
            ph.primary_skill_id as primary_skill_id,
            ph.secondary_skill_id as secondary_skill_id,
            ph.tertiary_skill_id as tertiary_skill_id
        FROM kw_employee_skill_expertise ph
        LEFT JOIN kw_emp_profile ep ON ep.emp_id = ph.emp_id
        )"""
        self.env.cr.execute(query)
