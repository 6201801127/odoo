from odoo import fields, models


class GrievanceCategory(models.Model):
    _name = 'grievance.ticket.category'
    _description = 'Grievance Ticket Category'
    _rec_name = "name"

    _sql_constraints = [
        ('name_uniq', 'unique (name)','Category Already Exist!')
    ]
    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    category_code = fields.Char('Code',required=True)
    sub_category = fields.Many2one('grievance.ticket.subcategory')
    team = fields.Many2one(comodel_name='grievance.ticket.team', string="Team")
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('grievance.ticket')
    )
