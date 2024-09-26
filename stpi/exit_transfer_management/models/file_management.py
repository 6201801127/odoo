from odoo import models, fields, api


# File management
class CorrespondenceExitManagement(models.Model):
    _name = "correspondence.exit.management"
    _description = "Correspondence Exit Management"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    correspondence_id = fields.Many2one('muk_dms.file', string='Correspondence')
    letter_no = fields.Char(string="Letter Number")
    file_assign_id = fields.Many2one('folder.master', string="File Assigned")
    transfer = fields.Boolean('Transfer')

    def correspondence_forward(self):
        value = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'file.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_defid': self.correspondence_id.id
            },
        }
        me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.env['exit.management.report'].sudo().create({
            "exit_transfer_id": self.exit_transfer_id.id,
            "employee_id": self.exit_transfer_id.employee_id.id,
            "exit_type": self.exit_transfer_id.exit_type,
            "module": 'Correspondence Forwarded',
            "module_id": str(self.letter_no),
            "action_taken_by": (me.id),
        })
        self.sudo().unlink()
        return value


class FileExitManagement(models.Model):
    _name = "file.exit.management"
    _description = "File Exit Management"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    file_id = fields.Many2one('folder.master', string="File")
    file_name = fields.Char(string='File Name')
    number = fields.Char(string='Number')
    transfer = fields.Boolean('Transfer')
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('closed', 'Action Completed'),('pending_close','Pending'),('pending_reopen','Pending'),
         ('closed_part', 'Action Part Completed')
         ], string='Status')

    def file_forward(self):
        value = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'folder.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_defid': self.file_id.id
            },
        }
        me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.env['exit.management.report'].sudo().create({
            "exit_transfer_id": self.exit_transfer_id.id,
            "employee_id": self.exit_transfer_id.employee_id.id,
            "exit_type": self.exit_transfer_id.exit_type,
            "module": 'File Forwarded',
            "module_id": str(self.file_name),
            "action_taken_by": (me.id),
        })
        self.sudo().unlink()
        return value

