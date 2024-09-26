# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError

class UserAppPermission(models.TransientModel):
    
    _name           = 'kw_bulk_user_app_permission'
    _description    = 'Bulk User App Permission'


    
    application_id = fields.Many2one(
        string='Application',
        comodel_name='ir.module.category',
        
        required=True
        
    )

    group_id    = fields.Many2one(
        string='Group',
        comodel_name='res.groups',
        required=True
    )
    
    employee_ids = fields.Many2many(
        string='Employee',
        comodel_name='hr.employee',
        domain="[('user_id', '!=', False)]",
        required=True
    )
    

    @api.onchange('application_id')
    def _onchange_field(self):

        self.group_id   = False

        return {'domain': {'group_id': [('category_id', '=', self.application_id.id)], }}

    
    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        
        result = super(UserAppPermission, self).create(values)

        if result.employee_ids:
            user_ids    = [[4,employee.user_id.id,False] for employee in result.employee_ids if employee.user_id ]

           
            #add the group to the inherited group list
            if result.group_id :
                
                result.group_id.write({'users': user_ids})   


    
        return result



    
    
    


