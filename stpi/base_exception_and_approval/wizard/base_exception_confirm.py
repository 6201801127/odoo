# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models,_
# from datetime import datetime
import datetime
from odoo.exceptions import UserError

class ExceptionRuleConfirm(models.AbstractModel):

    _name = 'exception.rule.confirm'
    _description = 'Exception Rule Confirm'

    related_model_id = fields.Many2one('base.exception',)
    exception_ids = fields.Many2many('exception.rule',
                                     string='Exceptions to resolve',
                                     readonly=True)
    ignore = fields.Boolean('Ignore Exceptions')



    @api.model
    def default_get(self, field_list):
        res = super(ExceptionRuleConfirm, self).default_get(field_list)
        current_model = self._context.get('active_model')
        model_except_obj = self.env[current_model]
        active_ids = self._context.get('active_ids')
        assert len(active_ids) == 1, "Only 1 ID accepted, got %r" % active_ids
        active_id = active_ids[0]
        related_model_except = model_except_obj.browse(active_id)
        exception_ids = [e.id for e in related_model_except.exception_ids]
        res.update({'exception_ids': [(6, 0, exception_ids)]})
        res.update({'related_model_id': active_id})
        return res

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def request_approval(self):
        model = self.env['ir.model'].search([('model','=',self.related_model_id._name)])

        reference = self.related_model_id._name + ',' + str(self.related_model_id.id)
        branch_id = self.env['res.branch'].sudo().search([], limit=1).id
        if self.related_model_id.branch_id.id:
            branch_id = self.related_model_id.branch_id.id
        if self.related_model_id.approved == True:
            raise UserError('Approval Already in process')
        
        print("-========================-", self.exception_ids.group_approval_ids, self.exception_ids.group_approval_ids[0] )
        for exception in self.exception_ids:
            for group in exception.group_approval_ids:
                x = self.env['approvals.list'].create({
                    'resource_ref': reference,
                    'branch_id': branch_id,
                    'user_id': self.env.user.id,
                    'test_int': self.id,
                    'date': datetime.datetime.now().date(),
                    'rule_id': exception.id,
                    'group_approval_id':group.id,
                    'group_id': group.group.id,
                    'model_id': model.id,
                    'day_approval':exception.day_approval,

                })
                for user in group.group.users:
                    self.env['approval.user.matrix'].create({
                        'user': user.id,
                        'accepted': False,
                        'rejected': False,
                        'approval_id':x.id
                    })
                print("oiiiiiiiiiiiiiiiiiiiiiii", x,self.exception_ids.group_approval_ids[0].group, x.group_id)
                if self.exception_ids.group_approval_ids[0].group == x.group_id:
                    x.condition_check = True
                for u_id in x.group_id.users.ids:
                    approval_date=datetime.datetime.now() + datetime.timedelta(days=x.day_approval)
                    x.update({'approval_deadline':approval_date.date()})

                    # print("______________________________u_id", u_id,datetime.datetime.now(),approval_date)
                    x.activity_schedule(summary='Approval Request',activity_type_id=4,date_deadline=approval_date,user_id=u_id,)

        _body = (_(
            (
                "<ul>Approval Requested</ul>")
                ))

        self.related_model_id.message_post(body=_body)
        self.related_model_id.approved = True




