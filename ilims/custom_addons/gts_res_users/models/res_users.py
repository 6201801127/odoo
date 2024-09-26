from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        record = super(ResUsers, self).create(vals_list)
        if record:
            timesheet_admin_group = self.env.ref('hr_timesheet.group_timesheet_manager')
            sale_admin_group = self.env.ref('sales_team.group_sale_manager')
            sale_all_document_group = self.env.ref('sales_team.group_sale_salesman_all_leads')
            sale_own_document_group = self.env.ref('sales_team.group_sale_salesman')
            accounting_admin_group = self.env.ref('account.group_account_manager')
            accounting_user_group = self.env.ref('account.group_account_user')
            accounting_billing_group = self.env.ref('account.group_account_invoice')
            accounting_auditor_group = self.env.ref('account.group_account_readonly')
            inventory_admin_group = self.env.ref('stock.group_stock_manager')
            inventory_user_group = self.env.ref('stock.group_stock_user')
            purchase_admin_group = self.env.ref('purchase.group_purchase_manager')
            purchase_user_group = self.env.ref('purchase.group_purchase_user')
            hr_admin_group = self.env.ref('hr.group_hr_manager')
            hr_officer_group = self.env.ref('hr.group_hr_user')
            hr_holidays_admin_group = self.env.ref('hr_holidays.group_hr_holidays_manager')
            hr_holidays_approver_group = self.env.ref('hr_holidays.group_hr_holidays_user')
            hr_holidays_responsible_group = self.env.ref('hr_holidays.group_hr_holidays_responsible')
            website_designer_group = self.env.ref('website.group_website_designer')
            website_editor_group = self.env.ref('website.group_website_publisher')
            admin_settings_group = self.env.ref('base.group_system')
            admin_access_rights_group = self.env.ref('base.group_erp_manager')
            acceptance_manager_group = self.env.ref('gts_acceptance_management.group_acceptance_manager')
            acceptance_user_group = self.env.ref('gts_acceptance_management.group_acceptance_user')
            risk_manager_group = self.env.ref('project_risk_management_app.group_risk_manager')
            risk_user_group = self.env.ref('project_risk_management_app.group_risk_user')
            quality_manager_group = self.env.ref('quality_control_oca.group_quality_control_manager')
            quality_user_group = self.env.ref('quality_control_oca.group_quality_control_user')
            ticket_manager_group = self.env.ref('gts_ticket_management.group_support_ticket_manager')
            ticket_user_group = self.env.ref('gts_ticket_management.group_support_ticket_user')
            project_costing_group = self.env.ref('gts_groups.group_project_costing_can_view')
            analytic_tags_group = self.env.ref('analytic.group_analytic_tags')
            tender_representative_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_user')
            bid_manager_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_manager')
            financial_committee_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_financial_committee')
            technical_committee_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_technical_committee')
            cr_approval_group = self.env.ref('gts_change_request.group_cr_approval_access')
            cr_close_approval_group = self.env.ref('gts_change_request.group_cr_close_approval_access')
            cr_manager_group = self.env.ref('gts_change_request.group_change_management_can_create')
            cr_user_group = self.env.ref('gts_change_request.group_change_management_can_view')
            contract_approve_group = self.env.ref('contract.group_contract_approver')
            contract_close_approve_group = self.env.ref('contract.group_contract_close_approval_access')
            contract_creator_group = self.env.ref('contract.group_contract_creator')
            contract_view_group = self.env.ref('contract.group_contract_view')
            task_iss_inc_create_group = self.env.ref('gts_groups.group_project_task_management_can_create')
            task_iss_inc_view_group = self.env.ref('gts_groups.group_project_task_management_can_view')
            quality_approve_group = self.env.ref('gts_groups.group_quality_management_can_approve')
            quality_view_group = self.env.ref('gts_groups.group_quality_management_can_view')
            quality_create_group = self.env.ref('gts_groups.group_quality_management_can_create')
            quality_auditor_group = self.env.ref('gts_groups.group_quality_control_auditor')
            acceptance_approve_group = self.env.ref('gts_groups.group_acceptance_management_can_approve')
            acceptance_create_group = self.env.ref('gts_groups.group_acceptance_management_can_create')
            acceptance_view_group = self.env.ref('gts_groups.group_acceptance_management_can_view')
            budget_create_group = self.env.ref('gts_groups.group_budget_management_can_create')
            budget_view_group = self.env.ref('gts_groups.group_budget_management_can_view')
            ticket_create_group = self.env.ref('gts_groups.group_helpdesk_management_can_create')
            ticket_view_group = self.env.ref('gts_groups.group_helpdesk_management_can_view')
            if record.has_group('project.group_project_manager'):
                timesheet_admin_group.write({'users': [(4, record.id)]})
                sale_admin_group.write({'users': [(4, record.id)]})
                accounting_admin_group.write({'users': [(4, record.id)]})
                inventory_admin_group.write({'users': [(4, record.id)]})
                if record.has_group('purchase.group_purchase_manager'):
                    purchase_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('purchase.group_purchase_user'):
                    purchase_user_group.write({'users': [(3, record.id)]})
                hr_admin_group.write({'users': [(4, record.id)]})
                hr_holidays_admin_group.write({'users': [(4, record.id)]})
                if record.has_group('website.group_website_designer'):
                    website_designer_group.write({'users': [(3, record.id)]})
                if record.has_group('website.group_website_publisher'):
                    website_editor_group.write({'users': [(3, record.id)]})
                admin_settings_group.write({'users': [(4, record.id)]})
                acceptance_manager_group.write({'users': [(4, record.id)]})
                risk_manager_group.write({'users': [(4, record.id)]})
                quality_manager_group.write({'users': [(4, record.id)]})
                ticket_manager_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_project_costing_can_view'):
                    project_costing_group.write({'users': [(3, record.id)]})
                analytic_tags_group.write({'users': [(4, record.id)]})
                tender_representative_group.write({'users': [(4, record.id)]})
                bid_manager_group.write({'users': [(4, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_financial_committee'):
                    financial_committee_group.write({'users': [(3, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_technical_committee'):
                    technical_committee_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_cr_approval_access'):
                    cr_approval_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_cr_close_approval_access'):
                    cr_close_approval_group.write({'users': [(3, record.id)]})
                cr_manager_group.write({'users': [(4, record.id)]})
                cr_user_group.write({'users': [(4, record.id)]})
                if record.has_group('contract.group_contract_approver'):
                    contract_approve_group.write({'users': [(3, record.id)]})
                contract_close_approve_group.write({'users': [(4, record.id)]})
                contract_creator_group.write({'users': [(4, record.id)]})
                contract_view_group.write({'users': [(4, record.id)]})
                task_iss_inc_create_group.write({'users': [(4, record.id)]})
                task_iss_inc_view_group.write({'users': [(4, record.id)]})
                quality_approve_group.write({'users': [(4, record.id)]})
                quality_view_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_quality_management_can_create'):
                    quality_create_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_groups.group_quality_control_auditor'):
                    quality_auditor_group.write({'users': [(3, record.id)]})
                acceptance_approve_group.write({'users': [(4, record.id)]})
                acceptance_create_group.write({'users': [(4, record.id)]})
                acceptance_view_group.write({'users': [(4, record.id)]})
                budget_create_group.write({'users': [(4, record.id)]})
                budget_view_group.write({'users': [(4, record.id)]})
                ticket_create_group.write({'users': [(4, record.id)]})
                ticket_view_group.write({'users': [(4, record.id)]})
            elif record.has_group('gts_project_stages.group_project_manager_new'):
                timesheet_admin_group.write({'users': [(4, record.id)]})
                if record.has_group('sales_team.group_sale_manager'):
                    sale_admin_group.write({'users': [(3, record.id)]})
                sale_all_document_group.write({'users': [(4, record.id)]})
                if record.has_group('account.group_account_manager'):
                    accounting_admin_group.write({'users': [(3, record.id)]})
                accounting_user_group.write({'users': [(4, record.id)]})
                inventory_admin_group.write({'users': [(4, record.id)]})
                purchase_admin_group.write({'users': [(4, record.id)]})
                if record.has_group('hr.group_hr_manager'):
                    hr_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('hr.group_hr_user'):
                    hr_officer_group.write({'users': [(3, record.id)]})
                if record.has_group('hr_holidays.group_hr_holidays_manager'):
                    hr_holidays_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('hr_holidays.group_hr_holidays_user'):
                    hr_holidays_approver_group.write({'users': [(3, record.id)]})
                if record.has_group('hr_holidays.group_hr_holidays_responsible'):
                    hr_holidays_responsible_group.write({'users': [(3, record.id)]})
                if record.has_group('website.group_website_designer'):
                    website_designer_group.write({'users': [(3, record.id)]})
                if record.has_group('website.group_website_publisher'):
                    website_editor_group.write({'users': [(3, record.id)]})
                if record.has_group('base.group_system'):
                    admin_settings_group.write({'users': [(3, record.id)]})
                if record.has_group('base.group_erp_manager'):
                    admin_access_rights_group.write({'users': [(3, record.id)]})
                acceptance_manager_group.write({'users': [(4, record.id)]})
                risk_manager_group.write({'users': [(4, record.id)]})
                quality_manager_group.write({'users': [(4, record.id)]})
                ticket_manager_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_project_costing_can_view'):
                    project_costing_group.write({'users': [(3, record.id)]})
                analytic_tags_group.write({'users': [(4, record.id)]})
                tender_representative_group.write({'users': [(4, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_manager'):
                    bid_manager_group.write({'users': [(3, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_financial_committee'):
                    financial_committee_group.write({'users': [(3, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_technical_committee'):
                    technical_committee_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_cr_approval_access'):
                    cr_approval_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_cr_close_approval_access'):
                    cr_close_approval_group.write({'users': [(3, record.id)]})
                cr_manager_group.write({'users': [(4, record.id)]})
                cr_user_group.write({'users': [(4, record.id)]})
                if record.has_group('contract.group_contract_approver'):
                    contract_approve_group.write({'users': [(3, record.id)]})
                if record.has_group('contract.group_contract_close_approval_access'):
                    contract_close_approve_group.write({'users': [(3, record.id)]})
                contract_creator_group.write({'users': [(4, record.id)]})
                contract_view_group.write({'users': [(4, record.id)]})
                task_iss_inc_create_group.write({'users': [(4, record.id)]})
                task_iss_inc_view_group.write({'users': [(4, record.id)]})
                quality_approve_group.write({'users': [(4, record.id)]})
                quality_view_group.write({'users': [(4, record.id)]})
                quality_create_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_quality_control_auditor'):
                    quality_auditor_group.write({'users': [(3, record.id)]})
                acceptance_approve_group.write({'users': [(4, record.id)]})
                acceptance_create_group.write({'users': [(4, record.id)]})
                acceptance_view_group.write({'users': [(4, record.id)]})
                budget_create_group.write({'users': [(4, record.id)]})
                budget_view_group.write({'users': [(4, record.id)]})
                ticket_create_group.write({'users': [(4, record.id)]})
                ticket_view_group.write({'users': [(4, record.id)]})
            elif record.has_group('project.group_project_user'):
                timesheet_admin_group.write({'users': [(4, record.id)]})
                if record.has_group('sales_team.group_sale_manager'):
                    sale_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('sales_team.group_sale_salesman_all_leads'):
                    sale_all_document_group.write({'users': [(3, record.id)]})
                sale_own_document_group.write({'users': [(4, record.id)]})
                if record.has_group('account.group_account_manager'):
                    accounting_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('account.group_account_user'):
                    accounting_user_group.write({'users': [(3, record.id)]})
                if record.has_group('account.group_account_invoice'):
                    accounting_billing_group.write({'users': [(3, record.id)]})
                if record.has_group('account.group_account_readonly'):
                    accounting_auditor_group.write({'users': [(3, record.id)]})
                if record.has_group('stock.group_stock_manager'):
                    inventory_admin_group.write({'users': [(3, record.id)]})
                inventory_user_group.write({'users': [(4, record.id)]})
                if record.has_group('purchase.group_purchase_manager'):
                    purchase_admin_group.write({'users': [(3, record.id)]})
                purchase_user_group.write({'users': [(4, record.id)]})
                if record.has_group('hr.group_hr_manager'):
                    hr_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('hr.group_hr_user'):
                    hr_officer_group.write({'users': [(3, record.id)]})
                if record.has_group('hr_holidays.group_hr_holidays_manager'):
                    hr_holidays_admin_group.write({'users': [(3, record.id)]})
                if record.has_group('hr_holidays.group_hr_holidays_user'):
                    hr_holidays_approver_group.write({'users': [(3, record.id)]})
                if record.has_group('hr_holidays.group_hr_holidays_responsible'):
                    hr_holidays_responsible_group.write({'users': [(3, record.id)]})
                if record.has_group('website.group_website_designer'):
                    website_designer_group.write({'users': [(3, record.id)]})
                if record.has_group('website.group_website_publisher'):
                    website_editor_group.write({'users': [(3, record.id)]})
                if record.has_group('base.group_system'):
                    admin_settings_group.write({'users': [(3, record.id)]})
                if record.has_group('base.group_erp_manager'):
                    admin_access_rights_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_acceptance_management.group_acceptance_manager'):
                    acceptance_manager_group.write({'users': [(3, record.id)]})
                acceptance_user_group.write({'users': [(4, record.id)]})
                if record.has_group('project_risk_management_app.group_risk_manager'):
                    risk_manager_group.write({'users': [(3, record.id)]})
                risk_user_group.write({'users': [(4, record.id)]})
                if record.has_group('quality_control_oca.group_quality_control_manager'):
                    quality_manager_group.write({'users': [(3, record.id)]})
                quality_user_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_ticket_management.group_support_ticket_manager'):
                    ticket_manager_group.write({'users': [(3, record.id)]})
                ticket_user_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_project_costing_can_view'):
                    project_costing_group.write({'users': [(3, record.id)]})
                analytic_tags_group.write({'users': [(4, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_user'):
                    tender_representative_group.write({'users': [(3, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_manager'):
                    bid_manager_group.write({'users': [(3, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_financial_committee'):
                    financial_committee_group.write({'users': [(3, record.id)]})
                if record.has_group('sh_po_tender_management.sh_purchase_tender_technical_committee'):
                    technical_committee_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_cr_approval_access'):
                    cr_approval_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_cr_close_approval_access'):
                    cr_close_approval_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_change_request.group_change_management_can_create'):
                    cr_manager_group.write({'users': [(3, record.id)]})
                cr_user_group.write({'users': [(4, record.id)]})
                if record.has_group('contract.group_contract_approver'):
                    contract_approve_group.write({'users': [(3, record.id)]})
                if record.has_group('contract.group_contract_close_approval_access'):
                    contract_close_approve_group.write({'users': [(3, record.id)]})
                if record.has_group('contract.group_contract_creator'):
                    contract_creator_group.write({'users': [(3, record.id)]})
                if record.has_group('contract.group_contract_view'):
                    contract_view_group.write({'users': [(3, record.id)]})
                task_iss_inc_create_group.write({'users': [(4, record.id)]})
                task_iss_inc_view_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_quality_management_can_approve'):
                    quality_approve_group.write({'users': [(3, record.id)]})
                quality_view_group.write({'users': [(4, record.id)]})
                quality_create_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_quality_control_auditor'):
                    quality_auditor_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_groups.group_acceptance_management_can_approve'):
                    acceptance_approve_group.write({'users': [(3, record.id)]})
                acceptance_create_group.write({'users': [(4, record.id)]})
                acceptance_view_group.write({'users': [(4, record.id)]})
                if record.has_group('gts_groups.group_budget_management_can_create'):
                    budget_create_group.write({'users': [(3, record.id)]})
                if record.has_group('gts_groups.group_budget_management_can_view'):
                    budget_view_group.write({'users': [(3, record.id)]})
                ticket_create_group.write({'users': [(4, record.id)]})
                ticket_view_group.write({'users': [(4, record.id)]})
            if record.has_group('account.group_account_manager') and not record.has_group('project.group_project_manager'):
                raise ValidationError(_('Cannot give access of Chief Accountant if he has access to Project Office'))
        return record

    def write(self, vals):
        rec = super(ResUsers, self).write(vals)
        for record in self:
            if record.has_group('account.group_account_manager') and not record.has_group('project.group_project_manager'):
                raise ValidationError(_(
                    'Cannot give access of Chief Accountant if he has access to Project Office'))
        return rec

    # def write(self, values):
    #     users = super(ResUsers, self).write(values)
        # timesheet_admin_group = self.env.ref('hr_timesheet.group_timesheet_manager')
        # sale_admin_group = self.env.ref('sales_team.group_sale_manager')
        # sale_all_document_group = self.env.ref('sales_team.group_sale_salesman_all_leads')
        # sale_own_document_group = self.env.ref('sales_team.group_sale_salesman')
        # accounting_admin_group = self.env.ref('account.group_account_manager')
        # accounting_user_group = self.env.ref('account.group_account_user')
        # accounting_billing_group = self.env.ref('account.group_account_invoice')
        # accounting_auditor_group = self.env.ref('account.group_account_readonly')
        # inventory_admin_group = self.env.ref('stock.group_stock_manager')
        # inventory_user_group = self.env.ref('stock.group_stock_user')
        # purchase_admin_group = self.env.ref('purchase.group_purchase_manager')
        # purchase_user_group = self.env.ref('purchase.group_purchase_user')
        # hr_admin_group = self.env.ref('hr.group_hr_manager')
        # hr_officer_group = self.env.ref('hr.group_hr_user')
        # hr_holidays_admin_group = self.env.ref('hr_holidays.group_hr_holidays_manager')
        # hr_holidays_approver_group = self.env.ref('hr_holidays.group_hr_holidays_user')
        # hr_holidays_responsible_group = self.env.ref('hr_holidays.group_hr_holidays_responsible')
        # website_designer_group = self.env.ref('website.group_website_designer')
        # website_editor_group = self.env.ref('website.group_website_publisher')
        # admin_settings_group = self.env.ref('base.group_system')
        # admin_access_rights_group = self.env.ref('base.group_erp_manager')
        # acceptance_manager_group = self.env.ref('gts_acceptance_management.group_acceptance_manager')
        # acceptance_user_group = self.env.ref('gts_acceptance_management.group_acceptance_user')
        # risk_manager_group = self.env.ref('project_risk_management_app.group_risk_manager')
        # risk_user_group = self.env.ref('project_risk_management_app.group_risk_user')
        # quality_manager_group = self.env.ref('quality_control_oca.group_quality_control_manager')
        # quality_user_group = self.env.ref('quality_control_oca.group_quality_control_user')
        # ticket_manager_group = self.env.ref('gts_ticket_management.group_support_ticket_manager')
        # ticket_user_group = self.env.ref('gts_ticket_management.group_support_ticket_user')
        # project_costing_group = self.env.ref('gts_groups.group_project_costing_can_view')
        # analytic_tags_group = self.env.ref('analytic.group_analytic_tags')
        # tender_representative_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_user')
        # bid_manager_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_manager')
        # financial_committee_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_financial_committee')
        # technical_committee_group = self.env.ref('sh_po_tender_management.sh_purchase_tender_technical_committee')
        # cr_approval_group = self.env.ref('gts_change_request.group_cr_approval_access')
        # cr_close_approval_group = self.env.ref('gts_change_request.group_cr_close_approval_access')
        # cr_manager_group = self.env.ref('gts_change_request.group_change_management_can_create')
        # cr_user_group = self.env.ref('gts_change_request.group_change_management_can_view')
        # contract_approve_group = self.env.ref('contract.group_contract_approver')
        # contract_close_approve_group = self.env.ref('contract.group_contract_close_approval_access')
        # contract_creator_group = self.env.ref('contract.group_contract_creator')
        # contract_view_group = self.env.ref('contract.group_contract_view')
        # task_iss_inc_create_group = self.env.ref('gts_groups.group_project_task_management_can_create')
        # task_iss_inc_view_group = self.env.ref('gts_groups.group_project_task_management_can_view')
        # quality_approve_group = self.env.ref('gts_groups.group_quality_management_can_approve')
        # quality_view_group = self.env.ref('gts_groups.group_quality_management_can_view')
        # quality_create_group = self.env.ref('gts_groups.group_quality_management_can_create')
        # quality_auditor_group = self.env.ref('gts_groups.group_quality_control_auditor')
        # acceptance_approve_group = self.env.ref('gts_groups.group_acceptance_management_can_approve')
        # acceptance_create_group = self.env.ref('gts_groups.group_acceptance_management_can_create')
        # acceptance_view_group = self.env.ref('gts_groups.group_acceptance_management_can_view')
        # budget_create_group = self.env.ref('gts_groups.group_budget_management_can_create')
        # budget_view_group = self.env.ref('gts_groups.group_budget_management_can_view')
        # ticket_create_group = self.env.ref('gts_groups.group_helpdesk_management_can_create')
        # ticket_view_group = self.env.ref('gts_groups.group_helpdesk_management_can_view')
        # for record in self:
        #     if record.has_group('project.group_project_manager'):
        #         timesheet_admin_group.write({'users': [(4, record.id)]})
        #         sale_admin_group.write({'users': [(4, record.id)]})
        #         accounting_admin_group.write({'users': [(4, record.id)]})
        #         inventory_admin_group.write({'users': [(4, record.id)]})
        #         hr_admin_group.write({'users': [(4, record.id)]})
        #         hr_holidays_admin_group.write({'users': [(4, record.id)]})
        #         admin_settings_group.write({'users': [(4, record.id)]})
        #         acceptance_manager_group.write({'users': [(4, record.id)]})
        #         risk_manager_group.write({'users': [(4, record.id)]})
        #         quality_manager_group.write({'users': [(4, record.id)]})
        #         ticket_manager_group.write({'users': [(4, record.id)]})
        #         analytic_tags_group.write({'users': [(4, record.id)]})
        #         tender_representative_group.write({'users': [(4, record.id)]})
        #         bid_manager_group.write({'users': [(4, record.id)]})
        #         cr_manager_group.write({'users': [(4, record.id)]})
        #         cr_user_group.write({'users': [(4, record.id)]})
        #         contract_approve_group.write({'users': [(4, record.id)]})
        #         contract_creator_group.write({'users': [(4, record.id)]})
        #         contract_view_group.write({'users': [(4, record.id)]})
        #         task_iss_inc_create_group.write({'users': [(4, record.id)]})
        #         task_iss_inc_view_group.write({'users': [(4, record.id)]})
        #         quality_approve_group.write({'users': [(4, record.id)]})
        #         quality_view_group.write({'users': [(4, record.id)]})
        #         acceptance_approve_group.write({'users': [(4, record.id)]})
        #         acceptance_create_group.write({'users': [(4, record.id)]})
        #         acceptance_view_group.write({'users': [(4, record.id)]})
        #         budget_create_group.write({'users': [(4, record.id)]})
        #         budget_view_group.write({'users': [(4, record.id)]})
        #         ticket_create_group.write({'users': [(4, record.id)]})
        #         ticket_view_group.write({'users': [(4, record.id)]})
        #         purchase_admin_group.write({'users': [(3, record.id)]})
        #         quality_create_group.write({'users': [(3, record.id)]})
        #     elif record.has_group('gts_project_stages.group_project_manager_new'):
        #         timesheet_admin_group.write({'users': [(4, record.id)]})
        #         if record.has_group('sales_team.group_sale_manager'):
        #             sale_admin_group.write({'users': [(3, record.id)]})
        #         sale_all_document_group.write({'users': [(4, record.id)]})
        #         if record.has_group('account.group_account_manager'):
        #             accounting_admin_group.write({'users': [(3, record.id)]})
        #         accounting_user_group.write({'users': [(4, record.id)]})
        #         inventory_admin_group.write({'users': [(4, record.id)]})
        #         purchase_admin_group.write({'users': [(4, record.id)]})
        #         if record.has_group('hr.group_hr_manager'):
        #             hr_admin_group.write({'users': [(2, record.id)]})
        #         if record.has_group('hr.group_hr_user'):
        #             hr_officer_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr_holidays.group_hr_holidays_manager'):
        #             hr_holidays_admin_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr_holidays.group_hr_holidays_user'):
        #             hr_holidays_approver_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr_holidays.group_hr_holidays_responsible'):
        #             hr_holidays_responsible_group.write({'users': [(3, record.id)]})
        #         if record.has_group('website.group_website_designer'):
        #             website_designer_group.write({'users': [(3, record.id)]})
        #         if record.has_group('website.group_website_publisher'):
        #             website_editor_group.write({'users': [(3, record.id)]})
        #         if record.has_group('base.group_system'):
        #             admin_settings_group.write({'users': [(3, record.id)]})
        #         if record.has_group('base.group_erp_manager'):
        #             admin_access_rights_group.write({'users': [(3, record.id)]})
        #         acceptance_manager_group.write({'users': [(4, record.id)]})
        #         risk_manager_group.write({'users': [(4, record.id)]})
        #         quality_manager_group.write({'users': [(4, record.id)]})
        #         ticket_manager_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_groups.group_project_costing_can_view'):
        #             project_costing_group.write({'users': [(3, record.id)]})
        #         analytic_tags_group.write({'users': [(4, record.id)]})
        #         tender_representative_group.write({'users': [(4, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_manager'):
        #             bid_manager_group.write({'users': [(3, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_financial_committee'):
        #             financial_committee_group.write({'users': [(3, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_technical_committee'):
        #             technical_committee_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_change_request.group_cr_approval_access'):
        #             cr_approval_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_change_request.group_cr_close_approval_access'):
        #             cr_close_approval_group.write({'users': [(3, record.id)]})
        #         cr_manager_group.write({'users': [(4, record.id)]})
        #         cr_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('contract.group_contract_approver'):
        #             contract_approve_group.write({'users': [(3, record.id)]})
        #         if record.has_group('contract.group_contract_close_approval_access'):
        #             contract_close_approve_group.write({'users': [(3, record.id)]})
        #         contract_creator_group.write({'users': [(4, record.id)]})
        #         contract_view_group.write({'users': [(4, record.id)]})
        #         task_iss_inc_create_group.write({'users': [(4, record.id)]})
        #         task_iss_inc_view_group.write({'users': [(4, record.id)]})
        #         quality_approve_group.write({'users': [(4, record.id)]})
        #         quality_view_group.write({'users': [(4, record.id)]})
        #         quality_create_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_groups.group_quality_control_auditor'):
        #             quality_auditor_group.write({'users': [(3, record.id)]})
        #         acceptance_approve_group.write({'users': [(4, record.id)]})
        #         acceptance_create_group.write({'users': [(4, record.id)]})
        #         acceptance_view_group.write({'users': [(4, record.id)]})
        #         budget_create_group.write({'users': [(4, record.id)]})
        #         budget_view_group.write({'users': [(4, record.id)]})
        #         ticket_create_group.write({'users': [(4, record.id)]})
        #         ticket_view_group.write({'users': [(4, record.id)]})
        #     elif record.has_group('project.group_project_user'):
        #         timesheet_admin_group.write({'users': [(4, record.id)]})
        #         if record.has_group('sales_team.group_sale_manager'):
        #             sale_admin_group.write({'users': [(3, record.id)]})
        #         if record.has_group('sales_team.group_sale_salesman_all_leads'):
        #             sale_all_document_group.write({'users': [(3, record.id)]})
        #         sale_own_document_group.write({'users': [(4, record.id)]})
        #         if record.has_group('account.group_account_manager'):
        #             accounting_admin_group.write({'users': [(3, record.id)]})
        #         if record.has_group('account.group_account_user'):
        #             accounting_user_group.write({'users': [(3, record.id)]})
        #         if record.has_group('account.group_account_invoice'):
        #             accounting_billing_group.write({'users': [(3, record.id)]})
        #         if record.has_group('account.group_account_readonly'):
        #             accounting_auditor_group.write({'users': [(3, record.id)]})
        #         if record.has_group('stock.group_stock_manager'):
        #             inventory_admin_group.write({'users': [(3, record.id)]})
        #         inventory_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('purchase.group_purchase_manager'):
        #             purchase_admin_group.write({'users': [(3, record.id)]})
        #         purchase_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('hr.group_hr_manager'):
        #             hr_admin_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr.group_hr_user'):
        #             hr_officer_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr_holidays.group_hr_holidays_manager'):
        #             hr_holidays_admin_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr_holidays.group_hr_holidays_user'):
        #             hr_holidays_approver_group.write({'users': [(3, record.id)]})
        #         if record.has_group('hr_holidays.group_hr_holidays_responsible'):
        #             hr_holidays_responsible_group.write({'users': [(3, record.id)]})
        #         if record.has_group('website.group_website_designer'):
        #             website_designer_group.write({'users': [(3, record.id)]})
        #         if record.has_group('website.group_website_publisher'):
        #             website_editor_group.write({'users': [(3, record.id)]})
        #         if record.has_group('base.group_system'):
        #             admin_settings_group.write({'users': [(3, record.id)]})
        #         if record.has_group('base.group_erp_manager'):
        #             admin_access_rights_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_acceptance_management.group_acceptance_manager'):
        #             acceptance_manager_group.write({'users': [(3, record.id)]})
        #         acceptance_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('project_risk_management_app.group_risk_manager'):
        #             risk_manager_group.write({'users': [(3, record.id)]})
        #         risk_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('quality_control_oca.group_quality_control_manager'):
        #             quality_manager_group.write({'users': [(3, record.id)]})
        #         quality_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_ticket_management.group_support_ticket_manager'):
        #             ticket_manager_group.write({'users': [(3, record.id)]})
        #         ticket_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_groups.group_project_costing_can_view'):
        #             project_costing_group.write({'users': [(3, record.id)]})
        #         analytic_tags_group.write({'users': [(4, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_user'):
        #             tender_representative_group.write({'users': [(3, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_manager'):
        #             bid_manager_group.write({'users': [(3, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_financial_committee'):
        #             financial_committee_group.write({'users': [(3, record.id)]})
        #         if record.has_group('sh_po_tender_management.sh_purchase_tender_technical_committee'):
        #             technical_committee_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_change_request.group_cr_approval_access'):
        #             cr_approval_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_change_request.group_cr_close_approval_access'):
        #             cr_close_approval_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_change_request.group_change_management_can_create'):
        #             cr_manager_group.write({'users': [(3, record.id)]})
        #         cr_user_group.write({'users': [(4, record.id)]})
        #         if record.has_group('contract.group_contract_approver'):
        #             contract_approve_group.write({'users': [(3, record.id)]})
        #         if record.has_group('contract.group_contract_close_approval_access'):
        #             contract_close_approve_group.write({'users': [(3, record.id)]})
        #         if record.has_group('contract.group_contract_creator'):
        #             contract_creator_group.write({'users': [(3, record.id)]})
        #         if record.has_group('contract.group_contract_view'):
        #             contract_view_group.write({'users': [(3, record.id)]})
        #         task_iss_inc_create_group.write({'users': [(4, record.id)]})
        #         task_iss_inc_view_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_groups.group_quality_management_can_approve'):
        #             quality_approve_group.write({'users': [(2, record.id)]})
        #         quality_view_group.write({'users': [(4, record.id)]})
        #         quality_create_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_groups.group_quality_control_auditor'):
        #             quality_auditor_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_groups.group_acceptance_management_can_approve'):
        #             acceptance_approve_group.write({'users': [(3, record.id)]})
        #         acceptance_create_group.write({'users': [(4, record.id)]})
        #         acceptance_view_group.write({'users': [(4, record.id)]})
        #         if record.has_group('gts_groups.group_budget_management_can_create'):
        #             budget_create_group.write({'users': [(3, record.id)]})
        #         if record.has_group('gts_groups.group_budget_management_can_view'):
        #             budget_view_group.write({'users': [(3, record.id)]})
        #         ticket_create_group.write({'users': [(4, record.id)]})
        #         ticket_view_group.write({'users': [(4, record.id)]})
        # return users
