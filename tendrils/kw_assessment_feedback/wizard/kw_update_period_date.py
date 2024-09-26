from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from datetime import datetime,date

class kw_update_period_date_wizard(models.TransientModel):
    _name       ='kw_update_period_date_wizard'
    _description= 'Update period Date wizard'

    def _get_default_assessment_periods(self):
        datas   = self.env['kw_feedback_assessment_period'].browse(self.env.context.get('active_ids'))
        return datas

    periods    = fields.Many2many('kw_feedback_assessment_period',readonly=1, default=_get_default_assessment_periods)
    from_date   = fields.Date(string='From Date')
    to_date     = fields.Date(string='To Date')
    assessment_date = fields.Date(string='Assessment Date')

    @api.onchange('from_date','to_date','assessment_date')
    def date_validation(self):
        if self.from_date and self.to_date and (self.from_date > self.to_date):
            raise ValidationError('End date must be greater than start date.')
        if self.assessment_date and self.assessment_date < date.today():
            raise ValidationError('Assessment date must be greater than current date.')

    @api.multi
    def update_date(self):
        self.ensure_one()
        if self._context.get('value1'):
            for record in self.periods:
                if record.state not in ['2']:
                    record.write({
                        'from_date':self.from_date,
                        'to_date':self.to_date
                    })
            self.env.user.notify_success("Periodic Date Updated Successfully.")

        elif self._context.get('value2'):
            for record in self.periods:
                if record.state not in ['2']:
                    record.write({
                        'assessment_date':self.assessment_date
                    })
            self.env.user.notify_success("Final Assessment Date Updated Successfully.")
        else:
            pass

        return {'type': 'ir.actions.act_window_close'}