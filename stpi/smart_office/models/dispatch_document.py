import base64
from datetime import datetime
from odoo import fields, models, api

class DispatchDocumentMode(models.Model):
    _name = 'dispatch.document.mode'
    _description = 'Dispatch Document Mode'

    dispatch_id = fields.Many2one('dispatch.document', string='Dispatch Document')
    dispatch_mode = fields.Selection(
        [('hand_to_hand', 'Hand to Hand'),('email', 'Email'), ('fax', 'Fax'), ('splmess', 'Spl. Messenger'), ('post', 'Post')
         ], string='Dispatch Mode', track_visibility='always')
    enter_mode = fields.Char('Dispatch Details')
    dispatch_number = fields.Char('Dispatch Number')

class DispatchDocument(models.Model):
    _name = 'dispatch.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Dispatch Letter'
    # _rec_name = 'name'

    name = fields.Float('Number')
    # cooespondence_ids = fields.Many2many('muk_dms.file', string='Correspondence', track_visibility='always')
    current_user_id = fields.Many2one('res.users','Created By', track_visibility='always')
    branch_id = fields.Many2one('res.branch', 'Branch', track_visibility='always')
    secondary_employee_ids = fields.Many2many("hr.employee",string="Secondary Owners")
    department_id = fields.Many2one('hr.department', 'Department', track_visibility='always')
    job_id = fields.Many2one('hr.job', 'Job Position', track_visibility='always')

    created_on = fields.Date(string='Date', default = fields.Date.today(), track_visibility='always')
    select_template = fields.Many2one('select.template.html',string="Template",track_visibility='always')
    template_html = fields.Html('Template', track_visibility='always')
    basic_version = fields.Float('Basic Version')
    print_heading = fields.Char('Heading')
    dispatch_mode_ids = fields.One2many('dispatch.document.mode','dispatch_id',string='Dispatch Mode')

    version = fields.Many2one('dispatch.document', string='Version ', track_visibility='always')
    previousversion = fields.Many2one('dispatch.document', string='Previous  Version', track_visibility='always')

    version_str = fields.Char("Version")
    prev_version_str = fields.Char("Previous Version")

    folder_id = fields.Many2one('folder.master', string="File", track_visibility='always')
    part_file_id = fields.Many2one('folder.master', string="Part File", track_visibility='always')
    
    dispatch_mode = fields.Selection(
        [('hand_to_hand', 'Hand to Hand'),('email', 'Email'), ('fax', 'Fax'), ('splmess', 'Spl. Messenger'), ('post', 'Post')
         ], string='Dispatch Mode', track_visibility='always')
    enter_mode = fields.Char('Enter Mode of Dispatch')

    state = fields.Selection([('draft', 'Draft'),
                              ('sent_approval', 'Sent for Approval'),
                              ('approve', 'Approved'),
                              ('obsolete', 'Obsolete'),
                              ('reject', 'Rejected'), 
                              ('dispatched', 'Dispatched')], required=True, default='draft', string='Status', track_visibility='always')
    
    forwarded = fields.Boolean("Forwarded ?")
    approved_by = fields.Many2one("res.users","Approved By")
    approved_on = fields.Datetime("Approved On")
    tracking_ids = fields.One2many('dispatch.letter.tracking','dispatch_id',string="Tracking Info")
    
    @api.multi
    def revise_dispatch_letter(self):
        self.env.user.notify_success("Dispatch Letter Revised Successfully.")

    @api.multi
    def action_send_dispatch_approval(self):
        self.write({'state':'sent_approval',
                    'tracking_ids':[[0,0,{
                    'action_id':self.env.ref('smart_office.dispatch_stage_sent_approval').id,
                    'version':self.prev_version_str,
            }]]
        })
        self.env.user.notify_success("Dispatch letter sent for approval.")

    @api.multi
    def action_open_dispatch_approve_form(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'dispatch.document',
                'view_id': self.env.ref('smart_office.document_dispatch_approve_remark_view').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new',
                'nodestroy': True,
            }

    @api.multi
    def action_open_dispatch_reject_form(self):
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'dispatch.document',
                'view_id': self.env.ref('smart_office.document_dispatch_reject_remark_view').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new',
                'nodestroy': True,
            }
    
    @api.multi
    def action_approve_dispatch_letter(self):
        self.write({'state':'approve',
                    'approved_by':self._uid,
                    'approved_on':datetime.now(),
                    'tracking_ids':[[0,0,{
                    'action_id':self.env.ref('smart_office.dispatch_stage_approved').id,
                    'version':self.version_str,
            }]]
        })
        # create correspondence of dispatch letter
        self.action_create_correspondence()
        self.env.user.notify_success("Dispatch letter approved successfully.")

    @api.multi
    def action_reject_dispatch_letter(self): 
        self.write({'state':'reject',
                    'tracking_ids':[[0,0,{
                    'action_id':self.env.ref('smart_office.dispatch_stage_rejected').id,
                    'version':self.version_str,
                }]]
            })
        self.env.user.notify_success("Dispatch letter rejected successfully.")


    @api.multi
    def button_dispatch(self):
        # self.sudo().action_create_correspondence()
        # start : dispatch letter tracking : dispatched
        self.write({'state':'dispatched',
                    'tracking_ids':[[0,0,{'action_id':self.env.ref('smart_office.dispatch_stage_dispatched').id,
                                        'version':self.version_str
                                        }]]
                    })
        
        all_documents_related_to_corresponding_version = self.sudo().search([('id','!=',self.id),('folder_id', '=', self.folder_id.id),('basic_version', '=', self.basic_version)])
        if all_documents_related_to_corresponding_version:
            all_documents_related_to_corresponding_version.write({'state': 'obsolete'})

    @api.multi
    def action_delete_correspondence(self):
        self.unlink()
        self.env.user.notify_success("Dispatch letter deleted successfully.")

    @api.multi
    def button_edit(self):
        for rec in self:
            last_version = self.sudo().search([('folder_id', '=', self.folder_id.id),('basic_version', '=', self.basic_version)],order="id desc",limit=1)
            split_data = last_version.version_str.split('.')
            new_version = f"{split_data[0]}.{int(split_data[1]) + 1}"

            cout = 0
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            dis_name = self.env['dispatch.document'].sudo().search([('folder_id', '=', self.folder_id.id),('basic_version', '=', self.basic_version)])
            m_name = self.env['dispatch.document'].sudo().search([('folder_id', '=', self.folder_id.id)])
            for ct in m_name:
                cout+=1
            if cout <1:
                name = 1
            else:
                name = rec.name
           
            form_view = self.env.ref('smart_office.document_dispatch_revise_form_view')
            tree_view = self.env.ref('smart_office.dispatch_document_tree_view1')
            value = {
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'dispatch.document',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'nodestroy': True,
                'context': {
                    'default_name': name + 0.001,
                    'default_version_str':new_version,
                    'default_prev_version_str':self.version_str,
                    'default_basic_version': int(rec.name),
                    'default_print_heading': rec.print_heading,
                    'default_previousversion': rec.id,
                    'default_dispatch_mode': rec.dispatch_mode,
                    'default_template_html': rec.template_html,
                    'default_select_template': rec.select_template.id,
                    'default_current_user_id': current_employee.user_id.id,
                    'default_department_id': current_employee.department_id.id,
                    'default_job_id': current_employee.job_id.id,
                    'default_branch_id': current_employee.branch_id.id,
                    'default_created_on': datetime.now().date(),
                    'default_folder_id': rec.folder_id.id,
                    'default_state': 'draft',
                        },
            }
            return value
    
    @api.model
    def create(self, vals):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        if current_employee:
            vals['secondary_employee_ids'] = [[4,current_employee.id]]
            
        record = super(DispatchDocument, self).create(vals)
        # start : create log i.e dispatch letter created
        record.tracking_ids = [[0,0,{
            'action_id':self.env.ref('smart_office.dispatch_stage_created').id,
            'version':record.version_str,
            'remark':'',
            # 'visible_user_ids':[[4,self._uid]]
        }]]
        # end : create log i.e dispatch letter created
        if record.previousversion:
            # create log because it is a revise
            data = {
                'action_id':self.env.ref('smart_office.dispatch_stage_revised').id,
                'version':record.prev_version_str,
                'new_version':record.version_str,
                'new_content':record.template_html,
                'old_content': record.previousversion.template_html
            }
            record.previousversion.tracking_ids = [[0,0,data]]
            # if record.previousversion:
                # data['old_template_id'] = record.previousversion.select_template.id                
            # self.env['dispatch.letter.tracking'].create(data)
        return record

    @api.multi
    def button_obsellete(self):
        self.write({'state': 'obsolete'})

    # @api.multi
    # def action_send_dispatch_approval(self):
    #     # for rec in self:
    #     #     dis_name = self.env['dispatch.document'].sudo().search([('id', '!=', rec.id),('folder_id', '=', rec.folder_id.id),('basic_version', '=', rec.basic_version)])
    #     #     for dd in dis_name:
    #     #         dd.sudo().button_obsellete()
    #     #     rec.write({'state': 'ready_for_dispatched'})
    #     current_version_all_dispatch_letters = self.sudo().search([('folder_id', '=', self.folder_id.id),('basic_version', '=', self.basic_version)])
    #     current_version_all_dispatch_letters.write({'state': 'ready_for_dispatched'})

    @api.multi
    def print_dispatch_document(self):
        return self.env.ref('smart_office.dispatch_document_status_print').report_action(self)

    @api.multi
    def action_create_correspondence(self):
        self.ensure_one()
        # print("inside action_create_correspondence")

        pdf = self.env.ref('smart_office.dispatch_document_status_print').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        directory = self.env['muk_dms.directory'].sudo().search([('name', '=', 'Incoming Files')], limit=1)
        pdf_name = f"Dispatch-{self.folder_id.number.replace('/','-')}-{self.version_str}.pdf"
        # print("pdf name is",pdf_name)
        correspondence = self.env['muk_dms.file'].create({
            'dispatch_id': self.id,
            'name':pdf_name,
            'content': b64_pdf,
            'directory': directory.id,
            'responsible_user_id': self.current_user_id.id,
            'current_owner_id': self.current_user_id.id,
            'last_owner_id': self.current_user_id.id,
            'subject':f"{self.print_heading}-{self.folder_id.folder_name}-{self.version_str}.pdf",
            'attach_to_file_date':datetime.now().date(),
            'attach_to_file_time':datetime.now(),
        })
        self.folder_id.file_ids = [(4, correspondence.id)]

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'reject'})
