# *******************************************************************************************************************
#  File Name             :   tour_details.py
#  Description           :   This is a master model 
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   14-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
import re
from odoo import models, fields, api
from datetime import datetime, date
import dateutil.parser
from odoo.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta



class Tourdetails(models.Model):
    _name = "bsscl.tour.details"
    _description = "Tour Details Model"
    _rec_name ='tour_type'

    tour_id = fields.Many2one(comodel_name="bsscl.tour",string="Tour / यात्रा")
    settlement_id = fields.Many2one(comodel_name="tour.settlement",string="Eettlement")
    tour_type = fields.Selection(string="Type / प्रकार", required=False,
                                 selection=[('Domestic', 'Domestic / घरेलू'), ('International', 'International / अंतरराष्ट्रीय')])
    from_date = fields.Date(string="From Date / तिथि से", required=True, )
    from_country_id = fields.Many2one(comodel_name='res.country', string="From Country / देश से")
    from_state_id = fields.Many2one(comodel_name='res.country.state', string="From State / राज्य से", required=True, )
    from_city = fields.Char(string="From City / शहर से")
    to_date = fields.Date(string="To Date / तारीख तक", required=True, )
    number_of_days = fields.Char(string='Number Of Days / दिनों की संख्या', compute='_compute_number_of_days',  store=True)
    to_country_id = fields.Many2one(comodel_name='res.country', string="To Country / देश को")
    to_state_id = fields.Many2one(comodel_name='res.country.state', string="To State / राज्य को", required=True, )
    to_city = fields.Char(string=" To City / शहर को")

# ***********************************ALL Compute methods **************************************************
    @api.depends('from_date','to_date')
    def _compute_number_of_days(self):
        if self.to_date:
            deff_day = (self.to_date - self.from_date).days
            self.number_of_days = deff_day
        else:
            pass
# ********************************************** End ****************************************************
    
# ***************************************All Onchange methods **********************************************
    @api.onchange('from_country_id')
    def _onchange_from_country_id(self):
        for rec in self:
            if rec.from_country_id:
                state = {'domain':{'from_state_id':[('country_id','=',rec.from_country_id.id)]}}
                return state
            if not rec.from_country_id:
                states = {'domain':{'from_state_id':['|',('country_id','=',rec.from_country_id.id),('country_id','!=',rec.from_country_id.id)]}}
                return states

    @api.onchange('to_country_id')
    def _onchange_to_country_id(self):
        for rec in self:
            if rec.to_country_id:
                country_state = {'domain':{'to_state_id':[('country_id','=',rec.to_country_id.id)]}}
                return country_state
            if not rec.to_country_id:
                country_states = {'domain':{'to_state_id':['|',('country_id','=',rec.to_country_id.id),('country_id','!=',rec.to_country_id.id)]}}
                return country_states            
    # @api.constrains('from_state_id','to_state_id')
    # @api.onchange('from_state_id','to_state_id')
    # def _onchnage_tour_details_ids(self):
    #     if not self.from_country_id and self.from_state_id:
    #         raise ValidationError("Please select from country first than select from state")
    #     if not self.to_country_id and self.to_state_id:
    #         raise ValidationError("Please select to country first than select to state")
        
    @api.constrains('from_date','to_date')
    @api.onchange('from_date','to_date')
    def _onchnage_travel_date(self):
        if self.from_date:
            if self.from_date <= date.today():
                raise ValidationError("From date should not past date or today date...please select future date!")
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError("Please select correct from date to date")
            
        if self.to_date and not self.from_date:
            raise ValidationError("Please select from date first than select to date ")
            
        # if not self.from_date:
        #     raise ValidationError("Please select to country first than select to state")
# ********************************************** End ****************************************************
        