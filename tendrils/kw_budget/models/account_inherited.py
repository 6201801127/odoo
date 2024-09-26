from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountInvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'

    project_wo_id = fields.Many2one('kw_project_budget_master_data',string="Project")
    budget_line = fields.Many2one('kw_revenue_budget_line',string='Treasury Budget Line',)
    capital_line = fields.Many2one('kw_capital_budget_line',string='Capital Budget Line',)
    project_line = fields.Many2one('kw_sbu_project_budget_line',string='Project Budget Line',)

    @api.onchange('budget_type','project_wo_id')
    def onchange_project_id(self):
        self.account_id,self.department_id,self.division_id,self.section_id = False, False, False,False
        project_budget_id = self.env['kw_project_budget_master_data'].sudo().search([('kw_wo_id','=',self.project_wo_id.kw_wo_id)],limit=1)
        budget_ids = self.env['kw_revenue_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.invoice_id.date),('fiscal_year_id.date_stop','>=',self.invoice_id.date)]).mapped('budget_dept')
        capital_ids = self.env['kw_capital_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.invoice_id.date),('fiscal_year_id.date_stop','>=',self.invoice_id.date)]).mapped('budget_dept')

        if self.budget_type == 'project' and project_budget_id:
            self.department_id = self.project_wo_id.sbu_id.representative_id.department_id.id 
            self.division_id = self.project_wo_id.sbu_id.representative_id.division.id
            self.section_id = self.project_wo_id.sbu_id.representative_id.section.id
            if project_budget_id and self.invoice_id.type not in ['out_invoice','out_refund']:
                project_budget_line_ids = self.env['kw_project_budget_line_items'].sudo().search([('project_crm_id','=',project_budget_id.id)])
                account_model = self.env['account.account']
                for line in project_budget_line_ids:
                    account_ids = account_model.search([('group_type','=',line.user_type_id.id),('user_type_id','=',line.group_head_id.id),('group_name','=',line.group_name.id),('account_head_id','=',line.account_head_id.id),('account_sub_head_id','=',line.account_sub_head_id.id)])
                    account_model += account_ids
                return {'domain': {'account_id': [('active', '=', True),('deprecated','=',False),('id', 'in', account_model.ids),('branch_id','=',self.invoice_id.unit_id.id)]}}
            else:
                return {'domain': {'account_id': [('active', '=', True),('deprecated','=',False),('branch_id','=',self.invoice_id.unit_id.id)]}}

        elif self.budget_type == 'treasury':
            self.project_wo_id = False
            if budget_ids:
                return {'domain': {'department_id': [('id','in',budget_ids.ids)]}}
            else:
                return {'domain': {'department_id': [('dept_type.code','=','department')]}}
        elif self.budget_type == 'capital':
            self.project_wo_id = False

            if capital_ids:
                return {'domain': {'department_id': [('id','in',capital_ids.ids)]}}
            else:
                return {'domain': {'department_id': [('dept_type.code','=','department')]}}
        else:
            self.project_wo_id = False
            return {'domain': {'department_id': [('dept_type.code','=','department')],'account_id': [('active', '=', True),('deprecated','=',False),('branch_id','=',self.invoice_id.unit_id.id)]}}

    @api.onchange('budget_line','capital_line')
    def onchange_budget_line(self):
        self.account_id = False
        if self.budget_line:
            return {'domain': {'account_id': [('id','=',self.budget_line.account_code_id.id),('branch_id','=',self.invoice_id.unit_id.id)]}}
        elif self.capital_line:
            return {'domain': {'account_id': [('id','=',self.capital_line.account_code_id.id),('branch_id','=',self.invoice_id.unit_id.id)]}}
        else:
            return {'domain': {'account_id': [('active', '=', True),('deprecated','=',False),('branch_id','=',self.invoice_id.unit_id.id)]}}

    @api.onchange('department_id')
    def onchange_department(self):
        if self.budget_type != 'project':
            self.division_id = False
            budget_ids = self.env['kw_revenue_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.invoice_id.date),('fiscal_year_id.date_stop','>=',self.invoice_id.date)]).mapped('budget_division')
            capital_ids = self.env['kw_capital_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.invoice_id.date),('fiscal_year_id.date_stop','>=',self.invoice_id.date)]).mapped('budget_division')
            if budget_ids and  self.budget_type == 'treasury':
                return {'domain': {'division_id': [('id','in',budget_ids.ids),('parent_id', '=', self.department_id.id), ('dept_type.code', '=', 'division')]}}
            elif capital_ids and  self.budget_type == 'capital':
                return {'domain': {'division_id': [('id','in',budget_ids.ids),('parent_id', '=', self.department_id.id), ('dept_type.code', '=', 'division')]}}
            else:
                return {'domain': {'division_id': [('parent_id', '=', self.department_id.id), ('dept_type.code', '=', 'division')]}}

    @api.onchange('division_id')
    def onchange_division(self):
        if self.budget_type != 'project': 
            self.section_id = False
            budget_ids = self.env['kw_revenue_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.invoice_id.date),('fiscal_year_id.date_stop','>=',self.invoice_id.date)]).mapped('budget_section')
            capital_ids = self.env['kw_capital_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.invoice_id.date),('fiscal_year_id.date_stop','>=',self.invoice_id.date)]).mapped('budget_section')
            
            if budget_ids and self.budget_type == 'treasury':
                return {'domain': {'section_id': [('id','in',budget_ids.ids),('parent_id', '=', self.division_id.id), ('dept_type.code', '=', 'section')]}}
            elif capital_ids and self.budget_type == 'capital':
                return {'domain': {'section_id': [('id','in',budget_ids.ids),('parent_id', '=', self.division_id.id), ('dept_type.code', '=', 'section')]}}
            else:
                return {'domain': {'section_id': [('parent_id', '=', self.division_id.id), ('dept_type.code', '=', 'section')]}}
    
    @api.onchange('budget_type','project_wo_id','department_id','division_id','section_id')
    def get_budget_line(self):
        self.budget_line,self.capital_line,self.project_line = False,False,False
        if self.budget_type == 'treasury':
            if self.department_id and not self.division_id and not self.section_id:
                return {'domain': {'budget_line': [('revenue_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('revenue_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('revenue_budget_id.budget_dept','=',self.department_id.id)]}}
            if self.department_id and self.division_id and not self.section_id:
                return {'domain': {'budget_line': [('revenue_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('revenue_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('revenue_budget_id.budget_dept','=',self.department_id.id),('revenue_budget_id.budget_division','=',self.division_id.id)]}}
            if self.department_id and self.division_id and self.section_id:
                return {'domain': {'budget_line': [('revenue_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('revenue_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('revenue_budget_id.budget_dept','=',self.department_id.id),('revenue_budget_id.budget_division','=',self.division_id.id),('revenue_budget_id.budget_section','=',self.section_id.id)]}}
        elif self.budget_type == 'capital':
            if self.department_id and not self.division_id and not self.section_id:
                return {'domain': {'capital_line': [('capital_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('capital_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('capital_budget_id.budget_dept','=',self.department_id.id)]}}
            if self.department_id and self.division_id and not self.section_id:
                return {'domain': {'capital_line': [('capital_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('capital_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('capital_budget_id.budget_dept','=',self.department_id.id),('capital_budget_id.budget_division','=',self.division_id.id)]}}
            if self.department_id and self.division_id and self.section_id:
                return {'domain': {'capital_line': [('capital_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('capital_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('capital_budget_id.budget_dept','=',self.department_id.id),('capital_budget_id.budget_division','=',self.division_id.id),('capital_budget_id.budget_section','=',self.section_id.id)]}}
        elif self.budget_type == 'project':
            if self.project_wo_id:
                return {'domain': {'project_line': [('sbu_project_budget_id.fiscal_year_id.date_start','<=',self.invoice_id.date),('sbu_project_budget_id.fiscal_year_id.date_stop','>=',self.invoice_id.date),('project_id','=',self.project_wo_id.id)]}}
        
        
    @api.onchange('account_id','project_wo_id','transaction_amount')
    def _check_budget_amount(self):
        project_budget_id = self.env['kw_project_budget_master_data'].sudo().search([('kw_wo_id','=',self.project_wo_id.kw_wo_id)],limit=1)
        if project_budget_id and self.invoice_id.type not in ['out_invoice','out_refund']:
            project_budget_line_id = self.env['kw_project_budget_line_items'].sudo().search([('project_crm_id','=',project_budget_id.id),('user_type_id','=',self.account_id.group_type.id),('group_head_id','=',self.account_id.user_type_id.id),('group_name','=',self.account_id.group_name.id),('account_head_id','=',self.account_id.account_head_id.id),('account_sub_head_id','=',self.account_id.account_sub_head_id.id)],limit=1)
            if ((project_budget_line_id.budget_amount - project_budget_line_id.actual_amount - project_budget_line_id.old_fy_balance) < self.transaction_amount):
                raise ValidationError("Budget amount exceeded of the respective account sub-head.")
        else:
            pass
        
class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    project_wo_id = fields.Many2one('kw_project_budget_master_data',string="Project")
    budget_line = fields.Many2one('kw_revenue_budget_line',string='Treasury Budget Line',)
    capital_line = fields.Many2one('kw_capital_budget_line',string='Capital Budget Line',)
    project_line = fields.Many2one('kw_sbu_project_budget_line',string='Project Budget Line',)


    @api.onchange('account_id','project_wo_id','debit','credit')
    def _check_budget_amount(self):
        project_budget_id = self.env['kw_project_budget_master_data'].sudo().search([('kw_wo_id','=',self.project_wo_id.kw_wo_id)],limit=1)
        if self.budget_type == 'project' and project_budget_id:
            project_budget_line_id = self.env['kw_project_budget_line_items'].sudo().search([('project_crm_id','=',project_budget_id.id),('user_type_id','=',self.account_id.group_type.id),('group_head_id','=',self.account_id.user_type_id.id),('group_name','=',self.account_id.group_name.id),('account_head_id','=',self.account_id.account_head_id.id),('account_sub_head_id','=',self.account_id.account_sub_head_id.id)],limit=1)
            if self.debit > 0 and ((project_budget_line_id.budget_amount - project_budget_line_id.actual_amount - project_budget_line_id.old_fy_balance) < self.debit):
                raise ValidationError("Budget amount exceeded of the respective account sub-head.")
        else:
            pass
    
    @api.onchange('budget_type','project_wo_id')
    def onchange_project_id(self):
        self.account_id,self.department_id,self.division_id,self.section_id = False, False, False,False
        project_budget_id = self.env['kw_project_budget_master_data'].sudo().search([('kw_wo_id','=',self.project_wo_id.kw_wo_id)],limit=1)
        budget_ids = self.env['kw_revenue_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.move_id.date),('fiscal_year_id.date_stop','>=',self.move_id.date)]).mapped('budget_dept')
        capital_ids = self.env['kw_capital_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.move_id.date),('fiscal_year_id.date_stop','>=',self.move_id.date)]).mapped('budget_dept')
        
        if self.budget_type == 'project' and project_budget_id:
            self.department_id = self.project_wo_id.sbu_id.representative_id.department_id.id 
            self.division_id = self.project_wo_id.sbu_id.representative_id.division.id
            self.section_id = self.project_wo_id.sbu_id.representative_id.section.id
            if project_budget_id:
                project_budget_line_ids = self.env['kw_project_budget_line_items'].sudo().search([('project_crm_id','=',project_budget_id.id)])
                account_model = self.env['account.account']
                for line in project_budget_line_ids:
                    account_ids = account_model.sudo().search([('group_type','=',line.user_type_id.id),('user_type_id','=',line.group_head_id.id),('group_name','=',line.group_name.id),('account_head_id','=',line.account_head_id.id),('account_sub_head_id','=',line.account_sub_head_id.id)])
                    account_model += account_ids
                return {'domain': {'account_id': [('active', '=', True),('deprecated','=',False),('id', 'in', account_model.ids),('branch_id','=',self.move_id.branch_id.id)]}}
            else:
                return {'domain': {'account_id': [('active', '=', True),('deprecated','=',False),('branch_id','=',self.move_id.branch_id.id)]}}

        elif self.budget_type == 'treasury':
            self.project_wo_id = False
            if budget_ids:
                return {'domain': {'department_id': [('id','in',budget_ids.ids)]}}
            else:
                return {'domain': {'department_id': [('dept_type.code','=','department')]}}
        elif self.budget_type == 'capital':
            self.project_wo_id = False
            if capital_ids:
                return {'domain': {'department_id': [('id','in',capital_ids.ids)]}}
            else:
                return {'domain': {'department_id': [('dept_type.code','=','department')]}}
        else:
            self.project_wo_id = False
            return {'domain': {'department_id': [('dept_type.code','=','department')],'account_id': [('active', '=', True),('deprecated','=',False),('branch_id','=',self.move_id.branch_id.id)]}}

    @api.onchange('budget_line','capital_line')
    def onchange_budget_line(self):
        self.account_id = False
        if self.budget_line:
            return {'domain': {'account_id': [('id','=',self.budget_line.account_code_id.id),('branch_id','=',self.move_id.branch_id.id)]}}
        elif self.capital_line:
            return {'domain': {'account_id': [('id','=',self.capital_line.account_code_id.id),('branch_id','=',self.move_id.branch_id.id)]}}
        else:
            return {'domain': {'account_id': [('active', '=', True),('deprecated','=',False),('branch_id','=',self.move_id.branch_id.id)]}}


    @api.onchange('department_id')
    def onchange_department(self):
        if self.budget_type != 'project':
            self.division_id = False
            budget_ids = self.env['kw_revenue_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.move_id.date),('fiscal_year_id.date_stop','>=',self.move_id.date)]).mapped('budget_division')
            capital_ids = self.env['kw_capital_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.move_id.date),('fiscal_year_id.date_stop','>=',self.move_id.date)]).mapped('budget_division')
            if budget_ids and self.budget_type == 'treasury':
                return {'domain': {'division_id': [('id','in',budget_ids.ids),('parent_id', '=', self.department_id.id), ('dept_type.code', '=', 'division')]}}
            elif capital_ids and self.budget_type == 'capital':
                return {'domain': {'division_id': [('id','in',budget_ids.ids),('parent_id', '=', self.department_id.id), ('dept_type.code', '=', 'division')]}}
            else:
                return {'domain': {'division_id': [('parent_id', '=', self.department_id.id), ('dept_type.code', '=', 'division')]}}

    @api.onchange('division_id')
    def onchange_division(self):
        if self.budget_type != 'project':
            self.section_id = False
            budget_ids = self.env['kw_revenue_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.move_id.date),('fiscal_year_id.date_stop','>=',self.move_id.date)]).mapped('budget_section')
            capital_ids = self.env['kw_capital_budget'].sudo().search([('state','=','validate'),('fiscal_year_id.date_start','<=',self.move_id.date),('fiscal_year_id.date_stop','>=',self.move_id.date)]).mapped('budget_section')
            
            if budget_ids and self.budget_type == 'treasury':
                return {'domain': {'section_id': [('id','in',budget_ids.ids),('parent_id', '=', self.division_id.id), ('dept_type.code', '=', 'section')]}}
            elif capital_ids and self.budget_type == 'capital':
                return {'domain': {'section_id': [('id','in',budget_ids.ids),('parent_id', '=', self.division_id.id), ('dept_type.code', '=', 'section')]}}
            else:
                return {'domain': {'section_id': [('parent_id', '=', self.division_id.id), ('dept_type.code', '=', 'section')]}}
    
    @api.onchange('budget_type','project_wo_id','department_id','division_id','section_id')
    def get_budget_line(self):
        self.budget_line,self.capital_line,self.project_line = False,False,False

        if self.budget_type == 'treasury':
            if self.department_id and not self.division_id and not self.section_id:
                return {'domain': {'budget_line': [('revenue_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('revenue_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('revenue_budget_id.budget_dept','=',self.department_id.id)]}}
            if self.department_id and self.division_id and not self.section_id:
                return {'domain': {'budget_line': [('revenue_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('revenue_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('revenue_budget_id.budget_dept','=',self.department_id.id),('revenue_budget_id.budget_division','=',self.division_id.id)]}}
            if self.department_id and self.division_id and self.section_id:
                return {'domain': {'budget_line': [('revenue_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('revenue_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('revenue_budget_id.budget_dept','=',self.department_id.id),('revenue_budget_id.budget_division','=',self.division_id.id),('revenue_budget_id.budget_section','=',self.section_id.id)]}}

        elif self.budget_type == 'capital':
            if self.department_id and not self.division_id and not self.section_id:
                return {'domain': {'capital_line': [('capital_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('capital_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('capital_budget_id.budget_dept','=',self.department_id.id)]}}
            if self.department_id and self.division_id and not self.section_id:
                return {'domain': {'capital_line': [('capital_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('capital_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('capital_budget_id.budget_dept','=',self.department_id.id),('capital_budget_id.budget_division','=',self.division_id.id)]}}
            if self.department_id and self.division_id and self.section_id:
                return {'domain': {'capital_line': [('capital_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('capital_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('capital_budget_id.budget_dept','=',self.department_id.id),('capital_budget_id.budget_division','=',self.division_id.id),('capital_budget_id.budget_section','=',self.section_id.id)]}}
        
        elif self.budget_type == 'project':
            if self.project_wo_id:
                return {'domain': {'project_line': [('sbu_project_budget_id.fiscal_year_id.date_start','<=',self.move_id.date),('sbu_project_budget_id.fiscal_year_id.date_stop','>=',self.move_id.date),('project_id','=',self.project_wo_id.id)]}}