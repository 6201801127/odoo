from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date
import calendar


class GrievanceReportWizard(models.TransientModel):
    _name = 'kw.grievance.report'
    _description = 'Kwantify Grievance Report'

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1953, -1)]
    
    applied_by = fields.Selection([
        ('all', 'All'),
        ('dt', 'Date wise'),
        ('my', 'Month & Year wise'),
        ('grievance','Grievance'),
    ], string="Applied By", default='my')
    date_from = fields.Date('Date From', help="Choose a starting date to get case details")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the case details")
    year = fields.Selection(selection='_get_year_list', string='Year',  default=str(date.today().year))

    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    grievance_state = fields.Selection([('draft', 'Draft'),
                              ('apply', 'Applied'),
                              ('receive', 'Received'),
                              ('in_progress', 'In Progress'),
                              ('verify', 'Verified'),
                              ('approve', 'FO Pending'),
                              ('closed', 'Closed'),
                              ('reject', 'Rejected')],
                             string="Grievance State")
    grievance_ids = fields.Many2many('grievance_status_report', 'kw_griev_report_rel', 'gr_rep_id', 'grie_rep_id',
                                             string='Grievance Report')
    def get_emp_grievance_data(self):
        tree_view_id = self.env.ref('kw_grievance_new.view_grievance_status_tree').id
        form_view_id = self.env.ref('kw_grievance_new.report_ticket_view_form').id
        action = {
            'name': 'Grievance Report',
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'grievance_status_report',
            'target': 'main',
        }
        record_datas = self.env['grievance_status_report'].sudo().search([])
        if self.applied_by == 'all':
            if self.env.user.has_group('kw_grievance_new.group_grievance_manager'):
                if self.grievance_state:
                    action['domain'] = [('state','=',self.grievance_state)]
                else:
                    action['domain'] = []
        
        if self.applied_by == 'grievance':
            if self.env.user.has_group('kw_grievance_new.group_grievance_manager'):
                action['domain'] = [('id', '=', self.grievance_ids.ids)]
            else:
                raise ValidationError(_("You don't have access to search Case Specific Reports"))

                
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            grievance_data = self.env['grievance_status_report'].sudo().search([('create_date','>=',dt1),('create_date','<=',dt2)])
            if self.env.user.has_group('kw_grievance_new.group_grievance_manager'):
                if self.grievance_state:
                    action['domain'] = [('id','in',grievance_data.ids),('state','=',self.grievance_state)]
                else:
                    action['domain'] = [('id','in',grievance_data.ids)]
            else:
                raise ValidationError(_("You don't have access to search Case Date Time Reports"))

        if self.applied_by == 'my':
            cuur_year = int(self.year)
            curr_month = int(self.month)
            num_days = calendar.monthrange(cuur_year, curr_month)
            lst_day = list(num_days)[1]
            first_day = date(cuur_year,curr_month, 1)
            last_day = date(cuur_year, curr_month, lst_day)
            griev_list = []
            griev_list2 = [] 
            for rec in record_datas:
                if rec.create_date and str(rec.create_date.year) == str(cuur_year) and str(rec.create_date.month) == str(curr_month):
                    griev_list.append(rec.id)
                # if rec.create_date and str(rec.create_date.year) == str(cuur_year) and str(rec.create_date.month) == str(curr_month) and rec.grievance_ids.id in self.env.user.branch_ids.ids:
                #     griev_list2.append(rec.id)
            if self.env.user.has_group('kw_grievance_new.group_grievance_manager'):
                if self.grievance_state:
                    action['domain'] =[('id','in',griev_list),('state','=',self.grievance_state)]
                else:
                    action['domain'] =[('id','in',griev_list)]
    
        return action

    