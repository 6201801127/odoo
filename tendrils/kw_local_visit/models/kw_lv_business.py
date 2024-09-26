import re
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_business(models.Model):
    _name = 'kw_lv_business'
    _description = 'Local Visit Business'
    _rec_name = "visit_for"

    lv_id = fields.Many2one(comodel_name='kw_lv_apply',string='Local Visit Id',ondelete='cascade')
    status = fields.Selection(related='lv_id.status',store=False)
    activity_name = fields.Many2one(comodel_name='kw_lv_activity_master',string='Activity',required=True,ondelete='restrict')
    sub_category = fields.Many2one(comodel_name='kw_lv_sub_category_master',string='Sub Category',required=True,ondelete='restrict')
    visit_for = fields.Selection(string="Visit For",selection=[('O','Opportunity'),('W','Work Order')],default='O',required=True)
    crm_id = fields.Many2one(comodel_name='crm.lead',string='Opportunity/Work Order',required=True,ondelete='restrict')
    purpose = fields.Text(string='Purpose')
    location = fields.Char(string='Location')
    meeting_id = fields.One2many('kw_lv_meeting','business_id',string='Meeting')
    color = fields.Integer()

    # Opportunity/Work list logic
    @api.onchange('visit_for')
    def _onchange_visit_for(self):
        self.crm_id = False
        if self.visit_for == 'O':
            return {'domain': {'crm_id': [('stage_id.code', '=', 'opportunity')]}}
        elif self.visit_for == 'W':
            return {'domain': {'crm_id': [('stage_id.code', '=', 'workorder')]}}