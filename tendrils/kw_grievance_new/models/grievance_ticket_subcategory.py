from odoo import fields, models, api


class GrievanceSubcategory(models.Model):
    _name = 'grievance.ticket.subcategory'
    _description = 'grievance Ticket Sub Category'

    _sql_constraints = [
        ('name_uniq', 'unique (name)','Sub-Category Already Exist!')
    ]
    name = fields.Char(string='Name', required=True)
    # category_code_id = fields.Many2one(string="Category",comodel_name='grievance.ticket.team')

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         result.append((record.id, "{} ({})".format(record.name, record.category_code_id.category_code)))
    #         # print("result......", result)
    #     return result
