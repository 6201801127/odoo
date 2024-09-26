# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval as eval
from odoo.exceptions import ValidationError, UserError, Warning
from datetime import datetime, date, time, timedelta
import random
import string
import logging

_logger = logging.getLogger(__name__)

CONDITION_CODE_TEMP = """# Available locals:
#  - use only the available fields of the model
#  - env: Odoo Environment.
#  - model: Model of the record on which the action is triggered.
#  - obj: Record on which the action is triggered if there is one, otherwise None.
#  - user, Current user object.
#  - workflow: Workflow engine.
#  - syslog : syslog(message), function to log debug information to Odoo logging file or console.
#  - warning: warning(message), Warning Exception to use with raise.


result = True"""


PYTHON_CODE_TEMP = """# Available locals:
#  - time, date, datetime, timedelta: Python libraries.
#  - env: Odoo Environment.
#  - model: Model of the record on which the action is triggered.
#  - obj: Record on which the action is triggered if there is one, otherwise None.
#  - user, Current user object.
#  - workflow: Workflow engine.
#  - syslog : syslog(message), function to log debug information to Odoo logging file or console.
#  - warning: warning(message), Warning Exception to use with raise.
# To return an action, assign: action = {...}


"""

MODEL_DOMAIN = """[
        ('state','in',['base','manual']),
        ('transient', '=', False),
        '!',
        '|',
        '|',
        '|',
        '|',
        '|',
        '|',
        '|',
        ('model', '=ilike', 'res.%'),
        ('model', '=ilike', 'ir.%'),
        ('model', '=ilike', 'odoo.workflow%'),
        ('model', '=ilike', 'bus.%'),
        ('model', '=ilike', 'base.%'),
        ('model', '=ilike', 'base_%'),
        ('model', '=', 'base'),
        ('model', '=', '_unknown'),
    ]"""

BTN_HIDE_DOMAIN = """[]"""

class OdooWorkflow(models.Model):
    _name           = 'odoo.workflow'
    _description    = 'Odoo Workflow'

    name            = fields.Char(string='Name', help="Give workflow a name.")
    model_id        = fields.Many2one('ir.model', string='Model', domain=MODEL_DOMAIN, help="Enter business model you would like to modify its workflow.")
    node_ids        = fields.One2many('odoo.workflow.node', 'workflow_id', string='Nodes')
    remove_default_attrs_mod = fields.Boolean(string='Remove Default Attributes & Modifiers', default=True, help="This option will remove default attributes set on fields & buttons of current model view in order to customized all attributes depending on your needs\nAttributes like: [required, readonly, invisible].")
    mail_thread_add = fields.Boolean(string='Add Mailthread/Messaging to Model', help="Add Mailthread area to model.")
    activities_add  = fields.Boolean(string='Add Activities to Model', help="Enable Activities in Mailthread")
    followers_add   = fields.Boolean(string='Add Followers to Model', help="Enable Followers in Mailthread")

    _sql_constraints = [
        ('uniq_name', 'unique(name)', _("Workflow name must be unique.")),
        ('uniq_model', 'unique(model_id)', _("Model must be unique.")),
    ]

    @api.constrains('node_ids')
    def validate_nodes(self):
        # Objects
        wkf_node_obj = self.env['odoo.workflow.node']
        for rec in self:
            # Must have one flow start node
            res = rec.node_ids.search_count([
                ('workflow_id', '=', rec.id),
                ('flow_start', '=', True),
            ])
            if res > 1:
                raise ValidationError(_("Workflow must have only one start node."))
            # Nodes' sequence must be unique per workflow
            for node in rec.node_ids:
                res = wkf_node_obj.search_count([
                    ('id', '!=', node.id),
                    ('workflow_id', '=', rec.id),
                    ('sequence', '=', node.sequence),
                ])
                if res:
                    raise ValidationError(_("Nodes' sequence must be unique per workflow."))

    @api.multi
    def btn_reload_workflow(self):
        from odoo.addons import kw_dynamic_workflow
        return kw_dynamic_workflow.update_workflow_reload(self)

    @api.multi
    def btn_nodes(self):
        for rec in self:
            act = {
                'name': _('Nodes'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'odoo.workflow.node',
                'domain': [('workflow_id', '=', rec.id)],
                'context': {'default_workflow_id': rec.id},
                'type': 'ir.actions.act_window',
            }
            return act

    @api.multi
    def btn_buttons(self):
        for rec in self:
            act = {
                'name': _('Buttons'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'odoo.workflow.node.button',
                'domain': [('workflow_id', '=', rec.id)],
                'context': {'default_workflow_id': rec.id},
                'type': 'ir.actions.act_window',
            }
            return act

    @api.multi
    def btn_links(self):
        for rec in self:
            act = {
                'name': _('Links'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'odoo.workflow.link',
                'domain': [
                    '|',
                    ('node_from.workflow_id', '=', rec.id),
                    ('node_to.workflow_id', '=', rec.id),
                ],
                'context': {},
                'type': 'ir.actions.act_window',
            }
            return act


class OdooWorkflowNode(models.Model):
    _name           = 'odoo.workflow.node'
    _description    = 'Odoo Workflow Nodes'
    _order          = 'sequence'

    name            = fields.Char(string='Name', translate=True, help="Enter string name of the node.")
    node_name       = fields.Char(string='Technical Name', help="Generated technical name which used by backend code.")
    sequence        = fields.Integer(string='Sequence', default=10, help="Arrange node by defining sequence.")
    flow_start      = fields.Boolean(string='Flow Start', help="Check it if this node is the starting node.")
    flow_end        = fields.Boolean(string='Flow End', help="Check it if this node is the ending node.")
    is_visible      = fields.Boolean(string='Appear in Statusbar', default=True, help="Control visiability of the node/state in view.")
    out_link_ids    = fields.One2many('odoo.workflow.link', 'node_from', string='Outgoing Transitions')
    in_link_ids     = fields.One2many('odoo.workflow.link', 'node_to', string='Incoming Transitions')
    field_ids       = fields.One2many('odoo.workflow.node.field', 'node_id', string='Fields')
    button_ids      = fields.One2many('odoo.workflow.node.button', 'node_id', string='Buttons')
    workflow_id     = fields.Many2one('odoo.workflow', string='Workflow Ref.', ondelete='cascade', required=True)
    model_id        = fields.Many2one('ir.model', string='Model Ref.', domain="[('state','in',['base','manual'])]", related='workflow_id.model_id', required=True)

    @api.onchange('name')
    def _compute_node_name(self):
        for rec in self:
            if rec and rec.name:
                name            = rec.name.lower().strip().replace(' ', '_')
                rec.node_name   = name

    @api.multi
    def btn_load_fields(self):
        # Variables
        field_obj = self.env['ir.model.fields']
        for rec in self:
            # Clear Fields List
            rec.field_ids.unlink()
            # Load Fields
            fields = field_obj.search([('model_id', '=', rec.model_id.id)])
            for field in fields:
                rec.field_ids.create({
                    'model_id'  : rec.model_id.id,
                    'node_id'   : rec.id,
                    'name'      : field.id,
                })
    ##method to get the model record url
    @api.multi
    def get_url(self,record_id):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        action   = self.env['ir.actions.act_window'].search([('res_model', '=', self.model_id.model), ('domain', '=', False)], limit=1)
        if not action:
            raise ValidationError(_('Approval object %s get_url not found action')%(self.model_id._description))
        url = "%s/web#id=%s&action=%s&model=%s&view_type=form"%(base_url,record_id, action.id,self.model_id.model)
        return url


class OdooWorkflowLink(models.Model):
    _name           = 'odoo.workflow.link'
    _description    = 'Odoo Workflow Links'

    name            = fields.Char(string='Name', help="Enter friendly link name that describe the process.")
    condition_code  = fields.Text(string='Condition Code', default=CONDITION_CODE_TEMP,
                                 help="Enter condition to pass thru this link.")
    node_from       = fields.Many2one('odoo.workflow.node', 'Source Node', ondelete='cascade', required=True)
    node_to         = fields.Many2one('odoo.workflow.node', 'Destination Node', ondelete='cascade', required=True)
    ##new field added by , T Ketaki Debadarshini, On : 23-Oct-2020
    workflow_id     = fields.Many2one('odoo.workflow', string='Workflow Ref.')

    @api.constrains('node_from', 'node_to')
    def check_nodes(self):
        for rec in self:
            if rec.node_from == rec.node_to:
                raise ValidationError(_("Sorry, source & destination nodes can't be the same."))

    @api.onchange('node_from', 'node_to')
    def onchange_nodes(self):
        for rec in self:
            if rec.node_from and rec.node_to:
                rec.name = "%s -> %s" % (rec.node_from.name, rec.node_to.name)

    @api.multi
    def trigger_link(self):
        # Variables
        cx = self.env.context
        model_name = cx.get('active_model')
        rec_id = cx.get('active_id')
        ##modified by: T Ketaki Debadarshini, On :23-Oct-2020 
        model_obj = self.env[model_name] #.sudo()
        rec = model_obj.browse(rec_id)
        # Validation
        if rec.state == self.node_from.node_name:
            rec.state = self.node_to.node_name
        return True


class OdooWorkflowNodeButton(models.Model):
    _name = 'odoo.workflow.node.button'
    _description = 'Odoo Workflow Node Buttons'
    _order = 'sequence'

    def _generate_key(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

    name = fields.Char(string='Button String', translate=True,
                       help="Enter button string name that will appear in the view.")
    sequence = fields.Integer(string='Sequence', default=10, help="Arrange buttons by defining sequence.")
    is_highlight = fields.Boolean(string='Is Highlighted', default=True,
                                  help="Control highlighting of the button if needs user attention..")
    has_icon = fields.Boolean(string='Has Icon', help="Enable it to add icon to the button.")
    icon = fields.Char(string='Icon', help="Enter icon name like: fa-print, it's recommended to use FontAwesome Icons.")
    btn_key = fields.Char(string='Button Key', default=_generate_key)
    btn_hide = fields.Boolean(string="Hide Button if Condition isn't fulfilled",
                              help="If condition is false the button will be hidden.")

    """
    New columns added to hide the button on view as per the model field conditions: 
    By - T Ketaki Debadarshini  
    """
    custom_domain   = fields.Boolean(string='Custom Domain', help="Enable it to add custom domain.")
    def _generate_default_domain(self):
        if self.env.context.get('default_node_id', 0):
            node_name = self.env['odoo.workflow.node'].sudo().browse(self.env.context.get('default_node_id')).node_name
            return """[('state', '!=', '%s')]""" % node_name
        else:
            return BTN_HIDE_DOMAIN

    btn_hide_user_domain = fields.Text(string='Button User Defined Invisible Property',default=_generate_default_domain,help="Enter domain condition to hide button.")
    btn_hide_domain      = fields.Text(string='Button Invisible Property',default=_generate_default_domain,help="Enter domain condition to hide button.")
    btn_hide_group       = fields.Text(string='Button Groups', help="Enter group names comma separated.")

    
    model_id             = fields.Many2one('ir.model',string='Model Ref.',related="workflow_id.model_id")
    model_name           = fields.Char(string='Model Ref.',related="model_id.model")
    btn_permitted_group_ids = fields.Many2many(string='Permitted Groups',comodel_name='res.groups',)

    send_notification    = fields.Boolean(string='Send Notification', )
    mail_template_id     = fields.Many2one("mail.template", string="E-mail Template")
    # notify_group_ids     = fields.Many2many(string='Notification Groups',comodel_name='res.groups',)
    
    notify_group_ids     = fields.Many2many(string='Notification Groups',comodel_name='res.groups',relation='res_group_workflow_button_mail_rel',column1='button_id',column2='group_id',)
    
    
    """ 
    New columns added to hide the button on view as per the model field conditions: 
    By - T Ketaki Debadarshini  
    """

    condition_code  = fields.Text(string='Condition Code', default=CONDITION_CODE_TEMP, help="Enter condition to execute button action.")
    action_type     = fields.Selection([
                    ('link', 'Trigger Link'),
                    ('code', 'Python Code'),
                    ('action', 'Server Action'),
                    ('win_act', 'Window Action'),
                ], string='Action Type', default='link', help="Choose type of action to be trigger by the button.")

    link_id = fields.Many2one('odoo.workflow.link', string='Link')
    code = fields.Text(string='Python Code', default=PYTHON_CODE_TEMP)
    server_action_id = fields.Many2one('ir.actions.server', string='Server Action')
    win_act_id = fields.Many2one('ir.actions.act_window', string='Window Action')
    node_id = fields.Many2one('odoo.workflow.node', string='Workflow Node Ref.', ondelete='cascade', required=True)
    workflow_id = fields.Many2one('odoo.workflow', string='Workflow Ref.', required=True)
    """New field added for button class: Girish Kumar Mohanta on 1-Sep-2020"""
    btn_class = fields.Selection([
        ('btn-primary', 'Primary'),
        ('btn-secondary', 'Secondary'),
        ('btn-success', 'Success'),
        ('btn-danger', 'Danger'),
        ('btn-warning', 'Warning'),
        ('btn-info', 'Info'),
        ('btn-light', 'Light'),
        ('btn-dark', 'Dark'),
        ('btn-link', 'Link')
    ], default='btn-primary', string='Button Class',)
    need_confirm = fields.Boolean('Need Confirmation Message')
    confirm_msg = fields.Char('Confirmation Message')

    @api.onchange('node_id')
    def change_workflow(self):
        for rec in self:
            if isinstance(rec.id, int) and rec.node_id and rec.node_id.workflow_id:
                rec.workflow_id = rec.node_id.workflow_id.id
            elif self.env.context.get('default_node_id', 0):
                model_id = self.env['odoo.workflow.node'].sudo().browse(self.env.context.get('default_node_id')).model_id.id
                rec.workflow_id = self.env['odoo.workflow'].sudo().search([('model_id', '=', model_id)])

    @api.constrains('btn_key')
    def validation(self):
        for rec in self:
            # Check if there is no duplicate button key
            res = self.search_count([
                ('id', '!=', rec.id),
                ('btn_key', '=', rec.btn_key),
            ])
            if res:
                rec.btn_key = self._generate_key()

    @api.multi
    def run(self):
        for rec in self:
            # Check Condition Before Executing Action
            result = False
            cx = self.env.context.copy() or {}
            act_record = self.env[cx.get('active_model', False)].browse(cx.get('active_id', 0))
            locals_dict = {
                'env'       : self.env,
                'model'     : self.env[cx.get('active_model', False)],
                'obj'       : act_record,
                'user'      : self.env.user,
                'datetime'  : datetime,
                'time'      : time,
                'date'      : date,
                'timedelta' : timedelta,
                'workflow'  : self.env['odoo.workflow'],
                'warning'   : self.warning,
                'syslog'    : self.syslog,
            }
            try:
                eval(rec.condition_code, locals_dict=locals_dict, mode='exec', nocopy=True)
                # print(locals_dict)
                result = 'result' in locals_dict and locals_dict['result'] or False
            except ValidationError as ex:
                raise ex
            except SyntaxError as ex:
                raise UserError(_("Wrong python code defined.\n\nError: %s\nLine: %s, Column: %s\n\n%s" % (
                ex.args[0], ex.args[1][1], ex.args[1][2], ex.args[1][3])))
            if result:
                # print("inside result section ---")
                # Run Proper Action
                func = getattr(self, "_run_%s" % rec.action_type)
                res  = func()
                ##code modified by T Ketaki Debadarshini, On -26th Oct 2020
                if res:
                    rec.send_notification_to_groups(act_record)
                return res

    @api.multi
    def _run_win_act(self):
        # Variables
        cx = self.env.context.copy() or {}
        win_act_obj = self.env['ir.actions.act_window']
        # Run Window Action
        for rec in self:
            action = win_act_obj.with_context(cx).browse(rec.win_act_id.id).read()[0]
            action['context'] = cx
            return action
        return False

    @api.multi
    def _run_action(self):
        # Variables
        srv_act_obj = self.env['ir.actions.server']
        # Run Server Action
        for rec in self:
            srv_act_rec = srv_act_obj.browse(rec.server_action_id.id)
            return srv_act_rec.run()

    @api.multi
    def _run_code(self):
        # Variables
        cx = self.env.context.copy() or {}
        locals_dict = {
            'env'       : self.env,
            'model'     : self.env[cx.get('active_model', False)],
            'obj'       : self.env[cx.get('active_model', False)].browse(cx.get('active_id', 0)),
            'user'      : self.env.user,
            'datetime'  : datetime,
            'time'      : time,
            'date'      : date,
            'timedelta' : timedelta,
            'workflow'  : self.env['odoo.workflow'],
            'warning'   : self.warning,
            'syslog'    : self.syslog,
        }
        # Run Code
        for rec in self:
            try:
                eval(rec.code, locals_dict=locals_dict, mode='exec', nocopy=True)
                action = 'action' in locals_dict and locals_dict['action'] or False
                if action:
                    return action
            except Warning as ex:
                raise ex
            except SyntaxError as ex:
                raise UserError(_("Wrong python code defined.\n\nError: %s\nLine: %s, Column: %s\n\n%s" % (ex.args[0], ex.args[1][1], ex.args[1][2], ex.args[1][3])))
        return True

    @api.multi
    def _run_link(self):
        for rec in self:
            # Check Condition Before Executing Action
            result = False
            cx = self.env.context.copy() or {}
            act_record = self.env[cx.get('active_model', False)].browse(cx.get('active_id', 0))
            locals_dict = {
                'env'       : self.env,
                'model'     : self.env[cx.get('active_model', False)],
                'obj'       : act_record,
                'user'      : self.env.user,
                'datetime'  : datetime,
                'time'      : time,
                'date'      : date,
                'timedelta' : timedelta,
                'workflow'  : self.env['odoo.workflow'],
                'warning'   : self.warning,
                'syslog'    : self.syslog,
            }
            try:
                eval(rec.link_id.condition_code, locals_dict=locals_dict, mode='exec', nocopy=True)
                result = 'result' in locals_dict and locals_dict['result'] or False
            except ValidationError as ex:
                raise ex
            except SyntaxError as ex:
                raise UserError(_("Wrong python code defined.\n\nError: %s\nLine: %s, Column: %s\n\n%s" % (
                ex.args[0], ex.args[1][1], ex.args[1][2], ex.args[1][3])))
            if result:
               
                # Trigger link function
                return rec.link_id.trigger_link()

    def warning(self, msg):
        if not isinstance(msg, str):
            msg = str(msg)
        raise Warning(msg)

    def syslog(self, msg):
        if not isinstance(msg, str):
            msg = str(msg)
        _logger.info(msg)

    """send notification to the selected user group after the button action triggers.., Created By : T Ketaki Debadarshini, Created On: 26-Oct-2020"""
    @api.multi
    def send_notification_to_groups(self,act_record):
        self.ensure_one()

        template    = self.mail_template_id 
        partner_to  = self.notify_group_ids.mapped('users').mapped('email') 
        # print(self.notify_group_ids.mapped('users'))
        # print(self.notify_group_ids.mapped('users').mapped('email'))
        # print(partner_to)
        if self.send_notification and template and partner_to:
            # print('------------------')
            # partner_tos = [str(follow.partner_id.id) for follow in self.notify_group_ids.mapped('users')]
            redirect_url = self.node_id.get_url(act_record.id)
            context_vals = {
                'email_to'      : ','.join(partner_to),
                # 'partner_to'    :','.join(partner_tos),
                'record'        : self.node_id,
                'pre_stage'     : self.node_id.name,
                'description'   : act_record._description,
                'name'          : act_record.name_get()[0][1],
                'act_record'    : act_record,
                'rec_res_id'    : act_record.id,
                'redirect_url'  : redirect_url
            }
            
            res = self.workflow_send_custom_mail(res_id=self.node_id.id,notif_layout='mail.mail_notification_light',template_layout=template,ctx_params=context_vals,description="")
            #template.with_context(context_vals).send_mail(self.node_id.id, force_send=False,notif_layout='mail.mail_notification_light')            
            return res

     ##send custom email by chnaging the model description 
    def workflow_send_custom_mail(self,res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False,template_layout=False,ctx_params=None,description=False):

        template        = template_layout       
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values       = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})
            # print(values)                    
            
            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            # encapsulate body
            if notif_layout and values['body_html']:
                try:
                    notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    pass
                else:
                    record = self.env[template.model].browse(res_id)
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name='')),
                        'model_description': 'Notification',
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            mail = self.env['mail.mail'].create(values)

            if force_send:
                mail.send(raise_exception=raise_exception)
            return mail.id  




class OdooWorkflowNodeField(models.Model):
    _name        = 'odoo.workflow.node.field'
    _description = 'Odoo Workflow Node Fields'

    name        = fields.Many2one('ir.model.fields', string='Field')
    model_id    = fields.Many2one('ir.model', string='Model', domain="[('state','in',['base','manual'])]")
    readonly    = fields.Boolean(string='Readonly')
    required    = fields.Boolean(string='Required')
    invisible   = fields.Boolean(string='Invisible')
    group_ids   = fields.Many2many('res.groups', string='Groups')
    user_ids    = fields.Many2many('res.users', string='Users')
    node_id     = fields.Many2one('odoo.workflow.node', string='Node Ref.', ondelete='cascade', required=True)
