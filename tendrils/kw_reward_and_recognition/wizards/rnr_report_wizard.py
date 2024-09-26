from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date
import calendar

def get_years():
    year_list = []
    for i in range((date.today().year), 1997, -1):
        year_list.append((i, str(i)))
    return year_list

class RnrReportWizard(models.TransientModel):
    _name = 'rnr_report_wizard'
    _description = 'Starlight Report Wizard'

    
    year = fields.Selection(get_years(), string='Year', default=date.today().year)
    # month = fields.Char(string='Month', default=str(date.today().month))
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    rnr_state = fields.Selection([('all','All'),('sbu', 'Draft'), ('nominate', 'Nominated'),('award','Awarded'),('finalise','Published'),('reject','Rejected')] ,default='all')
    report_id = fields.Many2one("reward_and_recognition")
    
    @api.multi
    def view_rnr_report(self):
        tree_view_id = self.env.ref('kw_reward_and_recognition.kw_starlight_report_tree_view').id
        # tree_view_id = self.env.ref('kw_reward_and_recognition.reward_andrecognition_view_tree_report').id
        # form_view_id = self.env.ref('kw_reward_and_recognition.reward_and_recognition_view_report_form').id
        # kanban_view_id = self.env.ref('kw_reward_and_recognition.reward_and_recognition_report_view_kanban').id
        # pivot_view_id = self.env.ref('kw_reward_and_recognition.reward_and_recognition_view_report_pivot_view').id
        # graph_view_id = self.env.ref('kw_reward_and_recognition.reward_and_recognition_view_report_graph_view').id

        action = {
            'name': 'Starlight Report',
            'type': 'ir.actions.act_window',
            # 'views': [(tree_view_id, 'tree'), (form_view_id, 'form'),(kanban_view_id, 'kanban'),(pivot_view_id,'pivot'),(graph_view_id,'graph')],
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            # 'res_model': 'reward_and_recognition',
            'res_model': 'kw_starlight_report',
            'target': 'main',
            'flags' : {'mode': 'readonly'},
            'search_view_id': (self.env.ref('kw_reward_and_recognition.kw_starlight_report_view_report_search_view').id,),
            'context': {'create':False,'edit':False,'delete':False,'search_default_group_by_month_name':1,'search_default_group_by_employee_id':1}
        }
        rnr_list = []
        record_data = self.env['kw_starlight_report'].sudo().search([])
        if self.month and self.year and self.rnr_state :
            cuur_year = int(self.year)
            curr_month = int(self.month)
            for rec in record_data:
                record_date = rec.nominated_on.date()
                if record_date and int(record_date.year) == cuur_year and int(record_date.month) == curr_month:
                    rnr_list.append(rec.id)
                    
        if self.rnr_state == 'all':
            data = False
            if self.env.user.has_group('kw_reward_and_recognition.rnr_sbu'):
                # if int(self.month) != int(date.today().month):
                #     data = record_data.filtered(lambda user: user.employee_id.department_id.id == self.env.user.employee_ids.department_id.id and user.month == self.month and user.year == self.year)
                # else:
                data = record_data.filtered(lambda user: user.employee_id.department_id.id == self.env.user.employee_ids.department_id.id and user.month == self.month and user.year == self.year)
                action['domain'] =[('id','in',data.ids if data else False)]
            if self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer'):
                data = record_data.filtered(lambda user: user.reviewed_by.id == self.env.user.employee_ids.id) + record_data.filtered(lambda user: user.pending_at.id == self.env.user.employee_ids.id)
                # print("data====",data,"----",record_data.filtered(lambda user: user.reviewed_by.id == self.env.user.employee_ids.id),"====",record_data.filtered(lambda user: user.pending_at.id == self.env.user.employee_ids.id))
                action['domain'] =[('id','in',data.ids if data else False),('month','=',int(self.month)),('year','=',int(self.year))]
            if self.env.user.has_group('kw_reward_and_recognition.rnr_final_reviewer') or self.env.user.has_group('kw_reward_and_recognition.rnr_manager'):
                # domain_data = []
                # if int(self.month) != int(date.today().month):
                #     domain_data = [('month','=',int(self.month))]
                # else:
                domain_data = [('month','=',int(self.month)),('year','=',int(self.year))]
                action['domain'] =domain_data
        else:
            if self.env.user.has_group('kw_reward_and_recognition.rnr_sbu'):
                # if int(self.month) != int(date.today().month):
                #     data = record_data.filtered(lambda user: user.employee_id.department_id.id == self.env.user.employee_ids.department_id.id and user.month == self.month and user.year == self.year and user.state == self.rnr_state)
                # else:
                data = record_data.filtered(lambda user: user.employee_id.department_id.id == self.env.user.employee_ids.department_id.id and user.state == self.rnr_state and user.year == self.year and user.month == self.month)
                action['domain'] =[('id','in',data.ids if data else False)]
            if self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer'):
                data = record_data.filtered(lambda user: user.reviewed_by.id == self.env.user.employee_ids.id)
                action['domain'] =[('id','in',data.ids if data else False),('state','=',self.rnr_state),('month','=',int(self.month)),('year','=',int(self.year))]
            if self.env.user.has_group('kw_reward_and_recognition.rnr_final_reviewer') or self.env.user.has_group('kw_reward_and_recognition.rnr_manager'):
                # domain_data = []
                # if int(self.month) != int(date.today().month):
                #     domain_data = [('id','in',rnr_list),('state','=',self.rnr_state),('month','=',int(self.month))]
                # else:
                domain_data = [('id','in',rnr_list),('state','=',self.rnr_state),('month','=',int(self.month)),('year','=',int(self.year))]
                action['domain'] = domain_data
        return action
        
        