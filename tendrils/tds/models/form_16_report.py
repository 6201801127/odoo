from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from odoo.addons import decimal_precision as dp
import math
from math import floor,ceil
import os
import base64
import zipfile
import tempfile

class form_16_report(models.Model):
    _name = 'form_16_report'
    _description = 'Form 16 Report'
    _auto = False


    employee_id = fields.Many2one("hr.employee")
    date_range = fields.Many2one('account.fiscalyear',string='Financial Year')
    tax_regime=fields.Selection([('new_regime', 'New Regime'),('old_regime', 'Old Regime')], required=True, default='new_regime',
                             string='Tax Regime', track_visibility="alaways")
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num', track_visibility="always")
    name = fields.Char(related='employee_id.name')
    emp_code = fields.Char(related='employee_id.emp_code')

    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            for record in rec.employee_id.identification_ids:
                if record.name == '1':
                    rec.pan_number = record.doc_number
    
    def action_download_form16(self):
        doc_folder = self.env['ir.config_parameter'].sudo().get_param('form16_pan_folder_url')
        financial_year = self.date_range.name
        financial_year_folder = os.path.join(doc_folder, financial_year)
        if not os.path.exists(financial_year_folder):
            raise ValidationError('Form16 Not Available.')
        pdf_files = [file for file in os.listdir(financial_year_folder) if file.startswith(f'{self.pan_number}')]

        pdf_paths = [os.path.join(financial_year_folder, file) for file in pdf_files]

        zip_file_name = f'{self.pan_number}_Form16.zip'
        zip_file_path = os.path.join(tempfile.gettempdir(), zip_file_name)
        zip_file_empty = True

        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            for path in pdf_paths:
                if os.path.isfile(path):
                    zip_file.write(path, os.path.basename(path))
                    zip_file_empty = False

        if zip_file_empty:
            os.unlink(zip_file_path)
            raise ValidationError('Form16 Not Available.')

        with open(zip_file_path, 'rb') as file:
            zip_data = file.read()

        transient_model = self.env['download_form16_transient_model'].create({
            'pdf_file': base64.b64encode(zip_data),
            'file_name': zip_file_name,
        })

        url = "/web/content/{model}/{id}/pdf_file/{file_name}?download=true".format(
            model='download_form16_transient_model',
            id=transient_model.id,
            file_name=transient_model.file_name
        )
        os.unlink(zip_file_path)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as(
        select row_number() over() as id,	
		tds.employee_id as employee_id,
        tds.date_range as date_range,
        tds.tax_regime as tax_regime from hr_declaration as tds where state = 'approved'
        )""" % (self._table))
