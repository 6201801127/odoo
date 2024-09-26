from odoo import models, fields, api
from datetime import date, datetime, time

class KWlifecyclemaster(models.Model):
    _name = 'kw_life_cycle_master'
    _rec_name = 'life_cycle_name'

    sl_no = fields.Integer(readonly=True,string="SL#", default=lambda self: self.env['kw_life_cycle_master'].search_count([]) + 1)
    project_type = fields.Many2one('kw_project_type_master',string="Project Type",required=True)
    life_cycle_name = fields.Char(string="LifeCycle Name",required=True)
    active = fields.Boolean(string="Active",default=True)
    description = fields.Text(string="Description")


class KWlifecyclePhasemaster(models.Model):
    _name = 'kw_life_cycle_phase_master'
    _rec_name = 'phase_name'

    life_cycle_id = fields.Many2one('kw_life_cycle_master',string="Life Cycle Name",required=True)
    phase_name = fields.Char(string="Phase Name",required=True)
    phase_order = fields.Integer(string="Phase Order",required=True)
    phase_type = fields.Selection([('dev','Development'),('test','Testing'),('uat','UAT'),('other','Others')],string="Phase Type",default='other')
    
    description = fields.Text(string="Description",required=True)
    
class TaskTypemaster(models.Model):
    _name = 'pm_task_type_master'
    _rec_name = 'task_type'

    cycle_id = fields.Many2one('kw_life_cycle_master',string="Life Cycle Name",required=True)
    life_cycle_phase_id = fields.Many2one('kw_life_cycle_phase_master',string="Life Cycle Phase",required=True)
    task_type = fields.Selection([('dev','Development'),('test','Testing'),('uat','UAT'),('other','Others')],string="Task Type",required=True,default='other')
    color_order = fields.Char(string="Color Code",required=True)
    description = fields.Text(string="Description",required=True)
    
    
    
class ReviewTypemaster(models.Model):
    _name = 'kw_review_type_master'
    _rec_name = 'review_type'

    life_cycle_id = fields.Many2one('kw_life_cycle_master',string="Life Cycle Name",required=True)
    life_cycle_phase_id = fields.Many2one('kw_life_cycle_phase_master',string="Life Cycle Phase",required=True)
    review_type = fields.Selection([('dev','Development'),('test','Testing'),('uat','UAT'),('other','Others')],string="Review Type",required=True,default='other')
    color_order = fields.Char(string="Color Code",required=True)
    
    description = fields.Text(string="Description",required=True)
    
class ArticatInfomaster(models.Model):
    _name = 'kw_artifact_info_master'
    _rec_name = 'artifact_name'

    life_cycle_id = fields.Many2one('kw_life_cycle_master',string="Life Cycle Name",required=True)
    life_cycle_phase_id = fields.Many2one('kw_life_cycle_phase_master',string="Life Cycle Phase",required=True)
    artifact_name = fields.Char(string="Artifact Name",required=True)
    artifact_initial = fields.Char(string="Artifact Initial",required=True)
    artifact_type = fields.Selection([('ci','CI'),('nci','NCI')],string="Artifact Type",required=True,default='ci')
    
    artifact_details = fields.Text(string="Description",required=True)
    
    
    
class ArchitectureTypemaster(models.Model):
    _name = 'project_architecture_type_master'
    _rec_name = 'architecture_name'

    architecture_name = fields.Char(string="Architecture Name",required=True)
    active = fields.Boolean(string="Active",default=True)
    description = fields.Text(string="Description")

