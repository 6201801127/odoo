from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ExEmployeeContactUpdate(models.TransientModel):
    _name = 'exemployee_contact_update_wizard'
    _description = "Ex-employee contact details update"
    employee_id = fields.Many2one('hr.employee', string="Ex-Employee", domain="[('active', '=', False)]")
    employee_email = fields.Char(string="Email")
    employee_phn_no = fields.Char(string="Phone Number")

    def update_exemployee_details(self):
        query = f"update hr_employee set personal_email='{self.employee_email}',mobile_phone='{self.employee_phn_no}' where id='{self.employee_id.id}'"
        self._cr.execute(query)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Ex-Employee Contact',
            'res_model': 'exemployee_contact_update_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'flags': {
                'form': {'action_buttons': True},
            },
        }

    @api.onchange('employee_id')
    def _change_employee(self):
        if self.employee_id:
            self.employee_email = self.employee_id.personal_email
            self.employee_phn_no = self.employee_id.mobile_phone
        else:
            self.employee_email = False
            self.employee_phn_no = False
