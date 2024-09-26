from datetime import datetime,timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime,date

class KwProbationCompletion(models.Model):
    _name           = 'kw_probation_completion'
    _description    = 'Employee probation Completion update'
    _rec_name       = 'empl_id'
    
    
    empl_id = fields.Many2one('hr.employee',string="Employee")
    completion_date = fields.Date(string="Confirmation Date")
    remark_confirm = fields.Text(string="Remark")
    state_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default='draft')
    probation_confirm_status = fields.Selection(string='Confirmation Status',
                                   selection=[('extended', 'Extended'), ('completed', 'Confirmed'),('failed_prob','Failed Probation Confirmation')])
    
    documents = fields.Binary(string=u'Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    
    def confirm_probation(self):
        if self.completion_date:
            self.write({'state_confirm':'confirm'})
            data_update = {'on_probation': False, 'date_of_completed_probation': self.completion_date}
            self.empl_id.sudo().write(data_update)