from odoo import api, fields, models, _


class kw_feedback_reply(models.Model):
    _name = 'kw_feedback_reply'
    _description = 'Kwantify Reply'
    _rec_name = 'module_name'



    reply_ids = fields.One2many('kw_reply_reply','reply_id',string="Reply Ids")
    reply_create_check = fields.Boolean(default=False,string="Reply Check")
    feedback_id = fields.Many2one('kw_feedback',string="Feedback relation",default=lambda self: self.env.context.get('default_feedback_id', False), store=True, readonly=True,required=True, ondelete='cascade')
    module_name = fields.Many2one(related="feedback_id.module_name")
    feedback_type = fields.Selection(related="feedback_id.feedback_type")
    feedback_headline = fields.Char(related="feedback_id.feedback_headline",string="Feedback")
    description = fields.Text(related="feedback_id.description",string="Description")
    upload_attachment = fields.Binary(related="feedback_id.upload_attachment",string='Upload Attachment')
    file_name = fields.Char(string="File Name")
    states = fields.Selection(related ="feedback_id.state" ,selection=[
        ('inprogress','Inprogress'),
         ('close','Close'),
    ], string='Status',store=True, copy=False, track_visibility='onchange') 

    admin_check = fields.Boolean(string="Admin Check",default=False)
    user_check = fields.Boolean(string="User Check",default=False)
    button_check = fields.Boolean(string="Button Check",default=False)

    reply = fields.Text(string="Reply")
    
    rpl_upload_attachment = fields.Binary(string='Attachment', attachment=True)
    file_name = fields.Char("File Name")


# Manager Reply Button
    @api.multi
    def admin_btn_reply_of_reply(self):
        wizard_view_id = self.env.ref('kw_review_feedback.kw_reply_of_reply_wizard_view').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_reply_of_reply_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': wizard_view_id,
            'target': 'new',
            'context':{'feedback_reply_id':self.id}        
        }
        self.admin_check=True
        return action

# User Reply Button
    @api.multi
    def user_btn_reply_of_reply(self):
        wizard_view_id = self.env.ref('kw_review_feedback.kw_reply_of_reply_wizard_view').id
        # print(self,"Self====")
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_reply_of_reply_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': wizard_view_id,
            'target': 'new',
            'context':{'feedback_reply_id':self.id}        
        }
        self.user_check=True
        return action

