import base64
from odoo import fields, models, api

class EditDispatchLetter(models.TransientModel):
    _name = 'edit.doc.dispatch'
    _description = 'Edit Dispatch Letter'

    template_html = fields.Html('Template')
    doc_dispatch = fields.Many2one('dispatch.document', string='Document Dispatch')
    select_template = fields.Many2one('select.template.html',string="Template",related="doc_dispatch.select_template")
    # cooespondence_ids = fields.Many2many('muk_dms.file', string='Correspondence',related="doc_dispatch.cooespondence_ids")
    current_user_id = fields.Many2one('res.users','Created By',related="doc_dispatch.current_user_id")
    branch_id = fields.Many2one('res.branch', 'Branch',related="doc_dispatch.branch_id")
    department_id = fields.Many2one('hr.department', 'Department',related="doc_dispatch.department_id")
    job_id = fields.Many2one('hr.job', 'Job Position',related="doc_dispatch.job_id")

    secondary_employee_ids = fields.Many2many("hr.employee",string="Secondary Owners",related="doc_dispatch.secondary_employee_ids")
    created_on = fields.Date(string='Date',related="doc_dispatch.created_on")
    print_heading = fields.Char('Heading',related="doc_dispatch.print_heading")
    previousversion = fields.Many2one('dispatch.document', string='Previous  Version',related="doc_dispatch.previousversion")
    folder_id = fields.Many2one('folder.master', string="File",related="doc_dispatch.folder_id")

    # @api.onchange('select_template')
    # def get_template(self):
    #     if self.select_template:
    #         self.template_html = self.select_template.template

    @api.multi
    def confirm_button(self):
        # print("edit confirm")
        old_content = self.doc_dispatch.template_html

        self.doc_dispatch.write({
            # 'select_template': self.select_template.id,
            'template_html': self.template_html,
            'tracking_ids':[[0,0,{
            'action_id':self.env.ref('smart_office.dispatch_stage_edited').id,
            'version':self.doc_dispatch.version_str,
            'old_content':old_content,
            'new_content':self.template_html
            }]]
        })
       