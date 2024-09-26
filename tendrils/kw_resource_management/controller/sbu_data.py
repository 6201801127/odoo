import re
from odoo import http
from odoo.http import request, json
from werkzeug.wrappers import Response
import werkzeug


class SbuData(http.Controller):
    @http.route('/kwantify/sbudata', methods=['POST'], type="json", auth="public", csrf=False)
    def month_year_resource_data(self, **kwargs):
        request.env.cr.execute(f'''select 
                                        salary_confirm_year as INT_YEAR,
                                        salary_confirmation_month as INT_MONTH,
                                        emp.sbu_master_id as INT_SBU,
                                        hj.name as VCH_DES,
                                        emp.name as NVCH_NAME,
                                        emp.kw_id as kw_id,
                                        emp.emp_code as emp_code
                                        
                                        from hr_payslip hp
                                        join hr_employee emp on emp.id = hp.employee_id
                                        join hr_job hj on hj.id = emp.job_id
                                        
                                        where emp.sbu_type='sbu' and hp.state='done' and hj.kw_id in (355,454,238,78,241,135,252,191,448)
                                        group by salary_confirmation_month,
                                        salary_confirm_year,
                                        emp.sbu_master_id,
                                        emp.job_id,
                                        hj.name,
                                        emp.name,
                                        emp.kw_id,
                                        emp.emp_code
                                       ''')

        sbu_data = request.env.cr.dictfetchall()
        return sbu_data

    @http.route('/monthly/ctc-data', methods=['POST'], type="json", auth="public", csrf=False)
    def getMonthlyCtcData(self, **kwargs):
        request.env.cr.execute(f"""select salary_confirmation_month as INT_MONTH,
                                        salary_confirm_year as INT_YEAR,
                                        emp.sbu_master_id as INT_SBU,
                                        sum(hpl.amount) as DEC_CTC_AMT
                                        
                                        from hr_payslip hp 
                                        
                                        join hr_employee emp on emp.id = hp.employee_id
                                        join hr_payslip_line hpl on hpl.slip_id = hp.id
                                        join hr_job hj on hj.id = emp.job_id
                                        
                                        where hp.state='done' and hpl.code='CTC' and emp.sbu_type='sbu' and hj.kw_id in (355,454,238,78,241,135,252,191,448)
                                        group by salary_confirmation_month,salary_confirm_year,emp.sbu_master_id,hp.state
                                        
                                        order by salary_confirmation_month,salary_confirm_year,sum(hpl.amount)""")
        data = request.env.cr.dictfetchall()
        return data

    @http.route('/employee-skill-expertise', auth='user', type='http', website=True, csrf=False)
    def all_emp_skill_expertise_report(self, **args):
        if request.env.user.employee_ids:
            employee_id = request.env.user.employee_ids[0]
            skills = request.env['kw_skill_master'].sudo().search([('skill_type','=','Technical')])
            # ('name', 'not in', ['Other', 'Others'])
            others = skills.filtered(lambda x: x.name in ['Other', 'Others'])
            skills = skills.filtered(lambda x: x.name not in ['Other', 'Others'])
            return http.request.render('kw_resource_management.kw_all_emp_skill_expertise',
                                       {'emp_name': employee_id.name,
                                        'skills': skills,
                                        'others': others,
                                        })
        else:
            # print('skip >>>>>>>>>>>>>>>>>>>> ')
            http.request.session['skip_skill'] = True
            return request.redirect('/web', )

    @http.route('/employee-skill-expertise-submit', auth='user', website=True, csrf=False)
    def all_emp_skill_expertise_report_submit(self, **args):
        emp_rec = request.env.user.employee_ids
        employee_id = request.env['kw_employee_skill_expertise'].sudo().search(
            [('emp_id', '=', emp_rec.id), ('is_submitted', '=', True)])
        if not employee_id:
            # skills = request.env['kw_skill_master'].sudo().search([])
            employee_id = emp_rec
            primary = args['txtskil1']
            primary_id = re.sub(r'\D', '', primary)
            # record = skills.filtered(lambda x: x.id == primary_id)

            secondary = args['txtskil2']
            secondary_id = re.sub(r'\D', '', secondary)
            # record2 = skills.filtered(lambda x: x.id == secondary_id)

            tertiary = args['txtskil3']
            tertiary_id = re.sub(r'\D', '', tertiary)
            # record3 = skills.filtered(lambda x: x.id == tertiary_id)

            request.env['kw_employee_skill_expertise'].sudo().create(
                {'emp_id': employee_id.id,
                 'is_submitted': True,
                 'reopen_survey': False,
                 'primary_skill': '' if not args['txtarea1'] else args['txtarea1'],
                 'primary_skill_id': primary_id,
                 'secondary_skill': '' if not args['txtarea2'] else args['txtarea2'],
                 'secondary_skill_id': secondary_id,
                 'tertiary_skill': '' if not args['txtarea3'] else args['txtarea3'],
                 'tertiary_skill_id': tertiary_id,
                 })

            return http.request.render("kw_resource_management.skill_expertise_submission_template")
        else:
            employee_skill_id = request.env['kw_employee_skill_expertise'].sudo().search(
                    [('emp_id', '=', emp_rec.id), ('is_submitted', '=', True)])
            if employee_id:
                employee_id = emp_rec
                primary = args['txtskil1']
                primary_id = re.sub(r'\D', '', primary)

                secondary = args['txtskil2']
                secondary_id = re.sub(r'\D', '', secondary)

                tertiary = args['txtskil3']
                tertiary_id = re.sub(r'\D', '', tertiary)
                employee_skill_id.write({'reopen_survey': False,
                                    'primary_skill': '' if not args['txtarea1'] else args['txtarea1'],
                                    'primary_skill_id': primary_id,
                                    'secondary_skill': '' if not args['txtarea2'] else args['txtarea2'],
                                    'secondary_skill_id': secondary_id,
                                    'tertiary_skill': '' if not args['txtarea3'] else args['txtarea3'],
                                    'tertiary_skill_id': tertiary_id,
                                   })
            http.request.session['skip_skill'] = True
            return request.redirect('/web', )

    @http.route('/cancel-skill-details', auth='public', website=True, csrf=False)
    def all_emp_skill_expertise_report_cancel(self, **args):
        return request.redirect('/web', )
