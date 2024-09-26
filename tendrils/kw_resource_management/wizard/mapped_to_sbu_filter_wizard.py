from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MappedToSBUFilter(models.TransientModel):
    _name           = 'mapped_to_sbu_wizard'
    _description    = "Mapped to SBU Filter Wizard"
    
    emp_role = fields.Many2one('kwmaster_role_name',string='Employee Role',default=lambda self: self.env['kwmaster_role_name'].search([('code', '=', 'S')]))
    emp_category = fields.Many2one('kwmaster_category_name',string='Employee Category')
    employement_type = fields.Many2one('kwemp_employment_type',string='Employment Type')

    @api.onchange('emp_role')
    def _get_categories(self):
        role_id = self.emp_role.id
        self.emp_category = False
        return {'domain': {'emp_category': [('role_ids', '=', role_id),('kw_id','in',[3,7,1,19])], }}

    @api.multi
    def button_mapped_employees_filter(self):
        tree_view_id = self.env.ref('kw_resource_management.sbu_resource_mapping_tree').id
        domain = []
        if self.emp_role:
            domain = domain + [('emp_role','=',self.emp_role.id),]
        if self.emp_category:
            domain += [('emp_category','=',self.emp_category.id),]
        if self.employement_type:
            domain += [('employement_type','=',self.employement_type.id),]

        # print(domain)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Mapping Employees',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'sbu_resource_mapping',
            'target': 'main',
            'domain': domain
        }
        return action