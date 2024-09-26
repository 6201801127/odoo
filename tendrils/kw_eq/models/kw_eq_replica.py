from odoo import models, fields, api
import math
from math import floor,ceil
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp



class SoftwareEstimatationReplica(models.Model):
    _name = 'kw_eq_replica'
    _description = 'Estimation Replica'
    _rec_name = 'client_name'
    _order = 'id desc'
    
    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)
        
    def get_approval_type(self):
        if self.env.context.get('get_opp_workoder'):
            return 'new'
        
    client_name = fields.Char(related='kw_oppertuinity_id.client_name')
    
    # oppertunity_code = fields.Char('OppCode') 
    client_id = fields.Many2one('res.partner',string='Client Name') 
    kw_oppertuinity_id = fields.Many2one('crm.lead',string="Opportunity Code | Name", domain=[('type', '=', 'opportunity'),('stage_id.code', '=', 'opportunity')])
    technology_ids = fields.One2many('kw_eq_software_development_config','technology_replica_id',string="Study, Development, Implementation & Support")
    java_ids = fields.One2many('kw_eq_software_development_config', 'java_replica_id')
    php_ids = fields.One2many('kw_eq_software_development_config', 'php_replica_id')
    dot_net_core_ids = fields.One2many('kw_eq_software_development_config', 'dot_net_core_replica_id')
    mobile_app_ids = fields.One2many('kw_eq_software_development_config', 'mobile_replica_id')
    odoo_ids = fields.One2many('kw_eq_software_development_config', 'odoo_replica_id')
    tableau_ids = fields.One2many('kw_eq_software_development_config', 'tableau_replica_id')
    sas_ids = fields.One2many('kw_eq_software_development_config', 'sas_replica_id')
    etl_ids = fields.One2many('kw_eq_software_development_config', 'etl_replica_id')
    functional_ids = fields.One2many('kw_eq_software_functional_config','functional_replica_id',string="Additional [Functional] > Long Term Basis Payroll" )
    consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','consultancy_replica_id',string="Estimate for Software Services > Consultancy" )
    it_infra_consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','it_infra_replica_id')
    social_consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','social_consultancy_replica_id')
    software_resource_ids = fields.One2many('kw_eq_software_resource_config','software_resource_replica_id',string="Software Support")
    social_resource_ids = fields.One2many('kw_eq_social_resource_config','social_resource_replica_id',string="Social Media Management" )
    consulatncy_resource_ids = fields.One2many('kw_eq_consulatncy_resource_config','consulatncy_resource_replica_id',string="Consultancy Service" )
    staffing_resource_ids = fields.One2many('kw_eq_staffing_resource_config','staffing_replica_id',string="Staffing Service" )
    third_party_audit_ids = fields.One2many('kw_eq_ancillary_config', 'third_party_replica_id')
    reimbursement_ids = fields.One2many('kw_eq_ancillary_config', 'reimbursement_replica_id')
    strategic_partner_sharing_ids = fields.One2many('kw_eq_ancillary_config', 'strategic_partner_replica_id')
    domain_email_sms_ids = fields.One2many('kw_eq_ancillary_config', 'domain_sms_replica_id')
    mobile_app_store_ids = fields.One2many('kw_eq_ancillary_config', 'mobile_app_replica_id')
    survey_degitalisation_ids = fields.One2many('kw_eq_ancillary_config', 'survey_replica_id')
    ancillary_ids = fields.One2many('kw_eq_ancillary_config','ancillary_replica_id',string="Ancillary Items" )
    out_of_pocket_expenditure_ids = fields.One2many('kw_eq_ancillary_config', 'expanditure_replica_id')
    total_operation_support_ids = fields.One2many('kw_eq_ancillary_config', 'total_operation_replica_id')
    external_ancillary_ids = fields.One2many('kw_eq_external_ancillary_config','estimation_replica_id',string="External Expert Service [Out Source]" )
    it_infra_puchase_ids = fields.One2many('kw_eq_it_infra_purchase_config','estimation_replica_id',string="IT Infra (Purchase)" )
    computer_hardware_ids = fields.One2many('kw_eq_computer_hardware_config','hardware_replica_id',string="Computer Hardware")
    software_licence_ids = fields.One2many('kw_eq_software_licenses_config','license_replica_id',string="Software Licenses - COTS")
    estimate_ids = fields.One2many('kw_eq_estimate_details','estimation_replica_id')
    proposed_eq = fields.Float(string="Proposed EQ")
    maintenance_percentage1 = fields.Selection(string="Standard Maintenance %",selection=[('0', '0 %'), ('7.5', '7.5 %'),('10', '10 %'),('12', '12 %'),('15', '15 %'),('18','18 %')],default='0')
    # maintenance_percentage = fields.Integer(string="Standard Maintenance %")
    maintenance_period = fields.Float(string='Maintenance Period [Yrs]')
    eq_approved = fields.Float(string="EQ Approved")
    margin_adjustment = fields.Float(string="Margin Adjustment")
    actual_margin = fields.Float(string="Actual Margin")
    gross_profit_margin = fields.Float(string="Gross Profit Margin")
    bid_currency = fields.Char(string="Bid Currency",default="INR")
    exchange_rate_to_inr = fields.Float(string="Exchange Rate To INR")
    bid_value_without_tax = fields.Float(string="Bid Value without Tax")
    pbg_implementation_ids = fields.One2many('kw_eq_pbg_config', 'pbg_replica_id')
    pbg_support_ids = fields.One2many('kw_eq_pbg_config', 'pbg_support_replica_id')
    pbg_implement =  fields.Float(string='Total [Implementation]')
    pbg_support =  fields.Float(string='Total [Operation & Support]')
    eq_log_ids = fields.One2many('eq_log','log_replica_id')
    state = fields.Selection(string="Status",selection=[('version_1', 'Version 1'), ('version_2', 'Version 2'),('version_3', 'Version 3'),('version_4', 'Version 4'),('version_5', 'Version 5'),('version_6', 'Version 6'),('grant','Grant')],default="version_1")
    effective_date = fields.Date(string="Effective Date", compute='compute_effective_date')
    level_1_id = fields.Many2one('hr.employee',string="Authority 1")
    level_2_id = fields.Many2one('hr.employee',string="Authority 2")
    level_3_id = fields.Many2one('hr.employee',string="Authority 3")
    level_4_id = fields.Many2one('hr.employee',string="Authority 4")
    level_5_id = fields.Many2one('hr.employee',string="Authority 5")
    level_6_id = fields.Many2one('hr.employee',string="Authority 6")
    page_software_bool = fields.Boolean(compute='compute_page_access')
    page_consultancy_bool = fields.Boolean(compute='compute_page_access')
    page_resource_bool = fields.Boolean(compute='compute_page_access')
    page_ancillary_bool = fields.Boolean(compute='compute_page_access')
    page_it_infra_bool = fields.Boolean(compute='compute_page_access')
    page_estimate_bool = fields.Boolean(compute='compute_page_access')
    page_pbg_bool = fields.Boolean(compute='compute_page_access')
    page_log_bool = fields.Boolean(compute='compute_page_access')
    page_ancillary_opx_bool = fields.Boolean(compute='compute_page_access')
    page_cashflow_bool = fields.Boolean(compute='compute_page_access')
    month = fields.Integer(string = 'CAP Month')
    op_month = fields.Integer(string = 'OP Month')
    milestone_total = fields.Integer(string = 'Milestone Total',default=10)
    quote_ids = fields.One2many('kw_eq_quote_config','quote_replica_id')
    paticulars_ids = fields.One2many('kw_eq_paticulars_config','paticular_replica_id')
    # deliverable_ids = fields.One2many('kw_eq_deliverable_config','deliverable_replica_id')
    op_year_ids = fields.One2many('kw_eq_cashflow_config','opyear_replica_id')
    cap_year_ids = fields.One2many('kw_eq_cashflow_config','capyear_replica_id')
    # audit_trail_details_ids = fields.One2many('kw_eq_audit_trail_details', 'eq_audit_trail_id')
    eq_audit_trail_id = fields.Many2one('kw_eq_audit_trail_details')
    action = fields.Char('Action')
    details = fields.Char(string="Details")
    date = fields.Datetime(string="Date")
    estimation_id = fields.Many2one('kw_eq_estimation',ondelete="cascade")
    roll_back_bool = fields.Boolean(compute="compute_rollback")
    revised_level_1_id = fields.Many2one('hr.employee',string="Revised Authority 1")
    revised_level_2_id = fields.Many2one('hr.employee',string="Revised Authority 2")
    revised_level_3_id = fields.Many2one('hr.employee',string="Revised Authority 3")
    revised_level_4_id = fields.Many2one('hr.employee',string="Revised Authority 4")
    revised_level_5_id = fields.Many2one('hr.employee',string="Revised Authority 5")
    revised_level_6_id = fields.Many2one('hr.employee',string="Revised Authority 6")
    revised_proposed_eq = fields.Float(string="Revised Proposed EQ")
    revised_eq_approved = fields.Float(string="Revised EQ Approved")
    revised_margin_adjustment = fields.Float(string="Revised Margin Adjustment")
    revised_actual_margin = fields.Float(string="Revised Actual Margin")
    revised_gross_profit_margin = fields.Float(string="Revised Gross Profit Margin")
    revised_bid_value_without_tax = fields.Float(string="Revised Bid Value without Tax")
    revised_exchange_rate_to_inr = fields.Float(string="Revised Exchange Rate To INR")
    revision_status = fields.Char()
    revision_state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'),('submit', 'Submitted'),('forward', 'Forwarded'),('recommend', 'Recommended'),('not_recommended', 'Not Recommended'),('grant', ' Granted'),('rejected', ' Rejected')],string="Status",default='draft')
    type = fields.Char()
    revision_id = fields.Many2one('kw_eq_revision',ondelete="cascade")
    eq_status = fields.Selection([('original', 'Original'), ('revision', 'Revision')],string="EQ Type")
    type_seggrigate = fields.Char(compute='_compute_type',string='Type')
    revision_version= fields.Char(related='revision_id.revision_status')
    code = fields.Char()
    revised_level_1_bool = fields.Boolean(compute='_check_level_1_emp')
    # resource_material_ids = fields.One2many('kw_eq_resources_data', 'resource_material_replica_id')
    approval_type = fields.Selection([('new', 'New'), ('extension', 'Extension'),('change', 'Change'),('revision','Revision')],string="Approval Type")


    def get_latest_record(self):
        estimate_lst=[]
        revision_lst = []
        replica_est_lst = []
        replica_rev_lst = []
        estimation = self.env['kw_eq_estimation'].sudo().search([('state','=','grant')])
        estimation_ids = estimation.ids
        revision = self.env['kw_eq_revision'].sudo().search([('state','=','grant'),('estimation_id','in',estimation_ids)])
        
        for rec in estimation:
            if rec.id not in revision.mapped('estimation_id').ids:
                estimate_lst.append(rec.id)
            latest_revision = revision.sudo().search([('state','=','grant'),('kw_oppertuinity_id','=',rec.kw_oppertuinity_id.id)], order='revision_status desc',limit=1)
            revision_lst.append(latest_revision.id)
        for est in estimate_lst:
            replica = self.env['kw_eq_replica'].sudo().search([('estimation_id','=',est),('estimation_id.state','=','grant')],order='id desc',limit=1)
            replica_est_lst.append(replica.id)
        if revision_lst:
            for rev in revision_lst:
                replica_rev = self.env['kw_eq_replica'].sudo().search([('revision_id','=',rev),('revision_id.state','=','grant')],order='id desc',limit=1)
                replica_rev_lst.append(replica_rev.id)
        view_tree_id = self.env.ref('kw_eq.kw_eq_replica_view_tree').id
        action = {
            'name': "Approved EQ",
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'kw_eq_replica',
            'views': [(view_tree_id, 'tree')],
            'type': 'ir.actions.act_window',
            'target': 'self',
            'context': {'create': False, 'delete': False, 'edit': False},
            'domain':['|',('id','in',replica_est_lst),('id','in',replica_rev_lst)]
        }
        return action
    
    def get_view_for_finance(self):
        if self.revision_id:
            view_id = self.env.ref('kw_eq.kw_eq_revision_form').id
            revised_number = self.env['kw_eq_revision'].sudo().search([('id','=',self.revision_id.id),('state','=','grant')],order='revision_status desc',limit=1)
            return {
                'name':"Revised EQ",
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': revised_number.id,
                'res_model': 'kw_eq_revision',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'self',
                'context':{'create': False,'delete':False,'edit':False},
            }
        else:
            view_id = self.env.ref('kw_eq.kw_eq_estimation_view_form').id
            last_estimation = self.env['kw_eq_estimation'].sudo().search([('id','=',self.estimation_id.id),('state','=','grant')],order='state desc',limit=1)
            return  {
                'name':"Approved EQ",
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': last_estimation.id,
                'res_model': 'kw_eq_estimation',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'self',
                'context':{'create': False,'delete':False,'edit':False},
            }



    def _check_level_1_emp(self):
        for rec in self:
            if rec.revised_level_1_id.id == self.env.user.employee_ids.id:
                rec.revised_level_1_bool = True
            else:
                rec.revised_level_1_bool = False
    
    def _compute_type(self):
        for rec in self:
            if not rec.revision_id:
                rec.type_seggrigate = "EQ"
            else:
                rec.type_seggrigate = "EQ Revision"
                

    @api.depends('details')
    def compute_rollback(self):
        for rec in self:
            if 'Rollback' in rec.details:
                rec.roll_back_bool = True
            else:
                rec.roll_back_bool = False




    def get_audit_trail_view(self):
        if self.type == 'revision':
            view_id_form = self.env.ref('kw_eq.kw_eq_replica_revision_audit_trail_view_form').id
            return {
            'name':"Audit Trail",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'kw_eq_replica',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'self',
            }
        else:
            view_id_form = self.env.ref('kw_eq.kw_eq_replica_audit_trail_view_form').id
            return {
            'name':"Audit Trail",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'kw_eq_replica',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'self',
                
            }
            
        
    
    @api.depends('write_date')
    def compute_effective_date(self):
        for rec in self:
            rec.effective_date = rec.write_date.date()

    @api.depends('kw_oppertuinity_id', 'level_1_id', 'level_2_id', 'level_3_id', 'level_4_id', 'level_5_id', 'level_6_id')
    def compute_page_access(self):
        current_emp_id = self.env.user.employee_ids.id
        page_mapping = {
            'software': 'page_software_bool',
            'consultancy': 'page_consultancy_bool',
            'resource': 'page_resource_bool',
            'ancillary': 'page_ancillary_bool',
            'it_infra': 'page_it_infra_bool',
            'estimate': 'page_estimate_bool',
            'pbg': 'page_pbg_bool',
            'log': 'page_log_bool',
            'ancillary_opx': 'page_ancillary_opx_bool',
            'cashflow': 'page_cashflow_bool',
        }
        roles = {
            'pm': 'pm_id',
            'reviewer': 'reviewer_id',
            'ceo': 'ceo_id',
            'csg_head': 'csg_head_id',
            'presales': 'presales_id',
            'cso': 'cso_id',
            'sbu_head': 'pm_id.sbu_master_id.representative_id'
        }
        def get_nested_attr(obj, attr_path):
            attrs = attr_path.split('.')
            for attr in attrs:
                obj = getattr(obj, attr, False)
                if not obj:
                    return False
            return obj
        for rec in self:
            has_workorder = rec.kw_oppertuinity_id.stage_id.code == 'workorder'
            sbu_representative = get_nested_attr(rec.kw_oppertuinity_id, 'pm_id.sbu_master_id.representative_id')
            user_is_sbu_representative = sbu_representative and sbu_representative.id == current_emp_id
            if (user_is_sbu_representative and not sbu_representative.user_id.has_group('kw_eq.group_eq_manager')) or has_workorder:
                access_records = self.env['kw_eq_page_access'].sudo().search([])
                for record in access_records:
                    names = record.authority_ids.mapped('code')
                    page_bool = page_mapping.get(record.page_name)
                    if page_bool:
                        for role, field in roles.items():
                            role_id = get_nested_attr(rec.kw_oppertuinity_id, field)
                            if role in names and role_id and role_id.id == current_emp_id:
                                setattr(rec, page_bool, True)
            elif not self.env.user.has_group('kw_eq.group_eq_manager') and not self.env.user.has_group('kw_eq.group_eq_report_manager') and not self.env.user.has_group('kw_eq.group_eq_finance'):
                if current_emp_id in (
                    rec.level_1_id.id, rec.level_2_id.id, rec.level_3_id.id, 
                    rec.level_4_id.id, rec.level_5_id.id, rec.level_6_id.id
                ):
                    access_records = self.env['kw_eq_page_access'].sudo().search([])
                    for record in access_records:
                        names = record.authority_ids.mapped('code')
                        page_bool = page_mapping.get(record.page_name)
                        if page_bool:
                            for role, field in roles.items():
                                role_id = get_nested_attr(rec.kw_oppertuinity_id, field)
                                if role in names and role_id and role_id.id == current_emp_id:
                                    setattr(rec, page_bool, True)
            elif self.env.user.has_group('kw_eq.group_eq_manager'):
                for page_bool in page_mapping.values():
                    setattr(rec, page_bool, True)
            else:
                for page_bool in page_mapping.values():
                    setattr(rec, page_bool, True)

    # @api.depends('kw_oppertuinity_id', 'level_1_id', 'level_2_id', 'level_3_id', 'level_4_id', 'level_5_id', 'level_6_id')
    # def compute_page_access(self):
    #     current_emp_id = self.env.user.employee_ids.id
    #     page_mapping = {
    #                 'software': 'page_software_bool',
    #                 'consultancy': 'page_consultancy_bool',
    #                 'resource': 'page_resource_bool',
    #                 'ancillary': 'page_ancillary_bool',
    #                 'it_infra': 'page_it_infra_bool',
    #                 'estimate': 'page_estimate_bool',
    #                 'pbg': 'page_pbg_bool',
    #                 'log': 'page_log_bool',
    #                 'ancillary_opx' : 'page_ancillary_opx_bool',
    #                 'cashflow': 'page_cashflow_bool',
    #                 }
    #     for rec in self:
    #         if not self.env.user.has_group('kw_eq.group_eq_manager') and not self.env.user.has_group('kw_eq.group_eq_report_manager') and not self.env.user.has_group('kw_eq.group_eq_finance'):
    #             if current_emp_id in (rec.level_1_id.id, rec.level_2_id.id, rec.level_3_id.id, rec.level_4_id.id, rec.level_5_id.id, rec.level_6_id.id):
    #                 access = self.env['kw_eq_page_access'].sudo().search([])
    #                 for record in access:
    #                     names = record.authority_ids.mapped('code')
    #                     if record.page_name in page_mapping:
    #                         page_bool = page_mapping[record.page_name]
    #                         for role in ['pm','reviewer', 'ceo', 'csg_head', 'presales', 'cso']:
    #                             if role in names and getattr(rec.kw_oppertuinity_id, role + '_id').id == current_emp_id:
    #                                 setattr(rec, page_bool, True)

    #         if self.kw_oppertuinity_id.pm_id.sbu_master_id.representative_id.id == self.env.user.employee_ids.id and not self.kw_oppertuinity_id.pm_id.sbu_master_id.representative_id.user_id.has_group('kw_eq.group_eq_manager') or self.kw_oppertuinity_id.stage_id.code == 'workorder':
    #             rec.page_software_bool = rec.page_consultancy_bool =rec.page_resource_bool =rec.page_ancillary_bool =rec.page_it_infra_bool =rec.page_estimate_bool =rec.page_pbg_bool =rec.page_log_bool =rec.page_ancillary_opx_bool =rec.page_cashflow_bool = True
    #         else:
    #             rec.page_software_bool = rec.page_consultancy_bool =rec.page_resource_bool =rec.page_ancillary_bool =rec.page_it_infra_bool =rec.page_estimate_bool =rec.page_pbg_bool =rec.page_log_bool =rec.page_ancillary_opx_bool =rec.page_cashflow_bool = True



class AuditTrailDetails(models.Model):
    _name = 'kw_eq_audit_trail_details'
    _description = 'Audit Trail Details'
    _rec_name = 'kw_oppertuinity_id'
    
    state = fields.Selection(string="Status",selection=[('version_1', 'Version 1'), ('version_2', 'Version 2'),('version_3', 'Version 3'),('version_4', 'Version 4'),('version_5', 'Version 5'),('version_6', 'Version 6'),('grant','Grant')],default="version_1")
    client_id = fields.Many2one('res.partner',string='Client Name') 
    kw_oppertuinity_id = fields.Many2one('crm.lead',string="Opportunity Code | Name", domain=[('type', '=', 'opportunity'),('stage_id.code', '=', 'opportunity')])
    level_1_id = fields.Many2one('hr.employee',string="PM Name")
    level_2_id = fields.Many2one('hr.employee',string="Authority 2")
    level_3_id = fields.Many2one('hr.employee',string="Authority 3")
    level_4_id = fields.Many2one('hr.employee',string="Authority 4")
    level_5_id = fields.Many2one('hr.employee',string="Authority 5")
    level_6_id = fields.Many2one('hr.employee',string="Authority 6")
    sbu = fields.Char(string="SBU",related="kw_oppertuinity_id.pm_id.sbu_master_id.name")
    ac_holder_name = fields.Char(string="AC Holder Name",related="kw_oppertuinity_id.sales_person_id.name")
    csg_div = fields.Char(string="CSG",related="kw_oppertuinity_id.csg_name")
    client_short_name = fields.Char(string="Client Short Name",related="kw_oppertuinity_id.client_short_name")
    pac_status = fields.Integer(string="PAC Status",related="kw_oppertuinity_id.pac_status")


    date = fields.Date(string="Date")
    estimation_id = fields.Many2one('kw_eq_estimation')
    audit_trail_details_ids = fields.One2many('kw_eq_replica', 'eq_audit_trail_id')
    client_name = fields.Char(related='kw_oppertuinity_id.client_name')
    revision_id = fields.Many2one('kw_eq_revision')

    revised_level_1_id = fields.Many2one('hr.employee',string="Revised Authority 1")
    revised_level_2_id = fields.Many2one('hr.employee',string="Revised Authority 2")
    revised_level_3_id = fields.Many2one('hr.employee',string="Revised Authority 3")
    revised_level_4_id = fields.Many2one('hr.employee',string="Revised Authority 4")
    revised_level_5_id = fields.Many2one('hr.employee',string="Revised Authority 5")
    revised_level_6_id = fields.Many2one('hr.employee',string="Revised Authority 6")