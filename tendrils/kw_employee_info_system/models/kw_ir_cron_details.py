from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil import relativedelta


class IrActions(models.Model):
    _inherit = "ir.actions.server"
    
    @api.multi
    def run(self):
        start_time = datetime.now()
        res = super(IrActions, self).run()
        end_time = datetime.now()
        for rec in self:
            self.env['kw_cron_details'].create({
                'name':rec.name,
                'start_time':start_time,
                'end_time':end_time,
            })
        return res

class KwCrondetails(models.Model):
    _name = "kw_cron_details"
    _description = "Kwantify Cron details"

    name = fields.Char()
    start_time = fields.Datetime()
    end_time = fields.Datetime()

    