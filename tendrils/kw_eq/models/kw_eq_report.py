# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools

class EQReport(models.Model):
    _name = 'kw_eq_estimate_report'
    _description = 'EQ Report'
    _auto = False
    _order = 'kw_oppertuinity_id desc'

    estimate_id = fields.Many2one('kw_eq_estimation') 
    kw_oppertuinity_id = fields.Many2one('crm.lead',string="Code | Name")    
    client_id = fields.Many2one('res.partner',string='Client Name')
    client_name = fields.Char(related='kw_oppertuinity_id.client_name')
    
    state = fields.Selection(string="Status",selection=[('version_1', 'Version 1'), ('version_2', 'Version 2'),('version_3', 'Version 3'),('version_4', 'Version 4'),('version_5', 'Version 5'),('version_6', 'Version 6'),('grant','Grant')])
    # pending_at_record= fields.Many2one('res.users',string="Pending At",compute="_compute_pending_at")
    pending_at = fields.Char(string="Pending At")
    effective_from = fields.Date(string="Effective Date")
    level_1_id = fields.Many2one('hr.employee',string="Authority 1")
    level_2_id = fields.Many2one('hr.employee',string="Authority 2")
    level_3_id = fields.Many2one('hr.employee',string="Authority 3")
    level_4_id = fields.Many2one('hr.employee',string="Authority 4")
    level_5_id = fields.Many2one('hr.employee',string="Authority 5")
    level_6_id = fields.Many2one('hr.employee',string="Authority 6")
    stage_id = fields.Many2one('crm.stage')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} as (
            SELECT 
            row_number() over() as id,
                a.id as estimate_id,
                a.kw_oppertuinity_id as kw_oppertuinity_id,
                a.client_id as client_id, 
                a.pending_at as pending_at,
                a.effective_from as effective_from,
                a.level_1_id as level_1_id,
                a.level_2_id as level_2_id,
                a.level_3_id as level_3_id,
                a.level_4_id as level_4_id,
                a.level_5_id as level_5_id,
                a.level_6_id as level_6_id,
                (select stage_id from crm_lead where id = kw_oppertuinity_id) as stage_id,
                a.state as state
            FROM 
                kw_eq_estimation a
        )"""
        self.env.cr.execute(query)



class EQRevisionReport(models.Model):
    _name = 'kw_eq_revision_report'
    _description = 'EQ Revision Report'
    _auto = False
    _order = 'kw_oppertuinity_id desc'

    estimate_id = fields.Many2one('kw_eq_revision') 
    kw_oppertuinity_id = fields.Many2one('crm.lead',string="Code | Name", domain=[('type', '=', 'opportunity'),('stage_id.code', '=', 'opportunity')])    
    client_id = fields.Many2one('res.partner',string='Client Name')
    client_name = fields.Char(related='kw_oppertuinity_id.client_name')
    
    state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'),('submit', 'Submitted'),('forward', 'Forwarded'),('recommend', 'Recommended'),('not_recommended', 'Not Recommended'),('grant', ' Granted'),('rejected', ' Rejected')],string="Status",default='draft')

    pending_at = fields.Char(string="Pending At")
    revised_level_1_id = fields.Many2one('hr.employee',string="Revised Authority 1")
    revised_level_2_id = fields.Many2one('hr.employee',string="Revised Authority 2")
    revised_level_3_id = fields.Many2one('hr.employee',string="Revised Authority 3")
    revised_level_4_id = fields.Many2one('hr.employee',string="Revised Authority 4")
    revised_level_5_id = fields.Many2one('hr.employee',string="Revised Authority 5")
    revised_level_6_id = fields.Many2one('hr.employee',string="Revised Authority 6")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} as (
            SELECT 
            row_number() over() as id,
                id as estimate_id,
                kw_oppertuinity_id as kw_oppertuinity_id,
                client_id as client_id, 
                pending_at as pending_at,
                revised_level_1_id as revised_level_1_id,
                revised_level_2_id as revised_level_2_id,
                revised_level_3_id as revised_level_3_id,
                revised_level_4_id as revised_level_4_id,
                revised_level_5_id as revised_level_5_id,
                revised_level_6_id as revised_level_6_id,
                state as state
            FROM 
                kw_eq_revision
        )"""
        self.env.cr.execute(query)