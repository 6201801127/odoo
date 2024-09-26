from odoo import models, fields, api


class HrDepartmentIn(models.Model):
    _inherit = "hr.department"
    _order = "name asc"
    _rec_name = 'name'

    name = fields.Char(string=u'Department Name', size=100, required=True)
    description = fields.Text(string=u'Description')
    kw_id = fields.Integer(string='Tendrils ID')
    dept_head = fields.Many2one('hr.employee', string="Department head")
    dept_type = fields.Many2one('kw_hr_department_type', string="Type")
    sort_no = fields.Integer()
    code = fields.Char('Code')
    no_of_employee = fields.Integer(compute='_compute_employees', string="Current Number of Employees",
                                    help='Number of employees currently occupying this job position.')

    # @api.constrains('name')
    # def check_name(self):
    #     exists_name = self.env['hr.department'].search([('name', '=', self.name), ('id', '!=', self.id)])
    #     if exists_name:
    #         raise ValueError("This Department name \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(HrDepartmentIn, self).create(vals)
        if record:
            self.env.user.notify_success(message='Department created successfully.')
        else:
            self.env.user.notify_danger(message='Department creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(HrDepartmentIn, self).write(vals)
        if res:
            self.env.user.notify_success(message='Department updated successfully.')
        else:
            self.env.user.notify_danger(message='Department updation failed.')
        return res

    @api.multi
    def _compute_employees(self):
        for record in self:
            if record.dept_type.code:
                domain = [('employement_type', '!=', 5)]
                # print("domain >>>>>>>>>> ", domain, record.id, record.dept_type.code)
                if record.dept_type.code == 'division':
                    record.no_of_employee = self.env['hr.employee'].search_count(domain + [('division', '=', record.id)])
                elif record.dept_type.code == 'section':
                    record.no_of_employee = self.env['hr.employee'].search_count(domain + [('section', '=', record.id)])
                elif record.dept_type.code == 'practice':
                    record.no_of_employee = self.env['hr.employee'].search_count(domain + [('practise', '=', record.id)])
                elif record.dept_type.code == 'department':
                    record.no_of_employee = self.env['hr.employee'].search_count(domain + [('department_id', '=', record.id)])
