# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from datetime import date, datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class WFHByHRProcess(models.Model):
    _name = 'kw_wfh_hr_process'
    _description = "WFH By HR"

    """ Assign 'Total Allowed days' after calculating. 
        :If total leave days = 0 --> 'Total Allowed days' = 'No Limit'
        :If total leave days = 'value' --> 'Total Allowed days' = 'value' 
        """
    @api.depends('no_of_leave_days')
    def _compute_allowed_days(self):
        if self.no_of_leave_days == '0':
            self.allowed_days = 'No limit'
        if self.no_of_leave_days != '0':
            self.allowed_days = self.no_of_leave_days

    """ Calculate total no of day's in selected date range excluding Saturday and Sunday 
    (Total Day's between From date - To date) for both 'WFH By User' and 'WFH By HR' 
        """
    @api.depends('from_date', 'to_date')
    def _compute_days_count(self):
        dt_from = dt_to = act_from_date = act_to_date = False
        for record in self:
            if record.from_date and record.to_date:
                act_from_date = record.from_date
                act_to_date = record.to_date
                dt_from = datetime.strptime(str(act_from_date), DEFAULT_SERVER_DATE_FORMAT).date()
                dt_to = datetime.strptime(str(act_to_date), DEFAULT_SERVER_DATE_FORMAT).date()
            if dt_from and dt_to and act_from_date and act_to_date:
                daysDiff = str((dt_to - dt_from).days)
                SatAndSun = 0
                dates_btwn = dt_from
                while dates_btwn <= dt_to:
                    if dates_btwn.strftime("%A") == "Saturday":
                        SatAndSun += 1
                    if dates_btwn.strftime("%A") == "Sunday":
                        SatAndSun += 1
                    else:
                        SatAndSun += 0
                    dates_btwn = dates_btwn + timedelta(days=1)
                if act_from_date <= act_to_date:
                    self.days_count = int(daysDiff) - int(SatAndSun) + 1

    @api.depends('search_by', 'department_id', 'division', 'section', 'practise', 'location_id', 'location_type')
    def _compute_employee_count(self):
        pass

    name = fields.Char(default="WFH By HR", string="Name")
    search_by = fields.Selection(string="Search Option",
                                 selection=[('user', 'By User'), ('hierarchy', 'By Hierarchy')],
                                 required=True, default='user')
    searched_user = fields.Many2many('hr.employee', string="Employee")
    department_id = fields.Many2many('hr.department', 'hr_process_department_rel', 'department_id', 'process_id', string="Department", default=False)
    division = fields.Many2many('hr.department', 'hr_process_division_rel', 'division_id', 'process_id', string="Division", default=False)
    section = fields.Many2many('hr.department', 'hr_process_section_rel', 'section_id', 'process_id', string="Practise", default=False)
    practise = fields.Many2many('hr.department', 'hr_process_practise_rel', 'practise_id', 'process_id', string="Section", default=False)
    location_type = fields.Selection(string="Location Type", selection=[('all', 'All'), ('location', 'Location Specific')], default='location')
    location_id = fields.Many2many('kw_res_branch', string="Location", track_visibility='onchange')
    from_date = fields.Date(string='From Date', track_visibility='onchange', index=True)
    to_date = fields.Date(string='To Date', track_visibility='onchange', index=True)
    days_count = fields.Char(string="Total days", compute='_compute_days_count', store=True, track_visibility='onchange')
    wfh_ids = fields.One2many('kw_wfh', 'process_id', string="WFH availed by Employee's")
    reason_id = fields.Many2one('kw_wfh_reason_master', string="Reason", required=True)
    allowed_days = fields.Char(string="Maximum Day's Allowed", compute='_compute_allowed_days')
    no_of_leave_days = fields.Char(related='reason_id.no_of_days', string="No of allowed WFH days")
    employee_count = fields.Integer(string='Employee Count', compute='_compute_employee_count')
    remark = fields.Text('Comment', size=40,required=True)

    """ On calling the Method
        :Hierarchy wise selection: show's list of employee with thier wfh status and date
        """
    @api.onchange('from_date', 'to_date', 'department_id', 'division', 'section', 'practise', 'location_id')
    def _populate_employees(self):
        self.wfh_ids = False
        if self.from_date and self.to_date and not self.searched_user:
            if self.from_date > self.to_date:
                raise ValidationError("From date should be less than To date.")
            # self.searched_user = False
            domain = []
            if self.search_by == 'hierarchy':
                if self.department_id:
                    domain.append(('department_id', 'in', self.department_id.ids))
                if self.division:
                    domain.append(('division', 'in', self.division.ids))
                if self.section:
                    domain.append(('section', 'in', self.section.ids))
                if self.practise:
                    domain.append(('practise', 'in', self.practise.ids))
            if self.location_id:
                domain.append(('job_branch_id', 'in', self.location_id.ids))
            emp_ids = self.env['hr.employee'].sudo().search(domain)
            wfh_domain = ['&','&',('state', '=', 'grant'), ('employee_id', 'in', emp_ids.ids),
                            '|', '|',
                           '&', ('request_from_date', '<=', self.from_date), ('request_to_date', '>=', self.from_date),
                           '&', ('request_from_date', '<=', self.to_date), ('request_to_date', '>=', self.to_date),
                           '&', ('request_from_date', '>=', self.from_date), ('request_to_date', '<=', self.to_date), ]
            wfh_records = self.env['kw_wfh'].sudo().search(wfh_domain)
            return {'value': {'wfh_ids': wfh_records.ids if wfh_records else []}}

    @api.onchange('department_id')
    def onchange_department(self):
        dept_child = self.mapped("department_id.child_ids")
        self.division &= dept_child
        return {'domain': {'division': [('id', 'in', dept_child.ids)]}}

    @api.onchange('division')
    def onchange_division(self):
        division_child = self.mapped("division.child_ids")
        self.section &= division_child
        return {'domain': {'section': [('id', 'in', division_child.ids)]}}

    @api.onchange('section')
    def onchange_section(self):
        section_child = self.mapped("section.child_ids")
        self.practise &= section_child
        return {'domain': {'practise': [('id', 'in', section_child.ids)]}}

    """ On onchange of 'search_by','location_type','location_id'
        :Hierarchy wise: populate list of employee's present in the selected Hierarchy (irrespective of location)
        :User wise: populate all employee's (irrespective of location) 
        """
    @api.onchange('search_by', 'location_type', 'location_id')
    def onchange_search_by(self):
        if self.search_by == 'user':
            self.department_id = False
            self.division = False
            self.section = False
            self.practise = False
        if self.location_type == 'all':
            self.location_id = False
