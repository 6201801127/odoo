from odoo import models, fields, api
import math
from math import floor,ceil
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime




class SoftwareEstimatationRevision(models.Model):
    _name = 'kw_eq_revision'
    _description = 'Estimation Revision'
    _rec_name = 'kw_oppertuinity_id'
    
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}

        if context.get('revision'):
            user_id = self.env.user.employee_ids.id
            
            domain = [
                '|',
                '&', ('revised_level_1_id', '=', user_id), ('state', '=', 'draft'),
                '|',
                '&', ('revised_level_2_id', '=', user_id), ('state', '=', 'applied'),
                '|',
                '&', ('revised_level_3_id', '=', user_id), ('state', '=', 'submit'),
                '|',
                '&', ('revised_level_4_id', '=', user_id), ('state', '=', 'forward'),
                
                '&', ('revised_level_5_id', '=', user_id), ('state', 'in', ('recommend','not_recommended')),
            ]
            args += domain

        return super(SoftwareEstimatationRevision, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
    
    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)
        
    estimation_id = fields.Many2one('kw_eq_estimation')
    # oppertunity_code = fields.Char('OppCode') 
    client_name = fields.Char(related='kw_oppertuinity_id.client_name')
    client_id = fields.Many2one('res.partner',string='Client Name') 
    kw_oppertuinity_id = fields.Many2one('crm.lead',string="Opportunity Code | Name",)
    technology_ids = fields.One2many('kw_eq_software_development_config','revision_id',string="Study, Development, Implementation & Support")
    functional_ids = fields.One2many('kw_eq_software_functional_config','revision_id',string="Additional [Functional] > Long Term Basis Payroll" )
    consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','revision_id',string="Estimate for Software Services > Consultancy" )
    it_infra_consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','it_infra_revision_id')
    social_consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','social_revision_id')
    ancillary_ids = fields.One2many('kw_eq_ancillary_config','revision_id',string="Ancillary Items" )
    external_ancillary_ids = fields.One2many('kw_eq_external_ancillary_config','revision_id',string="External Expert Service [Out Source]" )
    software_resource_ids = fields.One2many('kw_eq_software_resource_config','revision_id',string="Software Support" )
    social_resource_ids = fields.One2many('kw_eq_social_resource_config','revision_id',string="Social Media Management" )
    consulatncy_resource_ids = fields.One2many('kw_eq_consulatncy_resource_config','revision_id',string="Consultancy Service" )
    staffing_resource_ids = fields.One2many('kw_eq_staffing_resource_config','revision_id',string="Staffing Service" )
    it_infra_puchase_ids = fields.One2many('kw_eq_it_infra_purchase_config','revision_id',string="IT Infra (Purchase)" )
    estimate_ids = fields.One2many('kw_eq_estimate_details','revision_id')
    total_operation_support_ids = fields.One2many('kw_eq_ancillary_config', 'total_operation_revision_id')
    out_of_pocket_expenditure_ids = fields.One2many('kw_eq_ancillary_config', 'expanditure_revision_id')
    third_party_audit_ids = fields.One2many('kw_eq_ancillary_config', 'third_party_revision_id')
    reimbursement_ids = fields.One2many('kw_eq_ancillary_config', 'reimbursement_revision_id')
    domain_email_sms_ids = fields.One2many('kw_eq_ancillary_config', 'domain_sms_revision_id')
    strategic_partner_sharing_ids = fields.One2many('kw_eq_ancillary_config', 'strategic_partner_revision_id')
    mobile_app_store_ids = fields.One2many('kw_eq_ancillary_config', 'mobile_app_revision_id')
    survey_degitalisation_ids = fields.One2many('kw_eq_ancillary_config', 'survey_degitalisation_revision_id')
    java_ids = fields.One2many('kw_eq_software_development_config', 'java_estimate_revision_id')
    php_ids = fields.One2many('kw_eq_software_development_config', 'php_estimate_revision_id')
    dot_net_core_ids = fields.One2many('kw_eq_software_development_config', 'core_estimate_revision_id')
    mobile_app_ids = fields.One2many('kw_eq_software_development_config', 'mobile_estimate_revision_id')
    odoo_ids = fields.One2many('kw_eq_software_development_config', 'odoo_estimate_revision_id')
    tableau_ids = fields.One2many('kw_eq_software_development_config', 'tableu_estimate_revision_id')
    sas_ids = fields.One2many('kw_eq_software_development_config', 'sas_estimate_revision_id')
    etl_ids = fields.One2many('kw_eq_software_development_config', 'etl_estimate_revision_id')
    first_year_value = fields.Float(string= "First Year")
    computer_hardware_ids = fields.One2many('kw_eq_computer_hardware_config','hardware_revision_id',string="Computer Hardware")
    software_licence_ids = fields.One2many('kw_eq_software_licenses_config','license_revision_id',string="Software Licenses - COTS")
    pbg_implementation_ids = fields.One2many('kw_eq_pbg_config', 'pbg_implementation_revision_id')
    pbg_support_ids = fields.One2many('kw_eq_pbg_config', 'pbg_support_revision_id')
    maintenance_percentage1 = fields.Selection(string="Standard Maintenance %",selection=[('0', '0 %'), ('7.5', '7.5 %'),('10', '10 %'),('12', '12 %'),('15', '15 %'),('18','18 %')],default='0')
    maintenance_period = fields.Float(string='Maintenance Period [Yrs]')
    eq_approved = fields.Float(string="EQ Approved")
    margin_adjustment = fields.Float(string="Margin Adjustment")
    actual_margin = fields.Float(string="Actual Margin")
    gross_profit_margin = fields.Float(string="Gross Profit Margin")
    bid_currency = fields.Char(string="Bid Currency",default="INR")
    exchange_rate_to_inr = fields.Float(string="Exchange Rate To INR")
    bid_value_without_tax = fields.Float(string="Bid Value without Tax")
    proposed_eq = fields.Float(string="Proposed EQ")
    pbg_implement =  fields.Float(string='Total [Implementation]')
    pbg_support =  fields.Float(string='Total [Operation & Support]')
    eq_log_ids = fields.One2many('eq_log','eq_revision_id')
    pending_at = fields.Char(string="Pending At")
    effective_from = fields.Date(string="Effective Date")
    action = fields.Char('Action')
    details = fields.Char(string="Details")
    eq_status = fields.Selection([('original', 'Original'), ('revision', 'Revision')],string="EQ Type")
    revised_level_1_id = fields.Many2one('hr.employee',string="Revised Authority 1")
    revised_level_2_id = fields.Many2one('hr.employee',string="Revised Authority 2")
    revised_level_3_id = fields.Many2one('hr.employee',string="Revised Authority 3")
    revised_level_4_id = fields.Many2one('hr.employee',string="Revised Authority 4")
    revised_level_5_id = fields.Many2one('hr.employee',string="Revised Authority 5")
    revised_level_6_id = fields.Many2one('hr.employee',string="Revised Authority 6")
    revised_level_1_role = fields.Char(compute="_compute_revised_user_role")
    revised_level_2_role = fields.Char(compute="_compute_revised_user_role")
    revised_level_3_role = fields.Char(compute="_compute_revised_user_role")
    revised_level_4_role = fields.Char(compute="_compute_revised_user_role")
    revised_level_5_role = fields.Char(compute="_compute_revised_user_role")
    revised_level_6_role = fields.Char(compute="_compute_revised_user_role")
    revised_level_1_bool = fields.Boolean(compute='_check_level_1_emp')
    revised_proposed_eq = fields.Float(string="Revised Proposed EQ")
    revised_eq_approved = fields.Float(string="Revised EQ Approved")
    revised_margin_adjustment = fields.Float(string="Revised Margin Adjustment")
    revised_actual_margin = fields.Float(string="Revised Actual Margin")
    revised_gross_profit_margin = fields.Float(string="Revised Gross Profit Margin")
    revised_bid_value_without_tax = fields.Float(string="Revised Bid Value without Tax")
    revised_exchange_rate_to_inr = fields.Float(string="Revised Exchange Rate To INR")
    revision_status = fields.Char()
    state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'),('submit', 'Submitted'),('forward', 'Forwarded'),('recommend', 'Recommended'),('not_recommended', 'Not Recommended'),('grant', ' Granted'),('rejected', ' Rejected')],string="Status",default='draft')
    update_status = fields.Selection([('recommend', 'Recommended'), ('not_recommended', 'Not Recommended')],string="Update Status")
    code = fields.Char()
    revised_level_1_bool = fields.Boolean(compute="_compute_user_access")
    revised_level_2_bool = fields.Boolean(compute="_compute_user_access")
    revised_level_3_bool = fields.Boolean(compute="_compute_user_access")
    revised_level_4_bool = fields.Boolean(compute="_compute_user_access")
    revised_level_5_bool = fields.Boolean(compute="_compute_user_access")
    revert_check_bool =fields.Boolean(compute="_compute_revert_access")
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_revert_access', store=False)

    pending_at = fields.Char(string="Pending At")
    month = fields.Integer(string = 'CAP Month')
    op_month = fields.Integer(string = 'OP Month')
    milestone_total = fields.Integer(string = 'Milestone Total',default=10)
    quote_ids = fields.One2many('kw_eq_quote_config','revision_quote_id')
    paticulars_ids = fields.One2many('kw_eq_paticulars_config','revision_paticular_id')
    # deliverable_ids = fields.One2many('kw_eq_deliverable_config','revision_deliverable_id')
    op_year_ids = fields.One2many('kw_eq_cashflow_config','revision_op_id')
    cap_year_ids = fields.One2many('kw_eq_cashflow_config','revision_cap_id')

    
    
    def _compute_user_access(self):
        current_emp = self.env.user.employee_ids.id
        for rec in self:
            rec.revised_level_1_bool = rec.revised_level_1_id.id == current_emp and rec.state == "draft"
            rec.revised_level_2_bool = rec.revised_level_2_id.id == current_emp and rec.state == "applied"
            rec.revised_level_3_bool = rec.revised_level_3_id.id == current_emp and rec.state in ('submit')
            rec.revised_level_4_bool = rec.revised_level_4_id.id == current_emp and rec.state =="forward"
            rec.revised_level_5_bool = rec.revised_level_5_id.id == current_emp and rec.state in ('recommend','not_recommended')
                
   

    @api.onchange('month','op_month')
    def _onchange_year(self):
        if self.month:
            months = self.month
            lines = [(5, 0, 0)]
            for month in range(1, months + 1):
                lines.append((0, 0, {
                    'time_line': f'CAP M{month}',
                    'opening_balance': '',
                }))
            lines.append((0, 0, {
                'time_line': 'CAP Closure',
                'opening_balance': '',
            }))
            self.cap_year_ids = lines
        else:
            self.cap_year_ids = [(5, 0, 0)]
        if self.op_month:
            op_months = self.op_month
            lines = [(5, 0, 0)]
            for month in range(1, op_months + 2):
                lines.append((0, 0, {
                    'time_line': f'OP M{month}',
                    'opening_balance': '',
                }))
            lines.append((0, 0, {
                'time_line': 'Opex Closure',
                'opening_balance': '',
            }))
            lines.append((0, 0, {
                'time_line': 'Project Closure',
                'opening_balance': '',
            }))
            self.op_year_ids = lines
        else:
            self.op_year_ids = [(5, 0, 0)]
        
                
                

    @api.depends('state','revised_level_1_id','revised_level_2_id','revised_level_3_id','revised_level_4_id','revised_level_5_id')
    def _compute_revert_access(self):
        current_emp = self.env.user.employee_ids.id
        for rec in self:
            if rec.state == "draft":
                rec.revert_check_bool = True
            elif rec.state == 'applied' and rec.revised_level_1_id.id == current_emp:
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
                rec.revert_check_bool = True
            elif rec.state == 'submit' and rec.revised_level_2_id.id == current_emp:
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
                rec.revert_check_bool = True
            elif rec.state == 'forward' and rec.revised_level_3_id.id == current_emp:
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
                rec.revert_check_bool = True
            elif rec.state in ('recommend','not_recommended') and rec.revised_level_4_id.id == current_emp:
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
                rec.revert_check_bool = True
            elif rec.state in ('grant','rejected') and rec.revised_level_5_id.id == current_emp:
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
                rec.revert_check_bool = True
            elif rec.state in ('applied') and rec.revised_level_3_id.id == current_emp:
                rec.test_css = """
                <style>
                    .o_form_button_edit {display: none !important;}
                    .o_form_button_create {display: none !important;}
                </style>
            """
                rec.revert_check_bool = True

    def _check_level_1_emp(self):
        for rec in self:
            if rec.revised_level_1_id.id == self.env.user.employee_ids.id:
                rec.revised_level_1_bool = True
            else:
                rec.revised_level_1_bool = False
    
    @api.depends('revised_level_1_id', 'revised_level_2_id', 'revised_level_3_id', 'revised_level_4_id', 'revised_level_5_id', 'revised_level_6_id', 'kw_oppertuinity_id','eq_status')
    def _compute_revised_user_role(self):
        for rec in self:
            approval = self.env['kw_eq_approval_configuration'].sudo().search([('approval_type','=','revision'),('effective_date','<=',date.today())],order='effective_date desc',limit=1)
            level_1 ='Sales Head' if approval.level_1 =='cso' else 'Reviewer' if  approval.level_1 == 'reviewer' else 'CEO' if   approval.level_1 == 'ceo' else 'CSG Head' if approval.level_1 =='csg_head' else 'Pre Sales Head'  if   approval.level_1 == 'presales'  else 'CFO' if  approval.level_1 =='cfo' else 'PM'

            level_2 ='Sales Head' if approval.level_2 =='cso' else 'Reviewer' if  approval.level_2 == 'reviewer' else 'CEO' if   approval.level_2 == 'ceo' else 'CSG Head' if approval.level_2 =='csg_head' else 'Pre Sales Head'  if   approval.level_2 == 'presales'  else 'CFO' if  approval.level_2 =='cfo' else 'PM'  
 
            level_3 = 'Sales Head' if  approval.level_3 =='cso' else 'Reviewer' if   approval.level_3 == 'reviewer' else 'CEO' if    approval.level_3 == 'ceo' else 'CSG Head' if  approval.level_3 =='csg_head' else 'Pre Sales Head'  if    approval.level_3 == 'presales'  else 'CFO' if  approval.level_3 =='cfo' else 'PM'  

            level_4 = 'Sales Head' if  approval.level_4 =='cso' else 'Reviewer' if   approval.level_4 == 'reviewer' else 'CEO' if    approval.level_4 == 'ceo' else 'CSG Head' if  approval.level_4 =='csg_head' else 'Pre Sales Head'  if    approval.level_4 == 'presales'  else 'CFO' if  approval.level_4 =='cfo' else 'PM' 

            level_5 = 'Sales Head' if  approval.level_5 =='cso' else 'Reviewer' if   approval.level_5 == 'reviewer' else 'CEO' if    approval.level_5 == 'ceo' else 'CSG Head' if  approval.level_5 =='csg_head' else 'Pre Sales Head'  if    approval.level_5 == 'presales'  else 'CFO' if  approval.level_5 =='cfo' else 'PM'

            level_6 = 'Sales Head' if  approval.level_6 =='cso' else 'Reviewer' if   approval.level_6 == 'reviewer' else 'CEO' if    approval.level_6 == 'ceo' else 'CSG Head' if approval.level_6=='csg_head' else 'Pre Sales Head'  if    approval.level_6 == 'presales'  else 'CFO' if  approval.level_6 =='cfo' else 'PM' 
    
            if rec.kw_oppertuinity_id:
                if rec.revised_level_1_id :
                    rec.revised_level_1_role = f"{rec.revised_level_1_id.name} ({level_1})"
                if rec.revised_level_2_id:
                    rec.revised_level_2_role = f"{rec.revised_level_2_id.name} ({level_2})"
                if rec.revised_level_3_id:
                    rec.revised_level_3_role = f"{rec.revised_level_3_id.name} ({level_3})"
                if rec.revised_level_4_id:
                    rec.revised_level_4_role = f"{rec.revised_level_4_id.name} ({level_4})"
                if rec.revised_level_5_id:
                    rec.revised_level_5_role = f"{rec.revised_level_5_id.name} ({level_5})"
                if rec.revised_level_6_id:
                    rec.revised_level_6_role = f"{rec.revised_level_6_id.name} ({level_6})"

    @api.onchange('technology_ids','functional_ids','java_ids','php_ids','dot_net_core_ids','mobile_app_ids','odoo_ids','tableau_ids','sas_ids','etl_ids','out_of_pocket_expenditure_ids','pbg_implementation_ids','maintenance_percentage1','maintenance_period','total_operation_support_ids','pbg_support_ids','consultancy_ids','it_infra_consultancy_ids','social_consultancy_ids','software_resource_ids','social_resource_ids','consulatncy_resource_ids','staffing_resource_ids','third_party_audit_ids','ancillary_ids','reimbursement_ids','strategic_partner_sharing_ids','external_ancillary_ids','it_infra_puchase_ids','computer_hardware_ids','software_licence_ids','revised_proposed_eq','revised_margin_adjustment','revised_actual_margin','revised_eq_approved','revised_gross_profit_margin','revised_bid_value_without_tax','revised_exchange_rate_to_inr','bid_currency','survey_degitalisation_ids','mobile_app_store_ids','domain_email_sms_ids','month','op_month','cap_year_ids','paticulars_ids','quote_ids','op_year_ids')
    def _compute_revised_estimate_data(self):
        self.paticulars_ids = False
        paticulars_ids = []
        paticulars_records = self.env['kw_eq_paticulars_master'].search([])
        for record in paticulars_records:
            paticulars_ids.append([0, 0, {
                'paticulars_name': record.paticulars,
                'code': record.code,
            }])
        self.paticulars_ids = paticulars_ids
        if self.eq_status == 'revision':
            software_total = sum(self.technology_ids.mapped('implementation_total_cost')) + \
                            sum(self.java_ids.mapped('implementation_total_cost')) + \
                            sum(self.php_ids.mapped('implementation_total_cost')) + \
                            sum(self.dot_net_core_ids.mapped('implementation_total_cost')) + \
                            sum(self.mobile_app_ids.mapped('implementation_total_cost')) + \
                            sum(self.odoo_ids.mapped('implementation_total_cost')) + \
                            sum(self.tableau_ids.mapped('implementation_total_cost')) + \
                            sum(self.sas_ids.mapped('implementation_total_cost')) + \
                            sum(self.etl_ids.mapped('implementation_total_cost'))
            functional_total = sum(self.functional_ids.mapped('implementation_total_ctc'))
            ancillary_impl_total = sum(self.out_of_pocket_expenditure_ids.mapped('cost'))
            ancillary_support_total = sum(self.total_operation_support_ids.mapped('cost'))

            software_support_total = sum(self.technology_ids.mapped('support_total_cost')) + \
                            sum(self.java_ids.mapped('support_total_cost')) + \
                            sum(self.php_ids.mapped('support_total_cost')) + \
                            sum(self.dot_net_core_ids.mapped('support_total_cost')) + \
                            sum(self.mobile_app_ids.mapped('support_total_cost')) + \
                            sum(self.odoo_ids.mapped('support_total_cost')) + \
                            sum(self.tableau_ids.mapped('support_total_cost')) + \
                            sum(self.sas_ids.mapped('support_total_cost')) + \
                            sum(self.etl_ids.mapped('support_total_cost'))
            functional_support_total = sum(self.functional_ids.mapped('support_total_ctc'))

            consultancy_total = sum(self.consultancy_ids.mapped('total_cost'))
            consultancy_IT_total = sum(self.it_infra_consultancy_ids.mapped('total_cost'))
            consultancy_social_total = sum(self.social_consultancy_ids.mapped('total_cost'))

            resource_sw_total = sum(self.software_resource_ids.mapped('total_cost'))
            resource_social_total = sum(self.social_resource_ids.mapped('total_cost'))
            resource_consultancy_total = sum(self.consulatncy_resource_ids.mapped('total_cost'))
            resource_staffing_total = sum(self.staffing_resource_ids.mapped('total_cost'))

            ancillary_tpa_total = sum(self.third_party_audit_ids.mapped('cost'))
            ancillary_ssl_total = sum(self.ancillary_ids.filtered(lambda anc: anc.ancillary_id.name == "SSL Certificate").mapped('cost'))
            ancillary_dsign_total = sum(self.ancillary_ids.filtered(lambda anc: anc.ancillary_id.name == "Digital Signature").mapped('cost'))
            ancillary_des_total = sum(self.domain_email_sms_ids.mapped('cost'))
            ancillary_mas_total = sum(self.mobile_app_store_ids.mapped('cost'))
            ancillary_sd_total = sum(self.survey_degitalisation_ids.mapped('cost'))
            ancillary_reimb_total = sum(self.reimbursement_ids.mapped('cost'))
            ancillary_sps_total = sum(self.strategic_partner_sharing_ids.mapped('cost'))
            ancillary_external_total = sum(self.external_ancillary_ids.mapped('cost'))

            infra_external_total = sum(self.it_infra_puchase_ids.mapped('purchase_cost'))
            infra_hardware_purchace_total = sum(self.computer_hardware_ids.mapped('purchase_cost'))
            infra_licence_purchace_total = sum(self.software_licence_ids.mapped('purchase_cost'))
            infra_hardware_maintenance_total = sum(self.computer_hardware_ids.mapped('maintenance_cost'))
            infra_licence_maintenance_total = sum(self.software_licence_ids.mapped('maintenance_cost'))
            c3=c4 =c5=c6=c7=c8=c9=c10=0
            for res in self.pbg_implementation_ids:
                if res.code == 'BG':
                    res.implementation_value =  (res.implementation_percentage/100) * self.revised_eq_approved
                    c3 = res.implementation_value
                elif res.code == 'BCQ':
                    res.implementation_value = c3 * res.implementation_percentage/100
                    c4 = res.implementation_value
                elif res.code == 'FDA':
                    res.implementation_value = c3 * res.implementation_percentage/100
                    c5 = res.implementation_value
                elif res.code == 'IFD':
                    res.implementation_value = c5 * res.implementation_percentage/100
                    c6 = res.implementation_value
                elif res.code == 'ICC':
                    res.implementation_value = c5 * res.implementation_percentage/100 
                    c7 = res.implementation_value
                elif res.code=='NQ':
                    c8 =  res.implementation_value
                elif res.code == 'TBCBG':
                    res.implementation_value = c4 *c8
                    c10 = res.implementation_value
                elif res.code == 'DI':
                    res.implementation_value =( c7-c6)/4*(c8) if c8 >0 else 0
                    c9 = res.implementation_value
            self.pbg_implement = c9 + c10
            
            s3 = s4 = s5 = s6 =  s7 = s8 =  s9 = s10 = 0

            for val in self.pbg_support_ids:
                if val.code == 'BG':
                    val.support_value =  (val.support_percentage/100) * self.revised_eq_approved
                    s3 = val.support_value
                elif val.code == 'BCQ':
                    val.support_value = s3 * val.support_percentage/100
                    s4 = val.support_value
                elif val.code == 'FDA':
                    val.support_value = s3 * val.support_percentage/100
                    s5 = val.support_value
                elif val.code == 'IFD':
                    val.support_value = s5 * val.support_percentage/100
                    s6 = val.support_value
                elif val.code == 'ICC':
                    val.support_value = s5 * val.support_percentage/100 
                    s7 = val.support_value
                elif val.code=='NQ':
                    s8 =  val.support_value
                elif val.code == 'TBCBG':
                    val.support_value = s4 *s8
                    s10 = val.support_value
                elif val.code == 'DI':
                    val.support_value = (s7-s6)/4*(s8)  if s8 > 0  else 0
                    s9 =  val.support_value 
            self.pbg_support = s9 + s10
            for rec in self.estimate_ids:
                rec.revised_purchase_cost = 0
                rec.revised_production_overhead = 0
                rec.revised_logistic_cost = 0
                rec.revised_company_overhead = 0
                rec.revised_total_profit_overhead = 0
                if rec.code == "ADC":
                    overhead_percentages = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', 'in', ['production', 'company']),('effective_date','<=',date.today())])
                    purchase_cost = software_total + functional_total
                    production_overhead = purchase_cost * (overhead_percentages.filtered(lambda p: p.overhead_type == 'production').percentage / 100)
                    logistic_cost = ancillary_impl_total + self.pbg_implement
                    overhead_percentage = overhead_percentages.filtered(lambda p: p.overhead_type == 'company').percentage / 100
                    company_percentage = overhead_percentages.filtered(lambda p: p.overhead_type == 'company').company_ovhead_percentage / 100
                    company_overhead = (purchase_cost + production_overhead + logistic_cost) / overhead_percentage * company_percentage if overhead_percentage != 0 else 0
                    profit_percentage = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'ADC'),('effective_date','<=',date.today())]).total_profit_percentage / 100
                    total_profit_overhead = self.calculate_round_amount((purchase_cost + production_overhead + logistic_cost + company_overhead) * profit_percentage)
                    rec.revised_purchase_cost = purchase_cost
                    rec.revised_production_overhead = production_overhead
                    rec.revised_logistic_cost = logistic_cost
                    rec.revised_company_overhead = company_overhead
                    rec.revised_total_profit_overhead = total_profit_overhead
                    self.assign_purchase_cost()
                elif rec.code == "AWMS":
                    overhead_percentages = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', 'in', ['production', 'company']),('effective_date','<=',date.today())])
                    p_cost = software_total + functional_total
                    purchase_cost = p_cost * float(self.maintenance_percentage1) / 100 * self.maintenance_period
                    logistic_cost = ancillary_support_total + self.pbg_support
                    production_overhead = purchase_cost * (overhead_percentages.filtered(lambda p: p.overhead_type == 'production').percentage / 100)
                    overhead_percentage = overhead_percentages.filtered(lambda p: p.overhead_type == 'company').percentage / 100
                    company_percentage = overhead_percentages.filtered(lambda p: p.overhead_type == 'company').company_ovhead_percentage / 100
                    company_overhead = (purchase_cost + production_overhead + logistic_cost) / overhead_percentage * company_percentage if overhead_percentage != 0 else 0
                    profit_percentage = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'AWMS'),('effective_date','<=',date.today())]).total_profit_percentage / 100
                    total_profit_overhead = self.calculate_round_amount((purchase_cost + production_overhead + logistic_cost + company_overhead) * profit_percentage)
                    rec.revised_purchase_cost = purchase_cost
                    rec.revised_production_overhead = production_overhead
                    rec.revised_logistic_cost = logistic_cost
                    rec.revised_company_overhead = company_overhead
                    rec.revised_total_profit_overhead = total_profit_overhead
                    self.assign_purchase_cost()
                elif rec.code == "AWMA":
                    overhead_percentages = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', 'in', ['production', 'company']),('effective_date','<=',date.today())])
                    purchase_cost = software_support_total + functional_support_total
                    production_overhead = purchase_cost * (overhead_percentages.filtered(lambda p: p.overhead_type == 'production').percentage / 100)
                    overhead_percentage = overhead_percentages.filtered(lambda p: p.overhead_type == 'company').percentage / 100
                    company_percentage = overhead_percentages.filtered(lambda p: p.overhead_type == 'company').company_ovhead_percentage / 100
                    company_overhead = (purchase_cost + production_overhead) / overhead_percentage * company_percentage if overhead_percentage != 0 else 0
                    profit_percentage = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'AWMA'),('effective_date','<=',date.today())]).total_profit_percentage / 100
                    total_profit_overhead = self.calculate_round_amount((purchase_cost + production_overhead + company_overhead) * profit_percentage)
                    rec.revised_purchase_cost = purchase_cost
                    rec.revised_production_overhead = production_overhead
                    rec.revised_company_overhead = company_overhead
                    rec.revised_total_profit_overhead = total_profit_overhead
                    self.assign_purchase_cost()
                elif rec.code == "CS":
                    rec.revised_purchase_cost = consultancy_total
                    percentcal2 = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', '=', 'company'),('effective_date','<=',date.today())])
                    overhead_percentage = percentcal2.percentage/100
                    company_percentage = percentcal2.company_ovhead_percentage/100
                    rec.revised_company_overhead = ((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost) / overhead_percentage) * company_percentage if overhead_percentage != 0 else 0
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CS'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "CI":
                    rec.revised_purchase_cost = consultancy_IT_total
                    percentcal2 = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', '=', 'company'),('effective_date','<=',date.today())])
                    overhead_percentage = percentcal2.percentage/100
                    company_percentage = percentcal2.company_ovhead_percentage/100
                    rec.revised_company_overhead = ((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost) / overhead_percentage) * company_percentage if overhead_percentage != 0 else 0
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CI'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "CSM":
                    rec.revised_purchase_cost = consultancy_social_total
                    percentcal2 = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', '=', 'company'),('effective_date','<=',date.today())])
                    overhead_percentage = percentcal2.percentage/100
                    company_percentage = percentcal2.company_ovhead_percentage/100
                    rec.revised_company_overhead = ((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost) / overhead_percentage) * company_percentage if overhead_percentage != 0 else 0
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CSM'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "SS":
                    rec.revised_purchase_cost = resource_sw_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SS'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "SM":
                    rec.revised_purchase_cost = resource_social_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SM'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "CONS":
                    rec.revised_purchase_cost = resource_consultancy_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CONS'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "SSV":
                    rec.revised_purchase_cost = resource_staffing_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SSV'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "TPA":
                    rec.revised_purchase_cost = ancillary_tpa_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'TPA'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "SSL":
                    rec.revised_purchase_cost = ancillary_ssl_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SSL'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "DS":
                    rec.revised_purchase_cost = ancillary_dsign_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'DS'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount(self.calculate_round_amount(rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "DES":
                    rec.revised_purchase_cost = ancillary_des_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'DES'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "MAS":
                    rec.revised_purchase_cost = ancillary_mas_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'MAS'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "SD":
                    rec.revised_purchase_cost = ancillary_sd_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SD'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "REIMB":
                    rec.revised_purchase_cost = ancillary_reimb_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'REIMB'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "SPS":
                    rec.revised_purchase_cost = ancillary_sps_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SPS'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "EES":
                    rec.revised_purchase_cost = ancillary_external_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'EES'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                elif rec.code == "EC":
                    rec.revised_purchase_cost = infra_external_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'EC'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "SCH":
                    rec.revised_purchase_cost = infra_hardware_purchace_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SCH'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "SSLC":
                    rec.revised_purchase_cost = infra_licence_purchace_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SSLC'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "MCH":
                    rec.revised_purchase_cost = infra_hardware_maintenance_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'MCH'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
                elif rec.code == "MSLC":
                    rec.revised_purchase_cost = infra_licence_maintenance_total
                    percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'MSLC'),('effective_date','<=',date.today())])
                    profit_percentage = percentcal3.total_profit_percentage/100
                    rec.revised_total_profit_overhead =self.calculate_round_amount((rec.revised_purchase_cost + rec.revised_production_overhead + rec.revised_logistic_cost + rec.revised_company_overhead) * profit_percentage)
                    self.assign_purchase_cost()
            self.revised_proposed_eq = sum(self.estimate_ids.mapped('revised_total_profit_overhead'))
            self.revised_margin_adjustment = self.revised_eq_approved - self.revised_proposed_eq
            sum_of_purchace_cost = sum(self.estimate_ids.mapped('revised_purchase_cost'))
            sum_of_prod_overhead = sum(self.estimate_ids.mapped('revised_production_overhead'))
            sum_of_logistic_cost = sum(self.estimate_ids.mapped('revised_logistic_cost'))
            sum_of_company_overhead = sum(self.estimate_ids.mapped('revised_company_overhead'))
            self.revised_actual_margin = (self.revised_proposed_eq - sum_of_purchace_cost - sum_of_prod_overhead - sum_of_logistic_cost - sum_of_company_overhead) + self.revised_margin_adjustment
            self.revised_gross_profit_margin = (self.revised_actual_margin / self.revised_eq_approved) * 100 if self.revised_eq_approved != 0 else 0
            self.revised_bid_value_without_tax = self.revised_eq_approved / self.revised_exchange_rate_to_inr if self.revised_exchange_rate_to_inr != 0 else 0
            resource_internal_total = sum(float(item.resource_internal) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.resource_internal) for item in self.op_year_ids if "OP M" in item.time_line)
            total_inception6 = sum(float(item.inception) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.inception) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_srs6 = sum(float(item.srs) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.srs) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_uat6 = sum(float(item.uat) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.uat) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_golive6 = sum(float(item.golive) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.golive) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_delivery6 = sum(float(item.delivery) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.delivery) for item in self.op_year_ids if "OP M" in item.time_line)  
            total_o_and_m6 = sum(float(item.o_and_m) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.o_and_m) for item in self.op_year_ids if "OP M" in item.time_line)  
            total_milestone7 = sum(float(item.milestone7) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.milestone7) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_milestone8 = sum(float(item.milestone8) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.milestone8) for item in self.op_year_ids if "OP M" in item.time_line)
            total_milestone9 = sum(float(item.milestone9) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.milestone9) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_milestone10 = sum(float(item.milestone10) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.milestone10) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_milestone11 = sum(float(item.milestone11) for item in self.op_year_ids if "OP M" in item.time_line)  
            total_milestone12 = sum(float(item.milestone12) for item in self.op_year_ids if "OP M" in item.time_line)  
            total_resource_internal6 = sum(float(item.resource_internal) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.resource_internal) for item in self.op_year_ids if "OP M" in item.time_line)
            total_resource_external6 = sum(float(item.resource_external) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.resource_external) for item in self.op_year_ids if "OP M" in item.time_line)
            total_it_infra6 = sum(float(item.it_infra) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.it_infra) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_ancillary6 = sum(float(item.ancillary) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.ancillary) for item in self.op_year_ids if "OP M" in item.time_line) 
            total_others6 = sum(float(item.others) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
            sum(float(item.others) for item in self.op_year_ids if "OP M" in item.time_line) 
       

            initial_value = '0'
            closure_closing_balance = '0'
            for month in range(1, int(self.month)+1):
                cap_m_resource_internal = next((float(rec.resource_internal) for rec in self.cap_year_ids if rec.time_line == f"CAP M{month}"), 0)
                op_m_resource_internal = next((float(rec.resource_internal) for rec in self.op_year_ids if rec.time_line == f"OP M{month}"), 0)
                for rec in self.cap_year_ids:
                    if month == 1:
                        previous_closing_balance = initial_value
                    else:
                        previous_closing_balance = next((float(rec.closing_balance) for rec in self.cap_year_ids if rec.time_line == f"CAP M{month-1}"), 0)
                    if rec.time_line == f"CAP M{month}":
                        purchase_costs = self.assign_purchase_cost()
                        rec.opening_balance = previous_closing_balance
                        rec.total_inflow = (float(rec.inception) + float(rec.srs) + float(rec.uat) + float(rec.golive) + 
                                            float(rec.delivery) + float(rec.o_and_m) + float(rec.milestone7) +float(rec.milestone8) +float(rec.milestone9) + float(rec.milestone10))
                        rec.resource_internal = purchase_costs['irc1'] / self.month
                        rec.ancillary = (purchase_costs['anc1'] / (self.op_month + self.month)) if (self.op_month + self.month) > 0 else 0
                        if resource_internal_total != 0:
                            rec.coh = cap_m_resource_internal / resource_internal_total * purchase_costs['coh1']
                            rec.total_outflow = (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) +
                                            float(rec.ancillary) + float(rec.coh) + float(rec.others) )
                            rec.closing_balance = (float(rec.opening_balance) + float(rec.total_inflow) - float(rec.total_outflow))
                        else:
                            rec.coh = '0'
                            rec.total_outflow = (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) +
                                            float(rec.ancillary) + float(rec.coh) + float(rec.others) )
                            rec.closing_balance = (float(rec.opening_balance) + float(rec.total_inflow) - float(rec.total_outflow))
                        final_closing_balance = float(rec.closing_balance)
                        total_coh = sum(float(item.coh) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_resource_internal = sum(float(item.resource_internal) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_inception = sum(float(item.inception) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_srs = sum(float(item.srs) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_uat = sum(float(item.uat) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_golive = sum(float(item.golive) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_delivery = sum(float(item.delivery) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_o_and_m = sum(float(item.o_and_m) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_milestone7 = sum(float(item.milestone7) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_milestone8 = sum(float(item.milestone8) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_milestone9 = sum(float(item.milestone9) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_milestone10 = sum(float(item.milestone10) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_resource_external = sum(float(item.resource_external) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_it_infra = sum(float(item.it_infra) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_ancillary = sum(float(item.ancillary) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_others = sum(float(item.others) for item in self.cap_year_ids if "CAP M" in item.time_line)
                        total_internal = sum(float(item.resource_internal) for item in self.cap_year_ids if "CAP M" in item.time_line)
                    elif rec.time_line == f"CAP Closure":
                        rec.opening_balance = final_closing_balance
                        rec.inception = total_inception
                        rec.srs = total_srs
                        rec.uat = total_uat
                        rec.golive = total_golive
                        rec.delivery = total_delivery
                        rec.o_and_m = total_o_and_m
                        rec.milestone7 = total_milestone7
                        rec.milestone8 = total_milestone8
                        rec.milestone9 = total_milestone9
                        rec.milestone10 = total_milestone10
                        rec.total_inflow = (float(rec.inception) + float(rec.srs) + float(rec.uat) + float(rec.golive) + 
                                            float(rec.delivery) + float(rec.o_and_m) + float(rec.milestone7) +float(rec.milestone8) +float(rec.milestone9) + float(rec.milestone10))
                        rec.resource_internal = total_resource_internal
                        rec.resource_external = total_resource_external
                        rec.it_infra = total_it_infra
                        rec.ancillary = total_ancillary
                        rec.coh = total_coh
                        rec.others = total_others
                        rec.total_outflow =  (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) + float(rec.ancillary) + float(rec.coh) + float(rec.others))
                        rec.closing_balance = rec.opening_balance
                        closure_closing_balance = float(rec.closing_balance)


            # FOR op_year_ids====================
            closure_closing_balance1 = 0
            it_infra_total_value = 0
            # final_closing_balance2 = 0
            for month in range(1, int(self.op_month)+2):
                op_m_resource_internal = next((float(rec.resource_internal) for rec in self.op_year_ids if rec.time_line == f"OP M{month}"), 0)
                if month == 1:
                    previous_closing_balance1 = closure_closing_balance
                else:
                    previous_closing_balance1 = next((float(rec.closing_balance) for rec in self.op_year_ids if rec.time_line == f"OP M{month-1}"), 0)
                final_closing_balance2 = 0
                for rec in self.op_year_ids:
                    if rec.time_line == f"OP M{month}":
                        purchase_costs = self.assign_purchase_cost()
                        rec.opening_balance = previous_closing_balance1
                        rec.total_inflow = (float(rec.inception) + float(rec.srs) + float(rec.uat) + float(rec.golive) + 
                                            float(rec.delivery) + float(rec.o_and_m) + float(rec.milestone7) +float(rec.milestone8) +float(rec.milestone9) + float(rec.milestone10) + float(rec.milestone11) + float(rec.milestone12))
                        rec.resource_internal = purchase_costs['iro1'] / self.op_month if self.op_month > 0 else 0
                        rec.resource_external = purchase_costs['ero1'] / self.op_month if self.op_month > 0 else 0
                        rec.ancillary = purchase_costs['anc1'] / (self.op_month + self.month) if (self.op_month + self.month) > 0 else 0
                        if resource_internal_total != 0:
                            rec.coh = op_m_resource_internal / resource_internal_total * purchase_costs['coh1']
                            rec.total_outflow = (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) +
                                            float(rec.ancillary) + float(rec.coh) + float(rec.others))
                            rec.closing_balance = (float(rec.opening_balance) + float(rec.total_inflow) - float(rec.total_outflow))
                        else:
                            rec.coh = '0'
                            rec.total_outflow = (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) +
                                            float(rec.ancillary) + float(rec.coh) + float(rec.others))
                            rec.closing_balance = (float(rec.opening_balance) + float(rec.total_inflow) - float(rec.total_outflow))
                        final_closing_balance1 = float(rec.closing_balance)
                        total_coh1 = sum(float(item.coh) for item in self.op_year_ids if "OP M" in item.time_line)
                        total_resource_internal_op = sum(float(item.resource_internal) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_resource_external_op = sum(float(item.resource_external) for item in self.op_year_ids if "OP M" in item.time_line)
                        total_inception_op = sum(float(item.inception) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_srs_op = sum(float(item.srs) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_uat_op = sum(float(item.uat) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_golive_op = sum(float(item.golive) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_delivery_op = sum(float(item.delivery) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_o_and_m_op = sum(float(item.o_and_m) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_milestone7_op = sum(float(item.milestone7) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_milestone8_op = sum(float(item.milestone8) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_milestone9_op = sum(float(item.milestone9) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_milestone10_op = sum(float(item.milestone10) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_milestone11_op = sum(float(item.milestone11) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_milestone12_op = sum(float(item.milestone12) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_it_infra_op = sum(float(item.it_infra) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_ancillary_op = sum(float(item.ancillary) for item in self.op_year_ids if "OP M" in item.time_line) 
                        total_coh_op = sum(float(item.coh) for item in self.op_year_ids if "OP M" in item.time_line)
                        total_others_op = sum(float(item.others) for item in self.op_year_ids if "OP M" in item.time_line)
                    if rec.time_line == f"Opex Closure":
                        rec.opening_balance = final_closing_balance1
                        rec.inception = total_inception_op
                        rec.srs = total_srs_op
                        rec.uat = total_uat_op
                        rec.golive = total_golive_op
                        rec.delivery = total_delivery_op
                        rec.o_and_m = total_o_and_m_op
                        rec.milestone7 = total_milestone7_op
                        rec.milestone8 = total_milestone8_op
                        rec.milestone9 = total_milestone9_op
                        rec.milestone10 = total_milestone10_op
                        rec.milestone11 = total_milestone11_op
                        rec.milestone12 = total_milestone12_op
                        rec.total_inflow = (float(rec.inception) + float(rec.srs) + float(rec.uat) + float(rec.golive) + 
                                            float(rec.delivery) + float(rec.o_and_m)+ float(rec.milestone7) +float(rec.milestone8) +float(rec.milestone9) + float(rec.milestone10) + float(rec.milestone11) + float(rec.milestone12))
                        rec.resource_internal = total_resource_internal_op
                        rec.resource_external = total_resource_external_op
                        rec.it_infra = total_it_infra_op
                        rec.ancillary = total_ancillary_op
                        rec.coh = total_coh_op
                        rec.others = total_others_op
                        rec.total_outflow = (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) + float(rec.ancillary) + float(rec.coh) + float(rec.others))
                        rec.closing_balance = rec.opening_balance
                        final_closing_balance2 = float(rec.closing_balance)
                    if rec.time_line == f"Project Closure":
                        purchase_costs = self.assign_purchase_cost()
                        rec.opening_balance = final_closing_balance2
                        rec.inception = total_inception6
                        rec.srs = total_srs6
                        rec.uat = total_uat6
                        rec.golive = total_golive6
                        rec.delivery = total_delivery6
                        rec.o_and_m = total_o_and_m6
                        rec.milestone7 = total_milestone7
                        rec.milestone8 = total_milestone8
                        rec.milestone9 = total_milestone9
                        rec.milestone10 = total_milestone10
                        rec.milestone11 = total_milestone11
                        rec.milestone12 = total_milestone12
                        rec.total_inflow = (float(rec.inception) + float(rec.srs) + float(rec.uat) + float(rec.golive) + 
                                            float(rec.delivery) + float(rec.o_and_m)+ float(rec.milestone7) +float(rec.milestone8) +float(rec.milestone9) + float(rec.milestone10) + float(rec.milestone11) + float(rec.milestone12))
                        rec.resource_internal = total_resource_internal6
                        rec.resource_external = total_resource_external6
                        rec.it_infra = total_it_infra6
                        rec.ancillary = total_ancillary6
                        rec.coh = total_coh + total_coh1
                        rec.others = total_others6
                        rec.total_outflow = (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) + float(rec.ancillary) + float(rec.coh) + float(rec.others))
                        rec.closing_balance = rec.opening_balance
                        it_infra_total_value = rec.it_infra



    def assign_purchase_cost(self):
        purchase_cost_of_adc = sum(rec.revised_purchase_cost for rec in self.estimate_ids if rec.code == "ADC")
        purchase_cost_of_awma_awms = sum(rec.revised_purchase_cost for rec in self.estimate_ids if rec.code in ["AWMA", "AWMS"])
        purchase_cost_of_sscs = sum(rec.revised_purchase_cost for rec in self.estimate_ids if rec.code in ["SS", "SM","CONS","SSV"])
        purchase_cost_of_sch_sslc = sum(rec.revised_purchase_cost for rec in self.estimate_ids if rec.code in ["SCH", "SSLC"])
        purchase_cost_of_ec_mch_mslc = sum(rec.revised_purchase_cost for rec in self.estimate_ids if rec.code in ["EC", "MCH","MSLC"])
        purchase_cost_for_anc = sum(rec.revised_purchase_cost for rec in self.estimate_ids if rec.code in ["TPA", "SSL","DS","DES","MAS","SD","REIMB","SPS"])
        logistic_cost_for_anc = sum(rec.revised_logistic_cost for rec in self.estimate_ids if rec.code in ["ADC", "AWMS"])
        quote_total_amount = sum(self.quote_ids.mapped('amount'))
        irc1 = iro1 = ero1 = ic1 = io1 = anc1 = dc1 = mar1 = ctc1 = coh1 = erc1 =0
        for record in self.paticulars_ids:
            if record.code == "IRC":
                record.amount = purchase_cost_of_adc
                irc1 = record.amount
            elif record.code == "IRO":
                record.amount = purchase_cost_of_awma_awms
                iro1 = record.amount
            elif record.code == "ERO":
                record.amount = purchase_cost_of_sscs
                ero1 = record.amount
            elif record.code == "ERC":
                erc1 = record.amount
            elif record.code == "IC":
                record.amount = purchase_cost_of_sch_sslc
                ic1 = record.amount
            elif record.code == "IO":
                record.amount = purchase_cost_of_ec_mch_mslc
                io1 = record.amount
            elif record.code == "ANC":
                record.amount = logistic_cost_for_anc + purchase_cost_for_anc
                anc1 = record.amount
            elif record.code == "DC":
                record.amount = (irc1 + iro1 + ero1 + erc1 + ic1 + io1 + anc1)
                dc1 = record.amount
            elif record.code == "MAR":
                record.amount = self.revised_actual_margin
                mar1 = record.amount
            elif record.code == "CTC":
                record.amount = quote_total_amount - mar1
                ctc1 = record.amount
            elif record.code == "COH":
                record.amount = ctc1 - dc1
                coh1 = record.amount
        return {
        'irc1': irc1,
        'iro1': iro1,
        'ero1': ero1,
        'erc1': erc1,
        'ic1': ic1,
        'io1': io1,
        'anc1': anc1,
        'dc1': dc1,
        'mar1': mar1,
        'ctc1': ctc1,
        'coh1': coh1
    }


    @api.constrains('op_year_ids','paticulars_ids')
    def validate_it_infra(self):
        total_it_infra = sum(float(rec.it_infra) for rec in self.op_year_ids if rec.time_line == f"Project Closure")
        purchase_costs = self.assign_purchase_cost()
        if purchase_costs.get('ic1', 0) + purchase_costs.get('io1', 0) != total_it_infra:
            raise ValidationError("Total Expanditure is not matching")
        

    def btn_apply(self):
        if self.kw_oppertuinity_id.pm_id.id  == self.env.user.employee_ids.id:
            view_id = self.env.ref('kw_eq.eq_wizard_approve_form').id
            return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id, 'state':'applied','apply':'apply','type':'revision'}
        }
    def action_take_action(self):
        view_id = self.env.ref('kw_eq.kw_eq_revision_form').id
        return {
        'name':"Take Action",
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'kw_eq_revision',
        'res_id': self.id,
        'view_id': view_id,
        'type': 'ir.actions.act_window',
        'target': 'self',
        'context':{'create': False,'revision':True,'edit':True},
        
    }
    
    def btn_approve(self):
        if self.revised_eq_approved == 0:
            raise ValidationError("EQ Approved value can not be zero.")
        view_id = self.env.ref('kw_eq.eq_wizard_approve_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id,'approve':'approve','type':'revision','state':'submit','revision_approve':'revision_approve'}
        }
    def btn_forwarded(self):
        if self.revised_eq_approved == 0:
            raise ValidationError("EQ Approved value can not be zero.")
        view_id = self.env.ref('kw_eq.eq_wizard_approve_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id,'approve':'approve','type':'revision','state':'forward','revision_forward':'revision_forward'}
        }
        
    def btn_update_status(self):
        if self.state == 'forward':
            if not self.update_status:
                raise ValidationError('Kindly update the recommendation status!')
        view_id = self.env.ref('kw_eq.eq_wizard_approve_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id,'approve':'approve','type':'revision','state':'forward','update_status':self.update_status,'revision_rec':'revision_rec'}
        }

    def btn_reject(self):
        view_id = self.env.ref('kw_eq.eq_wizard_reject_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id,'revision_reject':'reject','state':'rejected'}
        }

    def btn_grant(self):
        if self.revised_eq_approved == 0:
            raise ValidationError("EQ Approved value can not be zero.")
        view_id = self.env.ref('kw_eq.eq_wizard_approve_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id,'approve':'approve','state':'grant'}
        }
    def btn_revert(self):
        view_id = self.env.ref('kw_eq.eq_wizard_reject_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'revision_id': self.id,'reject':'reject','revert':True}
        }