
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date,datetime

class LearningAndKnowledgeTraining(models.Model):
   
    _name = "lk_training_batch"
    _description = "Internship Batch Create"
    _rec_name = "batch_name"
    _order = "batch_name"

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', default=_default_financial_yr,
                                        required=True)
    batch_stage = fields.Selection([('Draft', 'Draft'), ('Start', 'Start'),('Complete','Complete')],string="Stage",default='Draft')

    batch_name = fields.Char(string="Batch Name")
    start_date = fields.Date(sring = 'Start Date')
    close_date = fields.Date(sring = 'Close Date')
    employee_ids = fields.Many2many('tendrils_internship',string = 'Interns')
    is_complete_internship = fields.Boolean(string = 'Is Complete Internship',default = False)
    internship_id = fields.Many2one('td_internship_schedule',string = 'Internship Id')
    session_count = fields.Integer("Number Of Sessions", compute="_compute_sessions")
    session_bool = fields.Boolean(string = 'Session Bool',default = False)

    
    @api.multi
    def _compute_sessions(self):
        for record in self:
            sessions = self.env['td_internship_schedule'].search_count([('internship_id', '=', record.id)])
            record.session_count = sessions

    @api.multi
    def view_internship_session(self):
        self.ensure_one()
        tree_view_id = self.env.ref('tendrils_internship.td_internship_schedule_list').id
        form_view_id = self.env.ref('tendrils_internship.td_internship_schedule_form').id
        kanban_view_id = self.env.ref('tendrils_internship.td_internship_schedule_kanban').id

        return {
            'name': 'Sessions',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'td_internship_schedule',
            'views': [(kanban_view_id,'kanban'),(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('internship_id', '=', self.id)],
            'context': {'default_internship_id': self.id,},
        }

    def btn_internship_start(self):
        self.write({
            'batch_stage':'Start',
            'session_bool':True
        })

    def btn_internship_complete(self):
        form_view_id = self.env.ref('tendrils_internship.internship_final_doc_upload_form_view').id
        
        return {
            'name': 'Upload Intens Document',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'internship_final_doc_upload',
            'views': [ (form_view_id, 'form')],
            'target': 'new',
            # 'domain': [('internship_id', '=', self.id)],
            # 'context': {'default_internship_id': self.id,},
        }
    

class InternshipDocumentUpload(models.Model):
    _name = "internship_final_doc_upload"
    _description = "Upload Document"

    interns_data_id = fields.Many2many('tendrils_internship', string='Interns')
    # upload_file = fields.Binary(string="Upload Document")

    @api.model
    def default_get(self, fields):
        res = super(InternshipDocumentUpload, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            # Fetch the lk_training_batch records
            training_batches = self.env['lk_training_batch'].browse(active_ids)
            # Collect all employee_ids from these batches
            interns = training_batches.mapped('employee_ids')
            res.update({
                'interns_data_id': [(6, 0, interns.ids)],
            })
        return res


    def upload_documents(self):
        for intern in self.interns_data_id:
            training_batches = self.env['lk_training_batch'].search([('employee_ids', 'in', intern.id)])
            for batch in training_batches:
                if not intern.intern_document_upload:
                    raise ValidationError("Please upload the document.")
                batch.write({
                        'batch_stage':'Complete',
                        'is_complete_internship':True,
                    })
                


        