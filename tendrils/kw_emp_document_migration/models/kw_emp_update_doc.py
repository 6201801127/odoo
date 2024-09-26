#*******************************************************************************************************************
#  File Name             :   kw_emp_update_doc.py
#  Description           :   These models are used to Update Employee Workexperience,Education details,Identification details document. 
#  Created by            :   Vishal kumar
#  Created On            :   12-04-2021
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************


from odoo import models, fields, api
import requests, os, zipfile, base64, shutil, json

class kw_emp_update_workexperience(models.Model):
    _name = 'kw_emp_update_workexperience'
    _description = 'Update Employee workexperience.'
    # _order = 'id desc'

    doc_id = fields.Many2one('kwemp_work_experience',string="Id")
    url = fields.Char(string="Url", attachment=True)
    status = fields.Boolean(string='Update Status', default=False)

    @api.multi
    def call_update_doc(self,val):
        emp_doc = False
        if val:
            url = val.url
            emp_doc = base64.b64encode(requests.get(val.url).content) if val.url else False
            file_name = ' '.join(url.split("/")[-1:])
            if emp_doc:
                val.status = True
                val.doc_id.sudo().write({
                    'uploaded_doc': emp_doc,
                    'doc_file_name': file_name.split("_")[-1:][0],
                })
                # print("Employee Document Updated..................")

    @api.multi
    def _record_limit(self):
        emp_cc_mail_list = []
        param = self.env['ir.config_parameter'].sudo()
        limit_val = param.get_param('kw_emp_document_migration.limit_value')
        if limit_val and limit_val != 0:
            return int(limit_val)

    @api.model
    def _update_employee_document(self):
        limit=self._record_limit()
        work_exp_ids = self.env['kw_emp_update_workexperience'].search([('status','=',False)],limit= limit if limit else 10)
        educational_ids = self.env['kw_emp_update_educational_details'].sudo().search([('status','=',False)],limit= limit if limit else 10)
        identification_ids = self.env['kw_emp_update_identification_details'].sudo().search([('status','=',False)],limit= limit if limit else 10)
        if work_exp_ids:
            for val in work_exp_ids:
                self.call_update_doc(val)
        if educational_ids:
            for val in educational_ids:
                self.call_update_doc(val)
        if identification_ids:
            for val in identification_ids:
                self.call_update_doc(val)

class kw_emp_update_educational_details(models.Model):
    _name = 'kw_emp_update_educational_details'
    _description = 'Update Employee educational details.'
    # _order = 'id desc'

    doc_id = fields.Many2one('kwemp_educational_qualification',string="Id")
    url = fields.Char(string="Url", attachment=True)
    status = fields.Boolean(string='Update Status', default=False)

class kw_emp_update_identification_details(models.Model):
    _name = 'kw_emp_update_identification_details'
    _description = 'Update Employee identification details.'
    # _order = 'id desc'

    doc_id = fields.Many2one('kwemp_identity_docs',string="Id")
    url = fields.Char(string="Url", attachment=True)
    status = fields.Boolean(string='Update Status', default=False)
