from odoo import models, fields, api ,tools
from datetime import  date , datetime , timedelta
from odoo.exceptions import ValidationError
import pytz

class OpportunityPortDashboard(models.Model):
    _name = 'kw_opp_port'
    _description= 'Opportunity Dashboard'
    _rec_name = 'opp_code'


    opp_id = fields.Integer('Kw Opp ID')
    opp_code=  fields.Char(string="Opp Code" ,required=True)
    client_name=  fields.Char(string="Client Name")
    client_short_name =  fields.Char(string="Client Short Name")
    opp_name = fields.Char(string='Opp Name')
    a_manager= fields.Char(string="A/M")
    expected_closing_date = fields.Date('Expected Closing Date')
    amount = fields.Float('Amount')
    action_log_ids = fields.One2many('kw_opp_port_action_log','opp_port_id',string="Action log")
    opp_val = fields.Float()
    acc_manager_id = fields.Many2one('hr.employee')
    reviewer_id = fields.Many2one('hr.employee')
    teamleader_id = fields.Many2one('hr.employee')
    updated_by = fields.Integer()
    csg = fields.Char()
    client_address = fields.Char()
    last_updated_on = fields.Char()
    next_execution_time = fields.Char()
    active = fields.Boolean()
    pac_status = fields.Integer()
    user_last_modified_date = fields.Datetime()


    @api.model
    def update_model_field(self, rec_id, given_date):
        data = self.env['kw_opp_port'].search([('id', '=', rec_id)])
        sync_data = self.env['kw_sync_portlet_data'].sudo().search([('rec_id', '=', rec_id), ('status', '=', 0)])
        if len(given_date) > 0:
            data.expected_closing_date = given_date
            indian_timezone = pytz.timezone('Asia/Kolkata')
            current_datetime_utc = datetime.now(pytz.utc)
            current_datetime_in_indian = current_datetime_utc.astimezone(indian_timezone) - timedelta(hours=5,minutes=30)
            # print('current_datetime_in_indian========',current_datetime_in_indian)
            data.user_last_modified_date = current_datetime_in_indian.strftime('%Y-%m-%d %H:%M:%S %p')
            opp_port_log = self.env['kw_opp_port_action_log']
            dataa = {
                'action_taken_date': date.today(),
                'action_taken_by_id': self.env.user.employee_ids.id,
                'changed_date': given_date,
                'opp_port_id': data.id,
            }
            opp_port_log.create(dataa)
            if not sync_data:
                sync_dataa = {
                    'model_id': 'kw_opp_port',
                    'rec_id': rec_id,
                    'created_on': date.today(),
                    'status': 0,
                }
                sync_data.create(sync_dataa)
            else:
                pass
        else:
            raise ValidationError('Please provide a valid date..')


class OpportunityPortDashboardLog(models.Model):
    _name = 'kw_opp_port_action_log'
    _description= 'Opportunity Dashboard Action Log'

    action_taken_date = fields.Date(string="Action taken Date")
    action_taken_by_id = fields.Many2one('hr.employee',string="Action taken By")
    changed_date = fields.Date(string="Changed Closing Date")
    opp_port_id = fields.Many2one('kw_opp_port')





