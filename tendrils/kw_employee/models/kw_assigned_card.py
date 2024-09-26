# *******************************************************************************************************************
#  File Name             :   kw_assigned_card.py
#  Description           :   This model is used to assign the Id card no. 
#  Modified by           :   Monalisha Rout
#  Modified On           :   
#  Modification History  :    
# *******************************************************************************************************************

from odoo import models, fields, api


class kw_assigned_card(models.TransientModel):
    _name = 'kw_assigned_card'
    _description = "Assigned and unassigned card on view level"

    employee_id = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env['hr.employee'].search(
        [('id', '=', self.env.context.get('employee_id'))]), domain=[('id_card_no', '=', False)], required=True)
    compute_card = fields.Char(string="Existing Card No", readonly=True)
    card_number = fields.Many2one('kw_card_master', string="New Card",
                                  domain=[('active', '=', True), ('state', '=', 'unassigned')], required=True,
                                  default=lambda self: self.env['kw_card_master'].search(
                                      [('id', '=', self.env.context.get('id_card'))]))
    old_card_no = fields.Many2one('kw_card_master', string='Old Card No')
    designation_id = fields.Char(string="Designation")
    emp_code = fields.Char(string="Employee Code")

    """shows the employee's corresponding card_no and designation"""

    @api.onchange('employee_id')
    def _compute_assigned_card(self):
        # if self.employee_id.id_card_no.name:
        self.old_card_no = self.employee_id.id_card_no.id
        self.emp_code = self.employee_id.emp_code
        self.designation_id = self.employee_id.job_id.name
        self.compute_card = self.employee_id.id_card_no.name if self.employee_id.id_card_no else False

    """make the the assigned card no to unassigned when an unassigned card number is assign to that particular employee """

    @api.multi
    def save_wizard_data(self, vals):
        for record in self:
            emp_rec = self.env['hr.employee'].sudo().search([('id', '=', record.employee_id.id)])
            if emp_rec.id_card_no != False:
                old_card = emp_rec.id_card_no.id
                new_card = record.card_number.id
                emp_rec.write({'id_card_no': new_card})

                old_card_rec = self.env['kw_card_master'].sudo().search([('id', '=', old_card)])
                old_card_rec.write({'state': 'unassigned', 'employee_id': False})

                new_card_rec = self.env['kw_card_master'].sudo().search([('id', '=', new_card)])
                new_card_rec.write({'state': 'assigned', 'employee_id': emp_rec.id})
            else:
                new_card = record.card_number.id
                emp_rec.write({'id_card_no': new_card})

                new_card_rec = self.env['kw_card_master'].sudo().search([('id', '=', new_card)])
                new_card_rec.write({'state': 'assigned', 'employee_id': emp_rec.id})
