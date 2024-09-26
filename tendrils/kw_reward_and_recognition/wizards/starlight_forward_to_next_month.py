from http.client import ImproperConnectionState
from odoo import fields,models,api
from odoo.exceptions import ValidationError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

def get_years():
    year_list = []
    for i in range((date.today().year), 1997, -1):
        year_list.append((i, str(i)))
    return year_list

class ForwardToNextMonth(models.TransientModel):
    _name = 'forward_to_next_month'
    _description = 'forward_to_next_month'
    
    def _default_starlight_records(self):
        if self._context.get('starlight_forwarded_ids') :
            reward_id = self.env['reward_and_recognition'].sudo().browse(self._context.get('starlight_forwarded_ids')).ids
        else:
            reward_id = []
        return reward_id
    
    
    starlight_ids = fields.Many2many('reward_and_recognition', 'active_reward_and_recognition_rel', 'forward_id', 'starlight_id',
                                     string="Starlight Records", default=_default_starlight_records)

    year = fields.Selection(get_years(), string='Forward to Year', default=date.today().year)
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Forward to Month")

    @api.constrains('year','month')
    def validate_duplicate_nomination(self):
        if self.year:
            if date.today().year > int(self.year):
                raise ValidationError("You cannot select past year.")
        # if self.month:
        #     if date.today().month > int(self.month):
        #         raise ValidationError("You cannot select past month.")

    @api.multi
    def forward_to_next_month(self):
        if self.starlight_ids:
            # if len(set(self.starlight_ids.mapped('month'))) > 1:
            #     raise ValidationError("You cannot forward multiple month datas.")
            # else:
            for rec in self.starlight_ids:
                day_count=date.today().day
                if int(date.today().month) == 1 and date.today().day in [29,30,31]:
                    leap_year = False
                    year_count = date.today().year
                    if((year_count % 400 == 0) or (year_count % 100 != 0) and (year_count % 4 == 0)):
                        leap_year = True
                    if leap_year:
                        day_count = 29
                    else:
                        day_count=28
                        
                migrated_to =  datetime(int(self.year), int(self.month), int(day_count)).date()
                create_date = datetime(int(self.year), int(self.month), int(day_count))
                write_date = datetime(int(self.year), int(self.month), int(day_count))
                compute_month = create_date.strftime("%B")
                action_taken_by = F"{self.env.user.employee_ids.name}"
                action_remark = "Manually Forwarded to Next Month"
                rec.execute_forward_to_next_month(rec,int(self.year),int(self.month),migrated_to,write_date,create_date,compute_month,action_taken_by,action_remark)
