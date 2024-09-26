# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from functools import wraps

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime

def implemented_by_base_exception(func):
    """Call a prefixed function based on 'namespace'."""
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        fun_name = func.__name__
        fun = '_%s%s' % (cls.rule_group, fun_name)
        if not hasattr(cls, fun):
            fun = '_default%s' % (fun_name)
        return getattr(cls, fun)(*args, **kwargs)
    return wrapper


class ExceptionRule(models.Model):
    _name = 'exception.rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Exception Rules"
    _order = 'active desc, sequence asc'


    name = fields.Char('Name', translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when applying the test")
    rule_group = fields.Selection(
        selection=[],
        help="Rule group is used to group the rules that must validated "
        "at same time for a target object. Ex: "
        "validate sale.order.line rules with sale order rules.",
        )
    model = fields.Selection(
        selection=[],
        string='Apply on')
    active = fields.Boolean('Active')
    filter_domain = fields.Char()
    action_type = fields.Selection([('domain', 'Filter'),('code', 'Python Code')],default='domain')
    group_approval_ids = fields.One2many('group.and.approval','rule_id')

    # check_len_group=fields.Integer("In Hand Value", compute="check_group_lines_exist",store=True)

    day_approval = fields.Integer("Days To Approve")

    # @api.depends('group_approval_ids')
    # def check_group_lines_exist(self):
    #     # print("-----------------compute method---------")
    #     for s in self:
    #         s.check_len_group = len(s.group_approval_ids)
    #
    # @api.constrains('check_len_group')
    # def check_no_of_group_validation(self):
    #     # print("--------------constaint method-----------")
    #     for i in self:
    #         if i.check_len_group <= 0:
    #             raise UserError(
    #             _('There should be atleast one group in Approval Matrix'))

    # ************* create and write method method***************
    @api.model
    def create(self, vals):
        res = super(ExceptionRule, self).create(vals)
        if not res.group_approval_ids:
            raise UserError(_('There should be atleast one group in Approval Matrix'))
        return res

    @api.multi
    def _write(self, vals):
        res = super(ExceptionRule, self)._write(vals)
        for s in self:
            if not s.group_approval_ids:
                raise UserError(_('There should be atleast one group in Approval Matrix'))
        return res

    @api.constrains('filter_domain')
    def change_chatter_on_filter(self):
        _body = (_(
            (
                "<ul>A new condition  <b style='color:green'>{0}</b> has been added in Rule</ul> ").format(
                self.filter_domain)))
        self.message_post(body=_body)

    @api.constrains('action_type')
    def change_chatter_on_action_type(self):

        if self.action_type == 'domain':
            previous = 'code'
        else:
            previous= 'domain'

        _body = (_(
            (
                "<ul>Exception Mode Changed <b style='color:red'>{1}</b> ------> <b style='color:green'>{0}</b></ul> ").format(
                previous,self.action_type)))
        self.message_post(body=_body)

    @api.constrains('code')
    def chatter_on_code(self):
        _body = (_(
            (
                "<ul>Code was changed<ul>")
                ))
        self.message_post(body=_body)



    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. The code must apply block = True to apply the "
             "exception.",
        default="""
        # Python code. Use failed = True to block the base.exception.
        # You can use the following variables :
        #  - self: ORM model of the record which is checked
        #  - "rule_group" or "rule_group_"line:
        #       browse_record of the base.exception or
        #       base.exception line (ex rule_group = sale for sale order)
        #  - object: same as order or line, browse_record of the base.exception or
        #    base.exception line
        #  - pool: ORM model pool (i.e. self.pool)
        #  - time: Python time module
        #  - cr: database cursor
        #  - uid: current user id
        #  - context: current context
    """
    )

    @api.multi
    def refactor_code(self):
        search_string = '''k = env['{0}'].search({1}) '''.format(self.model, self.filter_domain)
        remaining = [search_string,
                     'if sale.id in k.ids:',
                     '  failed = True']
        code_string = '\n'.join(remaining)
        self.code = code_string

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active


class BaseException(models.AbstractModel):
    _name = 'base.exception'
    _description = 'Base Exception'

    _order = 'main_exception_id asc'

    main_exception_id = fields.Many2one(
        'exception.rule',
        compute='_compute_main_error',
        string='Main Exception',
        store=True,copy=False)
    rule_group = fields.Selection(
        [],
        readonly=True,copy=False
    )
    exception_ids = fields.Many2many(
        'exception.rule',
        string='Exceptions')
    ignore_exception = fields.Boolean('Ignore Exceptions', copy=False)
    approved = fields.Boolean(copy=False)

    @api.depends('exception_ids', 'ignore_exception')
    def _compute_main_error(self):
        for obj in self:
            if not obj.ignore_exception and obj.exception_ids:
                obj.main_exception_id = obj.exception_ids[0]
            else:
                obj.main_exception_id = False

    @api.multi
    def _popup_exceptions(self):
        action = self._get_popup_action()
        action = action.read()[0]
        action.update({
            'context': {
                'active_id': self.ids[0],
                'active_ids': self.ids
            }
        })
        return action

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('base_exception.action_exception_rule_confirm')
        return action

    @api.multi
    def _check_exception(self):
        """
        This method must be used in a constraint that must be created in the
        object that inherits for base.exception.
        for sale :
        @api.constrains('ignore_exception',)
        def sale_check_exception(self):
            ...
            ...
            self._check_exception
        """
        exception_ids = self.detect_exceptions()
        if exception_ids:
            exceptions = self.env['exception.rule'].browse(exception_ids)
            raise ValidationError('\n'.join(exceptions.mapped('name')))

    @api.multi
    def test_exceptions(self):
        """
        Condition method for the workflow from draft to confirm
        """
        if self.detect_exceptions():
            return False
        return True

    @api.multi
    def detect_exceptions(self):
        """returns the list of exception_ids for all the considered base.exceptions
        """
        if not self:
            return []
        exception_obj = self.env['exception.rule']
        print('self[0].rule_group)self[0].rule_group)self[0].rule_group)', self[0].rule_group)
        all_exceptions = exception_obj.sudo().search(
            [('rule_group', '=', self[0].rule_group)])
        print('all_exceptionsall_exceptionsall_exceptions', all_exceptions)
        model_exceptions = all_exceptions.filtered(
            lambda ex: ex.model == self._name)
        print('model_exceptionsmodel_exceptionsmodel_exceptions', model_exceptions)
        sub_exceptions = all_exceptions.filtered(
            lambda ex: ex.model != self._name)
        print('sub_exceptionssub_exceptionssub_exceptions', sub_exceptions)
        all_exception_ids = []
        for obj in self:
            print("objobjobjobjobjobjobjobjobjobjobj", obj)
            if obj.ignore_exception:
                continue
            exception_ids = obj._detect_exceptions(
                model_exceptions, sub_exceptions)
            print('exception_idsexception_idsexception_idsexception_ids', exception_ids)
            obj.exception_ids = [(6, 0, exception_ids)]
            all_exception_ids += exception_ids
            print('all_exception_idsall_exception_idsall_exception_ids', all_exception_ids)
        return all_exception_ids

    @api.model
    def _exception_rule_eval_context(self, obj_name, rec):
        user = self.env['res.users'].browse(self._uid)
        return {obj_name: rec,
                'self': self.pool.get(rec._name),
                'object': rec,
                'obj': rec,
                'pool': self.pool,
                'cr': self._cr,
                'uid': self._uid,
                'user': user,
                'time': time,
                # copy context to prevent side-effects of eval
                'context': self._context.copy()}

    @api.model
    def _rule_eval(self, rule, obj_name, rec):
        if rule.action_type == 'code':
            expr = rule.code
            space = self._exception_rule_eval_context(obj_name, rec)
            try:
                safe_eval(expr,
                          space,
                          mode='exec',
                          nocopy=True)  # nocopy allows to return 'result'
            except  Exception:
                raise UserError(
                    _('Error when evaluating the exception.rule '
                      'rule:\n %s \n(%s)') % (rule.name, Exception))
            print ('_________________________________________JE SPACEE HAI',space)
            return space.get('failed', False)
        if rule.action_type == 'domain':
            space = self._exception_rule_eval_context(obj_name, rec)
            print ('_________________________________________',rule.filter_domain)
            dm = safe_eval(rule.filter_domain)
            record_list = self.env[rec._name].search(dm)
            print ('_________________________________',record_list)
            if rec.id in list(record_list.ids):
                return True
            else:
                return False


    @api.multi
    def _detect_exceptions(self, model_exceptions,
                           sub_exceptions):
        self.ensure_one()
        exception_ids = []
        for rule in model_exceptions:
            if self._rule_eval(rule, self.rule_group, self):
                exception_ids.append(rule.id)
        if sub_exceptions:
            for obj_line in self._get_lines():
                for rule in sub_exceptions:
                    if rule.id in exception_ids:
                        # we do not matter if the exception as already been
                        # found for an line of this object
                        # (ex sale order line if obj is sale order)
                        continue
                    group_line = self.rule_group + '_line'
                    if self._rule_eval(rule, group_line, obj_line):
                        exception_ids.append(rule.id)
        return exception_ids

    @implemented_by_base_exception
    def _get_lines(self):
        pass

    def _default_get_lines(self):
        return []


class Approvalslist(models.Model):
    _name = "approvals.list"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'resource_ref'
    _description="Approval"
    _order='create_date desc'

    @api.model
    def create(self, vals):
        if vals:
            vals.update({
                'name': self.env['ir.sequence'].get('approvals.list')
            })
        result = super(Approvalslist, self).create(vals)
        return result


    name =fields.Char(string="Name")
    model_id = fields.Many2one('ir.model', string='Approval Record')
    model_name =fields.Char(related="model_id.name",string='Model')
    branch_id = fields.Many2one('res.branch',string="Center", store=True)
    date = fields.Date(string='Requesting Date')
    user_id = fields.Many2one('res.users', string='Requesting User')
    rule_id = fields.Many2one('exception.rule', string='Approval Matrix')
    group_id = fields.Many2one('res.groups', string='Approving Groups')
    test_int = fields.Integer()
    resource_ref = fields.Reference(
        string='Record', selection='_selection_target_model',
    )
    state = fields.Selection(
        [('pending_approval', 'Pending Approval'),('approved', 'Approved'), ('rejected', 'Rejected')], default="pending_approval")
    group_approval_id = fields.Many2one('group.and.approval')
    approvals_done = fields.Integer(string="Approval Done")
    rejections_done = fields.Integer(string="Rejections Done")
    approvals_required = fields.Integer(related='group_approval_id.minimum_approval' ,string="Approvals Required")
    rejections_required = fields.Integer(related='group_approval_id.minimum_rejection',string="Rejections Required")
    approval_user_matrix_id = fields.One2many('approval.user.matrix','approval_id')

    day_approval=fields.Integer(string="Days To Approve")
    approval_deadline=fields.Date(string="Approval DeadLine Date")
    color = fields.Integer('Color Index', default=0)
    condition_check = fields.Boolean('Condition Check', default=0)

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        s = [(model.model, model.name) for model in models]
        return s

    @api.multi
    def approve(self):
        if self.env.user.id in self.group_id.users.ids:
            matrix_check = self.env['approval.user.matrix'].search([('approval_id','=',self.id),('user','=',self.env.user.id)],limit=1)

            if matrix_check.user_response == False:
                self.approvals_done += 1

                matrix_check.accepted = True
                self.user_took_action_chatter('Approved')


                sumry="Approved "+str(datetime.now())
                self.activity_feedback(['base_exception_and_approval.mail_act_approval'],user_id=self.env.user.id, feedback=sumry)


                if self.approvals_done == self.approvals_required:

                    self.all_activity_unlinks()
                    self.state = 'approved'
                    k = self.env['approvals.list'].search([('resource_ref','=',self.resource_ref._name +','+ str(self.resource_ref.id))])
                    list_of_approvals = [approval.state == 'approved'  for approval in k]
                    if all(list_of_approvals):
                        self.resource_ref.ignore_exception = True
                        return True
            else:
                raise UserError('You already have a response on this record')

            if len(self.rule_id.group_approval_ids)>1:
                for exp_line in self.rule_id.group_approval_ids:
                    print("-00000000000000", exp_line,exp_line.group)
                    if exp_line.group == self.group_id:
                        print("iuiuiuiiiiiiiiiiiiigroup", exp_line.sequence ,(exp_line.sequence + 1) )
                        matrix_check = self.env['group.and.approval'].search([('sequence','=',(exp_line.sequence + 1)), ('rule_id', '=', self.rule_id.id)])
                        print('matrix_checkoooooooooooooooooooooo', matrix_check, matrix_check.group.name)
                        exp1 = self.env['approvals.list'].search([('group_id','=', matrix_check.group.id),('resource_ref','=',self.resource_ref._name +','+ str(self.resource_ref.id))])
                        print('-==========', exp1)
                        for rec in exp1:
                            rec.condition_check = True
                            print("oiiiiiiiiiiiiiiioioioioioi", rec, rec.condition_check)
        else:
            raise UserError('You are not authorized to take an action')


    def user_took_action_chatter(self,s):
        _body = (_(
            (
                "<ul><b>{0}</b> {1} </ul> ").format(
                self.env.user.name,s)))
        self.resource_ref.message_post(body=_body)
        self.message_post(body=_body)




    @api.multi
    def reject(self):

        if self.env.user.id in self.group_id.users.ids:
            matrix_check = self.env['approval.user.matrix'].search(
                [('approval_id', '=', self.id), ('user', '=', self.env.user.id)], limit=1)

            if matrix_check.user_response == False:
                self.rejections_done += 1

                matrix_check.rejected = True
                self.user_took_action_chatter('Rejected')

                sumry = "Rejected " + str(datetime.now())
                self.activity_feedback(['base_exception_and_approval.mail_act_approval'], user_id=self.env.user.id,
                                       feedback=sumry)

                if self.rejections_done == self.rejections_required:
                    self.state = 'rejected'
                    self.all_activity_unlinks()
                    return True

            else:
                raise UserError('You already have a response on this record')
        else:
            raise UserError('You are not authorized to take an action')

    @api.multi
    def reopen_request(self):
        self.state = 'pending_approval'



     #--------------------------------------- Activity done

    def activity_feedback(self, act_type_xmlids, user_id=None, feedback=None):
        """ Set activities as done, limiting to some activity types and
        optionally to a given user. """
        if self.env.context.get('mail_activity_automation_skip'):
            return False

        # print("--------------------------act_type_xmlids",act_type_xmlids)
        Data = self.env['ir.model.data'].sudo()
        activity_types_ids = [Data.xmlid_to_res_id(xmlid) for xmlid in act_type_xmlids]

        # print("----------------------activity_types_ids ",activity_types_ids )

        domain = [
            '&', '&', '&',
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('automated', '=', True),
            ('activity_type_id', 'in', [4])
        ]
        if user_id:
            domain = ['&'] + domain + [('user_id', '=', user_id)]
        activities = self.env['mail.activity'].search(domain)
        if activities:
            activities.action_feedback(feedback=feedback)
        return True

    #-----------------------------------------

    def all_activity_unlinks(self):
        if self:
            # print("------------------all_activity_unlinks")
            domain = [
                '&', '&', '&',
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
                ('automated', '=', True),
                ('activity_type_id', '=', 4)
            ]
            activities = self.env['mail.activity'].search(domain)
            for activity in activities:
                activity.unlink()



class GroupAndApproval(models.Model):
    _name = 'group.and.approval'
    _description = 'Group and approval'
    _rec_name = 'group'

    group = fields.Many2one('res.groups',required=True ,string="Group")
    minimum_approval =  fields.Integer(default=1,required=True)
    minimum_rejection = fields.Integer(default=1,required=True)
    rule_id = fields.Many2one('exception.rule')
    sequence = fields.Integer('Seq No.')
    
    
    @api.constrains('group')
    def check_no_users(self):
        for i in self:
            k = len(i.group.users)
            if k == 0:
                raise UserError(
                    _('Your Group Got No users'))

    @api.constrains('rule_id')
    def post_on_chatter(self):
        for i in self:
            _body = (_(
                (
                    "<ul>A new group  <b style='color:red'>{0}</b> has been added in Rule</ul> ").format(
                    i.group.name)))
            i.rule_id.message_post(body=_body)

class ApprovalUserMatrix(models.Model):
    _name = 'approval.user.matrix'
    _description = 'Approval user matrix'
    _rec_name='user'

    user = fields.Many2one('res.users', string="User")
    accepted = fields.Boolean()
    rejected = fields.Boolean()
    approval_id = fields.Many2one('approvals.list')
    user_response = fields.Boolean(compute='calculate_user_response')
    

    @api.depends('accepted','rejected')
    def calculate_user_response(self):
        for i in self:
            i.user_response = self.accepted or self.rejected






        


