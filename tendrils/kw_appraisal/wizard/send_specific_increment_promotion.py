import base64
import datetime
from dateutil import relativedelta
from odoo import api, models, fields
from odoo.exceptions import UserError
import tempfile
import os
import decimal



class SendSpecificIncPro(models.TransientModel):
    _name = 'send_specific_increment_promotion'
    _description = 'send specific wizard'

    
    @api.model
    def default_get(self, fields):
        res = super(SendSpecificIncPro, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'increment_promotion_ids': active_ids,
        })
        return res
   
    increment_promotion_ids = fields.Many2many(string='Increment Promotion Info',
        comodel_name='shared_increment_promotion',
        relation='send_specific_increment_promotion_rel',
        column1='increment_id',
        column2='share_id')
    sent_by_current_user = fields.Boolean(string="Sent by Current User",compute='_compute_sent_by_current_user')
    
    def action_send_to_hod(self):
        self.env['shared_increment_promotion'].action_send_to_hod()

    def action_send_to_chro_iaa(self):
        self.env['shared_increment_promotion'].action_send_to_chro()

    def action_send_to_chro_hr(self):
        self.env['shared_increment_promotion'].action_send_to_chro_hr()

    def action_send_publish_record_to_chro(self):
        self.env['shared_increment_promotion'].action_send_publish_record_to_chro()
    
    def action_send_to_hr(self):
        self.env['shared_increment_promotion'].action_send_to_hr()

    def action_send_to_ceo(self):
        self.env['shared_increment_promotion'].action_send_to_ceo()

    def action_ceo_submit(self):
        self.env['shared_increment_promotion'].action_ceo_submit()

    def calculate_ctc(self):
        for rec in self.increment_promotion_ids:
            rec.actual_ctc = rec.current_ctc + rec.actual_increment_amount
            rec.revised_ctc = rec.current_ctc + rec.revised_amount if rec.revised_amount > 0 else 0

        
    @api.depends('increment_promotion_ids.status')
    def _compute_sent_by_current_user(self):
        for wizard in self:
            any_completed = any(promotion.status == 'completed' for promotion in wizard.increment_promotion_ids)
            wizard.sent_by_current_user = any_completed

    # def calculate_score(self):
    #     all_increments = self.env['shared_increment_promotion'].sudo().search([('add_in_appraisal','=','yes'),('appraisal_id','!=',False)])
    #     if all_increments:
    #        for record in all_increments:
    #             if record.appraisal_id:
    #                 record.total_final_score= record.appraisal_id.total_score
    #                 record.proposed_increment =  record.appraisal_id.increment_percentage


        






