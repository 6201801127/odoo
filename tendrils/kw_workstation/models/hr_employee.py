from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    issued_system = fields.Selection(string='Computer Allocated',
                                     selection=[('aio', 'AIO'), ('pc', 'Desktop'), ('laptop', 'Laptop')], default='')
    system_location = fields.Selection(string='System Location',
                                       selection=[('office', 'On Premise'), ('home', 'Remote')], default='')

    workstation_id = fields.Many2one('kw_workstation_master', string="WS", compute='_compute_infra',
                                     search='_search_employee_workstation')
    # infrastructure_id = fields.Many2one('kw_workstation_infrastructure',string="WS Infra", related='workstation_id.infrastructure')
    branch_unit_id = fields.Many2one(string="WS Infra", related='workstation_id.branch_unit_id')

    @api.multi
    def _compute_infra(self):
        for record in self:
            work_station = self.env['kw_workstation_master'].sudo().search([('employee_id', 'in', record.id)])
            record.workstation_id = work_station and work_station.id or False
            # record.infrastructure_id  = True

    @api.onchange('issued_system')
    def check_system_type(self):
        for rec in self:
            if rec.issued_system == 'laptop':
                rec.system_location = None

    @api.multi
    def write(self, vals):
        if vals.get('is_wfh') == True or vals.get('is_wfh') == False:
            work_station = self.env['kw_workstation_master'].search([('employee_id', 'in', self.ids)])
            if work_station:
                work_station.write({'is_wfh': vals.get('is_wfh')})

        return super(Employee, self).write(vals)

    @api.multi
    def _search_employee_workstation(self, operator, value):
        query = ''
        if value == 'unallocated':
            query = '''SELECT emp.id
                        FROM hr_employee emp
                        LEFT JOIN kw_workstation_hr_employee_rel ws ON ws.eid = emp.id
                        WHERE ws.wid is null'''
        elif value == 'allocated':
            query = '''
                SELECT emp.id
                FROM hr_employee emp
                LEFT JOIN kw_workstation_hr_employee_rel ws ON ws.eid = emp.id
                WHERE ws.wid is not null
                '''
        elif value == 'double':
            query = '''
                SELECT eid AS id FROM kw_workstation_hr_employee_rel WHERE wid in (
                SELECT wid FROM kw_workstation_hr_employee_rel group by wid HAVING count(id)>1)
                '''
        data = False
        if query != '':
            self._cr.execute(query)
            data = self._cr.fetchall()
        # print(">>>>>>>>>>>>>>>>>>>", data)
        return [('id', 'in', [rec[0] for rec in data])] if data else []
