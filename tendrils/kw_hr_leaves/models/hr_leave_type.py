# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

LEAVE_TYPE_EL,LEAVE_TYPE_MT      = 'EL','MT'

class KwLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    

    leave_type_config_ids   = fields.One2many(
        string='Leave Configuration Ids',
        comodel_name='kw_leave_type_config',
        inverse_name='leave_type_id',
    )
    leave_code              = fields.Char(string='Leave Code')
    for_probationary        = fields.Boolean(string='Applicable to Probation Employee')   
    employement_type_ids    = fields.Many2many('kwemp_employment_type', string="Applicable For")

    is_comp_off             = fields.Boolean(string='Is Comp Off')
    validity_days           = fields.Integer(string='Lapse After (in days)')
    allowing_notice_period_employees = fields.Boolean(string="Allowing Notice Period Employees")
    parent_leave_id = fields.Many2one('hr.leave.type',"Parent Leave")
    
    # kw_leave_type_master_id = fields.Many2one(
    #     string='Leave Type',
    #     comodel_name='kw_leave_type_master',
    #     ondelete='restrict',
    # )
    
    
    validation_type         = fields.Selection([
        ('hr', 'Human Resource officer'),
        ('manager', 'Employee Manager'),
        ('both', 'Double Validation')], default='manager', string='Validation By')
    
    for_notice_period       = fields.Boolean(string='Applicable to Notice Period')   

    carry_forward            = fields.Boolean(string='Carry Forward')
    carry_forward_percentage = fields.Float(string=">= 1 year service %",help='Carry Forward Percentage')
    carry_forward_lapsed     = fields.Integer(string='Accumulation Upto (in days)')
    cf_less_than_year_percent= fields.Float(string=">= 6 months & < 1 year service %",help='Carry Forward Percentage (Less 1 Year Service) ')


    encashable               = fields.Boolean(string='Encashable')
    encashable_percentage    = fields.Float(string=">= 1 year service %",help='Encashable Percentage')
    en_less_than_year_percent= fields.Float(string=">= 6 months & < 1 year service %",help='Encashable Percentage (Less 1 Year Service) ')

    _sql_constraints = [
        ('name_uniq', 'unique(leave_code,company_id)','The leave code must be unique!'),
    ]

    @api.constrains('name')
    def check_name(self):
        for record in self:
            leave_record = self.env['hr.leave.type'].search([('company_id','=',record.company_id.id)]) - record
            for leave in leave_record:
                if leave.name.lower() == record.name.lower():
                    raise ValidationError('Exists! Already a same Leave Type exist.')

            if not re.match("^[0-9a-zA-Z_. ]+$", str(record.name)) != None:
                raise ValidationError("Leave Type should not contain special characters.")

    @api.constrains('carry_forward', 'encashable','carry_forward_percentage','encashable_percentage','cf_less_than_year_percent','en_less_than_year_percent')
    def check_encashable_carry_forward_percentage(self):
        for record in self:
            if record.encashable == True and (record.encashable_percentage < 1 or record.encashable_percentage > 100.00 or record.en_less_than_year_percent < 0 or record.en_less_than_year_percent > 100.00):
                raise ValidationError("Encashable Percentage should be between 0-100% .")

            if record.carry_forward == True and ((record.carry_forward_percentage < 1 or record.carry_forward_percentage > 100.00) or (record.cf_less_than_year_percent < 0 or record.cf_less_than_year_percent > 100.00)):
                raise ValidationError("Carry Forward Percentage should be between 0-100% .")

            if record.carry_forward and record.encashable:
                if not ((record.encashable_percentage + record.carry_forward_percentage) == 100):
                    raise ValidationError("The sum of encashable percentage and carry forward percent applicable for >1 year sevice employees should be equal to 100% .")  
                if (record.cf_less_than_year_percent + record.en_less_than_year_percent) > 100 :
                    raise ValidationError("The sum of encashable percentage and carry forward percent should not exceed 100% .")  

    @api.constrains('carry_forward_lapsed', 'carry_forward')
    def check_carry_forward_lapsed(self):
        for record in self:
            if record.carry_forward == True:
                if record.carry_forward_lapsed >= 365 or record.carry_forward_lapsed < 1:
                    raise ValidationError("Carry forward accumulation days should be between 1-365.")

    @api.onchange('carry_forward')
    def onchange_carry_forward(self):
        if self.carry_forward == False:
            self.carry_forward_percentage   = 0.00
            self.cf_less_than_year_percent  = 0.00
            self.carry_forward_lapsed       = 0

    @api.onchange('encashable')
    def onchange_encashable(self):
        if self.encashable == False:
            self.encashable_percentage      = 0.00
            self.en_less_than_year_percent  = 0.00

    @api.constrains('leave_code')
    def check_code(self):
        for record in self:
            if not re.match("^[0-9a-zA-Z_]+$", str(record.leave_code)) != None:
                raise ValidationError("Only alphanumeric characters and underscore allowed.")   
    
    @api.constrains('is_comp_off')
    def _validate_compoff(self):
        for record in self:
            existing_records = self.env['hr.leave.type'].search([('is_comp_off','=',True)]) - record
            if existing_records and record.is_comp_off:
                raise ValidationError("A Comp Off leave type is already exist !")  
    
    @api.constrains('employement_type_ids')
    def _validate_employement_type_ids(self):
        for record in self:
            if not record.employement_type_ids:
                raise ValidationError("Applicable For list can't be left blank !")

    """Overriding the existing method of hr.leave.type"""
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.parent_leave_id:
                res.append((record.id, "{} ({})".format(record.name, record.parent_leave_id.name)))
            else:
                res.append((record.id, record.name))
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        ctx = self._context
        if 'order_display' in ctx:
            order = ctx['order_display']
        return super(KwLeaveType, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def _get_remaining_leave(self,employees,leave_type):
        result = []
        if employees and leave_type:
            for employee_id in employees:
                status_dict = {}
                status_dict.update({'employee_id':employee_id,
                'remaining_leave':leave_type.with_context(employee_id=employee_id).remaining_leaves})
                result.append(status_dict)
        return result
    
    def _get_contextual_leave_cyle_id(self):
        leave_cycle_id,cycle_period = None,None
        if 'leave_cycle_id' in self._context:
            leave_cycle_id = self._context['leave_cycle_id']
        if 'cycle_period' in self._context:
            cycle_period = self._context['cycle_period']
        return leave_cycle_id,cycle_period

    @api.multi
    def _compute_leaves(self):
        data_days = {}
        employee_id = self._get_contextual_employee_id()
        leave_cycle_id,cycle_period = self._get_contextual_leave_cyle_id()

        if employee_id:
            data_days = self.get_days(employee_id,leave_cycle_id,cycle_period)

        for holiday_status in self:
            result = data_days.get(holiday_status.id, {})
            holiday_status.max_leaves = result.get('max_leaves', 0)
            holiday_status.leaves_taken = result.get('leaves_taken', 0)
            holiday_status.remaining_leaves = result.get('remaining_leaves', 0)
            holiday_status.virtual_remaining_leaves = result.get('virtual_remaining_leaves', 0)

    @api.multi
    def get_days(self, employee_id,leave_cyle_id,cycle_period):
        # print(employee_id,leave_cyle_id)
        # need to use `dict` constructor to create a dict per id
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in self.ids)
        domain = [('employee_id', '=', employee_id),('state', 'in', ['confirm', 'validate1', 'validate']),('holiday_status_id', 'in', self.ids)]
        if leave_cyle_id != None:
            domain += [('leave_cycle_id','=',leave_cyle_id)]
        if cycle_period != None:
            domain += [('cycle_period','=',cycle_period)]

        requests = self.env['hr.leave'].search(domain)
        allocations = self.env['hr.leave.allocation'].search(domain)
        max_allocations = self.env['hr.leave.allocation'].search(domain)
        # print("allocations",allocations)

        for request in requests:
            status_dict = result[request.holiday_status_id.id]
            status_dict['virtual_remaining_leaves'] -= (request.number_of_hours_display
                                                    if request.leave_type_request_unit == 'hour'
                                                    else request.number_of_days)
            if request.state == 'validate':
                status_dict['leaves_taken'] += (request.number_of_hours_display
                                            if request.leave_type_request_unit == 'hour'
                                            else request.number_of_days)
                status_dict['remaining_leaves'] -= (request.number_of_hours_display
                                                if request.leave_type_request_unit == 'hour'
                                                else request.number_of_days)

        for allocation in allocations.sudo():
            status_dict = result[allocation.holiday_status_id.id]
            if allocation.state == 'validate':
                # note: add only validated allocation even for the virtual
                # count; otherwise pending then refused allocation allow
                # the employee to create more leaves than possible
                status_dict['virtual_remaining_leaves'] += (allocation.number_of_hours_display
                                                          if allocation.type_request_unit == 'hour'
                                                          else allocation.number_of_days)
                status_dict['remaining_leaves'] += (allocation.number_of_hours_display
                                                  if allocation.type_request_unit == 'hour'
                                                  else allocation.number_of_days)


        for leave in max_allocations:
            status_dict = result[leave.holiday_status_id.id]
            if leave.state == 'validate':
                status_dict['max_leaves'] += (leave.number_of_hours_display
                                            if leave.type_request_unit == 'hour'
                                            else leave.number_of_days)

        return result