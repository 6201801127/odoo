from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import os
import tempfile
import logging

_logger = logging.getLogger('****************Capital Budget Report****************')

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import xlwt
    import xlsxwriter
    from xlwt.Utils import rowcol_to_cell
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
import base64

class BudgetStatus(models.TransientModel):
    _name = "budget.status"
    _description = "Budget Status"

    budget_type = fields.Selection(
        [('All', 'All Budget'), ('Project', 'Project Budget'), ('Capital', 'Capital Budget'), ('Treasury', 'Treasury Budget')],
        string="Budget Type")
    project_budget_status_ids = fields.One2many('project.budget.status', 'budget_status_id', string='Project Budget', store=1)
    budget_status_line_ids = fields.One2many('project.budget.status', 'budget_status_line_id', string='Project Budget', store=1)

    @api.onchange('budget_type')
    def _onchange_budget_type(self):
        if self.project_budget_status_ids:
            self.project_budget_status_ids= [(5, 0, 0)]
        if self.budget_status_line_ids:
            self.budget_status_line_ids=[(5, 0, 0)]
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        new_lines = []
        new_lines2 = []
        if self.budget_type == 'Project':
            project_budget_ids = self.env['kw_sbu_project_budget'].sudo().search([('fiscal_year_id', '=', current_fiscal.id), ('state', 'in', ('to_approve', 'approved', 'cfo', 'confirm'))])
            project_budget_line_ids = self.env['revised_sbu_project_budget_wizard'].search(
                [('pending_at', 'in', ('L2', 'Finance', 'cfo', 'Approver')), ('sbu_project_budget_id.fiscal_year_id', '=', current_fiscal.id)])
            if project_budget_ids:
                for rec in project_budget_ids:
                    new_lines.append((0, 0, {
                        'fiscal_year_id': rec.fiscal_year_id.id,
                        'created_by': rec.create_uid.name,
                        'budget_department': rec.budget_department.sbu_id.name + rec.budget_department.sbu_id.representative_id.name,
                        'branch': rec.branch_id.name,
                        'pending_at_ids': [(6, 0, rec.pending_at_ids.ids)],
                        'pending_since': rec.pending_since,
                        # 'status': rec.state,
                        'status': 'L2' if rec.state == 'to_approve'  else 'Finance' if rec.state == 'approved' else 'CFO' if rec.state == 'cfo' else 'CEO' if rec.state == 'confirm' else rec.state,
                        'budget_status_id': self.id,
                        'date': rec.create_date,
                        'project_budget_id': rec.id,
                    }))
                self.project_budget_status_ids = new_lines
            if project_budget_line_ids:
                for rec in project_budget_line_ids:
                    if rec.pending_at not in ['L1', 'Validate', 'Cancel']:
                        new_lines2.append((0, 0, {
                            'fiscal_year_id': rec.sbu_project_budget_id.fiscal_year_id.id,
                            'created_by': rec.create_uid.name,
                            'budget_department': rec.sbu_project_budget_id.budget_department.sbu_id.name + rec.sbu_project_budget_id.budget_department.sbu_id.representative_id.name,
                            'branch': rec.branch_id ,
                            'status': 'CEO' if rec.pending_at == 'Approver'  else 'CFO' if rec.pending_at == 'cfo' else rec.pending_at,
                            'pending_since': rec.pending_since,
                            'budget_status_line_ids': self.id,
                            'budget_name': 'Project Budget',
                            'date': rec.create_date,
                            'project_budget_line_id': rec.id,
                        }))
                self.budget_status_line_ids = new_lines2
        elif self.budget_type == 'Capital':
            capital_budget_ids = self.env['kw_capital_budget'].sudo().search([('fiscal_year_id', '=', current_fiscal.id), ('state', 'in', ('to_approve', 'approved', 'cfo', 'confirm'))])
            capital_budget_line_ids = self.env['revised_budget_wizard'].search(
                [('pending_at', 'in', ('L2', 'Finance', 'cfo', 'Approver')), ('capital_budget_id.fiscal_year_id', '=', current_fiscal.id)])
            if capital_budget_ids:

                for rec in capital_budget_ids:
                    new_lines.append((0, 0, {
                        'fiscal_year_id': rec.fiscal_year_id.id,
                        'created_by': rec.create_uid.name,
                        'budget_department': rec.budget_department.name,
                        'branch': rec.branch_id.name,
                        'pending_at_ids': [(6, 0, rec.pending_at_ids.ids)],
                        'pending_since': rec.pending_since,
                        'status': 'L2' if rec.state == 'to_approve'  else 'Finance' if rec.state == 'approved' else 'CFO' if rec.state == 'cfo' else 'CEO' if rec.state == 'confirm' else rec.state,
                        'budget_status_id': self.id,
                        'date': rec.create_date,
                        'capital_budget_id': rec.id,
                    }))
                self.project_budget_status_ids = new_lines
            if capital_budget_line_ids:
                for rec in capital_budget_line_ids:
                    if rec.pending_at not in ['L1', 'Validate', 'Cancel']:
                        new_lines2.append((0, 0, {
                        'fiscal_year_id': rec.capital_budget_id.fiscal_year_id.id,
                        'created_by': rec.create_uid.name,
                        'budget_department': rec.budget_department,
                        'branch': rec.branch_id ,
                        'status': 'CEO' if rec.pending_at == 'Approver'  else 'CFO' if rec.pending_at == 'cfo' else rec.pending_at,
                        'pending_since': rec.pending_since,
                        'budget_status_line_ids': self.id,
                        'budget_name': 'Capital Budget',
                        'date': rec.create_date,
                        'capital_budget_line_id': rec.id,
                    }))
                self.budget_status_line_ids = new_lines2
        elif self.budget_type == 'Treasury':
            treasury_budget_ids = self.env['kw_revenue_budget'].sudo().search([('fiscal_year_id', '=', current_fiscal.id), ('state', 'in', ('to_approve', 'approved', 'cfo', 'confirm'))])
            treasury_budget_line_ids = self.env['revised_revenue_budget_wizard'].search(
                [('pending_at', 'in', ('L2', 'Finance', 'cfo', 'Approver')), ('revenue_budget_id.fiscal_year_id', '=', current_fiscal.id)])
            if treasury_budget_ids:
                new_lines = []
                new_lines2 = []
                for rec in treasury_budget_ids:
                    new_lines.append((0, 0, {
                        'fiscal_year_id': rec.fiscal_year_id.id,
                        'created_by': rec.create_uid.name,
                        'budget_department': rec.budget_department.name,
                        'branch': rec.branch_id.name,
                        'pending_at_ids': [(6, 0, rec.pending_at_ids.ids)],
                        'pending_since': rec.pending_since,
                        'status': 'L2' if rec.state == 'to_approve'  else 'Finance' if rec.state == 'approved' else 'CFO' if rec.state == 'cfo' else 'CEO' if rec.state == 'confirm' else rec.state,
                        'budget_status_id': self.id,
                        'date': rec.create_date,
                        'revenue_budget_id': rec.id,
                    }))
                self.project_budget_status_ids = new_lines
            if treasury_budget_line_ids:
                for rec in treasury_budget_line_ids:
                    if rec.pending_at not in ['L1', 'Validate', 'Cancel']:
                        new_lines2.append((0, 0, {
                            'fiscal_year_id': rec.revenue_budget_id.fiscal_year_id.id,
                            'created_by': rec.create_uid.name,
                            'budget_department': rec.budget_department,
                            'branch': rec.branch_id ,
                            'status': 'CEO' if rec.pending_at == 'Approver'  else 'CFO' if rec.pending_at == 'cfo' else rec.pending_at,
                            'pending_since': rec.pending_since,
                            'budget_status_line_ids': self.id,
                            'budget_name': 'Revenue Budget',
                            'date': rec.create_date,
                            'revenue_budget_line_id': rec.id,
                        }))
                self.budget_status_line_ids = new_lines2
        elif self.budget_type == 'All':
            self.show_all_budget_data()
        else:
            pass

    def show_all_budget_data(self):
        new_lines = []
        new_lines2 = []
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])

        project_budget_ids = self.env['kw_sbu_project_budget'].sudo().search(
            [('fiscal_year_id', '=', current_fiscal.id), ('state', 'in', ('to_approve', 'approved', 'cfo', 'confirm'))])
        project_budget_line_ids = self.env['revised_sbu_project_budget_wizard'].search(
            [('pending_at', 'in', ('L2', 'Finance', 'cfo', 'Approver')),
             ('sbu_project_budget_id.fiscal_year_id', '=', current_fiscal.id)])
        if project_budget_ids:

            for rec in project_budget_ids:
                new_lines.append((0, 0, {
                    'fiscal_year_id': rec.fiscal_year_id.id,
                    'created_by': rec.create_uid.name,
                    'budget_department': rec.budget_department.sbu_id.name + rec.budget_department.sbu_id.representative_id.name,
                    'branch': rec.branch_id.name,
                    'pending_at_ids': [(6, 0, rec.pending_at_ids.ids)],
                    'status': 'L2' if rec.state == 'to_approve'  else 'Finance' if rec.state == 'approved' else 'CFO' if rec.state == 'cfo' else 'CEO' if rec.state == 'confirm' else rec.state,
                    'pending_since': rec.pending_since,
                    'budget_status_id': self.id,
                    'date': rec.create_date,
                    'project_budget_id': rec.id,
                }))
            # self.project_budget_status_ids = new_lines
        if project_budget_line_ids:
            for rec in project_budget_line_ids:
                if rec.pending_at not in ['L1', 'Validate', 'Cancel']:
                    new_lines2.append((0, 0, {
                    'fiscal_year_id': rec.sbu_project_budget_id.fiscal_year_id.id,
                    'created_by': rec.create_uid.name,
                    'budget_department': rec.sbu_project_budget_id.budget_department.sbu_id.name + rec.sbu_project_budget_id.budget_department.sbu_id.representative_id.name,
                    'branch': rec.branch_id,
                    'pending_since': rec.pending_since,
                    'status': 'CEO' if rec.pending_at == 'Approver'  else 'CFO' if rec.pending_at == 'cfo' else rec.pending_at,
                    'budget_status_line_ids': self.id,
                    'budget_name': 'Project Budget',
                    'date': rec.create_date,
                    'project_budget_line_id': rec.id,
                }))
            # self.budget_status_line_ids = new_lines2


        capital_budget_ids = self.env['kw_capital_budget'].sudo().search(
            [('fiscal_year_id', '=', current_fiscal.id), ('state', 'in', ('to_approve', 'approved', 'cfo', 'confirm'))])
        capital_budget_line_ids = self.env['revised_budget_wizard'].search(
            [('pending_at', 'in', ('L2', 'Finance', 'cfo', 'Approver')),
             ('capital_budget_id.fiscal_year_id', '=', current_fiscal.id)])
        if capital_budget_ids:
            for rec in capital_budget_ids:
                new_lines.append((0, 0, {
                    'fiscal_year_id': rec.fiscal_year_id.id,
                    'created_by': rec.create_uid.name,
                    'budget_department': rec.budget_department.name,
                    'branch': rec.branch_id.name,
                    'pending_at_ids': [(6, 0, rec.pending_at_ids.ids)],
                    'status': 'L2' if rec.state == 'to_approve'  else 'Finance' if rec.state == 'approved' else 'CFO' if rec.state == 'cfo' else 'CEO' if rec.state == 'confirm' else rec.state,
                    'pending_since': rec.pending_since,
                    'budget_status_id': self.id,
                    'date': rec.create_date,
                    'capital_budget_id': rec.id,
                }))
            # self.project_budget_status_ids = new_lines
        if capital_budget_line_ids:
            for rec in capital_budget_line_ids:
                if rec.pending_at not in ['L1', 'Validate', 'Cancel']:
                    new_lines2.append((0, 0, {
                    'fiscal_year_id': rec.capital_budget_id.fiscal_year_id.id,
                    'created_by': rec.create_uid.name,
                    'budget_department': rec.budget_department,
                    'branch': rec.branch_id,
                    'pending_since': rec.pending_since,
                    'status': 'CEO' if rec.pending_at == 'Approver'  else 'CFO' if rec.pending_at == 'cfo' else rec.pending_at,
                    'budget_status_line_ids': self.id,
                    'budget_name': 'Capital Budget',
                    'date': rec.create_date,
                    'capital_budget_line_id': rec.id,
                }))
            # self.budget_status_line_ids = new_lines2

        treasury_budget_ids = self.env['kw_revenue_budget'].sudo().search(
            [('fiscal_year_id', '=', current_fiscal.id), ('state', 'in', ('to_approve', 'approved', 'cfo', 'confirm'))])
        treasury_budget_line_ids = self.env['revised_revenue_budget_wizard'].search(
            [('pending_at', 'in', ('L2', 'Finance', 'cfo', 'Approver')),
             ('revenue_budget_id.fiscal_year_id', '=', current_fiscal.id)])
        if treasury_budget_ids:

            for rec in treasury_budget_ids:
                new_lines.append((0, 0, {
                    'fiscal_year_id': rec.fiscal_year_id.id,
                    'created_by': rec.create_uid.name,
                    'budget_department': rec.budget_department.name,
                    'branch': rec.branch_id.name,
                    'pending_at_ids': [(6, 0, rec.pending_at_ids.ids)],
                    'status': 'L2' if rec.state == 'to_approve'  else 'Finance' if rec.state == 'approved' else 'CFO' if rec.state == 'cfo' else 'CEO' if rec.state == 'confirm' else rec.state,
                    'pending_since': rec.pending_since,
                    'budget_status_id': self.id,
                    'date': rec.create_date,
                    'revenue_budget_id': rec.id,
                }))
        if treasury_budget_line_ids:
            for rec in treasury_budget_line_ids:
                if rec.pending_at not in ['L1', 'Validate', 'Cancel']:
                    new_lines2.append((0, 0, {
                    'fiscal_year_id': rec.revenue_budget_id.fiscal_year_id.id,
                    'created_by': rec.create_uid.name,
                    'budget_department': rec.budget_department,
                    'branch': rec.branch_id,
                    'pending_since': rec.pending_since,
                    'status': 'CEO' if rec.pending_at == 'Approver'  else 'CFO' if rec.pending_at == 'cfo' else rec.pending_at,
                    'budget_status_line_ids': self.id,
                    'budget_name': 'Revenue Budget',
                    'date': rec.create_date,
                    'revenue_budget_line_id': rec.id,
                }))
        print(new_lines, 'nnnnnnnnnnnnnnnnnnn')
        print(new_lines2, 'CCCCCCCCCCCCCCCCCCC')
        self.budget_status_line_ids = new_lines2
        self.project_budget_status_ids = new_lines


    def print_budget_status_report(self):
        '''
        this function is used to print the XLXS report
        '''

        temp_dir = tempfile.gettempdir() or '/tmp'
        f_name = os.path.join(temp_dir, 'Budget Status.xlsx')
        workbook = xlsxwriter.Workbook(f_name)
        date_format = workbook.add_format({'num_format': 'd-m-yyyy',
                                           'align': 'center',
                                           'font_color': 'white',
                                           'valign': 'vcenter'})

        style_header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_data = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True})
        style_data2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'text_wrap': True})
        style_data3 = workbook.add_format({
            'border': 1,
            'align': 'left'})
        style_total = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_color': 'white',
            'valign': 'vcenter'})
        style_header2.set_text_wrap()
        style_header.set_font_size(18)
        # style_header.set_text_wrap()
        style_header.set_bg_color('#95edd9')
        style_header.set_font_name('Agency FB')
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        # style_data.set_text_wrap()
        style_data.set_font_name('Agency FB')
        style_data2.set_font_size(12)
        style_data2.set_font_name('Agency FB')
        style_data2.set_bg_color('#95DDF7')
        style_data3.set_font_size(12)
        style_data3.set_font_name('Agency FB')
        style_data3.set_bg_color('#6dd45c')
        style_total.set_font_size(12)
        style_total.set_text_wrap()
        style_total.set_border(style=2)
        date_format.set_font_size(12)
        date_format.set_bg_color('#108fbb')
        date_format.set_font_name('Agency FB')
        date_format.set_border(style=2)
        style_header2.set_font_size(12)
        style_header2.set_bg_color('#108fbb')
        style_header2.set_font_name('Agency FB')
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet('Budget Status Report')
        worksheet.set_column(0, 0, 6)
        worksheet.set_column(1, 1, 14)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 30)
        worksheet.set_column(4, 4, 30)
        worksheet.set_column(5, 5, 14)
        worksheet.set_column(6, 6, 14)
        worksheet.set_column(7, 7, 14)
        worksheet.set_row(0, 25)
        worksheet.set_row(1, 100)
        row, col = 0, 0

        if self.project_budget_status_ids:
            worksheet.merge_range(row, col, row, col + 7, "Budget Status", style_header)
            row += 1
            worksheet.write(row, col, 'sr.No ', style_header2)
            worksheet.write(row, col + 1, 'Fiscal Year', style_header2)
            worksheet.write(row, col + 2, 'Created By', style_header2)
            worksheet.write(row, col + 3, 'Budget For', style_header2)
            worksheet.write(row, col + 4, 'Pending Since', style_header2)
            worksheet.write(row, col + 5, 'Pending At ', style_header2)
            worksheet.write(row, col + 6, 'Status', style_header2)
            worksheet.write(row, col + 7, 'Create Date', style_header2)
            if self.project_budget_status_ids:
                seq = 1
                pending_date, create_date = '', ''
                for rec in self.project_budget_status_ids:
                    row += 1
                    print(rec.pending_since, 'PENDING SINCEEEEEEEEEEEEE')
                    date_from = rec.pending_since
                    if date_from:
                        pending_date = date_from.strftime('%d-%m-%Y')
                    create_date = rec.date
                    if create_date:
                        create_date = create_date.strftime('%d-%m-%Y')
                    names_line = ''
                    names_line = ', '.join([i.name for i in rec.pending_at_ids])
                    worksheet.write(row, col, seq, style_data)
                    worksheet.write(row, col + 1, rec.fiscal_year_id.name, style_data)
                    worksheet.write(row, col + 2, rec.created_by, style_data)
                    worksheet.write(row, col + 3, rec.budget_department, style_data)
                    worksheet.write(row, col + 4, pending_date, style_data)
                    worksheet.write(row, col + 5, names_line, style_data)
                    worksheet.write(row, col + 6, rec.status, style_data)
                    worksheet.write(row, col + 7, create_date, style_data2)
                    seq += 1
                row += 1
        if self.budget_status_line_ids:
            second_seq = 1
            worksheet.merge_range(row, col, row, col + 7, "Budget Additional/Revise Status", style_header)
            row +=1
            worksheet.write(row, col, 'sr.No ', style_header2)
            worksheet.write(row, col + 1, 'Budget Name', style_header2)
            worksheet.write(row, col + 2, 'Fiscal Year', style_header2)
            worksheet.write(row, col + 3, 'Created By', style_header2)
            worksheet.write(row, col + 4, 'Budget For', style_header2)
            worksheet.write(row, col + 5, 'Pending Since ', style_header2)
            worksheet.write(row, col + 6, 'Pending At', style_header2)
            worksheet.write(row, col + 7, 'Create Date', style_header2)
            if self.budget_status_line_ids:
                seq = 1
                create_date, pending_date = '', ''
                for data in self.budget_status_line_ids:
                    row += 1

                    date_from = data.pending_since
                    if date_from:
                        pending_date = date_from.strftime('%d-%m-%Y')
                    create_date = data.date
                    if create_date:
                        create_date = create_date.strftime('%d-%m-%Y')
                    worksheet.write(row, col, second_seq, style_data)
                    worksheet.write(row, col + 1, data.budget_name, style_data)
                    worksheet.write(row, col + 2, data.fiscal_year_id.name or '', style_data)
                    worksheet.write(row, col + 3, data.created_by, style_data)
                    worksheet.write(row, col + 4, data.budget_department, style_data)
                    worksheet.write(row, col + 5, pending_date, style_data)
                    worksheet.write(row, col + 6, data.status, style_data)
                    worksheet.write(row, col + 7, create_date, style_data2)
                    second_seq += 1



        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "Budget Status Report.xlsx"
        out_wizard = self.env['budget.xlsx.output'].create({'name': name,
                                                            'xls_output': base64.encodebytes(data)})
        view_id = self.env.ref('kw_budget.budget_xlsx_output_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'budget.xlsx.output',
            'target': 'new',
            'view_mode': 'form',
            'res_id': out_wizard.id,
            'views': [[view_id, 'form']],
        }


class ProjectBudgetStatus(models.TransientModel):
    _name = "project.budget.status"
    _description = "Project Budget Status"

    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year", store=1)
    created_by = fields.Char('Created By', store=1)
    budget_department = fields.Char('Budget For', store=1)
    branch = fields.Char('Branch', store=1)
    pending_at_ids = fields.Many2many('hr.employee', string='Pending at', store=1)
    status = fields.Char('Status', store=1)
    budget_status_id = fields.Many2one('budget.status', string='Budget Status', store=1)
    budget_status_line_id = fields.Many2one('budget.status', string='Budget Status', store=1)
    date = fields.Datetime('Create Date', store=1)
    pending_since = fields.Datetime('Pending Since', store=1)

    # for lines only
    budget_name = fields.Char('Budget Name')

    project_budget_id = fields.Many2one('kw_sbu_project_budget', 'Project')
    project_budget_line_id = fields.Many2one('revised_sbu_project_budget_wizard', 'Project Line')
    revenue_budget_id = fields.Many2one('kw_revenue_budget', 'Revenue')
    revenue_budget_line_id = fields.Many2one('revised_revenue_budget_wizard', 'Revenue Line')
    capital_budget_id = fields.Many2one('kw_capital_budget', 'Capital')
    capital_budget_line_id = fields.Many2one('revised_budget_wizard', 'Capital Line')

    def action_view_budget_lines(self):
        if self.project_budget_id:
            action = self.env['ir.actions.act_window'].for_xml_id('kw_sbu_project_budget_take_action_window')

            domain = [('id', '=',
                       self.project_budget_id.id)
                      ]
            action['domain'] = domain
            return action
        elif self.revenue_budget_id:
            action = self.env['ir.actions.act_window'].for_xml_id('kw_revenue_budget_take_action_window')
            domain = [('id', '=',
                       self.project_budget_id.id)
                      ]
            action['domain'] = domain
            return action
        elif self.capital_budget_id:
            action = self.env['ir.actions.act_window'].for_xml_id('kw_capital_budget_take_action_window')
            domain = [('id', '=',
                       self.project_budget_id.id)
                      ]
            action['domain'] = domain
            return action
        else:
            raise ValidationError('No Budget ID is tagged with this line.')

    def action_view_budget(self):

        if self.project_budget_id:
            action = self.env['ir.actions.act_window'].for_xml_id('kw_sbu_project_budget_take_action_window')
            
            domain = [('id', '=',
                       self.project_budget_id.id)
                      ]
            action['domain'] = domain
            return  action
        elif self.revenue_budget_id:
            action = self.env['ir.actions.act_window'].for_xml_id('kw_revenue_budget_take_action_window')
            domain = [('id', '=',
                       self.project_budget_id.id)
                      ]
            action['domain'] = domain
            return action
        elif self.capital_budget_id:
            action = self.env['ir.actions.act_window'].for_xml_id('kw_capital_budget_take_action_window')
            domain = [('id', '=',
                       self.project_budget_id.id)
                      ]
            action['domain'] = domain
            return action
        else:
            raise ValidationError('No Budget ID is tagged with this line.')

    # def action_open_budget_entries(self):
    #     action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
    #     domain = [('account_id', '=',
    #                self.account_id.id),
    #               ('project_line', '=', self.project_line.id),
    #               ('date', '>=', self.fiscal_year_id.date_start),
    #               ('date', '<=', self.fiscal_year_id.date_stop),
    #               ('move_id.state', '=', 'posted'),
    #
    #               ]
    #     if not self.department_id and not self.section_id and not self.division_id:
    #         domain.extend([('department_id', '=', False),
    #                        ('section_id', '=', False),
    #                        ('division_id', '=', False)])
    #     else:
    #         if self.section_id:
    #             domain.append(('section_id', '=', self.section_id.id))
    #         elif self.division_id:
    #             domain.append(('division_id', '=', self.division_id.id))
    #         elif self.department_id:
    #             domain.append(('department_id', '=', self.department_id.id))
    #             domain.append(('section_id', '=', False))
    #             domain.append(('division_id', '=', False))
    #     if not self.project_id:
    #         domain.extend([('project_wo_id', '=', False)])
    #     else:
    #         if self.project_id:
    #             domain.append(('project_wo_id', '=', self.project_id.id))
    #     action['domain'] = domain
    #     return action