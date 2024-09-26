# -*- coding: utf-8 -*-
import pytz,random
from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
import datetime, calendar

from dateutil.relativedelta import relativedelta
import json
from odoo.addons.ks_dashboard_ninja.lib.ks_date_filter_selections import ks_get_date

class KsDashboardNinjaBoard(models.Model):
    _name = 'ks_dashboard_ninja.board'
    _description = 'Dashboard Ninja'

    name = fields.Char(string="Dashboard Name", required=True, size=35)
    ks_dashboard_items_ids = fields.One2many('ks_dashboard_ninja.item', 'ks_dashboard_ninja_board_id',
                                             string='Dashboard Items')
    ks_dashboard_menu_name = fields.Char(string="Menu Name")
    ks_dashboard_top_menu_id = fields.Many2one('ir.ui.menu', domain="[('parent_id','=',False)]",
                                               string="Show Under Menu")
    ks_dashboard_client_action_id = fields.Many2one('ir.actions.client')
    ks_dashboard_menu_id = fields.Many2one('ir.ui.menu')
    ks_dashboard_state = fields.Char()
    ks_dashboard_active = fields.Boolean(string="Active", default=True)
    ks_dashboard_group_access = fields.Many2many('res.groups', string="Group Access")

    # DateFilter Fields
    ks_dashboard_start_date = fields.Datetime(string="Start Date")
    ks_dashboard_end_date = fields.Datetime(string="End Date")
    ks_date_filter_selection = fields.Selection([
        ('l_none', 'All Time'),
        ('l_day', 'Today'),
        ('t_week', 'This Week'),
        ('t_month', 'This Month'),
        ('t_quarter', 'This Quarter'),
        ('t_year', 'This Year'),
        ('n_day', 'Next Day'),
        ('n_week', 'Next Week'),
        ('n_month', 'Next Month'),
        ('n_quarter', 'Next Quarter'),
        ('n_year', 'Next Year'),
        ('ls_day', 'Last Day'),
        ('ls_week', 'Last Week'),
        ('ls_month', 'Last Month'),
        ('ls_quarter', 'Last Quarter'),
        ('ls_year', 'Last Year'),
        ('l_week', 'Last 7 days'),
        ('l_month', 'Last 30 days'),
        ('l_quarter', 'Last 90 days'),
        ('l_year', 'Last 365 days'),
        ('ls_past_until_now', 'Past Till Now'),
        ('ls_pastwithout_now', ' Past Excluding Today'),
        ('n_future_starting_now', 'Future Starting Now'),
        ('n_futurestarting_tomorrow', 'Future Starting Tomorrow'),
        ('l_custom', 'Custom Filter'),
    ], default='l_none', string="Default Date Filter")

    ks_gridstack_config = fields.Char('Item Configurations')
    ks_dashboard_default_template = fields.Many2one('ks_dashboard_ninja.board_template',
                                                    default=lambda self: self.env.ref('ks_dashboard_ninja.ks_blank',
                                                                                      False),
                                                    string="Dashboard Template")

    ks_set_interval = fields.Selection([
        (15000, '15 Seconds'),
        (30000, '30 Seconds'),
        (45000, '45 Seconds'),
        (60000, '1 minute'),
        (120000, '2 minute'),
        (300000, '5 minute'),
        (600000, '10 minute'),
    ], string="Default Update Interval", help="Update Interval for new items only")
    ks_dashboard_menu_sequence = fields.Integer(string="Menu Sequence", default=10,
                                                help="Smallest sequence give high priority and Highest sequence give "
                                                     "low priority")

    @api.model
    def create(self, vals):
        record = super(KsDashboardNinjaBoard, self).create(vals)
        if 'ks_dashboard_top_menu_id' in vals and 'ks_dashboard_menu_name' in vals:
            action_id = {
                'name': vals['ks_dashboard_menu_name'] + " Action",
                'res_model': 'ks_dashboard_ninja.board',
                'tag': 'ks_dashboard_ninja',
                'params': {'ks_dashboard_id': record.id},
            }
            record.ks_dashboard_client_action_id = self.env['ir.actions.client'].sudo().create(action_id)

            record.ks_dashboard_menu_id = self.env['ir.ui.menu'].sudo().create({
                'name': vals['ks_dashboard_menu_name'],
                'active': vals.get('ks_dashboard_active', True),
                'parent_id': vals['ks_dashboard_top_menu_id'],
                'action': "ir.actions.client," + str(record.ks_dashboard_client_action_id.id),
                'groups_id': vals.get('ks_dashboard_group_access', False),
                'sequence': vals.get('ks_dashboard_menu_sequence', 10)
            })

        if record.ks_dashboard_default_template and record.ks_dashboard_default_template.ks_item_count:
            ks_gridstack_config = {}
            template_data = json.loads(record.ks_dashboard_default_template.ks_gridstack_config)
            for item_data in template_data:
                dashboard_item = self.env.ref(item_data['item_id']).copy({'ks_dashboard_ninja_board_id': record.id})
                ks_gridstack_config[dashboard_item.id] = item_data['data']
            record.ks_gridstack_config = json.dumps(ks_gridstack_config)
        return record

    @api.onchange('ks_date_filter_selection')
    def ks_date_filter_selection_onchange(self):
        for rec in self:
            if rec.ks_date_filter_selection and rec.ks_date_filter_selection != 'l_custom':
                rec.ks_dashboard_start_date = False
                rec.ks_dashboard_end_date = False

    @api.multi
    def write(self, vals):
        if vals.get('ks_date_filter_selection', False) and vals.get('ks_date_filter_selection') != 'l_custom':
            vals.update({
                'ks_dashboard_start_date': False,
                'ks_dashboard_end_date': False

            })
        
        record = super(KsDashboardNinjaBoard, self).write(vals)
        for rec in self:
            if 'ks_dashboard_menu_name' in vals:
                if self.env.ref('ks_dashboard_ninja.ks_my_default_dashboard_board') and self.env.ref(
                        'ks_dashboard_ninja.ks_my_default_dashboard_board').sudo().id == rec.id:
                    if self.env.ref('ks_dashboard_ninja.board_menu_root', False):
                        self.env.ref('ks_dashboard_ninja.board_menu_root').sudo().name = vals['ks_dashboard_menu_name']
                else:
                    rec.ks_dashboard_menu_id.sudo().name = vals['ks_dashboard_menu_name']
            if 'ks_dashboard_group_access' in vals:
                if self.env.ref('ks_dashboard_ninja.ks_my_default_dashboard_board').id == rec.id:
                    if self.env.ref('ks_dashboard_ninja.board_menu_root', False):
                        self.env.ref('ks_dashboard_ninja.board_menu_root').groups_id = vals['ks_dashboard_group_access']
                else:
                    rec.ks_dashboard_menu_id.sudo().groups_id = vals['ks_dashboard_group_access']
            if 'ks_dashboard_active' in vals and rec.ks_dashboard_menu_id:
                rec.ks_dashboard_menu_id.sudo().active = vals['ks_dashboard_active']

            if 'ks_dashboard_top_menu_id' in vals:
                rec.ks_dashboard_menu_id.write(
                    {'parent_id': vals['ks_dashboard_top_menu_id']}
                )

            if 'ks_dashboard_menu_sequence' in vals:
                rec.ks_dashboard_menu_id.sudo().sequence = vals['ks_dashboard_menu_sequence']

        return record

    @api.multi
    def unlink(self):
        if self.env.ref('ks_dashboard_ninja.ks_my_default_dashboard_board').id in self.ids:
            raise ValidationError(_("Default Dashboard can't be deleted."))
        else:
            for rec in self:
                rec.ks_dashboard_client_action_id.sudo().unlink()
                rec.ks_dashboard_menu_id.sudo().unlink()
                rec.ks_dashboard_items_ids.unlink()
        res = super(KsDashboardNinjaBoard, self).unlink()
        return res

    def portlets_data(self):
        return self.env['portlet_master'].sudo().search_read([],['id','name','portlet_code'])

    def portlet_master_data(self, dashboard_id):
        portlet = []
        portlet_records = self.env['ks_dashboard_ninja.item'].search([('ks_dashboard_ninja_board_id','=',dashboard_id),('is_published','=',True)])
        item_ids = self.env['kw_user_portlets'].search([('employee_id.user_id','=',self.env.user.id),('ks_dashboard_ninja_board_id','=',dashboard_id)]).mapped('ks_dashboard_items_id').ids
        for record in portlet_records:
            if record.common_portlet == True:
                portlet.append({'id': record.id, 'name': record.name, 'ks_dashboard_ninja_board_id': record.ks_dashboard_ninja_board_id, 'ks_dashboard_item_type': record.ks_dashboard_item_type, 'portlet_status': 1 if record.id in item_ids else 0})
            elif self.env.user.employee_ids.id in record.employee_visible.ids:
                portlet.append({'id': record.id, 'name': record.name, 'ks_dashboard_ninja_board_id': record.ks_dashboard_ninja_board_id, 'ks_dashboard_item_type': record.ks_dashboard_item_type, 'portlet_status': 1 if record.id in item_ids else 0})
        return portlet

    def get_user_gridstack_config_details(self,dashboard_id):
        user_gridstack = self.env['kw_user_portlets_gridstack_config'].search([('employee_id','=',self.env.user.employee_ids.id),('ks_dashboard_ninja_board_id','=',dashboard_id)],limit=1)
        if user_gridstack:
            return user_gridstack.ks_gridstack_config
    
    def check_dashboard_exisiting_user(self, dashboard_id):
        dashboard_portlet_ids = self.env['ks_dashboard_ninja.item'].sudo().search([('common_portlet','=',True),('is_published','=',True),('ks_dashboard_ninja_board_id','=',dashboard_id)]).ids
        existing_user = self.env['kw_user_portlets'].sudo().search([('employee_id.user_id','=',self.env.user.id),('ks_dashboard_ninja_board_id','=',dashboard_id)])
        if not existing_user:
            self.env['kw_user_portlets'].create({
                'employee_id': self.env.user.employee_ids.id,
                'ks_dashboard_ninja_board_id': dashboard_id,
                'ks_dashboard_items_id':  [(6, 0, dashboard_portlet_ids)]
            })

    
    @api.model
    def ks_fetch_dashboard_data(self,ks_dashboard_id, ks_item_domain=False, **kwargs):

        """
        Return Dictionary of Dashboard Data.
        :param ks_dashboard_id: Integer
        :param ks_item_domain: List[List]
        :return: dict
        """
        dashboard_item_ids = []
        has_group_ks_dashboard_manager = self.env.user.has_group('ks_dashboard_ninja.ks_dashboard_ninja_group_manager')
        dashboard_data = {
            'name': self.browse(ks_dashboard_id).name,
            'ks_dashboard_manager': has_group_ks_dashboard_manager,
            'ks_dashboard_list': self.search_read([], ['id', 'name']),
            'ks_dashboard_start_date': self._context.get('ksDateFilterStartDate', False) or self.browse(
                ks_dashboard_id).ks_dashboard_start_date,
            'ks_dashboard_end_date': self._context.get('ksDateFilterEndDate', False) or self.browse(
                ks_dashboard_id).ks_dashboard_end_date,
            'ks_date_filter_selection': self._context.get('ksDateFilterSelection', False) or self.browse(
                ks_dashboard_id).ks_date_filter_selection,
            'existing_user': self.check_dashboard_exisiting_user(ks_dashboard_id),
            'ks_gridstack_config': self.get_user_gridstack_config_details(ks_dashboard_id),
            'ks_set_interval': self.browse(ks_dashboard_id).ks_set_interval,
            # 'ks_dashboard_items_ids': self.browse(ks_dashboard_id).ks_dashboard_items_ids.ids,
            'ks_item_data': {},
            'portlet_master': self.portlet_master_data(ks_dashboard_id),
            'portlets': self.portlets_data(),
            'branch_department': self.get_branch_department_data(),
            'get_month_year_list' : self.get_month_year_list(),
            'stpi_new_joinee': self.env['hr.employee'].search_count([('branch_id','=',self.env.user.employee_ids.branch_id.id),('date_of_join','>=', (datetime.datetime.now().date() - datetime.timedelta(days = 15)))])
        }
        
        ks_item_domain = ks_item_domain or []
        dashboard_items = self.env['kw_user_portlets'].sudo().search([('employee_id.user_id','=',self.env.user.id),('ks_dashboard_ninja_board_id','=',ks_dashboard_id)],limit=1)
        for item in dashboard_items.ks_dashboard_items_id:
            if item.is_published == True:
                if item.common_portlet == True or self.env.user.employee_ids.id in item.employee_visible.ids:
                    dashboard_item_ids.append(item.id)
        
        try:
            items = self.ks_dashboard_items_ids.sudo().search([['ks_dashboard_ninja_board_id', '=', ks_dashboard_id]] + ks_item_domain).ids
        except Exception as e:
            items = self.ks_dashboard_items_ids.sudo().search([['ks_dashboard_ninja_board_id', '=', ks_dashboard_id]] + ks_item_domain).ids
        dashboard_data['ks_dashboard_items_ids'] = dashboard_item_ids
        return dashboard_data
    
    def get_week(self, date):
        one_day = datetime.timedelta(days=1)
        date = date 
        day_idx = (date.weekday()) % 7 
        sunday = date - datetime.timedelta(days=day_idx) 
        date = sunday
        for n in range(7):
            yield date
            date += one_day

    def get_branch_department_data(self):
        branches = self.env['res.branch'].search_read([],['id','name'])
        departments = self.env['hr.department'].search_read([],['id','name'])
        return [branches, departments]

    def fetch_employee_data(self,args):
        print(args)
        emp_list = []
        if 'empSearch' in args and args.get('empSearch'):
            emp_rec = self.env['hr.employee'].search([('name','ilike',args.get('empSearch'))])
        elif 'branch' and 'department' in args:
            if args.get('branch') == '0' and args.get('department') == '0':
                emp_rec = self.env['hr.employee'].search([('branch_id','=',self.env.user.employee_ids.branch_id.id)],order='date_of_join asc')
            elif args.get('branch') != '0' and args.get('department') == '0':
                emp_rec = self.env['hr.employee'].search([('branch_id','=',int(args.get('branch')))],order='date_of_join asc')
            elif args.get('branch') == '0' and args.get('department') != '0':
                emp_rec = self.env['hr.employee'].search([('department_id','=',int(args.get('department')))],order='date_of_join asc')
            else:
                emp_rec = self.env['hr.employee'].search([('branch_id','=',int(args.get('branch'))),('department_id','=',int(args.get('department')))],order='date_of_join asc')
        elif 'new_joinee' in args and args.get('new_joinee'):
            emp_rec = self.env['hr.employee'].search([('branch_id','=',self.env.user.employee_ids.branch_id.id),('date_of_join','>=', (datetime.datetime.now().date() - datetime.timedelta(days = 15)))],order='date_of_join asc')
        else:
            emp_rec = self.env['hr.employee'].search([('branch_id','=',self.env.user.employee_ids.branch_id.id)],order='date_of_join asc')


        for record in emp_rec:
            emp_list.append({
                'id': record.id,
                'name': record.name,
                'designation': record.job_id.name,
                'image_exist': True if record.image_medium else False,
                'gender': record.gende,
                'branch':record.branch_id.name,
                'dob' : record.birthday,
                'pay_level_id': record.job_id.pay_level_id.pay_band_from,
                'department' : record.department_id.name,
                'job_role' : record.employee_type,
                'date_of_join' : record.date_of_join,
                'work_email': record.work_email,
                'identify_id': record.identify_id,
                'work_phone': record.work_phone,
                'work_mobile': record.mobile_phone
            })
        sorted_employee = sorted(emp_list, key=lambda r:r['pay_level_id'], reverse=True)
        return sorted_employee

    @api.model
    def getEmployeeDirectory(self,**kwargs):
        data = {'new_joinee_data': self.fetch_employee_data(kwargs)}
        return data

    def fetch_my_leaves_data(self):
        my_leaves_list = []
        my_leave_allocation_ids = self.env['hr.leave.allocation'].search([('employee_id','=',self.env.user.employee_ids.id),('state','=','validate')])
        for la in my_leave_allocation_ids:
            taken_percentage,balance_percentage = 0,0
            try:
                taken_percentage = ((la.holiday_status_id.max_leaves - la.holiday_status_id.virtual_remaining_leaves) / la.holiday_status_id.max_leaves ) * 100
                balance_percentage = (la.holiday_status_id.virtual_remaining_leaves / la.holiday_status_id.max_leaves) * 100
            except ZeroDivisionError:
                taken_percentage = 0
                balance_percentage = 0
            my_leaves_list.append({
                'leave_type': la.holiday_status_id.name,
                'balance': la.holiday_status_id.virtual_remaining_leaves,
                'allocated': la.holiday_status_id.max_leaves,
                'taken': (la.holiday_status_id.max_leaves - la.holiday_status_id.virtual_remaining_leaves),
                'taken_percentage':  taken_percentage,
                'balance_percentage': balance_percentage,
                'expire_on': la.date_to.strftime("%d-%b-%Y") if la.date_to else 'NA'
            })
        return [my_leaves_list]

    @api.model
    def getMyLeaves(self):
        myLeaves = {'myLeaveData': self.fetch_my_leaves_data()}
        return myLeaves

    def fetch_my_tour_data(self):
        my_tour_list,rupee = [], u'\u20B9'
        tour_request_ids = self.env['tour.request'].search([('claimed','!=','True'),('employee_id','=',self.env.user.employee_ids.id)])
        for tour in tour_request_ids:
            tour_claim = []
            tour_claim_id = self.env['employee.tour.claim'].search([('tour_request_id','=',tour.id),('employee_id','=',self.env.user.employee_ids.id)])
            if tour_claim_id:
                for journey in tour_claim_id.detail_of_journey:
                    tour_claim.append({
                        'from': journey.from_l.name if journey.from_l else 'NA',
                        'departure_date': journey.departure_date.strftime("%d-%m-%Y") if journey.departure_date else 'NA',
                        'to': journey.to_l.name if journey.to_l else 'NA',
                        'arrival_date': journey.arrival_date.strftime("%d-%m-%Y") if journey.arrival_date else 'NA',
                        'amount': rupee + "{:,}".format(float("%.2f" % journey.amount_claimed))
                    })
                    
            my_tour_list.append({
                'tour_sequence': tour.tour_sequence,
                'requested_date': tour.date.strftime("%d-%m-%Y") if tour.date else 'NA',
                'purpose': tour.purpose,
                'advance_amount': rupee + "{:,}".format(float("%.2f" % tour.advance_requested)),
                'tour_claim_length': len(tour_claim),
                'tour_claim': tour_claim
            })
                
        return my_tour_list

    @api.model
    def getMyTours(self):
        myTour = {'myTourData': self.fetch_my_tour_data()}
        return myTour

    def fetch_my_department_data(self):
        # my_department_list = []
        department_male = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('gende','=','male')])
        department_female = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('gende','=','female')])
        department_transgender = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('gende','=','transgender')])

        total_employees = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id)])
        
        probation_employee = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('state','=','test_period')])
        contract_employee = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('state','=','contract')])
        deputation_employee = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('state','=','deputation')])
        employment_employee = self.env['hr.employee'].search_count([('department_id','=',self.env.user.employee_ids.department_id.id),('state','=','employment')])

        # department_chart = [['Probation',probation_employee],['Contract',contract_employee],['Deputation',deputation_employee],['Regular',employment_employee]]
        return [[department_male,department_female,department_transgender,total_employees],probation_employee,contract_employee,deputation_employee,employment_employee]

    @api.model
    def getMyDepartment(self):
        myDepartment = {'myDepartmentData': self.fetch_my_department_data()}
        return myDepartment

    def get_month_year_list(self):
        current_year = datetime.datetime.now().date().year
        current_month = datetime.datetime.now().date().month
        years,months = [],[]
        for year in range(current_year,2019,-1):
            years.append({'year_index': year, 'year': year})

        for month in range(1,13):
            months.append({'month_index': datetime.date(current_year, month, 1).strftime('%m'),'month_name': datetime.date(current_year, month, 1).strftime('%B')})
        return[years,months]

    def fetch_holiday_calendar_data(self):
        holidays_list,rh_list,gh_list,week_off_list = [],[],[],[]
        resource_calendar_leave_ids = self.env['resource.calendar.leaves'].search([('resource_id','=',False),('calendar_id','=',self.env.user.employee_ids.resource_calendar_id.id)])
        emp_tz = self.env.user.employee_ids.tz or 'UTC' 
        for holiday in resource_calendar_leave_ids:
            if holiday.holiday_type == "rh":
                data_list = [holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).year, holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).month, holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).day, holiday.name, '#00A09D']
                rh_list.append(data_list)
            elif holiday.holiday_type == "gh":
                data_list = [holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).year, holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).month, holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).day, holiday.name, '#d83d2b']
                gh_list.append(data_list)
            elif holiday.holiday_type == "week_off":
                data_list = [holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).year, holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).month, holiday.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp_tz)).day, holiday.name, '#F5BB00']
                week_off_list.append(data_list)
        holidays_list = rh_list + gh_list + week_off_list
        return holidays_list

    @api.model  
    def getHolidayCalendar(self):
        holidayCalendar = {'holidayCalendarData': self.fetch_holiday_calendar_data()}
        return holidayCalendar

    @api.model
    def getLoanDetails(self):
        myLoans = {'loanDetails': self.fetch_loanDetails()}
        return myLoans
        
    def fetch_loanDetails(self):
        loan_details,loan_paid,rupee = [],[],u'\u20B9'
        # loan_ids = []

        emp_loan_rec = self.env['hr.loan'].search([('employee_id','=',self.env.user.employee_ids[0].id),('state','=','approve'),('balance_amount','>',0)])
        for loan_rec in emp_loan_rec:
            if loan_rec.balance_amount > 0:
                emi_list = []
                for emi in loan_rec.loan_lines:
                    emi_list.append({
                        'loan_line_id': emi.id,
                        'paid_status': emi.paid,
                        'emi_details': 'Date: ' + emi.date.strftime("%d-%m-%Y") + '<br/> Amount: ' + rupee + "{:,}".format(float("%.2f" % round(emi.amount,2))) + '<br/> Interest: ' + rupee + "{:,}".format(float("%.2f" % round(emi.monthly_interest_amount,2))) + '<br/> Status: ' + ('Paid' if emi.paid == True else 'Not Paid')
                    })
                loan_details.append({
                    'loan_id' : loan_rec.name.split('/')[1],
                    'total_amount' : "{:,}".format(float("%.2f" % loan_rec.total_amount)),
                    'total_paid_amount' : "{:,}".format(float("%.2f" % loan_rec.total_paid_amount)),
                    'taken_date': loan_rec.approve_date.strftime("%d-%m-%Y") if loan_rec.approve_date else 'NA',
                    'emi': sorted(emi_list, key = lambda r: r['loan_line_id']),
                    'total_emi': len(loan_rec.loan_lines),
                    'emi_paid': self.env['hr.loan.line'].search_count([('loan_id','=',loan_rec.id),('paid','=',True)])
                })

        paid_emp_loan_rec = self.env['hr.loan'].search([('employee_id','=',self.env.user.employee_ids[0].id),('state','=','paid')])
        for paid_loan_rec in paid_emp_loan_rec:
            if paid_loan_rec.balance_amount > 0:
                paid_emi_list = []
                for emi in paid_loan_rec.loan_lines:
                    paid_emi_list.append({
                        'loan_line_id': emi.id,
                        'paid_status': emi.paid,
                        'emi_details': 'Date: ' + emi.date.strftime("%d-%m-%Y") + '<br/> Amount: ' + rupee + "{:,}".format(float("%.2f" % round(emi.amount,2))) + '<br/> Interest: ' + rupee + "{:,}".format(float("%.2f" % round(emi.monthly_interest_amount,2))) + '<br/> Status: ' + ('Paid' if emi.paid == True else 'Not Paid')
                    })
                loan_paid.append({
                    'loan_id' : paid_loan_rec.name.split('/')[1],
                    'total_amount' : "{:,}".format(float("%.2f" % paid_loan_rec.total_amount)),
                    'total_paid_amount' : "{:,}".format(float("%.2f" % paid_loan_rec.total_paid_amount)),
                    'taken_date': paid_loan_rec.approve_date.strftime("%d-%m-%Y") if paid_loan_rec.approve_date else 'NA',
                    'emi': sorted(paid_emi_list, key = lambda r: r['loan_line_id']),
                    'total_emi': len(paid_loan_rec.loan_lines),
                    'emi_paid': self.env['hr.loan.line'].search_count([('loan_id','=',paid_loan_rec.id),('paid','=',True)])
                })
        return [loan_details, loan_paid]
        
    @api.model
    def getLtcDetails(self):
        ltc_details = {'ltcDetails' : self.fetch_ltc_details()}
        return ltc_details
        
    @api.model
    def fetch_ltc_details(self):
        ltcDetails,rupee = [],u'\u20B9'

        block_year_id = self.env['block.year'].search([('date_start','<=',datetime.datetime.today()),('date_end','>=',datetime.datetime.today())])
        for sub in block_year_id.child_block_year_ids:
            ltc_ids = self.env['employee.ltc.advance'].search([('employee_id','=',self.env.user.employee_ids[0].id),('block_year','=',block_year_id.id),('child_block_year','=',sub.id)])
        
            for ltc in ltc_ids:
                ltc_claim = self.env['employee.ltc.claim'].search([('employee_id','=',ltc.employee_id.id),('ltc_availed_for_m2o','=',ltc.id)],limit=1)
                ltcDetails.append({
                    'id':ltc.id,
                    'place_of_travel': (dict(self.env['employee.ltc.advance'].fields_get(allfields='place_of_trvel')['place_of_trvel']['selection'])[ltc.place_of_trvel]),
                    'child_block_year': sub.name,
                    'claim_amount': rupee + " " + "{:,}".format(float("%.2f" % ltc_claim.total_claimed_amount)) if ltc_claim else rupee + " 0.0",
                    'approved_amount': rupee + " " + "{:,}".format(float("%.2f" % ltc.single_fare_approved)) 
                })
        
        return [block_year_id.name, ltcDetails]
    
    def fetch_employee_on_tour_data(self):
        current_date = datetime.date.today()
        tour_list = []
        tour_ids = self.env['tour.request'].sudo().search([('branch_id','=',self.env.user.employee_ids.branch_id.id),('state','=','approved')])
        for tour in tour_ids:
            dates = []
            cities,city_list = [],[]
            for index,data in enumerate(tour.employee_journey):
                dates.append(data.departure_date)
                dates.append(data.arrival_date)
                if index == 0:
                    cities.append({
                        'id': data.from_l.id, 
                        'name': data.from_l.name,
                        'y': 1, 
                        'color': '#28a745' if current_date >= data.departure_date else '#198fbb', 
                        'marker' : {'radius': 8} if current_date >= data.departure_date else {'radius': 4},
                        'date': data.departure_date.strftime("%d-%m-%Y")
                    })
                    city_list.append(data.from_l.name)
                    cities.append({
                        'id': data.to_l.id, 
                        'name': data.to_l.name, 
                        'y': 1, 
                        'color': '#28a745' if current_date >= data.arrival_date else '#198fbb' , 
                        'marker' : {'radius': 8} if current_date >= data.arrival_date else {'radius': 4},
                        'date': data.arrival_date.strftime("%d-%m-%Y")
                    })
                    city_list.append(data.to_l.name)
                else:
                    cities.append({
                    'id': data.to_l.id, 
                    'name': data.to_l.name, 
                    'y': 1, 
                    'color': '#28a745' if current_date >= data.arrival_date else '#198fbb' , 
                    'marker' : {'radius': 8} if current_date >= data.arrival_date else {'radius': 4},
                    'date': data.arrival_date.strftime("%d-%m-%Y"),
                    })
                    city_list.append(data.to_l.name)
            if len(dates) > 0:
                start_date = dates[0]
                end_date = dates[-1]
                if start_date <= datetime.date.today() and end_date >= datetime.date.today():
                    tour_list.append({
                        'id': "tour_details_" + str(tour.id),
                        'employee_id': tour.employee_id.id,
                        'employee': tour.employee_id.name,
                        'designation': tour.employee_id.job_id.name,    
                        'department': tour.employee_id.department_id.name,
                        'tour_details':city_list,
                        'cities': cities,
                    })
        
        return tour_list

    @api.model
    def getEmployeeOnTourData(self):
        employees_on_tour_details = { 'employeesOnTourData' : self.fetch_employee_on_tour_data()}
        return employees_on_tour_details

    def fetch_employees_on_leave_data(self):
        today_leave_list, this_week_leave_list = [],[]
        emp_rec = self.env['hr.leave'].search([('request_date_from','<=',datetime.datetime.today().date()),('request_date_to','>=',datetime.datetime.today().date()),('state','=','validate'),('employee_id.branch_id','=',self.env.user.employee_ids.branch_id.id)])
        for emp in emp_rec:
            today_leave_list.append({
                'leave_type' : emp.holiday_status_id.name,
                'emp_name' : emp.employee_id.name,
                'number_of_days': emp.number_of_days,
                'leave_tooltip': 'Leave From: '+ datetime.datetime.strftime(emp.date_from, "%d-%m-%Y") + '<br/> Leave To: ' + datetime.datetime.strftime(emp.date_to, "%d-%m-%Y"),
                'designation' : emp.employee_id.job_id.name,
                'department' : emp.department_id.name,
                'status' : emp.state
            })
        dt = datetime.datetime.strptime(datetime.datetime.today().date().strftime('%d/%b/%Y'), '%d/%b/%Y')
        start_date = dt - datetime.timedelta(days=dt.weekday())
        end_date = start_date + datetime.timedelta(days=6)
        week = []
        week.append(start_date)
        for dat in range(1,7):
            week.append(start_date + datetime.timedelta(days=dat))

        week_leave = self.env['hr.leave'].search([('employee_id.branch_id','=',self.env.user.employee_ids.branch_id.id),('request_date_from','>=',week[0]),('request_date_from','<=',week[len(week)-1]),('state','=','validate')])
        for week in week_leave:
            this_week_leave_list.append({
                'leave_type' : week.holiday_status_id.name,
                'emp_name' : week.employee_id.name,
                'number_of_days': week.number_of_days,
                'leave_tooltip': 'Leave From: '+ datetime.datetime.strftime(week.date_from, "%d-%m-%Y") + '<br/> Leave To: ' + datetime.datetime.strftime(week.date_to, "%d-%m-%Y"),
                'designation' : week.employee_id.job_id.name,
                'department' : week.department_id.name,
                'status' : week.state
            })
        return [today_leave_list, this_week_leave_list]

    @api.model
    def getEmployeesOnLeave(self):
        employeesOnLeave = {'employeesOnLeaveData': self.fetch_employees_on_leave_data()}
        return employeesOnLeave

    def fetch_best_wishes_data(self):
        birthday_wishes,year_of_service_wishes = [],[]

        best_wishes_ids = self.env['hr.employee'].search([('branch_id','=',self.env.user.employee_ids.branch_id.id)])

        for wishes in best_wishes_ids:
            if wishes.birthday and datetime.datetime.today().day == wishes.birthday.day and datetime.datetime.today().month == wishes.birthday.month:
                birthday_wishes.append({
                    'id': wishes.id,
                    'full_name': wishes.name,
                    'name': wishes.name.split(' ')[0][:5] + '..',
                    'gender': wishes.gende,
                    'image_exist': True if wishes.image_medium else False,
                    'wishes_tooltip': wishes.name + '<br/>' + wishes.job_id.name  if wishes.job_id.name else '' + '<br/>' + wishes.department_id.name if wishes.department_id.name else '' 
                })
            if wishes.date_of_join and datetime.datetime.today().day == wishes.date_of_join.day and datetime.datetime.today().month == wishes.date_of_join.month:
                if relativedelta(datetime.date.today(), wishes.date_of_join).years > 0:
                    year_of_service_wishes.append({
                        'id': wishes.id,
                        'full_name': wishes.name,
                        'name': wishes.name.split(' ')[0][:5] + '..',
                        'gender': wishes.gende,
                        'total_year': relativedelta(datetime.date.today(), wishes.date_of_join).years,
                        'image_exist': True if wishes.image_medium else False,
                        'wishes_tooltip': wishes.name + '<br/>' + wishes.job_id.name  if wishes.job_id.name else '' + '<br/>' + wishes.department_id.name if wishes.department_id.name else '' 
                    })
        
        return [birthday_wishes, year_of_service_wishes]

    @api.model
    def getBestWishes(self):
        wishes = {'bestWishesData': self.fetch_best_wishes_data()}
        return wishes
        
    def fetch_my_reimbursement_data(self):
        check_status,yet_to_apply = [],[]
        lunch = '/ks_dashboard_ninja/static/src/img/food.png'
        telephone = '/ks_dashboard_ninja/static/src/img/telephone.png'
        broadband = '/ks_dashboard_ninja/static/src/img/internet.png'
        mobile = '/ks_dashboard_ninja/static/src/img/smartphone.png'
        medical = '/ks_dashboard_ninja/static/src/img/medical-history.png'
        tution ='/ks_dashboard_ninja/static/src/img/test.png'
        hostel = '/ks_dashboard_ninja/static/src/img/bunk-bed.png'
        briefcase = '/ks_dashboard_ninja/static/src/img/suitcase.png'
        newspaper = '/ks_dashboard_ninja/static/src/img/newspaper.png'
        earned = '/ks_dashboard_ninja/static/src/img/wallet.png'

        today_date = datetime.date.today()
        model = self.env['reimbursement.configuration']
        reimbursement_types = model.search([('employee_type', '=', self.env.user.employee_ids.employee_type)])
        filtered_reimbursement_types = reimbursement_types.filtered(lambda r: self.env.user.employee_ids.job_id.id in r.job_ids.ids and self.env.user.employee_ids.job_id.pay_level_id.id in r.pay_level_ids.ids)
        for types in filtered_reimbursement_types:
            if types.reimbursement_type_id.code != 'tuition_fee':
                date_range_id = self.env['date.range'].search([('type_id','=',types.date_range_type.id),('date_end','<=',datetime.datetime.now().date())])
                daterange_id = date_range_id[-1] if len(date_range_id) > 0 else False
            else:
                date_range_id = self.env['date.range'].search([('type_id','=',types.date_range_type.id),('date_start','<=',datetime.datetime.now().date())])
                daterange_id = date_range_id[-1] if len(date_range_id) > 0 else False
            # if types.date_range_type.name == 'Monthly':
            #     one_month_ago = today_date - relativedelta(months=1)
            
            reimbursement_id = self.env['reimbursement'].search([('reimbursement_type_id','=',types.reimbursement_type_id.id),('employee_id','=',self.env.user.employee_ids.id),('date_range','=',daterange_id.id if daterange_id else 0)],order='create_date desc', limit=1)
            if reimbursement_id.state:
                check_status.append({
                    'type': types.reimbursement_type_id.name,
                    'apply_date': datetime.datetime.strftime(types.create_date, "%d-%m-%Y"),
                    'net_amount': "{:,}".format(float("%.2f" % reimbursement_id.net_amount)),
                    'reimbursement_type': lunch if types.reimbursement_type_id.code == 'lunch' else telephone if types.reimbursement_type_id.code == 'telephone' else broadband if types.reimbursement_type_id.code == 'broadband' else mobile if types.reimbursement_type_id.code == 'mobile' else medical if types.reimbursement_type_id.code == 'medical' else tution if types.reimbursement_type_id.code == 'tuition_fee' else hostel if types.reimbursement_type_id.code == 'hostel' else briefcase if types.reimbursement_type_id.code == 'briefcase' else newspaper if types.reimbursement_type_id.code == 'quarterly' else earned,
                    'status': (dict(self.env['reimbursement'].fields_get(allfields='state')['state']['selection'])[reimbursement_id.state]) if reimbursement_id.state else ''
                })
            else:
                yet_to_apply.append({
                    'reimbursement_type_selection': types.reimbursement_type_id.code,
                    'type': types.reimbursement_type_id.name,
                    'date_range_id': daterange_id.id if daterange_id else False,
                    'date_range': daterange_id.name if daterange_id else '',
                    'eligible_amount':"{:,}".format(float("%.2f" % float(types.allowed))),
                    'reimbursement_type': lunch if types.reimbursement_type_id.code == 'lunch' else telephone if types.reimbursement_type_id.code == 'telephone' else broadband if types.reimbursement_type_id.code == 'broadband' else mobile if types.reimbursement_type_id.code == 'mobile' else medical if types.reimbursement_type_id.code == 'medical' else tution if types.reimbursement_type_id.code == 'tuition_fee' else hostel if types.reimbursement_type_id.code == 'hostel' else briefcase if types.reimbursement_type_id.code == 'briefcase' else newspaper if types.reimbursement_type_id.code == 'quarterly' else earned,
                })
        return [check_status,yet_to_apply]

    @api.model
    def getMyReimbursements(self):
        myReimbursement = {'myReimbursementData': self.fetch_my_reimbursement_data()}
        return myReimbursement

    def fetch_employee_inbox_data(self):
        approval_list = []
        model= self.env['approvals.list']
        approval_ids = model.search([('user_id', '=', self.env.user.id),('state','=','pending_approval')])
        for approval in approval_ids:
            approval_name = str(approval.resource_ref.name_get())
            approval_list.append({
                'request_id' : approval.name,
                'rule_id': approval.rule_id.name,
                'model_name': approval.model_id.name,
                'message': approval_name.split(", '")[1][:-3],
                'applied_date': approval.date.strftime("%d-%m-%Y"),
                'approval_deadline': approval.approval_deadline
            })
        return approval_list

    @api.model
    def getEmployeeInbox(self):
        employeeInbox = {'employeeInbox': self.fetch_employee_inbox_data()}
        return employeeInbox

    def fetch_managerial_inbox_data(self):
        date_list                       = []
        for week_date in self.get_week(datetime.date.today()):
            date_list.append(week_date)
        
        start_Date,end_Date             = date_list[0],date_list[-1]

        """ Leave Count """
        total_leave_counts              = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'hr_leave' ),('rule_id.model', '=', 'hr.leave'),('state','=','pending_approval')])
        week_leave_counts               = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'hr_leave' ),('rule_id.model', '=', 'hr.leave'),('state','=','pending_approval'),('date','<',start_Date)])

        """Loan Counts"""
        total_hr_loan_counts            = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'hr_loan'),('state','=','pending_approval')])
        total_hr_loan_close_counts      = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'hr_loan_close'),('state','=','pending_approval')])
        total_loan                      = total_hr_loan_counts + total_hr_loan_close_counts

        week_hr_loan_counts            = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'hr_loan'),('date','<',start_Date),('state','=','pending_approval')])
        week_hr_loan_close_counts      = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'hr_loan_close'),('date','<',start_Date),('state','=','pending_approval')])
        week_loan                      = week_hr_loan_counts + week_hr_loan_close_counts
        
        """Tour Counts"""
        total_tour_request_counts       = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'tour_request'),('state','=','pending_approval')])
        total_tour_claim_request_counts = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'employee_tour_claim'),('state','=','pending_approval')])
        total_tour_count                = total_tour_request_counts + total_tour_claim_request_counts

        week_tour_request_counts       = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'tour_request'),('date','<',start_Date),('state','=','pending_approval')])
        week_tour_claim_request_counts = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'employee_tour_claim'),('date','<',start_Date),('state','=','pending_approval')])
        week_tour_counts                = week_tour_request_counts + week_tour_claim_request_counts

        """Reimbursement Counts"""
        total_reimbursement_counts      = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'reimbursement'),('state','=','pending_approval')])
        week_reimbursement_counts       = self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'reimbursement'),('date','<',start_Date),('state','=','pending_approval')])

        """LTC Counts"""
        total_ltc_advance_counts         =  self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'employee_ltc_advance'),('state','=','pending_approval')])
        total_ltc_claim_counts          =  self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'employee_ltc_claim'),('state','=','pending_approval')])
        total_ltc_counts                = total_ltc_advance_counts + total_ltc_claim_counts

        week_ltc_advance_counts         =  self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'employee_ltc_advance'),('date','<',start_Date),('state','=','pending_approval')])
        week_ltc_claim_counts         =  self.env['approvals.list'].search_count([('rule_id.rule_group' ,'=', 'employee_ltc_claim'),('date','<',start_Date),('state','=','pending_approval')])
        week_ltc_counts          = week_ltc_advance_counts + week_ltc_claim_counts

        return [[total_leave_counts,week_leave_counts],[total_tour_count,week_tour_counts],[total_loan,week_loan],[total_reimbursement_counts,week_reimbursement_counts],[total_ltc_counts,week_ltc_counts]]
    
    @api.model
    def getManagerialInbox(self):
        managerial_inbox        = {'managerial_inbox' : self.fetch_managerial_inbox_data()}
        return managerial_inbox
    
    def fetch_my_appraisal_data(self,args):
        appraisal_year_id = args.get('appraisal_year_id', False)
        user_id = args.get('user_id', False)
        appraisal_ids = self.env['appraisal.main'].search([('employee_id.user_id','=',self.env.user.id),('abap_period','=',int(appraisal_year_id))])

        appraisal_year_id = args.get('appraisal_year_id', False)
        user_id = args.get('user_id', False)
        period_master_list,appraisal_period_id,average1_score,average2_score,average3_score,overall_rate,appraisal_record = [],0,'0.0','0.0','0.0','0.0' ,[]

        appraisal_ids = self.env['appraisal.main'].search([('employee_id.user_id','=',self.env.user.id),('state','=','completed')], order="id desc")
        for appraisal_period in appraisal_ids:
            period_master_list.append({'period_id':appraisal_period.abap_period.id, 'period_name': appraisal_period.abap_period.name})
        print(args)
        # if appraisal_year_id:
        #     current_period = self.env['kw_assessment_period_master'].search([('id','=',int(appraisal_year_id))])

        if args and appraisal_year_id and user_id:
            appraisal_record = self.env['appraisal.main'].search([('abap_period','=',int(appraisal_year_id)),('employee_id.user_id','=',int(user_id))], limit=1)
        else:
            if (len(period_master_list) > 0):
                appraisal_record = self.env['appraisal.main'].search([('abap_period','=',period_master_list[0]['period_id'] or False),('employee_id','=',self.env.user.employee_ids.id)], limit=1)

        if appraisal_record:
            appraisal_period_id = appraisal_record.abap_period.id
            average1_score = float("%.2f" % appraisal_record.average1)  if appraisal_record.average1 else '0.00'
            average2_score = float("%.2f" % appraisal_record.average2)  if appraisal_record.average2 else '0.00'
            average3_score = float("%.2f" % appraisal_record.average3)  if appraisal_record.average3 else '0.00'
            overall_rate = float("%.2f" % appraisal_record.overall_rate_num)  if appraisal_record.overall_rate_num else '0.00'
        else:
            appraisal_period_id = 0
            average1_score = '0.00'
            average2_score = '0.00'
            average3_score = '0.00'
            overall_rate = '0.00'
        print("output",appraisal_record,appraisal_period_id,average1_score,average2_score,average3_score,overall_rate)
        return [period_master_list,appraisal_record,appraisal_period_id,average1_score,average2_score,average3_score,overall_rate]
        
    @api.model
    def getMyAppraisal(self,**kwargs):
        print(kwargs)
        my_appraisal = {'my_appraisal': self.fetch_my_appraisal_data(kwargs)}
        return my_appraisal

    def fetch_efile_data(self):
        correspondences_data, file_data = [],[]
        correspondences_ids = self.env['muk_dms.file'].search([('current_owner_id','=',self.env.user.id),("folder_id", "=", False)],order="action_time desc,write_date desc")
        for cor in correspondences_ids:
            correspondences_data.append({
                'id': cor.id,
                'name': cor.name,
                'letter_number': cor.letter_number,
                'subject': cor.subject
            })
        file_ids = self.env['folder.master'].search([('current_owner_id','=',self.env.user.id)],order="action_time desc,write_date desc")
        for file in file_ids:
            file_data.append({
                'id': file.id,
                'name': file.folder_name,
                'subject': file.subject.subject,
                'number': file.number,
            })

        return [correspondences_data, file_data]

    @api.model
    def geteFile(self):
        efile = {'efile': self.fetch_efile_data()}
        return efile

    @api.model
    def ks_fetch_item(self, item_list, ks_dashboard_id):
        """
        :rtype: object
        :param item_list: list of item ids.
        :return: {'id':[item_data]}
        """
        self = self.ks_set_date(ks_dashboard_id)
        items = {}
        item_model = self.env['ks_dashboard_ninja.item']
        for item_id in item_list:
            item = self.ks_fetch_item_data(item_model.browse(item_id))
            items[item['id']] = item
        return items

    # fetching Item info (Divided to make function inherit easily)
    def ks_fetch_item_data(self, rec):
        """
        :rtype: object
        :param item_id: item object
        :return: object with formatted item data
        """
        if rec.ks_actions:
            action = {}
            context = {}
            try:
                context = eval(rec.ks_actions.context)
            except Exception:
                context = {}

            action['name'] = rec.ks_actions.name
            action['type'] = rec.ks_actions.type
            action['res_model'] = rec.ks_actions.res_model
            action['views'] = rec.ks_actions.views
            action['view_mode'] = rec.ks_actions.view_mode
            action['search_view_id'] = rec.ks_actions.search_view_id.id
            action['context'] = context
            action['target'] = 'current'
        else:
            action = False
        item = {
            'name': rec.name if rec.name else rec.ks_model_id.name if rec.ks_model_id else "Name",
            'ks_background_color': rec.ks_background_color,
            'ks_font_color': rec.ks_font_color,
            # 'ks_domain': rec.ks_domain.replace('"%UID"', str(
            #     self.env.user.id)) if rec.ks_domain and "%UID" in rec.ks_domain else rec.ks_domain,
            'ks_domain': rec.ks_convert_into_proper_domain(rec.ks_domain, rec),
            'ks_dashboard_id': rec.ks_dashboard_ninja_board_id.id,
            'ks_icon': rec.ks_icon,
            'ks_model_id': rec.ks_model_id.id,
            'ks_model_name': rec.ks_model_name,
            'ks_model_display_name': rec.ks_model_id.name,
            'ks_record_count_type': rec.ks_record_count_type,
            'ks_record_count': rec.ks_record_count,
            'id': rec.id,
            'ks_layout': rec.ks_layout,
            'ks_icon_select': rec.ks_icon_select,
            'ks_default_icon': rec.ks_default_icon,
            'ks_default_icon_color': rec.ks_default_icon_color,
            # Pro Fields
            'ks_dashboard_item_type': rec.ks_dashboard_item_type,
            'ks_item_code': rec.item_code,
            'ks_chart_item_color': rec.ks_chart_item_color,
            'ks_chart_groupby_type': rec.ks_chart_groupby_type,
            'ks_chart_relation_groupby': rec.ks_chart_relation_groupby.id,
            'ks_chart_relation_groupby_name': rec.ks_chart_relation_groupby.name,
            'ks_chart_date_groupby': rec.ks_chart_date_groupby,
            'ks_record_field': rec.ks_record_field.id if rec.ks_record_field else False,
            'ks_chart_data': rec.ks_chart_data,
            'ks_list_view_data': rec.ks_list_view_data,
            'ks_chart_data_count_type': rec.ks_chart_data_count_type,
            'ks_bar_chart_stacked': rec.ks_bar_chart_stacked,
            'ks_semi_circle_chart': rec.ks_semi_circle_chart,
            'ks_list_view_type': rec.ks_list_view_type,
            'ks_list_view_group_fields': rec.ks_list_view_group_fields.ids if rec.ks_list_view_group_fields else False,
            'ks_previous_period': rec.ks_previous_period,
            'ks_kpi_data': rec.ks_kpi_data,
            'ks_goal_enable': rec.ks_goal_enable,
            'ks_model_id_2': rec.ks_model_id_2.id,
            'ks_record_field_2': rec.ks_record_field_2.id,
            'ks_data_comparison': rec.ks_data_comparison,
            'ks_target_view': rec.ks_target_view,
            'ks_date_filter_selection': rec.ks_date_filter_selection,
            'ks_show_data_value': rec.ks_show_data_value,
            'ks_update_items_data': rec.ks_update_items_data,
            'ks_show_records': rec.ks_show_records,
            # 'action_id': rec.ks_actions.id if rec.ks_actions else False,
            'sequence': 0,
            'max_sequnce': len(rec.ks_action_lines) if rec.ks_action_lines else False,
            'action': action,
            'ks_chart_sub_groupby_type': rec.ks_chart_sub_groupby_type,
            'ks_chart_relation_sub_groupby': rec.ks_chart_relation_sub_groupby.id,
            'ks_chart_relation_sub_groupby_name': rec.ks_chart_relation_sub_groupby.name,
            'ks_chart_date_sub_groupby': rec.ks_chart_date_sub_groupby,
            'ks_hide_legend': rec.ks_hide_legend,

        }
        return item

    def ks_set_date(self, ks_dashboard_id):
        if self._context.get('ksDateFilterSelection', False):
            ks_date_filter_selection = self._context['ksDateFilterSelection']
            if ks_date_filter_selection == 'l_custom':
                self = self.with_context(
                    ksDateFilterStartDate=fields.datetime.strptime(self._context['ksDateFilterStartDate'],
                                                                   "%Y-%m-%dT%H:%M:%S.%fz"))
                self = self.with_context(
                    ksDateFilterEndDate=fields.datetime.strptime(self._context['ksDateFilterEndDate'],
                                                                 "%Y-%m-%dT%H:%M:%S.%fz"))

        else:
            ks_date_filter_selection = self.browse(ks_dashboard_id).ks_date_filter_selection
            self = self.with_context(ksDateFilterStartDate=self.browse(ks_dashboard_id).ks_dashboard_start_date)
            self = self.with_context(ksDateFilterEndDate=self.browse(ks_dashboard_id).ks_dashboard_end_date)
            self = self.with_context(ksDateFilterSelection=ks_date_filter_selection)

        if ks_date_filter_selection and ks_date_filter_selection not in ['l_custom', 'l_none']:
            ks_date_data = ks_get_date(ks_date_filter_selection, self)
            self = self.with_context(ksDateFilterStartDate=ks_date_data["selected_start_date"])
            self = self.with_context(ksDateFilterEndDate=ks_date_data["selected_end_date"])

        return self

    def ks_view_items_view(self):
        self.ensure_one()
        return {
            'name': _("Dashboard Items"),
            'res_model': 'ks_dashboard_ninja.item',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(False, 'tree'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('ks_dashboard_ninja_board_id', '!=', False)],
            'search_view_id': self.env.ref('ks_dashboard_ninja.ks_item_search_view').id,
            'context': {
                'search_default_ks_dashboard_ninja_board_id': self.id,
                'group_by': 'ks_dashboard_ninja_board_id',
            },
            'help': _('''<p class="o_view_nocontent_smiling_face">
                                        You can find all items related to Dashboard Here.</p>
                                    '''),

        }

    def ks_export_item(self,item_id):
        return {
            'ks_file_format': 'ks_dashboard_ninja_item_export',
            'item': self.ks_export_item_data(self.ks_dashboard_items_ids.browse(int(item_id)))
        }
    # fetching Item info (Divided to make function inherit easily)
    def ks_export_item_data(self, rec):
        ks_chart_measure_field = []
        ks_chart_measure_field_2 = []
        for res in rec.ks_chart_measure_field:
            ks_chart_measure_field.append(res.name)
        for res in rec.ks_chart_measure_field_2:
            ks_chart_measure_field_2.append(res.name)

        ks_list_view_group_fields = []
        for res in rec.ks_list_view_group_fields:
            ks_list_view_group_fields.append(res.name)

        ks_goal_lines = []
        for res in rec.ks_goal_lines:
            goal_line = {
                'ks_goal_date': datetime.datetime.strftime(res.ks_goal_date, "%Y-%m-%d"),
                'ks_goal_value': res.ks_goal_value,
            }
            ks_goal_lines.append(goal_line)

        ks_action_lines = []
        for res in rec.ks_action_lines:
            action_line = {
                'ks_item_action_field': res.ks_item_action_field.name,
                'ks_item_action_date_groupby': res.ks_item_action_date_groupby,
                'ks_chart_type': res.ks_chart_type,
                'ks_sort_by_field': res.ks_sort_by_field.name,
                'ks_sort_by_order': res.ks_sort_by_order,
                'ks_record_limit': res.ks_record_limit,
                'sequence': res.sequence,
            }
            ks_action_lines.append(action_line)

        ks_list_view_field = []
        for res in rec.ks_list_view_fields:
            ks_list_view_field.append(res.name)
        item = {
            'name': rec.name if rec.name else rec.ks_model_id.name if rec.ks_model_id else "Name",
            'ks_background_color': rec.ks_background_color,
            'ks_font_color': rec.ks_font_color,
            'ks_domain': rec.ks_domain,
            'ks_icon': str(rec.ks_icon) if rec.ks_icon else False,
            'ks_id': rec.id,
            'ks_model_id': rec.ks_model_name,
            'ks_record_count': rec.ks_record_count,
            'ks_layout': rec.ks_layout,
            'ks_icon_select': rec.ks_icon_select,
            'ks_default_icon': rec.ks_default_icon,
            'ks_default_icon_color': rec.ks_default_icon_color,
            'ks_record_count_type': rec.ks_record_count_type,
            # Pro Fields
            'ks_dashboard_item_type': rec.ks_dashboard_item_type,
            'ks_chart_item_color': rec.ks_chart_item_color,
            'ks_chart_groupby_type': rec.ks_chart_groupby_type,
            'ks_chart_relation_groupby': rec.ks_chart_relation_groupby.name,
            'ks_chart_date_groupby': rec.ks_chart_date_groupby,
            'ks_record_field': rec.ks_record_field.name,
            'ks_chart_sub_groupby_type': rec.ks_chart_sub_groupby_type,
            'ks_chart_relation_sub_groupby': rec.ks_chart_relation_sub_groupby.name,
            'ks_chart_date_sub_groupby': rec.ks_chart_date_sub_groupby,
            'ks_chart_data_count_type': rec.ks_chart_data_count_type,
            'ks_chart_measure_field': ks_chart_measure_field,
            'ks_chart_measure_field_2': ks_chart_measure_field_2,
            'ks_list_view_fields': ks_list_view_field,
            'ks_list_view_group_fields': ks_list_view_group_fields,
            'ks_list_view_type': rec.ks_list_view_type,
            'ks_record_data_limit': rec.ks_record_data_limit,
            'ks_sort_by_order': rec.ks_sort_by_order,
            'ks_sort_by_field': rec.ks_sort_by_field.name,
            'ks_date_filter_field': rec.ks_date_filter_field.name,
            'ks_goal_enable': rec.ks_goal_enable,
            'ks_standard_goal_value': rec.ks_standard_goal_value,
            'ks_goal_liness': ks_goal_lines,
            'ks_date_filter_selection': rec.ks_date_filter_selection,
            'ks_item_start_date': rec.ks_item_start_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.ks_item_start_date else False,
            'ks_item_end_date': rec.ks_item_end_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.ks_item_end_date else False,
            'ks_date_filter_selection_2': rec.ks_date_filter_selection_2,
            'ks_item_start_date_2': rec.ks_item_start_date_2.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.ks_item_start_date_2 else False,
            'ks_item_end_date_2': rec.ks_item_end_date_2.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.ks_item_end_date_2 else False,
            'ks_previous_period': rec.ks_previous_period,
            'ks_target_view': rec.ks_target_view,
            'ks_data_comparison': rec.ks_data_comparison,
            'ks_record_count_type_2': rec.ks_record_count_type_2,
            'ks_record_field_2': rec.ks_record_field_2.name,
            'ks_model_id_2': rec.ks_model_id_2.model,
            'ks_date_filter_field_2': rec.ks_date_filter_field_2.name,
            'ks_action_liness': ks_action_lines,
            'ks_compare_period': rec.ks_compare_period,
            'ks_year_period': rec.ks_year_period,
            'ks_compare_period_2': rec.ks_compare_period_2,
            'ks_semi_circle_chart': rec.ks_semi_circle_chart,
            'ks_year_period_2': rec.ks_year_period_2,
            'ks_domain_2': rec.ks_domain_2,
            'ks_show_data_value': rec.ks_show_data_value,
            'ks_update_items_data': rec.ks_update_items_data,
            'ks_list_target_deviation_field': rec.ks_list_target_deviation_field.name,
            'ks_unit': rec.ks_unit,
            'ks_show_records': rec.ks_show_records,
            'ks_hide_legend': rec.ks_hide_legend,
            'ks_fill_temporal': rec.ks_fill_temporal,
            'ks_domain_extension': rec.ks_domain_extension,
            'ks_domain_extension_2': rec.ks_domain_extension_2,
            'ks_unit_selection': rec.ks_unit_selection,
            'ks_chart_unit': rec.ks_chart_unit,
            'ks_bar_chart_stacked': rec.ks_bar_chart_stacked,
            'ks_goal_bar_line': rec.ks_goal_bar_line,
        }
        return item


    def ks_import_item(self, dashboard_id, **kwargs):
        try:
            # ks_dashboard_data = json.loads(file)
            file = kwargs.get('file', False)
            ks_dashboard_file_read = json.loads(file)
        except:
            raise ValidationError(_("This file is not supported"))

        if 'ks_file_format' in ks_dashboard_file_read and ks_dashboard_file_read[
            'ks_file_format'] == 'ks_dashboard_ninja_item_export':
            item = ks_dashboard_file_read['item']
        else:
            raise ValidationError(_("Current Json File is not properly formatted according to Dashboard Ninja Model."))

        item['ks_dashboard_ninja_board_id'] = int(dashboard_id)
        self.ks_create_item(item)

        return "Success"

    @api.model
    def ks_dashboard_export(self, ks_dashboard_ids):
        ks_dashboard_data = []
        ks_dashboard_export_data = {}
        ks_dashboard_ids = json.loads(ks_dashboard_ids)
        for ks_dashboard_id in ks_dashboard_ids:
            dashboard_data = {
                'name': self.browse(ks_dashboard_id).name,
                'ks_dashboard_menu_name': self.browse(ks_dashboard_id).ks_dashboard_menu_name,
                'ks_gridstack_config': self.browse(ks_dashboard_id).ks_gridstack_config,
                'ks_set_interval': self.browse(ks_dashboard_id).ks_set_interval,
                'ks_date_filter_selection': self.browse(ks_dashboard_id).ks_date_filter_selection,
                'ks_dashboard_start_date': self.browse(ks_dashboard_id).ks_dashboard_start_date,
                'ks_dashboard_end_date': self.browse(ks_dashboard_id).ks_dashboard_end_date,
                'ks_dashboard_top_menu_id': self.browse(ks_dashboard_id).ks_dashboard_top_menu_id.id,
            }
            if len(self.browse(ks_dashboard_id).ks_dashboard_items_ids) < 1:
                dashboard_data['ks_item_data'] = False
            else:
                items = []
                for rec in self.browse(ks_dashboard_id).ks_dashboard_items_ids:
                    item = self.ks_export_item_data(rec)
                    items.append(item)

                dashboard_data['ks_item_data'] = items

            ks_dashboard_data.append(dashboard_data)

            ks_dashboard_export_data = {
                'ks_file_format': 'ks_dashboard_ninja_export_file',
                'ks_dashboard_data': ks_dashboard_data
            }
        return ks_dashboard_export_data

    @api.model
    def ks_import_dashboard(self, file):
        try:
            # ks_dashboard_data = json.loads(file)
            ks_dashboard_file_read = json.loads(file)
        except:
            raise ValidationError(_("This file is not supported"))

        if 'ks_file_format' in ks_dashboard_file_read and ks_dashboard_file_read[
            'ks_file_format'] == 'ks_dashboard_ninja_export_file':
            ks_dashboard_data = ks_dashboard_file_read['ks_dashboard_data']
        else:
            raise ValidationError(_("Current Json File is not properly formatted according to Dashboard Ninja Model."))

        ks_dashboard_key = ['name', 'ks_dashboard_menu_name', 'ks_gridstack_config']
        ks_dashboard_item_key = ['ks_model_id', 'ks_chart_measure_field', 'ks_list_view_fields', 'ks_record_field',
                                 'ks_chart_relation_groupby', 'ks_id']

        # Fetching dashboard model info
        for data in ks_dashboard_data:
            if not all(key in data for key in ks_dashboard_key):
                raise ValidationError(
                    _("Current Json File is not properly formatted according to Dashboard Ninja Model."))
            ks_dashboard_top_menu_id = data.get('ks_dashboard_top_menu_id', False)
            if ks_dashboard_top_menu_id:
                try:
                    self.env['ir.ui.menu'].browse(ks_dashboard_top_menu_id).name
                    ks_dashboard_top_menu_id = self.env['ir.ui.menu'].browse(ks_dashboard_top_menu_id)
                except Exception:
                    ks_dashboard_top_menu_id = False
            vals = {
                'name': data.get('name'),
                'ks_dashboard_menu_name': data.get('ks_dashboard_menu_name'),
                'ks_dashboard_top_menu_id': ks_dashboard_top_menu_id.id if ks_dashboard_top_menu_id else self.env.ref("ks_dashboard_ninja.board_menu_root").id,
                'ks_dashboard_active': True,
                'ks_gridstack_config': data.get('ks_gridstack_config'),
                'ks_dashboard_default_template': self.env.ref("ks_dashboard_ninja.ks_blank").id,
                'ks_dashboard_group_access': False,
                'ks_set_interval': data.get('ks_set_interval'),
                'ks_date_filter_selection': data.get('ks_date_filter_selection'),
                'ks_dashboard_start_date': data.get('ks_dashboard_start_date'),
                'ks_dashboard_end_date': data.get('ks_dashboard_end_date'),
            }
            # Creating Dashboard
            dashboard_id = self.create(vals)

            if data['ks_gridstack_config']:
                ks_gridstack_config = eval(data['ks_gridstack_config'])
            ks_grid_stack_config = {}

            item_ids = []
            item_new_ids = []
            if data['ks_item_data']:
                # Fetching dashboard item info
                for item in data['ks_item_data']:
                    if not all(key in item for key in ks_dashboard_item_key):
                        raise ValidationError(
                            _("Current Json File is not properly formatted according to Dashboard Ninja Model."))

                    # Creating dashboard items
                    item['ks_dashboard_ninja_board_id'] = dashboard_id.id
                    item_ids.append(item['ks_id'])
                    del item['ks_id']
                    ks_item = self.ks_create_item(item)
                    item_new_ids.append(ks_item.id)

            for id_index, id in enumerate(item_ids):
                if data['ks_gridstack_config'] and str(id) in ks_gridstack_config:
                    ks_grid_stack_config[str(item_new_ids[id_index])] = ks_gridstack_config[str(id)]

            self.browse(dashboard_id.id).write({
                'ks_gridstack_config': json.dumps(ks_grid_stack_config)
            })

        return "Success"
        # separate function to make item for import

    def ks_create_item(self,item):
        model = self.env['ir.model'].search([('model', '=', item['ks_model_id'])])

        if item.get('ks_data_calculation_type')  is not None and item['ks_model_id'] == False:
            raise ValidationError(_(
                "That Item contain properties of the Dashboard Ninja Adavance, Please Install the Module "
                "Dashboard Ninja Advance."))

        if not model:
            raise ValidationError(_(
                "Please Install the Module which contains the following Model : %s " % item['ks_model_id']))

        ks_model_name = item['ks_model_id']

        ks_goal_lines = item['ks_goal_liness'].copy() if item.get('ks_goal_liness', False) else False
        ks_action_lines = item['ks_action_liness'].copy() if item.get('ks_action_liness', False) else False

        # Creating dashboard items
        item = self.ks_prepare_item(item)

        if 'ks_goal_liness' in item:
            del item['ks_goal_liness']
        if 'ks_id' in item:
            del item['ks_id']
        if 'ks_action_liness' in item:
            del item['ks_action_liness']
        if 'ks_icon' in item:
            item['ks_icon_select'] = "Default"
            item['ks_icon'] = False

        ks_item = self.env['ks_dashboard_ninja.item'].create(item)

        if ks_goal_lines and len(ks_goal_lines) != 0:
            for line in ks_goal_lines:
                line['ks_goal_date'] = datetime.datetime.strptime(line['ks_goal_date'].split(" ")[0],
                                                                  '%Y-%m-%d')
                line['ks_dashboard_item'] = ks_item.id
                self.env['ks_dashboard_ninja.item_goal'].create(line)

        if ks_action_lines and len(ks_action_lines) != 0:

            for line in ks_action_lines:
                if line['ks_sort_by_field']:
                    ks_sort_by_field = line['ks_sort_by_field']
                    ks_sort_record_id = self.env['ir.model.fields'].search(
                        [('model', '=', ks_model_name), ('name', '=', ks_sort_by_field)])
                    if ks_sort_record_id:
                        line['ks_sort_by_field'] = ks_sort_record_id.id
                    else:
                        line['ks_sort_by_field'] = False
                if line['ks_item_action_field']:
                    ks_item_action_field = line['ks_item_action_field']
                    ks_record_id = self.env['ir.model.fields'].search(
                        [('model', '=', ks_model_name), ('name', '=', ks_item_action_field)])
                    if ks_record_id:
                        line['ks_item_action_field'] = ks_record_id.id
                        line['ks_dashboard_item_id'] = ks_item.id
                        self.env['ks_dashboard_ninja.item_action'].create(line)

        return ks_item

    def ks_prepare_item(self, item):
        ks_measure_field_ids = []
        ks_measure_field_2_ids = []

        for ks_measure in item['ks_chart_measure_field']:
            ks_measure_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_measure), ('model', '=', item['ks_model_id'])])
            if ks_measure_id:
                ks_measure_field_ids.append(ks_measure_id.id)
        item['ks_chart_measure_field'] = [(6, 0, ks_measure_field_ids)]

        for ks_measure in item['ks_chart_measure_field_2']:
            ks_measure_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_measure), ('model', '=', item['ks_model_id'])])
            if ks_measure_id:
                ks_measure_field_2_ids.append(ks_measure_id.id)
        item['ks_chart_measure_field_2'] = [(6, 0, ks_measure_field_2_ids)]

        ks_list_view_group_fields = []
        for ks_measure in item['ks_list_view_group_fields']:
            ks_measure_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_measure), ('model', '=', item['ks_model_id'])])

            if ks_measure_id:
                ks_list_view_group_fields.append(ks_measure_id.id)
        item['ks_list_view_group_fields'] = [(6, 0, ks_list_view_group_fields)]

        ks_list_view_field_ids = []
        for ks_list_field in item['ks_list_view_fields']:
            ks_list_field_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_list_field), ('model', '=', item['ks_model_id'])])
            if ks_list_field_id:
                ks_list_view_field_ids.append(ks_list_field_id.id)
        item['ks_list_view_fields'] = [(6, 0, ks_list_view_field_ids)]

        if item['ks_record_field']:
            ks_record_field = item['ks_record_field']
            ks_record_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_record_field), ('model', '=', item['ks_model_id'])])
            if ks_record_id:
                item['ks_record_field'] = ks_record_id.id
            else:
                item['ks_record_field'] = False

        if item['ks_date_filter_field']:
            ks_date_filter_field = item['ks_date_filter_field']
            ks_record_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_date_filter_field), ('model', '=', item['ks_model_id'])])
            if ks_record_id:
                item['ks_date_filter_field'] = ks_record_id.id
            else:
                item['ks_date_filter_field'] = False

        if item['ks_chart_relation_groupby']:
            ks_group_by = item['ks_chart_relation_groupby']
            ks_record_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_group_by), ('model', '=', item['ks_model_id'])])
            if ks_record_id:
                item['ks_chart_relation_groupby'] = ks_record_id.id
            else:
                item['ks_chart_relation_groupby'] = False

        if item['ks_chart_relation_sub_groupby']:
            ks_group_by = item['ks_chart_relation_sub_groupby']
            ks_chart_relation_sub_groupby = self.env['ir.model.fields'].search(
                [('name', '=', ks_group_by), ('model', '=', item['ks_model_id'])])
            if ks_chart_relation_sub_groupby:
                item['ks_chart_relation_sub_groupby'] = ks_chart_relation_sub_groupby.id
            else:
                item['ks_chart_relation_sub_groupby'] = False

        # Sort by field : Many2one Entery
        if item['ks_sort_by_field']:
            ks_group_by = item['ks_sort_by_field']
            ks_sort_by_field = self.env['ir.model.fields'].search(
                [('name', '=', ks_group_by), ('model', '=', item['ks_model_id'])])
            if ks_sort_by_field:
                item['ks_sort_by_field'] = ks_sort_by_field.id
            else:
                item['ks_sort_by_field'] = False

        if item['ks_list_target_deviation_field']:
            ks_list_target_deviation_field = item['ks_list_target_deviation_field']
            record_id = self.env['ir.model.fields'].search(
                [('name', '=', ks_list_target_deviation_field), ('model', '=', item['ks_model_id'])])
            if record_id:
                item['ks_list_target_deviation_field'] = record_id.id
            else:
                item['ks_list_target_deviation_field'] = False

        ks_model_id = self.env['ir.model'].search([('model', '=', item['ks_model_id'])]).id

        if (item['ks_model_id_2']):
            ks_model_2 = item['ks_model_id_2'].replace(".", "_")
            ks_model_id_2 = self.env['ir.model'].search([('model', '=', item['ks_model_id_2'])]).id
            if item['ks_record_field_2']:
                ks_record_field = item['ks_record_field_2']
                ks_record_id = self.env['ir.model.fields'].search(
                    [('model', '=', item['ks_model_id_2']), ('name', '=', ks_record_field)])

                if ks_record_id:
                    item['ks_record_field_2'] = ks_record_id.id
                else:
                    item['ks_record_field_2'] = False
            if item['ks_date_filter_field_2']:
                ks_record_id = self.env['ir.model.fields'].search(
                    [('model', '=', item['ks_model_id_2']), ('name', '=', item['ks_date_filter_field_2'])])

                if ks_record_id:
                    item['ks_date_filter_field_2'] = ks_record_id.id
                else:
                    item['ks_date_filter_field_2'] = False

            item['ks_model_id_2'] = ks_model_id_2
        else:
            item['ks_date_filter_field_2'] = False
            item['ks_record_field_2'] = False

        item['ks_model_id'] = ks_model_id

        item['ks_goal_liness'] = False
        item['ks_item_start_date'] = datetime.datetime.strptime(item['ks_item_start_date'].split(" ")[0], '%Y-%m-%d') if \
            item['ks_item_start_date'] else False
        item['ks_item_end_date'] = datetime.datetime.strptime(item['ks_item_end_date'].split(" ")[0], '%Y-%m-%d') if \
            item['ks_item_end_date'] else False
        item['ks_item_start_date_2'] = datetime.datetime.strptime(item['ks_item_start_date_2'].split(" ")[0],
                                                                  '%Y-%m-%d') if \
            item['ks_item_start_date_2'] else False
        item['ks_item_end_date_2'] = datetime.datetime.strptime(item['ks_item_end_date_2'].split(" ")[0], '%Y-%m-%d') if \
            item['ks_item_end_date_2'] else False

        return item

    # List view pagination
    @api.model
    def ks_get_list_view_data_offset(self, ks_dashboard_item_id, offset, dashboard_id):
        self = self.ks_set_date(dashboard_id)
        item = self.ks_dashboard_items_ids.browse(ks_dashboard_item_id)

        return item.ks_get_next_offset(ks_dashboard_item_id, offset)