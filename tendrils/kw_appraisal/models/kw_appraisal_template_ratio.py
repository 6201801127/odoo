# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.exceptions import  ValidationError



class KwAppraisalTemplateWiseRatio(models.Model):
    _name           = "kw_appraisal_template_ratio"
    _description    = "Appraisal Template wise ratio"
    
    year_id = fields.Many2one('kw_assessment_period_master', string='Appraisal Period')
    survey_template_ids = fields.Many2many('survey.survey','survey_template_wise_report_rel','survey_id','template_id',string='Template') 
    ratio_details_ids =  fields.One2many('kw_appraisal_ratio_details','ratio_id',string='Template Wise Ratio') 

    @api.onchange('survey_template_ids')
    def _get_template_details(self):
        self.ratio_details_ids = False
        vals = []
        for survey_template in self.survey_template_ids:
            assigned_template_rec = self.env['kw_appraisal_employee'].sudo().search([('kw_survey_id','=',survey_template.id)])
            for record in assigned_template_rec:
                template = self.env['kw_appraisal_template_score_view'].search([('survey_id','=',record.kw_survey_id.id)])
                vals.append([0, 0, {
                        'survey_id': record.kw_survey_id.id,
                        'employee_count': len(record.employee_id.ids),
                        'per_appraisal': template.per_appraisal if template else 0,
                        'per_inc': template.per_inc if template else 0,
                        'per_kra': template.per_kra if template else 0,
                        'per_training':template.per_training if template else 0,
                    }])
        self.ratio_details_ids = vals

    @api.onchange('year_id')
    def _get_survey_template_ids(self):
        self.survey_template_ids = False
        records =  self.env['kw_appraisal'].sudo().search([('year','=',self.year_id.id)])
        employee_ids = records.mapped('employee.kw_survey_id').ids
        self.survey_template_ids = [(6,0,employee_ids)]
        return {'domain': {'survey_template_ids': [('id', 'in', employee_ids)]}}





    def assign_ratio(self):
        for record in self.ratio_details_ids:
            template = self.env['kw_appraisal_template_score_view'].sudo()
            template_rec = template.search([('survey_id','=',record.survey_id.id)])
            data = {'employee_count': record.employee_count,
                'per_appraisal': record.per_appraisal,
                'per_inc':record.per_inc,
                'per_training':record.per_training,
                'per_kra':record.per_kra}
            if not template_rec:
                data['survey_id'] = record.survey_id.id,
                template.create(data)
            else:
                template_rec.write(data)

class KwAppraisalTemplateWiseRatio(models.TransientModel):
    _name           = "kw_appraisal_ratio_details"
    _description    = "Ratio Details"

    survey_id = fields.Many2one('survey.survey')
    per_appraisal = fields.Integer(string='Competency Weightage')
    per_kra = fields.Integer(string='KRA Weightage')
    per_training = fields.Integer(string='Training Weightage')
    per_inc = fields.Integer(string='Increment Percentage')
    ratio_id =  fields.Many2one('kw_appraisal_template_ratio',string='Template') 
    employee_count = fields.Integer(string='No. of Employees')


class KwAppraisalTemplateScoreRatio(models.Model):
    _name           = "kw_appraisal_template_score_view"
    _description    = "Ratio Details"

    survey_id = fields.Many2one('survey.survey')
    per_appraisal = fields.Integer(string='Competency Weightage')
    per_kra = fields.Integer(string='KRA Weightage')
    per_inc = fields.Integer(string='Increment Percentage')
    per_training = fields.Integer(string='Training Weightage')
    employee_count = fields.Integer(string='No. of Employees')

    @api.constrains('per_appraisal','per_kra','per_training')
    def _validate_total(self):
        for record in self:
            if (record.per_appraisal + record.per_kra + record.per_training) != 100:
                raise ValidationError("Sum of KRA, Competency and Training  Pecentage must be 100.")