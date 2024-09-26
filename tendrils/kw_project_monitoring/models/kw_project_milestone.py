from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class KwProjectMilestone(models.Model):
    _name = 'kw_project_milestone'
    _description = 'Project Milestone'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project',string='Project',track_visibility='onchange')
    workorder_id = fields.Many2one('crm.lead',string='Workorder Name',domain=[('type','=','opportunity'),('stage_id.code','=','workorder')],track_visibility='onchange')
    milestone_code = fields.Char(string="Milestone Code",track_visibility='onchange')
    milestone_date = fields.Date(string="Milestone Date",track_visibility='onchange')
    artifact_deliverable = fields.Selection([('yes','Yes'),('no','No')],track_visibility='onchange',string='Artifact Deliverable')
    artifact_name = fields.Many2many('kw_artifact_info_master','milestone_artifact_details','milestone_id', 'artifact_id',string="Artifact Name",track_visibility='onchange')
    module_deliverable = fields.Selection([('yes','Yes'),('no','No')],track_visibility='onchange',string='Module Deliverable')
    module_name = fields.Many2one('kw_project.module',string="Module Name")
    tag_to_billing = fields.Selection([('yes','Yes'),('no','No')],track_visibility='onchange',string='Tag To Billing')
    amount = fields.Float(string="Amount(INR)",track_visibility='onchange')
    milestone_name = fields.Text(string="Milestone Name",track_visibility='onchange')
    penalty_clause = fields.Text(string='Penalty Clause',track_visibility='onchange')
    is_milestone_added = fields.Boolean("Is milestone added",default=False)
    is_component_added = fields.Boolean("Is Component Added",default=False)
    component_type_id = fields.One2many("kw_component_type_master",'milestone_id',string="Component Type")
    component_name= fields.Many2one("kw_component_type_master",string="Component Name")
    component_code= fields.Char(related='component_name.component_code',store=True)
    component_amount= fields.Float(related='component_name.component_amount',store=True)
    milestone_status = fields.Selection([('inprogress','In Progress'),('closed','Closed')],track_visibility='onchange',string='Status')
    closing_date = fields.Date(string="Closing Date",track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string="Currency")
    rest_billing_amount = fields.Float(string="Rest Billing Amount",track_visibility='onchange')
    artifact_review_ids = fields.One2many('kw_artifact_review_details','artifact_id',string='Review Details')
    review_date = fields.Date(string='Review Date')
    ready_to_bill = fields.Boolean('Is ready to bill')
    remark = fields.Text("Remark")
    is_reviewing = fields.Boolean("Is Reviewing",default=False)
    review_history_log = fields.One2many('kw_review_history_log','review_id',)
    

    @api.model
    def create(self, vals):
        vals['milestone_code'] = self.env['ir.sequence'].next_by_code('kw.project.milestone.code') or '/'
        res = super(KwProjectMilestone, self).create(vals)
        return res
    
    @api.multi
    def add_milestone_details(self):
        self.is_milestone_added =True

    @api.multi
    def add_component_details(self):
        self.is_component_added =True

    @api.multi
    def review_milestone(self):
        self.is_reviewing = True
        return {
            'name': 'Project Milestone',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'kw_project_milestone',
            'res_id': self.id,
            'target': 'self',
            'flags':{'mode':'edit'}
        }
    @api.multi
    def submit_review(self):
            self.env['kw_review_history_log'].create({
                'last_review_date': self.review_date,  # Assuming review_date is set somewhere
                'status': self.milestone_status,
                'review_remarks': self.remark,
                'review_id': self.id,
            })
class KwProjectMilestoneArtifactReviewDetails(models.Model):
    _name = 'kw_artifact_review_details'
    _description = 'Artifact Review Details'
    _rec_name = 'artifact_name'

    artifact_name = fields.Many2one('kw_artifact_info_master',string="Artifact Name",track_visibility='onchange')
    artifact_status = fields.Selection([('notstarted','Not Started'),('inprogress','In Progress'),('complete','Complete')],track_visibility='onchange',string='Status')
    artifact_review_remark = fields.Text('Remark')
    artifact_id = fields.Many2one('kw_project_milestone')

class KwReviewHistoryLog(models.Model):
    _name = 'kw_review_history_log'
    _description = 'Review History Log'

    last_review_date = fields.Date(string="Last Review Date",track_visibility='onchange')
    status = fields.Selection([('notstarted','Not Started'),('inprogress','In Progress'),('complete','Complete')],track_visibility='onchange',string='Status')
    review_remarks = fields.Text('Review Remarks')
    review_id = fields.Many2one('kw_project_milestone')


