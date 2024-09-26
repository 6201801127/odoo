from odoo import api, fields, models,_


class Reason_wizard(models.TransientModel):
    _name = 'reason.wizard'
    _description = "Reason Wizard"


    res_id = fields.Integer()
    res_model = fields.Char('Model')
    reason_des = fields.Char('Reason')
    action_taken = fields.Selection([('approve', 'Approve'),
                                    ('reject', 'Reject'),
                                    ], string='Action Taken')

    def button_confirm(self):
        model_id = self.env[self.res_model].browse(self.res_id)
        print('===================', self.action_taken)
        if self.action_taken == 'approve':
            _body = (_(
                (
                    "Reason for Approval: <ul><b style='color:green'>{0}</b></ul> ").format(self.reason_des)))
        elif self.action_taken == 'reject':
            _body = (_(
                (
                    "Reason for Rejection: <ul><b style='color:red'>{0}</b></ul> ").format(self.reason_des)))
        else:
            _body = (_(
                (
                    "<ul><b>{0}</b></ul> ").format(self.reason_des)))
        model_id.message_post(body=_body)
