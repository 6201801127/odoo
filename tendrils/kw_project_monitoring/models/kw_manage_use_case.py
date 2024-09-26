import io
import base64
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.http import request, content_disposition
from odoo.exceptions import ValidationError


class KwProjectUseCaseMaster(models.Model):
    _name = 'kw_project_use_case_master'
    _description = 'Use Case Master'
    _rec_name = 'domain_name'

    use_case_code = fields.Char("Use Case Code")
    activity_name = fields.Many2one("kw_project_activity_master", string="Activity Name")
    use_case_details = fields.Text("Use Case Details")
    complexity_level = fields.Selection([('simple', 'Simple'), ('average', 'Average'), ('complex', 'Complex')], 'Complexity')
    reusable = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Reusable')
    customization_effort = fields.Integer("Customization Effort")
    effective_uc_point = fields.Float("Effective UC Point")
    create_date = fields.Date("Created On")
    create_uid = fields.Many2one('res.users',string="Created By")
    write_date = fields.Date("Updated On")
    write_uid = fields.Many2one('res.users',string='Updated By')
    use_case_id = fields.Many2one("kw_project_add_use_case_master")
    domain_name = fields.Many2one('kw_domain_master', string="Domain Name")

    _sql_constraints = [
        ('name_uniq', 'unique(use_case_details)', 'Use case already exist.'),
    ]

    def action_download_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        headers = [
            'Use Case Code', 'Activity Name', 'Use Case Details', 'Complexity Level',
            'Reusable', 'Customization Effort', 'Effective UC Point',
        ]
        
        column_widths = [20, 20, 30, 15, 15, 20, 20, 15]
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFF00', 
            'border': 1
        })

        for col_num, (header, width) in enumerate(zip(headers, column_widths)):
            worksheet.set_column(col_num, col_num, width)
            worksheet.write(0, col_num, header, header_format)

        complexity_level_values = ['simple', 'average', 'complex']
        reusable_values = ['yes', 'no']

        worksheet.data_validation('D2:D1048576', {'validate': 'list', 'source': complexity_level_values})
        worksheet.data_validation('E2:E1048576', {'validate': 'list', 'source': reusable_values})

        workbook.close()
        output.seek(0)
        
        file_data = base64.b64encode(output.read()).decode('utf-8')
        
        attachment_id = self.env['ir.attachment'].create({
            'name': 'use_case_template.xlsx',
            'type': 'binary',
            'datas': file_data,
            'store_fname': 'use_case_template.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment_id.id),
            'target': 'new',
        }


class KwProjectAddUseCaseMaster(models.Model):
    _name = 'kw_project_add_use_case_master'
    _description = 'Manage Use Case'
    _rec_name = 'project_name'

    project_name = fields.Many2one("project.project",string="Project Name",)
    project_manager_name = fields.Many2one("hr.employee",related='project_name.emp_id',string="PM Name",)
    project_id = fields.Char("Project ID/Ref.Code")
    project_short_code = fields.Char('Project Short Code',related='project_name.code')
    domain = fields.Many2one("kw_domain_master")
    use_case_ids = fields.One2many("kw_project_use_case_master",'use_case_id',compute='_compute_use_case_ids',readonly=False)
            
    @api.constrains('project_name')
    def _check_unique_project_name(self):
        for record in self:
            existing_records = self.search([('project_name', '=', record.project_name.id)])
            if len(existing_records) > 1:
                raise ValidationError('Use Cases for this project already exists.')
            
    @api.depends('domain')
    def _compute_use_case_ids(self):
        for record in self:
            if record.domain:
                record.use_case_ids = self.env['kw_project_use_case_master'].search([('domain_name', '=', record.domain.name)]).ids
            else:
                record.use_case_ids = []

class KwDomainMaster(models.Model):
    _name = 'kw_domain_master'
    _description = 'Manage Domains'

    name = fields.Char(string="Domain",)

class KwDComponentMaster(models.Model):
    _name = 'kw_component_master'
    _description = 'Component master'
    _rec_name = 'component'

    component = fields.Char(string="Component",)
    code = fields.Char(string='Code')
class ComponentTypeMaster(models.Model):
    _name = 'kw_component_type_master'
    _description = 'Component Type Master'
    _rec_name = 'component_name'

    component_name = fields.Many2one('kw_component_master',string='Component Name',track_visibility='onchange')
    component_code = fields.Char(string="Component Code",related='component_name.code',store=True,track_visibility='onchange')
    component_amount = fields.Float("Amount",track_visibility='onchange')
    milestone_id = fields.Many2one("kw_project_milestone")



    

       