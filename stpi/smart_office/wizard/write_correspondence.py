from odoo import fields, models, api
from datetime import datetime

class AddReference(models.TransientModel):
    _name = 'write.correspondence'
    _description = 'Add Dispatch Letter'

    print_heading = fields.Char('Heading',required=True)
    # cooespondence_ids = fields.Many2many('muk_dms.file', string='Correspondence')
    
    current_user_id = fields.Many2one('res.users','Created By')
    
    branch_id = fields.Many2one('res.branch', 'Center')
    department_id = fields.Many2one('hr.department', 'Department')
    
    created_on = fields.Date(string='Date', default = fields.Date.today())

    select_template = fields.Many2one('select.template.html','Template')

    template_html = fields.Html('Template')
    
    version = fields.Many2one('dispatch.document', string='Version')
    previousversion = fields.Many2one('dispatch.document', string = 'Previous Version')
    
    folder_id = fields.Many2one('folder.master', string="Select File")
    
    dispatch_mode = fields.Selection(
        [('hand_to_hand', 'Hand to Hand'),('email', 'Email'), ('fax', 'Fax'), ('splmess', 'Spl. Messenger'), ('post', 'Post')
         ], string='Dispatch Mode', track_visibility='always')

    @api.onchange('select_template')
    def get_template(self):
        if self.select_template:
            self.template_html = self.select_template.template
            
    @api.multi
    def confirm_button(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        current_user = self.env.user
        
        dis_name = self.env['dispatch.document'].sudo().search([('folder_id', '=', self.folder_id.id)],order="name desc",limit=1)
        max_version = dis_name.name if dis_name else 0

        name = int(max_version) + 1

        dispatch_letter = self.env['dispatch.document'].create({
            'name': name,
            'version_str':str(float(name)),
            'print_heading': self.print_heading,
            'basic_version': name,
            'dispatch_mode': self.dispatch_mode,
            'template_html': self.template_html,
            'select_template': self.select_template.id,
            'current_user_id': current_employee.user_id.id,
            'department_id': current_employee.department_id.id,
            'job_id': current_employee.job_id.id,
            'branch_id': current_user.default_branch_id.id,
            'created_on': datetime.now().date(),
            'folder_id': self.folder_id.id,
            'state': 'draft',
        })
       
        dispatch_letter.version = dispatch_letter.id
        
        prev_dispatch_letter = self.env['dispatch.document'].sudo().search([('folder_id', '=', self.folder_id.id),('name', '=', name - 1)], limit=1)
        dispatch_letter.previousversion = prev_dispatch_letter.id if prev_dispatch_letter else dispatch_letter.id
        