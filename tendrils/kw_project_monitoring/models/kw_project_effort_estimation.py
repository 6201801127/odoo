from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class KwProjectEffortEstimation(models.Model):
    _name = 'kw_project_effort_estimation'
    _description = 'Effort Estimation'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project')
    project_manager_id = fields.Many2one('hr.employee',string='Project Manager Name',related='project_id.emp_id')
    project_ref_code = fields.Char(string='Project Id/Ref Code',related='project_id.code')
    estimation_total_id = fields.One2many('kw_effort_estimation_total', 'estimation_id',string='Estimation')
    enviromental_complexity_id = fields.One2many('kw_enviromental_complexity_factor', 'estimation_id',string='Estimation')
    unadjusted_use_case_id = fields.One2many('kw_unadjusted_use_case_weight', 'estimation_id',string='Estimation')
    total_calculated_factor = fields.Float(string='Total Calculated Factor', compute='_compute_total_calculated_factor', store=True)
    total_calculated_factor1 = fields.Float(string='Total Calculated Factor', compute='_compute_total_calculated_factor', store=True)
    total_effective =fields.Float(string='Total Effective',compute='_compute_total_calculated_factor', store=True)
    unadjusted_actor_id = fields.One2many('kw_unadjusted_actor_weight', 'estimation_id',string='Estimation')
    total_actor_weight = fields.Float(string='Total UAW', compute='_compute_total_calculated_factor', store=True)
    toal_tcf = fields.Float(string='Total TCF', compute='_compute_total_calculated_factor', store=True)
    toal_ecf = fields.Float(string='Total ECF', compute='_compute_total_calculated_factor', store=True)
    total_uucp = fields.Float(string='Total UUCP', compute='_compute_total_calculated_factor', store=True)
    total_aucp = fields.Float(string='Total AUCP', compute='_compute_total_calculated_factor', store=True)
    productivity_factor = fields.Float(string='Productivity Factor', compute='_compute_total_calculated_factor', store=True)
    estimated_effort = fields.Float(string='Estimated Effort', compute='_compute_total_calculated_factor', store=True)
    estimation_baseline_id = fields.One2many('kw_estimation_baseline', 'estimation_id',string='Estimation')

    @api.constrains('project_id')
    def _check_unique_project_id(self):
        for record in self:
            existing_records = self.search([('project_id', '=', record.project_id.id)])
            if len(existing_records) > 1:
                raise ValidationError('Effort estimation for this project already exists.')

    @api.model
    def create(self, vals):
        record = super(KwProjectEffortEstimation, self).create(vals)
        record._update_estimation_baseline()
        return record

    def write(self, vals):
        res = super(KwProjectEffortEstimation, self).write(vals)
        self._update_estimation_baseline()
        return res

    def _update_estimation_baseline(self):
        for record in self:
            baseline_vals = {
                'tcf_count': record.toal_tcf,
                'ecf_count': record.toal_ecf,
                'uucw_count': record.total_uucp,
                'uaw_count': record.total_actor_weight,
                'estimated_effort': record.estimated_effort,
                'modified_by': self.env.user.employee_ids.id,
                'modified_on': fields.Date.today(),
                'estimation_id': record.id,
            }
            self.env['kw_estimation_baseline'].create(baseline_vals)



    @api.model
    def default_get(self, fields):
        res = super(KwProjectEffortEstimation, self).default_get(fields)
        if 'estimation_total_id' in fields:
            res['estimation_total_id'] = [
                ((0, 0, {'name': 'T1','description': 'Distributed System','weight': 2,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T2','description': 'Performance','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T3','description': 'End User Efficiency','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T4','description': 'Complex internal Processing','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T5','description': 'Reusability','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T6','description': 'Easy to install','weight': 0.5,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T7','description': 'Easy to use','weight': 0.5,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T8','description': 'Portable','weight': 2,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T9','description': 'Easy to change','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T10','description': 'Concurrent','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T11','description': 'Special security features','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T12','description': 'Provides direct access for third parties','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'T13','description': 'Special user training facilities are required','weight': 1,'perceived_complexity': '0', })),
                
            ]
        if 'enviromental_complexity_id' in fields:
            res['enviromental_complexity_id'] = [
                ((0, 0, {'name': 'E1','description': 'Familarity with UML','weight': 1.5,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E2','description': 'Application Experience','weight': 0.5,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E3','description': 'Object Oriented Experience','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E4','description': 'Lead analyst capability','weight': 0.5,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E5','description': 'Motivation','weight': 1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E6','description': 'Stable Requirements','weight': 2,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E7','description': 'Part-time workers','weight': -1,'perceived_complexity': '0', })),
                ((0, 0, {'name': 'E8','description': 'Difficult programming language','weight': 2,'perceived_complexity': '0', })),
            ]

        if 'unadjusted_use_case_id' in fields:
            res['unadjusted_use_case_id'] = [
                ((0, 0, {'name': 'Simple','description': 'A simple user interface and touches only a single database entity; its success scenario has 3 steps or less; its implementation involves less than 5 classes.','weight': 5,})),
                ((0, 0, {'name': 'Average','description': 'More interface design and touches 2 or more database entities; between 4 to 7 steps; its implementation involves between 5 to 10 classes.','weight': 10,})),
                ((0, 0, {'name': 'Complex','description': 'Involves a complex user interface or processing and touches 3 or more database entities; over seven steps; its implementation involves more than 10 classes.','weight': 15,})),
            ]

        if 'unadjusted_actor_id' in fields:
            res['unadjusted_actor_id'] = [
                ((0, 0, {'name': 'Simple','description': 'The Actor represents another system with a defined API.','weight': 1,})),
                ((0, 0, {'name': 'Average','description': 'The Actor represents another system interacting through a protocol, like TCP/IP.','weight': 2,})),
                ((0, 0, {'name': 'Complex','description': 'The Actor is a person interacting via an interface.','weight': 3,})),
            ]

        return res
    
    @api.depends('estimation_total_id.calculated_factor','enviromental_complexity_id.calculated_factor','unadjusted_use_case_id.effective','unadjusted_actor_id.result')
    def _compute_total_calculated_factor(self):
        for record in self:
            record.total_calculated_factor = sum(line.calculated_factor for line in record.estimation_total_id)
            record.total_calculated_factor1 = sum(line.calculated_factor for line in record.enviromental_complexity_id)
            record.total_effective = sum(line.effective for line in record.unadjusted_use_case_id)
            record.total_actor_weight = sum(line.result for line in record.unadjusted_actor_id)
            record.toal_tcf = (0.6 + (.01*record.total_calculated_factor))
            record.toal_ecf = (1.4 + (-0.3*record.total_calculated_factor1))
            record.total_uucp = (record.total_effective + record.total_actor_weight)
            record.total_aucp = (record.toal_tcf * record.toal_ecf * record.total_uucp)
            record.productivity_factor = 18
            record.estimated_effort =  (record.toal_tcf * record.toal_ecf * record.total_uucp * record.productivity_factor)

    
    @api.onchange('project_id')
    def onchange_project_id(self):
        for record in self:
            data = self.env['kw_project_add_use_case_master'].sudo().search([('project_name', '=', record.project_id.id)])
            if data:
                complexity_counts = {'Simple': 0, 'Average': 0, 'Complex': 0}
                effective_sums = {'Simple': 0.0, 'Average': 0.0, 'Complex': 0.0}
                
                for rec in data.use_case_ids:
                    complexity_level = rec.complexity_level.capitalize()
                    if complexity_level in complexity_counts:
                        complexity_counts[complexity_level] += 1
                        effective_sums[complexity_level] += rec.effective_uc_point
                        # print("effective_sums[complexity_level]===============",effective_sums[complexity_level])

                unadjusted_use_case_ids = self.env['kw_unadjusted_use_case_weight'].sudo().search([])

                for weight in unadjusted_use_case_ids:
                    if weight.name in complexity_counts:
                        weight.sudo().write({
                            'no_of_use_cases': complexity_counts[weight.name],
                            'effective': effective_sums[weight.name],
                        })
    
    def update_effort_estimation(self):
        pass

    def update_baseline(self):
        pass

class EffortEstimationTotal(models.Model):
    _name = 'kw_effort_estimation_total'
    _description = 'Effort Estimation Total'

    name = fields.Char(string='Technical Factor')
    description = fields.Char(string='Technical Factor Description',)
    weight = fields.Float(string='Weight (W)', default=1.0)
    perceived_complexity = fields.Selection([(str(i), str(i)) for i in range(6)], string='Perceived Complexity (PC)', required=True, default='0')
    calculated_factor = fields.Float(string='Calculated Factor (W*PC)', compute='_compute_calculated_factor', store=True)
    total_factor = fields.Float(string='Total Factor', compute='_compute_total_factor', store=True)
    estimation_id = fields.Many2one('kw_project_effort_estimation',string='Efforts')

    @api.depends('weight', 'perceived_complexity',)
    def _compute_calculated_factor(self):
        for record in self:
            record.calculated_factor = record.weight * float(record.perceived_complexity)

class EnviromentalComplexityFactor(models.Model):
    _name = 'kw_enviromental_complexity_factor'
    _description = 'Enviromental Complexity Factor'

    name = fields.Char(string='Enviromental Factor')
    description = fields.Char(string='Enviromental Factor Description',)
    weight = fields.Float(string='Weight (W)', default=1.0)
    perceived_complexity = fields.Selection([(str(i), str(i)) for i in range(6)], string='Perceived Complexity (PC)', required=True, default='0')
    calculated_factor = fields.Float(string='Calculated Factor (W*PC)', compute='_compute_calculated_factor', store=True)
    total_factor = fields.Float(string='Total Factor', compute='_compute_total_factor', store=True)
    estimation_id = fields.Many2one('kw_project_effort_estimation',string='Efforts')

    @api.depends('weight', 'perceived_complexity',)
    def _compute_calculated_factor(self):
        for record in self:
            record.calculated_factor = record.weight * float(record.perceived_complexity)

class UnadjustedUseCaseWeight(models.Model):
    _name = 'kw_unadjusted_use_case_weight'
    _description = 'Unadjusted Use Case Weight'

    name = fields.Char(string='Case Type')
    description = fields.Char(string='Description',)
    weight = fields.Float(string='Weight (W)', default=1.0)
    no_of_use_cases = fields.Float(string='No.of Use Cases(UC)')
    standard = fields.Float(string='Standard',compute='_compute_standard_result',store=True)
    effective = fields.Float(string='Effective')
    estimation_id = fields.Many2one('kw_project_effort_estimation',string='Efforts')

    @api.depends('weight','no_of_use_cases')
    def _compute_standard_result(self):
        for record in self:
            record.standard = record.weight * record.no_of_use_cases

class UnadjustedActorWeight(models.Model):
    _name = 'kw_unadjusted_actor_weight'
    _description = 'Unadjusted Actor Weight'

    name = fields.Char(string='Actor Type')
    description = fields.Char(string='Description',)
    weight = fields.Float(string='Weight (W)', default=1.0)
    no_of_actor = fields.Float(string='No.of Actor (A)')
    result = fields.Float(string='Result (W*A)',compute='_compute_calculated_factor',store=True)
    estimation_id = fields.Many2one('kw_project_effort_estimation',string='Efforts')

    @api.depends('weight', 'no_of_actor',)
    def _compute_calculated_factor(self):
        for record in self:
            record.result = record.weight * record.no_of_actor


class EstimationBaseline(models.Model):
    _name = 'kw_estimation_baseline'
    _description = 'View Baseline'

    baseline_count = fields.Float(string='Baseline Count')
    tcf_count = fields.Float(string='TCF Count',)
    ecf_count = fields.Float(string='ECF Count')
    uucw_count = fields.Float(string='UUCW Count')
    uaw_count = fields.Float(string='UAW Count')
    estimated_effort = fields.Float(string='Estimated Effort')
    modified_by = fields.Many2one('hr.employee', string='Start Date')
    modified_on = fields.Date(string='End Date')
    estimation_id = fields.Many2one('kw_project_effort_estimation',string='Efforts')

    @api.depends('weight', 'no_of_actor',)
    def _compute_calculated_factor(self):
        for record in self:
            record.result = record.weight * record.no_of_actor

    
          