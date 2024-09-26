from odoo import api, fields, models, _


class kw_reply_reply(models.Model):
    _name = 'kw_reply_reply'
    _description = 'Reply Relational Model'
    _rec_name = 'reply_id'

    reply_id = fields.Many2one('kw_feedback_reply', string='Feedback Reply Id', ondelete='restrict')

    reply = fields.Text(string="Reply")
    states = fields.Selection([
        ('inprogress', 'Inprogress'),
        ('close', 'Close'),
    ], string='Status', index=True, copy=False, track_visibility='onchange')
    rpl_upload_attachment = fields.Binary(string='Attachment', attachment=True)
    file_name = fields.Char("File Name")
    is_editable = fields.Boolean(string="Is editable ?", default=False, compute="compute_last")
    is_current_user = fields.Boolean(string="Is current user ?", default=False, compute="compute_last")

    @api.multi
    def compute_last(self):
        current_uid = self._uid
        for reply in self:
            last_reply = reply.reply_id.reply_ids[-1]
            if reply.id == last_reply.id:
                reply.is_editable = True
            if reply.create_uid.id == current_uid:
                reply.is_current_user = True

    # edit button method
    @api.multi
    def admin_edit_reply(self):
        view_id = self.env.ref('kw_review_feedback.kw_reply_reply_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_reply_reply',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'res_id': self.id,
            'target': 'self',
            'flags': {'mode': 'edit', "toolbar": False}
        }
        return action
