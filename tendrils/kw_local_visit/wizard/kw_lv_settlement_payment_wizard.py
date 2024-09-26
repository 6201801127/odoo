from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions,_
import pytz
from datetime import datetime, timedelta,date

class kw_lv_settlement_payment_wizard(models.TransientModel):
    _name='kw_lv_settlement_payment_wizard'
    _description = 'Settlement Payment wizard'

    def _get_default_settlement_payment(self):
        datas = self.env['kw_lv_settlement'].browse(self.env.context.get('active_ids'))
        return datas

    active_records = fields.Many2many('kw_lv_settlement',readonly=1, default=_get_default_settlement_payment)
    payment_date = fields.Date(string='Payment Date',default=fields.Date.context_today)

    @api.multi
    def update_payment(self):
        for record in self.active_records:
            if record.payment_state == 'applied':
                if record.lv_id:
                    for payments in record.lv_id:
                        payments.write({
                            'payment_status':'payment'
                        })
                else:
                    pass
                record.write({
                    'payment_taken_by':self.env.user.employee_ids.id,
                    'payment_taken_on':date.today(),
                    'payment_state':'payment',
                    'payment_date':self.payment_date,
                })
                self.env.user.notify_info(message='Payment Successfully.')
            else:
                pass