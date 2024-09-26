from odoo import fields, models, api
from datetime import datetime

class AddReference(models.TransientModel):
    _name = 'add.reference.file'
    _description = 'Add Reference'

    correspondence_ids = fields.Many2many('muk_dms.file', string='Select Correspondences')
    description = fields.Text("Remark")
    folder_id = fields.Many2one('folder.master', string="File")

    @api.multi
    def confirm_button(self):
        # current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for corres in self.correspondence_ids:
            corres.write({'folder_id': self.folder_id.id,
                          'attach_to_file_date' : datetime.now().date(),
                          'attach_to_file_time' : datetime.now(),
                        })

            # self.env['file.tracker.report'].create({
            #     'name': str(corres.name),
            #     'type': 'Correspondence',
            #     'assigned_by': str(current_employee.user_id.name),
            #     'assigned_by_dept': str(current_employee.department_id.name),
            #     'assigned_by_jobpos': str(current_employee.job_id.name),
            #     'assigned_by_branch': str(current_employee.branch_id.name),
            #     'assigned_date': datetime.now().date(),
            #     'action_taken': 'assigned_to_file',
            #     'remarks': self.description,
            #     'details': "Correspondence attached to file {}".format(self.folder_id.folder_name)
            # })

            self.env['smart_office.correspondence.tracking'].create({
                'correspondence_id': corres.id,
                'action_stage_id': self.env.ref('smart_office.corres_stage_attach_file_from_create_file').id,
                'remark': self.description
            })
        self.env.user.notify_success("Correspondence(s) attached successfully.")
        return {'type': 'ir.actions.act_window_close'}
