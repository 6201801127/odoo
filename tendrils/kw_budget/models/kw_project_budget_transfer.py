from odoo import models, fields, api

class TransferProjectBudget(models.Model):
    _name = 'transfer_project_budget_amounts'
    _description = "Transfer Project Budget Amount"

    head_of_expense = fields.Char('Particular')
    account_code_id = fields.Many2one('account.account', 'Account code')
    work_order_type = fields.Selection([
        ('work_order', 'Work Order'),
        ('opportunity', 'Opportunity'),
    ], default='work_order', string='Order Type', track_visibility='always')
    opportunity_name = fields.Char(string='Opportunity Name')
    order_code = fields.Char('Order Code')
    budget_department=fields.Many2one('kw_sbu_project_mapping', string="SBU ID")
    budget_department_name=fields.Char(related='budget_department.sbu_id.name', string="SBU Name")
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    sbu_name = fields.Char(string="SBU Name")
    project_code = fields.Char('Work Order Code')
    client = fields.Char(string='Client Name')
    # order_id = fields.Many2one('project.project', 'Order Name')
    project_id = fields.Many2one('kw_project_budget_master_data', 'Project Name')
    order_value = fields.Char(string='Order Value')
    category_id = fields.Many2one('kw_sbu_project_category_master', string='Category', required=True)
    total_original_budget = fields.Float(string='Total')
    apr_budget_org = fields.Float('Apr Original')
    apr_budget_rev = fields.Float('Apr Reallocation')
    may_budget_org = fields.Float('May Original')
    may_budget_rev = fields.Float('May Reallocation')
    jun_budget_org = fields.Float('Jun Original')
    jun_budget_rev = fields.Float('Jun Reallocation')
    jul_budget_org = fields.Float('Jul Original')
    jul_budget_rev = fields.Float('Jul Reallocation')
    aug_budget_org = fields.Float('Aug Original')
    aug_budget_rev = fields.Float('Aug Reallocation')
    sep_budget_org = fields.Float('Sep Original')
    sep_budget_rev = fields.Float('Sep Reallocation')
    oct_budget_org = fields.Float('Oct Original')
    oct_budget_rev = fields.Float('Oct Reallocation')
    nov_budget_org = fields.Float('Nov Original')
    nov_budget_rev = fields.Float('Nov Reallocation')
    dec_budget_org = fields.Float('Dec Original')
    dec_budget_rev = fields.Float('Dec Reallocation')
    jan_budget_org = fields.Float('Jan Original')
    jan_budget_rev = fields.Float('Jan Reallocation')
    feb_budget_org = fields.Float('Feb Original')
    feb_budget_rev = fields.Float('Feb Reallocation')
    mar_budget_org = fields.Float('Mar Original')
    mar_budget_rev = fields.Float('Mar Reallocation')
    sbu_project_budget_id = fields.Many2one('kw_sbu_project_budget', 'SBU Project Budget')
    work_order_type =  fields.Char(string='Workorder Type')
    project_name_id = fields.Many2one('kw_project_budget_master_data', string="Project Name")
    ref_id= fields.Many2one('kw_sbu_project_budget_line', string='Project Budget Line')

    # sbu_id = fields.Many2one('kw_sbu_master', string="SBU Name")
    sequence_ref = fields.Char( string='ID')
    has_revised_amounts = fields.Boolean('Has Revised Amounts', compute='_compute_has_revised_amounts', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ], 'Status', default='draft', required=True, readonly=True, copy=False, track_visibility='always')
    
    remarks = fields.Char("Remark")


    # @api.depends('may_budget_org', 'jun_budget_org', 'jul_budget_org', 'aug_budget_org',
    #              'sep_budget_org', 'oct_budget_org', 'nov_budget_org', 'dec_budget_org',
    #              'jan_budget_org', 'feb_budget_org', 'mar_budget_org')
    # def _compute_total_original_budget(self):
    #     for record in self:
    #         total = (
    #             record.may_budget_org + record.jun_budget_org + record.jul_budget_org +
    #             record.aug_budget_org + record.sep_budget_org + record.oct_budget_org +
    #             record.nov_budget_org + record.dec_budget_org + record.jan_budget_org +
    #             record.feb_budget_org + record.mar_budget_org
    #         )
    #         record.total_original_budget = total


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('report_action_project_budget_transfer'):
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group(
                    'kw_budget.group_approver_kw_budget') or self.env.user.has_group(
                    'kw_budget.group_manager_kw_budget'):
                args += []
                return super(TransferProjectBudget, self)._search(args, offset, limit, order, count, access_rights_uid)
            data = self.env['kw_sbu_project_mapping'].sudo().search([
                ('level_1_approver.user_id', '=', self.env.user.id)
            ])
            if data:
                args += [('budget_department', 'in', data.ids)]
            return super(TransferProjectBudget, self)._search(args, offset, limit, order, count, access_rights_uid)
        if not self._context.get('report_action_project_budget_transfer'):
            data = self.env['kw_sbu_project_mapping'].sudo().search([
                ('level_2_approver.user_id', '=', self.env.user.id)
            ])
            if self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                args += []
            elif data:
                args += [('budget_department', 'in', data.ids)]
            return super(TransferProjectBudget, self)._search(args, offset, limit, order, count, access_rights_uid)

    @api.depends('apr_budget_rev', 'may_budget_rev', 'jun_budget_rev', 'jul_budget_rev',
                 'aug_budget_rev', 'sep_budget_rev', 'oct_budget_rev', 'nov_budget_rev',
                 'dec_budget_rev', 'jan_budget_rev', 'feb_budget_rev', 'mar_budget_rev')
    def _compute_has_revised_amounts(self):
        for record in self:
            revised_fields = [
                'apr_budget_rev', 'may_budget_rev', 'jun_budget_rev', 'jul_budget_rev',
                'aug_budget_rev', 'sep_budget_rev', 'oct_budget_rev', 'nov_budget_rev',
                'dec_budget_rev', 'jan_budget_rev', 'feb_budget_rev', 'mar_budget_rev'
            ]
            record.has_revised_amounts = any(getattr(record, field) for field in revised_fields)

    @api.model
    def transfer_project_budget_amounts(self):
        # self.search([]).unlink()
        budget_lines = self.env['kw_sbu_project_budget_line'].search([('state', '=', 'validate')])
        for line in budget_lines:
            # Check if a record already exists with the same criteria
            budget_department = line.sbu_project_budget_id.budget_department
            fiscal_year_id = line.sbu_project_budget_id.fiscal_year_id
            existing_record = self.env['transfer_project_budget_amounts'].sudo().search([
                # ('head_of_expense', '=', line.head_of_expense),
                # ('category_id', '=', line.category_id.id),
                # ('sbu_project_budget_id', '=', line.sbu_project_budget_id.id),
                # ('order_id', '=', line.order_id.id),
                # ('project_id', '=', line.project_id.id),
                # ('opportunity_name', '=', line.opportunity_name),
                ('ref_id','=',line.id)
            ], limit=1)

            if existing_record:
                existing_record.write({
                    'head_of_expense': line.head_of_expense,
                    'account_code_id': line.account_code_id.id,
                    'work_order_type': line.work_order_type,
                    'opportunity_name': line.opportunity_name,
                    'order_code': line.order_code,
                    'project_code': line.project_code,
                    'client': line.client,
                    'project_id': line.project_id.id,
                    'order_value': line.order_value,
                    'category_id': line.category_id.id,
                    'apr_budget_org': line.apr_budget,
                    'may_budget_org': line.may_budget,
                    'jun_budget_org': line.jun_budget,
                    'jul_budget_org': line.jul_budget,
                    'aug_budget_org': line.aug_budget,
                    'sep_budget_org': line.sep_budget,
                    'oct_budget_org': line.oct_budget,
                    'nov_budget_org': line.nov_budget,
                    'dec_budget_org': line.dec_budget,
                    'jan_budget_org': line.jan_budget,
                    'feb_budget_org': line.feb_budget,
                    'mar_budget_org': line.mar_budget,
                    'sbu_project_budget_id': line.sbu_project_budget_id.id,
                    'budget_department': budget_department.id,
                    'fiscal_year_id': fiscal_year_id.id,
                    'sequence_ref': line.sequence_ref,
                    'ref_id':line.id,
                    'total_original_budget':line.total_amount
                })
            
            else:
                new_re = self.env['transfer_project_budget_amounts'].sudo().create({
                    'head_of_expense': line.head_of_expense,
                    'account_code_id': line.account_code_id.id,
                    'work_order_type': line.work_order_type,
                    'opportunity_name': line.opportunity_name,
                    'order_code': line.order_code,
                    'project_code': line.project_code,
                    'client': line.client,
                    'project_id': line.project_id.id,
                    'order_value': line.order_value,
                    'category_id': line.category_id.id,
                    'apr_budget_org': line.apr_budget,
                    'may_budget_org': line.may_budget,
                    'jun_budget_org': line.jun_budget,
                    'jul_budget_org': line.jul_budget,
                    'aug_budget_org': line.aug_budget,
                    'sep_budget_org': line.sep_budget,
                    'oct_budget_org': line.oct_budget,
                    'nov_budget_org': line.nov_budget,
                    'dec_budget_org': line.dec_budget,
                    'jan_budget_org': line.jan_budget,
                    'feb_budget_org': line.feb_budget,
                    'mar_budget_org': line.mar_budget,
                    'sbu_project_budget_id': line.sbu_project_budget_id.id,
                    'budget_department': budget_department.id,
                    'fiscal_year_id': fiscal_year_id.id,
                    'sequence_ref': line.sequence_ref,
                    'ref_id':line.id,
                    'total_original_budget':line.total_amount
                })
              

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(TransferProjectBudget, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self.env.context.get('call_transfer_project_budget_amounts'):
            self.transfer_project_budget_amounts()
        return res
    
    def action_open_approve_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'res_model': 'approve_revision_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_record_id': self.id},
        }
