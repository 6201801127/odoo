from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from odoo import exceptions,_

class kwantify_survey_publish_wizard(models.TransientModel):
    _name       ='kwantify_survey_publish_wizard'
    _description= 'Publish Survey wizard'

    def _get_default_kwantify_survey(self):
        datas   = self.env['kw_surveys_details'].browse(self.env.context.get('active_ids'))
        return datas

    surveys    = fields.Many2many('kw_surveys_details',readonly=1, default=_get_default_kwantify_survey)

    @api.multi
    def publish_survey(self):
        for record in self.surveys:
            if record.state == '3':

                record.state = '4'

        self.env.user.notify_success("Survey Published Successfully.")
        return {'type': 'ir.actions.act_window_close'}