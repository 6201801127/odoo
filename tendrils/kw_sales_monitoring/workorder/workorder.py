from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api , _
from odoo import http
from odoo.exceptions import UserError, ValidationError, Warning
import base64
import io
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.kw_utility_tools import kw_validations

class SalesWorkorder(models.Model):
    _name = 'sales.workorder'
    _description = 'Workorders'
    _rec_name = 'code'

    def _get_nodal_officers(self):
        return [('parent_id','=',self.partner_id.id)] 

    company_id = fields.Many2one('res.company', string='Company/Subsidiary')
    partner_id = fields.Many2one('res.partner',string='PartnerClient Name', domain="[('parent_id','=',False),'|',('is_partner', '=', True),('customer', '=', True)]")
    country_id = fields.Many2one('res.country', string="Country Name")
    state_id = fields.Many2one('res.country.state',string="State anf UT")
    project_id = fields.Many2one('project.project', string="Project Name")
    sub_category_id = fields.Many2one('kw_lead_category_master',string="Sub Category" )
    order_name = fields.Char(string='Order Name')
    order_reference_no = fields.Char(string='Order Reference No.')
    order_date = fields.Date(string='Order Date')
    procurement_mode = fields.Many2one('procurement_master', string='Procurement Mode')
    order_value = fields.Float(string='Order Value (Excluding Tax)')
    order_exempted_tax = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Order Exempted From Tax?')
    delivery_location = fields.Many2one('res.country.state', string='Delivery Location')
    contract_start_date = fields.Date(string='Contract Start Date')
    contract_end_date = fields.Date(string='Contract End Date')
    workorder_comp_id = fields.One2many('workorder.component', 'workorder_id', 'Components of Workorder')
    nodal_officer_id  = fields.Many2one('res.partner',string = "Select Name",domain =_get_nodal_officers)
    nodal_officer_name = fields.Char(related='nodal_officer_id.name',string="Enter Name" ,store=True)
    nodal_officer_designation = fields.Char(related='nodal_officer_id.contact_designation',string="Designation" ,store=True)
    nodal_officer_mobile_no = fields.Char(related='nodal_officer_id.phone',string="Mobile Number",store=True)
    nodal_officer_email_address = fields.Char(related='nodal_officer_id.email',string="Email Address",store=True)
    user_officer_id  = fields.Many2one('res.partner',string = "Select Name",domain =_get_nodal_officers)
    user_officer_name = fields.Char(related='user_officer_id.name',string="Enter Name" ,store=True)
    user_officer_designation = fields.Char(related='user_officer_id.contact_designation',string="Designation" ,store=True)
    user_officer_mobile_no = fields.Char(related='user_officer_id.phone',string="Mobile Number",store=True)
    user_officer_email_address = fields.Char(related='user_officer_id.email',string="Email Address",store=True)
    document_ids = fields.One2many('lead_document_details','document_details_id',string = "Document Details")
    account_holder_id = fields.Many2one('hr.employee',string="Name")
    department_id = fields.Many2one('hr.department', string='Department',
                                  domain=[('dept_type.code', '=', 'department')],
                                  default=lambda self: self.env.user.employee_ids.department_id.id)
    division_id = fields.Many2one('hr.department', string="Division", 
                                    domain="[('parent_id','=',department_id)]",
                                    default=lambda self: self.env.user.employee_ids.division)
    section_id = fields.Many2one('hr.department',string='Section',
                                    domain="[('parent_id','=',division_id)]",
                                    default=lambda self: self.env.user.employee_ids.practise)
    sbu_id = fields.Many2one('kw_sbu_master',string = "SBU",domain=[('type','=','sbu')])
    code = fields.Char('Workorder Code')
    eq_id = fields.Many2one('kw_eq_estimation', string="EQ")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.nodal_officer_id = False
        if self.partner_id:
            self.nodal_officer_id = False
            self.nodal_officer_name = False
            self.nodal_officer_designation = False
            self.nodal_officer_mobile_no = False
            self.nodal_officer_email_address = False
    
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            current_year = datetime.now().year
            year_suffix = str(current_year)[-2:]
            fiscal_year = 'FY{}'.format(year_suffix)
            sequence = self.env['ir.sequence'].next_by_code('sales.workorder.code')
            vals['code'] = '{}{}'.format(sequence, fiscal_year)
        return super(SalesWorkorder, self).create(vals)
    

class WorkorderComponents(models.Model):
    _name = 'workorder.component'
    _description = 'Component of Workorder'

    s_no = fields.Integer(String='Sl#')
    hsn_code = fields.Char(string='HSN/SAC Code')
    group_id = fields.Many2one('account.group', string='Group')
    account_head_id = fields.Many2one('account.group', string='Account Head')
    account_subhead_id = fields.Many2one('account.group', string='Account Sub-Head')
    price_unit = fields.Float(string='Value')
    workorder_id = fields.Many2one('sales.workorder', string='Workorder')

