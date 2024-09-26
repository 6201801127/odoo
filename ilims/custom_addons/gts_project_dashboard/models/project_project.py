import pytz
from odoo import models, fields, api
from datetime import timedelta, datetime, date


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def get_details(self):
        user = self.env.user
        dt = datetime.now().date()
        projects = self.env['project.project'].search([])
        project_task = self.env['project.task']
        revenue_expense, tenders_list, quality_list, project_tagged, tasks_list, issue_list, \
        change_request_list, ticket_list = [], [], [], [], [], [], [], []
        for record in projects:
            # Revenue and Expense
            if record.analytic_account_id:
                invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                                                            ('analytic_account_id', '=', record.analytic_account_id.id)])
                bills = self.env['account.move'].search([('move_type', '=', 'in_invoice'),
                                                         ('analytic_account_id', '=', record.analytic_account_id.id)])
                total_invoice, total_bill = 0, 0
                if invoices:
                    for invoice in invoices:
                        total_invoice += invoice.amount_total
                if bills:
                    for bill in bills:
                        total_bill += bill.amount_total
                revenue_expense.append({
                    'project': record.name,
                    'expense': '{0:,.2f}'.format(total_bill),
                    'profit_loss': '{0:,.2f}'.format(total_invoice - total_bill)
                })
            # Quality
            inspection_created = self.env['qc.inspection'].search_count([('project_id', '=', record.id),
                                                                         ('state', '=', 'draft')])
            inspection_inprogress = self.env['qc.inspection'].search_count([('project_id', '=', record.id),
                                                                            ('state', '=', 'audit_in_progress')])
            inspection_success = self.env['qc.inspection'].search_count([('project_id', '=', record.id),
                                                                         ('state', '=', 'success')])
            inspection_failed = self.env['qc.inspection'].search_count([('project_id', '=', record.id),
                                                                         ('state', '=', 'failed')])
            quality_list.append({
                'project': record.name,
                'inspection_created': inspection_created,
                'inspection_inprogress': inspection_inprogress,
                'inspection_success': inspection_success,
                'inspection_failed': inspection_failed
            })
            # Project tagged
            project_tagged.append({
                'project': record.name,
                'customer': record.partner_id.name
            })
            # Tasks
            total_tasks = project_task.search_count([('project_id', '=', record.id),('risk_incident', '=', False),
                                                     ('is_issue', '=', False), ('user_id', '=', user.id)])
            closed_tasks = project_task.search_count([('project_id', '=', record.id), ('risk_incident', '=', False),
                                                      ('is_issue', '=', False), ('user_id', '=', user.id),
                                                      ('stage_id.is_closed', '=', True)])
            inprogress_tasks = project_task.search_count([('project_id', '=', record.id), ('risk_incident', '=', False),
                                                          ('is_issue', '=', False), ('user_id', '=', user.id),
                                                          ('stage_id.is_closed', '=', False)])
            tasks_list.append({
                'project': record.name,
                'total_tasks': total_tasks,
                'closed_tasks': closed_tasks,
                'inprogress_tasks': inprogress_tasks
            })
            # Issue
            total_issue = project_task.search_count([('is_issue', '=', True), ('user_id', '=', user.id)])
            open_issue = project_task.search_count([('is_issue', '=', True), ('user_id', '=', user.id),
                                                    ('stage_id.is_closed', '!=', True)])
            closed_issue = project_task.search_count([('is_issue', '=', True), ('user_id', '=', user.id),
                                                      ('stage_id.is_closed', '=', True)])
            issue_list.append({
                'project': record.name,
                'total_issue': total_issue,
                'open_issue': open_issue,
                'closed_issue': closed_issue
            })
            # Change Request
            total_cr = self.env['change.request'].search_count([('project_id', '=', record.id),
                                                                ('state', 'in', ('approved', 'waiting_for_approval'))])
            approved_cr = self.env['change.request'].search_count([('project_id', '=', record.id),
                                                                   ('state', '=', 'approved')])
            pending_cr = self.env['change.request'].search_count([('project_id', '=', record.id),
                                                                  ('state', '=', 'waiting_for_approval')])
            change_request_list.append({
                'project': record.name,
                'total_cr': total_cr,
                'approved_cr': approved_cr,
                'pending_cr': pending_cr
            })
            # Tickets
            total_ticket = self.env['support.ticket'].search_count([('project_id', '=', record.id)])
            approved_ticket = self.env['support.ticket'].search_count([('project_id', '=', record.id),
                                                                    ('stage_id.is_close', '=', True)])
            pending_ticket = self.env['support.ticket'].search_count([('project_id', '=', record.id),
                                                                       ('stage_id.is_close', '=', False)])
            ticket_list.append({
                'project': record.name,
                'total_ticket': total_ticket,
                'approved_ticket': approved_ticket,
                'pending_ticket': pending_ticket
            })
            if user.has_group('gts_project_stages.group_project_manager_new') or user.has_group('project.group_project_manager'):
                # Tenders
                tenders = self.env['purchase.agreement'].search([('project_id', '=', record.id),
                                                                 ('state', 'not in', ['draft', 'confirm', 'cancel']),
                                                                 ('is_published', '=', True)])
                open_count, open_amount = 0, 0
                proforma_count, proforma_amount = 0, 0
                for tender in tenders:
                    open_count += 1
                    for lines in tender.sh_purchase_agreement_line_ids:
                        open_amount += lines.sh_price_unit
                tenders = self.env['purchase.agreement'].search([('project_id', '=', record.id),
                                                                 ('state', 'not in', ['draft', 'confirm', 'cancel']),
                                                                 ('is_published', '=', False)])
                for tender in tenders:
                    purchases = self.env['purchase.order'].search([('agreement_id', '=', tender.id),
                                                                   ('state', 'in', ('draft', 'sent'))])
                    for purchase in purchases:
                        proforma_count += 1
                        proforma_amount += purchase.amount_total
                purchases = self.env['purchase.order'].search([('state', '=', 'purchase'),
                                                               ('analytic_account_id', '=', record.analytic_account_id.id)])
                direct_count, direct_amount = 0, 0
                for purchase in purchases:
                    direct_count += 1
                    direct_amount += purchase.amount_total
                tenders_list.append({
                    'project': record.name,
                    'open_count': open_count,
                    'open_amount': '{0:,.2f}'.format(open_amount),
                    'proforma_count': proforma_count,
                    'proforma_amount': '{0:,.2f}'.format(proforma_amount),
                    'direct_count': direct_count,
                    'direct_amount': '{0:,.2f}'.format(direct_amount)
                })
        if user.has_group('gts_project_stages.group_project_manager_new') or user.has_group(
                'project.group_project_manager'):
            open_count, open_amount = 0, 0
            proforma_count, proforma_amount = 0, 0
            for tender in self.env['purchase.agreement'].search([('project_id', '=', False),
                                                                 ('state', 'not in', ['draft', 'confirm', 'cancel']),
                                                                 ('is_published', '=', True)]):
                open_count += 1
                for lines in tender.sh_purchase_agreement_line_ids:
                    open_amount += lines.sh_price_unit
            for tender in self.env['purchase.agreement'].search([('project_id', '=', False),
                                                                 ('state', 'not in', ['draft', 'confirm', 'cancel']),
                                                                 ('is_published', '=', False)]):
                purchases = self.env['purchase.order'].search([('agreement_id', '=', tender.id),
                                                               ('state', 'in', ('draft', 'sent'))])
                for purchase in purchases:
                    proforma_count += 1
                    proforma_amount += purchase.amount_total
            purchases = self.env['purchase.order'].search([('state', '=', 'purchase'),
                                                           ('analytic_account_id', '=', False)])
            direct_count, direct_amount = 0, 0
            for purchase in purchases:
                direct_count += 1
                direct_amount += purchase.amount_total
            tenders_list.append({
                'project': 'Undefined',
                'open_count': open_count,
                'open_amount': '{0:,.2f}'.format(open_amount),
                'proforma_count': proforma_count,
                'proforma_amount': '{0:,.2f}'.format(proforma_amount),
                'direct_count': direct_count,
                'direct_amount': '{0:,.2f}'.format(direct_amount)
            })
        return {
            'revenue_expense': revenue_expense,
            'tenders_list': tenders_list,
            'quality_list': quality_list,
            'project_tagged': project_tagged,
            'tasks_list': tasks_list,
            'issue_list': issue_list,
            'change_request_list': change_request_list,
            'ticket_list': ticket_list
        }

    @api.model
    def get_contract_count(self):
        dt = datetime.now().date()
        projects = self.env['project.project'].search([])
        active_contracts = self.env['partner.contract'].search_count([('related_project', 'in', projects.ids),
                                                                      ('start_date', '<=', dt), ('end_date', '>=', dt),
                                                                      ('state', '!=', 'closed')])
        closed_contracts = self.env['partner.contract'].search_count([('related_project', 'in', projects.ids),
                                                                      ('state', '=', 'closed')])
        return {
            'active_contracts': active_contracts,
            'closed_contracts': closed_contracts,
        }

    @api.model
    def get_stage_wise_project(self):
        project_stage = self.env['project.stage'].search([])
        project_obj = self.env['project.project']
        stage_list, project_list = [], []
        for stage in project_stage:
            projects = project_obj.search_count([('stage_id', '=', stage.id)])
            stage_list.append(stage.name)
            project_list.append(projects)
        return {
            'stage_list': stage_list,
            'project_list': project_list
        }

    @api.model
    def get_project_manager_tagged(self):
        users_obj = self.env['res.users']
        project_managers = users_obj.search([('groups_id', 'in',
                                              self.env.ref('gts_project_stages.group_project_manager_new').id)])
        project_manager_name, count_list = [], []
        for manager in project_managers:
            project_count = self.env['project.project'].search_count([('user_id', '=', manager.id)])
            project_manager_name.append(manager.name)
            count_list.append(project_count)
        return {
            'project_manager_name': project_manager_name,
            'count_list': count_list
        }

    @api.model
    def get_program_manager_tagged(self):
        users_obj = self.env['res.users']
        program_managers = users_obj.search([('groups_id', 'in',
                                              self.env.ref('gts_project_stages.group_program_manager').id)])
        program_manager_name, count_list = [], []
        for manager in program_managers:
            project_count = self.env['project.project'].search_count([('program_manager_id', '=', manager.id)])
            program_manager_name.append(manager.name)
            count_list.append(project_count)
        return {
            'program_manager_name': program_manager_name,
            'count_list': count_list
        }

    @api.model
    def get_budget_cost_expense(self):
        user = self.env.user
        projects = self.env['project.project'].search([])
        project_list, budget_list, utilized_list = [], [], []
        for project in projects:
            budget_lines = self.env['crossovered.budget.lines'].search([('analytic_account_id', '=', project.analytic_account_id.id)])
            budget_amount, utilized_amount = 0, 0
            for lines in budget_lines:
                if lines.crossovered_budget_id.state != 'cancel':
                    budget_amount += lines.planned_amount
                    utilized_amount += lines.practical_amount
            project_list.append(project.name)
            budget_list.append(budget_amount)
            utilized_list.append(utilized_amount)
        return {
            'project_list': project_list,
            'budget_list': budget_list,
            'utilized_list': utilized_list
        }

    @api.model
    def get_project_resource(self):
        user = self.env.user
        projects = self.env['project.project'].search([])
        project_resource, internal_list, external_list = [], [], []
        for project in projects:
            internal, external = 0, 0
            for lines in project.stakeholder_ids:
                if lines.type_of_stakeholder.name == 'Internal':
                    internal += 1
                if lines.type_of_stakeholder.name == 'External':
                    external += 1
            project_resource.append(project.name)
            internal_list.append(internal)
            external_list.append(external)
        return {
            'project_resource': project_resource,
            'internal_list': internal_list,
            'external_list': external_list
        }

    @api.model
    def get_project_risk(self):
        user = self.env.user
        projects = self.env['project.project'].search([])
        project_list, risk_list = [], []
        for record in projects:
            risks = self.env['project.task'].search_count([('risk_incident', '=', True), ('user_id', '=', user.id),
                                                           ('project_id', '=', record.id)])
            project_list.append(record.name)
            risk_list.append(risks)
        return {
            'project_list': project_list,
            'risk_list': risk_list
        }
