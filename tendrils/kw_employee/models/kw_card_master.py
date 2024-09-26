# *******************************************************************************************************************
#  File Name             :   kw_card_master.py
#  Description           :   This model is used to create the Id card no 
#  Modified by           :   Monalisha Rout
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import models, fields, api
from odoo.exceptions import Warning


class KWCardMaster(models.Model):
    _name = "kw_card_master"
    _description = "ID and Access Card Master"
    _rec_name = 'name'
    _order = "name"

    name = fields.Char(string='Card No', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([('assigned', 'Assigned'), ('unassigned', 'Un-Assigned')], string="Status",
                             default='unassigned')
    assigned = fields.Char(compute='_get_assigned_card', string="Assigned To")
    designation_id = fields.Char(compute='_get_assigned_card', string="Designation")
    code = fields.Char(compute='_get_assigned_card', string='Employee Code')
    compute_onboarding = fields.Boolean(compute='compute_onboarding_emp', default=False)
    card_type = fields.Selection([('1', 'ID Card'), ('2', 'Access Card')], 'Card Type', default='1')

    employee_id = fields.Many2one('hr.employee', string="Employee Tagged")


    def compute_onboarding_emp(self):
        for record in self:
            if record.active == True and record.state == 'assigned':
                card_rec = self.env['hr.employee'].sudo().search([('id_card_no', '=', record.id)])
                if not card_rec:
                    record.compute_onboarding = True

    """ Release Card when Click To Confirm"""
    def release_card(self):
        for record in self:
            if record.state == 'assigned':
                card_rec = self.env['hr.employee'].sudo().search([('id_card_no', '=', record.id)])
                if card_rec:
                    card_rec.id_card_no = None
                    record.assigned = None
                    record.state = "unassigned"
                    record.employee_id=False
                    record.enrollment_id=False
                else:
                    enrollment_rec = self.env['kwonboard_enrollment'].sudo().search([('id_card_no', '=', record.id)])
                    # new_joinee_rec = self.env['kwonboard_new_joinee'].sudo().search([('card_no', '=', record.id)])
                    
                    if enrollment_rec:
                        enrollment_rec.id_card_no = None
                        record.enrollment_id=False
                        record.employee_id=False
                        record.state = "unassigned"
                    # if new_joinee_rec:
                    #     new_joinee_rec.card_no = None

    """Render the Confirmation page by clicking on Release card Button"""
    def button_release_card(self):
        form_view_id = self.env.ref("kw_employee.kw_release_card_view").id
        return {
            'name': 'Release Card',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_card_master',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'view_id': form_view_id,
            'res_id': self.id,
            'domain': [('id', '=', self.id)]
        }

    """ used for hiding assign/reassign button when a card is assigned during onboarding side"""

    def compute_onboarding_emp(self):
        for record in self:
            if record.active and record.state == 'assigned':
                card_rec = self.env['hr.employee'].sudo().search([('id_card_no', '=', record.id)])
                if not card_rec:
                    record.compute_onboarding = True

    """used for showing the employee details when a card will assign/reassign to the employee """
    @api.model
    def _get_assigned_card(self):
        for record in self:
            if not record.employee_id and not record.enrollment_id:
                # print("get assigned card >>>>> ")
                card_rec = self.env['hr.employee'].sudo().search([('id_card_no', '=', record.id)], limit=1)
                if card_rec:
                    record.assigned = f"%s (%s)" % (card_rec.name, card_rec.emp_code)
                    record.code = card_rec.emp_code
                    record.designation_id = card_rec.job_id.name
                    record.write({"employee_id": card_rec.id})
                else:
                    card_rec = self.env['kwonboard_enrollment'].sudo().search([('id_card_no', '=', record.id)], limit=1)
                    if card_rec:
                        record.assigned = card_rec.name
                        record.write({"enrollment_id": card_rec.id})
                    else:
                        record.assigned = '--'

    """click the wizard of assign card by a button click and """

    def button_assign_card(self):
        for record in self:
            wizard_form = self.env.ref('kw_employee.kw_assigned_card_form')
            if record.state == "assigned":
                rec = self.env['hr.employee'].sudo().search([('id_card_no', '=', record.id)])
                return {
                    'name': 'Assign/Reassign Card',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': wizard_form.id,
                    'res_model': 'kw_assigned_card',
                    'context': {'employee_id': rec.id, 'old_card': rec.id_card_no.id},
                    # for showing the corresponding card  holder name and card number in wizard
                    'target': 'new',
                }
            else:
                return {
                    'name': 'Assign/Reassign Card',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': wizard_form.id,
                    'res_model': 'kw_assigned_card',
                    'target': 'new',
                    'context': {'id_card': record.id},
                    # 'flags' : {'mode': 'readonly'},
                }

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'assigned':
                raise Warning("Assigned cards can not be deleted!")
        return super(KWCardMaster, self).unlink()

    @api.multi
    def write(self, vals):
        # print("vals  >>> ", vals)
        if 'employee_id' in vals and vals.get('employee_id', False) != False:
            for rec in self:
                existing_rec = self.search([('employee_id', '=', vals.get('employee_id', False))])
                if existing_rec:
                    # raise ValidationError('Already assigned.')
                    for xrec in existing_rec:
                        # xrec.employee_id.id_card_no = None
                        emp_query = f"UPDATE hr_employee SET id_card_no=null WHERE id={xrec.employee_id.id};"
                        self._cr.execute(emp_query)
                        xrec.employee_id = None
                rec.enrollment_id = None

        elif 'enrollment_id' in vals and vals.get('enrollment_id', False) != False:
            for rec in self:
                rec.employee_id = None

        response = super(KWCardMaster, self).write(vals)
        if 'employee_id' in vals and vals.get('employee_id', False) != False:
            for rec in self:
                # rec.employee_id.id_card_no = rec.id
                emp_query = f"UPDATE hr_employee SET id_card_no={rec.id} WHERE id={rec.employee_id.id};"
                self._cr.execute(emp_query)
        return response

    _sql_constraints = [('name_uniq', 'unique (name)',
                         'Duplicate Card No not allowed.!')]

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     print("card search read >>>> ", self)
    #     res = super().search_read(domain, fields, offset, limit, order)
    #     print("card details >>> ", res)
    #     return res
