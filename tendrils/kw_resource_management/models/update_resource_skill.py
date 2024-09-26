# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from datetime import date
from odoo.exceptions import ValidationError


class SBUResourceTagging(models.Model):
    _name = 'update_resource_skill'
    _description = 'SBU Resource Skill Update'
    _auto = False
    _order = "date_of_joining desc"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    name = fields.Char(related='employee_id.name', string='Employee Name')
    designation = fields.Many2one('hr.job', string='Designation')
    department = fields.Many2one('hr.department', string='Department')
    division = fields.Many2one('hr.department',string='Division')
    section = fields.Many2one('hr.department',string='Practice')
    practise = fields.Many2one('hr.department',string='Section')
    date_of_joining = fields.Date(string='Date of Joining')
    job_branch_id = fields.Many2one('kw_res_branch', string='Location')
    applied_eos = fields.Boolean(compute='_compute_eos')
    primary_skill_id = fields.Many2one('kw_skill_master',string='Primary Skill')
    secondary_skill_id = fields.Many2one('kw_skill_master',string='Secondary Skill')
    tertial_skill_id = fields.Many2one('kw_skill_master',string='Tertiarry Skill')
    sbu_id = fields.Many2one('kw_sbu_master',string='SBU')
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT  row_number() over() as id,
                hr.id as employee_id,
                hr.job_id as designation,
                hr.name as name,
                hr.date_of_joining as date_of_joining,
                hr.department_id as department,
                hr.division as division,
                hr.section as section,
                hr.practise as practise,
                hr.job_branch_id as job_branch_id,
                hr.sbu_master_id as sbu_id,
                rsd.primary_skill_id as primary_skill_id,
			 	rsd.secondary_skill_id as secondary_skill_id,
			  	rsd.tertial_skill_id as tertial_skill_id
                from hr_employee as hr 
                join hr_department as hrd on hrd.id= hr.department_id
				left join resource_skill_data rsd on hr.id = rsd.employee_id
                where hr.active =true and hrd.code='BSS' 
                AND hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
    )""" % (self._table))

    @api.depends('employee_id')
    def _compute_eos(self):
        for rec in self:
            resignation = self.env['kw_resignation'].sudo().search(
                [('state', 'not in', ['reject', 'cancel']), ('applicant_id', '=', rec.employee_id.id)], limit=1)
            rec.applied_eos = True if resignation else False


class ResourceSkillUpdate(models.TransientModel):
    _name = "skill_update_wizard"
    _description = "Skill Wizard"

    @api.model
    def default_get(self, fields):
        res = super(ResourceSkillUpdate, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many(
        string='Resource Info',
        comodel_name='update_resource_skill',
        relation='skill_update_employee_rel',
        column1='wizard_id',
        column2='skill_id',
    )
    primary_skill_id = fields.Many2one('kw_skill_master',string='Primary Skill'  , domain=[('skill_type.skill_type', '=', 'Technical')])
    secondary_skill_id = fields.Many2one('kw_skill_master',string='Secondary Skill' , domain=[('skill_type.skill_type', '=', 'Technical')]) 
    tertial_skill_id = fields.Many2one('kw_skill_master',string='Tertiarry Skill'  , domain=[('skill_type.skill_type', '=', 'Technical')])

    # def update_resource_skill(self):
    #     query = ''
    #     for record in self.employee_ids:
    #         for rec in self:
    #             if rec.primary_skill_id:
    #                 query = f"update hr_employee set primary_skill_id={self.primary_skill_id.id} where id = {record.employee_id.id}"
    #         if len(query) > 0:
    #             self._cr.execute(query)

    def update_resource_skill(self):
        if not self.primary_skill_id and not self.secondary_skill_id and not self.tertial_skill_id:
            raise ValidationError("At least one skill should be selected before updating.")
        for record in self.employee_ids:
            if record.employee_id:
                existing_record = self.env['resource_skill_data'].search([('employee_id', '=', record.employee_id.id)], limit=1)

                if existing_record:
                    existing_record.write({
                                            'primary_skill_id': self.primary_skill_id.id if self.primary_skill_id.id else existing_record.primary_skill_id.id,
                                            'secondary_skill_id': self.secondary_skill_id.id if self.secondary_skill_id.id else existing_record.secondary_skill_id.id,
                                            'tertial_skill_id': self.tertial_skill_id.id if self.tertial_skill_id.id else existing_record.tertial_skill_id.id,
                    })
                else:
                    self.env['resource_skill_data'].create({
                                                        'employee_id': record.employee_id.id,
                                                        'primary_skill_id': self.primary_skill_id.id,
                                                        'secondary_skill_id': self.secondary_skill_id.id,
                                                        'tertial_skill_id': self.tertial_skill_id.id,
                    })