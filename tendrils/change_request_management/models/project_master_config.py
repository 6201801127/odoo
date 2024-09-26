"""
This module provides utility functions for data processing tasks.
"""
import base64
from io import BytesIO
import re
import unicodedata
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class KwProjectMasterConfiguration(models.Model):
    """
        This class represents project change request master configurations in Odoo.
    """
    _name = "kw_cr_project_configuration"
    _description = "Project CR Master Configuration"
    _rec_name = "project_id"

    project_id = fields.Many2one('project.project', string="Project Name", required=True)
    project_code = fields.Char(string="Project Code", related="project_id.code")
    kickoff_ids = fields.One2many('kw_cr_kickoff', 'project_cr_id', string="Kickoff")
    scm_data = fields.Selection(string="SCM", selection=[('GIT', 'GIT'), ('SVN', 'SVN'), ('TFS', 'TFS')])
    environment_ids = fields.One2many('cr_environment_project_server', 'project_env_cr_id', string="Environment")
    remarks = fields.Text(string="Note")
    email = fields.Text(string="Email")
    ssl = fields.Text(string="SSL")
    sms = fields.Text(string="SMS")
    domain_ids = fields.One2many('kw_domain_sub_domain', 'domain_sub_domain_id', string="Domain and Sub-Domains")
    active = fields.Boolean(string="Active", default=True)

    # @api.constrains('kickoff_ids', 'project_id')
    # def validation_for_kickoff(self):
    #     if not self.kickoff_ids and not self._context.get('bypass_kickoff_validation'):
    #         raise ValidationError("Warning! Enter at least one Kickoff Details.")

    # @api.constrains('domain_ids', 'kickoff_ids')
    # def validation_for_domain(self):
    #     if not self.domain_ids and not self._context.get('bypass_validation_for_domain'):
    #         raise ValidationError("Warning! Enter at least one Domain Details.")

    # @api.constrains('environment_ids', 'domain_ids')
    # def validation_for_environment(self):
    #     if not self.environment_ids and not self._context.get('bypass_environment_validation'):
    #         raise ValidationError("Warning! Enter at least one Environment Details.")

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}

        if "project_id" not in default:
            default["project_id"] = self.project_id.id
        if "scm_data" not in default:
            default["scm_data"] = self.scm_data

        # Handle kickoff_ids
        if "kickoff_ids" not in default:
            kickoff_values = [(0, 0, {'type_kickoff': value.type_kickoff,
                                      'date_of_start': value.date_of_start}) for value in self.kickoff_ids]
            default["kickoff_ids"] = kickoff_values

        # Handle domain_ids
        if "domain_ids" not in default:
            domain_values = [(0, 0, {'domain_id': value.domain_id.id}) for value in self.domain_ids]
            default["domain_ids"] = domain_values

        # Handle environment_ids
        if "environment_ids" not in default:
            environment_values = [(0, 0,
                                   {'environment_id': value.environment_id.id,
                                    'infra_details': value.infra_details.id,
                                    'server_id': value.server_id.id,
                                    'cpu': value.cpu,
                                    'remark': value.remark,
                                    'purpose': value.purpose, }) for value in self.environment_ids]
            default["environment_ids"] = environment_values

        # Set the context flag to bypass validation during copy
        bypass_kickoff_validation = self._context.get('bypass_kickoff_validation', False)
        bypass_validation_for_domain = self._context.get('bypass_validation_for_domain', False)
        bypass_environment_validation = self._context.get('bypass_environment_validation', False)

        res = super(KwProjectMasterConfiguration, self.with_context(bypass_kickoff_validation=bypass_kickoff_validation,
                                                                    bypass_validation_for_domain=bypass_validation_for_domain,
                                                                    bypass_environment_validation=bypass_environment_validation)).copy(default)
        return res


class KwDomainSubDomain(models.Model):
    """
    This class represents domain and sub-domain relationships in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
    """
    _name = "kw_domain_sub_domain"
    _description = "kw_domain_sub_domain"

    domain_sub_domain_id = fields.Many2one('kw_cr_project_configuration')
    domain_id = fields.Many2one('kw_domain_master')
    url_type_id = fields.Many2one(related='domain_id.environment_id')
    remark = fields.Text(sring = "Remark")


class KwProjectKickoff(models.Model):
    """
    This class represents project kickoffs in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
    """
    _name = "kw_cr_kickoff"
    _description = "kw_cr_kickoff"

    type_kickoff = fields.Selection(string="Type", selection=[('Internal', 'Internal'), ('External', 'External')])
    date_of_start = fields.Date(string="Date")
    project_cr_id = fields.Many2one('kw_cr_project_configuration')


class kwProjectDownlodexcel(models.TransientModel):
    """
    This class represents a transient model for downloading PDF files in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
    """
    _name = "pdf_download_wizard"
    _description = "pdf_download_wizard"

    @api.model
    def default_get(self, fields):
        res = super(kwProjectDownlodexcel, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'project_data_id': active_ids,
        })

        return res

    project_data_id = fields.Many2many('kw_cr_project_configuration',
                                       default=lambda self: self.env.context.get('current_ids', [(6, 0, [])]))
    download_file = fields.Binary(string="Download Xls")

    def action_to_download_excel(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        date_default_col1_style = workbook.add_format({'font_name': 'FreeMono', 'font_size': 12, 'align': 'center', 'bold': True, 'num_format': 'yyyy-mm-dd', 'bg_color': '#b6d4be'})
        date_default_col1_style.set_border()
        date_default_col1_style2 = workbook.add_format({'font_name': 'FreeMono', 'font_size': 12, 'align': 'center', 'bold': False, 'num_format': 'yyyy-mm-dd'})
        date_default_col1_style2.set_border()
        cell_text_format_n = workbook.add_format({'font_name': 'FreeMono', 'align': 'left', 'bold': False, 'size': 9})
        cell_text_format_n.set_border()
        cell_text_center_normal = workbook.add_format({'font_name': 'FreeMono', 'align': 'center', 'bold': True, 'size': 11, 'bg_color': '#d8e8dc'})
        cell_text_center_normal.set_border()
        cell_text_center_no_color = workbook.add_format({'font_name': 'FreeMono', 'align': 'center', 'bold': True, 'size': 11, 'bg_color': '#FFFFFF'})
        cell_text_center_no_color.set_border()
        cell_text_format = workbook.add_format({'font_name': 'FreeMono', 'align': 'center', 'bold': False, 'size': 12})
        cell_text_format.set_border()
        cell_text_amount_format = workbook.add_format({'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_text_amount_format.set_border()
        cell_total_amount_format = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, 'num_format': '#,###0.00'})
        cell_total_amount_format.set_border()
        cell_number_total_format = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, 'num_format': '########', 'bg_color': '#b6d4be'})
        cell_number_total_format.set_border()
        worksheet = workbook.add_worksheet('Project Configuration report')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 30)
        worksheet.set_column('K:K', 30)
        worksheet.set_column('L:L', 30)
        worksheet.set_column('M:M', 30)
        worksheet.set_column('N:N', 30)
        row = 0
        col = 0

        for formb in self.project_data_id:
            project_id = formb.project_id.name
            project_name_format = workbook.add_format({'align': 'center', 'bold': True, 'size': 12, 'bg_color': '#b6d4be'})
            project_name_format.set_border()
            heading_format = workbook.add_format({'font_name': 'FreeMono', 'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 16, 'bg_color': '#b6d4be'})
            heading_format.set_border()
            worksheet.set_row(0, 30)  # Adjust the height as needed
            worksheet.merge_range('B1:C1', 'Project Configuration Excel', heading_format)
            row += 2

            worksheet.write(row, col, 'Project Name', cell_text_center_no_color)
            worksheet.write(row, col + 1, project_id or '', cell_text_format)
            worksheet.write(row + 1, col, 'Project Code', cell_text_center_no_color)
            worksheet.write(row + 1, col + 1, formb.project_code or '', cell_text_format)
            worksheet.write(row + 2, col, 'SCM', cell_text_center_no_color)
            worksheet.write(row + 2, col + 1, formb.scm_data or '', cell_text_format)
            worksheet.write(row + 3, col, 'Email', cell_text_center_no_color)
            worksheet.write(row + 3, col + 1, formb.email or '', cell_text_format)
            worksheet.write(row + 4, col, 'SSL', cell_text_center_no_color)
            worksheet.write(row + 4, col + 1, formb.ssl or '', cell_text_format)
            worksheet.write(row + 5, col, 'SMS', cell_text_center_no_color)
            worksheet.write(row + 5, col + 1, formb.sms or '', cell_text_format)
            worksheet.write(row + 6, col, 'Note', cell_text_center_no_color)
            worksheet.write(row + 6, col + 1, formb.remarks or '', cell_text_format)
            row += 8
        row += 2

        # KICKOFF DETAILS
        worksheet.write(row, col, 'Kickoff Details', cell_text_center_normal)
        row += 2
        worksheet.write(row, col, 'Type', cell_text_center_normal)
        worksheet.write(row, col + 1, 'Date', cell_text_center_normal)
        row += 1
        for kick in formb.kickoff_ids:
            worksheet.write(row, col, kick.type_kickoff or '', cell_text_format)
            worksheet.write(row, col + 1, kick.date_of_start or '', date_default_col1_style2)
            row += 1
        row += 2

        # DOMAIN AND SUB DOMAIN DETAILS
        worksheet.write(row, col, 'Domain and Sub-domain Details', cell_text_center_normal)
        row += 2
        worksheet.write(row, col, 'Domain', cell_text_center_normal)
        row += 1
        for domain in formb.domain_ids:
            worksheet.write(row, col, domain.domain_id.name or '', cell_text_format)
            row += 1
        row += 2

        # ENVIRONMENT DETAILS
        worksheet.write(row, col, 'Environment Details', cell_text_center_normal)
        row += 2
        worksheet.write(row, col, 'Environment', cell_text_center_normal)
        worksheet.write(row, col + 1, 'InfraDetails', cell_text_center_normal)
        worksheet.write(row, col + 2, 'Server Name', cell_text_center_normal)
        worksheet.write(row, col + 3, 'CPU Nos', cell_text_center_normal)
        worksheet.write(row, col + 4, 'RAM', cell_text_center_normal)
        worksheet.write(row, col + 5, 'Hosting Type', cell_text_center_normal)
        worksheet.write(row, col + 6, 'Purpose', cell_text_center_normal)
        worksheet.write(row, col + 7, 'Remark', cell_text_center_normal)
        row += 1
        for envo in formb.environment_ids:
            worksheet.write(row, col, envo.environment_id.name or '', cell_text_format)
            worksheet.write(row, col + 1, envo.infra_details.name or '', cell_text_format)
            worksheet.write(row, col + 2, envo.server_id.server_name or '', cell_text_format)
            worksheet.write(row, col + 3, envo.cpu or '', cell_text_format)
            worksheet.write(row, col + 4, envo.ram_p or '', cell_text_format)
            worksheet.write(row, col + 5, envo.dedicate_share or '', cell_text_format)
            worksheet.write(row, col + 6, envo.purpose or '', cell_text_format)
            worksheet.write(row, col + 7, envo.remark or '', cell_text_format)
            row += 1

        # Save the workbook after making changes
        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/pdf_download_wizard/{self.id}/download_file/Project-Configuration-report.xlsx?download=true',
            'target': 'self',
            'tag': 'reload',
        }
