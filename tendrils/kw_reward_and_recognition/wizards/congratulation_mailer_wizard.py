from http.client import ImproperConnectionState
from odoo import fields,models,api
from odoo.exceptions import ValidationError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
import calendar

def get_years():
    year_list = []
    for i in range((date.today().year), 1997, -1):
        year_list.append((i, str(i)))
    return year_list

class CongratulationMailerWizard(models.TransientModel):
    _name = 'congratulation_mailer_wizard'
    _description = 'congratulation_mailer_wizard'

    starlight_ids = fields.Many2many('reward_and_recognition', string="Starlight Records")

    year = fields.Selection(get_years(), string='Year', default=date.today().year)
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")

    @api.onchange('year', 'month')
    def _populate_employees(self):
        reward_ids = self.env['reward_and_recognition'].sudo().search([('year','=',int(self.year)),('month','=',int(self.month)),('state','=','finalise')])
        self.starlight_ids = [(6, 0, reward_ids.ids)]

    @api.multi
    def send_congratulation_mail(self):
        param = self.env['kw_starlight_general_configuration'].sudo().search([],order='id desc',limit=1)
        congratulation_mail_from = param.congratulation_mail_from
        congratulation_mail_to = param.congratulation_mail_to
        awarded_nominee = self.starlight_ids
        template = self.env.ref('kw_reward_and_recognition.kw_rnr_congratulation_mailer_template')
        log = self.env['nomination_log'].sudo().create({
            'send_to': 'tendrils@csm.tech',
            'send_from': self.env.user.employee_ids.name if self.env.user.employee_ids else 'System User (Odoo Bot)',
            'status': 'success',
            'date': date.today()
        })
        template.with_context(months=date.today().strftime("%B"),
                                records=awarded_nominee,
                                month_year = f"{calendar.month_name[int(self.month)]} {self.year}",
                                congratulation_mail_from=congratulation_mail_from,
                                congratulation_mail_to=congratulation_mail_to).send_mail(log.id,
                                                                    notif_layout="kwantify_theme.csm_mail_notification_light")