# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api , _
from odoo import http
from odoo.exceptions import UserError, ValidationError, Warning
import base64
import io
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.kw_utility_tools import kw_validations

class kwSalesCrmInherit(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead','portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def _get_nodal_officers(self):
        return [('parent_id','=',self.partner_id.id)] 

    code = fields.Char('Code',default="New")
    partner_id = fields.Many2one('res.partner',string='Partner', domain="[('parent_id','=',False),'|',('is_partner', '=', True),('customer', '=', True)]")
    client_type = fields.Selection(related='partner_id.incorporation_type', string="Client Type")
    tender_type_id = fields.Many2one('kw_crm_tender_type_master',string = "Tender Type")
    evalution_method_id = fields.Many2one('kw_crm_financial_evaluation_master',string = "Evaluation Method ")
    funding_agenecy_id = fields.Many2one('funding_agency_master',string = "Funding Agency")
    is_ref_tor_eoi_published = fields.Selection(stirng = "Is the RFP/TOR/EOI published? " , selection=[('yes', 'Yes'), ('no', 'No')])
    approximate_delivery_timeline = fields.Float(string = "Approximate delivery timeline (Month)")
    project_detail_ids = fields.One2many('project_details','crm_id', string = "Project Details")
    high_level_scope_summary = fields.Text('High Level Scope Summary')
    procurement_id = fields.Many2one('procurement_master',string ="Mode Of Procurement")
    estimate_lead_value = fields.Float(string = "Estimated Lead Value")
    # code = fields.Char(string = "Lead Code")
    lead_currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]))
    exchange_rate_to_inr = fields.Float(string='Exchange Rate To INR' , default=1.0)
    value_in_inr = fields.Float(string='Value In INR' , store=True, compute='_compute_value_in_inr')
    publising_date = fields.Date(string = "Publising Date")
    pre_bid_time = fields.Selection(string='Pre-Bid Meeting Time', selection='_get_pre_bid_time_list')
    submission_datetime = fields.Date(string = "Submission Date & Time ")
    document_ids = fields.One2many('lead_document_details','document_details_id',string = "Document Details")
    technology_ids = fields.Many2many('kw_partner_tech_service_master',domain=[('type','=','2')])
    developmen_is_required = fields.Selection(string='Development is required ?',selection=[('onsite', 'On-Site'), ('offside', 'Off-Site'),('combined', 'Combined')])
    tender_piblising_date = fields.Date(string = "Tender Publishing Date")
    department_id = fields.Many2one('hr.department', string='Department',
                                  domain=[('dept_type.code', '=', 'department')],
                                  default=lambda self: self.env.user.employee_ids.department_id.id)
    division_id = fields.Many2one('hr.department', string="Division", 
                                    domain="[('parent_id','=',department_id)]",
                                    default=lambda self: self.env.user.employee_ids.division)
    section_id = fields.Many2one('hr.department',string='Section',
                                    domain="[('parent_id','=',division_id)]",
                                    default=lambda self: self.env.user.employee_ids.practise)
    account_holder_id = fields.Many2one('hr.employee',string="Name")
    category_id = fields.Many2one('kw_lead_category_master',string ="Category")
    sub_category_id = fields.Many2one('sub_category_master',string="Sub Category" )
    revenue_breakup_a = fields.Float(string = " A : Software Development,Operation and Maintenance,Consultancy ")
    revenue_breakup_b = fields.Float(string = " B : Resource Deployment ")
    revenue_breakup_c = fields.Float(string = " C : Ancillary Services ")
    revenue_breakup_d = fields.Float(string = " D : Implementation,Supply,Maintenance ")
    nodal_officer_id  = fields.Many2one('res.partner',string = "Select Name",domain =_get_nodal_officers)
    nodal_officer_name = fields.Char(related='nodal_officer_id.name',string="Enter Name" ,store=True)
    nodal_officer_designation = fields.Char(related='nodal_officer_id.contact_designation',string="Designation" ,store=True)
    nodal_officer_mobile_no = fields.Char(related='nodal_officer_id.phone',string="Mobile Number",store=True)
    nodal_officer_email_address = fields.Char(related='nodal_officer_id.email',string="Email Address",store=True)
    opportunity_value = fields.Float(string = " Opportunity Value")
    tentative_order_date =fields.Date(string ="Tentative Order Date")
    order_exempted_from_tax = fields.Selection(string='Order Exempted From Tax?', selection=[('yes', 'Yes'), ('no', 'No')])
    contract_start_date = fields.Date(string = "Contract Start Date")
    contract_end_date = fields.Date(string = "Contract End Date")
    wo_plan_date = fields.Date(string = "WO Plan Date")
    lac_applied_on = fields.Datetime(string="LAC Applied On")
    lac_decision_on = fields.Date(string="LAC Decision On")
    lead_created_on = fields.Date(string = "Lead Created On")
    pac_apply_date = fields.Date(string = "PAC Apply Date")
    remark = fields.Text(string = "Remark")
    lac_remarks = fields.Text(string = "Remark")
    order_ref_no = fields.Char(string = "Order Reference No.")
    stage_name = fields.Char(releated="stage_id.code")
    drop_lead_bool = fields.Boolean(string ="Drop Lead bool")
    apply_lac_bool = fields.Boolean(string ="Apply Lac Bool")
    # procurement_bool = fields.Boolean(string = "Procurement Bool")
    pac_approve_remark = fields.Text(string = "Remark")
    lead_remarks = fields.Text(string="Drop Reason")
    csg_head_dept_id =fields.Many2one('hr.department',string = "CSG Head")
    csg_member_id =fields.Many2one('hr.employee',string = "CSG Member")
    sbu_id = fields.Many2one('kw_sbu_master',string = "Tag SBU",domain=[('type','=','sbu')])
    risk_analysis_document = fields.Binary(string='Risk Analysis Document', attachment=True)
    risk_doc_filename = fields.Char(string='Risk Analysis Document')
    question_master_ids = fields.One2many('lead_criteria_master','parent_id',string="Criteria Details")
    operation_team_member = fields.Many2one('hr.employee', string='Operations Team Member')
    is_pm_assigned = fields.Boolean(string="Is PM Assigned", compute='_compute_is_pm_assigned')
    is_operations_manager_assigned = fields.Boolean(string="Is Operations Manager Assigned", compute='_compute_is_operations_manager_assigned')
    
    @api.depends('pm_id')
    def _compute_is_pm_assigned(self):
        for record in self:
            record.is_pm_assigned = bool(record.pm_id)
            # print("kjjjjjjjjjjjjjjjjjjjjjjjjj", record.is_pm_assigned)
    
    # Compute method to check if Operations Manager is assigned
    @api.depends('operation_team_member')
    def _compute_is_operations_manager_assigned(self):
        for record in self:
            record.is_operations_manager_assigned = bool(record.operation_team_member)
            # print("kjjjjjjjjjjjjjjjjjjjjjjjjj", record.is_pm_assigned)


    def _get_departments(self):
        department_ids = self.env['request_for_service_master'].search([]).mapped('department_id')
        return [('id','in',department_ids.ids)]

    request_department_id = fields.Many2one('hr.department',domain=_get_departments,string="Department")
    request_service_id = fields.Many2one('request_for_service_master',string="Service",)

    @api.onchange('request_department_id')
    def _get_service_requests(self):
        service_request_id = self.env['request_for_service_master'].search([('department_id','in',[self.request_department_id.id])])
        self.request_service_id = False
        return {'domain': {'request_service_id': [('id', 'in',service_request_id.ids)]}}


    @api.model
    def get_empty_list_help(self, help):
        help_title = _('No Records Found.')
        # alias_record = self.env['mail.alias'].search([
        #     ('alias_name', '!=', False),
        #     ('alias_name', '!=', ''),
        #     ('alias_model_id.model', '=', 'crm.lead'),
        #     ('alias_parent_model_id.model', '=', 'crm.team'),
        #     ('alias_force_thread_id', '=', False)
        # ], limit=1)
        # if alias_record and alias_record.alias_domain and alias_record.alias_name:
        #     email = '%s@%s' % (alias_record.alias_name, alias_record.alias_domain)
        #     email_link = "<a href='mailto:%s'>%s</a>" % (email, email)
        #     sub_title = _('or send an email to %s') % (email_link)
        return '<p class="o_view_nocontent_smiling_face">%s</p>' % (help_title)
        
    @api.constrains('risk_analysis_document')
    def validate_upload_file(self):
        max_file_size_mb = 2.0
        allowed_file_list = ['application/pdf',
                             'application/msword',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']   
        for record in self:
            if record.risk_analysis_document:
                mimetype = guess_mimetype(base64.b64decode(record.risk_analysis_document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError(_("Unsupported file format ! allowed file formats are .pdf and .doc "))
                elif ((len(record.risk_analysis_document) * 3 / 4) / 1024) / 1024 > max_file_size_mb:
                        raise ValidationError(_("Maximum file size should be less than {} MB.".format(max_file_size_mb)))
                kw_validations.validate_file_mimetype(record.risk_analysis_document, allowed_file_list)
                kw_validations.validate_file_size(record.risk_analysis_document, 2)
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record.ensure_one()
            if record.code:
                if self._context.get('by_crm_code'):
                    record_name = str(record.code)
                else:
                    record_name = str(record.code) + ' | ' + str(record.name)
            else:
                record_name = str(record.name)
            result.append((record.id, record_name))
        return result

    @api.model
    def create(self, vals):
        res = super(kwSalesCrmInherit, self).create(vals)
        # print(vals)
        if vals.get('code','New') == 'New':
            # print("after", vals)
            if self.env.user.has_group('kw_sales_monitoring.group_sm_sales'):
                res.code = self.env['ir.sequence'].next_by_code('ops_sales') or 'New'
            elif self.env.user.has_group('kw_sales_monitoring.group_sm_marketing'):
                res.code = self.env['ir.sequence'].next_by_code('opm_marketing') or 'New'
            elif self.env.user.has_group('kw_sales_monitoring.group_sm_business_development'):
                res.code = self.env['ir.sequence'].next_by_code('opb_buisness') or 'New'
            elif self.env.user.has_group('kw_sales_monitoring.group_sm_sbu'):
                res.code = self.env['ir.sequence'].next_by_code('opp_sbu') or 'New'
            # print(res.code)
        return res

    @api.model
    def _get_pre_bid_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=6, minute=0, second=0, microsecond=0)
        end_loop = start_loop + timedelta(days=1)

        time_list = []
        current_time = start_loop
        while current_time < end_loop:
            time_list.append((current_time.strftime('%H:%M:%S'), current_time.strftime('%I:%M %p')))
            current_time = current_time + relativedelta(minutes=+15)
        return time_list


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.nodal_officer_id = False
        if self.partner_id:
            self.nodal_officer_id = False
            self.nodal_officer_name = False
            self.nodal_officer_designation = False
            self.nodal_officer_mobile_no = False
            self.nodal_officer_email_address = False
       

    
    # @api.onchange('procurement_id')
    # def onchange_procurement_id(self):
    #     self.publising_date = False
    #     if self.procurement_id and self.procurement_id.code == 'ot':
    #         self.procurement_bool = True
    #     else:
    #         self.procurement_bool = False

    # @api.onchange('category_id')
    # def _onchange_category_id(self):
    #     self.sub_category_id = False
    #     if self.category_id:
    #         self.sub_category_id = False
    #         return {
    #             'domain': {
    #                 'sub_category_id': [('id', 'in', self.category_id.sub_category_ids.ids)]
    #             }
    #         }

    @api.constrains('revenue_breakup_a', 'revenue_breakup_b', 'revenue_breakup_c', 'revenue_breakup_d')
    def development_required_check(self):
        for record in self:
            total_revenue_breakup = (record.revenue_breakup_a + record.revenue_breakup_b +
                                        record.revenue_breakup_c + record.revenue_breakup_d)
            if total_revenue_breakup != 100:
                raise ValidationError("The sum of Revenue Breakup Category should be 100%.")
    
    @api.onchange('account_holder_id')
    def onchange_account_holder_id(self):
        if self.account_holder_id:
            self.department_id = self.account_holder_id.department_id.id
            self.division_id = self.account_holder_id.division.id
            self.section_id = self.account_holder_id.section.id

    def request_for_service(self):
        view_id = self.env.ref("kw_sales_monitoring.request_for_service_view").id
        action = {
            'name': 'Request For Service',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id, 
            'res_id': self.id,
            'target': 'new',
            'context': {'default_state_id': self.state_id.id,
                        'default_name':self.name,
                        'default_partner_id':self.partner_id.id}
        }
        return action


    def request_for_service_btn(self):
        presales_lead_group = self.env.ref('kw_sales_monitoring.group_presales_lead')
        
        if presales_lead_group and self.env.user in presales_lead_group.users:
            self.env['service_request'].sudo().create({
                'lead_name': self.name,
                'request_by_id': self.env.user.id,
                'request_department_id': self.request_department_id.id,
                'request_service_id': self.request_service_id.id,
                'request_date': datetime.now(),
            })
            self.env.user.notify_success("Service Request Created Successfully.")
       
    def apply_lac(self):
        self.ensure_one()  
        lac_applied_stage = self.env.ref('kw_sales_monitoring.stage_lead6').id
        action_id = self.env.ref('kw_sales_monitoring.lac_action_window').id
        
        # Update the lead stage and apply LAC
        self.write({'stage_id': lac_applied_stage, 'apply_lac_bool': True})

        # If the 'Risk Analysis Document' is not provided, show the form view
        if not self.risk_analysis_document:
            view_id = self.env.ref("kw_sales_monitoring.pickup_the_lead_view").id
            return {
                'name': 'Pick Up the Lead',
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'res_id': self.id,
            }
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }


    def re_assign(self):
        view_id = self.env.ref("kw_sales_monitoring.lead_reassign_view").id
        action = {
            'name': 'Lead Re_Assign',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id, 
            'res_id': self.id,
            'target': 'new',
            'context': {'default_state_id': self.state_id.id,
                        'default_name':self.name,
                        'default_partner_id':self.partner_id.id,
                        'default_source_id':self.source_id.id}
        }
        return action

    def drop_the_lead(self):
        view_id = self.env.ref("kw_sales_monitoring.drop_the_lead_view").id
        action = {
            'name': 'Drop The Lead',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'default_state_id': self.state_id.id,
                        'default_name':self.name,
                        'default_partner_id':self.partner_id.id}
        }
        return action

    def approve_lac(self):
        lac_approve_stage = self.env.ref('kw_sales_monitoring.stage_lead7').id
        action_id = self.env.ref('kw_sales_monitoring.qualified_lead_action_window').id
        
        if self.pm_id.sbu_master_id.name != self.sbu_id.name:
            view_id = self.env.ref("kw_sales_monitoring.kw_lac_approve_view").id
            return {
                'name': 'LAC Approve',
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'res_id': self.id,
            }
        if lac_approve_stage:
            self.write({'stage_id': lac_approve_stage})
        
        self.env.user.notify_success("LAC Approved Successfully.")
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }

    def drop_lac(self):
        drop_lac_stage = self.env.ref('kw_sales_monitoring.stage_lead9').id
        if drop_lac_stage:
            self.write({'stage_id': drop_lac_stage})

    def differ_lac(self):
        differ_lac_stage = self.env.ref('kw_sales_monitoring.stage_lead8').id
        if differ_lac_stage:
            self.write({'stage_id': differ_lac_stage})

    def pick_up_lead(self):
        self.ensure_one()  # Ensure that only one record is being processed
        
        lead_added_stage = self.env.ref('kw_sales_monitoring.stage_lead5').id
        action_id = self.env.ref('kw_sales_monitoring.cold_lead_action_window').id
        
        self.write({
            'stage_id': lead_added_stage,
            'account_holder_id': self.env.user.employee_ids.id,
            'department_id': self.env.user.employee_ids.department_id.id,
            'division_id': self.env.user.employee_ids.division.id,
            'section_id': self.env.user.employee_ids.section.id,
        })
        
        # If the 'Risk Analysis Document' is not provided, show the form view
        if not self.risk_analysis_document:
            view_id = self.env.ref("kw_sales_monitoring.pickup_the_lead_view").id
            return {
                'name': 'Pick Up the Lead',
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'res_id': self.id,
            }
        
        # If 'Risk Analysis Document' is provided, redirect to the action window
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }


    def redirect_warm_lead(self):
        self.ensure_one()  # Ensure that only one record is being processed
        lead_added_stage = self.env.ref('kw_sales_monitoring.stage_lead5').id
        action_id = self.env.ref('kw_sales_monitoring.warm_lead_action_window').id
       
        if lead_added_stage:
            self.write({'stage_id': lead_added_stage})
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }
    def redirect_qualified_lead(self):
        self.ensure_one() 
        lac_approve_stage = self.env.ref('kw_sales_monitoring.stage_lead7').id
        action_id = self.env.ref('kw_sales_monitoring.qualified_lead_action_window').id
        
        if lac_approve_stage:
            self.write({'stage_id': lac_approve_stage})
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }

    def drop_lead(self):
        self.ensure_one()
        lead_drop_stage = self.env.ref('kw_sales_monitoring.stage_lead10').id
        action_id = self.env.ref('kw_sales_monitoring.warm_lead_action_window').id

        self.write({'stage_id': lead_drop_stage,
                        'drop_lead_bool':True})
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }

    def apply_for_pac(self):
        self.ensure_one()
        pac_applied_stage = self.env.ref('kw_sales_monitoring.stage_lead13').id
        action_id = self.env.ref('kw_sales_monitoring.pac_action_window').id

        self.write({'stage_id': pac_applied_stage})
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }

    def pac_approve(self):
        self.ensure_one()
        pac_approve_stage = self.env.ref('kw_sales_monitoring.stage_lead14').id
        action_id = self.env.ref('kw_sales_monitoring.hot_lead_action_window').id

        self.write({'stage_id': pac_approve_stage})
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }
    def take_action_pac(self):
        view_id = self.env.ref("kw_sales_monitoring.pac_view_form").id
        action = {
            'name': 'PAC',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'current_id': self.id}
        }
        return action
    def take_action_lac(self):
        view_id = self.env.ref("kw_sales_monitoring.kw_lac_form_view_wizard").id
        action = {
            'name': 'Take LAC Decision',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'current_id': self.id}
        }
        return action
           
    
    def action_withdraw(self):
        lac_approve_stage = self.env.ref('kw_sales_monitoring.stage_lead7').id
        action_id = self.env.ref('kw_sales_monitoring.qualified_lead_action_window').id
        
        if lac_approve_stage:
            self.write({'stage_id': lac_approve_stage})
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=crm.lead&view_type=list',
            'target': 'self',
        }
    
    def action_update_hot_lead(self):
        return True

    @api.onchange('approximate_delivery_timeline')
    def _check_approximate_delivery_timeline(self):
        if self.approximate_delivery_timeline > 99:
            warning = {
                'title': "Value Exceeded",
                'message': "The approximate delivery timeline should not exceed 99 days.",
            }
            return {'warning': warning}
    
    @api.constrains('approximate_delivery_timeline')
    def _validate_approximate_delivery_timeline(self):
        for record in self:
            if record.approximate_delivery_timeline > 99:
                raise ValidationError(
                    "The approximate delivery timeline cannot be greater than 99."
                )

    @api.onchange('exchange_rate_to_inr', 'estimate_lead_value')
    def _onchange_exchange_rate_and_value(self):
        if self.exchange_rate_to_inr <= 0:
            return {
                'warning': {
                    'title': "Invalid Exchange Rate",
                    'message': "Exchange rate must be greater than 0. It has been reset to 1.",
                }
            }
        self.value_in_inr = self.estimate_lead_value * self.exchange_rate_to_inr
        
    @api.depends('estimate_lead_value', 'exchange_rate_to_inr')
    def _compute_value_in_inr(self):
        for record in self:
            record.value_in_inr = record.estimate_lead_value * record.exchange_rate_to_inr
    
    @api.onchange('revenue_breakup_a', 'revenue_breakup_b', 'revenue_breakup_c', 'revenue_breakup_d')
    def _onchange_revenue_breakup_fields(self):
        total = (
            self.revenue_breakup_a +
            self.revenue_breakup_b +
            self.revenue_breakup_c +
            self.revenue_breakup_d
        )
        if total > 100:
            raise ValidationError(
                "The total of Revenue Breakup Category should not exceed 100. The current total is {}.".format(total)
            )

    @api.constrains('revenue_breakup_a', 'revenue_breakup_b', 'revenue_breakup_c', 'revenue_breakup_d')
    def _check_revenue_breakup_sum(self):
        for record in self:
            total = (
                record.revenue_breakup_a +
                record.revenue_breakup_b +
                record.revenue_breakup_c +
                record.revenue_breakup_d
            )
            if total > 100:
                raise ValidationError(
                    "The total of Revenue Breakup Category should not exceed 100. The current total is {}.".format(total)
                )

    def status_update(self):
        view_id = self.env.ref("kw_sales_monitoring.status_update_view").id
        action = {
            'name': 'Update Criteria Details',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'res_id': self.id,
            'context': {'current_id': self.id}
        }
        return action

    @api.model
    def default_get(self, fields_list):
        val = super(kwSalesCrmInherit, self).default_get(fields_list)
        for rec in fields_list:
            question_data = []
            question_ids = self.env['question_master'].sudo().search([])
            for res in question_ids:
                question_data.append((0, 0, {
                    'question_id': res.id,
                }))
                val['question_master_ids'] = question_data
            
        return val

    # Method for Assigning Project Manager
    def action_project_manager_review(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Project Manager',
            'res_model': 'project.manager.review.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }

    # Method for Reassigning Project Manager
    def action_reassign_project_manager(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reassign Project Manager',
            'res_model': 'project.manager.review.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }

    # Method for Assigning Operations Manager
    def action_operations_manager_review(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Operations Manager',
            'res_model': 'operations.manager.review.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }

    # Method for Reassigning Operations Manager
    def action_reassign_operations_manager(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reassign Operations Manager',
            'res_model': 'operations.manager.review.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }
class TdProjectDetails(models.Model):
    _name = "project_details"

    line_of_business_id = fields.Selection([('domain_offering','Domain Offering'),('services','Services')], string="Line Of Business")
    domain_offering_service_line_id = fields.Many2one('domain_offering_service_line',string="Domain Offering/ Service Line")
    solution_service_line_id = fields.Many2one('domain_offering_service_line',string="Solutions/ Services")
    crm_id = fields.Many2one('crm.lead', string="Project ID")

    @api.onchange('line_of_business_id')
    def _onchange_line_of_business_id(self):
        if self.line_of_business_id:
            self.domain_offering_service_line_id = False
            
            return {
                'domain': {
                    'domain_offering_service_line_id': [('line_of_business_id','=',self.line_of_business_id),('type','=','domain_service'),('parent_id','=',False)],
                }
            }

    @api.onchange('domain_offering_service_line_id')
    def _onchange_domain_offering_service_line_id(self):
        if self.domain_offering_service_line_id:
            self.solution_service_line_id = False,False
            return {
                'domain': {
                    'solution_service_line_id': [('type','=','solution_service'),('parent_id','=',self.domain_offering_service_line_id.id)],
                }
            }

class LeadDocumentDetails(models.Model):
    _name = "lead_document_details"

    doc_name_selection = fields.Selection(string='Name',selection=[('Advertisement', 'Advertisement'), ('Tender', 'Tender'), ('EOI', 'EOI'), ('Corrigendum', 'Corrigendum')])
    upload_file = fields.Binary(string = "Upload File")
    upload_filename = fields.Char(string='Upload Filename')
    document_details_id = fields.Many2one('crm.lead',string = "Document ID")
    
class ProjectManagerReviewWizard(models.TransientModel):
    _name = 'project.manager.review.wizard'
    _description = 'Wizard for Project Manager Review'

    sbu_id = fields.Many2one('kw_sbu_master',string = "SBU",domain=[('type','=','sbu')])
    pm_id = fields.Many2one('hr.employee', string='Project Manager')
    lead_id = fields.Many2one('crm.lead', string="Opportunity", required=True)

    @api.model
    def default_get(self, fields):
        res = super(ProjectManagerReviewWizard, self).default_get(fields)
        lead_id = self.env.context.get('active_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            res.update({
                'sbu_id': lead.sbu_id.id if lead.sbu_id else False,
                'pm_id': lead.pm_id.id if lead.pm_id else False,
            })
        return res

    def submit_review(self):
        lead = self.env['crm.lead'].browse(self.env.context.get('default_lead_id'))
        if self.pm_id and self.sbu_id:
            pm_sbu = self.pm_id.sbu_master_id
            if pm_sbu and pm_sbu != self.sbu_id:
                raise UserError("The SBU of the Project Manager does not match the selected SBU. Please verify the details.")
        if self.pm_id:
            lead.pm_id = self.pm_id
        if self.sbu_id:
            lead.sbu_id = self.sbu_id
        lead.message_post(body="Project Manager Review completed with SBU: %s and PM: %s." % (
            lead.sbu_id.name if lead.sbu_id else 'Not Assigned',
            lead.pm_id.name if lead.pm_id else 'Not Assigned'
        ))
        return {'type': 'ir.actions.act_window_close'}

# Wizard for Operations Manager Review
class OperationsManagerReviewWizard(models.TransientModel):
    _name = 'operations.manager.review.wizard'
    _description = 'Wizard for Operations Manager Review'

    operation_team_member = fields.Many2one('hr.employee', string='Operations Team Member')
    lead_id = fields.Many2one('crm.lead', string="Opportunity", required=True)

    @api.model
    def default_get(self, fields):
        res = super(OperationsManagerReviewWizard, self).default_get(fields)
        lead_id = self.env.context.get('active_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            res.update({
                'operation_team_member': lead.operation_team_member.id if lead.operation_team_member else False,
            })
        return res

    def submit_review(self):
        lead = self.env['crm.lead'].browse(self.env.context.get('default_lead_id'))
        if self.operation_team_member:
            lead.operation_team_member = self.operation_team_member
        lead.message_post(body="Operations Manager Review completed with Operations Manager: %s." % (
            lead.operation_team_member.name if lead.operation_team_member else 'Not Assigned'
        ))
        return {'type': 'ir.actions.act_window_close'}

class ChangeOrderWizard(models.TransientModel):
    _name = 'change_order_wizard'
    _description = 'Change Order Wizard'


    def _get_nodal_officers(self):
        return [('parent_id','=',self.partner_id.id)] 


    sbu_id = fields.Many2one('kw_sbu_master', string='SBU')
    work_order_id = fields.Many2one('sales.workorder', string="WO")
    company_id = fields.Many2one('res.company',string="Company")
    country_id = fields.Many2one('res.country', string="Country Name")
    state_id = fields.Many2one('res.country.state',string="State anf UT")

    name = fields.Char('Name')
    source_id = fields.Many2one('utm.source', string="Reference Mode")
    partner_id = fields.Many2one('res.partner',string='Partner',domain="[('parent_id','=',False),'|',('is_partner', '=', True),('customer', '=', True)]")
    client_type = fields.Selection(related='partner_id.incorporation_type', string="Client Type")
    approximate_delivery_timeline = fields.Float(string = "Approximate delivery timeline (Month)")
    project_detail_ids = fields.One2many('project_details','crm_id', string = "Project Details")
    high_level_scope_summary = fields.Text('High Level Scope Summary')
    estimate_lead_value = fields.Float(string = "Estimated Lead Value")
    lead_currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]))
    exchange_rate_to_inr = fields.Float(string='Exchange Rate To INR' , default=1.0)
    value_in_inr = fields.Float(string='Value In INR' , store=True, compute='_compute_value_in_inr')
    document_ids = fields.One2many('lead_document_details','document_details_id',string = "Document Details")
    technology_ids = fields.Many2many('kw_partner_tech_service_master',domain=[('type','=','2')])
    developmen_is_required = fields.Selection(string='Development is required ?',selection=[('onsite', 'On-Site'), ('offside', 'Off-Site'),('combined', 'Combined')])
    revenue_breakup_a = fields.Float(string = " A : Software Development,Operation and Maintenance,Consultancy ")
    revenue_breakup_b = fields.Float(string = " B : Resource Deployment ")
    revenue_breakup_c = fields.Float(string = " C : Ancillary Services ")
    revenue_breakup_d = fields.Float(string = " D : Implementation,Supply,Maintenance ")
    nodal_officer_id  = fields.Many2one('res.partner',string = "Select Name",domain =_get_nodal_officers)
    nodal_officer_name = fields.Char(string="Enter Name")
    nodal_officer_designation = fields.Char(string="Designation")
    nodal_officer_mobile_no = fields.Char(string="Mobile Number")
    nodal_officer_email_address = fields.Char(string="Email Address")

    @api.onchange('work_order_id')
    def _onchange_work_order_id(self):
        if self.work_order_id:
            work_order_data = self.env['sales.workorder'].sudo().browse(self.work_order_id.id)
            # print(work_order_data,"work_order_data===================")
            if work_order_data:
                self.name = work_order_data.eq_id.kw_oppertuinity_id.name
                self.company_id = work_order_data.eq_id.kw_oppertuinity_id.company_id.id
                self.source_id = work_order_data.eq_id.kw_oppertuinity_id.source_id.id
                self.approximate_delivery_timeline = work_order_data.eq_id.kw_oppertuinity_id.approximate_delivery_timeline
                self.partner_id = work_order_data.eq_id.kw_oppertuinity_id.partner_id.id
                self.country_id = work_order_data.eq_id.kw_oppertuinity_id.country_id.id
                self.state_id = work_order_data.eq_id.kw_oppertuinity_id.country_id.id
                self.project_detail_ids = [(6, 0, work_order_data.eq_id.kw_oppertuinity_id.project_detail_ids.ids)]
                self.high_level_scope_summary = work_order_data.eq_id.kw_oppertuinity_id.high_level_scope_summary
                self.developmen_is_required = work_order_data.eq_id.kw_oppertuinity_id.developmen_is_required
                self.technology_ids = [(6,0, work_order_data.eq_id.kw_oppertuinity_id.technology_ids.ids)]
                self.estimate_lead_value = work_order_data.eq_id.kw_oppertuinity_id.estimate_lead_value
                self.lead_currency_id = work_order_data.eq_id.kw_oppertuinity_id.lead_currency_id.id
                self.exchange_rate_to_inr = work_order_data.eq_id.kw_oppertuinity_id.exchange_rate_to_inr
                self.value_in_inr = work_order_data.eq_id.kw_oppertuinity_id.value_in_inr
                self.revenue_breakup_a = work_order_data.eq_id.kw_oppertuinity_id.revenue_breakup_a
                self.revenue_breakup_b = work_order_data.eq_id.kw_oppertuinity_id.revenue_breakup_b
                self.revenue_breakup_c = work_order_data.eq_id.kw_oppertuinity_id.revenue_breakup_c
                self.revenue_breakup_d = work_order_data.eq_id.kw_oppertuinity_id.revenue_breakup_d
                self.nodal_officer_id = work_order_data.eq_id.kw_oppertuinity_id.nodal_officer_id.id
                self.nodal_officer_name = work_order_data.eq_id.kw_oppertuinity_id.nodal_officer_name
                self.nodal_officer_designation = work_order_data.eq_id.kw_oppertuinity_id.nodal_officer_designation
                self.nodal_officer_mobile_no = work_order_data.eq_id.kw_oppertuinity_id.nodal_officer_mobile_no
                self.nodal_officer_email_address = work_order_data.eq_id.kw_oppertuinity_id.nodal_officer_email_address
                self.document_ids = [(6,0, work_order_data.eq_id.kw_oppertuinity_id.document_ids.ids)]


    @api.model
    def create(self, vals):
        res = super(ChangeOrderWizard, self).create(vals)

        cr_applied_stage = self.env['crm.stage'].search([('code', '=', 'cr_applied')], limit=1)

        crm_lead_vals = {
            'name': res.name,
            'partner_id': res.partner_id.id,
            'company_id': res.company_id.id,
            'stage_id': cr_applied_stage.id if cr_applied_stage else False, 
            'approximate_delivery_timeline': res.approximate_delivery_timeline,
            'estimate_lead_value': res.estimate_lead_value,
            'lead_currency_id': res.lead_currency_id.id,
            'exchange_rate_to_inr': res.exchange_rate_to_inr,
            'value_in_inr': res.value_in_inr,
            'revenue_breakup_a': res.revenue_breakup_a,
            'revenue_breakup_b': res.revenue_breakup_b,
            'revenue_breakup_c': res.revenue_breakup_c,
            'revenue_breakup_d': res.revenue_breakup_d,
            'nodal_officer_id': res.nodal_officer_id.id,
            'technology_ids': [(6, 0, res.technology_ids.ids)],
            'document_ids': [(6, 0, res.document_ids.ids)]
        }

        self.env['crm.lead'].sudo().create(crm_lead_vals)

        return res