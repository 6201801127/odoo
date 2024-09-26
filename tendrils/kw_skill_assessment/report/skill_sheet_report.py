from odoo import models, fields, api
from odoo.http import request


class SkillSheetWizardReportFilter(models.TransientModel):
    _name = 'skill_sheet_report_filter_wizard'
    _description = "Skill Sheet Filter Report Wizard"

    fis_year = fields.Many2one('account.fiscalyear', "Financial Year", required=True)
    quarter = fields.Selection([('q1', 'Q1'), ('q2', 'Q2'), ('q3', 'Q3'), ('q4', 'Q4')],
                               string="Quarter", required=True)

    def get_client_action(self):
        request.session['quarter'] = self.quarter if self.quarter else False
        request.session['start_year'] = self.fis_year.date_start.year if self.fis_year else False
        request.session['end_year'] = self.fis_year.date_stop.year if self.fis_year else False

        return {
            'name': 'Skill Sheet Report',
            'type': 'ir.actions.client',
            'tag': 'skill_sheet_client',
            'target': 'current',
        }

    @api.model
    def get_skill_sheet_data(self):
        m_data = self.env['kw_skill_master'].sudo().search([('active', '=', True)])
        s_data = self.env['kw_skill_type_master'].sudo().search([('active', '=', True)])
        score = self.env['kw_skill_mark_sheet_table'].sudo().search([])
        all_data = {}
        for record in s_data:
            return_data = {}
            skill_data = m_data.filtered(lambda x: x.skill_type.id == record.id)
            for skill in skill_data:
                score_data = {}
                return_data['count'] = len(skill_data)
                return_data[skill.name] = skill.name
                score_records = score.filtered(lambda x: x.skills_id.id == skill.id)
                if score_records:
                    for score in score_records:
                        score_data['Employee Code'] = score.kw_skill_emp_id.employee_id.emp_code
                        score_data['Location'] = score.kw_skill_emp_id.employee_id.job_branch_id.city
                        score_data['Department'] = score.kw_skill_emp_id.employee_id.department_id.name
                        score_data['Section'] = score.kw_skill_emp_id.employee_id.section.name
                        score_data['Designation'] = score.kw_skill_emp_id.employee_id.job_id.name
                        score_data['Grade'] = score.kw_skill_emp_id.employee_id.grade.name
                        score_data['Employee Name'] = score.kw_skill_emp_id.employee_id.name
                        if score.skills_id.id == skill.id:
                            score_data[score.skills_id.name] = score.mark
                        else:
                            score_data[score.skills_id.name] = 'NA'
                else:
                    pass
            if return_data:
                all_data[record.skill_type] = return_data

        template_body_data = []
        quarter = request.session['quarter']
        start_year = request.session['start_year']
        end_year = request.session['end_year']
        if quarter and start_year and end_year:
            q1 = [start_year, 'q1', ['4', '5', '6']]
            q2 = [start_year, 'q2', ['7', '8', '9']]
            q3 = [start_year, 'q3', ['10', '11', '12']]
            q4 = [end_year, 'q4', ['1', '2', '3']]
            record = self.env['kw_skill_sheet'].sudo().search([])
            quarter_rec = {}
            for rec in record:
                if rec.date_.year == q1[0] and quarter == q1[1] and str(rec.date_.month) in q1[2]:
                    quarter_rec[q1[0]] = q1[2]
                elif rec.date_.year == q2[0] and quarter == q2[1] and str(rec.date_.month) in q2[2]:
                    quarter_rec[q2[0]] = q2[2]
                elif rec.date_.year == q3[0] and quarter == q3[1] and str(rec.date_.month) in q3[2]:
                    quarter_rec[q3[0]] = q3[2]
                elif rec.date_.year == q4[0] and quarter == q4[1] and str(rec.date_.month) in q4[2]:
                    quarter_rec[q4[0]] = q4[2]
                else:
                    pass
            if quarter_rec:
                skill_sheet = self.env['kw_skill_sheet'].sudo().search([('state', '=', '2')])
                for rec in skill_sheet:
                    emp_temp_data = {}
                    if rec.date_.year == list(quarter_rec.keys())[0] and str(rec.date_.month) in \
                            quarter_rec[list(quarter_rec.keys())[0]]:
                        emp_temp_data['emp_code'] = rec.code
                        emp_temp_data['location'] = rec.location
                        emp_temp_data['department'] = rec.department_name
                        emp_temp_data['section'] = rec.section
                        emp_temp_data['designation'] = rec.job_name
                        emp_temp_data['grade'] = rec.grade
                        emp_temp_data['emp_name'] = rec.employee_id.name
                        data = self.env['kw_skill_mark_sheet_table'].sudo().search([('kw_skill_emp_id', '=', rec.id)])
                        for recc in all_data.values():
                            for h_skill in recc:
                                if h_skill != 'count':
                                    if data:
                                        if h_skill in data.mapped('skills_id.name'):
                                            value = data.filtered(lambda x: x.mark if x.skills_id.name == h_skill else 0).mark
                                            emp_temp_data[h_skill] = value
                                        else:
                                            emp_temp_data[h_skill] = 0
                                    else:
                                        emp_temp_data[h_skill] = 0
                    template_body_data.append(emp_temp_data)
                    # print(template_body_data, '-------------------------------->>>>>>>>>>>>>>>>>>')
        new_list = list(filter(None, template_body_data))
        # print(new_list)
        return all_data, len(all_data), new_list
