from odoo import fields, models, api

class File_Tracking_information(models.Model):
    _name = 'file.tracking.information'
    _description = 'file.tracking.information'

    forwarded_by = fields.Many2one('res.users', string='Forwarded by', readonly=True)
    forwarded_date = fields.Char(string = "Forwarded Date", readonly=True)
    forwarded_to_user = fields.Many2one('res.users', string='Forwarded to(User)', readonly=True)
    forwarded_to_dept = fields.Many2one('hr.department',string='Forwarded to(Department)', readonly=True)
    job_pos = fields.Many2one('hr.job', string = "Job position", readonly = True)
    remarks = fields.Text('Remarks')

    create_let_id = fields.Many2one('muk_dms.file', string = "File", invisible = 1)