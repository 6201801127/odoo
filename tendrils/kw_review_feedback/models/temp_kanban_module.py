from odoo import models, fields, api


class temp_kanban(models.Model):
    _name = 'temp_kanban'
    _description = "kanban"
    _rec_name = 'rel_name'

    rel_name = fields.Many2one('ir.module.module', string="Name Relation")
    c_appreciation = fields.Integer(string="Appreciation")
    c_issue = fields.Integer(string="Issue")
    c_suggestion = fields.Integer(string="Suggestion")
    c_rating = fields.Float(compute='compute_rating', string="Rating")
    c_star = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                              string="Star Ratings", compute='compute_rating')
    c_feedback = fields.Integer(string="Feedback", default=1)
    rating_count = fields.Integer(string="Feedback", compute='compute_rating')

    # Rating calculation
    @api.multi
    def compute_rating(self):

        for module in self:
            feedback_ids = self.env['kw_module_rating'].sudo().search([('module_id', '=', module.rel_name.id)])
            if feedback_ids:
                module.rating_count = len(feedback_ids)
                module.c_rating = sum(feedback_ids.mapped(lambda r: int(r.ratings))) / len(feedback_ids)
                module.c_star = str(sum(feedback_ids.mapped(lambda r: int(r.ratings))) // len(feedback_ids))
