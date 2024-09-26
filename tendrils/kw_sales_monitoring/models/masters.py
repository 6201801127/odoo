
from odoo import models, fields, api

class TdEvalutionMethod(models.Model):
    _name = 'evalution_method_master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)


    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code already exist.'),
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]

class TdFundingAgencyMaster(models.Model):
    _name = 'funding_agency_master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)


    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code already exist.'),
        ('name_uniq', 'unique(name)', 'Name already exist.'),

    ]



class ProcurementMaster(models.Model):
    _name = 'procurement_master'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)


    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code already exist.'),
        ('name_uniq', 'unique(name)', 'Name already exist.'),

    ]

class QuestionMaster(models.Model):
    _name = "question_master"
    _rec_name = "question_name"

    question_name = fields.Char(string='Question')

class ValueMaster(models.Model):
    _name = "value_master"
    _rec_name = "value_name"

    value_name = fields.Char(string='Value')
    marks = fields.Float(string='Marks')

class QuestionStatus(models.Model):
    _name="question_status"
    _description = 'Question Status'

    question_id = fields.Many2one('question_master',string="Criteria")
    current_value_id = fields.Many2many('value_master','criteria_value_rel', 'question_id', 'value_id',string="Current Value")

class RequestForServiceMaster(models.Model):
    _name = 'request_for_service_master'
    _description = 'Request For Service Master'
    _rec_name = 'item'

    department_id = fields.Many2many('hr.department',string="Department",domain=[('dept_type.code','=','department')])
    item = fields.Char(string="Item")

class DomainOfferingServices(models.Model):
    _name = 'domain_offering_service_line'
    _description = 'Domain Offering/ Services/ Solutions'
    _rec_name = 'name'

    line_of_business_id = fields.Selection([('domain_offering','Domain Offering'),('services','Services')], string="Line Of Business")
    type = fields.Selection([('domain_service','Domain Offering/ Service Line'),('solution_service','Solutions/ Service')], string="Type")
    name = fields.Char(string="Name")
    parent_id = fields.Many2one('domain_offering_service_line',string="Parent")

class LeadCriteriaRel(models.Model):
    _name = 'lead_criteria_master'
    _description = 'Lead Criteria Master'
    _rec_name = 'question_id'

    parent_id = fields.Many2one('crm.lead',string="Lead")
    question_id = fields.Many2one('question_master')




    