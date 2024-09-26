from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hq_workstation  = fields.Boolean(string="WS", compute='_compute_infra',search='_search_employee_hq_office')
    camp_workstation = fields.Boolean(string="WS", compute='_compute_infra',search='_search_employee_camp_office')

    @api.multi
    def _compute_infra(self):
        pass

    @api.multi
    def _search_employee_hq_office(self, operator, value):
        query = '''
            SELECT emp.id
            FROM hr_employee emp
            LEFT JOIN kw_workstation_hr_employee_rel ws ON ws.eid = emp.id
            left join hr_employee_workstation_mis_report res on res.emp_id = emp.id
            left join kw_res_branch_unit br on br.id = ws_branch_unit_id
            WHERE ws.wid is not null and br.code = 'hq'
            '''
        data = False
        if query != '':
            self._cr.execute(query)
            data = self._cr.fetchall()
        # print(">>>>>>>>>>>>>>>>>>>", data)
        return [('id', 'in', [rec[0] for rec in data])] if data else []

    @api.multi
    def _search_employee_camp_office(self, operator, value):
        query = '''
            SELECT emp.id
            FROM hr_employee emp
            LEFT JOIN kw_workstation_hr_employee_rel ws ON ws.eid = emp.id
            left join hr_employee_workstation_mis_report res on res.emp_id = emp.id
            left join kw_res_branch_unit br on br.id = ws_branch_unit_id
            WHERE ws.wid is not null and br.code = 'camp-office'
            '''
        data = False
        if query != '':
            self._cr.execute(query)
            data = self._cr.fetchall()
        # print(">>>>>>>>>>>>>>>>>>>", data)
        return [('id', 'in', [rec[0] for rec in data])] if data else []