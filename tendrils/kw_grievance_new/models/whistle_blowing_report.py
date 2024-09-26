from odoo import fields, models, api, tools


class WhistleBlowingReport(models.Model):
    _name = 'whistle_blowing_report'
    _description = 'Whistle Blowing Report'
    _rec_name = 'number'
    _auto = False


    def get_employee(self):
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            return employee
            
    id = fields.Integer(string="SL No")
    number = fields.Char(string='Grievance number', default="New",
                            readonly=True) 
    name = fields.Char(string='Grievance')       
    category_id = fields.Many2one('grievance.ticket.team',
                                  string='Category')
    sub_category = fields.Many2one('grievance.ticket.subcategory',
                                  string='Sub Category')
    # description = fields.Html(string='Subject', sanitize_style=True)
    stage_id = fields.Many2one(
        'grievance.ticket.stage',
        string='Status',
    )
    closed_date = fields.Datetime(string='Closed On')
    create_date = fields.Datetime(string='Created On')
    user_id = fields.Many2one('res.users',string='Assigned SPOC Person')
    # users_id = fields.Many2one(comodel_name='res.users', string='Employee')
    users_id = fields.Many2one(comodel_name='hr.employee', string='Employee', default=get_employee)
    raised_by = fields.Many2one('hr.employee', 'Raised By')
    remarks_for_done = fields.Char(string='Close Remarks') 
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        SELECT row_number() over() as id,
                    wb.number,
                    wb.name as name,
                    wb.create_date,
                    wb.users_id,
                    wb.category_id,
                    wb.sub_category,
                    wb.user_id,
                    wb.stage_id,
                    wb.closed_date,
                    wb.raised_by,
                    wb.remarks_for_done
                    from kw_whistle_blowing wb
                    )"""% (self._table))

    def whistle_blowing_status_report_action_view(self):
        form_view_id = self.env.ref("kw_grievance_new.kw_whistle_blowing_view_form").id
        for rec in self:
            ticket_rec = self.env['kw_whistle_blowing'].sudo().search([('number','=',rec.number)]).id
            context = {'hide_button': True} 
            return  {
                'name': 'Close',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_whistle_blowing',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': ticket_rec,
                'target': 'self',
                'view_id': form_view_id,
                'context': context,
            }