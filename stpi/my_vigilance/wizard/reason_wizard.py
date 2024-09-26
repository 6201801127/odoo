# Commit HIstory
# type aded for major and minor 7 June 2021(Gouranga kala)
# penalty_type added to vigillance while closing application 
# 
from odoo import api, fields, models,_

class Reason_wizard(models.TransientModel):
    _name = 'revert.vigilance.wizard'
    _description = "Revert Vigilance"


    res_id = fields.Integer('ID')
    res_model = fields.Char('Model')
    # Start : added on  7 June 2021(Gouranga kala)
    type = fields.Selection(string="Type",selection=[('major','Major'),('minor','Minor')])
    # End : added on  7 June 2021(Gouranga kala)
    reason_des = fields.Text('Remarks: ')
    penalty = fields.Many2one('vigilance.penalty', string='Penalty: ')
    # Start : added on  7 June 2021(Gouranga kala)
    @api.onchange('type')
    def validate_type(self):
        if self.type and self.penalty and self.penalty.type != self.type:
            self.penalty = False
    # End : added on  7 June 2021(Gouranga kala)
    def button_confirm(self):
        model_id = self.env[self.res_model].browse(self.res_id)
        _body = (_(
            (
                "Remarks(Close): <ul><b>{0}</b></ul> ").format(self.reason_des)))
        model_id.message_post(body=_body)
        model_id.penalty = self.penalty.id
        # Start : added on  7 June 2021(Gouranga kala)
        model_id.penalty_type = self.type
        # End : added on  7 June 2021(Gouranga kala)
        model_id.write({'state': 'closed'})
