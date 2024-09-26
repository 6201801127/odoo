from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import re

class kw_choose_module(models.Model):
    _name = 'kw_choose_module'
    _description = 'Choose Kwantify module'
    _rec_name = 'rec_module_name'


    rec_module_name = fields.Text(string="Module Name",required=True)
    choose_module_id = fields.Many2one("ir.module.module",string="Select Module",domain="[('state','=','installed')]", required=True, ondelete='restrict')
    active_module = fields.Boolean(string="Active",default=True)

    c_appreciation = fields.Integer(string="Appreciation", compute='compute_feedback')
    c_issue = fields.Integer(string="Issue", compute='compute_feedback')
    c_suggestion = fields.Integer(string="Suggestion", compute='compute_feedback')
    c_feedback = fields.Integer(string="Feedback", compute='compute_feedback')

    c_rating = fields.Float(compute = 'compute_rating',string="Rating")
    c_star = fields.Selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], string="Star Ratings", compute='compute_rating')
    rating_count = fields.Integer(string="Feedback", compute='compute_rating')


    @api.constrains('rec_module_name')
    def name_constratints(self):
        if not re.findall('[A-Za-z0-9]', self.rec_module_name):
            raise ValidationError("Invalid Module Name")

# No duplicate module 
    @api.constrains('choose_module_id')
    def check_module(self):  
        rec = self.env['kw_choose_module'].sudo().search([])-self
        for m_rec in rec:
            if m_rec.choose_module_id.id == self.choose_module_id.id and m_rec.create_uid.id == self._uid:
                raise ValidationError('This module is already active.')

# Compute for rating count
    @api.multi
    def compute_rating(self):
        for module in self:
            feedback_ids = self.env['kw_module_rating'].sudo().search([('module_id','=',module.id)])
            if feedback_ids:
                module.rating_count = len(feedback_ids)
                module.c_rating = sum(feedback_ids.mapped(lambda r : int(r.ratings)))/len(feedback_ids)
                module.c_star = str(sum(feedback_ids.mapped(lambda r : int(r.ratings)))//len(feedback_ids))

# Compute for feedback count
    @api.multi
    def compute_feedback(self):
        for module in self:
            feedback_ids = self.env['kw_feedback'].sudo().search([('module_name','=',module.id)])
            module.c_feedback = len(feedback_ids)
            module.c_appreciation = len(feedback_ids.filtered(lambda r : r.feedback_type == 'Appreciation'))
            module.c_issue = len(feedback_ids.filtered(lambda r : r.feedback_type == 'Issue'))
            module.c_suggestion = len(feedback_ids.filtered(lambda r : r.feedback_type == 'Suggestion'))
            
# Return appreciation view
    @api.multi
    def view_appreciation(self):
        action = {
            'model': 'ir.actions.act_window',
            'name': 'Appreciations',
            'type': 'ir.actions.act_window',
            'target': 'self',
            'res_model': 'kw_feedback',
        }
        if self.env.user.has_group('kw_review_feedback.group_feedback_manager'):
            admin_tree_view = self.env.ref('kw_review_feedback.kw_review_feedback_list_admin').id
            action['view_mode'] = 'tree'
            action['views'] = [(admin_tree_view, 'tree')]
            action['domain'] = [('module_name', '=', self.id),('feedback_type','=','Appreciation')]
        else:
            feedback_ids = self.env['kw_feedback'].sudo().search([('create_uid','=',self._uid),('module_name','=',self.id),('feedback_type','=','Appreciation')])
            form_view_id = self.env.ref('kw_review_feedback.kw_review_feedback_form_user').id
            action['context'] = {
                "default_module_name":self.id,
                "default_feedback_type":'Appreciation'}
            action['view_type']= 'form'
            if not feedback_ids:
                action['view_mode'] = 'form'
                action['view_id'] = form_view_id
            else:
                tree_view_id = self.env.ref('kw_review_feedback.kw_review_feedback_list_user').id
                action['view_mode'] = 'form,tree'
                action['views'] = [(tree_view_id, 'tree'), (form_view_id, 'form')]
                action['domain'] = [('id', 'in', feedback_ids.ids)]
        return action
                
               
# Return Issue view
    @api.multi
    def view_issue(self):
        action = {
            'model': 'ir.actions.act_window',
            'name': 'Issue',
            'type': 'ir.actions.act_window',
            'target': 'self',
            'res_model': 'kw_feedback',
        }
        if self.env.user.has_group('kw_review_feedback.group_feedback_manager'):
            admin_tree_view = self.env.ref('kw_review_feedback.kw_review_feedback_list_admin').id
            action['view_mode'] = 'tree'
            action['views'] = [(admin_tree_view, 'tree')]
            action['domain'] = [('module_name', '=', self.id),('feedback_type','=','Issue')]
        else:
            feedback_ids = self.env['kw_feedback'].sudo().search([('create_uid','=',self._uid),('module_name','=',self.id),('feedback_type','=','Issue')])
            form_view_id = self.env.ref('kw_review_feedback.kw_review_feedback_form_user').id
            action['context'] = {
                "default_module_name":self.id,
                "default_feedback_type":'Issue'}
            action['view_type']= 'form'
            if not feedback_ids:
                action['view_mode'] = 'form'
                action['view_id'] = form_view_id
            else:
                tree_view_id = self.env.ref('kw_review_feedback.kw_review_feedback_list_user').id
                action['view_mode'] = 'form,tree'
                action['views'] = [(tree_view_id, 'tree'), (form_view_id, 'form')]
                action['domain'] = [('id', 'in', feedback_ids.ids)]
        return action


# Return Suggestion view
    @api.multi
    def view_suggestion(self):
        action = {
            'model': 'ir.actions.act_window',
            'name': 'Suggestion',
            'type': 'ir.actions.act_window',
            'target': 'self',
            'res_model': 'kw_feedback',
        }
        if self.env.user.has_group('kw_review_feedback.group_feedback_manager'):
            admin_tree_view = self.env.ref('kw_review_feedback.kw_review_feedback_list_admin').id
            action['view_mode'] = 'tree'
            action['views'] = [(admin_tree_view, 'tree')]
            action['domain'] = [('module_name', '=', self.id),('feedback_type','=','Suggestion')]
        else:
            feedback_ids = self.env['kw_feedback'].sudo().search([('create_uid','=',self._uid),('module_name','=',self.id),('feedback_type','=','Suggestion')])
            form_view_id = self.env.ref('kw_review_feedback.kw_review_feedback_form_user').id
            action['context'] = {
                "default_module_name":self.id,
                "default_feedback_type":'Suggestion'}
            action['view_type']= 'form'
            if not feedback_ids:
                action['view_mode'] = 'form'
                action['view_id'] = form_view_id
            else:
                tree_view_id = self.env.ref('kw_review_feedback.kw_review_feedback_list_user').id
                action['view_mode'] = 'form,tree'
                action['views'] = [(tree_view_id, 'tree'), (form_view_id, 'form')]
                action['domain'] = [('id', 'in', feedback_ids.ids)]
        return action

# Return Rating View
    @api.multi
    def view_star(self):

        action = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_module_rating',
                'name':"Ratings",
                'view_mode': 'tree',
                'target': 'self',
            }
         
        if self.env.user.has_group('kw_review_feedback.group_feedback_manager'):
            tree_view_id = self.env.ref('kw_review_feedback.kw_admin_module_rating_tree_view').id
            action['view_mode'] = 'tree'
            action['views'] = [(tree_view_id, 'tree')]
            action['domain'] = [('module_id', '=', self.id)]
            
        else:
            rating_id = self.env['kw_module_rating'].sudo().search([('create_uid','=',self._uid),('module_id','=',self.id)])
            form_view_id = self.env.ref('kw_review_feedback.kw_module_rating_form_view').id
            action['view_mode'] = 'form'
            action['view_type'] =  'form'
            if not rating_id:
                action['view_id'] = form_view_id
                action['context'] = {"default_module_id":self.id }
            else:
                action['views'] =  [(form_view_id, 'form')]
                action['res_id'] = rating_id.id
        return action
                    