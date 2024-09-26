# -*- coding: utf-8 -*-
import re
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class kw_feedback(models.Model):
    _name = 'kw_feedback'
    _rec_name = 'module_name'
    _description = 'Kwantify Review and Feedback Module'

    module_name = fields.Many2one('kw_choose_module',string="Module Name",domain="[('active_module','=',True)]",required=True, ondelete='restrict')
    feedback_type = fields.Selection(
        string='Feedback Type',
        selection=[('Appreciation', 'Appreciation'), ('Issue', 'Issue'),('Suggestion','Suggestion')],required=True)
    feedback_reply_ids = fields.One2many('kw_feedback_reply','feedback_id',string="Feedback Reply Relation") 
    feedback_headline = fields.Char(string="Feedback",required=True)
    description = fields.Text(string="Description",required=True)
    state = fields.Selection([
        ('inprogress','Inprogress'),
        ('close','Close'),
    ], string='Status',default='inprogress')   
    upload_attachment = fields.Binary(string='Upload Attachment', attachment=True)
    file_name = fields.Char("File Name")

    computed_reply = fields.Integer(string="Reply", compute='get_computed_reply')
    rply_length_check = fields.Boolean(default=False,compute='get_computed_reply')
    admin_color_check = fields.Boolean(string="admin color check",default=False)
    user_color_check = fields.Boolean(string="user color check",default=False)
    

# Return Reply action 
    @api.multi
    def get_reply(self):
        feedback_rec_id = self.env['kw_feedback'].sudo().search([('create_uid','=',self._uid),('id','=',self.id)],limit=1)
        reply = self.env['kw_feedback_reply'].sudo().search([('feedback_id','=',feedback_rec_id.id)],limit=1)
        reply.feedback_id.user_color_check=False
        create_edit_view_id = self.env.ref('kw_review_feedback.kw_reply_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_feedback_reply',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': create_edit_view_id,
            'res_id':reply.id,
            'target': 'self',
            'domain':[('feedback_id','=',self.id)]           
        }
        return action

# Reopen method
    @api.multi
    def btn_reopen(self):
        self.state = 'inprogress'
        # wizard_view_id = self.env.ref('kw_review_feedback.kw_reply_of_reply_wizard_view').id
        # reply_id = self.env['kw_feedback_reply'].sudo().search([('feedback_id','=',self.id)],limit=1)
        # action = {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'kw_reply_of_reply_wizard',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'view_id': wizard_view_id,
        #     'target': 'new',
        #     'context':{'default_is_reopen':True,'default_feedback_id':self.id,'feedback_reply_id':reply_id.id}
        # }
        # return action


# Reply count compute method
    @api.multi
    def get_computed_reply(self):
        for record in self:
            if len(record.feedback_reply_ids.reply_ids) == 0:
                record.rply_length_check = True
            else:
                record.rply_length_check=False

            for feed_reply_ids in record.feedback_reply_ids:
                for reply_of_reply in feed_reply_ids:
                    reply_of_reply_ids = len(reply_of_reply.reply_ids.ids)
                    record.computed_reply = reply_of_reply_ids

# Manager action button method
    def go_to_action_view(self):
        edit_view_id = self.env.ref('kw_review_feedback.kw_reply_edit_form').id
        create_edit_view_id = self.env.ref('kw_review_feedback.kw_reply_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_feedback_reply',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'self',
            'flags':{'mode':'readonly'}       
        }
        
        reply = self.env['kw_feedback_reply'].sudo().search([('feedback_id','=',self.id),('module_name','=',self.module_name.id)],limit=1)
        # print("Reply==",reply)
        if reply:
            action['res_id'] = reply.id
            action['view_id'] = edit_view_id
            reply.feedback_id.admin_color_check = False
        else:
            action['view_id'] = create_edit_view_id
            action['context'] = { 'default_feedback_id': self.id}
        return action

# Feedback create method
    @api.model
    def create(self, vals):
        record = super(kw_feedback, self).create(vals)
        self.env.user.notify_success(message='Feedback submitted successfully.')
        return record