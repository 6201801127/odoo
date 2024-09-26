# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class EqCashflowConfig(models.Model):
    _name = 'kw_eq_cashflow_config'
    _description = 'Cash Flow'

    cap_year_id = fields.Many2one('kw_eq_estimation')
    op_year_id = fields.Many2one('kw_eq_estimation')
    revision_op_id = fields.Many2one('kw_eq_revision')
    revision_cap_id = fields.Many2one('kw_eq_revision')
    opening_balance = fields.Float(string="Opening Balance")
    time_line = fields.Char(string='Time Line')
    capyear_replica_id = fields.Many2one('kw_eq_replica')
    opyear_replica_id = fields.Many2one('kw_eq_replica')
    total_inflow = fields.Float (string="Total Inflow")
    deliverables = fields.Char(string='Deliverables')
    month = fields.Char(string="Month")
    inception = fields.Char(string='Milestone 1',digits=dp.get_precision('eq'))
    srs = fields.Char(string='Milestone 2',digits=dp.get_precision('eq'))
    uat = fields.Char(string='Milestone 3',digits=dp.get_precision('eq'))
    golive = fields.Char(string='Milestone 4',digits=dp.get_precision('eq'))
    delivery = fields.Char(string='Milestone 5',digits=dp.get_precision('eq'))
    o_and_m = fields.Char(string='Milestone 6',digits=dp.get_precision('eq'))
    milestone7 = fields.Char(string='Milestone 7',digits=dp.get_precision('eq'))
    milestone8 = fields.Char(string='Milestone 8',digits=dp.get_precision('eq'))
    milestone9 = fields.Char(string='Milestone 9',digits=dp.get_precision('eq'))
    milestone10 = fields.Char(string='Milestone 10',digits=dp.get_precision('eq'))
    milestone11 = fields.Char(string='Milestone 11',digits=dp.get_precision('eq'))
    milestone12 = fields.Char(string='Milestone 12',digits=dp.get_precision('eq'))

    resource_internal = fields.Float(string="Resource Internal")
    resource_external = fields.Float(string="Resource External")
    it_infra = fields.Float(string="IT Infra",digits=dp.get_precision('eq'))
    ancillary = fields.Float(string="Ancillary")
    coh = fields.Float(string="COH")
    others = fields.Float(string="Others",digits=dp.get_precision('eq'))
    total_outflow = fields.Float(string="Total Outflow")
    closing_balance = fields.Float(string="Closing Balance")
    cap_closure_bool = fields.Boolean(compute = "get_closure_value")
    deliverable_bool = fields.Boolean(compute="make_deliverable_readonly")
    


    @api.depends('cap_year_id','op_year_id')
    def get_closure_value(self):
        for record in self:
            if record.time_line == "CAP Closure":
                record.cap_closure_bool = True
            elif record.time_line == "Project Closure":
                record.cap_closure_bool = True
            elif record.time_line == "Opex Closure":
                record.cap_closure_bool = True
            else:
                record.cap_closure_bool = False
   

    @api.depends('cap_year_id')
    def make_deliverable_readonly(self):
        for record in self:
            if record.time_line == "Deliverables" or record.time_line ==  'Payment term %':
                record.deliverable_bool = True

    @api.onchange('inception', 'srs', 'uat', 'golive', 'delivery', 'o_and_m', 
                    'milestone7', 'milestone8', 'milestone9', 'milestone10', 
                    'milestone11', 'milestone12', 'time_line')
    def get_valid_value(self):
        for record in self:
            if record.time_line not in ('Deliverables', 'Payment term %'):
                fields_to_check = ['inception', 'srs', 'uat', 'golive', 
                                'delivery', 'o_and_m', 'milestone7', 
                                'milestone8', 'milestone9', 'milestone10', 
                                'milestone11', 'milestone12']
                for field in fields_to_check:
                    value = getattr(record, field)
                    if value:
                        try:
                            float(value)
                        except ValueError:
                            raise ValidationError('Kindly enter numerical values!')




            

class deliverableConfig(models.Model):
    _name = 'kw_eq_deliverable_config'
    _description = 'Deliverable Details'

    deliverable_id = fields.Many2one('kw_eq_estimation')
    revision_deliverable_id = fields.Many2one('kw_eq_revision')
    deliverable_replica_id = fields.Many2one('kw_eq_replica')
    deliverables = fields.Char()
    payment_term = fields.Float(string='Payment Term %')
    month = fields.Char(string='Month')
    milestones = fields.Char(string='Milestones')

    @api.constrains('payment_term')
    def validate_oppertunity(self):
        if self.payment_term > 100:
            raise ValidationError("Payment Term percentage can't be greater than 100.")


class quoteConfig(models.Model):
    _name = 'kw_eq_quote_config'
    _description = 'Quote Details'

    quote_id = fields.Many2one('kw_eq_estimation')
    revision_quote_id = fields.Many2one('kw_eq_revision')
    quote_replica_id = fields.Many2one('kw_eq_replica')
    paticulars = fields.Char(string="Particulars")
    amount = fields.Float(string="Amount")

