from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import tools
from datetime import datetime , date, timedelta


class TourPassport(models.Model):
    _name = 'kw_tour_passport'
    _description = 'Passport Expiry Reminder'
    _auto = False
    _rec_name = 'name'
    _order = 'name'

    emp_id = fields.Many2one('hr.employee', string="emp")
    name = fields.Char(string="Name")
    emp_code = fields.Char(string=u'Employee Code', size=100)
    job_id = fields.Many2one("hr.job", string="Designation")
    department_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Section")
    practise = fields.Many2one('hr.department', string="Practise")
    job_branch_id = fields.Many2one("kw_res_branch", string="Branch")
    work_email = fields.Char(string="Work Email", size=100)
    mobile_phone = fields.Char(string="Work Phone No", size=18)
    identy_type = fields.Selection(string="Identification Type",
                                   selection=[('1', 'PAN'), ('2', 'Passport'), ('3', 'Driving Licence'),
                                              ('4', 'Voter ID'),
                                              ('5', 'AADHAAR'), ('6', 'Yellow Fever')], required=True)
    doc_number = fields.Char(string="Document Number", required=True, size=100)
    date_of_issue = fields.Date(string="Date of Issue")
    date_of_expiry = fields.Date(string="Date of Expiry")
    uploaded_doc = fields.Binary(string="Document Upload", attachment=True)
    doc_file_name = fields.Char(string="Document Name")
    fever_doc_number = fields.Char(string="Document Number", required=True, size=100)
    fever_date_of_issue = fields.Date(string="Date of Taken")

    def _scheduling_mail_for_passport_expairy(self):
        passport_expiry_emp_list = []
        current_date = datetime.now().date()
        sch_date = current_date + timedelta(days=30)
        emp_recs = self.env['kwemp_identity_docs'].sudo().search(
            [('name', '=', '2'), ("date_of_expiry", '<', sch_date), ('emp_id.active', '=', True)])
        # print("emp_recs > ", emp_recs)
        # return
        if emp_recs:
            for rec in emp_recs:
                # print('active >> ', rec.emp_id, rec.emp_id.active)
                # return
                passport_expiry_emp_list.append({'emp_name': rec.emp_id.name,
                                                 'emp_code': rec.emp_id.emp_code,
                                                 'department': rec.emp_id.department_id.name,
                                                 'pass_num': rec.doc_number,
                                                 'pass_ex': rec.date_of_expiry.strftime('%d-%b-%Y')
                                                 })
            extra_params = {'emp_list2': passport_expiry_emp_list}

            travel_desk_user = self.env.ref('kw_tour.group_kw_tour_travel_desk')
            travel_desk_employees = travel_desk_user.users.mapped('employee_ids') or False
            email_ids = travel_desk_employees and ','.join(travel_desk_employees.mapped('work_email')) or ''

            template_id = self.env.ref('kw_tour.kw_tour_send_email_for_passport_update_template')
            template_id.with_context(to_mail=email_ids, ctx_params=extra_params, emp_list=passport_expiry_emp_list).send_mail(self.id,  notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
        with tour_table AS (
            SELECT row_number() over() AS id,
                    hr.id AS emp_id,
                    hr.name AS name,
                    hr.emp_code AS emp_code,
                    hr.job_id AS job_id,
                    hr.department_id AS department_id,
                    hr.division AS division,
                    hr.section AS section,
                    hr.practise AS practise,
                    hr.job_branch_id AS job_branch_id, 
                    hr.work_email AS work_email,
                    hr.mobile_phone AS mobile_phone,
					(SELECT name1.name from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='2' ) AS identy_type,
					(SELECT name1.doc_number from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='2' ) AS doc_number,
					(SELECT name1.date_of_expiry from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='2' ) AS date_of_expiry,
                    (SELECT name1.date_of_issue from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='2' ) AS date_of_issue,
					(SELECT name1.doc_file_name from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='2' ) AS doc_file_name,
                    (SELECT name1.doc_number from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='6' ) AS fever_doc_number,
                    (SELECT name1.date_of_issue from kwemp_identity_docs AS name1 where hr.id=name1.emp_id and name1.name='6' ) AS fever_date_of_issue
					FROM hr_employee AS hr where hr.active =True
                )
                    SELECT row_number() over() AS id, emp_id,
                            name,
                            emp_code, 
                            job_id, 
                            department_id, 
                            division,
                            section,
                            practise,
                            job_branch_id,
                            work_email,
                            mobile_phone,
                            identy_type,
                            doc_number,
                            date_of_expiry,
                            date_of_issue,
                            doc_file_name,
                            fever_doc_number,
                            fever_date_of_issue
                            
                            FROM tour_table
            )"""

        self.env.cr.execute(query)

    @api.multi
    def call_download_doc(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download_update_doc/{self.emp_id.id}',
            'target': 'new',
        }

        # def update_passport_info(self):
        #     form_view_id = self.env.ref('kw_tour.kw_tour_identity_docs_view_form').id
        #     return {
        #         'name': 'Update Passport',
        #         'type': 'ir.actions.act_window',
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'res_model': 'kw_tour_passport_details_wizard',
        #         'views': [(form_view_id, 'form')],
        #         'target': 'new',
        #         'context': {'default_emp_id':self.id},        
        #     }   
        # def update_passport_info(self):
        #     pass

    class TourPassport(models.TransientModel):
        _name = 'kw_tour_passport_details_wizard'
        _description = 'Tour passport update record'

        name = fields.Selection(string="Identification Type",
                                selection=[('2', 'Passport'), ('6', 'Yellow Fever')], default='2', required=True)
        doc_number = fields.Char(string="Document Number", required=True, size=100)
        date_of_issue = fields.Date(string="Date of Issue")
        date_of_expiry = fields.Date(string="Date of Expiry")
        renewal_sts = fields.Boolean("Renewal Applied", default=False)

        uploaded_doc = fields.Binary(string="Document Upload", attachment=True)
        doc_file_name = fields.Char(string="Document Name")

        # emp_id = fields.Many2one('hr.employee',string="Employee ID")
        employee_id = fields.Many2one('kw_tour_passport', string="Employee",
                                      default=lambda self: self._context.get('current_record'))

        def action_button_view_form(self):
            records = self.env['kwemp_identity_docs'].sudo().search(
                [('emp_id', '=', self.employee_id.emp_id.id), ('name', '=', self.name)])
            # records = self.employee_id.emp_id.id ('name', '=', self.name)])
            records2 = self.env['kwemp_identity_docs']

            if records:
                records.write({
                    'doc_number': self.doc_number,
                    'date_of_expiry': self.date_of_expiry,
                    'date_of_issue': self.date_of_issue,
                    'renewal_sts': self.renewal_sts if self.renewal_sts else False,
                    'uploaded_doc': self.uploaded_doc if self.uploaded_doc else False,
                })
            else:
                records2.create({
                    'emp_id': self.employee_id.emp_id.id,
                    'name': self.name,
                    'doc_number': self.doc_number,
                    'date_of_expiry': self.date_of_expiry,
                    'date_of_issue': self.date_of_issue,
                    'renewal_sts': self.renewal_sts if self.renewal_sts else False,
                    'uploaded_doc': self.uploaded_doc if self.uploaded_doc else False,
                })

            profile_id = self.env['kw_emp_profile'].search([('emp_id', '=', self.employee_id.emp_id.id)]).id
            profile_records = self.env['kw_emp_profile_identity_docs'].sudo().search(
                [('emp_id', '=', profile_id), ('name', '=', self.name)])
            profile_records2 = self.env['kw_emp_profile_identity_docs']
            if records:
                profile_records.write({
                    'doc_number': self.doc_number,
                    'date_of_expiry': self.date_of_expiry,
                    'date_of_issue': self.date_of_issue,
                    'renewal_sts': self.renewal_sts if self.renewal_sts else False,
                    'uploaded_doc': self.uploaded_doc if self.uploaded_doc else False,
                })
            else:
                profile_records2.create({
                    'emp_id': profile_id,
                    'name': self.name,
                    'doc_number': self.doc_number,
                    'date_of_expiry': self.date_of_expiry,
                    'date_of_issue': self.date_of_issue,
                    'renewal_sts': self.renewal_sts if self.renewal_sts else False,
                    'uploaded_doc': self.uploaded_doc if self.uploaded_doc else False,
                })

            self.env.user.notify_success(message=f"{'Passport' if self.name == '2' else 'Yellow Fever'} details updated successfully.")
