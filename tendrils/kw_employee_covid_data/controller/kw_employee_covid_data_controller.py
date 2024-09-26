
import werkzeug
import base64
from odoo import http, api
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError

class EmployeeCovidData(http.Controller):


    @http.route('/employee-covid-data', auth='public', website=True, csrf=False)
    def employee_covid_data(self, **kw):
        if not request.env.user.employee_ids:
            return werkzeug.utils.redirect('/web')

        record = request.env['kw_employee_covid_data'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id)])

        # render only employee when don't have any record!
        if not record:
            return request.render("kw_employee_covid_data.kw_employee_covid_data_web_template")
        else:
            return werkzeug.utils.redirect('/web')


    """ 1) Creating covid record on submit 
        2) Rendering to thankyou page 
    """
    @http.route('/employee-covid-data-submit/', auth='public', website=True, csrf=False)
    def employee_covid_data_submit(self, **kw):
        if kw:
            record = request.env['kw_employee_covid_data'].sudo()
            doc1 = base64.encodestring(kw['dose_1_document'].read())
            doc2 = base64.encodestring(kw['dose_2_document'].read())
            data = {
                'employee_id':request.env.user.employee_ids.id,
                'dose':kw['dose'],
            }
            if kw['date']:
                data['date'] = kw['date']
            if kw['due_date']:
                data['due_date'] = kw['due_date']
            if kw['remark']:
                data['remark'] = kw['remark']
            if kw['dose_1_document']:
                data['dose_1_document'] = doc1
                data['dose_1_file_name'] = str(kw['dose_1_document'])[15:-21].strip("'") if "'" in str(kw['dose_1_document'])[15:-21] else str(kw['dose_1_document'])[15:-21]
            if kw['dose_2_document']:
                data['dose_2_document'] = doc2
                data['dose_2_file_name'] = str(kw['dose_2_document'])[15:-21].strip("'") if "'" in str(kw['dose_2_document'])[15:-21] else str(kw['dose_2_document'])[15:-21]
            record.create(data)
            return http.request.render("kw_employee_covid_data.kw_employee_covid_data_submission_template")
        else:
            return http.request.redirect('/web')
        
            

