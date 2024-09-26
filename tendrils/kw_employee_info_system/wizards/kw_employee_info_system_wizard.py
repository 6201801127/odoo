from odoo import api,fields, models,_

class kw_employee_info_system_wizard(models.TransientModel):

    _name = 'kw_employee_info_system_wizard'
    _description = 'Employee Information'


    select_by = fields.Selection([
        ('existing', 'Existing'),
        ('ex', 'EX'),
    ], string="Employee",default='existing')
    department_ids = fields.Many2many('hr.department', 'department_info_rel', 'info_id', 'dept_id',string="Department")
    section_id = fields.Many2many('hr.department', 'section_info_rel', 'info_id', 'section_id', string="Practice")
    division_id = fields.Many2many('hr.department', 'division_info_rel', 'info_id', 'div_id', string="Division")
    practise_id = fields.Many2many('hr.department', 'practise_info_rel', 'info_id', 'practise_id', string='Section')
    location_ids = fields.Many2many('kw_res_branch', 'location_info_rel', 'info_id', 'location_id',string="Location")
    employee_ids = fields.Many2many('hr.employee','employee_info_rel', 'info_id', 'employee_id',string="Selection Of Employee")


    @api.onchange('department_ids')
    def onchange_department(self):
        
        dept_child = self.mapped("department_ids.child_ids")
        self.division_id &= dept_child
        return {'domain': {'division': [('id', 'in', dept_child.ids)]}}

    @api.onchange('division_id')
    def onchange_division(self):
        
        division_child = self.mapped("division_id")
        self.section_id &= division_child
        return {'domain': {'section': [('id', 'in', division_child.ids)]}}
        
    @api.onchange('section_id')
    def onchange_section(self):
        section_child = self.mapped("section_id.child_ids")
        self.practise_id &= section_child
        return {'domain': {'practise_id': [('id', 'in', section_child.ids)]}}

    def view_page(self):
        if self.select_by:
            domain = []
            if self.select_by == 'existing':
                domain +=[('active','=',True)]
            else:
                domain +=[('active','=',False)]
            tree_view_id = self.env.ref('kw_employee_info_system.kw_employee_info_system_hr_employee_tree').id
            if self.location_ids:
                domain += [('job_branch_id','in',self.location_ids.ids)]
            if self.department_ids:
                domain += [('department_id','in',self.department_ids.ids)]
            if self.section_id:
                domain += [('section','in',self.section_id.ids)]    
            if self.division_id:
                domain += [('division','in',self.division_id.ids)]
            if self.practise_id:
                domain += [('practise','in',self.practise_id.ids)]
            if self.employee_ids:
                domain += [('id','in',self.employee_ids.ids)]              
            # print(domain)
            return {
                   
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'res_model': 'hr.employee',
                    'name': 'Employee Info',
                    'domain':domain,
                    'target': 'main',
                }
 