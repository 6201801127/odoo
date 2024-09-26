import ast
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    # dms_policy_doc_settings = fields.Boolean(
    #     string="Show Access Groups on User Form",
    #     help="Allows users to edit the access groups of a directory.")
    
    dms_policy_doc_folder   = fields.Many2one('kw_dms.directory',ondelete='restrict', 
            string="Policy Doc Workspace",
        help="Centralize files attached to policy documents")
    # dms_training_material_folder = fields.Many2one('kw_dms.directory', ondelete='restrict',
    #                                         string="Training Material Workspace",
    #                                         help="Centralize files attached to policy documents")

    # dms_policy_doc_tags     = fields.Many2many('kw_dms.tag',default='',
    #     string="Policy Doc Tags",
    #     help="Tags to identify the documents.")

    dms_digilock_hr_employee_folder = fields.Many2one('kw_dms.directory',ondelete='restrict',
        string="DigiLocker Workspace",
        help="Centralize files attached to employee uploaded documents")

    
    # dms_hr_employee_tags     = fields.Many2many('kw_dms.tag',
    #     string="Employee Doc Tags",
    #     help="Tags to identify the documents.")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def set_values(self):
        res     = super(ResConfigSettings, self).set_values()
        param   = self.env['ir.config_parameter'].sudo()

        param.set_param('kw_dms.policy_doc_folder', self.dms_policy_doc_folder.id or False)
        param.set_param('kw_dms.digilock_hr_employee_folder',self.dms_digilock_hr_employee_folder.id or False)
        # param.set_param('kw_dms.training_material_folder',self.dms_training_material_folder.id or False)

        # param.set_param('kw_dms.policy_doc_tags', [(6,0,self.dms_policy_doc_tags.ids)])
        
        return res

    @api.model
    def get_values(self):
        res     = super(ResConfigSettings, self).get_values()
        params  = self.env['ir.config_parameter'].sudo()

        # policy_doc_tags = params.get_param('kw_dms.policy_doc_tags')
        res.update(
             dms_policy_doc_folder          = int(params.get_param('kw_dms.policy_doc_folder')),
             dms_digilock_hr_employee_folder= int(params.get_param('kw_dms.digilock_hr_employee_folder')),
            # dms_training_material_folder    = int(params.get_param('kw_dms.training_material_folder')),

            # dms_policy_doc_tags=params.get_param('kw_dms.policy_doc_tags', default=""), ast.literal_eval(
            # dms_policy_doc_tags=ast.literal_eval(policy_doc_tags),
        )

        return res

