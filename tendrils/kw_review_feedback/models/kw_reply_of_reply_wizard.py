from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions,_
from datetime import date

class kw_reply_of_reply_wizard(models.TransientModel):
    _name='kw_reply_of_reply_wizard'
    _description = 'Reply wizard'

    def _get_default_confirm(self):
        datas = self.env['kw_feedback_reply'].browse(self.env.context.get('active_ids'))
        return datas

    get_reply_id = fields.Many2one('kw_feedback_reply',string="Get Reply Id",default=lambda self: self.env.context.get('feedback_reply_id', False), store=True, readonly=True,required=True)
    reply_of_reply_id = fields.Many2many('kw_feedback_reply',readonly=1, default=_get_default_confirm)

    reply = fields.Text(string="Reply",required=True)
    states = fields.Selection([
        ('inprogress','Inprogress'),
         ('close','Close'),
    ], string='Status', index=True, copy=False, track_visibility='onchange',default='inprogress') 
    rpl_upload_attachment = fields.Binary(string='Attachment', attachment=True)
    file_name = fields.Char("File Name")
    is_reopen = fields.Boolean(string="Is reopen",default=False)
    feedback_id = fields.Many2one('kw_feedback',string = "Get Feedback Id", ondelete='restrict')

# Reopen method
    # @api.multi
    # def action_confirm(self):
    #     print("Reply id",self.get_reply_id)
    #     feedback_rec = self.env['kw_feedback'].sudo().search([('id','=',self.feedback_id.id)],limit=1)
    #     reply_of_reply_data = self.env['kw_reply_reply']
    #     reply_data = reply_of_reply_data.create({
    #         'reply_id':self.get_reply_id.id,
    #         'reply':self.reply,
    #         'rpl_upload_attachment':self.rpl_upload_attachment,
    #         'file_name':self.file_name
    #     })

    #     feedback_rec.state = 'inprogress'
    #     if check_id.user_check == True:
    #         check_id.button_check = False
    #         check_id.user_check = False
    #         check_id.feedback_id.admin_color_check = True



# Wizard submit button
    @api.multi
    def button_submit(self):
        check_id = self.env['kw_feedback_reply'].sudo().search([('id','=',self.get_reply_id.id)],limit=1)
        reply_of_reply_data = self.env['kw_reply_reply']
        reply_data = reply_of_reply_data.create({
            'reply_id':self.get_reply_id.id,
            'reply':self.reply,
            'states':self.states,
            'rpl_upload_attachment':self.rpl_upload_attachment,
            'file_name':self.file_name
        })

        # reply_data.edit_boolean = True
        

        if check_id.admin_check == True:
            check_id.button_check = True
            check_id.admin_check = False
            check_id.feedback_id.user_color_check = True

        if check_id.user_check == True:
            check_id.button_check = False
            check_id.user_check = False
            check_id.feedback_id.admin_color_check = True
        

        if check_id.reply_ids.ids:
            check_id.reply_create_check = True
        if self.states == 'close':
            check_id.feedback_id.state = 'close'
            check_id.states = 'close'
        
        if len(check_id.reply_ids) == 1:
            prvs_user = check_id.feedback_id.create_uid
            module = check_id.module_name.choose_module_id.shortdesc
            user = reply_data.create_uid
        else:
            last_record = check_id.reply_ids.sorted(lambda r : r.id)[-2]
            # print(prvs_id,'prvs id=====')
            # prvs_id.edit_boolean = False
            user = reply_data.create_uid
            module = check_id.module_name.choose_module_id.shortdesc
            prvs_user = last_record.create_uid


        # channel sent
        ch_obj = self.env['mail.channel']
        channel1 = prvs_user.name + ', ' + user.name
        channel2 = user.name + ', ' + prvs_user.name
        channel = ch_obj.sudo().search(
            ["|", ('name', 'ilike', str(channel1)), ('name', 'ilike', str(channel2))])
        if not channel:
            channel_id = ch_obj.channel_get([prvs_user.partner_id.id])
            channel = ch_obj.browse([channel_id['id']])
        channel[0].message_post(
                    body=f"You have a new reply for <b> {module} </b> module.",
                    message_type='comment', subtype='mail.mt_comment',
                    author_id=user.partner_id.id,
                    notif_layout='mail.mail_notification_light')

        # Mail sent
        template = self.env.ref('kw_review_feedback.kw_review_feedback_template')
        template.with_context(module=module,user=user,prvs_user=prvs_user).send_mail(reply_data.id)
        self.env.user.notify_success(message='Mail sent successfully')

        

