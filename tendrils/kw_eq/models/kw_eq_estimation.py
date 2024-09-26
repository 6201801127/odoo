from odoo import models, fields, api
import math
from math import floor,ceil
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
# from lxml import etree




class SoftwareEstimatation(models.Model):
    _name = 'kw_eq_estimation'
    _description = 'Estimation'
    _rec_name = 'kw_oppertuinity_id'


    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)
        
    def get_opp(self):
        emp_ids = self.env.user.employee_ids.ids
        data = self.env['crm.lead'].sudo().search([('type', '=', 'opportunity'),('stage_id.code', '=','opportunity'),('pac_status','=',3)])
        opp_list =[]
        if self.env.context.get('get_oppertunity'):
            for rec in data:
                if any(emp_id in [rec.pm_id.id, rec.reviewer_id.id, rec.ceo_id.id, rec.csg_head_id.id, rec.presales_id.id, rec.cso_id.id] for emp_id in emp_ids):
                    opp_list.append(rec.id)
        elif self.env.context.get('get_opp_workoder'):
            if self.env.user.has_group('kw_eq.group_eq_backlog'):
                data = self.env['crm.lead'].sudo().search([])
                opp_list = data.ids
        return [('id','in',opp_list)]
    
    def _get_type(self):
        if self.env.context.get('get_opp_workoder'):
            return 'backlog'
        else:
            return 'regular'
    def get_approval_type(self):
        if self.env.context.get('get_opp_workoder'):
            return 'new'

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(SoftwareEstimatation, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field[@name='op_year_ids']"):
    #             node.set('context', "{'limit': 700}")
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res
    
    # oppertunity_code = fields.Char('OppCode') 
    code = fields.Char()
    client_name = fields.Char(related='kw_oppertuinity_id.client_name')
    client_id = fields.Many2one('res.partner',string='Client Name') 
    kw_oppertuinity_id = fields.Many2one('crm.lead',string="Opportunity Code | Name", domain=get_opp)
    technology_ids = fields.One2many('kw_eq_software_development_config','estimation_id',string="Study, Development, Implementation & Support")
    functional_ids = fields.One2many('kw_eq_software_functional_config','estimation_id',string="Additional [Functional] > Long Term Basis Payroll" )
    consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','estimation_id',string="Estimate for Software Services > Consultancy" )
    it_infra_consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','it_infra_consultancy_id')
    social_consultancy_ids = fields.One2many('kw_eq_software_consultancy_config','social_consultancy_id')
    ancillary_ids = fields.One2many('kw_eq_ancillary_config','estimation_id',string="Ancillary Items" )
    external_ancillary_ids = fields.One2many('kw_eq_external_ancillary_config','estimation_id',string="External Expert Service [Out Source]" )
    software_resource_ids = fields.One2many('kw_eq_software_resource_config','estimation_id',string="Software Support" )
    social_resource_ids = fields.One2many('kw_eq_social_resource_config','estimation_id',string="Social Media Management" )
    consulatncy_resource_ids = fields.One2many('kw_eq_consulatncy_resource_config','estimation_id',string="Consultancy Service" )
    staffing_resource_ids = fields.One2many('kw_eq_staffing_resource_config','estimation_id',string="Staffing Service" )
    it_infra_puchase_ids = fields.One2many('kw_eq_it_infra_purchase_config','estimation_id',string="IT Infra (Purchase)" )
    estimate_ids = fields.One2many('kw_eq_estimate_details','estimation_id')
    total_operation_support_ids = fields.One2many('kw_eq_ancillary_config', 'total_operation_id')
    out_of_pocket_expenditure_ids = fields.One2many('kw_eq_ancillary_config', 'expanditure_id')
    third_party_audit_ids = fields.One2many('kw_eq_ancillary_config', 'third_party_id')
    reimbursement_ids = fields.One2many('kw_eq_ancillary_config', 'reimbursement_id')
    domain_email_sms_ids = fields.One2many('kw_eq_ancillary_config', 'domain_sms_id')
    strategic_partner_sharing_ids = fields.One2many('kw_eq_ancillary_config', 'strategic_partner_id')
    mobile_app_store_ids = fields.One2many('kw_eq_ancillary_config', 'mobile_app_id')
    survey_degitalisation_ids = fields.One2many('kw_eq_ancillary_config', 'survey_degitalisation_id')
    java_ids = fields.One2many('kw_eq_software_development_config', 'java_estimate_id')
    php_ids = fields.One2many('kw_eq_software_development_config', 'php_estimate_id')
    dot_net_core_ids = fields.One2many('kw_eq_software_development_config', 'core_estimate_id')
    mobile_app_ids = fields.One2many('kw_eq_software_development_config', 'mobile_estimate_id')
    odoo_ids = fields.One2many('kw_eq_software_development_config', 'odoo_estimate_id')
    tableau_ids = fields.One2many('kw_eq_software_development_config', 'tableu_estimate_id')
    sas_ids = fields.One2many('kw_eq_software_development_config', 'sas_estimate_id')
    etl_ids = fields.One2many('kw_eq_software_development_config', 'etl_estimate_id')
    first_year_value = fields.Float(string= "First Year")
    computer_hardware_ids = fields.One2many('kw_eq_computer_hardware_config','hardware_id',string="Computer Hardware")
    software_licence_ids = fields.One2many('kw_eq_software_licenses_config','license_id',string="Software Licenses - COTS")
    pbg_implementation_ids = fields.One2many('kw_eq_pbg_config', 'pbg_implementation_id')
    pbg_support_ids = fields.One2many('kw_eq_pbg_config', 'pbg_support_id')
    # maintenance_percentage = fields.Integer(string="Standard Maintenance %")
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
    level_1_id = fields.Many2one('hr.employee',string="Authority 1")
    level_2_id = fields.Many2one('hr.employee',string="Authority 2")
    level_3_id = fields.Many2one('hr.employee',string="Authority 3")
    level_4_id = fields.Many2one('hr.employee',string="Authority 4")
    level_5_id = fields.Many2one('hr.employee',string="Authority 5")
    level_6_id = fields.Many2one('hr.employee',string="Authority 6")
    level_1_role = fields.Char(compute="_compute_get_des",store=True)
    level_2_role = fields.Char(compute="_compute_get_des",store=True)
    level_3_role = fields.Char(compute="_compute_get_des",store=True)
    level_4_role = fields.Char(compute="_compute_get_des",store=True)
    level_5_role = fields.Char(compute="_compute_get_des",store=True)
    level_6_role = fields.Char(compute="_compute_get_des",store=True)
    state = fields.Selection(string="Status",selection=[('version_1', 'Version 1'), ('version_2', 'Version 2'),('version_3', 'Version 3'),('version_4', 'Version 4'),('version_5', 'Version 5'),('version_6', 'Version 6'),('grant','Grant')],default="version_1")
    level_1_bool = fields.Boolean(compute="_compute_user_access")
    level_2_bool = fields.Boolean(compute="_compute_user_access")
    level_3_bool = fields.Boolean(compute="_compute_user_access")
    level_4_bool = fields.Boolean(compute="_compute_user_access")
    level_5_bool = fields.Boolean(compute="_compute_user_access")
    level_6_bool = fields.Boolean(compute="_compute_user_access")
    action_log_ids = fields.One2many('eq_log', 'eq_id', string='Action Log Table')
    eq_log_ids = fields.One2many('eq_log','eq_id')
    approval_type = fields.Selection([('new', 'New'), ('extension', 'Extension'),('change', 'Change'),('revision','Revision')],string="Approval Type",default=get_approval_type)
    page_software_bool = fields.Boolean(compute='compute_page_access')
    page_consultancy_bool = fields.Boolean(compute='compute_page_access')
    page_resource_bool = fields.Boolean(compute='compute_page_access')
    page_ancillary_bool = fields.Boolean(compute='compute_page_access')
    page_it_infra_bool = fields.Boolean(compute='compute_page_access')
    page_estimate_bool = fields.Boolean(compute='compute_page_access')
    page_pbg_bool = fields.Boolean(compute='compute_page_access')
    page_log_bool = fields.Boolean(compute='compute_page_access')
    page_ancillary_opx_bool = fields.Boolean(compute='compute_page_access')
    pending_at = fields.Char(string="Pending At")
    effective_from = fields.Date(string="Effective Date")
    page_cashflow_bool = fields.Boolean(compute='compute_page_access')
    month = fields.Integer(string = 'CAP Month')
    op_month = fields.Integer(string = 'OP Month')
    milestone_total = fields.Integer(string = 'Milestone Total',default=10)
    quote_ids = fields.One2many('kw_eq_quote_config','quote_id')
    paticulars_ids = fields.One2many('kw_eq_paticulars_config','paticular_id')
    deliverable_ids = fields.One2many('kw_eq_deliverable_config','deliverable_id')
    op_year_ids = fields.One2many('kw_eq_cashflow_config','op_year_id')
    cap_year_ids = fields.One2many('kw_eq_cashflow_config','cap_year_id')
    action = fields.Char('Action')
    details = fields.Char(string="Details")
    type = fields.Selection(
    string="Type",
    selection=[('regular', 'Regular'), ('backlog', 'Backlog')],
    default=lambda self: self._get_type()
    )

    
    revision_status = fields.Char()

    @api.onchange('month','op_month')
    def _onchange_year(self):
        if self.month:
            months = self.month
            lines = [(5, 0, 0)]
            lines.append((0, 0, {
                'time_line': 'Deliverables',
                'opening_balance': '',
            }))
            lines.append((0, 0, {
                'time_line': 'Payment term %',
                'opening_balance': '',
            }))
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

    # @api.onchange('milestone_total')
    # def get_deliverables(self):
    #     if self.milestone_total:
    #         milestones = self.milestone_total
    #         lines = [(5, 0, 0)]
    #         for milestone in range(1, milestones + 1):
    #             lines.append((0, 0, {
    #                 'milestones': f'Milestone {milestone}',
    #             }))
    #         self.deliverable_ids = lines
    #     else:
    #         self.deliverable_ids = [(5, 0, 0)]

    def btn_revise_eq(self):
        eq_rev = self.env['kw_eq_revision'].sudo().search([('estimation_id','=',self.id),('state','not in',('grant','rejected'))])
        if not eq_rev:
            approval_record = self.env['kw_eq_approval_configuration'].sudo().search([('approval_type','=','revision'),('effective_date','<=',date.today())],order='effective_date desc',limit=1)
            level_to_id = {
                "project_manager": self.kw_oppertuinity_id.pm_id.id,
                "reviewer": self.kw_oppertuinity_id.reviewer_id.id,
                "ceo": self.kw_oppertuinity_id.ceo_id.id,
                "csg_head": self.kw_oppertuinity_id.csg_head_id.id,
                "presales": self.kw_oppertuinity_id.presales_id.id,
                "cso": self.kw_oppertuinity_id.cso_id.id,
                "cfo": self.kw_oppertuinity_id.cfo_id.id,
            }
            revised_level_1_id = level_to_id.get(approval_record.level_1)
            revised_level_2_id = level_to_id.get(approval_record.level_2)
            revised_level_3_id = level_to_id.get(approval_record.level_3)
            revised_level_4_id = level_to_id.get(approval_record.level_4)
            revised_level_5_id = level_to_id.get(approval_record.level_5)
            revised_level_6_id= level_to_id.get(approval_record.level_6)
            if revised_level_1_id == self.env.user.employee_ids.id:
                revised_number = len(self.env['kw_eq_revision'].sudo().search([('estimation_id','=',self.id),('state','not in',('draft','rejected'))]))+1
                var = self.env['kw_eq_revision'].sudo().create({
                    'revision_status':f'Revision {revised_number}',
                    'eq_status':'revision',
                    'client_id' : self.client_id.id,
                    'kw_oppertuinity_id' :self.kw_oppertuinity_id.id,
                    'code':self.kw_oppertuinity_id.code,
                    'revised_level_1_id' :revised_level_1_id,
                    'revised_level_2_id' :revised_level_2_id,
                    'revised_level_3_id' :revised_level_3_id,
                    'revised_level_4_id' :revised_level_4_id,
                    'revised_level_5_id' :revised_level_5_id,
                    'revised_level_6_id' :revised_level_6_id,
                    'technology_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.technology_ids] if self.technology_ids else False,
                    'java_ids': [[0, 0, {
                                    'java_estimate_revision_id': r.java_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.java_ids] if self.java_ids else False,
                    'php_ids': [[0, 0, {
                                    'php_estimate_revision_id': r.php_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.php_ids] if self.php_ids else False,
                    'dot_net_core_ids': [[0, 0, {
                                    'core_estimate_revision_id': r.core_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.dot_net_core_ids] if self.dot_net_core_ids else False,
                    'mobile_app_ids': [[0, 0, {
                                    'mobile_estimate_revision_id': r.mobile_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.mobile_app_ids] if self.mobile_app_ids else False,
                    'odoo_ids': [[0, 0, {
                                    'odoo_estimate_revision_id': r.odoo_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.odoo_ids] if self.odoo_ids else False,
                    'tableau_ids': [[0, 0, {
                                    'tableu_estimate_revision_id': r.tableu_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.tableau_ids] if self.tableau_ids else False,
                    'sas_ids': [[0, 0, {
                                    'sas_estimate_revision_id': r.sas_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.sas_ids] if self.sas_ids else False,
                    'etl_ids': [[0, 0, {
                                    'etl_estimate_revision_id': r.etl_estimate_revision_id.id,
                                    'skill_id': r.skill_id.id,
                                    'designation_id': r.designation_id.id,
                                    'experience': r.experience,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_cost': r.implementation_total_cost,
                                    'support_total_cost': r.support_total_cost,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.etl_ids] if self.etl_ids else False,
                    'functional_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'designation_id': r.designation_id.id,
                                    'other_item': r.other_item,
                                    'implementation_man_month': r.implementation_man_month,
                                    'support_man_month': r.support_man_month,
                                    'implementation_total_ctc': r.implementation_total_ctc,
                                    'support_total_ctc': r.support_total_ctc,
                                    'ctc': r.ctc,
                                    'remark':r.remark,
                                }] for r in self.functional_ids] if self.functional_ids else False,
                    'consultancy_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'consultancy_type': r.consultancy_type,
                                    'designation_id': r.designation_id.id,
                                    'other_item': r.other_item,
                                    'experience_proposed': r.experience_proposed,
                                    'man_month_rate': r.man_month_rate,
                                    'man_month_effort': r.man_month_effort,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.consultancy_ids] if self.consultancy_ids else False,
                    'it_infra_consultancy_ids': [[0, 0, {
                                    'it_infra_revision_id': r.it_infra_revision_id.id,
                                    'consultancy_type': r.consultancy_type,
                                    'designation_id': r.designation_id.id,
                                    'other_item': r.other_item,
                                    'experience_proposed': r.experience_proposed,
                                    'man_month_rate': r.man_month_rate,
                                    'man_month_effort': r.man_month_effort,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.it_infra_consultancy_ids] if self.it_infra_consultancy_ids else False,
                    'social_consultancy_ids': [[0, 0, {
                                    'social_revision_id': r.social_revision_id.id,
                                    'consultancy_type': r.consultancy_type,
                                    'designation_id': r.designation_id.id,
                                    'other_item': r.other_item,
                                    'experience_proposed': r.experience_proposed,
                                    'man_month_rate': r.man_month_rate,
                                    'man_month_effort': r.man_month_effort,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.social_consultancy_ids] if self.social_consultancy_ids else False,
                    'software_resource_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'resource_deploy_duration': r.resource_deploy_duration,
                                    'average_percentage':r.average_percentage,
                                    'first_year': r.first_year,
                                    'average': r.average,
                                    'skill': r.skill,
                                    'qualification': r.qualification,
                                    'resources': r.resources,
                                    'man_month': r.man_month,
                                    'ctc': r.ctc,
                                    'ope_month': r.ope_month,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.software_resource_ids] if self.software_resource_ids else False,
                    'social_resource_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'resource_deploy_duration': r.resource_deploy_duration,
                                    'average_percentage':r.average_percentage,
                                    'first_year': r.first_year,
                                    'average': r.average,
                                    'skill': r.skill,
                                    'qualification': r.qualification,
                                    'resources': r.resources,
                                    'man_month': r.man_month,
                                    'ctc': r.ctc,
                                    'ope_month': r.ope_month,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.social_resource_ids] if self.social_resource_ids else False,
                    'consulatncy_resource_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'resource_deploy_duration': r.resource_deploy_duration,
                                    'average_percentage':r.average_percentage,
                                    'first_year': r.first_year,
                                    'average': r.average,
                                    'skill': r.skill,
                                    'qualification': r.qualification,
                                    'resources': r.resources,
                                    'man_month': r.man_month,
                                    'ctc': r.ctc,
                                    'ope_month': r.ope_month,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.consulatncy_resource_ids] if self.consulatncy_resource_ids else False,
                    'staffing_resource_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'resource_deploy_duration': r.resource_deploy_duration,
                                    'average_percentage':r.average_percentage,
                                    'first_year': r.first_year,
                                    'average': r.average,
                                    'skill': r.skill,
                                    'qualification': r.qualification,
                                    'resources': r.resources,
                                    'man_month': r.man_month,
                                    'ctc': r.ctc,
                                    'ope_month': r.ope_month,
                                    'total_cost': r.total_cost,
                                    'remark':r.remark,
                                }] for r in self.staffing_resource_ids] if self.staffing_resource_ids else False,
                    'third_party_audit_ids': [[0, 0, {
                                    'third_party_revision_id': r.third_party_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.third_party_audit_ids] if self.third_party_audit_ids else False,
                    'reimbursement_ids': [[0, 0, {
                                    'reimbursement_revision_id': r.reimbursement_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.reimbursement_ids] if self.reimbursement_ids else False,
                    'strategic_partner_sharing_ids': [[0, 0, {
                                    'strategic_partner_revision_id': r.strategic_partner_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.strategic_partner_sharing_ids] if self.strategic_partner_sharing_ids else False,
                    'domain_email_sms_ids': [[0, 0, {
                                    'domain_sms_revision_id': r.domain_sms_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.domain_email_sms_ids] if self.domain_email_sms_ids else False,
                    'mobile_app_store_ids': [[0, 0, {
                                    'mobile_app_revision_id': r.mobile_app_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.mobile_app_store_ids] if self.mobile_app_store_ids else False,
                    'survey_degitalisation_ids': [[0, 0, {
                                    'survey_degitalisation_revision_id': r.survey_degitalisation_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.survey_degitalisation_ids] if self.survey_degitalisation_ids else False,
                    'ancillary_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                }] for r in self.ancillary_ids] if self.ancillary_ids else False,
                    'out_of_pocket_expenditure_ids': [[0, 0, {
                                    'expanditure_revision_id': r.expanditure_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                    'sort_no': r.sort_no,
                                }] for r in self.out_of_pocket_expenditure_ids] if self.out_of_pocket_expenditure_ids else False,
                    'total_operation_support_ids': [[0, 0, {
                                    'total_operation_revision_id': r.total_operation_revision_id.id,
                                    'ancillary_id': r.ancillary_id.id,
                                    'item': r.item,
                                    'other_item': r.other_item,
                                    'unit': r.unit,
                                    'rate': r.rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'remark':r.remark,
                                    'sort_no': r.sort_no,
                                }] for r in self.total_operation_support_ids] if self.total_operation_support_ids else False,
                    'external_ancillary_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'designation_id': r.designation_id.id,
                                    'other_item': r.other_item,
                                    'man_month_rate': r.man_month_rate,
                                    'qty': r.qty,
                                    'cost': r.cost,
                                    'sort_no': r.sort_no,
                                    'remark':r.remark,
                                }] for r in self.external_ancillary_ids] if self.external_ancillary_ids else False, 
                    'it_infra_puchase_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'infra_id': r.infra_id.id,
                                    'other_item': r.other_item,
                                    'description': r.description,
                                    'purchase_unit': r.purchase_unit,
                                    'purchase_rate': r.purchase_rate,
                                    'purchase_qty': r.purchase_qty,
                                    'purchase_cost': r.purchase_cost,
                                    'remark':r.remark,
                                }] for r in self.it_infra_puchase_ids] if self.it_infra_puchase_ids else False,
                    'computer_hardware_ids': [[0, 0, {
                                    'hardware_revision_id': r.hardware_revision_id.id,
                                    'item': r.item,
                                    'description': r.description,
                                    'purchase_unit': r.purchase_unit,
                                    'purchase_rate': r.purchase_rate,
                                    'purchase_qty': r.purchase_qty,
                                    'purchase_cost': r.purchase_cost,
                                    'maintenance_unit': r.maintenance_unit,
                                    'maintenance_rate': r.maintenance_rate,
                                    'maintenance_qty': r.maintenance_qty,
                                    'maintenance_cost': r.maintenance_cost,
                                    'remark':r.remark,
                                }] for r in self.computer_hardware_ids] if self.computer_hardware_ids else False,
                    'software_licence_ids': [[0, 0, {
                                    'license_revision_id': r.license_revision_id.id,
                                    # 'license_id': r.license_id.id,
                                    'item': r.item,
                                    'description': r.description,
                                    'purchase_unit': r.purchase_unit,
                                    'purchase_rate': r.purchase_rate,
                                    'purchase_qty': r.purchase_qty,
                                    'purchase_cost': r.purchase_cost,
                                    'maintenance_unit': r.maintenance_unit,
                                    'maintenance_rate': r.maintenance_rate,
                                    'maintenance_qty': r.maintenance_qty,
                                    'maintenance_cost': r.maintenance_cost,
                                    'remark':r.remark,
                                }] for r in self.software_licence_ids] if self.software_licence_ids else False,
                    'estimate_ids': [[0, 0, {
                                    'revision_id': r.revision_id.id,
                                    'account_head_id': r.account_head_id.id,
                                    'account_subhead_id': r.account_subhead_id.id,
                                    'purchase_cost': r.purchase_cost,
                                    'production_overhead': r.production_overhead,
                                    'logistic_cost': r.logistic_cost,
                                    'company_overhead': r.company_overhead,
                                    'total_profit_overhead': r.total_profit_overhead,
                                    'code': r.code,
                                    'sort_no': r.sort_no,
                                }] for r in self.estimate_ids] if self.estimate_ids else False,
                    'proposed_eq' : self.proposed_eq,
                    'maintenance_percentage1' : self.maintenance_percentage1,
                    'maintenance_period' : self.maintenance_period,
                    'eq_approved' : self.eq_approved,
                    'margin_adjustment' : self.margin_adjustment,
                    'actual_margin' : self.actual_margin,
                    'gross_profit_margin' : self.gross_profit_margin,
                    'bid_currency' : self.bid_currency,
                    'exchange_rate_to_inr' : self.exchange_rate_to_inr,
                    'bid_value_without_tax' : self.bid_value_without_tax,
                    'pbg_implementation_ids': [[0, 0, {
                                    'pbg_implementation_revision_id': r.pbg_implementation_revision_id.id,
                                    'item': r.item,
                                    'implementation_percentage': r.implementation_percentage,
                                    'implementation_value': r.implementation_value,
                                    'value_edit_bool': r.value_edit_bool,
                                    'percentage_edit_bool': r.percentage_edit_bool,
                                    'remark':r.remark,
                                    'code': r.code,
                                }] for r in self.pbg_implementation_ids] if self.pbg_implementation_ids else False,
                    'pbg_support_ids': [[0, 0, {
                                    'pbg_support_revision_id': r.pbg_support_revision_id.id,
                                    'item': r.item,
                                    'support_percentage': r.support_percentage,
                                    'support_value': r.support_value,
                                    'value_edit_bool': r.value_edit_bool,
                                    'percentage_edit_bool': r.percentage_edit_bool,
                                    'remark':r.remark,
                                    'code': r.code,
                                }] for r in self.pbg_support_ids] if self.pbg_support_ids else False,
                    'pbg_implement' : self.pbg_implement,
                    'pbg_support' : self.pbg_support,
                    # 'state' : self.state,
                    'estimation_id':self.id,
                    'date':datetime.now(),
                    'revised_eq_approved':self.eq_approved,
                    'month': self.month,
                    'op_month':self.op_month,
                    'milestone_total':self.milestone_total,
                    'quote_ids': [[0, 0, {
                                    'revision_quote_id': r.revision_quote_id.id,
                                    'paticulars': r.paticulars,
                                    'amount': r.amount,
                                }] for r in self.quote_ids] if self.quote_ids else False,
                    'paticulars_ids': [[0, 0, {
                                    'revision_paticular_id': r.revision_paticular_id.id,
                                    'paticulars_name': r.paticulars_name,
                                    'amount': r.amount,
                                }] for r in self.paticulars_ids] if self.paticulars_ids else False,
                    # 'deliverable_ids': [[0, 0, {
                    #                 'revision_deliverable_id': r.revision_deliverable_id.id,
                    #                 'milestones': r.milestones,
                    #                 'deliverables': r.deliverables,
                    #                 'payment_term': r.payment_term,
                    #                 'month': r.month,
                    #             }] for r in self.deliverable_ids] if self.deliverable_ids else False,
                    'op_year_ids': [[0, 0, {
                                    'revision_op_id': r.revision_op_id.id,
                                    'time_line': r.time_line,
                                    'opening_balance': r.opening_balance,
                                    'inception': r.inception,
                                    'srs': r.srs,
                                    'uat': r.uat,
                                    'golive': r.golive,
                                    'delivery': r.delivery,
                                    'o_and_m': r.o_and_m,
                                    'milestone7': r.milestone7,
                                    'milestone8': r.milestone8,
                                    'milestone9': r.milestone9,
                                    'milestone10': r.milestone10,
                                    'milestone11': r.milestone11,
                                    'milestone12': r.milestone12,
                                    'total_inflow': r.total_inflow,
                                    'resource_internal': r.resource_internal,
                                    'resource_external': r.resource_external,
                                    'it_infra': r.it_infra,
                                    'ancillary': r.ancillary,
                                    'coh': r.coh,
                                    'others': r.others,
                                    'total_outflow': r.total_outflow,
                                    'closing_balance': r.closing_balance,
                                    'cap_closure_bool': r.cap_closure_bool,
                                }] for r in self.op_year_ids] if self.op_year_ids else False,
                    'cap_year_ids': [[0, 0, {
                                    'revision_cap_id': r.revision_cap_id.id,
                                    'time_line': r.time_line,
                                    'opening_balance': r.opening_balance,
                                    'inception': r.inception,
                                    'srs': r.srs,
                                    'uat': r.uat,
                                    'golive': r.golive,
                                    'delivery': r.delivery,
                                    'o_and_m': r.o_and_m,
                                    'milestone7': r.milestone7,
                                    'milestone8': r.milestone8,
                                    'milestone9': r.milestone9,
                                    'milestone10': r.milestone10,
                                    'total_inflow': r.total_inflow,
                                    'resource_internal': r.resource_internal,
                                    'resource_external': r.resource_external,
                                    'it_infra': r.it_infra,
                                    'ancillary': r.ancillary,
                                    'coh': r.coh,
                                    'others': r.others,
                                    'total_outflow': r.total_outflow,
                                    'closing_balance': r.closing_balance,
                                    'cap_closure_bool': r.cap_closure_bool,
                                }] for r in self.cap_year_ids] if self.cap_year_ids else False,
                    # 'action': action,
                    # 'details':details,
                })
                self.revision_status = var.revision_status
                view_id = self.env.ref('kw_eq.kw_eq_revision_form').id
                action = {
                    'name':"Revision",
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'kw_eq_revision',
                    'res_id': var.id,
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'target': 'self',
                    'context':{'create': False,'revision':True,'edit':True},
                    # 'flags': {'mode':'editable'},
                }
                return action

        else:
            for rev in eq_rev:
                if rev.state == 'draft':
                    raise ValidationError("You have a draft EQ Revision.Kindly check the same on the Revised EQ Menu!")
                else:
                    raise ValidationError(f"Your application is pending with {rev.revised_level_2_id.name if rev.state=='applied' else rev.revised_level_3_id.name if rev.state=='submit' else rev.revised_level_4_id.name if rev.state == 'forward' else rev.revised_level_5_id.name}!")
    @api.depends('level_1_id', 'level_2_id', 'level_3_id', 'level_4_id', 'level_5_id', 'level_6_id', 'kw_oppertuinity_id','approval_type')
    def _compute_get_des(self):
        for rec in self:
            approval = self.env['kw_eq_approval_configuration'].sudo().search([('approval_type','=',rec.approval_type),('effective_date','<=',date.today())],order='effective_date desc',limit=1)
            level_1 ='Sales Head' if approval.level_1 =='cso' else 'Reviewer' if  approval.level_1 == 'reviewer' else 'CEO' if   approval.level_1 == 'ceo' else 'CSG Head' if approval.level_1 =='csg_head' else 'Pre Sales Head'  if   approval.level_1 == 'presales'  else 'PM' 

            level_2 ='Sales Head' if approval.level_2 =='cso' else 'Reviewer' if  approval.level_2 == 'reviewer' else 'CEO' if   approval.level_2 == 'ceo' else 'CSG Head' if approval.level_2 =='csg_head' else 'Pre Sales Head'  if   approval.level_2 == 'presales'  else 'PM'  
 
            level_3 = 'Sales Head' if  approval.level_3 =='cso' else 'Reviewer' if   approval.level_3 == 'reviewer' else 'CEO' if    approval.level_3 == 'ceo' else 'CSG Head' if  approval.level_3 =='csg_head' else 'Pre Sales Head'  if    approval.level_3 == 'presales'  else 'PM'  

            level_4 = 'Sales Head' if  approval.level_4 =='cso' else 'Reviewer' if   approval.level_4 == 'reviewer' else 'CEO' if    approval.level_4 == 'ceo' else 'CSG Head' if  approval.level_4 =='csg_head' else 'Pre Sales Head'  if    approval.level_4 == 'presales'  else 'PM' 

            level_5 = 'Sales Head' if  approval.level_5 =='cso' else 'Reviewer' if   approval.level_5 == 'reviewer' else 'CEO' if    approval.level_5 == 'ceo' else 'CSG Head' if  approval.level_5 =='csg_head' else 'Pre Sales Head'  if    approval.level_5 == 'presales'  else 'PM' 

            level_6 = 'Sales Head' if  approval.level_6 =='cso' else 'Reviewer' if   approval.level_6 == 'reviewer' else 'CEO' if    approval.level_6 == 'ceo' else 'CSG Head' if approval.level_6=='csg_head' else 'Pre Sales Head'  if    approval.level_6 == 'presales'  else 'PM' 
    
            if rec.kw_oppertuinity_id:
                if rec.level_1_id :
                    rec.level_1_role = f"{rec.level_1_id.name} ({level_1})"
                if rec.level_2_id:
                    rec.level_2_role = f"{rec.level_2_id.name} ({level_2})"
                if rec.level_3_id:
                    rec.level_3_role = f"{rec.level_3_id.name} ({level_3})"
                if rec.level_4_id:
                    rec.level_4_role = f"{rec.level_4_id.name} ({level_4})"
                if rec.level_5_id:
                    rec.level_5_role = f"{rec.level_5_id.name} ({level_5})"
                if rec.level_6_id:
                    rec.level_6_role = f"{rec.level_6_id.name} ({level_6})"





    # @api.constrains('kw_oppertuinity_id')
    # def validate_oppertunity(self):
    #     if  not self.kw_oppertuinity_id.pm_id.id or not self.kw_oppertuinity_id.reviewer_id.id or not self.kw_oppertuinity_id.ceo_id.id or not self.kw_oppertuinity_id.csg_head_id.id or not self.kw_oppertuinity_id.presales_id.id or not self.kw_oppertuinity_id.cso_id.id:
    #         raise ValidationError('Kindly set the authority.')


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
        roles = ['pm', 'reviewer', 'ceo', 'csg_head', 'presales', 'cso']
        role_ids = {
            'pm': 'pm_id',
            'reviewer': 'reviewer_id',
            'ceo': 'ceo_id',
            'csg_head': 'csg_head_id',
            'presales': 'presales_id',
            'cso': 'cso_id'
        }

        for rec in self:
            if current_emp_id in (
                rec.level_1_id.id, rec.level_2_id.id, rec.level_3_id.id, 
                rec.level_4_id.id, rec.level_5_id.id, rec.level_6_id.id
            ):
                access_records = self.env['kw_eq_page_access'].sudo().search([])
                for record in access_records:
                    names = record.authority_ids.mapped('code')
                    page_bool = page_mapping.get(record.page_name)
                    if page_bool:
                        for role in roles:
                            role_id = role_ids[role]
                            if role in names and getattr(rec.kw_oppertuinity_id, role_id).id == current_emp_id:
                                setattr(rec, page_bool, True)
            if self.env.user.has_group('kw_eq.group_eq_finance'):
                rec.page_software_bool = True
                rec.page_consultancy_bool  = True
                rec.page_resource_bool  = True
                rec.page_ancillary_bool  = True
                rec.page_it_infra_bool  = True
                rec.page_estimate_bool  = True
                rec.page_pbg_bool  = True
                rec.page_log_bool  = True
                rec.page_ancillary_opx_bool  = True
    # @api.constrains('maintenance_percentage','page_estimate_bool')
    # def _check_maintenance_percentage(self):
    #     if self.page_estimate_bool == True:
    #         if not self.maintenance_percentage or self.maintenance_percentage <= 0  or self.maintenance_percentage > 100:
    #             raise ValidationError("Please provide a valid maintenance percentage.")
        
    @api.constrains('level_1_id')
    def _check_valid_user(self):
        if not self.env.user.has_group('kw_eq.group_eq_backlog'):
            if self.level_1_id.id != self.env.user.employee_ids.id:
                raise ValidationError("You are unable to apply for this opportunity.")


    @api.onchange('kw_oppertuinity_id','approval_type')
    def get_client(self):
        self.code = self.kw_oppertuinity_id.code
        self.level_1_id = False
        self.level_2_id = False
        self.level_3_id = False
        self.level_4_id = False
        self.level_5_id = False
        self.level_6_id = False
        if self.kw_oppertuinity_id and self.approval_type:
            self.client_id = self.kw_oppertuinity_id.partner_id.id
            approval_record = self.env['kw_eq_approval_configuration'].sudo().search([('approval_type','=',self.approval_type),('effective_date','<=',date.today())],order='effective_date desc',limit=1)
            level_to_id = {
                "project_manager": self.kw_oppertuinity_id.pm_id.id,
                "reviewer": self.kw_oppertuinity_id.reviewer_id.id,
                "ceo": self.kw_oppertuinity_id.ceo_id.id,
                "csg_head": self.kw_oppertuinity_id.csg_head_id.id,
                "presales": self.kw_oppertuinity_id.presales_id.id,
                "cso": self.kw_oppertuinity_id.cso_id.id,
                "sbu_head": self.kw_oppertuinity_id.pm_id.sbu_master_id.representative_id.id,
            }

            for level_number in range(1, 7):
                approval_level = getattr(approval_record, f'level_{level_number}')
                level_id = level_to_id.get(approval_level)
                if level_id:
                    setattr(self, f'level_{level_number}_id', level_id)


    def _compute_user_access(self):
        current_emp = self.env.user.employee_ids.id
        for rec in self:
            rec.level_1_bool = rec.level_1_id.id == current_emp and rec.state == "version_1"
            rec.level_2_bool = rec.level_2_id.id == current_emp and rec.state == "version_2"
            rec.level_3_bool = rec.level_3_id.id == current_emp and rec.state == "version_3"
            rec.level_4_bool = rec.level_4_id.id == current_emp and rec.state == "version_4"
            rec.level_5_bool = rec.level_5_id.id == current_emp and rec.state == "version_5"
            rec.level_6_bool = rec.level_6_id.id == current_emp and rec.state == "version_6"


    def btn_apply(self):
        for rec in self:
            eq_lst = []
            self._cr.execute(f"select id from kw_eq_estimation where approval_type = '{self.approval_type}' and kw_oppertuinity_id={self.kw_oppertuinity_id.id}")
            records = self._cr.dictfetchall()
            if records:
                eq_lst = [d['id'] for d in records]
            if self.id in eq_lst:
                eq_lst.remove(self.id)
            if len(eq_lst)>0:
                raise ValidationError(
                f"Duplicate entry found for {rec.kw_oppertuinity_id.name}.")
        if self.page_estimate_bool == True:
            if self.eq_approved == 0:
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
        'context':{'current_id': self.id, 'state':'version_2','apply':'apply','type':'eq'}
    }



    def btn_approve(self):
        for rec in self:
            eq_lst = []
            self._cr.execute(f"select id from kw_eq_estimation where approval_type = '{self.approval_type}' and kw_oppertuinity_id={self.kw_oppertuinity_id.id}")
            records = self._cr.dictfetchall()
            if records:
                eq_lst = [d['id'] for d in records]
            if self.id in eq_lst:
                eq_lst.remove(self.id)
            if len(eq_lst)>0:
                raise ValidationError(
                f"Duplicate entry found for {rec.kw_oppertuinity_id.name}.")
        if self.page_estimate_bool == True:
            if self.eq_approved == 0:
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
            'context':{'current_id': self.id,'approve':'approve','type':'eq'}
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
            'context':{'current_id': self.id,'reject':'reject'}
        }
    
    def get_estimate_data(self):
        view_id = self.env.ref('kw_eq.eq_wizard_rollback_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'current_id': self.id,'rollback':'rollback'}
        }
    
    def get_backlog(self):
        if self.eq_approved == 0:
            raise ValidationError("EQ Approved value can not be zero.")
        for rec in self:
            eq_lst = []
            self._cr.execute(f"select id from kw_eq_estimation where type = 'backlog' and approval_type = '{self.approval_type}' and state='grant' and kw_oppertuinity_id={self.kw_oppertuinity_id.id}")
            records = self._cr.dictfetchall()
            if records:
                eq_lst = [d['id'] for d in records]
            if self.id in eq_lst:
                eq_lst.remove(self.id)
            if len(eq_lst)>0:
                raise ValidationError(
                f"Duplicate entry found for {rec.kw_oppertuinity_id.name}.")
        view_id = self.env.ref('kw_eq.eq_wizard_backlog_form').id
        return {
            'name':"Remark",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eq_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'current_id': self.id,'backlog':'backlog'}
        }

 
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}

        if context.get('estimate'):
            user_id = self.env.user.employee_ids.id
            
            domain = [
                '|',
                '&', ('level_1_id', '=', user_id), ('state', '=', 'version_1'),
                '|',
                '&', ('level_2_id', '=', user_id), ('state', '=', 'version_2'),
                '|',
                '&', ('level_3_id', '=', user_id), ('state', '=', 'version_3'),
                '|',
                '&', ('level_4_id', '=', user_id), ('state', '=', 'version_4'),
                '|',
                '&', ('level_5_id', '=', user_id), ('state', '=', 'version_5'),
                '&', ('level_6_id', '=', user_id), ('state', '=', 'version_6'),
            ]
            args += domain

        return super(SoftwareEstimatation, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
   

   
    @api.onchange('first_year_value', 'maintenance_period', 'eq_approved','pbg_implement', 'pbg_support','exchange_rate_to_inr')
    def check_positive_values(self):
        if self.first_year_value < 0:
            raise ValidationError("First Year Value can not be negative.")
        elif self.maintenance_period < 0:
            raise ValidationError("Maintenance Period can not be negative.")
        elif self.eq_approved < 0:
            raise ValidationError("EQ Approved value can not be negative.")
        elif self.pbg_implement < 0:
            raise ValidationError("Total Implementation value can not be negative.")
        elif self.pbg_support < 0:
            raise ValidationError("Total Support value can not be negative.")
        elif self.exchange_rate_to_inr < 0:
            raise ValidationError("Exchange Rate To INR can not be negative.")

    @api.onchange('technology_ids','functional_ids','java_ids','php_ids','dot_net_core_ids','mobile_app_ids','odoo_ids','tableau_ids','sas_ids','etl_ids','out_of_pocket_expenditure_ids','pbg_implementation_ids','maintenance_percentage1','maintenance_period','total_operation_support_ids','pbg_support_ids','consultancy_ids','it_infra_consultancy_ids','social_consultancy_ids','software_resource_ids','social_resource_ids','consulatncy_resource_ids','staffing_resource_ids','third_party_audit_ids','ancillary_ids','reimbursement_ids','strategic_partner_sharing_ids','external_ancillary_ids','it_infra_puchase_ids','computer_hardware_ids','software_licence_ids','proposed_eq','margin_adjustment','actual_margin','eq_approved','gross_profit_margin','bid_value_without_tax','exchange_rate_to_inr','bid_currency','survey_degitalisation_ids','mobile_app_store_ids','domain_email_sms_ids','month','op_month','cap_year_ids','paticulars_ids','quote_ids','op_year_ids')
    def _compute_estimate_data(self):
        self.paticulars_ids = False
        paticulars_ids = []
        paticulars_records = self.env['kw_eq_paticulars_master'].search([])
        for record in paticulars_records:
            paticulars_ids.append([0, 0, {
                'paticulars_name': record.paticulars,
                'code': record.code,
            }])
        self.paticulars_ids = paticulars_ids
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
                res.implementation_value =  (res.implementation_percentage/100) * self.eq_approved
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
                val.support_value =  (val.support_percentage/100) * self.eq_approved
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
            rec.purchase_cost = 0
            rec.production_overhead = 0
            rec.logistic_cost = 0
            rec.company_overhead = 0
            rec.total_profit_overhead = 0
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
                rec.purchase_cost = purchase_cost
                rec.production_overhead = production_overhead
                rec.logistic_cost = logistic_cost
                rec.company_overhead = company_overhead
                rec.total_profit_overhead = total_profit_overhead
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
                rec.purchase_cost = purchase_cost
                rec.production_overhead = production_overhead
                rec.logistic_cost = logistic_cost
                rec.company_overhead = company_overhead
                rec.total_profit_overhead = total_profit_overhead
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
                rec.purchase_cost = purchase_cost
                rec.production_overhead = production_overhead
                rec.company_overhead = company_overhead
                rec.total_profit_overhead = total_profit_overhead
                self.assign_purchase_cost()
            elif rec.code == "CS":
                rec.purchase_cost = consultancy_total
                percentcal2 = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', '=', 'company'),('effective_date','<=',date.today())])
                overhead_percentage = percentcal2.percentage/100
                company_percentage = percentcal2.company_ovhead_percentage/100
                rec.company_overhead = ((rec.purchase_cost + rec.production_overhead + rec.logistic_cost) / overhead_percentage) * company_percentage if overhead_percentage != 0 else 0
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CS'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "CI":
                rec.purchase_cost = consultancy_IT_total
                percentcal2 = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', '=', 'company'),('effective_date','<=',date.today())])
                overhead_percentage = percentcal2.percentage/100
                company_percentage = percentcal2.company_ovhead_percentage/100
                rec.company_overhead = ((rec.purchase_cost + rec.production_overhead + rec.logistic_cost) / overhead_percentage) * company_percentage if overhead_percentage != 0 else 0
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CI'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "CSM":
                rec.purchase_cost = consultancy_social_total
                percentcal2 = self.env['kw_eq_overhead_percentage_master'].search([('overhead_type', '=', 'company'),('effective_date','<=',date.today())])
                overhead_percentage = percentcal2.percentage/100
                company_percentage = percentcal2.company_ovhead_percentage/100
                rec.company_overhead = ((rec.purchase_cost + rec.production_overhead + rec.logistic_cost) / overhead_percentage) * company_percentage if overhead_percentage != 0 else 0
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CSM'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "SS":
                rec.purchase_cost = resource_sw_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SS'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "SM":
                rec.purchase_cost = resource_social_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SM'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "CONS":
                rec.purchase_cost = resource_consultancy_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'CONS'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "SSV":
                rec.purchase_cost = resource_staffing_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SSV'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "TPA":
                rec.purchase_cost = ancillary_tpa_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'TPA'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "SSL":
                rec.purchase_cost = ancillary_ssl_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SSL'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "DS":
                rec.purchase_cost = ancillary_dsign_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'DS'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount(self.calculate_round_amount(rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "DES":
                rec.purchase_cost = ancillary_des_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'DES'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "MAS":
                rec.purchase_cost = ancillary_mas_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'MAS'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "SD":
                rec.purchase_cost = ancillary_sd_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SD'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "REIMB":
                rec.purchase_cost = ancillary_reimb_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'REIMB'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "SPS":
                rec.purchase_cost = ancillary_sps_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SPS'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "EES":
                rec.purchase_cost = ancillary_external_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'EES'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
            elif rec.code == "EC":
                rec.purchase_cost = infra_external_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'EC'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "SCH":
                rec.purchase_cost = infra_hardware_purchace_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SCH'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "SSLC":
                rec.purchase_cost = infra_licence_purchace_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'SSLC'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "MCH":
                rec.purchase_cost = infra_hardware_maintenance_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'MCH'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
            elif rec.code == "MSLC":
                rec.purchase_cost = infra_licence_maintenance_total
                percentcal3 = self.env['kw_eq_acc_head_sub_head'].search([('code', '=', 'MSLC'),('effective_date','<=',date.today())])
                profit_percentage = percentcal3.total_profit_percentage/100
                rec.total_profit_overhead =self.calculate_round_amount((rec.purchase_cost + rec.production_overhead + rec.logistic_cost + rec.company_overhead) * profit_percentage)
                self.assign_purchase_cost()
        self.proposed_eq = sum(self.estimate_ids.mapped('total_profit_overhead'))
        self.margin_adjustment = self.eq_approved - self.proposed_eq
        sum_of_purchace_cost = sum(self.estimate_ids.mapped('purchase_cost'))
        sum_of_prod_overhead = sum(self.estimate_ids.mapped('production_overhead'))
        sum_of_logistic_cost = sum(self.estimate_ids.mapped('logistic_cost'))
        sum_of_company_overhead = sum(self.estimate_ids.mapped('company_overhead'))
        self.actual_margin = (self.proposed_eq - sum_of_purchace_cost - sum_of_prod_overhead - sum_of_logistic_cost - sum_of_company_overhead) + self.margin_adjustment
        self.gross_profit_margin = (self.actual_margin / self.eq_approved) * 100 if self.eq_approved != 0 else 0
        self.bid_value_without_tax = self.eq_approved / self.exchange_rate_to_inr if self.exchange_rate_to_inr != 0 else 0

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
        total_milestone_sum7 = sum(float(item.milestone7) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
        sum(float(item.milestone7) for item in self.op_year_ids if "OP M" in item.time_line) 
        total_milestone_sum8 = sum(float(item.milestone8) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
        sum(float(item.milestone8) for item in self.op_year_ids if "OP M" in item.time_line)
        total_milestone_sum9 = sum(float(item.milestone9) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
        sum(float(item.milestone9) for item in self.op_year_ids if "OP M" in item.time_line) 
        total_milestone_sum10 = sum(float(item.milestone10) for item in self.cap_year_ids if "CAP M" in item.time_line) + \
        sum(float(item.milestone10) for item in self.op_year_ids if "OP M" in item.time_line)  
        total_milestone_sum11 = sum(float(item.milestone11) for item in self.op_year_ids if "OP M" in item.time_line)  
        total_milestone_sum12 = sum(float(item.milestone12) for item in self.op_year_ids if "OP M" in item.time_line)  
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
                                        float(rec.delivery) + float(rec.o_and_m) + float(rec.milestone7) + float(rec.milestone8) + float(rec.milestone9) + float(rec.milestone10))
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
                                        float(rec.delivery) + float(rec.o_and_m) + float(rec.milestone7) + float(rec.milestone8) + float(rec.milestone9) + float(rec.milestone10))
                    rec.resource_internal = total_resource_internal
                    rec.resource_external = total_resource_external
                    rec.it_infra = total_it_infra
                    rec.ancillary = total_ancillary
                    rec.coh = total_coh
                    rec.others = total_others
                    rec.total_outflow =  (float(rec.resource_internal) + float(rec.resource_external) + float(rec.it_infra) + float(rec.ancillary) + float(rec.coh) + float(rec.others))
                    rec.closing_balance = rec.opening_balance
                    closure_closing_balance = rec.closing_balance


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
                    rec.milestone7 = total_milestone_sum7
                    rec.milestone8 = total_milestone_sum8
                    rec.milestone9 = total_milestone_sum9
                    rec.milestone10 = total_milestone_sum10
                    rec.milestone11 = total_milestone_sum11
                    rec.milestone12 = total_milestone_sum12
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
        purchase_cost_of_adc = sum(rec.purchase_cost for rec in self.estimate_ids if rec.code == "ADC")
        purchase_cost_of_awma_awms = sum(rec.purchase_cost for rec in self.estimate_ids if rec.code in ["AWMA", "AWMS"])
        purchase_cost_of_sscs = sum(rec.purchase_cost for rec in self.estimate_ids if rec.code in ["SS", "SM","CONS","SSV"])
        purchase_cost_of_sch_sslc = sum(rec.purchase_cost for rec in self.estimate_ids if rec.code in ["SCH", "SSLC"])
        purchase_cost_of_ec_mch_mslc = sum(rec.purchase_cost for rec in self.estimate_ids if rec.code in ["EC", "MCH","MSLC"])
        purchase_cost_for_anc = sum(rec.purchase_cost for rec in self.estimate_ids if rec.code in ["TPA", "SSL","DS","DES","MAS","SD","REIMB","SPS"])
        logistic_cost_for_anc = sum(rec.logistic_cost for rec in self.estimate_ids if rec.code in ["ADC", "AWMS"])
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
                record.amount = self.actual_margin
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
        

    @api.model
    def default_get(self, data):
        defaults = super(SoftwareEstimatation, self).default_get(data)
        functional = self.env['kw_eq_designation_master'].search([])
        functional_ids = []
        external_ancillary_ids = []
        for record in functional:
            functional_ids.append((0, 0, {
                'designation_id': record.designation_id.id,
                'sort_no':1 if record.functional_category == '1' else 2 if record.functional_category == '2' else 3
            }))
            external_ancillary_ids.append((0, 0, {
                'designation_id': record.designation_id.id,
                'sort_no':1 if record.functional_category == '1' else 2 if record.functional_category == '2' else 3
            }))
            defaults['functional_ids'] = functional_ids
            defaults['external_ancillary_ids'] = external_ancillary_ids
        consultancy_ids = []
        consultancy_records = self.env['kw_eq_designation_master'].search([]).filtered(lambda x:x.section == "1")
        for record in consultancy_records:
            consultancy_ids.append([0, 0, {
                    'designation_id': record.designation_id.id,
                    'consultancy_type':record.functional_category,
                    'sort_no':1 if record.functional_category == '1' else 2 if record.functional_category == '2' else 3
                        }])
            defaults['consultancy_ids'] = consultancy_ids
        it_infra_consultancy_ids = []
        consultancy_infra_records = self.env['kw_eq_designation_master'].search([]).filtered(lambda x:x.section == "2")
        for record in consultancy_infra_records:
            it_infra_consultancy_ids.append([0, 0, {
                    'designation_id': record.designation_id.id,
                    'consultancy_type':record.functional_category,
                    'sort_no':1 if record.functional_category == '1' else 2 if record.functional_category == '2' else 3
                        }])
            defaults['it_infra_consultancy_ids'] = it_infra_consultancy_ids
        social_consultancy_ids = []
        consultancy_social_records = self.env['kw_eq_designation_master'].search([]).filtered(lambda x:x.section == "3")
        for record in consultancy_social_records:
            social_consultancy_ids.append([0, 0, {
                    'designation_id': record.designation_id.id,
                    'consultancy_type':record.functional_category,
                    'sort_no':1 if record.functional_category == '1' else 2 if record.functional_category == '2' else 3
                        }])
            defaults['social_consultancy_ids'] = social_consultancy_ids
        pbg_implementation_ids = []
        pbg_imp_records = self.env['kw_eq_pbg_master'].search([('effective_from','<=',date.today())])
        for record in pbg_imp_records:
            pbg_implementation_ids.append([0, 0, {
                    'item': record.item,
                    'implementation_percentage': record.implementation_percentage,
                    'code': record.code,
                    'value_edit_bool':record.value_edit_bool,
                    'percentage_edit_bool':record.percentage_edit_bool
                        }])
            defaults['pbg_implementation_ids'] = pbg_implementation_ids
        pbg_support_ids = []
        pbg_support_records = self.env['kw_eq_pbg_master'].search([('effective_from','<=',date.today())])
        for record in pbg_support_records:
            pbg_support_ids.append([0, 0, {
                    'item': record.item,
                    'support_percentage': record.support_percentage,
                    'code': record.code,
                    'value_edit_bool':record.value_edit_bool,
                    'percentage_edit_bool':record.percentage_edit_bool
                        }])
            defaults['pbg_support_ids'] = pbg_support_ids
        technology_ids = []
        sw_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "1")
        for record in sw_records:
            technology_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['technology_ids'] = technology_ids
        java_ids = []
        java_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "2")
        for record in java_records:
            java_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['java_ids'] = java_ids
        php_ids = []
        php_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "3")
        for record in php_records:
            php_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['php_ids'] = php_ids
        dot_net_core_ids = []
        core_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "4")
        for record in core_records:
            dot_net_core_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['dot_net_core_ids'] = dot_net_core_ids
        mobile_app_ids = []
        app_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "5")
        for record in app_records:
            mobile_app_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['mobile_app_ids'] = mobile_app_ids
        odoo_ids = []
        odoo_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "6")
        for record in odoo_records:
            odoo_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['odoo_ids'] = odoo_ids
        tableau_ids = []
        tableau_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "7")
        for record in tableau_records:
            tableau_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['tableau_ids'] = tableau_ids
        sas_ids = []
        sas_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "8")
        for record in sas_records:
            sas_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['sas_ids'] = sas_ids
        etl_ids = []
        etl_records = self.env['kw_eq_software_master'].search([('effective_date','<=',date.today())]).filtered(lambda x:x.section == "9")
        for record in etl_records:
            etl_ids.append([0, 0, {
                    'skill_id': record.skill_id.id,
                    'designation_id': record.designation_id.id,
                    'experience': record.experience,
                    'ctc':record.ctc
                        }])
            defaults['etl_ids'] = etl_ids
        ancillary_ids = []
        ancillary = self.env['kw_eq_ancillary_item_master'].search([]).filtered(lambda r: r.section not in ['2', '1','3','5','6','7','8','9'])
        for record in ancillary:
            ancillary_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['ancillary_ids'] = ancillary_ids
        out_of_pocket_expenditure_ids = []
        pocket_expenditure = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '3')])
        for record in pocket_expenditure:
            out_of_pocket_expenditure_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit,
                'sort_no':record.sort_no
            }))
            defaults['out_of_pocket_expenditure_ids'] = out_of_pocket_expenditure_ids
        total_operation_support_ids = []
        operation_support_data = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '2')])
        for record in operation_support_data:
            total_operation_support_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit,
                'sort_no':record.sort_no
            }))
            defaults['total_operation_support_ids'] = total_operation_support_ids
        third_party_audit_ids = []
        third_party_audit = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '1')])
        for record in third_party_audit:
            third_party_audit_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['third_party_audit_ids'] = third_party_audit_ids
        reimbursement_ids = []
        reimbursement = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '5')])
        for record in reimbursement:
            reimbursement_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['reimbursement_ids'] = reimbursement_ids
        strategic_partner_sharing_ids = []
        strategic_partner_sharing = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '6')])
        for record in strategic_partner_sharing:
            strategic_partner_sharing_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['strategic_partner_sharing_ids'] = strategic_partner_sharing_ids
        domain_email_sms_ids = []
        domain_email_record = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '7')])
        for record in domain_email_record:
            domain_email_sms_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['domain_email_sms_ids'] = domain_email_sms_ids
        mobile_app_store_ids = []
        mobile_app_record = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '8')])
        for record in mobile_app_record:
            mobile_app_store_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['mobile_app_store_ids'] = mobile_app_store_ids
            defaults['domain_email_sms_ids'] = domain_email_sms_ids
        survey_degitalisation_ids = []
        survey_record = self.env['kw_eq_ancillary_item_master'].search([('section', '=', '9')])
        for record in survey_record:
            survey_degitalisation_ids.append((0, 0, {
                'ancillary_id': record.ancillary_id.id,
                'item':record.item,
                'unit':record.unit
            }))
            defaults['survey_degitalisation_ids'] = survey_degitalisation_ids
        estimate_ids = []
        estimate = self.env['kw_eq_acc_head_sub_head'].search([])
        for record in estimate:
            estimate_ids.append((0, 0, {
                'account_head_id': record.account_head_id.id,
                'account_subhead_id':record.account_subhead_id.id,
                'code':record.code,
                'sort_no':record.sort_no
            }))
            defaults['estimate_ids'] = estimate_ids

        it_infra_puchase_ids = []
        infras = self.env['kw_eq_it_infra_master'].search([])
        puchase = infras.filtered(lambda x:x.type == 'purchase')
        both = infras.filtered(lambda x:x.type == 'both')
        for record in puchase:
            it_infra_puchase_ids.append((0, 0, {
                'infra_id': record.id,
            }))
        defaults['it_infra_puchase_ids'] = it_infra_puchase_ids
        return defaults


class SoftwareDevelopmentConfig(models.Model):
    _name = 'kw_eq_software_development_config'
    _description = 'Software Development Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    java_estimate_id = fields.Many2one('kw_eq_estimation')
    php_estimate_id = fields.Many2one('kw_eq_estimation')
    core_estimate_id = fields.Many2one('kw_eq_estimation')
    mobile_estimate_id = fields.Many2one('kw_eq_estimation')
    odoo_estimate_id = fields.Many2one('kw_eq_estimation')
    tableu_estimate_id = fields.Many2one('kw_eq_estimation')
    sas_estimate_id = fields.Many2one('kw_eq_estimation')
    etl_estimate_id = fields.Many2one('kw_eq_estimation')
    skill_id = fields.Many2one('kw_skill_master',string="Technology")
    designation_id = fields.Many2one('hr.job',string="Designation")
    experience = fields.Selection(string="Experience",selection=[('1', '<= 2yrs'), ('2', '> 2 to ≤4 Yrs'),('3', '> 4 to ≤6 Yrs'),('4', '> 6 to ≤8 Yrs'),('5', '> 8 to ≤10 Yrs'),('6', '> 10 Yrs')])
    implementation_man_month = fields.Float(string="Implementation Man Month")
    support_man_month =fields.Float(string="Support Man Month")
    implementation_total_cost = fields.Float(string="Implementation Total Cost")
    support_total_cost = fields.Float(string="Support Total Cost")
    ctc = fields.Float('CTC/Month')
    technology_replica_id = fields.Many2one('kw_eq_replica')
    java_replica_id = fields.Many2one('kw_eq_replica')
    php_replica_id = fields.Many2one('kw_eq_replica')
    dot_net_core_replica_id = fields.Many2one('kw_eq_replica')
    mobile_replica_id = fields.Many2one('kw_eq_replica')
    odoo_replica_id = fields.Many2one('kw_eq_replica')
    tableau_replica_id = fields.Many2one('kw_eq_replica')
    sas_replica_id = fields.Many2one('kw_eq_replica')
    etl_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')
    java_estimate_revision_id = fields.Many2one('kw_eq_revision')
    php_estimate_revision_id = fields.Many2one('kw_eq_revision')
    core_estimate_revision_id = fields.Many2one('kw_eq_revision')
    mobile_estimate_revision_id = fields.Many2one('kw_eq_revision')
    odoo_estimate_revision_id = fields.Many2one('kw_eq_revision')
    tableu_estimate_revision_id = fields.Many2one('kw_eq_revision')
    sas_estimate_revision_id = fields.Many2one('kw_eq_revision')
    etl_estimate_revision_id = fields.Many2one('kw_eq_revision')



    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)

    @api.onchange('ctc','implementation_man_month','support_man_month')
    def count_ctc(self):
        if self.implementation_man_month < 0:
            raise ValidationError("Implementation Man Month can not be negative.")
        else:
            self.implementation_total_cost = self.calculate_round_amount(self.ctc * self.implementation_man_month)
        if self.support_man_month < 0:
            raise ValidationError("Support Man Month can not be negative.")
        else:
            self.support_total_cost = self.calculate_round_amount(self.ctc * self.support_man_month)



        
   
class SoftwareConfig(models.Model):
    _name = 'kw_eq_software_functional_config'
    _description = 'Software Functional Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    ctc = fields.Float('CTC/Month')
    designation_id = fields.Many2one('hr.job',string="Designation")
    implementation_man_month = fields.Float(string="Implementation Man Month")
    implementation_total_ctc = fields.Float(string="Implementation Total Cost")
    support_man_month =fields.Float(string="Support Man Month")
    support_total_ctc =fields.Float(string="Support Total Cost")
    sort_no = fields.Integer()
    other_item = fields.Char(string='Add New Skill')
    functional_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')

    
    @api.onchange('ctc','implementation_man_month','support_man_month')
    def count_ctc(self):
        if self.implementation_man_month < 0:
            raise ValidationError("Implementation Man Month can not be negative.")
        else:
            self.implementation_total_ctc = self.estimation_id.calculate_round_amount(self.ctc * self.implementation_man_month)
        if self.support_man_month < 0:
            raise ValidationError("Support Man Month can not be negative.")
        else:
            self.support_total_ctc = self.estimation_id.calculate_round_amount(self.ctc * self.support_man_month)


        
class SoftwareConsultancy(models.Model):
    _name = 'kw_eq_software_consultancy_config'
    _description = 'Software Consultancy Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    it_infra_consultancy_id = fields.Many2one('kw_eq_estimation')
    social_consultancy_id = fields.Many2one('kw_eq_estimation')
    designation_id = fields.Many2one('hr.job',string="Designation")
    consultancy_type = fields.Selection(string="Consultancy Type",selection=[('1', 'Software Consultancy'), ('2', 'IT Infra Consultancy'),('3', 'Social Media Consultancy')])
    experience_proposed = fields.Char(string='Experience Proposed')
    man_month_rate = fields.Float(string="Man Month Rate")
    man_month_effort =fields.Float(string="Man Month Effort")
    total_cost = fields.Float(string='Total Cost')
    other_item = fields.Char(string='Add New Skill')
    consultancy_replica_id = fields.Many2one('kw_eq_replica')
    it_infra_replica_id = fields.Many2one('kw_eq_replica')
    social_consultancy_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')
    it_infra_revision_id = fields.Many2one('kw_eq_revision')
    social_revision_id = fields.Many2one('kw_eq_revision')


    
    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)
    @api.onchange('man_month_rate','man_month_effort')
    def count_ctc(self):
        if self.man_month_rate < 0:
                raise ValidationError("Man Month Rate can not be negative.")
        elif self.man_month_effort < 0:
            raise ValidationError("Man Month Effort can not be negative.")
        self.total_cost = self.calculate_round_amount(self.man_month_rate * self.man_month_effort)
    
    
            
        
class AncillaryConfig(models.Model):
    _name = 'kw_eq_ancillary_config'
    _description = 'Ancillary Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    total_operation_id = fields.Many2one('kw_eq_estimation')
    expanditure_id = fields.Many2one('kw_eq_estimation')
    third_party_id = fields.Many2one('kw_eq_estimation')
    reimbursement_id = fields.Many2one('kw_eq_estimation')
    ancillary_id = fields.Many2one('kw_eq_ancillary_master')
    domain_sms_id = fields.Many2one('kw_eq_estimation')
    strategic_partner_id = fields.Many2one('kw_eq_estimation')
    mobile_app_id = fields.Many2one('kw_eq_estimation')
    survey_degitalisation_id = fields.Many2one('kw_eq_estimation')
    third_party_replica_id = fields.Many2one('kw_eq_replica')
    reimbursement_replica_id = fields.Many2one('kw_eq_replica')
    strategic_partner_replica_id = fields.Many2one('kw_eq_replica')
    domain_sms_replica_id = fields.Many2one('kw_eq_replica')
    mobile_app_replica_id = fields.Many2one('kw_eq_replica')
    survey_replica_id = fields.Many2one('kw_eq_replica')
    ancillary_replica_id = fields.Many2one('kw_eq_replica')
    expanditure_replica_id = fields.Many2one('kw_eq_replica')
    total_operation_replica_id = fields.Many2one('kw_eq_replica')
    item = fields.Char()
    unit = fields.Char()
    rate = fields.Float()
    qty = fields.Float()
    cost = fields.Float()
    other_item = fields.Char()
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')
    total_operation_revision_id = fields.Many2one('kw_eq_revision')
    expanditure_revision_id = fields.Many2one('kw_eq_revision')
    third_party_revision_id = fields.Many2one('kw_eq_revision')
    reimbursement_revision_id = fields.Many2one('kw_eq_revision')
    domain_sms_revision_id = fields.Many2one('kw_eq_revision')
    strategic_partner_revision_id = fields.Many2one('kw_eq_revision')
    mobile_app_revision_id = fields.Many2one('kw_eq_revision')
    survey_degitalisation_revision_id = fields.Many2one('kw_eq_revision')
    code = fields.Char()
    sort_no = fields.Integer()
    sort_no_sequence = fields.Integer(compute="get_sort_no_sequence")

    @api.depends('ancillary_id')
    def get_sort_no_sequence(self):
        for rec in self:
            rec.sort_no_sequence = rec.sort_no




    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)
    @api.onchange('rate','qty')
    def count_ctc(self):
        if self.rate < 0:
            raise ValidationError("Rate can not be negative.")
        elif self.qty < 0:
            raise ValidationError("quantity can not be negative.")
        self.cost = self.calculate_round_amount(self.rate * self.qty)


class ExternalAncillaryConfig(models.Model):
    _name = 'kw_eq_external_ancillary_config'
    _description = 'External Ancillary Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    designation_id = fields.Many2one('hr.job',string="Designation")
    man_month_rate = fields.Float()
    qty = fields.Float()
    cost = fields.Float()
    sort_no = fields.Integer()
    other_item = fields.Char()
    estimation_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')


    @api.onchange('man_month_rate','qty')
    def count_ctc(self):
        if self.man_month_rate < 0:
            raise ValidationError("Man Month Rate can not be negative.")
        elif self.qty < 0:
            raise ValidationError("quantity can not be negative.")
        self.cost = self.estimation_id.calculate_round_amount(self.man_month_rate * self.qty)


    
class ITInfraPurchaseConfig(models.Model):
    _name = 'kw_eq_it_infra_purchase_config'
    _description = 'IT Infra Purchase Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    infra_id = fields.Many2one('kw_eq_it_infra_master',string="Item")
    description = fields.Char()
    purchase_unit = fields.Char()
    purchase_rate = fields.Float()
    purchase_qty = fields.Float()
    purchase_cost = fields.Float()
    other_item = fields.Char()
    estimation_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')



    @api.onchange('purchase_rate','purchase_qty')
    def count_ctc(self):
        if self.purchase_rate < 0:
            raise ValidationError("Purchase Rate can not be negative.")
        elif self.purchase_qty < 0:
            raise ValidationError("Purchase quantity can not be negative.")
        self.purchase_cost = self.estimation_id.calculate_round_amount(self.purchase_rate * self.purchase_qty)

   
            
class ITInfraMaintenanceConfig(models.Model):
    _name = 'kw_eq_it_infra_purchase_maintenance_config'
    _description = 'IT Infra Purchase & Maintenance Configuration'
    
    estimation_id = fields.Many2one('kw_eq_estimation')
    infra_id = fields.Many2one('kw_eq_it_infra_master',string="Item")
    description = fields.Char()
    purchase_unit = fields.Char()
    purchase_rate = fields.Float()
    purchase_qty = fields.Float()
    purchase_cost = fields.Float()
    
    maintenance_unit = fields.Char()
    maintenance_rate = fields.Float()
    maintenance_qty = fields.Float()
    maintenance_cost = fields.Float()
    
    


class SocialResource(models.Model):
    _name = 'kw_eq_social_resource_config'
    _description = 'Social Resource Configuration'
    
    skill = fields.Char()
    estimation_id = fields.Many2one('kw_eq_estimation')
    qualification = fields.Char('Qualification & Experience')
    resources = fields.Float()
    man_month = fields.Float( string='Man-Month')
    ctc = fields.Float(string="CTC/Month")
    ope_month = fields.Float(string="OPE/Month")
    total_cost = fields.Float()
    first_year = fields.Integer('1st Year')
    average =  fields.Float('Average',compute="change_years_amt")
    resource_deploy_duration = fields.Selection(string="Resource Deployment Duration",selection=[('1', '1 Yrs'), ('2', '2 Yrs'),('3', '3 Yrs'),('4', '4 Yrs'),('5', '5 Yrs'),('6', '6 Yrs'),('7', '7 Yrs')])
    social_resource_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    sec_year = fields.Integer('2nd Year')
    third_year = fields.Integer('3rd Year')
    forth_year = fields.Integer('4th Year')
    fifth_year = fields.Integer('5th Year')
    sixth_year = fields.Integer('6th Year')
    seventh_year = fields.Integer('7th Year')
    average_percentage  = fields.Integer('Average Percentage')
    revision_id = fields.Many2one('kw_eq_revision')


    



    
    @api.depends('resource_deploy_duration','average_percentage','first_year')
    def change_years_amt(self):
        for rec in self:
            if rec.resource_deploy_duration:
                # AvgRateCalculation = rec.env['kw_eq_avg_rate_calculation'].search([('effective_from','<=',date.today())],limit=1)
                percentage = rec.average_percentage/100
                rec.sec_year = ((percentage * rec.first_year)) if rec.resource_deploy_duration in ('2','3','4','5','6','7') else  0
                rec.third_year =((percentage * rec.sec_year)) if rec.resource_deploy_duration in ('3','4','5','6','7') else  0
                rec.forth_year = ((percentage * rec.third_year)) if rec.resource_deploy_duration in ('4','5','6','7') else  0
                rec.fifth_year = ((percentage * rec.forth_year)) if rec.resource_deploy_duration in ('5','6','7') else  0
                rec.sixth_year = ((percentage * rec.fifth_year)) if rec.resource_deploy_duration in ('6','7') else  0
                rec.seventh_year = ((percentage  * rec.sixth_year)) if rec.resource_deploy_duration in ('7') else  0 

                

                rec.average = ((rec.sec_year+rec.third_year+rec.forth_year+rec.fifth_year+rec.sixth_year+rec.seventh_year+rec.first_year)/int(rec.resource_deploy_duration))
                rec.ctc = (rec.average)
                rec.total_cost = rec.estimation_id.calculate_round_amount((rec.ctc + rec.ope_month ) *rec.resources * rec.man_month)


    @api.multi
    def get_all_years_amount1(self):
            view_id_form = self.env.ref('kw_eq.resource_all_year_amount_form').id
            return {
            'name':"Resource",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'kw_eq_social_resource_config',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            
        }
        
                

    

    @api.onchange('ope_month','ctc','resources','man_month','first_year')
    def calculate_total(self):
        if self.man_month < 0:
            raise ValidationError("Man Month can not be negative.")
        elif self.ctc < 0:
            raise ValidationError("CTC can not be negative.")
        elif self.ope_month < 0:
            raise ValidationError("OPE Month can not be negative.")
        elif self.first_year < 0:
            raise ValidationError("First Year can not be negative.")
        elif self.resources < 0:
            raise ValidationError("Resources can not be negative.")
        self.total_cost =self.estimation_id.calculate_round_amount((self.ctc + self.ope_month ) *self.resources * self.man_month)



class ConsultancyResource(models.Model):
    _name = 'kw_eq_consulatncy_resource_config'
    _description = 'Consultancy Resource Configuration'
    
    skill = fields.Char()
    estimation_id = fields.Many2one('kw_eq_estimation')
    qualification = fields.Char('Qualification & Experience')
    resources = fields.Float()
    man_month = fields.Float(string="Man-Month")
    ctc = fields.Float(string="CTC/Month")
    ope_month = fields.Float(string="OPE/Month")
    total_cost = fields.Float()
    first_year = fields.Integer('1st Year')
    average =  fields.Float('Average',compute="change_years_amt")
    resource_deploy_duration = fields.Selection(string="Resource Deployment Duration",selection=[('1', '1 Yrs'), ('2', '2 Yrs'),('3', '3 Yrs'),('4', '4 Yrs'),('5', '5 Yrs'),('6', '6 Yrs'),('7', '7 Yrs')])
    consulatncy_resource_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    sec_year = fields.Integer('2nd Year')
    third_year = fields.Integer('3rd Year')
    forth_year = fields.Integer('4th Year')
    fifth_year = fields.Integer('5th Year')
    sixth_year = fields.Integer('6th Year')
    seventh_year = fields.Integer('7th Year')
    average_percentage  = fields.Integer('Average Percentage')
    revision_id = fields.Many2one('kw_eq_revision')


    
    @api.depends('resource_deploy_duration','average_percentage','first_year')
    def change_years_amt(self):
        for rec in self:
            if rec.resource_deploy_duration:
                # AvgRateCalculation = rec.env['kw_eq_avg_rate_calculation'].search([('effective_from','<=',date.today())],limit=1)
                percentage = rec.average_percentage/100
                rec.sec_year = ((percentage * rec.first_year)) if rec.resource_deploy_duration in ('2','3','4','5','6','7') else  0
                rec.third_year = ((percentage * rec.sec_year)) if rec.resource_deploy_duration in ('3','4','5','6','7') else  0
                rec.forth_year = ((percentage * rec.third_year)) if rec.resource_deploy_duration in ('4','5','6','7') else  0
                rec.fifth_year = ((percentage * rec.forth_year)) if rec.resource_deploy_duration in ('5','6','7') else  0
                rec.sixth_year = ((percentage * rec.fifth_year)) if rec.resource_deploy_duration in ('6','7') else  0
                rec.seventh_year = ((percentage  * rec.sixth_year)) if rec.resource_deploy_duration in ('7') else  0 
                
                rec.average = ((rec.sec_year+rec.third_year+rec.forth_year+rec.fifth_year+rec.sixth_year+rec.seventh_year+rec.first_year)/int(rec.resource_deploy_duration))
                rec.ctc = (rec.average)
                rec.total_cost = rec.estimation_id.calculate_round_amount((rec.ctc + rec.ope_month ) *rec.resources * rec.man_month)

    @api.multi
    def get_all_years_amount3(self):
            view_id_form = self.env.ref('kw_eq.consultancy_resource_all_year_amount_form').id
            return {
            'name':"Resource",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'kw_eq_consulatncy_resource_config',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            
        }



    @api.onchange('ope_month','ctc','resources','man_month','first_year')
    def calculate_total(self):
        if self.man_month < 0:
            raise ValidationError("Man Month can not be negative.")
        elif self.ctc < 0:
            raise ValidationError("CTC can not be negative.")
        elif self.ope_month < 0:
            raise ValidationError("OPE Month can not be negative.")
        elif self.first_year < 0:
            raise ValidationError("First Year can not be negative.")
        elif self.resources < 0:
            raise ValidationError("Resources can not be negative.")
        self.total_cost = self.estimation_id.calculate_round_amount((self.ctc + self.ope_month ) *self.resources * self.man_month)



class StaffingResource(models.Model):
    _name = 'kw_eq_staffing_resource_config'
    _description = 'Staffing Resource Configuration'
    
    
    skill = fields.Char()
    estimation_id = fields.Many2one('kw_eq_estimation')
    qualification = fields.Char('Qualification & Experience')
    resources = fields.Float()
    man_month = fields.Float(string="Man-Month")
    ctc = fields.Float(string="CTC/Month")
    ope_month = fields.Float(string="OPE/Month")
    total_cost = fields.Float()
    first_year = fields.Integer('1st Year')
    average =  fields.Float('Average',compute="change_years_amt")
    resource_deploy_duration = fields.Selection(string="Resource Deployment Duration",selection=[('1', '1 Yrs'), ('2', '2 Yrs'),('3', '3 Yrs'),('4', '4 Yrs'),('5', '5 Yrs'),('6', '6 Yrs'),('7', '7 Yrs')])
    staffing_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    sec_year = fields.Integer('2nd Year')
    third_year = fields.Integer('3rd Year')
    forth_year = fields.Integer('4th Year')
    fifth_year = fields.Integer('5th Year')
    sixth_year = fields.Integer('6th Year')
    seventh_year = fields.Integer('7th Year')
    average_percentage  = fields.Integer('Average Percentage')
    revision_id = fields.Many2one('kw_eq_revision')

    
    @api.depends('resource_deploy_duration','average_percentage','first_year')
    def change_years_amt(self):
        for rec in self:
            if rec.resource_deploy_duration:
                # AvgRateCalculation = rec.env['kw_eq_avg_rate_calculation'].search([('effective_from','<=',date.today())],limit=1)
                percentage = rec.average_percentage/100
                rec.sec_year = ((percentage * rec.first_year)) if rec.resource_deploy_duration in ('2','3','4','5','6','7') else  0
                rec.third_year = ((percentage * rec.sec_year)) if rec.resource_deploy_duration in ('3','4','5','6','7') else  0
                rec.forth_year = ((percentage * rec.third_year)) if rec.resource_deploy_duration in ('4','5','6','7') else  0
                rec.fifth_year = ((percentage * rec.forth_year)) if rec.resource_deploy_duration in ('5','6','7') else  0
                rec.sixth_year = ((percentage * rec.fifth_year)) if rec.resource_deploy_duration in ('6','7') else  0
                rec.seventh_year = ((percentage  * rec.sixth_year)) if rec.resource_deploy_duration in ('7') else  0 
                
                rec.average = ((rec.sec_year+rec.third_year+rec.forth_year+rec.fifth_year+rec.sixth_year+rec.seventh_year+rec.first_year)/int(rec.resource_deploy_duration))
                rec.ctc = (rec.average)
                rec.total_cost = rec.estimation_id.calculate_round_amount((rec.ctc + rec.ope_month ) *rec.resources * rec.man_month)

    @api.multi
    def get_all_years_amount4(self):
            view_id_form = self.env.ref('kw_eq.staffing_resource_all_year_amount_form').id
            return {
            'name':"Resource",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'kw_eq_staffing_resource_config',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            
        }



   

    @api.onchange('ope_month','ctc','resources','man_month','first_year')
    def calculate_total(self):
        if self.man_month < 0:
            raise ValidationError("Man Month   be negative.")
        elif self.ctc < 0:
            raise ValidationError("CTC can not be negative.")
        elif self.ope_month < 0:
            raise ValidationError("OPE Month can not be negative.")
        elif self.first_year < 0:
            raise ValidationError("First Year can not be negative.")
        elif self.resources < 0:
            raise ValidationError("Resources can not be negative.")
        self.total_cost = self.estimation_id.calculate_round_amount((self.ctc + self.ope_month ) *self.resources * self.man_month)


    
class SoftwareResource(models.Model):
    _name = 'kw_eq_software_resource_config'
    _description = 'SW Resource Configuration'

    
    skill = fields.Char()
    estimation_id = fields.Many2one('kw_eq_estimation')
    qualification = fields.Char('Qualification & Experience')
    resources = fields.Float()
    man_month = fields.Float(string="Man-Month")
    ctc = fields.Float(string='CTC/Month')
    ope_month = fields.Float(string="OPE/Month")
    total_cost = fields.Float()
    first_year = fields.Integer('1st Year')
    average =  fields.Float('Average',compute="change_years_amt")
    resource_deploy_duration = fields.Selection(string="Resource Deployment Duration",selection=[('1', '1 Yrs'), ('2', '2 Yrs'),('3', '3 Yrs'),('4', '4 Yrs'),('5', '5 Yrs'),('6', '6 Yrs'),('7', '7 Yrs')])
    software_resource_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    sec_year = fields.Integer('2nd Year')
    third_year = fields.Integer('3rd Year')
    forth_year = fields.Integer('4th Year')
    fifth_year = fields.Integer('5th Year')
    sixth_year = fields.Integer('6th Year')
    seventh_year = fields.Integer('7th Year')
    average_percentage  = fields.Integer('Average Percentage')
    revision_id = fields.Many2one('kw_eq_revision')

    @api.depends('resource_deploy_duration','average_percentage','first_year')
    def change_years_amt(self):
        for rec in self:
            if rec.resource_deploy_duration:
                # AvgRateCalculation = rec.env['kw_eq_avg_rate_calculation'].search([('effective_from','<=',date.today())],limit=1)
                percentage = rec.average_percentage/100
                rec.sec_year = ((percentage * rec.first_year)) if rec.resource_deploy_duration in ('2','3','4','5','6','7') else  0
                rec.third_year = ((percentage * rec.sec_year)) if rec.resource_deploy_duration in ('3','4','5','6','7') else  0
                rec.forth_year = ((percentage * rec.third_year)) if rec.resource_deploy_duration in ('4','5','6','7') else  0
                rec.fifth_year = ((percentage * rec.forth_year)) if rec.resource_deploy_duration in ('5','6','7') else  0
                rec.sixth_year = ((percentage * rec.fifth_year)) if rec.resource_deploy_duration in ('6','7') else  0
                rec.seventh_year = ((percentage  * rec.sixth_year)) if rec.resource_deploy_duration in ('7') else  0 
                rec.average = ((rec.sec_year+rec.third_year+rec.forth_year+rec.fifth_year+rec.sixth_year+rec.seventh_year+rec.first_year)/int(rec.resource_deploy_duration))
                rec.ctc = (rec.average)
                rec.total_cost = rec.estimation_id.calculate_round_amount((rec.ctc + rec.ope_month ) *rec.resources * rec.man_month)

    @api.multi
    def get_all_years_amount2(self):
            view_id_form = self.env.ref('kw_eq.software_resource_all_year_amount_form').id
            return {
            'name':"Resource",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'kw_eq_software_resource_config',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            }
    
    
    @api.onchange('ope_month','ctc','resources','man_month','first_year')
    def calculate_total(self):
        if self.man_month < 0:
            raise ValidationError("Man Month can not be negative.")
        elif self.ctc < 0:
            raise ValidationError("CTC can not be negative.")
        elif self.ope_month < 0:
            raise ValidationError("OPE Month can not be negative.")
        elif self.first_year < 0:
            raise ValidationError("First Year can not be negative.")
        elif self.resources < 0:
            raise ValidationError("Resources can not be negative.")
        self.total_cost = self.estimation_id.calculate_round_amount((self.ctc + self.ope_month ) *self.resources * self.man_month)

 

   
class kw_eq_estimate_details(models.Model):
    _name = 'kw_eq_estimate_details'
    _description = 'Estimate Details'

    account_head_id = fields.Many2one('account.head',string='Heads of Income')
    account_subhead_id = fields.Many2one('account.sub.head',string='Sub Head')
    estimation_id = fields.Many2one('kw_eq_estimation')
    purchase_cost = fields.Float('Lab / Purchase Cost',digits=dp.get_precision('eq'))
    production_overhead = fields.Float('Prod. Overhead',digits=dp.get_precision('eq'))
    logistic_cost = fields.Float('Logistics/OPEx',digits=dp.get_precision('eq'))
    company_overhead = fields.Float('Company Overhead',digits=dp.get_precision('eq'))
    total_profit_overhead = fields.Float('Total (Profit & OHs)',digits=dp.get_precision('eq'))
    code = fields.Char()
    estimation_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    revision_id = fields.Many2one('kw_eq_revision')
    sort_no = fields.Integer()
    sort_no_sequence = fields.Integer(compute="get_sort_no_sequence")

    revised_purchase_cost = fields.Float('Revised Lab / Purchase Cost',digits=dp.get_precision('eq'))
    revised_production_overhead = fields.Float('Revised Prod. Overhead',digits=dp.get_precision('eq'))
    revised_logistic_cost = fields.Float('Revised Logistics/OPEx',digits=dp.get_precision('eq'))
    revised_company_overhead = fields.Float('Revised Company Overhead',digits=dp.get_precision('eq'))
    revised_total_profit_overhead = fields.Float('Revised Total (Profit & OHs)',digits=dp.get_precision('eq'))

    @api.depends('account_head_id')
    def get_sort_no_sequence(self):
        for rec in self:
            records = self.env['kw_eq_acc_head_sub_head'].sudo().search([('code','=',rec.code)],limit=1)
            rec.sort_no_sequence = records.sort_no




class ComputerHardware(models.Model):
    _name = 'kw_eq_computer_hardware_config'
    _description = 'Computer Hardware'
    
    hardware_id = fields.Many2one('kw_eq_estimation')
    item = fields.Char(string="Item Name")
    description = fields.Char(string="Description / Specification")
    purchase_unit = fields.Char()
    purchase_rate = fields.Float()
    purchase_qty = fields.Float()
    purchase_cost = fields.Float()
    
    maintenance_unit = fields.Char()
    maintenance_rate = fields.Float()
    maintenance_qty = fields.Float()
    maintenance_cost = fields.Float()
    hardware_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    hardware_revision_id = fields.Many2one('kw_eq_revision')
    


    @api.onchange('purchase_rate','purchase_qty','maintenance_rate','maintenance_qty')
    def count_ctc(self):
        if self.purchase_rate < 0 or self.purchase_qty < 0:
            raise ValidationError("Purchase Rate,Quantity can not be negative.")
        else:
            self.purchase_cost = self.hardware_id.calculate_round_amount(self.purchase_rate * self.purchase_qty)
        if self.maintenance_rate < 0 or self.maintenance_qty < 0:
            raise ValidationError("Maintenance Rate,Quantity can not be negative.")
        else:
            self.maintenance_cost = self.hardware_id.calculate_round_amount(self.maintenance_rate * self.maintenance_qty)

    




class SoftwareLicenses(models.Model):
    _name = 'kw_eq_software_licenses_config'
    _description = 'Software Licenses COTS'
    
    license_id = fields.Many2one('kw_eq_estimation')
    item = fields.Char(string="Item Name")
    description = fields.Char(string="Description / Specification")
    purchase_unit = fields.Char()
    purchase_rate = fields.Float()
    purchase_qty = fields.Float()
    purchase_cost = fields.Float()
    
    maintenance_unit = fields.Char()
    maintenance_rate = fields.Float()
    maintenance_qty = fields.Float()
    maintenance_cost = fields.Float() 
    license_replica_id = fields.Many2one('kw_eq_replica')
    remark = fields.Text(string="Remark")
    license_revision_id = fields.Many2one('kw_eq_revision')


    @api.onchange('purchase_rate','purchase_qty','maintenance_rate','maintenance_qty')
    def count_ctc(self):
        if self.purchase_rate < 0 or self.purchase_qty < 0:
            raise ValidationError("Purchase Rate,Quantity can not be negative.")
        else:
            self.purchase_cost = self.license_id.calculate_round_amount(self.purchase_rate * self.purchase_qty)
        if self.maintenance_rate < 0 or self.maintenance_qty < 0:
            raise ValidationError("Maintenance Rate,Quantity can not be negative.")
        else:
            self.maintenance_cost = self.license_id.calculate_round_amount(self.maintenance_rate * self.maintenance_qty)

   


class PBGConfig(models.Model):
    _name = 'kw_eq_pbg_config'
    _description = 'PBG Config'

    pbg_implementation_id = fields.Many2one("kw_eq_estimation")
    pbg_support_id = fields.Many2one("kw_eq_estimation")
    item = fields.Char(string="Item")
    implementation_percentage = fields.Float(string='Implementation Percentage')
    support_percentage = fields.Float(string='Support Percentage')
    implementation_value = fields.Float(string='Implementation Value')
    support_value = fields.Float(string='Support Value')
    code = fields.Char()
    value_edit_bool = fields.Boolean(string="Value Editable")
    percentage_edit_bool = fields.Boolean(string="Percentage Editable")
    pbg_replica_id = fields.Many2one("kw_eq_replica")
    pbg_support_replica_id = fields.Many2one("kw_eq_replica")
    remark = fields.Text(string="Remark")
    pbg_implementation_revision_id = fields.Many2one('kw_eq_revision')
    pbg_support_revision_id = fields.Many2one('kw_eq_revision')



class EqLog(models.Model):
    _name           = 'eq_log'
    _description    = "Eq Log"
    _order = 'create_date desc'


    eq_id = fields.Many2one('kw_eq_estimation')
    eq_log_id = fields.Many2one('eq_wizard')
    date = fields.Date(string="Date", default = fields.date.today())
    action_by_id = fields.Many2one('res.users', string="Action Taken By")
    remark = fields.Text()
    log_replica_id = fields.Many2one('kw_eq_replica')
    state = fields.Selection([('version_1', 'Version 1'), ('version_2', 'Version 2'),('version_3', 'Version 3'),('version_4', 'Version 4'),('version_5', 'Version 5'),('version_6', 'Version 6'),('grant','Grant')],string="Current State")
    eq_revision_id = fields.Many2one('kw_eq_revision')
    revision_state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'),('submit', 'Submitted'),('forward', 'Forwarded'),('recommend', 'Recommended'),('not_recommended', 'Not Recommended'),('grant', ' Granted'),('rejected', ' Rejected')],string="Status",default='draft')


class EqWizard(models.Model):
    _name = 'eq_wizard'
    
    ref_id = fields.Many2one('kw_eq_estimation', default= lambda self:self.env.context.get('current_id'))
    remarks = fields.Text(string="Remark", required=True)
    action_log_ids = fields.One2many('eq_log', 'eq_log_id', string='Action Log Table')
    revision_id = fields.Many2one('kw_eq_revision', default= lambda self:self.env.context.get('revision_id'))
    
    


    def replica_data(self,action=False,details=False,revision=False):
        if not revision or revision == False:
            var = self.env['kw_eq_replica'].sudo().create({
                'client_id' : self.ref_id.client_id.id,
                'code':self.ref_id.kw_oppertuinity_id.code,
                'kw_oppertuinity_id' : self.ref_id.kw_oppertuinity_id.id,
                'approval_type' : self.ref_id.approval_type,
                'level_1_id' : self.ref_id.level_1_id.id,
                'level_2_id' : self.ref_id.level_2_id.id,
                'level_3_id' : self.ref_id.level_3_id.id,
                'level_4_id' : self.ref_id.level_4_id.id,
                'level_5_id' : self.ref_id.level_5_id.id,
                'level_6_id' : self.ref_id.level_6_id.id,
                'page_software_bool' : self.ref_id.page_software_bool,
                'page_consultancy_bool' : self.ref_id.page_consultancy_bool,
                'page_resource_bool' : self.ref_id.page_resource_bool,
                'page_ancillary_bool' : self.ref_id.page_ancillary_bool,
                'page_it_infra_bool' : self.ref_id.page_it_infra_bool,
                'page_estimate_bool' : self.ref_id.page_estimate_bool,
                'page_pbg_bool' : self.ref_id.page_pbg_bool,
                'page_log_bool' : self.ref_id.page_log_bool,
                'page_ancillary_opx_bool' : self.ref_id.page_ancillary_opx_bool,
                'technology_ids': [[0, 0, {
                                'technology_replica_id': r.technology_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.technology_ids] if self.ref_id.technology_ids else False,
                'java_ids': [[0, 0, {
                                'java_replica_id': r.java_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.java_ids] if self.ref_id.java_ids else False,
                'php_ids': [[0, 0, {
                                'php_replica_id': r.php_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.php_ids] if self.ref_id.php_ids else False,
                'dot_net_core_ids': [[0, 0, {
                                'dot_net_core_replica_id': r.dot_net_core_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.dot_net_core_ids] if self.ref_id.dot_net_core_ids else False,
                'mobile_app_ids': [[0, 0, {
                                'mobile_replica_id': r.mobile_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.mobile_app_ids] if self.ref_id.mobile_app_ids else False,
                'odoo_ids': [[0, 0, {
                                'odoo_replica_id': r.odoo_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.odoo_ids] if self.ref_id.odoo_ids else False,
                'tableau_ids': [[0, 0, {
                                'tableau_replica_id': r.tableau_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.tableau_ids] if self.ref_id.tableau_ids else False,
                'sas_ids': [[0, 0, {
                                'sas_replica_id': r.sas_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.sas_ids] if self.ref_id.sas_ids else False,
                'etl_ids': [[0, 0, {
                                'etl_replica_id': r.etl_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.etl_ids] if self.ref_id.etl_ids else False,
                'functional_ids': [[0, 0, {
                                'functional_replica_id': r.functional_replica_id.id,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_ctc': r.implementation_total_ctc,
                                'support_total_ctc': r.support_total_ctc,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.ref_id.functional_ids] if self.ref_id.functional_ids else False,
                'consultancy_ids': [[0, 0, {
                                'consultancy_replica_id': r.consultancy_replica_id.id,
                                'consultancy_type': r.consultancy_type,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'experience_proposed': r.experience_proposed,
                                'man_month_rate': r.man_month_rate,
                                'man_month_effort': r.man_month_effort,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.consultancy_ids] if self.ref_id.consultancy_ids else False,
                'it_infra_consultancy_ids': [[0, 0, {
                                'it_infra_replica_id': r.it_infra_replica_id.id,
                                'consultancy_type': r.consultancy_type,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'experience_proposed': r.experience_proposed,
                                'man_month_rate': r.man_month_rate,
                                'man_month_effort': r.man_month_effort,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.it_infra_consultancy_ids] if self.ref_id.it_infra_consultancy_ids else False,
                'social_consultancy_ids': [[0, 0, {
                                'social_consultancy_replica_id': r.social_consultancy_replica_id.id,
                                'consultancy_type': r.consultancy_type,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'experience_proposed': r.experience_proposed,
                                'man_month_rate': r.man_month_rate,
                                'man_month_effort': r.man_month_effort,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.social_consultancy_ids] if self.ref_id.social_consultancy_ids else False,
                'software_resource_ids': [[0, 0, {
                                'software_resource_replica_id': r.software_resource_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.software_resource_ids] if self.ref_id.software_resource_ids else False,
                'social_resource_ids': [[0, 0, {
                                'social_resource_replica_id': r.social_resource_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.social_resource_ids] if self.ref_id.social_resource_ids else False,
                'consulatncy_resource_ids': [[0, 0, {
                                'consulatncy_resource_replica_id': r.consulatncy_resource_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.consulatncy_resource_ids] if self.ref_id.consulatncy_resource_ids else False,
                'staffing_resource_ids': [[0, 0, {
                                'staffing_replica_id': r.staffing_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.staffing_resource_ids] if self.ref_id.staffing_resource_ids else False,
                'third_party_audit_ids': [[0, 0, {
                                'third_party_replica_id': r.third_party_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.third_party_audit_ids] if self.ref_id.third_party_audit_ids else False,
                'reimbursement_ids': [[0, 0, {
                                'reimbursement_replica_id': r.reimbursement_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.reimbursement_ids] if self.ref_id.reimbursement_ids else False,
                'strategic_partner_sharing_ids': [[0, 0, {
                                'strategic_partner_replica_id': r.strategic_partner_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.strategic_partner_sharing_ids] if self.ref_id.strategic_partner_sharing_ids else False,
                'domain_email_sms_ids': [[0, 0, {
                                'domain_sms_replica_id': r.domain_sms_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.domain_email_sms_ids] if self.ref_id.domain_email_sms_ids else False,
                'mobile_app_store_ids': [[0, 0, {
                                'mobile_app_replica_id': r.mobile_app_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.mobile_app_store_ids] if self.ref_id.mobile_app_store_ids else False,
                'survey_degitalisation_ids': [[0, 0, {
                                'survey_replica_id': r.survey_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.survey_degitalisation_ids] if self.ref_id.survey_degitalisation_ids else False,
                'ancillary_ids': [[0, 0, {
                                'ancillary_replica_id': r.ancillary_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.ancillary_ids] if self.ref_id.ancillary_ids else False,
                'out_of_pocket_expenditure_ids': [[0, 0, {
                                'expanditure_replica_id': r.expanditure_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                                'sort_no': r.sort_no,

                            }] for r in self.ref_id.out_of_pocket_expenditure_ids] if self.ref_id.out_of_pocket_expenditure_ids else False,
                'total_operation_support_ids': [[0, 0, {
                                'total_operation_replica_id': r.total_operation_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                                'sort_no': r.sort_no,

                            }] for r in self.ref_id.total_operation_support_ids] if self.ref_id.total_operation_support_ids else False,
                'external_ancillary_ids': [[0, 0, {
                                'estimation_replica_id': r.estimation_replica_id.id,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'man_month_rate': r.man_month_rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'sort_no': r.sort_no,
                                'remark':r.remark,
                            }] for r in self.ref_id.external_ancillary_ids] if self.ref_id.external_ancillary_ids else False, 
                'it_infra_puchase_ids': [[0, 0, {
                                'estimation_replica_id': r.estimation_replica_id.id,
                                'infra_id': r.infra_id.id,
                                'other_item': r.other_item,
                                'description': r.description,
                                'purchase_unit': r.purchase_unit,
                                'purchase_rate': r.purchase_rate,
                                'purchase_qty': r.purchase_qty,
                                'purchase_cost': r.purchase_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.it_infra_puchase_ids] if self.ref_id.it_infra_puchase_ids else False,
                'computer_hardware_ids': [[0, 0, {
                                'hardware_replica_id': r.hardware_replica_id.id,
                                'item': r.item,
                                'description': r.description,
                                'purchase_unit': r.purchase_unit,
                                'purchase_rate': r.purchase_rate,
                                'purchase_qty': r.purchase_qty,
                                'purchase_cost': r.purchase_cost,
                                'maintenance_unit': r.maintenance_unit,
                                'maintenance_rate': r.maintenance_rate,
                                'maintenance_qty': r.maintenance_qty,
                                'maintenance_cost': r.maintenance_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.computer_hardware_ids] if self.ref_id.computer_hardware_ids else False,
                'software_licence_ids': [[0, 0, {
                                'license_replica_id': r.license_replica_id.id,
                                # 'license_id': r.license_id.id,
                                'item': r.item,
                                'description': r.description,
                                'purchase_unit': r.purchase_unit,
                                'purchase_rate': r.purchase_rate,
                                'purchase_qty': r.purchase_qty,
                                'purchase_cost': r.purchase_cost,
                                'maintenance_unit': r.maintenance_unit,
                                'maintenance_rate': r.maintenance_rate,
                                'maintenance_qty': r.maintenance_qty,
                                'maintenance_cost': r.maintenance_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.software_licence_ids] if self.ref_id.software_licence_ids else False,
                'estimate_ids': [[0, 0, {
                                'estimation_replica_id': r.estimation_replica_id.id,
                                'account_head_id': r.account_head_id.id,
                                'account_subhead_id': r.account_subhead_id.id,
                                'purchase_cost': r.purchase_cost,
                                'production_overhead': r.production_overhead,
                                'logistic_cost': r.logistic_cost,
                                'company_overhead': r.company_overhead,
                                'total_profit_overhead': r.total_profit_overhead,
                                'code': r.code,
                                'sort_no': r.sort_no,
                            }] for r in self.ref_id.estimate_ids] if self.ref_id.estimate_ids else False,
                'proposed_eq' : self.ref_id.proposed_eq,
                'maintenance_percentage1' : self.ref_id.maintenance_percentage1,
                'maintenance_period' : self.ref_id.maintenance_period,
                'eq_approved' : self.ref_id.eq_approved,
                'margin_adjustment' : self.ref_id.margin_adjustment,
                'actual_margin' : self.ref_id.actual_margin,
                'gross_profit_margin' : self.ref_id.gross_profit_margin,
                'bid_currency' : self.ref_id.bid_currency,
                'exchange_rate_to_inr' : self.ref_id.exchange_rate_to_inr,
                'bid_value_without_tax' : self.ref_id.bid_value_without_tax,
                'pbg_implementation_ids': [[0, 0, {
                                'pbg_replica_id': r.pbg_replica_id.id,
                                'item': r.item,
                                'implementation_percentage': r.implementation_percentage,
                                'implementation_value': r.implementation_value,
                                'value_edit_bool': r.value_edit_bool,
                                'percentage_edit_bool': r.percentage_edit_bool,
                                'remark':r.remark,
                            }] for r in self.ref_id.pbg_implementation_ids] if self.ref_id.pbg_implementation_ids else False,
                'pbg_support_ids': [[0, 0, {
                                'pbg_support_replica_id': r.pbg_support_replica_id.id,
                                'item': r.item,
                                'support_percentage': r.support_percentage,
                                'support_value': r.support_value,
                                'value_edit_bool': r.value_edit_bool,
                                'percentage_edit_bool': r.percentage_edit_bool,
                                'remark':r.remark,
                            }] for r in self.ref_id.pbg_support_ids] if self.ref_id.pbg_support_ids else False,
                'pbg_implement' : self.ref_id.pbg_implement,
                'pbg_support' : self.ref_id.pbg_support,
                'eq_log_ids': [[0, 0, {
                                'log_replica_id': r.log_replica_id.id,
                                'date': r.date,
                                'action_by_id': r.action_by_id.id,
                                'remark': r.remark,
                                'state': r.state,
                            }] for r in self.ref_id.eq_log_ids] if self.ref_id.eq_log_ids else False,
                'state' : self.ref_id.state,
                'estimation_id':self.ref_id.id,
                'date': datetime.now(),
                'action': action,
                'details':details,
                'month': self.ref_id.month,
                'op_month':self.ref_id.op_month,
                'milestone_total':self.ref_id.milestone_total,
                'quote_ids': [[0, 0, {
                                'quote_replica_id': r.quote_replica_id.id,
                                'paticulars': r.paticulars,
                                'amount': r.amount,
                            }] for r in self.ref_id.quote_ids] if self.ref_id.quote_ids else False,
                'paticulars_ids': [[0, 0, {
                                'paticular_replica_id': r.paticular_replica_id.id,
                                'paticulars_name': r.paticulars_name,
                                'amount': r.amount,
                            }] for r in self.ref_id.paticulars_ids] if self.ref_id.paticulars_ids else False,
                # 'deliverable_ids': [[0, 0, {
                #                 'deliverable_replica_id': r.deliverable_replica_id.id,
                #                 'milestones': r.milestones,
                #                 'deliverables': r.deliverables,
                #                 'payment_term': r.payment_term,
                #                 'month': r.month,
                #             }] for r in self.ref_id.deliverable_ids] if self.ref_id.deliverable_ids else False,
                'op_year_ids': [[0, 0, {
                                'opyear_replica_id': r.opyear_replica_id.id,
                                'time_line': r.time_line,
                                'opening_balance': r.opening_balance,
                                'inception': r.inception,
                                'srs': r.srs,
                                'uat': r.uat,
                                'golive': r.golive,
                                'delivery': r.delivery,
                                'o_and_m': r.o_and_m,
                                'milestone7': r.milestone7,
                                'milestone8': r.milestone8,
                                'milestone9': r.milestone9,
                                'milestone10': r.milestone10,
                                'milestone11': r.milestone11,
                                'milestone12': r.milestone12,
                                'total_inflow': r.total_inflow,
                                'resource_internal': r.resource_internal,
                                'resource_external': r.resource_external,
                                'it_infra': r.it_infra,
                                'ancillary': r.ancillary,
                                'coh': r.coh,
                                'others': r.others,
                                'total_outflow': r.total_outflow,
                                'closing_balance': r.closing_balance,
                                'cap_closure_bool': r.cap_closure_bool,
                            }] for r in self.ref_id.op_year_ids] if self.ref_id.op_year_ids else False,
                'cap_year_ids': [[0, 0, {
                                'capyear_replica_id': r.capyear_replica_id.id,
                                'time_line': r.time_line,
                                'opening_balance': r.opening_balance,
                                'inception': r.inception,
                                'srs': r.srs,
                                'uat': r.uat,
                                'golive': r.golive,
                                'delivery': r.delivery,
                                'o_and_m': r.o_and_m,
                                'milestone7': r.milestone7,
                                'milestone8': r.milestone8,
                                'milestone9': r.milestone9,
                                'milestone10': r.milestone10,
                                'total_inflow': r.total_inflow,
                                'resource_internal': r.resource_internal,
                                'resource_external': r.resource_external,
                                'it_infra': r.it_infra,
                                'ancillary': r.ancillary,
                                'coh': r.coh,
                                'others': r.others,
                                'total_outflow': r.total_outflow,
                                'closing_balance': r.closing_balance,
                                'cap_closure_bool': r.cap_closure_bool,
                            }] for r in self.ref_id.cap_year_ids] if self.ref_id.cap_year_ids else False,
            })
            existing_records = self.env['kw_eq_audit_trail_details'].sudo().search([('kw_oppertuinity_id','=',self.ref_id.kw_oppertuinity_id.id)])
            if not existing_records:
                self.env['kw_eq_audit_trail_details'].sudo().create({
                    'client_id' : self.ref_id.client_id.id,
                    'kw_oppertuinity_id' : self.ref_id.kw_oppertuinity_id.id,
                    'level_1_id' : self.ref_id.level_1_id.id,
                    'estimation_id':self.ref_id.id,
                    'level_2_id':self.ref_id.level_2_id.id,
                    'level_3_id':self.ref_id.level_3_id.id,
                    'level_4_id':self.ref_id.level_4_id.id,
                    'level_5_id':self.ref_id.level_5_id.id,
                    'level_6_id':self.ref_id.level_6_id.id,
                    'audit_trail_details_ids': [(4, var.id)] })
            else:
                existing_records.write({'audit_trail_details_ids': [(4, var.id)]})
        else:
            var = self.env['kw_eq_replica'].sudo().create({
            'client_id' : self.revision_id.client_id.id,
            'code':self.revision_id.kw_oppertuinity_id.code,
            'kw_oppertuinity_id' : self.revision_id.kw_oppertuinity_id.id,
            'revised_level_1_id' : self.revision_id.revised_level_1_id.id,
            'revised_level_2_id' : self.revision_id.revised_level_2_id.id,
            'revised_level_3_id' : self.revision_id.revised_level_3_id.id,
            'revised_level_4_id' : self.revision_id.revised_level_4_id.id,
            'revised_level_5_id' : self.revision_id.revised_level_5_id.id,
            'revised_level_6_id' : self.revision_id.revised_level_6_id.id,
           'technology_ids': [[0, 0, {
                                'technology_replica_id': r.technology_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.technology_ids] if self.revision_id.technology_ids else False,
                'java_ids': [[0, 0, {
                                'java_replica_id': r.java_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.java_ids] if self.revision_id.java_ids else False,
                'php_ids': [[0, 0, {
                                'php_replica_id': r.php_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.php_ids] if self.revision_id.php_ids else False,
                'dot_net_core_ids': [[0, 0, {
                                'dot_net_core_replica_id': r.dot_net_core_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.dot_net_core_ids] if self.revision_id.dot_net_core_ids else False,
                'mobile_app_ids': [[0, 0, {
                                'mobile_replica_id': r.mobile_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.mobile_app_ids] if self.revision_id.mobile_app_ids else False,
                'odoo_ids': [[0, 0, {
                                'odoo_replica_id': r.odoo_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.odoo_ids] if self.revision_id.odoo_ids else False,
                'tableau_ids': [[0, 0, {
                                'tableau_replica_id': r.tableau_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.tableau_ids] if self.revision_id.tableau_ids else False,
                'sas_ids': [[0, 0, {
                                'sas_replica_id': r.sas_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.sas_ids] if self.revision_id.sas_ids else False,
                'etl_ids': [[0, 0, {
                                'etl_replica_id': r.etl_replica_id.id,
                                'skill_id': r.skill_id.id,
                                'designation_id': r.designation_id.id,
                                'experience': r.experience,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_cost': r.implementation_total_cost,
                                'support_total_cost': r.support_total_cost,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.etl_ids] if self.revision_id.etl_ids else False,
                'functional_ids': [[0, 0, {
                                'functional_replica_id': r.functional_replica_id.id,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'implementation_man_month': r.implementation_man_month,
                                'support_man_month': r.support_man_month,
                                'implementation_total_ctc': r.implementation_total_ctc,
                                'support_total_ctc': r.support_total_ctc,
                                'ctc': r.ctc,
                                'remark':r.remark,
                            }] for r in self.revision_id.functional_ids] if self.revision_id.functional_ids else False,
                'consultancy_ids': [[0, 0, {
                                'consultancy_replica_id': r.consultancy_replica_id.id,
                                'consultancy_type': r.consultancy_type,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'experience_proposed': r.experience_proposed,
                                'man_month_rate': r.man_month_rate,
                                'man_month_effort': r.man_month_effort,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.consultancy_ids] if self.revision_id.consultancy_ids else False,
                'it_infra_consultancy_ids': [[0, 0, {
                                'it_infra_replica_id': r.it_infra_replica_id.id,
                                'consultancy_type': r.consultancy_type,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'experience_proposed': r.experience_proposed,
                                'man_month_rate': r.man_month_rate,
                                'man_month_effort': r.man_month_effort,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.it_infra_consultancy_ids] if self.revision_id.it_infra_consultancy_ids else False,
                'social_consultancy_ids': [[0, 0, {
                                'social_consultancy_replica_id': r.social_consultancy_replica_id.id,
                                'consultancy_type': r.consultancy_type,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'experience_proposed': r.experience_proposed,
                                'man_month_rate': r.man_month_rate,
                                'man_month_effort': r.man_month_effort,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.social_consultancy_ids] if self.revision_id.social_consultancy_ids else False,
                'software_resource_ids': [[0, 0, {
                                'software_resource_replica_id': r.software_resource_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.software_resource_ids] if self.revision_id.software_resource_ids else False,
                'social_resource_ids': [[0, 0, {
                                'social_resource_replica_id': r.social_resource_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.social_resource_ids] if self.revision_id.social_resource_ids else False,
                'consulatncy_resource_ids': [[0, 0, {
                                'consulatncy_resource_replica_id': r.consulatncy_resource_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.consulatncy_resource_ids] if self.revision_id.consulatncy_resource_ids else False,
                'staffing_resource_ids': [[0, 0, {
                                'staffing_replica_id': r.staffing_replica_id.id,
                                'resource_deploy_duration': r.resource_deploy_duration,
                                'average_percentage':r.average_percentage,
                                'first_year': r.first_year,
                                'average': r.average,
                                'skill': r.skill,
                                'qualification': r.qualification,
                                'resources': r.resources,
                                'man_month': r.man_month,
                                'ctc': r.ctc,
                                'ope_month': r.ope_month,
                                'total_cost': r.total_cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.staffing_resource_ids] if self.revision_id.staffing_resource_ids else False,
                'third_party_audit_ids': [[0, 0, {
                                'third_party_replica_id': r.third_party_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.third_party_audit_ids] if self.revision_id.third_party_audit_ids else False,
                'reimbursement_ids': [[0, 0, {
                                'reimbursement_replica_id': r.reimbursement_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.reimbursement_ids] if self.revision_id.reimbursement_ids else False,
                'strategic_partner_sharing_ids': [[0, 0, {
                                'strategic_partner_replica_id': r.strategic_partner_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.strategic_partner_sharing_ids] if self.revision_id.strategic_partner_sharing_ids else False,
                'domain_email_sms_ids': [[0, 0, {
                                'domain_sms_replica_id': r.domain_sms_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.domain_email_sms_ids] if self.revision_id.domain_email_sms_ids else False,
                'mobile_app_store_ids': [[0, 0, {
                                'mobile_app_replica_id': r.mobile_app_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.mobile_app_store_ids] if self.revision_id.mobile_app_store_ids else False,
                'survey_degitalisation_ids': [[0, 0, {
                                'survey_replica_id': r.survey_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.survey_degitalisation_ids] if self.revision_id.survey_degitalisation_ids else False,
                'ancillary_ids': [[0, 0, {
                                'ancillary_replica_id': r.ancillary_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                            }] for r in self.revision_id.ancillary_ids] if self.revision_id.ancillary_ids else False,
                'out_of_pocket_expenditure_ids': [[0, 0, {
                                'expanditure_replica_id': r.expanditure_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                                'sort_no': r.sort_no,

                            }] for r in self.revision_id.out_of_pocket_expenditure_ids] if self.revision_id.out_of_pocket_expenditure_ids else False,
                'total_operation_support_ids': [[0, 0, {
                                'total_operation_replica_id': r.total_operation_replica_id.id,
                                'ancillary_id': r.ancillary_id.id,
                                'item': r.item,
                                'other_item': r.other_item,
                                'unit': r.unit,
                                'rate': r.rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'remark':r.remark,
                                'sort_no': r.sort_no,

                            }] for r in self.revision_id.total_operation_support_ids] if self.revision_id.total_operation_support_ids else False,
                'external_ancillary_ids': [[0, 0, {
                                'estimation_replica_id': r.estimation_replica_id.id,
                                'designation_id': r.designation_id.id,
                                'other_item': r.other_item,
                                'man_month_rate': r.man_month_rate,
                                'qty': r.qty,
                                'cost': r.cost,
                                'sort_no': r.sort_no,
                                'remark':r.remark,
                            }] for r in self.ref_id.external_ancillary_ids] if self.ref_id.external_ancillary_ids else False, 
                'it_infra_puchase_ids': [[0, 0, {
                                'estimation_replica_id': r.estimation_replica_id.id,
                                'infra_id': r.infra_id.id,
                                'other_item': r.other_item,
                                'description': r.description,
                                'purchase_unit': r.purchase_unit,
                                'purchase_rate': r.purchase_rate,
                                'purchase_qty': r.purchase_qty,
                                'purchase_cost': r.purchase_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.it_infra_puchase_ids] if self.ref_id.it_infra_puchase_ids else False,
                'computer_hardware_ids': [[0, 0, {
                                'hardware_replica_id': r.hardware_replica_id.id,
                                'item': r.item,
                                'description': r.description,
                                'purchase_unit': r.purchase_unit,
                                'purchase_rate': r.purchase_rate,
                                'purchase_qty': r.purchase_qty,
                                'purchase_cost': r.purchase_cost,
                                'maintenance_unit': r.maintenance_unit,
                                'maintenance_rate': r.maintenance_rate,
                                'maintenance_qty': r.maintenance_qty,
                                'maintenance_cost': r.maintenance_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.computer_hardware_ids] if self.ref_id.computer_hardware_ids else False,
                'software_licence_ids': [[0, 0, {
                                'license_replica_id': r.license_replica_id.id,
                                # 'license_id': r.license_id.id,
                                'item': r.item,
                                'description': r.description,
                                'purchase_unit': r.purchase_unit,
                                'purchase_rate': r.purchase_rate,
                                'purchase_qty': r.purchase_qty,
                                'purchase_cost': r.purchase_cost,
                                'maintenance_unit': r.maintenance_unit,
                                'maintenance_rate': r.maintenance_rate,
                                'maintenance_qty': r.maintenance_qty,
                                'maintenance_cost': r.maintenance_cost,
                                'remark':r.remark,
                            }] for r in self.ref_id.software_licence_ids] if self.ref_id.software_licence_ids else False,
            'estimate_ids': [[0, 0, {
                            'estimation_replica_id': r.estimation_replica_id.id,
                            'account_head_id': r.account_head_id.id,
                            'account_subhead_id': r.account_subhead_id.id,
                            'purchase_cost': r.purchase_cost,
                            'production_overhead': r.production_overhead,
                            'logistic_cost': r.logistic_cost,
                            'company_overhead': r.company_overhead,
                            'total_profit_overhead': r.total_profit_overhead,
                            'code': r.code,
                            'sort_no': r.sort_no,
                            'revised_purchase_cost':r.revised_purchase_cost,
                            'revised_production_overhead':r.revised_production_overhead,
                            'revised_logistic_cost':r.revised_logistic_cost,
                            'revised_company_overhead':r.revised_company_overhead,
                            'revised_total_profit_overhead':r.revised_total_profit_overhead,
                        }] for r in self.revision_id.estimate_ids] if self.revision_id.estimate_ids else False,
            'proposed_eq' : self.revision_id.proposed_eq,
            'maintenance_percentage1' : self.revision_id.maintenance_percentage1,
            'maintenance_period' : self.revision_id.maintenance_period,
            'eq_approved' : self.revision_id.eq_approved,
            'margin_adjustment' : self.revision_id.margin_adjustment,
            'actual_margin' : self.revision_id.actual_margin,
            'gross_profit_margin' : self.revision_id.gross_profit_margin,
            'bid_currency' : self.revision_id.bid_currency,
            'exchange_rate_to_inr' : self.revision_id.exchange_rate_to_inr,
            'bid_value_without_tax' : self.revision_id.bid_value_without_tax,
            'revised_proposed_eq':self.revision_id.revised_proposed_eq,
            'revised_eq_approved':self.revision_id.revised_eq_approved,
            'revised_margin_adjustment':self.revision_id.revised_margin_adjustment,
            'revised_actual_margin':self.revision_id.revised_actual_margin,
            'revised_gross_profit_margin':self.revision_id.revised_gross_profit_margin,
            'revised_bid_value_without_tax':self.revision_id.revised_bid_value_without_tax,
            'revised_exchange_rate_to_inr':self.revision_id.revised_exchange_rate_to_inr,
            'pbg_implementation_ids': [[0, 0, {
                            'pbg_replica_id': r.pbg_replica_id.id,
                            'item': r.item,
                            'implementation_percentage': r.implementation_percentage,
                            'implementation_value': r.implementation_value,
                            'value_edit_bool': r.value_edit_bool,
                            'percentage_edit_bool': r.percentage_edit_bool,
                            'remark':r.remark,
                        }] for r in self.revision_id.pbg_implementation_ids] if self.revision_id.pbg_implementation_ids else False,
            'pbg_support_ids': [[0, 0, {
                            'pbg_support_replica_id': r.pbg_support_replica_id.id,
                            'item': r.item,
                            'support_percentage': r.support_percentage,
                            'support_value': r.support_value,
                            'value_edit_bool': r.value_edit_bool,
                            'percentage_edit_bool': r.percentage_edit_bool,
                            'remark':r.remark,
                        }] for r in self.revision_id.pbg_support_ids] if self.revision_id.pbg_support_ids else False,
            'pbg_implement' : self.revision_id.pbg_implement,
            'pbg_support' : self.revision_id.pbg_support,
            'eq_log_ids': [[0, 0, {
                                'log_replica_id': r.log_replica_id.id,
                                'date': r.date,
                                'action_by_id': r.action_by_id.id,
                                'remark': r.remark,
                                'revision_state': r.revision_state,
                            }] for r in self.revision_id.eq_log_ids] if self.revision_id.eq_log_ids else False,
            'revision_state' : self.revision_id.state,
            'estimation_id':self.revision_id.estimation_id.id,
            'revision_id':self.revision_id.id,
            'date': datetime.now(),
            'action': action,
            'details':details,
            'type':'revision',
            'month': self.revision_id.month,
                'op_month':self.revision_id.op_month,
                'milestone_total':self.revision_id.milestone_total,
                'quote_ids': [[0, 0, {
                                'quote_replica_id': r.quote_replica_id.id,
                                'paticulars': r.paticulars,
                                'amount': r.amount,
                            }] for r in self.revision_id.quote_ids] if self.revision_id.quote_ids else False,
                'paticulars_ids': [[0, 0, {
                                'paticular_replica_id': r.paticular_replica_id.id,
                                'paticulars_name': r.paticulars_name,
                                'amount': r.amount,
                            }] for r in self.revision_id.paticulars_ids] if self.revision_id.paticulars_ids else False,
                # 'deliverable_ids': [[0, 0, {
                #                 'deliverable_replica_id': r.deliverable_replica_id.id,
                #                 'milestones': r.milestones,
                #                 'deliverables': r.deliverables,
                #                 'payment_term': r.payment_term,
                #                 'month': r.month,
                #             }] for r in self.ref_id.deliverable_ids] if self.ref_id.deliverable_ids else False,
                'op_year_ids': [[0, 0, {
                                'opyear_replica_id': r.opyear_replica_id.id,
                                'time_line': r.time_line,
                                'opening_balance': r.opening_balance,
                                'inception': r.inception,
                                'srs': r.srs,
                                'uat': r.uat,
                                'golive': r.golive,
                                'delivery': r.delivery,
                                'o_and_m': r.o_and_m,
                                'milestone7': r.milestone7,
                                'milestone8': r.milestone8,
                                'milestone9': r.milestone9,
                                'milestone10': r.milestone10,
                                'milestone11': r.milestone11,
                                'milestone12': r.milestone12,
                                'total_inflow': r.total_inflow,
                                'resource_internal': r.resource_internal,
                                'resource_external': r.resource_external,
                                'it_infra': r.it_infra,
                                'ancillary': r.ancillary,
                                'coh': r.coh,
                                'others': r.others,
                                'total_outflow': r.total_outflow,
                                'closing_balance': r.closing_balance,
                                'cap_closure_bool': r.cap_closure_bool,
                            }] for r in self.revision_id.op_year_ids] if self.revision_id.op_year_ids else False,
                'cap_year_ids': [[0, 0, {
                                'capyear_replica_id': r.capyear_replica_id.id,
                                'time_line': r.time_line,
                                'opening_balance': r.opening_balance,
                                'inception': r.inception,
                                'srs': r.srs,
                                'uat': r.uat,
                                'golive': r.golive,
                                'delivery': r.delivery,
                                'o_and_m': r.o_and_m,
                                'milestone7': r.milestone7,
                                'milestone8': r.milestone8,
                                'milestone9': r.milestone9,
                                'milestone10': r.milestone10,
                                'total_inflow': r.total_inflow,
                                'resource_internal': r.resource_internal,
                                'resource_external': r.resource_external,
                                'it_infra': r.it_infra,
                                'ancillary': r.ancillary,
                                'coh': r.coh,
                                'others': r.others,
                                'total_outflow': r.total_outflow,
                                'closing_balance': r.closing_balance,
                                'cap_closure_bool': r.cap_closure_bool,
                            }] for r in self.revision_id.cap_year_ids] if self.revision_id.cap_year_ids else False,
            
            
        })
            existing_records = self.env['kw_eq_audit_trail_details'].sudo().search([('estimation_id','=',self.revision_id.estimation_id.id)])
            if not existing_records:
                self.env['kw_eq_audit_trail_details'].sudo().create({
                    'client_id' : self.revision_id.client_id.id,
                    'kw_oppertuinity_id' : self.revision_id.kw_oppertuinity_id.id,
                    'estimation_id':self.revision_id.estimation_id.id,
                    'revised_level_1_id' : self.revision_id.revised_level_1_id.id,
                    'revised_level_2_id':self.revision_id.revised_level_2_id.id,
                    'revised_level_3_id':self.revision_id.revised_level_3_id.id,
                    'revised_level_4_id':self.revision_id.revised_level_4_id.id,
                    'revised_level_5_id':self.revision_id.revised_level_5_id.id,
                    'revised_level_6_id':self.revision_id.revised_level_6_id.id,
                    'revision_id':self.revision_id.id,
                    'audit_trail_details_ids': [(4, var.id)] })
            else:
                existing_records.write({'audit_trail_details_ids': [(4, var.id)]})




    def proceed_with_remark_apply(self):
        if self.env.context.get('type') == 'eq':
            active_id = self.env.context.get('current_id')
            if self.ref_id.level_1_id.id == self.env.user.employee_ids.id and self.ref_id.state == "version_1":
                self.ref_id.pending_at = self.ref_id.level_2_id.name
                self.ref_id.effective_from = date.today()
                role = self.ref_id.level_1_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Preparation by {role}"
                role1 = self.ref_id.level_1_role.split('(')[0].strip()
                details = f"{role1} prepared the EQ"
                self.replica_data(action,details)
                model_data = self.env['kw_eq_estimation'].search([('id','=',active_id)])
                model_data.write({
                        'state': self.env.context.get('state')
                    })
                self.ref_id.eq_log_ids.create({
                'eq_id':self.ref_id.id,
                'eq_log_id':self.id,
                'action_by_id':self.env.user.id,
                'remark':self.remarks,
                'state':self.env.context.get('state')
                })
                template_id = self.env.ref('kw_eq.kw_eq_apply_mail_template')
                approver_email = ''
                approver = ''
                approval_pending = ''
                if template_id:
                    if self.ref_id.state=='version_2':
                        if self.ref_id.level_2_id.id:
                            approver=self.ref_id.level_1_id.name
                            approver_email =self.ref_id.level_2_id.work_email
                            approval_pending=self.ref_id.level_2_id.name
                    if approver_email:
                        template_id.with_context(email_to=approver_email,
                                                approver = approver,
                                                approval_pending=approval_pending,
                                                ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")            
                action_id = self.env.ref('kw_eq.kw_eq_estimation_action').id
                return {
                'type': 'ir.actions.act_url',
                'tag': 'reload',
                'url': f'/web#action={action_id}&model=kw_eq_estimation&view_type=list',
                'target': 'self',
                }
        elif self.env.context.get('type') == 'revision':
            active_id = self.env.context.get('revision_id')
            if self.revision_id.revised_level_1_id.id == self.env.user.employee_ids.id and self.revision_id.state == "draft":
                self.revision_id.pending_at = self.revision_id.revised_level_2_id.name
                self.revision_id.effective_from = date.today()
                role = self.revision_id.revised_level_1_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Revision Preparation by {role}"
                role1 = self.revision_id.revised_level_1_role.split('(')[0].strip()
                details = f"{role1} prepared the EQ Revision"
                
                model_data = self.env['kw_eq_revision'].search([('id','=',active_id)])
                model_data.write({
                        'state': self.env.context.get('state')
                    })
                self.revision_id.eq_log_ids.create({
                'eq_revision_id':self.revision_id.id,
                'action_by_id':self.env.user.id,
                'remark':self.remarks,
                'revision_state':self.env.context.get('state')
                })
                template_id = self.env.ref('kw_eq.kw_eq_revision_approve_mail_template')
                approver_email = self.revision_id.revised_level_2_id.work_email if self.revision_id.revised_level_2_id else ''
                approval_pending = self.revision_id.revised_level_2_id.name if self.revision_id.revised_level_2_id else ''
                approver = self.revision_id.revised_level_1_id.name
                if approver_email:
                    template_id.with_context(email_to=approver_email,
                                             approver = approver,
                                            approval_pending=approval_pending,
                                            status='applied',
                                            reject = False
                                            ).sudo().send_mail(self.revision_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                self.replica_data(action,details,revision=True)
                return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': f'EQ Revision is Applied successfully. Record is Sent to {self.revision_id.revised_level_2_id.name}',
                            'img_url':  '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }
         




    def proceed_with_remark_approve(self):
        if not self.env.context.get('revision_id'):
            active_id = self.env.context.get('current_id')
            if self.ref_id.level_2_id.id == self.env.user.employee_ids.id and self.ref_id.state == "version_2":
                if self.ref_id.level_3_id.id:
                    role = self.ref_id.level_2_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Reviewed by {role}"
                    role1 = self.ref_id.level_2_role.split('(')[0].strip()
                    details = f"{role1} Reviewed the EQ"
                    self.replica_data(action,details)
                    self.ref_id.state = "version_3"
                    self.ref_id.pending_at = self.ref_id.level_3_id.name
                else:
                    role = self.ref_id.level_2_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Approved by {role}"
                    role1 = self.ref_id.level_2_role.split('(')[0].strip()
                    details = f"{role1} Approved the EQ"
                    self.ref_id.state = "grant"
                    self.ref_id.pending_at = "---"
                    self.replica_data(action,details)
            elif self.ref_id.level_3_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_3':
                if self.ref_id.level_4_id.id:
                    role = self.ref_id.level_3_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Reviewed by {role}"
                    role1 = self.ref_id.level_3_role.split('(')[0].strip()
                    details = f"{role1} Reviewed the EQ"
                    self.replica_data(action,details)
                    self.ref_id.state = "version_4"
                    self.ref_id.pending_at = self.ref_id.level_4_id.name
                else:
                    role = self.ref_id.level_3_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Approved by {role}"
                    role1 = self.ref_id.level_3_role.split('(')[0].strip()
                    details = f"{role1} Approved the EQ"
                    self.ref_id.state = "grant"
                    self.ref_id.pending_at = "---"
                    self.replica_data(action,details)
            elif self.ref_id.level_4_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_4':
                if self.ref_id.level_5_id.id:
                    role = self.ref_id.level_4_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Reviewed by {role}"
                    role1 = self.ref_id.level_4_role.split('(')[0].strip()
                    details = f"{role1} Reviewed the EQ"
                    self.replica_data(action,details)
                    self.ref_id.state = "version_5"
                    self.ref_id.pending_at = self.ref_id.level_5_id.name
                else:
                    role = self.ref_id.level_4_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Approved by {role}"
                    role1 = self.ref_id.level_4_role.split('(')[0].strip()
                    details = f"{role1} Approved the EQ"
                    self.ref_id.state = "grant"
                    self.ref_id.pending_at = "---"
                    self.replica_data(action,details)
            elif self.ref_id.level_5_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_5':
                if self.ref_id.level_6_id.id:
                    role = self.ref_id.level_5_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Reviewed by {role}"
                    role1 = self.ref_id.level_5_role.split('(')[0].strip()
                    details = f"{role1} Reviewed the EQ"
                    self.replica_data(action,details)
                    self.ref_id.state = "version_6"
                    self.ref_id.pending_at = self.ref_id.level_6_id.name
                else:
                    role = self.ref_id.level_5_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Approved by {role}"
                    role1 = self.ref_id.level_5_role.split('(')[0].strip()
                    details = f"{role1} Approved the EQ"
                    self.ref_id.state = "grant"
                    self.ref_id.pending_at = "---"
                    self.replica_data(action,details)
            elif self.ref_id.level_6_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_6':
                role = self.ref_id.level_6_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Approved by {role}"
                role1 = self.ref_id.level_6_role.split('(')[0].strip()
                details = f"{role1} Approved the EQ"
                self.ref_id.state = "grant"
                self.ref_id.pending_at = "---"
                self.replica_data(action,details)
            elif self.ref_id.state == 'grant':
                self.ref_id.pending_at = "---"
                self.replica_data()
            self.ref_id.eq_log_ids.create({
            'eq_id':self.ref_id.id,
            'eq_log_id':self.id,
            'action_by_id':self.env.user.id,
            'remark':self.remarks,
            'state':self.ref_id.state
            })
            # if self._context.get('approve_for_templete'):
            template_id = self.env.ref('kw_eq.kw_eq_approve_mail_template')
            approver_email = ''
            approver = ''
            approval_pending = ''
            if template_id:
                if self.ref_id.state=='version_3':
                    if self.ref_id.level_3_id.id:
                        approver=self.ref_id.level_2_id.name
                        approver_email =self.ref_id.level_3_id.work_email
                        approval_pending=self.ref_id.level_3_id.name
                elif self.ref_id.state=='version_4':
                    if self.ref_id.level_4_id.id:
                        approver=self.ref_id.level_3_id.name
                        approver_email =self.ref_id.level_4_id.work_email
                        approval_pending=self.ref_id.level_4_id.name
                elif self.ref_id.state=='version_5':
                    if self.ref_id.level_5_id.id:
                        approver=self.ref_id.level_4_id.name
                        approver_email =self.ref_id.level_5_id.work_email
                        approval_pending=self.ref_id.level_5_id.name
                elif self.ref_id.state=='version_6':
                    if self.ref_id.level_6_id.id:
                        approver=self.ref_id.level_5_id.name
                        approver_email =self.ref_id.level_6_id.work_email
                        approval_pending=self.ref_id.level_6_id.name
                if approver_email:
                    template_id.with_context(email_to=approver_email,
                                            approver = approver,
                                            approval_pending=approval_pending,
                                            ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            action_id = self.env.ref('kw_eq.kw_eq_estimation_action').id
            return {
            'type': 'ir.actions.act_url',
            'tag': 'reload',
            'url': f'/web#action={action_id}&model=kw_eq_estimation&view_type=list',
            'target': 'self',
            }
        elif self.env.context.get('revision_id'):
            if self.revision_id.revised_level_2_id.id == self.env.user.employee_ids.id and self.revision_id.state == "applied":
                if self.revision_id.revised_level_3_id.id:
                    role = self.revision_id.revised_level_2_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Revision Reviewed by {role}"
                    role1 = self.revision_id.revised_level_2_role.split('(')[0].strip()
                    details = f"{role1} Reviewed the EQ Revision"
                    self.revision_id.state = "submit"
                    self.replica_data(action,details,revision=True)
                    self.revision_id.pending_at = self.revision_id.revised_level_3_id.name
            elif self.revision_id.revised_level_3_id.id == self.env.user.employee_ids.id and self.revision_id.state == 'submit':
                if self.env.context.get('state') == 'forward':
                    if self.revision_id.revised_level_4_id.id:
                        role = self.revision_id.revised_level_3_role.split('(')[-1].split(')')[0].strip()
                        action = f"EQ Revision Forwarded by {role}"
                        role1 = self.revision_id.revised_level_3_role.split('(')[0].strip()
                        details = f"{role1} Forwarded the EQ Revision"
                        self.revision_id.state = "forward"
                        self.replica_data(action,details,revision=True)
                        self.revision_id.pending_at = self.revision_id.revised_level_4_id.name
                if self.env.context.get('state') == 'grant':
                        role = self.revision_id.revised_level_3_role.split('(')[-1].split(')')[0].strip()
                        action = f"EQ Revision is granted by {role}"
                        details = f"{role} Granted the EQ Revision"
                        self.revision_id.state = "grant"
                        self.replica_data(action,details,revision=True)
                        self.revision_id.pending_at = f"Granted by {role}"
            elif self.revision_id.revised_level_4_id.id == self.env.user.employee_ids.id and self.revision_id.state == 'forward':
                if self.revision_id.revised_level_5_id.id:
                    role = self.revision_id.revised_level_4_role.split('(')[-1].split(')')[0].strip()
                    status = 'Recommended' if self.env.context.get('update_status') == 'recommend' else 'Not Recommended'
                    action = f"EQ Revision {status} by {role}"
                    role1 = self.revision_id.revised_level_4_role.split('(')[0].strip()
                    details = f"{role1} {status} the EQ Revision"
                    self.revision_id.state = 'recommend' if self.env.context.get('update_status') == 'recommend' else 'not_recommended'
                    self.replica_data(action,details,revision=True)
                    self.revision_id.pending_at = self.revision_id.revised_level_5_id.name

            elif self.revision_id.revised_level_5_id.id == self.env.user.employee_ids.id and self.revision_id.state in ('recommend','not_recommended'):
                role = self.revision_id.revised_level_5_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Revision is granted by {role}"
                details = f"{role} Granted the EQ Revision"
                self.revision_id.state = "grant"
                self.replica_data(action,details,revision=True)
                self.revision_id.pending_at = f"Granted by {role}"
            self.revision_id.eq_log_ids.create({
            'eq_revision_id':self.revision_id.id,
            'eq_log_id':self.id,
            'action_by_id':self.env.user.id,
            'remark':self.remarks,
            'revision_state':self.revision_id.state
            })

            template_id = self.env.ref('kw_eq.kw_eq_revision_approve_mail_template')
            approver_email = ''
            approver = ''
            approval_pending = ''
            if template_id:
                # if self._context.get('revision_approve'):
                if self.revision_id.state == 'submit':
                        if self.revision_id.revised_level_3_id.id:
                            approver=self.revision_id.revised_level_2_id.name
                            approver_email =self.revision_id.revised_level_3_id.work_email
                            approval_pending=self.revision_id.revised_level_3_id.name
                            status='submitted'
                if self.revision_id.state == 'forward':
                        if self.revision_id.revised_level_4_id.id:
                            approver=self.revision_id.revised_level_3_id.name
                            approver_email =self.revision_id.revised_level_4_id.work_email
                            approval_pending=self.revision_id.revised_level_4_id.name
                            status='forwarded'
                if self.revision_id.state in ('recommend','not_recommended'):
                        if self.revision_id.revised_level_5_id.id:
                            approver=self.revision_id.revised_level_4_id.name
                            approver_email =self.revision_id.revised_level_5_id.work_email
                            approval_pending=self.revision_id.revised_level_5_id.name
                            status='recommended' if self.revision_id.state == 'recommend' else 'not recommended'
                if approver_email:
                    template_id.with_context(email_to=approver_email,
                                            approver = approver,
                                            approval_pending=approval_pending,
                                            status=status,
                                            reject = False
                                            ).sudo().send_mail(self.revision_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            message = f"EQ revision sent to {approval_pending} Successfully. " if approval_pending != '' else 'EQ Revision Approved Successfully.'
            
            return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': message,
                        'img_url':  '/web/static/src/img/smile.svg',
                        'type': 'rainbow_man',
                        # 'url': f'/web#action={action_id}&model=kw_eq_revision&view_type=list',
                    }
                }
            



    def proceed_with_remark_reject(self):
        # active_id = self.env.context.get('current_id')
        if not self.env.context.get('revision_id'):
            if self.ref_id.level_2_id.id == self.env.user.employee_ids.id and self.ref_id.state == "version_2":
                role = self.ref_id.level_2_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Rejected by {role}"
                role1 = self.ref_id.level_2_role.split('(')[0].strip()
                details = f"{role1} Rejected the EQ"
                self.replica_data(action,details)
                self.ref_id.pending_at = self.ref_id.level_1_id.name
                self.ref_id.state = "version_1"
            elif self.ref_id.level_3_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_3':
                role = self.ref_id.level_3_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Rejected by {role}"
                role1 = self.ref_id.level_3_role.split('(')[0].strip()
                details = f"{role1} Rejected the EQ"
                self.replica_data(action,details)
                self.ref_id.state = "version_2"
                self.ref_id.pending_at = self.ref_id.level_2_id.name
            elif self.ref_id.level_4_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_4':
                role = self.ref_id.level_4_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Rejected by {role}"
                role1 = self.ref_id.level_4_role.split('(')[0].strip()
                details = f"{role1} Rejected the EQ"
                self.replica_data(action,details)
                self.ref_id.state = "version_3"
                self.ref_id.pending_at = self.ref_id.level_3_id.name
            elif self.ref_id.level_5_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_5':
                role = self.ref_id.level_5_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Rejected by {role}"
                role1 = self.ref_id.level_5_role.split('(')[0].strip()
                details = f"{role1} Rejected the EQ"
                self.replica_data(action,details)
                self.ref_id.state = "version_4"
                self.ref_id.pending_at = self.ref_id.level_4_id.name
            elif self.ref_id.level_6_id.id == self.env.user.employee_ids.id and self.ref_id.state == 'version_6':
                role = self.ref_id.level_6_role.split('(')[-1].split(')')[0].strip()
                action = f"EQ Rejected by {role}"
                role1 = self.ref_id.level_6_role.split('(')[0].strip()
                details = f"{role1} Rejected the EQ"
                self.replica_data(action,details)
                self.ref_id.state = "version_5"
                self.ref_id.pending_at = self.ref_id.level_5_id.name
            self.ref_id.eq_log_ids.create({
            'eq_id':self.ref_id.id,
            'eq_log_id':self.id,
            'action_by_id':self.env.user.id,
            'remark':self.remarks,
            'state':self.ref_id.state
            })
            if self._context.get('reject_for_templete'):
                template_id = self.env.ref('kw_eq.kw_eq_reject_mail_template')
                rejecter_email = ''
                rejecter = ''
                rejection_pending = ''
                if template_id:
                    if self.ref_id.state=='version_1':
                        rejecter=self.ref_id.level_2_id.name
                        rejecter_email =self.ref_id.level_1_id.work_email
                        rejection_pending=self.ref_id.level_1_id.name
                    elif self.ref_id.state=='version_2':
                        rejecter=self.ref_id.level_3_id.name
                        rejecter_email =self.ref_id.level_2_id.work_email
                        rejection_pending=self.ref_id.level_2_id.name
                    elif self.ref_id.state=='version_3':
                        rejecter=self.ref_id.level_4_id.name
                        rejecter_email =self.ref_id.level_3_id.work_email
                        rejection_pending=self.ref_id.level_3_id.name
                    elif self.ref_id.state=='version_4':
                        rejecter=self.ref_id.level_5_id.name
                        rejecter_email =self.ref_id.level_4_id.work_email
                        rejection_pending=self.ref_id.level_4_id.name
                    elif self.ref_id.state=='version_5':
                        rejecter=self.ref_id.level_6_id.name
                        rejecter_email =self.ref_id.level_5_id.work_email
                        rejection_pending=self.ref_id.level_5_id.name
                    else:
                        pass
                    template_id.with_context(email_to=rejecter_email,
                                                rejecter = rejecter,
                                                rejection_pending=rejection_pending,
                                                ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success(message='EQ Rejected.') 

            action_id = self.env.ref('kw_eq.kw_eq_estimation_action').id
            return {
            'type': 'ir.actions.act_url',
            'tag': 'reload',
            'url': f'/web#action={action_id}&model=kw_eq_estimation&view_type=list',
            'target': 'self',
            }
        elif self.env.context.get('revision_id'):
            if not self.env.context.get('revert'):
                if (self.revision_id.revised_level_5_id.id == self.env.user.employee_ids.id and self.revision_id.state in ('recommend','not_recommended')) or  (self.revision_id.revised_level_3_id.id == self.env.user.employee_ids.id and self.revision_id.state in ('submit')):
                    role = self.revision_id.revised_level_5_role.split('(')[-1].split(')')[0].strip() if self.revision_id.state in ('recommend','not_recommended') else self.revision_id.revised_level_3_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Revision is Rejected by {role}"
                    details = f"{role} Rejected the EQ Revision"
                    self.replica_data(action,details,revision=True)
                    self.revision_id.state = "rejected"
                    self.revision_id.pending_at = '--'
                    template_id = self.env.ref('kw_eq.kw_eq_revision_approve_mail_template')
                    approver_email = ''
                    approver = ''
                    approval_pending = ''
                    if self.revision_id.revised_level_5_id.id:
                        approver=self.revision_id.revised_level_5_id.name if self.revision_id.state in ('recommend','not_recommended') else self.revision_id.revised_level_3_id.name
                        status='rejected'
                        approver_email = ",".join(self.revision_id.revised_level_4_id.work_email) + ",".join(self.revision_id.revised_level_2_id.work_email) + ",".join(self.revision_id.revised_level_1_id.work_email) or ''
                    if approver_email:
                        template_id.with_context(email_to=approver_email,
                                                approver = approver,
                                                approval_pending=approval_pending,
                                                status=status,
                                                reject = True
                                                ).sudo().send_mail(self.revision_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            elif self.env.context.get('revert'):
                email_to = ''
                if self.revision_id.revised_level_2_id.id == self.env.user.employee_ids.id and self.revision_id.state == "applied":
                    role = self.revision_id.revised_level_2_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Revision Rejected by {role}"
                    role1 = self.revision_id.revised_level_2_role.split('(')[0].strip()
                    details = f"{role1} Rejected the EQ Revision"
                    self.replica_data(action,details,revision=True)
                    self.revision_id.pending_at = self.revision_id.revised_level_1_id.name
                    self.revision_id.state = "draft"
                    email_to = self.revision_id.revised_level_1_id.work_email
                elif self.revision_id.revised_level_3_id.id == self.env.user.employee_ids.id and self.revision_id.state == 'submit':
                    role = self.revision_id.revised_level_3_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Revision Rejected by {role}"
                    role1 = self.revision_id.revised_level_3_role.split('(')[0].strip()
                    details = f"{role1} Rejected the EQ Revision"
                    self.replica_data(action,details,revision=True)
                    self.revision_id.state = "applied"
                    self.revision_id.pending_at = self.revision_id.revised_level_2_id.name
                    email_to = self.revision_id.revised_level_2_id.work_email
                elif self.revision_id.revised_level_4_id.id == self.env.user.employee_ids.id and self.revision_id.state == 'forward':
                    role = self.revision_id.revised_level_4_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Revision Rejected by {role}"
                    role1 = self.revision_id.revised_level_4_role.split('(')[0].strip()
                    details = f"{role1} Rejected the EQ Revision"
                    self.replica_data(action,details,revision=True)
                    self.revision_id.state = "submit"
                    self.revision_id.pending_at = self.revision_id.revised_level_3_id.name
                    email_to = self.revision_id.revised_level_3_id.work_email
                elif self.revision_id.revised_level_5_id.id == self.env.user.employee_ids.id and self.revision_id.state in ('recommend','not_recommended'):
                    role = self.revision_id.revised_level_5_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Revision Rejected by {role}"
                    role1 = self.revision_id.revised_level_5_role.split('(')[0].strip()
                    details = f"{role1} Rejected the EQ Revision"
                    self.replica_data(action,details,revision=True)
                    self.revision_id.state = "applied" 
                    email_to = self.revision_id.revised_level_2_id.work_email
                    self.revision_id.pending_at = self.revision_id.revised_level_2_id.name
               
                
                self.revision_id.eq_log_ids.create({
                'eq_revision_id':self.revision_id.id,
                'eq_log_id':self.id,
                'action_by_id':self.env.user.id,
                'remark':self.remarks,
                'revision_state':self.revision_id.state
                })
                template_id = self.env.ref('kw_eq.kw_eq_revision_approve_mail_template')
                approver = ''
                approval_pending = ''
                # if self.revision_id.revised_level_5_id.id:
                approver=self.env.user.employee_ids.name
                status='reverted'
                email_to = email_to
                approval_pending = self.revision_id.pending_at
                approver_email = email_to
                if email_to:
                    template_id.with_context(email_to=approver_email,
                                            approver = approver,
                                            approval_pending=approval_pending,
                                            status=status,
                                            reject = True
                                            ).sudo().send_mail(self.revision_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                message = f'EQ Revision is Reverted. Application is sent to {approval_pending}' if approval_pending else 'EQ Revision is Reverted'
                return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': message,
                            'img_url':  '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }

    def proceed_with_remark_rollback(self):
        template_id = self.env.ref('kw_eq.kw_eq_rollback_mail_template')
        if template_id:
            if self.ref_id.state == "grant":
                if self.ref_id.level_6_id.id:
                    role = self.ref_id.level_6_role.split('(')[-1].split(')')[0].strip()
                    action = f"EQ Roll Backed to {role}"
                    role1 = self.ref_id.level_6_role.split('(')[0].strip()
                    details = f"{role1} Rollback the EQ"
                    self.replica_data(action,details)
                    self.ref_id.pending_at = self.ref_id.level_6_id.name
                    self.ref_id.state = "version_6"
                    rollback_to=self.ref_id.level_6_id.name
                    rollback_to_email =self.ref_id.level_6_id.work_email
                    rollback_pending=self.ref_id.level_6_id.name
                    template_id.with_context(email_to=rollback_to_email,
                                            rollback_to = rollback_to,
                                            rollback_pending=rollback_pending,
                                            ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    if self.ref_id.level_5_id.id:
                        role = self.ref_id.level_5_role.split('(')[-1].split(')')[0].strip()
                        action = f"EQ Roll Backed to {role}"
                        role1 = self.ref_id.level_5_role.split('(')[0].strip()
                        details = f"{role1} Rollback the EQ"
                        self.replica_data(action,details)
                        self.ref_id.pending_at = self.ref_id.level_5_id.name
                        self.ref_id.state = "version_5"
                        rollback_to=self.ref_id.level_5_id.name
                        rollback_to_email =self.ref_id.level_5_id.work_email
                        rollback_pending=self.ref_id.level_5_id.name
                        template_id.with_context(email_to=rollback_to_email,
                                                rollback_to = rollback_to,
                                                rollback_pending=rollback_pending,
                                                ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        if self.ref_id.level_4_id.id:
                            role = self.ref_id.level_4_role.split('(')[-1].split(')')[0].strip()
                            action = f"EQ Roll Backed to {role}"
                            role1 = self.ref_id.level_4_role.split('(')[0].strip()
                            details = f"{role1} Rollback the EQ"
                            self.replica_data(action,details)
                            self.ref_id.pending_at = self.ref_id.level_4_id.name
                            self.ref_id.state = "version_4"
                            rollback_to=self.ref_id.level_4_id.name
                            rollback_to_email =self.ref_id.level_4_id.work_email
                            rollback_pending=self.ref_id.level_4_id.name
                            template_id.with_context(email_to=rollback_to_email,
                                                    rollback_to = rollback_to,
                                                    rollback_pending=rollback_pending,
                                                    ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                        else:
                            if self.ref_id.level_3_id.id:
                                role = self.ref_id.level_3_role.split('(')[-1].split(')')[0].strip()
                                action = f"EQ Roll Backed to {role}"
                                role1 = self.ref_id.level_3_role.split('(')[0].strip()
                                details = f"{role1} Rollback the EQ"
                                self.replica_data(action,details)
                                self.ref_id.pending_at = self.ref_id.level_3_id.name
                                self.ref_id.state = "version_3"
                                rollback_to=self.ref_id.level_3_id.name
                                rollback_to_email =self.ref_id.level_3_id.work_email
                                rollback_pending=self.ref_id.level_3_id.name
                                template_id.with_context(email_to=rollback_to_email,
                                                        rollback_to = rollback_to,
                                                        rollback_pending=rollback_pending,
                                                        ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                            else:
                                if self.ref_id.level_2_id.id:
                                    role = self.ref_id.level_2_role.split('(')[-1].split(')')[0].strip()
                                    action = f"EQ Roll Backed to {role}"
                                    role1 = self.ref_id.level_2_role.split('(')[0].strip()
                                    details = f"{role1} Rollback the EQ"
                                    self.replica_data(action,details)
                                    self.ref_id.pending_at = self.ref_id.level_2_id.name
                                    self.ref_id.state = "version_2"
                                    rollback_to=self.ref_id.level_2_id.name
                                    rollback_to_email =self.ref_id.level_2_id.work_email
                                    rollback_pending=self.ref_id.level_3_id.name
                                    template_id.with_context(email_to=rollback_to_email,
                                                            rollback_to = rollback_to,
                                                            rollback_pending=rollback_pending,
                                                            ).sudo().send_mail(self.ref_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.ref_id.eq_log_ids.create({
        'eq_id':self.ref_id.id,
        'eq_log_id':self.id,
        'action_by_id':self.env.user.id,
        'remark':self.remarks,
        'state':self.ref_id.state
        })

    def proceed_with_remark_backlog(self):
        if self.ref_id.state == "version_1":
            self.ref_id.state = "grant"
            action = f"EQ is manually created."
            details = f"{self.env.user.employee_ids.name} manually created the EQ."
            self.replica_data(action,details)

        self.ref_id.eq_log_ids.create({
        'eq_id':self.ref_id.id,
        'eq_log_id':self.id,
        'action_by_id':self.env.user.id,
        'remark':self.remarks,
        'state':self.ref_id.state
        })
        action_id = self.env.ref('kw_eq.kw_eq_estimation_backlog_record_action').id
        return {
        'type': 'ir.actions.act_url',
        'tag': 'reload',
        'url': f'/web#action={action_id}&model=kw_eq_estimation&view_type=list',
        'target': 'self',
        }