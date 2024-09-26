from odoo import fields, models, api

class FolderTrackingInformation(models.Model):
    _name = 'folder.tracking.information'
    _description = 'folder.tracking.information'

    forwarded_by = fields.Many2one('res.users', string='Forwarded by', readonly=True)
    forwarded_date = fields.Char(string = "Forwarded Date", readonly=True)
    forwarded_to_user = fields.Many2one('res.users', string='Forwarded to(User)', readonly=True)
    forwarded_to_dept = fields.Many2one('hr.department',string='Forwarded to(Department)', readonly=True)
    job_pos = fields.Many2one('hr.job', string = "Job position", readonly = True)
    remarks = fields.Text('Remarks')

    create_let_id = fields.Many2one('folder.master', string = "Folder", invisible = 1)