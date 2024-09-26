# Copyright 2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re
from datetime import date,datetime,time

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError


class HrHolidaysPublic(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _rec_name = 'year'
    _order = 'year desc'

    display_name    = fields.Char('Name', compute='_compute_display_name', store=True,)
    year            = fields.Integer('Calendar Year', required=True, default=date.today().year,)
    line_ids        = fields.One2many('hr.holidays.public.line', 'year_id', 'Holiday Dates',required=True)
    country_id      = fields.Many2one('res.country', 'Country')
    holiday_assign_type = fields.Selection([('csm_holiday','CSM Holiday'),('onsite_holiday','Onsite Holiday')],string="Holiday Type")

    @api.multi
    @api.constrains('year','line_ids')
    def _check_year(self):
        for line in self:
            # if not line.line_ids:
            #     raise ValidationError("Please Fill up Public holiday details.")
            line._check_year_one()

    def _check_year_one(self):
        if self.search_count([('year', '=', self.year), ('id', '!=', self.id),('holiday_assign_type','=',self.holiday_assign_type)]):
            
            raise ValidationError(_(
                'You can\'t create duplicate public holiday per year.'
            ))  # ('country_id', '=', self.country_id.id),
        return True

    @api.multi
    @api.depends('year')
    def _compute_display_name(self):
        for line in self:
            if line.year:
                line.display_name = line.year

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.display_name))
        return result

    @api.model
    @api.returns('hr.holidays.public.line')
    def get_holidays_list(self, year, employee_id=None,shift_id=None,branch_id=None):
        
        """
        Returns recordset of hr.holidays.public.line
        for the specified year and employee
        :param year: year as string
        :param employee_id: ID of the employee
        :return: recordset of hr.holidays.public.line
        """
        # print(shift_id)
        shift = self.env['resource.calendar'].browse(shift_id)
        pholidays       = self.search([('year', '=', year)])
        if not pholidays:
            return self.env['hr.holidays.public.line']


        employee        = False
        if employee_id:
            employee    = self.env['hr.employee'].browse(employee_id)

        states_filter   = [('year_id', 'in', pholidays.ids)]

        ##add by T Ketaki Debadarshini , for getting fixed holidays
        # if not optional_holiday:
        #     states_filter.append(('optional_holiday', '=', False))

        hhplo           = self.env['hr.holidays.public.line']
        if employee and (branch_id or ((employee.resource_calendar_id and employee.resource_calendar_id.branch_id) or (employee.user_id and employee.user_id.branch_id))):
            ##get holidays belong to the employee shift branch
            if not branch_id:
                branch_id   = employee.resource_calendar_id.branch_id.id if employee.resource_calendar_id.branch_id else employee.user_id.branch_id.id
            if shift.onsite_shift == True:
                states_filter += [('shift_ids','=',shift_id),('year_id.holiday_assign_type', '=','onsite_holiday')]
            else:
                states_filter += ['|',('shift_ids','=',shift_id),('branch_ids', '=',branch_id)]

            holidays_lines  = hhplo.search(states_filter)     
            return holidays_lines      
            
        else:
            # states_filter.append(('branch_ids', '=', False))
            return hhplo
            
        

    @api.model
    def is_public_holiday(self, selected_date, employee_id=None):
        """
        Returns True if selected_date is a public holiday for the employee
        :param selected_date: datetime object
        :param employee_id: ID of the employee
        :return: bool
        """
        holidays_lines  = self.get_holidays_list(selected_date.year, employee_id=employee_id)
        if holidays_lines:
            hol_date    = holidays_lines.filtered(lambda r: r.date == selected_date) # and not r.optional_holiday
            if hol_date.ids:
                return True
        return False


class HrHolidaysPublicLine(models.Model):
    _name           = 'hr.holidays.public.line'
    _description    = 'Public Holidays Lines'
    _order          = 'date, name desc'

    name            = fields.Char('Name', required=True, )
    date            = fields.Date('Date', required=True,autocomplete="off")
    year_id         = fields.Many2one('hr.holidays.public','Calendar Year',required=True,ondelete='cascade',)
    variable_date   = fields.Boolean('Date may change', oldname='variable', default=True, )
    branch_ids      = fields.Many2many('kw_res_branch', 'hr_holiday_public_branch_rel','line_id','branch_id',string='Branch/SBU')
    shift_ids       = fields.Many2many('resource.calendar','hr_holiday_public_shift_rel','line_id','shift_id',string="Shifts")
    # optional_holiday    = fields.Boolean('Optional Holiday', default=False, )
    # meeting_id = fields.Many2one('calendar.event', string='Meeting')

    @api.constrains('name')
    def holiday_name_validation(self):
        for record in self:
            if not (re.match('^[ a-zA-Z0-9()-]+$',record.name)):
                raise ValidationError("Special Characters are not allowed.")

    @api.multi
    @api.constrains('date', 'branch_ids')
    def _check_date_branch(self):
        for line in self:
            line._check_date_branch_one()

    def _check_date_branch_one(self):
        if self.date.year != self.year_id.year:
            raise ValidationError(_(
                'Dates of holidays should be the same year as the calendar'
                ' year they are being assigned to'
            ))

        if self.branch_ids:
            domain = [
                ('date', '=', self.date),
                ('year_id', '=', self.year_id.id),
                ('branch_ids', '!=', False),
                ('id', '!=', self.id),
            ]
            holidays = self.search(domain)

            for holiday in holidays:
                if self.branch_ids & holiday.branch_ids:
                    raise ValidationError(_(
                        'You can\'t create duplicate public holiday per date'
                        ' %s and one of the branches.'
                    ) % self.date)
        domain = [('date', '=', self.date),
                  ('year_id', '=', self.year_id.id),
                  ('branch_ids', '=', False),('shift_ids','in',self.shift_ids.ids)]
        if self.search_count(domain) > 1:
            raise ValidationError(_(
                'You can\'t create duplicate public holiday per date %s.'
            ) % self.date)
        return True

    
    @api.model
    def create(self, values):
        res = super().create(values)
    
        return res
    
   
    