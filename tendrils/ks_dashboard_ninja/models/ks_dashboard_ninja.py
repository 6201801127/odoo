# -*- coding: utf-8 -*-
from statistics import mode
from tracemalloc import start
import pytz,random
from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
import datetime, calendar
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import json
import secrets
from datetime import date,timedelta
from odoo.addons.ks_dashboard_ninja.lib.ks_date_filter_selections import ks_get_date
import locale

locale.setlocale(locale.LC_ALL, '')

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

    def get_month_year_list(self):
        current_year = datetime.datetime.now().date().year
        current_month = datetime.datetime.now().date().month
        years,months = [],[]
        for year in range(current_year,2019,-1):
            years.append({'year_index': year, 'year': year})

        for month in range(1,13):
            months.append({'month_index': datetime.date(current_year, month, 1).strftime('%m'),'month_name': datetime.date(current_year, month, 1).strftime('%B')})
        return[years,months]
        
    def get_branch_data(self):
        branch_list = []
        branches = self.env['kw_res_branch'].sudo().search([('active','=',True)])
        for branch in branches:
            branch_list.append({'id': branch.id,'name': branch.alias})
        return branch_list

    def get_department_and_location_data(self):
        data = []
        locations = self.env['kw_res_branch'].sudo().search_read([],['id','alias'])
        departments = self.env['hr.department'].sudo().search_read([('dept_type.code','=','department')],['id','name'])
        data.append({'locations': locations, 'departments': departments})
        return data

    def kwantify_employee_directory(self,args, limit=15):
        # offset = args.get('offset', False)
        # print(args)
        emp_table = 'select e.id from hr_employee e'
        join_table = 'left join kwemp_grade g on g.grade_id = e.grade and coalesce(g.band_id, 0) = coalesce(e.emp_band, 0)'
        order_by = "order by g.sort_no desc NULLS LAST, e.date_of_joining asc, e.name asc"
        load_button = False
        employees,employees_list,offset_employees,offset_employees_list,emp_ids,off_emp_ids = [],[],[],[],[],[]
        attendance,query,off_query,location,departments_filter = '','','','',''
        employee_id = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id)])
        department = employee_id.department_id.name if 'new_joinee' not in args else False
        has_group_employee_manager = self.env.user.has_group('hr.group_hr_manager')
        
        # print(args)
        page = args.get('offset', False)
        if 'offset' in args:
            if 'operation' in args:
                if args.get('operation') == 'empSearch':
                    off_query = f"{emp_table} {join_table} where e.name ilike '%{args.get('value')}%' or e.work_email ilike '%{args.get('value')}%' or e.mobile_phone ilike '%{args.get('value')}%' or e.epbx_no ilike '%{args.get('value')}%' {order_by} limit {limit} offset {limit*page}"
                elif args.get('operation') == 'refresh':
                    off_query = f"{emp_table} {join_table} where e.department_id = {employee_id.department_id.id} {order_by} limit {limit} offset {limit*page}"
                elif args.get('operation') == 'presence':
                    if args.get('value') == 'present':
                        attendance = 'Present'
                        present_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('check_in','!=',False)]).mapped('employee_id').ids
                        if len(present_attendance_records) > 1:
                            off_query = f"{emp_table} {join_table} where e.id in {tuple(present_attendance_records)} {order_by} limit {limit} offset {limit*page}"
                        elif len(present_attendance_records) == 1:
                            off_query = f"{emp_table} {join_table} where e.id in ({present_attendance_records[0]}) {order_by} limit {limit} offset {limit*page}"
                        else:
                            off_query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit} offset {limit*page}"

                    elif args.get('value') == 'absent':
                        attendance = 'Absent'
                        absent_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status', 'in',['0','3'])]).mapped('employee_id').ids
                        if len(absent_attendance_records) > 1:
                            off_query = f"{emp_table} {join_table} where e.id in {tuple(absent_attendance_records)} {order_by} limit {limit} offset {limit*page}"
                        elif len(absent_attendance_records) == 1:
                            off_query = f"{emp_table} {join_table} where e.id in ({absent_attendance_records[0]}) {order_by} limit {limit} offset {limit*page}"
                        else:
                            off_query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit} offset {limit*page}"

                    elif args.get('value') == 'tour':
                        attendance = 'Tour'
                        tour_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('is_on_tour','=',True)]).mapped('employee_id').ids
                        if len(tour_attendance_records) > 1:
                            off_query = f"{emp_table} {join_table} where e.id in {tuple(tour_attendance_records)} {order_by} limit {limit} offset {limit*page}"
                        elif len(tour_attendance_records) == 1:
                            off_query = f"{emp_table} {join_table} where e.id in ({tour_attendance_records[0]}) {order_by} limit {limit} offset {limit*page}"
                        else:
                            off_query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit} offset {limit*page}"

                    elif args.get('value') == 'leave':
                        attendance = 'Leave'
                        leave_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('leave_status','!=',False)]).mapped('employee_id').ids
                        if len(leave_attendance_records) > 1:
                            off_query = f"{emp_table} {join_table} where e.id in {tuple(leave_attendance_records)} {order_by} limit {limit} offset {limit*page}"
                        elif len(leave_attendance_records) == 1:
                            off_query = f"{emp_table} {join_table} where e.id in ({leave_attendance_records[0]}) {order_by} limit {limit} offset {limit*page}"
                        else:
                            off_query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit} offset {limit*page}"


                elif args.get('operation') == 'location':
                    locations = self.env['kw_res_branch'].sudo().search([('id','=',int(args.get('value',False)))])
                    location = locations.alias
                    off_query = f"{emp_table} {join_table} where e.job_branch_id = {int(args.get('value'))} {order_by} limit {limit} offset {limit*page}"

                elif args.get('operation') == 'department':
                    departments = self.env['hr.department'].sudo().search([('id','=',int(args.get('value',False)))])
                    departments_filter = departments.name
                    off_query = f"{emp_table} {join_table} where e.department_id = {int(args.get('value'))} {order_by} limit {limit} offset {limit*page}"
                elif args.get('operation') == 'reset_filter':
                    off_query = f"{emp_table} {join_table} {order_by} limit {limit} offset {limit*page}"
                else:
                    off_query = f"{emp_table} {join_table} where e.department_id = {employee_id.department_id.id} {order_by} limit {limit} offset {limit*page}"
                
        elif 'reset_filter' in args and args.get('reset_filter') == True:
            query = f"{emp_table} {join_table} {order_by} limit {limit}"
            
        elif 'empSearch' in args and args.get('empSearch'):
            query = f"{emp_table} {join_table} where e.name ilike '%{args.get('empSearch')}%' or e.work_email ilike '%{args.get('empSearch')}%' or e.mobile_phone ilike '%{args.get('empSearch')}%' or e.epbx_no ilike '%{args.get('empSearch')}%' {order_by} limit {limit}"

        elif 'refresh' in args and args.get('refresh') == True:
            query = f"{emp_table} {join_table} where e.department_id = {employee_id.department_id.id} {order_by} limit {limit}"
            
        elif 'presence' in args:
            if args.get('presence') == 'present':
                attendance = 'Present'
                present_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('check_in','!=',False)]).mapped('employee_id').ids
                if len(present_attendance_records) > 1:
                    query = f"{emp_table} {join_table} where e.id in {tuple(present_attendance_records)} {order_by} limit {limit}"
                elif len(present_attendance_records) == 1:
                    query = f"{emp_table} {join_table} where e.id in ({present_attendance_records[0]}) {order_by} limit {limit}"
                else:
                    query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit}"
            elif args.get('presence') == 'absent':
                attendance = 'Absent'
                absent_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status', 'in',['0','3'])]).mapped('employee_id').ids
                if len(absent_attendance_records) > 1:
                    query = f"{emp_table} {join_table} where e.id in {tuple(absent_attendance_records)} {order_by} limit {limit}"
                elif len(absent_attendance_records) == 1:
                    query = f"{emp_table} {join_table} where e.id in ({absent_attendance_records[0]}) {order_by} limit {limit}"
                else:
                    query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit}"
            elif args.get('presence') == 'tour':
                attendance = 'Tour'
                tour_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('is_on_tour','=',True)]).mapped('employee_id').ids
                if len(tour_attendance_records) > 1:
                    query = f"{emp_table} {join_table} where e.id in {tuple(tour_attendance_records)} {order_by} limit {limit}"
                elif len(tour_attendance_records) == 1:
                    query = f"{emp_table} {join_table} where e.id in ({tour_attendance_records[0]}) {order_by} limit {limit}"
                else:
                    query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit}"
            elif args.get('presence') == 'leave':
                attendance = 'Leave'
                leave_attendance_records = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('leave_status','!=',False)]).mapped('employee_id').ids
                if len(leave_attendance_records) > 1:
                    query = f"{emp_table} {join_table} where e.id in {tuple(leave_attendance_records)} {order_by} limit {limit}"
                elif len(leave_attendance_records) == 1:
                    query = f"{emp_table} {join_table} where e.id in ({leave_attendance_records[0]}) {order_by} limit {limit}"
                else:
                    query = f"{emp_table} {join_table} where e.id in (NULL) {order_by} limit {limit}"

        elif 'location' in args:
            locations = self.env['kw_res_branch'].sudo().search([('id','=',int(args.get('location', False)))])
            location = locations.alias
            query = f"{emp_table} {join_table} where e.job_branch_id = {int(args.get('location'))} {order_by} limit {limit}"

        elif 'department' in args:
            departments = self.env['hr.department'].sudo().search([('id','=',int(args.get('department', False)))])
            departments_filter = departments.name
            query = f"{emp_table} {join_table} where e.department_id = {int(args.get('department'))} {order_by} limit {limit}"

        else:
            query = f"{emp_table} {join_table} where e.department_id = {employee_id.department_id.id} {order_by} limit {limit}"
        

        if query:
            self._cr.execute(query)
            emp_ids = self._cr.fetchall()
            if len(emp_ids) > 0:
                employees = self.env['hr.employee'].browse([c[0] for c in emp_ids])
        if off_query:
            self._cr.execute(off_query)
            off_emp_ids = self._cr.fetchall()
            if len(off_emp_ids) > 0:
                offset_employees = self.env['hr.employee'].browse([c[0] for c in off_emp_ids])

        if len(employees) == limit or len(offset_employees) == limit:
            load_button = True

        # import urllib
        # url = 'http://crazy.ai/medhak'
        # medha_status = urllib.request.urlopen(url).getcode()
        medha_status = 200

        for emp in employees:
            if emp.active == True and emp.employement_type.code != 'O':
                employees_list.append({
                    'id' : emp.id,
                    'name' : emp.name,
                    'work_phone' : emp.mobile_phone,
                    'epbx_no' : emp.epbx_no,
                    # 'image' : emp.image,
                    'work_email' : emp.work_email,
                    'attendance_state' :  emp.attendance_state ,
                    'emp_code' : emp.emp_code,
                    'dob': emp.date_of_joining,
                    'date_of_joining' : datetime.datetime.strftime(emp.date_of_joining, "%d-%b-%Y") if emp.date_of_joining else 'NA',
                    'job_id' : emp.job_id.name,
                    'department_id' : emp.department_id.name,
                    'division' : emp.division.name,'employee_manager': has_group_employee_manager,
                    'section': emp.section.name,
                    'practice': emp.practise.name,
                    'job_branch_id' : emp.job_branch_id.alias,
                    'parent_id' : emp.parent_id.display_name,
                    'today_attendance_status' : 'present' if (emp.id == 3500 and medha_status == 200) else emp.today_attendance_status,
                    'present_address1': emp.present_addr_street,
                    'present_address2': emp.present_addr_street2,
                    'present_country': emp.present_addr_country_id.name,
                    'present_state': emp.present_addr_state_id.name,
                    'present_city': emp.present_addr_city,
                    'new_joinee': True if emp.date_of_joining and emp.date_of_joining >= (datetime.datetime.now().date() - datetime.timedelta(days = 15)) else False
                })
            if emp.active == True and emp.employement_type.code == 'O' and emp.id in [3774,5407]:
                employees_list.append({
                    'id' : emp.id,
                    'name' : emp.name,
                    'work_phone' : emp.mobile_phone,
                    'epbx_no' : emp.epbx_no,
                    # 'image' : emp.image,
                    'work_email' : emp.work_email,
                    'attendance_state' :  emp.attendance_state ,
                    'emp_code' : emp.emp_code,
                    'dob': emp.date_of_joining,
                    'date_of_joining' : datetime.datetime.strftime(emp.date_of_joining, "%d-%b-%Y") if emp.date_of_joining else 'NA',
                    'job_id' : emp.job_id.name,
                    'department_id' : emp.department_id.name,
                    'division' : emp.division.name,'employee_manager': has_group_employee_manager,
                    'section': emp.section.name,
                    'practice': emp.practise.name,
                    'job_branch_id' : emp.job_branch_id.alias,
                    'parent_id' : emp.parent_id.display_name,
                    'today_attendance_status' : 'present' if (emp.id == 3500 and medha_status == 200) else emp.today_attendance_status,
                    'present_address1': emp.present_addr_street,
                    'present_address2': emp.present_addr_street2,
                    'present_country': emp.present_addr_country_id.name,
                    'present_state': emp.present_addr_state_id.name,
                    'present_city': emp.present_addr_city,
                    'new_joinee': True if emp.date_of_joining and emp.date_of_joining >= (datetime.datetime.now().date() - datetime.timedelta(days = 15)) else False
                })

        for off_emp in offset_employees:
            if off_emp.active == True and off_emp.employement_type.code != 'O':
                offset_employees_list.append({
                    'id' : off_emp.id,
                    'name' : off_emp.name,
                    'work_phone' : off_emp.mobile_phone,
                    'epbx_no' : off_emp.epbx_no,
                    # 'image' : off_emp.image,
                    'work_email' : off_emp.work_email,
                    'attendance_state' : off_emp.attendance_state,
                    'emp_code' : off_emp.emp_code,
                    'dob':off_emp.date_of_joining,
                    'date_of_joining' : datetime.datetime.strftime(off_emp.date_of_joining, "%d-%b-%Y") if off_emp.date_of_joining else 'NA',
                    'job_id' : off_emp.job_id.name,
                    'department_id' : off_emp.department_id.name,
                    'division' : off_emp.division.name,
                    'section': off_emp.section.name,
                    'practice': off_emp.practise.name,
                    'job_branch_id' : off_emp.job_branch_id.alias,
                    'parent_id' : off_emp.parent_id.display_name,
                    'today_attendance_status' : 'present' if (off_emp.id == 3500 and medha_status == 200) else off_emp.today_attendance_status,
                    'present_address1': off_emp.present_addr_street,
                    'present_address2': off_emp.present_addr_street2,
                    'present_country': off_emp.present_addr_country_id.name,
                    'present_state': off_emp.present_addr_state_id.name,
                    'present_city': off_emp.present_addr_city,
                    'new_joinee': True if off_emp.date_of_joining and off_emp.date_of_joining  >= (datetime.datetime.now().date() - datetime.timedelta(days = 15)) else False
                })
            if off_emp.active == True and off_emp.employement_type.code == 'O' and off_emp.id in [3774,5407]:
                offset_employees_list.append({
                    'id' : off_emp.id,
                    'name' : off_emp.name,
                    'work_phone' : off_emp.mobile_phone,
                    'epbx_no' : off_emp.epbx_no,
                    # 'image' : off_emp.image,
                    'work_email' : off_emp.work_email,
                    'attendance_state' : off_emp.attendance_state,
                    'emp_code' : off_emp.emp_code,
                    'dob':off_emp.date_of_joining,
                    'date_of_joining' : datetime.datetime.strftime(off_emp.date_of_joining, "%d-%b-%Y") if off_emp.date_of_joining else 'NA',
                    'job_id' : off_emp.job_id.name,
                    'department_id' : off_emp.department_id.name,
                    'division' : off_emp.division.name,
                    'section': off_emp.section.name,
                    'practice': off_emp.practise.name,
                    'job_branch_id' : off_emp.job_branch_id.alias,
                    'parent_id' : off_emp.parent_id.display_name,
                    'today_attendance_status' : 'present' if (off_emp.id == 3500 and medha_status == 200) else off_emp.today_attendance_status,
                    'present_address1': off_emp.present_addr_street,
                    'present_address2': off_emp.present_addr_street2,
                    'present_country': off_emp.present_addr_country_id.name,
                    'present_state': off_emp.present_addr_state_id.name,
                    'present_city': off_emp.present_addr_city,
                    'new_joinee': True if off_emp.date_of_joining and off_emp.date_of_joining  >= (datetime.datetime.now().date() - datetime.timedelta(days = 15)) else False
                })

            

        return [department, employees_list, offset_employees_list, location, attendance, departments_filter, load_button,has_group_employee_manager]

    def current_month_attendance(self):
        current_date = datetime.datetime.now().date()
        current_year = datetime.datetime.now().date().year
        current_month = datetime.datetime.now().date().month
        present_days,absent_days,leave_days,late_entry_days,worked_hours_data = [],[],[],[],[]
        check_in_time,check_out_time,check_in,check_out,color = "","","","",""

        current_month_year = datetime.datetime.now().date().strftime("%b")+ ' ' + str(current_year)
        attendance_records = self.env['kw_daily_employee_attendance'].search([('employee_id.user_id','=',self.env.user.id),('attendance_recorded_date','=',current_date)])
        for record in attendance_records:
            emp_tz = record.employee_id.tz or 'UTC' 
            emp_timezone = pytz.timezone(emp_tz)
            check_in_time = datetime.datetime.strftime(record.check_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M %p") if record.check_in else  ''
            check_out_time = datetime.datetime.strftime(record.check_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M %p") if record.check_out else  ''

        month_attendance_records = self.env['kw_daily_employee_attendance'].search([('employee_id.user_id','=',self.env.user.id)])
        for data in month_attendance_records:
            if data.attendance_recorded_date.month == current_month and data.attendance_recorded_date.year == current_year:
                if data.check_in != False and data.state in ['1','7','8']:
                    present_data_list = [data.attendance_recorded_date.year, data.attendance_recorded_date.month, data.attendance_recorded_date.day, 'present']
                    present_days.append(present_data_list)

                if data.check_in == False and data.leave_status not in ['1','2','3'] and data.is_on_tour == False and data.day_status in ['0','3']:
                    absent_data_list = [data.attendance_recorded_date.year, data.attendance_recorded_date.month, data.attendance_recorded_date.day, 'absent']
                    absent_days.append(absent_data_list)

                if data.leave_status != False:
                    leave_data_list = [data.attendance_recorded_date.year, data.attendance_recorded_date.month, data.attendance_recorded_date.day, 'leave']
                    leave_days.append(leave_data_list)

                if data.check_in_status in ['2','3'] and data.day_status in ['0','3']:
                    late_entry_data_list = [data.attendance_recorded_date.year, data.attendance_recorded_date.month, data.attendance_recorded_date.day, 'late_entry']
                    late_entry_days.append(late_entry_data_list)
        
        attendance_data = self.env['kw_daily_employee_attendance'].search([('employee_id.user_id','=',self.env.user.id)], order="attendance_recorded_date asc")
        for rec in attendance_data:
            emp_tz = rec.employee_id.tz or 'UTC' 
            emp_timezone = pytz.timezone(emp_tz)
            worked = 0
            if rec.attendance_recorded_date.month == current_month and rec.attendance_recorded_date.year == current_year:
                check_in = datetime.datetime.strftime(rec.check_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M %p") if rec.check_in else  ''
                check_out = datetime.datetime.strftime(rec.check_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M %p") if rec.check_out else  ''
                if rec.shift_id:
                    worked = (rec.worked_hours/(rec.shift_out_time - rec.shift_in_time - rec.shift_rest_time))*100
                worked = float("%.2f" % worked)
                color = '#28a745' if rec.check_in != False else '#ff9800' if rec.check_in == False and rec.leave_status not in ['1','2','3'] and rec.is_on_tour == False and rec.day_status in ['0','3']  else '#108fbb' if rec.leave_status != False else '#ffc107' if rec.check_in_status in ['2','3'] and rec.day_status in ['0','3'] else '#7f7f7f'
                worked_hours_data.append({
                    'date': rec.attendance_recorded_date,
                    'y': worked,
                    'color': color,
                    'effort': str(worked) + "%",
                    'office_In': check_in,
                    'office_Out': check_out
                    })
        start_date = sorted(worked_hours_data, key=lambda r: r['date'])[0] if worked_hours_data else []
        attendance_start_date = start_date['date'].day if start_date else False
        return [present_days,absent_days,leave_days,late_entry_days,check_in_time,check_out_time, current_month_year, worked_hours_data,attendance_start_date]
    
    def current_employee_subordinates(self):
        current_year = datetime.datetime.now().date().year
        current_month = datetime.datetime.now().date().month
        years, months, currentUserAndSubordinates = [], [], []
        for year in range(current_year, 2019, -1):
            years.append({'year_index': year, 'year': year})

        for month in range(1, 13):
            months.append({'month_index': datetime.date(current_year, month, 1).strftime('%m'),
                           'month_name': datetime.date(current_year, month, 1).strftime('%B')})
        
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        subordinates_ids = self.env['hr.employee'].search([('parent_id.user_id','=',self.env.user.id)])
        has_group_attendance_manager = self.env.user.has_group('hr_attendance.group_hr_attendance_manager')
        if has_group_attendance_manager:
            emp_records = self.env['hr.employee'].search([('active','=',True)])
            for rec in emp_records:
                currentUserAndSubordinates.append({'id': rec.id,'name': rec.name,'emp_code': rec.emp_code})
        else:
            currentUserAndSubordinates.append({'id': employee_id.id,'name': employee_id.name,'emp_code': employee_id.emp_code})
            if subordinates_ids:
                for record in subordinates_ids:
                    currentUserAndSubordinates.append({'id': record.id,'name': record.name,'emp_code': record.emp_code})

        return [years, months, currentUserAndSubordinates, current_year, current_month]

    def get_filter_attendance_data(self, args):
        employeeSelect = args.get('employeeSelect', False)
        yearSelect = args.get('yearSelect', False)
        monthSelect = args.get('monthSelect', False)
        present_days,absent_days,leave_days,late_entry_days,worked_hours_data = [],[],[],[],[]
        check_in,check_out,color = "","",""

        current_month_year = datetime.datetime(int(yearSelect), int(monthSelect), 1).date().strftime('%B %Y')
        attendance_records = self.env['kw_daily_employee_attendance'].search([('employee_id','=',int(employeeSelect))])
        for record in attendance_records:
            if record.attendance_recorded_date.strftime("%m") == monthSelect and record.attendance_recorded_date.year == int(yearSelect):
                if record.check_in != False and record.state in ['1','7','8']:
                    present_data_list = [record.attendance_recorded_date.year, record.attendance_recorded_date.month, record.attendance_recorded_date.day, 'present']
                    present_days.append(present_data_list)

                if record.check_in == False and record.leave_status not in ['1','2','3'] and record.is_on_tour == False and record.day_status in ['0','3']:
                    absent_data_list = [record.attendance_recorded_date.year, record.attendance_recorded_date.month, record.attendance_recorded_date.day, 'absent']
                    absent_days.append(absent_data_list)

                if record.leave_status != False:
                    leave_data_list = [record.attendance_recorded_date.year, record.attendance_recorded_date.month, record.attendance_recorded_date.day, 'leave']
                    leave_days.append(leave_data_list)

                if record.check_in_status in ['2','3'] and record.day_status in ['0','3']:
                    late_entry_data_list = [record.attendance_recorded_date.year, record.attendance_recorded_date.month, record.attendance_recorded_date.day, 'late_entry']
                    late_entry_days.append(late_entry_data_list)
        
        attendance_data = self.env['kw_daily_employee_attendance'].search([('employee_id','=',int(employeeSelect))], order="attendance_recorded_date asc")
        for rec in attendance_data:
            emp_tz = rec.employee_id.tz or 'UTC' 
            emp_timezone = pytz.timezone(emp_tz)
            worked = 0
            color = '#28a745' if rec.check_in != False else '#ff9800' if rec.check_in == False and rec.leave_status not in ['1','2','3'] and rec.is_on_tour == False and rec.day_status in ['0','3']  else '#108fbb' if rec.leave_status != False else '#ffc107' if rec.check_in_status in ['2','3'] and rec.day_status in ['0','3'] else '#7f7f7f'
            if rec.attendance_recorded_date.strftime("%m") == monthSelect and rec.attendance_recorded_date.year == int(yearSelect):
                check_in = datetime.datetime.strftime(rec.check_in.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M %p") if rec.check_in else  ''
                check_out = datetime.datetime.strftime(rec.check_out.replace(tzinfo=pytz.utc).astimezone(emp_timezone), "%I:%M %p") if rec.check_out else  ''
                if rec.shift_id:
                    worked = (rec.worked_hours/(rec.shift_out_time - rec.shift_in_time - rec.shift_rest_time))*100
                worked = float("%.2f" % worked)
                worked_hours_data.append({
                    'date': rec.attendance_recorded_date,
                    'y': worked,
                    'color': color,
                    'effort': str(worked) + "%",
                    'office_In': check_in,
                    'office_Out': check_out
                    })
        emp_name = self.env['hr.employee'].search([('id','=',int(employeeSelect))]).name
        start_date = sorted(worked_hours_data, key=lambda r: r['date'])[0] if worked_hours_data else []
        attendance_start_date = start_date['date'].day if 'date' in start_date else ''
        return [present_days,absent_days,leave_days,late_entry_days,current_month_year,worked_hours_data,len(present_days),len(absent_days),len(leave_days),len(late_entry_days),emp_name,monthSelect,yearSelect, attendance_start_date]
        
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

    def get_meeting_data(self, meeting_date):
        meeting_data = []
        today_meeting_data = self.env['kw_meeting_events'].search([('kw_start_meeting_date','=',meeting_date),('state','=','confirmed')])
        for meeting in today_meeting_data:
            if self.env.user.employee_ids.id in meeting.employee_ids.ids:
                agenda = []
                internal_members = []
                duration_hours = '{0:02.0f}:{1:02.0f}'.format(*divmod(meeting.duration * 60, 60))
                duration_hour = datetime.datetime.strptime(duration_hours,"%H:%M").strftime("%HH %MM") if duration_hours else ''
                for agendas in meeting.agenda_ids:
                    agenda.append({'id': agendas.id, 'name': agendas.name})
                for im in meeting.employee_ids:
                    internal_members.append({'id': im.id,'name': im.name, 'designation': im.job_id.name, 'department': im.department_id.name}) 
            
                meeting_data.append({
                    'id': meeting.id,
                    'name': meeting.name,
                    'category' : dict(
                                self.env['kw_meeting_events'].fields_get(allfields='meeting_category')
                                ['meeting_category']['selection'])[meeting.meeting_category],
                    'start': datetime.datetime.strptime(meeting.kw_start_meeting_date.strftime("%Y-%m-%d")+ ' ' + meeting.kw_start_meeting_time, "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %I:%M %p"),
                    'duration': duration_hour,
                    'room': (meeting.meeting_room_id.name + " (" + meeting.meeting_room_id.floor_name + ")") if meeting.meeting_room_id and meeting.meeting_room_id.floor_name else 'Virtual',
                    'members': internal_members,
                    'recurrency': meeting.recurrency,
                    'total_members': len(internal_members),
                    'agenda': agenda,
                    'meeting_owner': meeting.user_id.employee_ids.id,
                    'meeting_owner_name': meeting.user_id.employee_ids.name
                })
        return meeting_data

    def today_meeting_data(self):
        current_date = datetime.datetime.now().date()
        return self.get_meeting_data(current_date)

    def tomorrow_meeting_data(self):
        nextDay_Date = datetime.datetime.today() + datetime.timedelta(days=1)
        return self.get_meeting_data(nextDay_Date)

    def get_week(self, week_date):
        one_day = datetime.timedelta(days=1)
        date = week_date 
        day_idx = (date.weekday()) % 7 
        sunday = date - datetime.timedelta(days=day_idx) 
        date = sunday
        for n in range(7):
            yield date
            date += one_day

    def week_meeting_data(self, current_date):
        meeting_data = []
        for d in self.get_week(current_date):
            week_meeting_data = self.env['kw_meeting_events'].search([('kw_start_meeting_date','=',d.date()),('state','=','confirmed')])
            for meeting in week_meeting_data:
                if self.env.user.employee_ids.id in meeting.employee_ids.ids:
                    agenda = []
                    internal_members = []
                    duration_hours = '{0:02.0f}:{1:02.0f}'.format(*divmod(meeting.duration * 60, 60))
                    duration_hour = datetime.datetime.strptime(duration_hours,"%H:%M").strftime("%HH %MM") if duration_hours else ''
                    for agendas in meeting.agenda_ids:
                        agenda.append({'id': agendas.id, 'name': agendas.name})
                    for im in meeting.employee_ids:
                        internal_members.append({'id': im.id,'name': im.name, 'designation': im.job_id.name, 'department': im.department_id.name}) 
                
                    meeting_data.append({
                        'id': meeting.id,
                        'name': meeting.name,
                        'category' : dict(
                                    self.env['kw_meeting_events'].fields_get(allfields='meeting_category')
                                    ['meeting_category']['selection'])[meeting.meeting_category],
                        'start': datetime.datetime.strptime(meeting.kw_start_meeting_date.strftime("%Y-%m-%d")+ ' ' + meeting.kw_start_meeting_time, "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y %I:%M %p"),
                        'duration': duration_hour,
                        'room': (meeting.meeting_room_id.name + " (" + meeting.meeting_room_id.floor_name + ")") if meeting.meeting_room_id and meeting.meeting_room_id.floor_name else 'Virtual',
                        'members': internal_members,
                        'recurrency': meeting.recurrency,
                        'total_members': len(internal_members),
                        'agenda': agenda,
                        'meeting_owner': meeting.user_id.employee_ids.id,
                        'meeting_owner_name': meeting.user_id.employee_ids.name
                    })
        return meeting_data
    
    def team_attendance_data(self):
        team_absent,team_leave,team_late_entry,team_late_exit,team_wfh = [],[],[],[],[]
        current_date = datetime.datetime.now().date()
        absent_attendance = self.env['kw_daily_employee_attendance'].search([('employee_id.parent_id.user_id','=',self.env.user.id),('attendance_recorded_date','=',current_date),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
        for record in absent_attendance:
            team_absent.append({
                'id': record.id,
                'attendance_date': record.attendance_recorded_date,
                'employee_id': record.employee_id.id,
                'employee_name': record.employee_id.name,
                # 'employee_image': record.employee_id.image,
                'employee_designation': record.employee_id.job_id.name,
                'employee_department': record.employee_id.department_id.name,
                'parent_id': True if record.employee_id.parent_id.user_id.id == self.env.user.id else False
            })
            
        leave_attendance = self.env['kw_daily_employee_attendance'].search([('employee_id.parent_id.user_id','=',self.env.user.id),('attendance_recorded_date','=',current_date),('leave_status','!=',False)])
        for record in leave_attendance:
            team_leave.append({
                'id': record.id,
                'employee_id': record.employee_id.id,
                'attendance_date': record.attendance_recorded_date,
                'employee_name': record.employee_id.name,
                # 'employee_image': record.employee_id.image,
                'employee_designation': record.employee_id.job_id.name,
                'employee_department': record.employee_id.department_id.name
            })

        late_entry_attendance = self.env['kw_daily_employee_attendance'].search([('employee_id.parent_id.user_id','=',self.env.user.id),('attendance_recorded_date','=',current_date),('check_in_status','in',['2','3']),('day_status','in',['0','3'])])
        for record in late_entry_attendance:
            team_late_entry.append({
                    'id': record.id,
                    'employee_id': record.employee_id.id,
                    'attendance_date': record.attendance_recorded_date,
                    'employee_name': record.employee_id.name,
                    # 'employee_image': record.employee_id.image,
                    'employee_designation': record.employee_id.job_id.name,
                    'employee_department': record.employee_id.department_id.name
                })
        
        late_exit_attendance = self.env['kw_daily_employee_attendance'].search([('employee_id.parent_id.user_id','=',self.env.user.id),('attendance_recorded_date','=',(current_date - datetime.timedelta(days=1))),('check_out_status','in',['2','3']),('day_status','in',['0','3'])])
        for record in late_exit_attendance:
            team_late_exit.append({
                'id': record.id,
                'employee_id': record.employee_id.id,
                'attendance_date': record.attendance_recorded_date,
                'employee_name': record.employee_id.name,
                # 'employee_image': record.employee_id.image,
                'employee_designation': record.employee_id.job_id.name,
                'employee_department': record.employee_id.department_id.name
            })

        wfh_attendance = self.env['kw_daily_employee_attendance'].search([('employee_id.parent_id.user_id','=',self.env.user.id),('attendance_recorded_date','=',current_date),('work_mode','=','0'),('day_status','in',['0','3'])])
        for record in wfh_attendance:
            team_wfh.append({
                'id': record.id,
                'employee_id': record.employee_id.id,
                'attendance_date': record.attendance_recorded_date,
                'employee_name': record.employee_id.name,
                # 'employee_image': record.employee_id.image,
                'employee_designation': record.employee_id.job_id.name,
                'employee_department': record.employee_id.department_id.name
            })

        time_list = self.env['kw_announcement']._get_time_list()
        return [team_absent,team_leave,team_late_entry,team_late_exit,team_wfh,time_list]

    def get_meeting_room_availability(self, meeting_date):
        meeting_data = []
        user_tz = self.env.user.tz  or 'UTC'
        local = pytz.timezone(user_tz)
        event_calendar = self.env['kw_meeting_events']
        start_datetime = meeting_date.strftime("%Y-%m-%d") + ' 00:00:00'
        end_datetime = meeting_date.strftime("%Y-%m-%d") + ' 23:45:00'

        # print(end_datetime)

        start_loop = datetime.datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        end_loop = datetime.datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")

        intial_time = start_loop
        schedule_time_set = {}

        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            date_wd_timezone = start_loop.astimezone(local)
            time_index = (datetime.datetime.strptime(date_wd_timezone.strftime("%Y-%m-%d %H:%M:%S"),
                                            "%Y-%m-%d %H:%M:%S") - intial_time).seconds / 3600.0

            schedule_time_set[time_index] = [
                {'date_wdout_timezone': start_loop, 'fdate_wdout_timezone': start_loop.strftime('%Y-%m-%d %H:%M:%S'),
                 'date_wd_timezone': date_wd_timezone.strftime("%Y-%m-%d %H:%M:%S"),
                 'time_wd_timezone': date_wd_timezone.strftime('%I:%M %p'),'room_info': {}}]

        # all_ids                 = str(id).split('-')
        calendar_events = event_calendar.sudo().search(
            [('state', '!=', 'cancelled'),('start', '>=', start_datetime),('start', '<', end_datetime)])

        # print(calendar_events)       

        for date_info in schedule_time_set:
            info_data = []
            info_data = schedule_time_set[date_info][0]
            # print(info_data)

            for event in calendar_events:
                if info_data['date_wdout_timezone'] >= event.start and (
                        info_data['date_wdout_timezone'] <= event.stop or (
                        info_data['date_wdout_timezone'] - event.stop).seconds == 1):

                    # info_data['room_id'] = event.meeting_room_id.id
                    # info_data['event_id'] = event.id
                    info_data['name'] = event.name
                    if not event.meeting_room_id.id in info_data['room_info']:
                        info_data['room_info'][event.meeting_room_id.id] = {}

                    info_data['room_info'][event.meeting_room_id.id]['event_id'] = event.id
                    info_data['room_info'][event.meeting_room_id.id]['name'] = event.name

                    employee_ext = self.env['hr.employee'].search([('user_id', '=', event.user_id.id)],
                                                                     limit=1).epbx_no
                    info_data['room_info'][event.meeting_room_id.id][
                        'event_details'] = event.name + """<br/> By: """ + event.user_id.name + """<br/> Extn: """ + str(
                        employee_ext)
                    info_data['room_info'][event.meeting_room_id.id]['display_time'] = event.display_time
                    info_data['room_info'][event.meeting_room_id.id]['my_meeting'] = 1 if self.env.user.employee_ids in event.employee_ids else 0 
        
        final_schedule_time = []
        for i in sorted(schedule_time_set):
            if 8 <= i <= 22:
                final_schedule_time.append(schedule_time_set[i][0])

        m_rooms,meeting_rooms = [],[]
        has_group_meeting_manager = self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager')
        if not has_group_meeting_manager:
            meeting_rooms = self.env['kw_meeting_room_master'].sudo().search([('restricted_access','=',False)])
        else: 
            meeting_rooms = self.env['kw_meeting_room_master'].sudo().search([])
        for rooms in meeting_rooms:
            m_rooms.append({'id': rooms.id, 'name': rooms.name})

        meeting_data.append({'event_data': final_schedule_time, 'meeting_room': m_rooms})
        return meeting_data

    def today_meeting_room_availability(self):
        today = datetime.datetime.today()
        return self.get_meeting_room_availability(today)
            
    def tomorrow_meeting_room_availability(self):
        meeting_date = datetime.datetime.today() + datetime.timedelta(days=1)
        return self.get_meeting_room_availability(meeting_date)
    
    def get_meeting_on_date_select(self, args):
        meetingdateselect = args.get('meetingDateSelect', False)
        meeting_date = datetime.datetime.strptime(meetingdateselect, "%Y-%m-%d")
        return self.get_meeting_room_availability(meeting_date)
    
    def get_user_gridstack_config_details(self,dashboard_id):
        user_gridstack = self.env['kw_user_portlets_gridstack_config'].search([('employee_id','=',self.env.user.employee_ids.id),('ks_dashboard_ninja_board_id','=',dashboard_id)],limit=1)
        if user_gridstack:
            return user_gridstack.ks_gridstack_config
    
    def get_holiday_calendar_data(self,args):
        formatted_calendar_data_list = []
        args_branch_id, args_shift_id = args.get('branch_id', False), args.get('shift_id',False)
        employee_id = self.env.user.employee_ids 
        if args:
            calendar_data = self.env['resource.calendar.leaves'].get_calendar_global_leaves(args_branch_id,args_shift_id,0,None)
        else:
            branch_id = self.env.user.employee_ids.resource_calendar_id.branch_id.id 
            personal_calendar = 1
            shift_id = self.env.user.employee_ids.resource_calendar_id.id
            calendar_data = self.env['resource.calendar.leaves'].get_calendar_global_leaves(branch_id,shift_id,personal_calendar,employee_id[0].id)
        for data in calendar_data['holiday_calendar']:
            data_list = [data['date_from'].year, data['date_from'].month, data['date_from'].day, data['name'], data['prime_color'], data['overlap_public_holiday']]
            formatted_calendar_data_list.append(data_list)
    
        return formatted_calendar_data_list

    def local_visits(self):
        local_visit_list = []
        model = self.env['kw_lv_apply'].sudo()
        lvs = model.search([('visit_date','=',datetime.datetime.now().date()),('status','!=',False)])
        for lv in lvs:
            local_visit_list.append({
                'id': lv.id,
                'visit_category': lv.visit_category.category_name,
                'location': lv.location,
                'employee_id': lv.emp_name.id,
                'employee_name': lv.emp_name.name,
                # 'employee_image': lv.emp_name.image, 
                'employee_designation': lv.emp_name.job_id.name, 
                'employee_department': lv.emp_name.department_id.name, 
                'out_time': (dict(model.fields_get(allfields='out_time')['out_time']['selection'])[lv.out_time]), 
                'expected_in_time': (dict(model.fields_get(allfields='expected_in_time')['expected_in_time']['selection'])[lv.expected_in_time]) if lv.expected_in_time else '--', 
                'actual_in_time': (dict(model.fields_get(allfields='actual_in_time')['actual_in_time']['selection'])[lv.actual_in_time]) if lv.actual_in_time else '--'
                })
        return local_visit_list    

    def get_announcement_data(self):
        announcement_datas = []
        announcements = self.env['kw_announcement'].sudo().search([('start_date','<=', datetime.date.today()),('expire_date','>=', datetime.date.today()),('state','=','published'),('active','=',True)], order="id desc")
        for announcement in announcements:
            emp_attendance = self.env['kw_daily_employee_attendance'].search([('employee_id','=',announcement.employee_id.id),('attendance_recorded_date','=',datetime.date.today()),('check_in','!=',False)],limit=1)
            if announcement.start_date == datetime.date.today() and announcement.category_id.alias == 'late_entry' and emp_attendance:
                announcement.update({'active': False})
            announcement_datas.append({
                'id': announcement.id,
                'category_id' : announcement.category_id.name,
                'category_alias' : announcement.category_id.alias,
                'headline' : announcement.headline,
                'start_date' :  datetime.datetime.strftime(announcement.start_date, "%d-%b-%Y"),
                'state' : announcement.state,
                'employee_id' : announcement.employee_id.name,
                'coming_to_office' : announcement.coming_to_office, 
                'office_time': announcement.office_time, 
                'description': announcement.description,
                'create_uid': announcement.user_id.name
            })
        return announcement_datas

    def get_tour_data(self):
        current_date = datetime.date.today()
        tour_list = []
        tour_ids = self.env['kw_tour'].sudo().search([('state','in',['Approved','Traveldesk Approved','Finance Approved']),('public_view','=',True),('date_travel','<=',datetime.date.today()),('date_return','>=',datetime.date.today())])
        for tour in tour_ids:
            cities = []
            city_list = []
            for index,data in enumerate(tour.tour_detail_ids):
                if index == 0:
                    cities.append({
                        'id': data.from_city_id.id, 
                        'name': data.from_city_id.name,
                        'y': 1, 
                        'color': '#28a745' if current_date >= data.from_date else '#198fbb', 
                        'marker' : {'radius': 12} if current_date >= data.from_date else {'radius': 6},
                        'date': data.from_date.strftime("%d-%b-%Y")
                    })
                    city_list.append(data.from_city_id.name)
                    cities.append({
                        'id': data.to_city_id.id, 
                        'name': data.to_city_id.name, 
                        'y': 1, 
                        'color': '#28a745' if current_date >= data.to_date else '#198fbb' , 
                        'marker' : {'radius': 12} if current_date >= data.to_date else {'radius': 6},
                        'date': data.to_date.strftime("%d-%b-%Y")
                    })
                    city_list.append(data.to_city_id.name)
                else:
                    cities.append({
                    'id': data.to_city_id.id, 
                    'name': data.to_city_id.name, 
                    'y': 1, 
                    'color': '#28a745' if current_date >= data.to_date else '#198fbb' , 
                    'marker' : {'radius': 12} if current_date >= data.to_date else {'radius': 6},
                    'date': data.to_date.strftime("%d-%b-%Y"),
                    })
                    city_list.append(data.to_city_id.name)

            tour_list.append({
                'id': "tour_details_" + str(tour.id),
                'employee_id': tour.employee_id.id,
                # 'employee_image': tour.employee_id.image, 
                'employee': tour.employee_id.name,
                'designation': tour.employee_id.job_id.name,    
                'department': tour.employee_id.department_id.name,
                'tour_details':city_list,
                'cities': cities,
                'public_view': tour.public_view
            })
        return tour_list

    def get_leave_and_absent_data(self):
        leave_list,absent_list,from_day,to_day,leave_user,announcement_user = [],[],'','',[],[]
        has_group_ks_dashboard_manager = self.env.user.has_group('ks_dashboard_ninja.ks_dashboard_ninja_group_manager')
        leave_data = self.env['hr.leave'].sudo().search([('state','=','validate'),('employee_id.job_branch_id','=',self.env.user.branch_id.id),('date_from','<=',datetime.datetime.today().date()),('date_to','>=',datetime.datetime.today().date())])
        for leave in leave_data:
            if leave.request_unit_half :
                if leave.request_date_from_period == 'am':
                    from_day = "Morning"
                if leave.request_date_from_period == 'pm':
                    from_day = "Afternoon"
            else:
                from_day = ''

            if leave.request_unit_half_to_period:
                if leave.request_date_to_period == 'am':
                    to_day = "Morning"
                if leave.request_date_to_period == 'pm':
                    to_day = "Afternoon"
            else :
                to_day = ''

            leave_list.append({
                'id': leave.id,
                'holiday_status': leave.holiday_status_id.display_name,
                'employee_id': leave.employee_id.name,
                'department_id': leave.employee_id.department_id.name,
                'number_of_days': leave.number_of_days,
                'date_from': datetime.datetime.strftime(leave.date_from, "%d-%b-%Y"),
                'date_to': datetime.datetime.strftime(leave.date_to, "%d-%b-%Y"),
                'leave_tooltip': 'Leave From: '+ datetime.datetime.strftime(leave.date_from, "%d-%b-%Y") + (' (' + from_day + ')' if from_day else '') + '<br/> Leave To: ' + datetime.datetime.strftime(leave.date_to, "%d-%b-%Y") + (' (' + to_day + ')' if to_day else '')
            })
        absent_data = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today()),('employee_id.job_branch_id','=',self.env.user.branch_id.id),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status', 'in',['0','3'])])
        absent_data = absent_data.sorted(key = lambda r: r.employee_id.name)
        for absent in absent_data:
            leave_user = self.env['hr.leave'].sudo().search([('state','not in',['validate','refuse','cancel']),('employee_id','=',absent.employee_id.id),('date_from','<=',datetime.datetime.today().date()),('date_to','>=',datetime.datetime.today().date())])
            announcement_user = self.env['kw_announcement'].search([('employee_id','=',absent.employee_id.id),('start_date','=',datetime.date.today())])
        
            absent_list.append({
                'id': absent.id,
                'employee_id': absent.employee_id.id,
                'employee_name': absent.employee_id.name,
                'status': 'informed' if leave_user else 'announcement' if announcement_user else 'not-informed',
                'announcement_headline': announcement_user.headline if announcement_user else False,
                'parent_id': has_group_ks_dashboard_manager,
            })
        time_list = self.env['kw_announcement']._get_time_list()
        return [leave_list, absent_list, time_list]

    @api.model
    def create_absent_announcement(self,**args):
        employee_id = args.get('employee_id',False)
        status = args.get('status', False)
        time = args.get('time',False)

        announcement = self.env['kw_announcement']
        announcement_category_id = self.env['kw_announcement_category'].search([('alias','=','late_entry')])
        employee = self.env['hr.employee'].browse(int(employee_id))
        current_announcement_id = announcement.search([('category_id.alias','=','late_entry'),('employee_id','=',int(employee_id)),('start_date','=',datetime.date.today())])
        # print(current_announcement_id)
        if current_announcement_id:
            current_announcement_id.write({
                'headline': (employee.name + " will come to office by " + datetime.datetime.strptime(time,"%H:%M:%S").strftime("%I:%M %p")) if status == 'yes' else (employee.name + " will not come to office today." ),
                'coming_to_office': status,
                'user_id': self.env.user.id,
                'office_time': time if status == 'yes' else False,
            })
        else:
            announcement.sudo().create({
                'category_id': announcement_category_id.id,
                'headline': (employee.name + " will come to office by " + time) if status == 'yes' else (employee.name + " will not come to office today." ),
                'start_date': datetime.date.today(),
                'expire_date': datetime.date.today(),
                'state': 'published',
                'user_id': self.env.user.id,
                'coming_to_office': status,
                'employee_id': int(employee_id),
                'office_time': time if status == 'yes' else False,
            })
    
    def best_wishes(self):
        birthday_greetings_ids = self.env['hr_employee_greetings'].search_count([('send_wish_status','=','1'),('greeting_type','=','birth_day')])
        year_of_service_greetings_ids = self.env['hr_employee_greetings'].search_count([('send_wish_status','=','1'),('greeting_type','=','year_of_service')])
        well_wishes_greetings_ids = self.env['hr_employee_greetings'].search_count([('send_wish_status','=','1'),('greeting_type','=','well_wish')])
        anniversary_greetings_ids = self.env['hr_employee_greetings'].search_count([('send_wish_status','=','1'),('greeting_type','=','anniversary')])
        return [birthday_greetings_ids,year_of_service_greetings_ids,well_wishes_greetings_ids,anniversary_greetings_ids]

    def get_attendance_count(self):
        time_list = self.env['kw_meeting_events']._get_time_list()
        times, attendance_count_list = [],[]
        for time in time_list:
            attendance_time = datetime.datetime.strptime((datetime.date.today().strftime("%Y-%m-%d ") + time[0]),"%Y-%m-%d %H:%M:%S")
            times.append(attendance_time)
            prev_attendance_time = attendance_time - datetime.timedelta(minutes=15)
            user_tz = pytz.timezone(self.env.user.tz  or 'UTC')
            attendance_ids = self.env['kw_daily_employee_attendance'].sudo().search([('attendance_recorded_date','=',datetime.date.today())])
            attendance_count = attendance_ids.filtered(lambda r: r.check_in.astimezone(user_tz).replace(tzinfo=None) >= prev_attendance_time and r.check_in.astimezone(user_tz).replace(tzinfo=None) <= attendance_time if r.check_in else '')
            attendance_count_list.append({'y': len(attendance_count),'color': '#28a745', 'count': len(attendance_count), 'time': time[1]})
        
        return [times, attendance_count_list]

    def remove_announcement_data(self):
        remove_announcement = False
        announcement_ids = self.env['kw_announcement'].search([('start_date','=',datetime.date.today()),('category_id.alias','=','late_entry')])
        for announcement in announcement_ids:
            attendance_data = self.env['kw_daily_employee_attendance'].search([('employee_id','=',announcement.employee_id.id),('check_in','!=',False),('attendance_recorded_date','=',datetime.date.today())],limit=1)
            if attendance_data:
                remove_announcement = True 
        return remove_announcement

    def get_kw_appraisal_data(self, args):
        appraisal_user = self.env.user.has_group('kw_appraisal.group_appraisal_employee')
        appraisal_manager = self.env.user.has_group('kw_appraisal.group_appraisal_manager')
        appraisal_year_id = args.get('appraisal_year_id', False)
        user_id = args.get('user_id', False)
        period_master_list, appraisal_period_id,appraisal_score,kra_score,total_score,appraisal_record,current_period,no_appraisal = [],'','','','' ,[],[],False
        # print(args)
        if appraisal_manager == True or appraisal_user == True:
            appraisal_ids = self.env['hr.appraisal'].search([('emp_id.user_id','=',self.env.user.id),('state','=',6)], order="id desc")
            for appraisal_period in appraisal_ids:
                period_master_list.append({'period_id':appraisal_period.appraisal_year_rel.id, 'period_name': appraisal_period.appraisal_year_rel.assessment_period})
            
            period_master = self.env['kw_assessment_period_master'].search([],order='id desc')
            if appraisal_year_id:
                current_period = self.env['kw_assessment_period_master'].search([('id','=',int(appraisal_year_id))])

            if args and appraisal_year_id and user_id:
                appraisal_record = self.env['hr.appraisal'].search([('appraisal_year_rel','=',int(appraisal_year_id)),('emp_id.user_id','=',int(user_id))], limit=1)
            else:
                appraisal_record = self.env['hr.appraisal'].search([('appraisal_year_rel','=',period_master[0].id or False),('emp_id','=',self.env.user.employee_ids.id)], limit=1)

            # print(appraisal_record)
            if appraisal_record:
                if appraisal_record.state.sequence == 6:
                    appraisal_period_id = appraisal_record.appraisal_year_rel.id if appraisal_record.appraisal_year_rel else current_period.id
                    appraisal_score = float("%.2f" % appraisal_record.score)  if appraisal_record.score else '0.00'
                    kra_score = float("%.2f" % appraisal_record.kra_score)  if appraisal_record.kra_score else '0.00'
                    total_score = float("%.2f" % appraisal_record.total_score)  if appraisal_record.total_score else '0.00'
                else:
                    appraisal_record = self.env['hr.appraisal'].search([('appraisal_year_rel','=',period_master[1].id or False),('emp_id','=',self.env.user.employee_ids.id),('state','=',6)], limit=1)
                    if appraisal_record:
                        appraisal_period_id = appraisal_record.appraisal_year_rel.id if appraisal_record.appraisal_year_rel else current_period.id
                        appraisal_score = float("%.2f" % appraisal_record.score)  if appraisal_record.score else '0.00'
                        kra_score = float("%.2f" % appraisal_record.kra_score)  if appraisal_record.kra_score else '0.00'
                        total_score = float("%.2f" % appraisal_record.total_score)  if appraisal_record.total_score else '0.00'
                    else:
                        appraisal_period_id = 0
                        no_appraisal = True
                        appraisal_score = '0.00'
                        kra_score = '0.00'
                        total_score = '0.00'
            else:
                appraisal_period_id = 0
                no_appraisal = True
                appraisal_score = '0.00'
                kra_score = '0.00'
                total_score = '0.00'


        return [appraisal_period_id,appraisal_score,kra_score,total_score, period_master_list,no_appraisal,appraisal_manager,appraisal_user]

    def check_dashboard_exisiting_user(self, dashboard_id):
        dashboard_portlet_ids = self.env['ks_dashboard_ninja.item'].sudo().search([('common_portlet','=',True),('is_published','=',True),('ks_dashboard_ninja_board_id','=',dashboard_id)]).ids
        existing_user = self.env['kw_user_portlets'].sudo().search([('employee_id.user_id','=',self.env.user.id),('ks_dashboard_ninja_board_id','=',dashboard_id)])
        if not existing_user:
            self.env['kw_user_portlets'].create({
                'employee_id': self.env.user.employee_ids.id,
                'ks_dashboard_ninja_board_id': dashboard_id,
                'ks_dashboard_items_id':  [(6, 0, dashboard_portlet_ids)]
            })

    def random_color(self):
        # random_number = random.randint(0,16777215)
        random_number = secrets.randint(0,16777215)
        hex_number = str(hex(random_number))
        hex_number ='#'+ hex_number[2:]
        return hex_number

    def get_self_timesheet(self, args):
        timesheet_month = args.get('timesheet_month',False)
        timesheet_year = args.get('timesheet_year',False)
        current_month_year = ''
        timesheet_efforts,required_effort,current_week_timesheet_effort,current_week_required_effort,last_week_timesheet_effort,last_week_required_effort,effort_variations_list,current_month_timesheet_effort = [],[],[],[],[],[],[],[]
        if args:
            current_month_year = datetime.date(int(timesheet_year), int(timesheet_month), 1).strftime('%B %Y')
            current_month,current_year = int(timesheet_month), int(timesheet_year)
        else:
            current_month_year = datetime.datetime.today().strftime("%b %Y")
            current_month,current_year = datetime.datetime.today().month, datetime.datetime.today().year


        current_date, last_week_date = datetime.datetime.today(), datetime.datetime.today() - datetime.timedelta(days=7)
        start_date,end_date = self.env['kw_late_attendance_summary_report']._get_month_range(current_year,current_month)
        
        timesheet_effort_ids = self.env['account.analytic.line'].search([('employee_id','=',self.env.user.employee_ids.id),('date','>=',start_date),('date','<=',end_date)])
        total_no_activities = len(timesheet_effort_ids.mapped('unit_amount'))
        total_timesheet_effort = float("%.2f" % sum(timesheet_effort_ids.mapped('unit_amount')))
        str_total_timesheet_effort = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(timesheet_effort_ids.mapped('unit_amount')) * 60, 60))

        present_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','>=',start_date),('attendance_recorded_date','<=',end_date),('check_in','!=',False),('day_status','in',['0','3']),('leave_status','not in',['1','2','3'])])
        absent_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','>=',start_date),('attendance_recorded_date','<=',end_date),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
        leave_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','>=',start_date),('attendance_recorded_date','<=',end_date),('leave_day_value','=',0.5)])
        
        for present in present_attendance_ids:
            required_effort.append(present.shift_out_time - present.shift_in_time - present.shift_rest_time )
        for absent in absent_attendance_ids:
            required_effort.append(absent.shift_out_time - absent.shift_in_time - absent.shift_rest_time )
        for leave in leave_attendance_ids:
            required_effort.append((leave.shift_out_time - leave.shift_in_time - leave.shift_rest_time) * 0.5)
        str_total_required_effort = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(required_effort) * 60, 60))

        num_days = calendar.monthrange(current_year,current_month)[1]
        current_month_days = [datetime.date(current_year,current_month, day)  for day in range(1, num_days+1)]
        for day in current_month_days:
            timesheet_ids = self.env['account.analytic.line'].search([('employee_id','=',self.env.user.employee_ids.id),('date','=',day)])
            attendance_day_status = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',day)]).day_status
            current_month_timesheet_effort.append({
                'day': 'Date: ' + day.strftime('%d-%b-%Y') + '<br/> Effort: ' + '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(timesheet_ids.mapped('unit_amount')) * 60, 60)) + " Hrs", #str(float("%.2f" % sum(timesheet_ids.mapped('unit_amount')))) + " Hrs",
                'timesheet': 1 if timesheet_ids and (attendance_day_status in ['0','3'] or attendance_day_status in ['2','4','5']) else -1 if day > current_date.date() else 2 if not timesheet_ids and attendance_day_status in ['2','4','5'] else 0
            })

        #last week timesheet report
        for d in self.get_week(last_week_date):
            timesheet_ids = self.env['account.analytic.line'].search([('employee_id','=',self.env.user.employee_ids.id),('date','=',d.date())])
            for t in timesheet_ids:
                last_week_timesheet_effort.append(t.unit_amount)
            
            last_week_present_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',d.date()),('check_in','!=',False),('day_status','in',['0','3']),('leave_status','not in',['1','2','3'])])
            last_week_absent_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',d.date()),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
            last_week_leave_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',d.date()),('leave_day_value','=',0.5)])

            for present in last_week_present_attendance_ids:
                last_week_required_effort.append(present.shift_out_time - present.shift_in_time - present.shift_rest_time )
            for absent in last_week_absent_attendance_ids:
                last_week_required_effort.append(absent.shift_out_time - absent.shift_in_time - absent.shift_rest_time )
            for leave in last_week_leave_attendance_ids:
                last_week_required_effort.append((leave.shift_out_time - leave.shift_in_time - leave.shift_rest_time) * 0.5)

        #current week timesheet report
        for d in self.get_week(current_date):
            timesheet_ids = self.env['account.analytic.line'].search([('employee_id','=',self.env.user.employee_ids.id),('date','=',d.date())])
            for t in timesheet_ids:
                current_week_timesheet_effort.append(t.unit_amount)
            
            current_week_present_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',d.date()),('check_in','!=',False),('day_status','in',['0','3']),('leave_status','not in',['1','2','3'])])
            current_week_absent_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',d.date()),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
            current_week_leave_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',self.env.user.employee_ids.id),('attendance_recorded_date','=',d.date()),('leave_day_value','=',0.5)])

            for present in current_week_present_attendance_ids:
                current_week_required_effort.append(present.shift_out_time - present.shift_in_time - present.shift_rest_time )
            for absent in current_week_absent_attendance_ids:
                current_week_required_effort.append(absent.shift_out_time - absent.shift_in_time - absent.shift_rest_time )
            for leave in current_week_leave_attendance_ids:
                current_week_required_effort.append((leave.shift_out_time - leave.shift_in_time - leave.shift_rest_time) * 0.5)

        total_current_week_timesheet = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(current_week_timesheet_effort) * 60, 60)) 
        total_current_week_required_Effort = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(current_week_required_effort) * 60, 60)) 
        total_last_week_timesheet = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(last_week_timesheet_effort) * 60, 60)) 
        total_last_week_requires_effort = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(last_week_required_effort) * 60, 60))

        #effort variation progress bar
        color_list = ['#28a745','#198fbb','#ff9800','#3572A5','#f1e05a','#563d7c','#b07219','#f6546a','#00ced1','#468499','#ff6666','#ffd700','#ff7373','#008080','#00ff00','#800000','#800080','#ff7f50','#003366','#0ff1ce','#f7347a']
        c = 0
        category_timesheet_efforts = self.env['account.analytic.line'].search([('employee_id','=',self.env.user.employee_ids.id),('date','>=',start_date),('date','<=',end_date)]).mapped('prject_category_id')
        for tc in category_timesheet_efforts:
            timesheet_efforts = self.env['account.analytic.line'].search([('employee_id','=',self.env.user.employee_ids.id),('date','>=',start_date),('date','<=',end_date),('prject_category_id','=',tc.id)]).mapped('unit_amount')
            total_timesheet_category_effort = (sum(timesheet_efforts)/total_timesheet_effort) * 100
            effort_variations_list.append({
                'name': tc.name,
                'effort': float("%.2f" % total_timesheet_category_effort),
                'color': color_list[c] 
            })
            c += 1

            if c == len(color_list):
                c=0
        sorted_effort_variations_list = sorted(effort_variations_list, key = lambda r: r['effort'], reverse=True) if effort_variations_list else []
        return [current_month_year, str_total_timesheet_effort, str_total_required_effort, total_no_activities, total_current_week_timesheet,total_current_week_required_Effort,total_last_week_timesheet,total_last_week_requires_effort,current_month_timesheet_effort,sorted_effort_variations_list]

    def get_sub_ordinates_timesheet(self):
        sub_ordinates_timesheet_data_list = []
        current_month_year = datetime.datetime.today().strftime("%b %Y")
        current_date, last_week_date = datetime.datetime.today(), datetime.datetime.today() - datetime.timedelta(days=7)
        current_month,current_year = datetime.datetime.today().month, datetime.datetime.today().year
        start_date,end_date = self.env['kw_late_attendance_summary_report']._get_month_range(current_year,current_month)
        sub_ordinate_ids = self.env['hr.employee'].search([('parent_id','=',self.env.user.employee_ids.id),('enable_timesheet','=',True)])

        for sub in sub_ordinate_ids:
            last_week_timesheet_effort,last_week_validated,last_week_required_effort,current_week_timesheet_effort,current_week_required_effort= [],[],[],[],[]
            last_week_status,total_last_week_effort_percentage,current_week_status,total_current_week_effort_percentage = 1,'',1,''
            timesheet_effort_ids = self.env['account.analytic.line'].search([('employee_id','=',sub.id),('date','>=',start_date),('date','<=',end_date)])
            total_timesheet_effort = float("%.2f" % sum(timesheet_effort_ids.mapped('unit_amount')))  
            str_total_required_effort = '{0:02.0f}:{1:02.0f}'.format(*divmod(sum(timesheet_effort_ids.mapped('unit_amount')) * 60, 60)) 

            for d in self.get_week(last_week_date):
                timesheet_ids = self.env['account.analytic.line'].search([('employee_id','=',sub.id),('date','=',d.date())])
                for t in timesheet_ids:
                    last_week_validated.append(t.validated)
                    last_week_timesheet_effort.append(t.unit_amount)

                last_week_present_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',sub.id),('attendance_recorded_date','=',d.date()),('check_in','!=',False),('day_status','in',['0','3']),('leave_status','not in',['1','2','3'])])
                last_week_absent_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',sub.id),('attendance_recorded_date','=',d.date()),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
                last_week_leave_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',sub.id),('attendance_recorded_date','=',d.date()),('leave_day_value','=',0.5)])
                for present in last_week_present_attendance_ids:
                    last_week_required_effort.append(present.shift_out_time - present.shift_in_time - present.shift_rest_time )
                for absent in last_week_absent_attendance_ids:
                    last_week_required_effort.append(absent.shift_out_time - absent.shift_in_time - absent.shift_rest_time )
                for leave in last_week_leave_attendance_ids:
                    last_week_required_effort.append((leave.shift_out_time - leave.shift_in_time - leave.shift_rest_time ) * 0.5)

            for d in self.get_week(current_date):
                timesheet_ids = self.env['account.analytic.line'].search([('employee_id','=',sub.id),('date','=',d.date())])
                for t in timesheet_ids:
                    current_week_timesheet_effort.append(t.unit_amount)
                
                current_week_present_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',sub.id),('attendance_recorded_date','=',d.date()),('check_in','!=',False),('day_status','in',['0','3']),('leave_status','not in',['1','2','3'])])
                current_week_absent_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',sub.id),('attendance_recorded_date','=',d.date()),('check_in','=',False),('leave_status','not in',['1','2','3']),('is_on_tour','=',False),('day_status','in',['0','3'])])
                current_week_leave_attendance_ids = self.env['kw_daily_employee_attendance'].search([('employee_id','=',sub.id),('attendance_recorded_date','=',d.date()),('leave_day_value','=',0.5)])
                for present in current_week_present_attendance_ids:
                    current_week_required_effort.append(present.shift_out_time - present.shift_in_time - present.shift_rest_time )
                for absent in current_week_absent_attendance_ids:
                    current_week_required_effort.append(absent.shift_out_time - absent.shift_in_time - absent.shift_rest_time )
                for leave in current_week_leave_attendance_ids:
                    current_week_required_effort.append((leave.shift_out_time - leave.shift_in_time - leave.shift_rest_time ) * 0.5)

            total_last_week_required_effort = sum(last_week_required_effort)
            if total_last_week_required_effort == 0:
                total_last_week_effort_percentage = '0.0'
                last_week_status = 1
            else:
                last_week_effort_percentage = float("%.2f" % ((sum(last_week_timesheet_effort) / sum(last_week_required_effort)) * 100))
                total_last_week_effort_percentage = str(last_week_effort_percentage)
                last_week_status = 1 if last_week_effort_percentage < 90 else 0

            total_current_week_required_effort = sum(current_week_required_effort)
            if total_current_week_required_effort == 0:
                total_current_week_effort_percentage = '0.0'
                current_week_status = 1
            else:
                current_week_effort_percentage = float("%.2f" % ((sum(current_week_timesheet_effort) / sum(current_week_required_effort)) * 100))
                total_current_week_effort_percentage = str(current_week_effort_percentage)
                current_week_status = 1 if current_week_effort_percentage < 90 else 0
            
            sub_ordinates_timesheet_data_list.append({
                'employee': sub.name,
                'effort_given': total_timesheet_effort,
                'effort_given_percentage': str_total_required_effort,
                'last_week_effort_percentage': total_last_week_effort_percentage,
                'last_week_status': last_week_status,
                'current_week_effort_percentage': total_current_week_effort_percentage,
                'current_week_status': current_week_status,
                'validated': 1 if len(last_week_validated) != 0 and 0 not in last_week_validated else 0
            })

        return [current_month_year,sub_ordinates_timesheet_data_list]

    def get_canteen_meal_beverage_data(self):
        today_baverage_list,weekly_baverage_list,monthly_baverage_list = [],[],[]
        today_meal_list,weekly_meal_list,monthly_meal_list,today_meal_menu = [],[],[],''
        current_date = datetime.date.today()
        current_month = datetime.datetime.now().date().month
        current_year = datetime.datetime.now().date().year
        today_beverage_price,weekly_beverage_price,monthly_beverage_price = 0.0,0.0,0.0
        today_meal_price,weekly_meal_price,monthly_meal_price = 0.0,0.0,0.0

        ## Today Beverage And Meal Data
        today_beverage_ids = self.env['baverage_bio_log'].search([('employee_id','=',self.env.user.employee_ids.id),('recorded_date','>=',datetime.datetime.today().date()),('recorded_date','<=',datetime.datetime.today().date())])
        beverage_type_ids = today_beverage_ids.mapped('beverage_type_id')
        for beverage in beverage_type_ids:
            today_data = today_beverage_ids.filtered(lambda x: x.beverage_type_id == beverage)
            today_beverage_price = sum(today_data.mapped(lambda x: x.total_price))
            beverage_count = len(today_data)
            today_baverage_list.append({'id':beverage.id,'name': beverage.beverage_type,'units' : beverage_count,'price': float("%.2f" % today_beverage_price) })

        today_meal_ids = self.env['meal_bio_log'].search([('employee_id','=',self.env.user.employee_ids.id),('recorded_date','=',datetime.datetime.today().date())])
        meal_type_ids = today_meal_ids.mapped('meal_type_id')
        for meal in meal_type_ids:
            today_meal_data = today_meal_ids.filtered(lambda x: x.meal_type_id == meal)
            today_meal_price = sum(today_meal_data.mapped(lambda x: x.total_price))
            meal_count = len(today_meal_data)
            today_meal_list.append({'id':meal.id,'name': meal.meal_type,'units' : meal_count,'price': float("%.2f" % today_meal_price) })
        

        ## Weekly Beverage And Meal Data
        weekly_beverage_model_ids = self.env['baverage_bio_log']
        weekly_meal_model_ids = self.env['meal_bio_log']
        for d in self.get_week(current_date):
            weekly_beverage_model_ids += self.env['baverage_bio_log'].search([('employee_id','=',self.env.user.employee_ids.id),('recorded_date','>=',d),('recorded_date','<=',d)])
            weekly_meal_model_ids += self.env['meal_bio_log'].search([('employee_id','=',self.env.user.employee_ids.id),('recorded_date','=',d)])
            
        weekly_beverage_type_ids = weekly_beverage_model_ids.mapped('beverage_type_id')
        for w_beverage in weekly_beverage_type_ids:
            weekly_data = weekly_beverage_model_ids.filtered(lambda x: x.beverage_type_id == w_beverage)
            weekly_beverage_price = sum(weekly_data.mapped(lambda x: x.total_price))
            weekly_beverage_count = len(weekly_data)
            weekly_baverage_list.append({'id':w_beverage.id,'name': w_beverage.beverage_type,'units' : weekly_beverage_count,'price': float("%.2f" % weekly_beverage_price) })

        weekly_meal_type_ids = weekly_meal_model_ids.mapped('meal_type_id')
        for w_meal in weekly_meal_type_ids:
            weekly_meal_data = weekly_meal_model_ids.filtered(lambda x: x.meal_type_id == w_meal)
            weekly_meal_price = sum(weekly_meal_data.mapped(lambda x: x.total_price))
            weekly_meal_count = len(weekly_meal_data)
            weekly_meal_list.append({'id':w_meal.id,'name': w_meal.meal_type,'units' : weekly_meal_count,'price': float("%.2f" % weekly_meal_price) })

        ## Monthly Beverage And Meal Data
        if current_date.day >=25:
            start_date = datetime.date(current_year,current_month, 26) 
            end_date = datetime.date(current_year,current_month, 25) + relativedelta(months=1)
        else: 
            start_date = datetime.date(current_year,current_month, 26) - relativedelta(months=1)
            end_date = datetime.date(current_year,current_month, 25)
        delta = end_date - start_date   # returns timedelta
        monthly_beverage_model_ids = self.env['baverage_bio_log']
        monthly_meal_model_ids = self.env['meal_bio_log']
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            monthly_beverage_model_ids += self.env['baverage_bio_log'].search([('employee_id','=',self.env.user.employee_ids.id),('recorded_date','>=',day),('recorded_date','<=',day)])
            monthly_meal_model_ids += self.env['meal_bio_log'].search([('employee_id','=',self.env.user.employee_ids.id),('recorded_date','=',day)])

        monthly_beverage_type_ids = monthly_beverage_model_ids.mapped('beverage_type_id')
        for m_beverage in monthly_beverage_type_ids:
            monthly_data = monthly_beverage_model_ids.filtered(lambda x: x.beverage_type_id == m_beverage)
            monthly_beverage_price = sum(monthly_data.mapped(lambda x: x.total_price))
            monthly_beverage_count = len(monthly_data)
            monthly_baverage_list.append({'id':m_beverage.id,'name': m_beverage.beverage_type,'units' : monthly_beverage_count,'price': float("%.2f" % monthly_beverage_price)  })
        
        monthly_meal_type_ids = monthly_meal_model_ids.mapped('meal_type_id')
        for m_meal in monthly_meal_type_ids:
            monthly_meal_data = monthly_meal_model_ids.filtered(lambda x: x.meal_type_id == m_meal)
            monthly_meal_price = sum(monthly_meal_data.mapped(lambda x: x.total_price))
            monthly_meal_count = len(monthly_meal_data)
            monthly_meal_list.append({'id':m_meal.id,'name': m_meal.meal_type,'units' : monthly_meal_count,'price': float("%.2f" % monthly_meal_price) })
        
        today_meal_menu_id = self.env['weekly_meal_configuration'].sudo().search([(['weekdays','=',str(current_date.weekday() + 1)])],limit=1)
        today_meal_menu_items = today_meal_menu_id.items if today_meal_menu_id else ''
        if len(today_meal_menu_items) > 0:
            menu_items = today_meal_menu_items.split(',')
            for menu in menu_items:
                today_meal_menu += menu + """<br/>"""
        return [today_baverage_list,weekly_baverage_list,monthly_baverage_list,today_meal_list,weekly_meal_list,monthly_meal_list,today_meal_menu]

    @api.model
    def get_canteen_meal_beverage_all_data(self, **kwargs):
        today_baverage_list,weekly_baverage_list,monthly_baverage_list = [],[],[]
        today_meal_list,weekly_meal_list,monthly_meal_list = [],[],[]
        current_date = datetime.date.today()
        current_month = datetime.datetime.now().date().month
        current_year = datetime.datetime.now().date().year
        today_beverage_price,weekly_beverage_price,monthly_beverage_price = 0.0,0.0,0.0
        today_meal_price,weekly_meal_price,monthly_meal_price = 0.0,0.0,0.0

        ## Today Beverage And Meal Data
        today_beverage_ids = self.env['baverage_bio_log'].search([('recorded_date','>=',datetime.datetime.today().date()),('recorded_date','<=',datetime.datetime.today().date())])
        beverage_type_ids = today_beverage_ids.mapped('beverage_type_id')
        for beverage in beverage_type_ids:
            today_data = today_beverage_ids.filtered(lambda x: x.beverage_type_id == beverage)
            today_beverage_price = sum(today_data.mapped(lambda x: x.total_price))
            beverage_count = len(today_data)
            today_baverage_list.append({'id':beverage.id,'name': beverage.beverage_type,'units' : beverage_count,'price': float("%.2f" % today_beverage_price) })

        today_meal_ids = self.env['meal_bio_log'].search([('recorded_date','=',datetime.datetime.today().date())])
        meal_type_ids = today_meal_ids.mapped('meal_type_id')
        for meal in meal_type_ids:
            today_meal_data = today_meal_ids.filtered(lambda x: x.meal_type_id == meal)
            today_meal_price = sum(today_meal_data.mapped(lambda x: x.total_price))
            meal_count = len(today_meal_data)
            today_meal_list.append({'id':meal.id,'name': meal.meal_type,'units' : meal_count,'price': float("%.2f" % today_meal_price) })
        

        ## Weekly Beverage And Meal Data
        weekly_beverage_model_ids = self.env['baverage_bio_log']
        weekly_meal_model_ids = self.env['meal_bio_log']
        for d in self.get_week(current_date):
            weekly_beverage_model_ids += self.env['baverage_bio_log'].search([('recorded_date','>=',d),('recorded_date','<=',d)])
            weekly_meal_model_ids += self.env['meal_bio_log'].search([('recorded_date','=',d)])
            
        weekly_beverage_type_ids = weekly_beverage_model_ids.mapped('beverage_type_id')
        for w_beverage in weekly_beverage_type_ids:
            weekly_data = weekly_beverage_model_ids.filtered(lambda x: x.beverage_type_id == w_beverage)
            weekly_beverage_price = sum(weekly_data.mapped(lambda x: x.total_price))
            weekly_beverage_count = len(weekly_data)
            weekly_baverage_list.append({'id':w_beverage.id,'name': w_beverage.beverage_type,'units' : weekly_beverage_count,'price': float("%.2f" % weekly_beverage_price) })

        weekly_meal_type_ids = weekly_meal_model_ids.mapped('meal_type_id')
        for w_meal in weekly_meal_type_ids:
            weekly_meal_data = weekly_meal_model_ids.filtered(lambda x: x.meal_type_id == w_meal)
            weekly_meal_price = sum(weekly_meal_data.mapped(lambda x: x.total_price))
            weekly_meal_count = len(weekly_meal_data)
            weekly_meal_list.append({'id':w_meal.id,'name': w_meal.meal_type,'units' : weekly_meal_count,'price': float("%.2f" % weekly_meal_price) })

        ## Monthly Beverage And Meal Data
        if current_date.day >=25:
            start_date = datetime.date(current_year,current_month, 26) 
            end_date = datetime.date(current_year,current_month, 25) + relativedelta(months=1)
        else: 
            start_date = datetime.date(current_year,current_month, 26) - relativedelta(months=1)
            end_date = datetime.date(current_year,current_month, 25)
        # print(start_date,end_date)
        delta = end_date - start_date   # returns timedelta
        monthly_beverage_model_ids = self.env['baverage_bio_log']
        monthly_meal_model_ids = self.env['meal_bio_log']
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            monthly_beverage_model_ids += self.env['baverage_bio_log'].search([('recorded_date','>=',day),('recorded_date','<=',day)])
            monthly_meal_model_ids += self.env['meal_bio_log'].search([('recorded_date','=',day)])

        monthly_beverage_type_ids = monthly_beverage_model_ids.mapped('beverage_type_id')
        for m_beverage in monthly_beverage_type_ids:
            monthly_data = monthly_beverage_model_ids.filtered(lambda x: x.beverage_type_id == m_beverage)
            monthly_beverage_price = sum(monthly_data.mapped(lambda x: x.total_price))
            monthly_beverage_count = len(monthly_data)
            monthly_baverage_list.append({'id':m_beverage.id,'name': m_beverage.beverage_type,'units' : monthly_beverage_count,'price': float("%.2f" % monthly_beverage_price)  })
        
        monthly_meal_type_ids = monthly_meal_model_ids.mapped('meal_type_id')
        for m_meal in monthly_meal_type_ids:
            monthly_meal_data = monthly_meal_model_ids.filtered(lambda x: x.meal_type_id == m_meal)
            monthly_meal_price = sum(monthly_meal_data.mapped(lambda x: x.total_price))
            monthly_meal_count = len(monthly_meal_data)
            monthly_meal_list.append({'id':m_meal.id,'name': m_meal.meal_type,'units' : monthly_meal_count,'price': float("%.2f" % monthly_meal_price) })
            
        return [today_baverage_list,weekly_baverage_list,monthly_baverage_list,today_meal_list,weekly_meal_list,monthly_meal_list]

    def get_forward_month_list(self,d):
        return [[(d + relativedelta(months=i)).strftime('%b') for i in range(12)],[(d + relativedelta(months=i)) for i in range(12)]]

    def get_filter_canteen_meal_beverage_data(self,args):
        beverage_month_price_list,meal_month_price_list = [],[]
        branch_id = args.get('branch_id',False)
        current_date = datetime.date.today()
        current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search([('date_start','<=',current_date),('date_stop','>=',current_date)],limit=1)
        months = self.get_forward_month_list(current_fiscal_year_id.date_start)
        yearly_baverage_count = self.env['baverage_bio_log'].search_count([('employee_id.base_branch_id','=',int(branch_id)),('recorded_date','>=',current_fiscal_year_id.date_start),('recorded_date','<=',current_fiscal_year_id.date_stop)])
        yearly_meal_count = self.env['meal_bio_log'].search_count([('employee_id.base_branch_id','=',int(branch_id)),('recorded_date','>=',current_fiscal_year_id.date_start),('recorded_date','<=',current_fiscal_year_id.date_stop)])
        for m in months[1]:
            _, num_days = calendar.monthrange(m.year, m.month)
            first_day = datetime.date(m.year, m.month, 1)
            last_day = datetime.date(m.year, m.month, num_days)
            weekly_beverage_model_ids = self.env['baverage_bio_log'].search([('employee_id.base_branch_id','=',int(branch_id)),('recorded_date','>=',first_day),('recorded_date','<=',last_day)])
            weekly_meal_model_ids = self.env['meal_bio_log'].search([('employee_id.base_branch_id','=',int(branch_id)),('recorded_date','>=',first_day),('recorded_date','<=',last_day)])
            beverage_month_price_list.append({'y':sum(weekly_beverage_model_ids.mapped(lambda x: x.total_price)),'count':len(weekly_beverage_model_ids) or 0, 'price': sum(weekly_beverage_model_ids.mapped(lambda x: x.total_price))})
            meal_month_price_list.append({'y':sum(weekly_meal_model_ids.mapped(lambda x: x.total_price)),'count':len(weekly_meal_model_ids) or 0, 'price': sum(weekly_meal_model_ids.mapped(lambda x: x.total_price))})
        return [months[0],beverage_month_price_list,meal_month_price_list,yearly_baverage_count,yearly_meal_count]

    @api.model
    def get_canteen_type_filter_data(self, **kwargs):
        status = kwargs.get('filters',False)
        type_id = kwargs.get('type',False)
        beverage_domain,meal_domain,context = (),(),{}
        current_date = datetime.date.today()
        
        if status == 'today_beverage':
            beverage_domain = (('recorded_date','>=',datetime.date.today()),('recorded_date','<=',datetime.date.today()),('beverage_type_id','=',int(type_id)))
        elif status == 'today_self_beverage':
            beverage_domain = (('recorded_date','>=',datetime.date.today()),('recorded_date','<=',datetime.date.today()),('beverage_type_id','=',int(type_id)),('employee_id','=',self.env.user.employee_ids.id))
        elif status == 'this_week_beverage':
            start_date = current_date - datetime.timedelta(days=current_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            beverage_domain = (('recorded_date','>=',start_date),('recorded_date','<=',end_date),('beverage_type_id','=',int(type_id)))
        elif status == 'this_week_self_beverage':
            start_date = current_date - datetime.timedelta(days=current_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            beverage_domain = (('recorded_date','>=',start_date),('recorded_date','<=',end_date),('beverage_type_id','=',int(type_id)),('employee_id','=',self.env.user.employee_ids.id))
        elif status == 'this_month_beverage':
            _, num_days = calendar.monthrange(current_date.year, current_date.month)
            if current_date.day >=25:
                first_day = datetime.date(current_date.year,current_date.month, 26) 
                last_day = datetime.date(current_date.year,current_date.month, 25) + relativedelta(months=1)
            else: 
                first_day = datetime.date(current_date.year,current_date.month, 26) - relativedelta(months=1)
                last_day = datetime.date(current_date.year,current_date.month, 25)
            beverage_domain = (('recorded_date','>=',first_day),('recorded_date','<=',last_day),('beverage_type_id','=',int(type_id)))
        elif status == 'this_month_self_beverage':
            _, num_days = calendar.monthrange(current_date.year, current_date.month)
            if current_date.day >=25:
                first_day = datetime.date(current_date.year,current_date.month, 26) 
                last_day = datetime.date(current_date.year,current_date.month, 25) + relativedelta(months=1)
            else: 
                first_day = datetime.date(current_date.year,current_date.month, 26) - relativedelta(months=1)
                last_day = datetime.date(current_date.year,current_date.month, 25)
            beverage_domain = (('recorded_date','>=',first_day),('recorded_date','<=',last_day),('beverage_type_id','=',int(type_id)),('employee_id','=',self.env.user.employee_ids.id))

        elif status == 'today_meal':
            meal_domain = (('recorded_date','>=',datetime.date.today()),('recorded_date','<=',datetime.date.today()),('meal_type_id','=',int(type_id)))
        elif status == 'today_self_meal':
            meal_domain = (('recorded_date','>=',datetime.date.today()),('recorded_date','<=',datetime.date.today()),('meal_type_id','=',int(type_id)),('employee_id','=',self.env.user.employee_ids.id))
        elif status == 'this_week_meal':
            start_date = current_date - datetime.timedelta(days=current_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            meal_domain = (('recorded_date','>=',start_date),('recorded_date','<=',end_date),('meal_type_id','=',int(type_id)))
        elif status == 'this_week_self_meal':
            start_date = current_date - datetime.timedelta(days=current_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
            meal_domain = (('recorded_date','>=',start_date),('recorded_date','<=',end_date),('meal_type_id','=',int(type_id)),('employee_id','=',self.env.user.employee_ids.id))
        elif status == 'this_month_meal':
            _, num_days = calendar.monthrange(current_date.year, current_date.month)
            if current_date.day >=25:
                first_day = datetime.date(current_date.year,current_date.month, 26) 
                last_day = datetime.date(current_date.year,current_date.month, 25) + relativedelta(months=1)
            else: 
                first_day = datetime.date(current_date.year,current_date.month, 26) - relativedelta(months=1)
                last_day = datetime.date(current_date.year,current_date.month, 25)
            meal_domain = (('recorded_date','>=',first_day),('recorded_date','<=',last_day),('meal_type_id','=',int(type_id)))
        elif status == 'this_month_self_meal':
            _, num_days = calendar.monthrange(current_date.year, current_date.month)
            if current_date.day >=25:
                first_day = datetime.date(current_date.year,current_date.month, 26) 
                last_day = datetime.date(current_date.year,current_date.month, 25) + relativedelta(months=1)
            else: 
                first_day = datetime.date(current_date.year,current_date.month, 26) - relativedelta(months=1)
                last_day = datetime.date(current_date.year,current_date.month, 25)
            meal_domain = (('recorded_date','>=',first_day),('recorded_date','<=',last_day),('meal_type_id','=',int(type_id)),('employee_id','=',self.env.user.employee_ids.id))
        
        return [beverage_domain,context,meal_domain]

    def get_project_preview(self, args):
        sbu_id = args.get('sbu_id', False)
        sbu_list, project_list, cost, revenue = [], [], 0.0, 0.0
        sbu_ids = self.env['kw_sbu_master'].sudo().search([('type', '=', 'sbu')])
        selected_sbu = self.env['kw_sbu_master'].sudo().browse(int(sbu_id))
        for sbu in sbu_ids:
            sbu_list.append({'id': sbu.id, 'name': sbu.name})
        project_ids = self.env['project.project'].search([('sbu_id', '=', int(sbu_id))])
        for project in project_ids:
            cost = sum(project.analytic_account_id.line_ids.filtered(lambda x: x.amount < 0).mapped('amount'))
            revenue = sum(project.analytic_account_id.line_ids.filtered(lambda x: x.amount > 0).mapped('amount'))
            # print(project.name, cost, revenue)

            project_list.append({'id':project.id,'name':project.name,'cost': cost, 'revenue':revenue})
        return [sbu_list,project_list,selected_sbu.id or 0]
    
    def get_lost_and_found_data(self):
        lost_list,found_list,first_lost,rest_lost,first_found,rest_found = [],[],[],[],[],[]
        model = self.env['kw_lost_and_found']
        found_count = model.search_count([('category','=','found'),('state','=','informed')])
        lost_count = model.search_count([('category','=','lost'),('state','=','informed')])

        lost_ids = model.search([('category','=','lost'),('state','=','informed')])
        for lost in lost_ids:
            lost_message = ''
            for response in lost.response_log:
                lost_message += f"<tr class='response_log'><td>{response.employee_id.name}</td><td>{response.response}</td></tr>"
            lost_list.append({
                'id': lost.id,
                'item': dict(model.fields_get(allfields='item_name')['item_name']['selection'])[lost.item_name],
                'item_attributes': lost.item_attributes,
                'description': lost.item_attributes,
                'office_location':lost.office_location_id.name ,
                'location': lost.lost_location,
                'date': lost.lost_datetime.strftime("%d-%b-%Y %I:%M %p"),
                'image': lost.upload_image,
                'current_user_id' : self.env.user.id,
                'requested_by': lost.requested_by.user_id.id,
                'lf_manager': self.env.user.has_group('kw_lost_and_found.lost_and_found_hr_user'),
                'response_log': lost_message,
                'response' : 1 if len(lost.response_log) > 0 else 0,
                'employee': lost.requested_by.name
            })
        if len(lost_list) > 1:
            rest_lost = lost_list[1:]
        if len(lost_list) > 0:
            first_lost = lost_list[:1]

        found_ids = model.search([('category','=','found'),('state','=','informed')])
        for found in found_ids:
            found_message = ''
            for response in found.response_log:
                found_message += f"<tr><td>{response.employee_id.name}</td><td>{response.response}</td></tr>"
            found_list.append({
                'id': found.id,
                'item': dict(model.fields_get(allfields='item_name')['item_name']['selection'])[found.item_name],
                'item_attributes': found.item_attributes,
                'description': found.item_attributes,
                'location': found.tentative_location,
                'office_location':found.office_location_id.name ,
                'date': found.lost_datetime.strftime("%d-%b-%Y %I:%M %p"),
                'image': found.upload_image,
                'response_log': found_message,
                'response' : 1 if len(found.response_log) > 0 else 0,
                'lf_manager': self.env.user.has_group('kw_lost_and_found.lost_and_found_hr_user')
                
            })
        if len(found_list) > 1:
            rest_found = found_list[1:]
        if len(found_list) > 0:
            first_found = found_list[:1]
        return [first_found,rest_found,found_count,lost_count,first_lost,rest_lost]

    @api.model
    def update_response_log_lf_data(self, **kwargs):
        lnf_id = kwargs.get('id',False)
        response = kwargs.get('response',False)
        respond_type = kwargs.get('respond_type',False)
        lf_id = self.env['kw_lost_and_found'].browse(int(lnf_id))
        if lf_id:
            if respond_type == 'close':
                lf_id.write({'state':'close','close_remarks':response,'close_date': datetime.datetime.today()})    
            else:
                lf_id.write({
                    'response_log': [[0,0,{
                                        'lf_id': lf_id.id,
                                        'employee_id':self.env.user.employee_ids.id,
                                        'response':response,
                            }]]
                })
            

    @api.model
    def get_shift_from_branch(self, **kwargs):
        shift_list = []
        branch_id = kwargs.get('branch_id', False)
        shift_ids = self.env['resource.calendar'].sudo().search([('branch_id','=',int(branch_id)),('employee_id','=',False)])
        for shift in shift_ids:
            shift_list.append({'id': shift.id, 'name': shift.name})
        return shift_list

    def fetch_project_performer_data(self,args):
        project_month = args.get('project_month',False)
        project_year = args.get('project_year',False)
        if args:
            current_month_year = datetime.date(int(project_year), int(project_month), 1).strftime('%B %Y')
            current_month,current_year = int(project_month), int(project_year)
        else:
            current_month_year = datetime.datetime.today().strftime("%b %Y")
            current_month,current_year = datetime.datetime.today().month, datetime.datetime.today().year
        data=[]
        # quality_resource = self.env.user.has_group('kw_project_performer_metrics.group_quality_engineer')
        # quality_head = self.env.user.has_group('kw_project_performer_metrics.group_quality_head')


        fetch_data = self.env['kw_project_performer_metrics'].sudo().search([('state','in',['reject','publish']),('year','=',str(current_year)),('month','=',str(current_month))],order="total_score desc")
        if fetch_data:
            for rec in fetch_data:
                data.append({
                    'project_name':rec.project_id.name,
                    'project_manager':rec.project_manager_id.name,
                    'audit_schedule':rec.audit_schedule,
                    'audit_compliance':rec.audit_compliance,
                    'product_review':rec.product_review,
                    'audit_score': rec.audit_score,
                    'winner_data': True if rec.state =='publish' else False

                    })
        return [data,current_month_year]


    def fetch_health_insurance_data(self,args):
        health_policy_list,accidental_policy_list,first_health_policy,first_accidental_policy,rest_health_policy,rest_accidental_policy = [],[],[],[],[],[]
        health_policy_ids = self.env['health_insurance_policy_master'].search([('policy_type','=','health')])
        accidental_policy_ids = self.env['health_insurance_policy_master'].search([('policy_type','=','accidental')])
        for health in health_policy_ids:
            health_policy_list.append({
                'id': health.id,
                'policy_number': health.policy_number,
                'vendor_name': health.vendor_name,
                'sum_assured_amount': health.sum_assured_amount,
                'validity_upto': health.validity_upto.strftime("%d-%b-%Y"),
                'toll_free_number': health.toll_free_number,
                'claim_form_attachment': health.claim_form_attachment,
                'attachment_id': health.attachment_id,
                'benefits': health.benefits,
                'spoc_contact' : self.env['health_insurance_policy_spoc'].search_read([('policy_id','=',health.id)],['spoc_name','spoc_contact_no'])
            })

        if len(health_policy_list) > 1:
            rest_health_policy = health_policy_list[1:]
        if len(health_policy_list) > 0:
            first_health_policy = health_policy_list[:1]
        for accident in accidental_policy_ids:
            accidental_policy_list.append({
                'id': accident.id,
                'policy_number': accident.policy_number,
                'vendor_name': accident.vendor_name,
                'sum_assured_amount': accident.sum_assured_amount,
                'validity_upto': accident.validity_upto.strftime("%d-%b-%Y"),
                'toll_free_number': accident.toll_free_number,
                'claim_form_attachment': accident.claim_form_attachment,
                'attachment_id': accident.attachment_id,
                'benefits': accident.benefits,
                'spoc_contact' : self.env['health_insurance_policy_spoc'].search_read([('policy_id','=',accident.id)],['spoc_name','spoc_contact_no'])
            })

        if len(accidental_policy_list) > 1:
            rest_accidental_policy = accidental_policy_list[1:]
        if len(accidental_policy_list) > 0:
            first_accidental_policy = accidental_policy_list[:1]
        return [first_health_policy,rest_health_policy,first_accidental_policy,rest_accidental_policy]
    
    def fetch_count_debt_opp_list_data(self):
        super_user_ids = self.env['ir.config_parameter'].sudo().search([('key', '=', 'Sales Portlet Super Users')]).value
        is_super_user = True if str(self.env.user.employee_ids.id) in super_user_ids else False

        debtor_records = self.env['kw_debtor_list_master'].search([]).filtered(lambda x: x.acc_manager_id.id == self.env.user.employee_ids.id or x.teamleader_id.id == self.env.user.employee_ids.id) if not is_super_user else self.env['kw_debtor_list_master'].search([])
        coln_plan_expired_rec = debtor_records.filtered(lambda x: x.expected_date < date.today() if x.expected_date else False)
        debtor_within_90_days = debtor_records.filtered(lambda x: x.expected_date >= date.today() and x.expected_date <= date.today() + timedelta(days=90) if x.expected_date else False)
        debtor_within_91_to_180_days = debtor_records.filtered(lambda x: x.expected_date >= date.today()+timedelta(days=91) and x.expected_date <= date.today()+timedelta(days=180) if x.expected_date else False)
        debtor_above_180_days = debtor_records.filtered(lambda x: x.expected_date >= date.today()+timedelta(days=181) if x.expected_date else False)
        total_expired_debtor_value = round((int(sum(coln_plan_expired_rec.mapped('pending_amt'))) / 10000000),3)
        formatted_total_expired_debtor_value = locale.format('%.2f', total_expired_debtor_value, grouping=True)

        opportunity_records = self.env['kw_opp_port'].search([]).filtered(lambda x: x.acc_manager_id.id == self.env.user.employee_ids.id or x.teamleader_id.id == self.env.user.employee_ids.id) if not is_super_user else self.env['kw_opp_port'].search([])
        closing_opp_expired_rec = opportunity_records.filtered(lambda x: x.expected_closing_date < date.today() if x.expected_closing_date else False)
        pac_3 = opportunity_records.filtered(lambda x: x.pac_status == 3 if x.pac_status else False)
        pac_2 = opportunity_records.filtered(lambda x: x.pac_status == 2 if x.pac_status else False)
        pac_1 = opportunity_records.filtered(lambda x: x.pac_status == 1 if x.pac_status else False)

        total_opp_val = round((int(sum(opportunity_records.mapped('opp_val'))) / 10000000),3)
        total_expired_opp_val = round((int(sum(closing_opp_expired_rec.mapped('opp_val'))) / 10000000),3)
        total_pac_3_opp_val = round((int(sum(pac_3.mapped('opp_val'))) / 10000000),3)
        total_pac_2_opp_val = round((int(sum(pac_2.mapped('opp_val'))) / 10000000),3)
        total_pac_1_opp_val = round((int(sum(pac_1.mapped('opp_val'))) / 10000000),3)

        formatted_total_opp_val = locale.format('%.2f', total_opp_val, grouping=True)
        formatted_total_expired_opp_val = locale.format('%.2f', total_expired_opp_val, grouping=True)
        formatted_total_pac_3_opp_val = locale.format('%.2f', total_pac_3_opp_val, grouping=True)
        formatted_total_pac_2_opp_val = locale.format('%.2f', total_pac_2_opp_val, grouping=True)
        formatted_total_pac_1_opp_val = locale.format('%.2f', total_pac_1_opp_val, grouping=True)

        return {
        'len_total':len(debtor_records),
        'len_exp': len(coln_plan_expired_rec),
        'len_90': len(debtor_within_90_days),
        'len_91_180': len(debtor_within_91_to_180_days),
        'len_180': len(debtor_above_180_days),
        'total_expired_debtor_value':formatted_total_expired_debtor_value,
        'len_opp_total': len(opportunity_records),
        'len_opp_exp': len(closing_opp_expired_rec),
        'len_pac_3': len(pac_3),
        'len_pac_2': len(pac_2),
        'len_pac_1': len(pac_1),
        'total_opp_val': formatted_total_opp_val,
        'total_expired_opp_val': formatted_total_expired_opp_val,
        'total_pac_3_opp_val': formatted_total_pac_3_opp_val,
        'total_pac_2_opp_val': formatted_total_pac_2_opp_val,
        'total_pac_1_opp_val': formatted_total_pac_1_opp_val,}
    

    def fetch_debtor_list_data(self,status,args):
        debtor_list,debtor_with_date_list,debtor_without_date_list =[],[],[]
        debtor_records = self.env['kw_debtor_list_master'].search([])
        if status == 'total_debtor_list':
            required_debtor_rec = debtor_records
        elif status == 'expired_debtor_list':
            required_debtor_rec = debtor_records.filtered(lambda x: x.expected_date < date.today() if x.expected_date else False)
        elif status == 'within_90_days_debtor_list':
            required_debtor_rec = debtor_records.filtered(lambda x: x.expected_date >= date.today() and x.expected_date <= date.today() + timedelta(days=90) if x.expected_date else False)
        elif status == 'within_91_180_days_debtor_list':
            required_debtor_rec = debtor_records.filtered(lambda x: x.expected_date >= date.today()+timedelta(days=91) and x.expected_date <= date.today()+timedelta(days=180) if x.expected_date else False)
        elif status == 'above_180_days_debtor_list':
            required_debtor_rec = debtor_records.filtered(lambda x: x.expected_date >= date.today()+timedelta(days=181) if x.expected_date else False)
        else:
            required_debtor_rec = debtor_records
        
        debtor_with_date_ids = required_debtor_rec.filtered(lambda x: x.expected_date != False)
        debtor_w_o_date_ids = required_debtor_rec.filtered(lambda x: x.expected_date == False)
        super_user_ids = self.env['ir.config_parameter'].sudo().search([('key', '=', 'Sales Portlet Super Users')]).value
        is_super_user = True if str(self.env.user.employee_ids.id) in super_user_ids else False
        for debtor in debtor_with_date_ids:
            formatted_expected_date = debtor.expected_date.strftime("%d-%b-%Y") if debtor.expected_date else None
            formatted_inv_amount = locale.format_string("%d", debtor.invoice_amt, grouping=True)
            formatted_pend_amount = locale.format_string("%d", debtor.pending_amt, grouping=True)
            invoice_date = debtor.invoice_date.strftime("%d-%b-%Y") if debtor.invoice_date else None
            if is_super_user or self.env.user.employee_ids.id == debtor.acc_manager_id.id or self.env.user.employee_ids.id == debtor.teamleader_id.id:
                debtor_with_date_list.append({
                    'id': debtor.id,
                    'wo_code': debtor.wo_code,
                    'invoice_no': debtor.invoice_no,
                    'invoice_date': invoice_date,
                    'invoice_amt': formatted_inv_amount,
                    'pending_amt': formatted_pend_amount,
                    'expected_date': debtor.expected_date,
                    'formatted_expected_date': formatted_expected_date,
                    'less_than_curdate': debtor.expected_date < date.today() if debtor.expected_date else False,
                    'last_updated_on':debtor.last_updated_on,
                    'next_execution_time':debtor.next_execution_time})
                
        for debtor in debtor_w_o_date_ids:
            formatted_expected_date = debtor.expected_date.strftime("%d-%b-%Y") if debtor.expected_date else None
            formatted_inv_amount = locale.format_string("%d", debtor.invoice_amt, grouping=True)
            formatted_pend_amount = locale.format_string("%d", debtor.pending_amt, grouping=True)
            invoice_date = debtor.invoice_date.strftime("%d-%b-%Y") if debtor.invoice_date else None
            if is_super_user or self.env.user.employee_ids.id == debtor.acc_manager_id.id or self.env.user.employee_ids.id == debtor.teamleader_id.id:
                debtor_without_date_list.append({
                    'id': debtor.id,
                    'wo_code': debtor.wo_code,
                    'invoice_no': debtor.invoice_no,
                    'invoice_date': invoice_date,
                    'invoice_amt': formatted_inv_amount,
                    'pending_amt': formatted_pend_amount,
                    'expected_date': debtor.expected_date,
                    'formatted_expected_date':formatted_expected_date,
                    'less_than_curdate': debtor.expected_date < date.today() if debtor.expected_date else False,
                    'last_updated_on':debtor.last_updated_on,
                    'next_execution_time':debtor.next_execution_time})
        sorted_debtor_date_list = sorted(debtor_with_date_list, key=lambda x: x['expected_date'], reverse=False)
        debtor_list = sorted_debtor_date_list + debtor_without_date_list
        return [debtor_list]
    
    def fetch_guest_house_data(self,args):
        guest_house_list = []
        guest_house_ids = self.env['kw_guest_house_master'].search([])
        for guest in guest_house_ids:
            guest_house_list.append({
                'id':guest.id,
                'guest_house_name': guest.guest_house_name,
                'country': guest.country_id.name,
                'state':guest.state_id.name,
                'city':guest.city_id.name,
                'contact_person':guest.contact_person_1_id.name,
                'contact_number':guest.contact_no_1,
                'available_single_room': guest.available_single_room,
                'available_double_room' : guest.available_double_room
            })
        return [guest_house_list]

    def fetch_opp_port_data(self,status,args):
        opp_list,opp_with_date_list,opp_without_date_list =[],[],[]
        opportunity_records = self.env['kw_opp_port'].search([])
        if status == 'total_opp_list':
            required_opp_rec = opportunity_records
        elif status == 'expired_opp_list':
            required_opp_rec = opportunity_records.filtered(lambda x: x.expected_closing_date < date.today() if x.expected_closing_date else False)
        elif status == 'pac_approved_opp_list':
            required_opp_rec = opportunity_records.filtered(lambda x: x.pac_status == 3 if x.pac_status else False)
        elif status == 'pending_at_pac_opp_list':
            required_opp_rec = opportunity_records.filtered(lambda x: x.pac_status == 2 if x.pac_status else False)
        elif status == 'not_applied_to_pac_opp_list':
            required_opp_rec = opportunity_records.filtered(lambda x: x.pac_status == 1 if x.pac_status else False)
        else:
            required_opp_rec = opportunity_records.filtered(lambda x: x.pac_status == 3 if x.pac_status else False)
        
        opp_with_date_ids = required_opp_rec.filtered(lambda x: x.expected_closing_date != False)
        opp_w_o_date_ids = required_opp_rec.filtered(lambda x: x.expected_closing_date == False)

        super_user_ids = self.env['ir.config_parameter'].sudo().search([('key', '=', 'Sales Portlet Super Users')]).value
        is_super_user = True if str(self.env.user.employee_ids.id) in super_user_ids else False

        for opp in opp_with_date_ids:
            formatted_closing_date = opp.expected_closing_date.strftime("%d-%b-%Y") if opp.expected_closing_date else None
            formatted_amount = locale.format_string("%d", opp.opp_val, grouping=True)
            if is_super_user or self.env.user.employee_ids.id == opp.acc_manager_id.id or self.env.user.employee_ids.id == opp.teamleader_id.id:
                opp_with_date_list.append({
                        'id': opp.id,
                        'opp_code': opp.opp_code,
                        'client_name': opp.client_short_name if opp.client_short_name else None,
                        'opp_name': opp.opp_name,
                        'a_m': opp.a_manager,
                        'formatted_closing_date':formatted_closing_date,
                        'closing_date': opp.expected_closing_date,
                        'amount':formatted_amount,
                        'less_than_curdate': opp.expected_closing_date < date.today() if opp.expected_closing_date else False,
                        'last_updated_on':opp.last_updated_on,
                        'next_execution_time':opp.next_execution_time}) 
        for opp in opp_w_o_date_ids:
            formatted_closing_date = opp.expected_closing_date.strftime("%d-%b-%Y") if opp.expected_closing_date else None
            formatted_amount = locale.format_string("%d", opp.opp_val, grouping=True)
            if is_super_user or self.env.user.employee_ids.id == opp.acc_manager_id.id or self.env.user.employee_ids.id == opp.teamleader_id.id:
                opp_without_date_list.append({
                        'id': opp.id,
                        'opp_code': opp.opp_code,
                        'client_name': opp.client_short_name if opp.client_short_name else None,
                        'opp_name': opp.opp_name,
                        'a_m': opp.a_manager,
                        'formatted_closing_date': formatted_closing_date,
                        'closing_date': opp.expected_closing_date,
                        'amount':formatted_amount,
                        'less_than_curdate': opp.expected_closing_date < date.today() if opp.expected_closing_date else False,
                        'last_updated_on':opp.last_updated_on,
                        'next_execution_time':opp.next_execution_time}) 
        sorted_opp_list = sorted(opp_with_date_list, key=lambda x: x['closing_date'], reverse=False)
        opp_list = sorted_opp_list + opp_without_date_list
        return [opp_list]
    
    def fetch_billing_port_data(self, args):
        super_user_ids = self.env['ir.config_parameter'].sudo().search([('key', '=', 'Sales Portlet Super Users')]).value
        is_super_user = True if str(self.env.user.employee_ids.id) in super_user_ids else False
        query = """SELECT sbu_name,wo_code AS wo_code,wo_name AS wo_name,sum(billing_amount) AS billing_amount,project_id as project_id,last_updated_on as last_updated_on,next_execution_time as next_execution_time,account_leader_id as account_leader_id,account_manager_id as account_manager_id,project_manager_id as project_manager_id,reviewer_id as reviewer_id,sbu_head_id as sbu_head_id,sum(case when billing_target_date < CURRENT_DATE then 1 else 0 end) as date_status_count
            FROM kw_billing_dashboard_port where active = true GROUP BY sbu_name,wo_code,wo_name,project_id,last_updated_on,next_execution_time,account_leader_id,account_manager_id,project_manager_id,reviewer_id,sbu_head_id"""
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        billing_data = []
        for result in results:
            formatted_billing_amount = locale.format_string("%d", result['billing_amount'], grouping=True)
            if is_super_user or (self.env.user.employee_ids.id == result['account_leader_id'] if result['account_leader_id'] else False) or (self.env.user.employee_ids.id == result['account_manager_id'] if result['account_manager_id'] else False) or (self.env.user.employee_ids.id == result['project_manager_id'] if result['project_manager_id'] else False) or (self.env.user.employee_ids.id == result['reviewer_id'] if result['reviewer_id'] else False) or (self.env.user.employee_ids.id == result['sbu_head_id'] if result['sbu_head_id'] else False):
                billing_data.append({
                'sbu_name': result['sbu_name'],
                'wo_code': result['wo_code'],
                'wo_name': result['wo_name'],
                'billing_amount': formatted_billing_amount,
                'project_id':result['project_id'],
                'last_updated_on':result['last_updated_on'],
                'next_execution_time':result['next_execution_time'],
                'date_status_count':result['date_status_count']})

        return [billing_data]


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
        has_group_canteen_manager = self.env.user.has_group('kw_canteen.canteen_manager_group')
        has_lf_manager = self.env.user.has_group('kw_lost_and_found.lost_and_found_hr_user')
        dashboard_data = {
            'name': self.browse(ks_dashboard_id).name,
            'ks_dashboard_manager': has_group_ks_dashboard_manager,

            'canteen_manager': has_group_canteen_manager,
            'lost_found_spoc':has_lf_manager,
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
            'branch_data': self.get_branch_data(),
            'department_and_location_data': self.get_department_and_location_data(),
            'current_employee_subordinates': self.current_employee_subordinates(),
            'get_month_year_list' : self.get_month_year_list(),
            'remove_announcement': self.remove_announcement_data(),
        }
        
        ks_item_domain = ks_item_domain or []
        dashboard_items = self.env['kw_user_portlets'].sudo().search([('employee_id.user_id','=',self.env.user.id),('ks_dashboard_ninja_board_id','=',ks_dashboard_id)],limit=1)
        for item in dashboard_items.ks_dashboard_items_id:
            if item.is_published == True:
                if item.common_portlet == True or self.env.user.employee_ids.id in item.employee_visible.ids:
                    dashboard_item_ids.append(item.id)
        # print(dashboard_item_ids)
        
        try:
            items = self.ks_dashboard_items_ids.sudo().search([['ks_dashboard_ninja_board_id', '=', ks_dashboard_id]] + ks_item_domain).ids
        except Exception as e:
            items = self.ks_dashboard_items_ids.sudo().search([['ks_dashboard_ninja_board_id', '=', ks_dashboard_id]] + ks_item_domain).ids
        dashboard_data['ks_dashboard_items_ids'] = dashboard_item_ids
        return dashboard_data

    @api.model
    def fetch_employee_data(self, **kwargs):
        employee_portlet_data = {
            'kwantify_employee_list': self.kwantify_employee_directory(kwargs),
        }
        return employee_portlet_data

    @api.model
    def fetch_meeting_data(self):
        meeting_data = {
            'today_meeting_data': self.today_meeting_data(),
            'tomorrow_meeting_data': self.tomorrow_meeting_data(),
            'week_meeting_data': self.week_meeting_data(datetime.datetime.today())
        }
        return meeting_data
    
    @api.model
    def fetch_attendance_data(self, **kwargs):
        attendance_data = {
            'current_month_attendance': self.current_month_attendance(),
            'get_filter_attendance_data': self.get_filter_attendance_data(kwargs) if 'employeeSelect' and 'yearSelect' and 'monthSelect' in kwargs else False,
        }
        return attendance_data

    @api.model
    def holidays_calendar_data(self, **kwargs):
        holiday_data = {
            'holiday_calendar_data': self.get_holiday_calendar_data(kwargs)
        }
        return holiday_data

    @api.model
    def meeting_room_data(self, **kwargs):
        meeting_room_availability_data = {
            'today_meeting_room_availability': self.today_meeting_room_availability(),
            'tomorrow_meeting_room_availability': self.tomorrow_meeting_room_availability(),
            'choose_date_meeting_room_availability': self.get_meeting_on_date_select(kwargs) if 'meetingDateSelect' in kwargs else False
        }
        return meeting_room_availability_data

    @api.model
    def team_attendance(self):
        team_attendance_status_data = {
            'team_attendance_data': self.team_attendance_data(),
        }
        return team_attendance_status_data
    
    @api.model
    def local_visit_data(self):
        localVisit = {
            'local_visits': self.local_visits()
        }
        return localVisit
        
    @api.model
    def announcement_data(self):
        announcement_datas = {
            'announcement': self.get_announcement_data()
        }
        return announcement_datas
    
    @api.model
    def tour_data(self):
        tour_data = {
            'tour': self.get_tour_data()
        }
        return tour_data

    @api.model
    def fetch_leave_and_absent_data(self):
        leave_and_absent_data = {
            'leave_and_absent': self.get_leave_and_absent_data()
        }
        return leave_and_absent_data

    @api.model
    def get_best_wishes_data(self):
        best_wishes_data = {
            'best_wishes': self.best_wishes()
        }
        return best_wishes_data

    @api.model
    def get_daily_attendance_data(self):
        daily_attendance_data = {
            'daily_attendance': self.get_attendance_count()
        }
        return daily_attendance_data

    @api.model
    def get_appraisal_data(self, **kwargs):
        appraisal_data = {
            'appraisal_data': self.get_kw_appraisal_data(kwargs)
        }
        return appraisal_data

    @api.model
    def get_timesheet_data(self, **kwargs):
        timesheet_data = {
            'self_timesheet_data': self.get_self_timesheet(kwargs)
        }
        return timesheet_data

    @api.model
    def get_sub_ordinates_timesheet_data(self):
        timesheet_data = {
            'self_sub_ordinates_timesheet_data': self.get_sub_ordinates_timesheet()
        }
        return timesheet_data
    
    @api.model
    def get_canteen_data(self):
        canteen_data = {
            'canteen_data': self.get_canteen_meal_beverage_data()
        }
        return canteen_data

    @api.model
    def get_canteen_filter_data(self,**kwargs):
        filter_canteen_data = {
            'canteen_data': self.get_filter_canteen_meal_beverage_data(kwargs)
        }
        return filter_canteen_data

    @api.model
    def get_project_preview_data(self, **kwargs):
        project_preview_data = {
            'project_preview_data': self.get_project_preview(kwargs)
        }
        return project_preview_data
    
    @api.model
    def fetch_lost_and_found_data(self, **kwargs):
        lost_and_found_data = {
            'lost_and_found_data': self.get_lost_and_found_data()
        }
        return lost_and_found_data

    @api.model
    def get_project_performer_metrics_data(self, **kwargs):
        project_performer_data = {
            'project_performer_data': self.fetch_project_performer_data(kwargs)
        }
        return project_performer_data

    @api.model
    def get_health_insurance_data(self, **kwargs):
        health_insurance_data = {
            'health_insurance_data': self.fetch_health_insurance_data(kwargs),
        }
        return health_insurance_data
    
    @api.model
    def get_debtor_list_data(self,status, **kwargs):
        guest_house_data = {
            'debtor_list_data': self.fetch_debtor_list_data(status,kwargs),
        }
        return guest_house_data
    
    @api.model
    def get_count_debtor_list_data(self, **kwargs):
        count_debtor_opp_list_data = {
            'count_debtor_opp_list_data': self.fetch_count_debt_opp_list_data(),
        }
        return count_debtor_opp_list_data

    @api.model
    def get_guest_house_data(self, **kwargs):
        guest_house_data = {
            'guest_house_data': self.fetch_guest_house_data(kwargs),
        }
        return guest_house_data

    @api.model
    def get_opportunity_data(self, status,**kwargs):
        opportunity_data = {
            'opportunity_data': self.fetch_opp_port_data(status,kwargs),
        }
        return opportunity_data
    
    @api.model
    def get_billing_data(self, **kwargs):
        billing_data = {
            'billing_data': self.fetch_billing_port_data(kwargs),
        }
        return billing_data
    
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