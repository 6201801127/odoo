from odoo import api, fields, models,_


class Reason_wizard(models.TransientModel):
    _name = 'revert.requisition.wizard'
    _description = "Revert Requisition"


    res_id = fields.Integer()
    res_model = fields.Char('Model')
    reason_des = fields.Char('Reason')

    def button_confirm(self):
        model_id = self.env[self.res_model].browse(self.res_id)
        _body = (_(
            (
                "Reason of Reverting: <ul><b>{0}</b></ul> ").format(self.reason_des)))
        model_id.message_post(body=_body)
        model_id.write({'state':'draft'})
