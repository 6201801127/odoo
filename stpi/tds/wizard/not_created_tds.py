from odoo import api, fields, models,_


class SendTdsReminder(models.TransientModel):
    _name = 'nc.tds.wizard'
    _description = 'ITR Exception Report Wizard'


    branch_id = fields.Many2many('res.branch', string="Branch", store=True, track_visibility='always')
    date_range = fields.Many2one('date.range','Financial Year', track_visibility='always')


    def show_list_nc_tds(self):
        emp_list = []
        employees = self.env['hr.employee'].search([('branch_id', 'in', self.branch_id.ids)])
        declarations = self.env['hr.declaration'].search([('branch_id', 'in', self.branch_id.ids),('date_range', '=', self.date_range.id)])
        for dec in declarations:
            emp_list.append(dec.employee_id)
        for emp in employees:
            if emp not in declarations.employee_id:
                self.env['nc.tds'].create({
                    'employee_id': emp.id,
                    'branch_id': emp.branch_id.id
                })