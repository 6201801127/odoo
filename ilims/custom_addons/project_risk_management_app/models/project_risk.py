from odoo import api, fields, models, _
from odoo.osv import expression


class ProjectRisk(models.Model):
    _name = 'project.risk'
    _description = 'project risk'
    _rec_name = 'code'

    risk_name = fields.Char("Name", required=True, track_visibility='always')
    code = fields.Char(string='Code', copy=False, track_visibility='always', readonly=True, index=True,
                       default=lambda self: _(''))
    risk_quantification = fields.Selection([
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('low', 'Low'),
        ('Critical', 'Critical')
    ], 'Risk Quantification', track_visibility='always')
    risk_category_id = fields.Many2one('risk.category', "Category ", track_visibility='always')
    risk_type_id = fields.Many2one('risk.type', "Type of Risk", track_visibility='always')
    risk_response_id = fields.Many2one('risk.response', " Response of Risk", track_visibility='always')
    internal_note = fields.Text("Risk Description", track_visibility='always')
    risk_impact = fields.Char('Risk Impact')

    # @api.onchange('stage_id')
    # def _onchange_stage_id(self):
    #     print('=============]]]]]]]]]]]', 'changed stage')
    #     users_obj = self.env['res.users']
    #     notification_ids = []
    #     if self.user_id:
    #         notification_ids.append((0, 0, {
    #             'res_partner_id': self.user_id.partner_id.id,
    #             'notification_type': 'inbox'
    #         }))
    #     if self.project_id and self.project_id.stakeholder_ids:
    #         for lines in self.project_id.stakeholder_ids:
    #             user = users_obj.search([('partner_id', '=', lines.partner_id.id)], limit=1)
    #             notification_ids.append((0, 0, {
    #                 'res_partner_id': user.partner_id.id,
    #                 'notification_type': 'inbox'}))
    #     message = 'Risk Incident stage has benn changed By ' + str(self.env.user.name)
    #
    #     # Notification to the user for closer of chnage request
    #
    #     self.message_post(body=message, message_type='notification',
    #                       subtype_xmlid='mail.mt_comment', author_id=self.env.user.partner_id.id,
    #                       notification_ids=notification_ids)

    # create sequence for risk
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('seq.sh_risk_task') or _('New')
        result = super(ProjectRisk, self).create(vals)
        return result

    def name_get(self):
        res = []
        for record in self:
            name = "[" + str(record.code) + "] " + str(record.risk_name)
            res.append((record.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = ['|', ('risk_name', operator, name), ('code', operator, name)]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return super(ProjectRisk, self)._name_search(name=name, args=args, operator=operator,
                                                                      limit=limit, name_get_uid=name_get_uid)


class ProjectRiskLine(models.Model):
    _name = 'project.risk.line'
    _description = 'Project Risk Line'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string='Project', tracking=True)
    task_id = fields.Many2one('project.task', string='Task', tracking=True)
    project_risk_id = fields.Many2one('project.risk', string='Risk', tracking=True)
    description = fields.Text("Description")
    category_id = fields.Many2one('risk.category', string='Category of Risk', track_visibility='always')
    response_id = fields.Many2one('risk.response', string='Response of Risk', tracking=True)
    type_id = fields.Many2one('risk.type', string='Type of Risk', tracking=True)
    probability = fields.Float("Risk Probability(%)", tracking=True)
    name_title = fields.Char(readonl=True, tracking=True)
    risk_impact = fields.Text('Risk Impact', tracking=True)
    status = fields.Selection([
        ('close', 'Close'),                                     #('accept', 'Accept'),
        ('open', 'Open')                                        # ('reject', 'Reject')
    ], string='Status', tracking=True)

    @api.onchange('project_risk_id')
    def onchange_project_risk(self):
        if self.project_risk_id:
            self.risk_impact = self.project_risk_id.risk_impact
            self.description = self.project_risk_id.internal_note
            self.category_id = self.project_risk_id.risk_category_id or False
            self.response_id = self.project_risk_id.risk_response_id or False
            self.type_id = self.project_risk_id.risk_type_id or False

    def write(self, vals):
        prev_risk = "[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name
        prev_impact = self.risk_impact
        prev_description = self.description or None
        prev_category = self.category_id.name
        prev_response = self.response_id.name
        prev_type = self.type_id.name
        prev_probability = self.probability
        prev_status = dict(self._fields['status'].selection).get(self.status)
        rec = super(ProjectRiskLine, self).write(vals)
        message_body = """<b>Risk Register</b><br/>"""
        if prev_risk == "[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name:
            message_body += """• Risk: {prev_risk} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {risk} <br/>""".format(
                prev_risk=prev_risk, risk="[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name
            )
        else:
            message_body += """<span style='color:red;'>• Risk: {prev_risk} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {risk}</span><br/>""".format(
                prev_risk=prev_risk, risk="[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name
            )
        if prev_impact == self.risk_impact:
            message_body += """• Risk Impact: {prev_impact} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {impact}<br/>""".format(
                prev_impact=prev_impact, impact=self.risk_impact
            )
        else:
            message_body += """<span style='color:red;'>• Risk Impact: {prev_impact} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {impact}</span><br/>""".format(
                prev_impact=prev_impact, impact=self.risk_impact
            )
        new_prev_description = self.description or None
        if prev_description == new_prev_description:
            message_body += """• Description: {prev_description} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}<br/>""".format(
                prev_description=prev_description, description=self.description or None
            )
        else:
            message_body += """<span style='color:red;'>• Description: {prev_description} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}</span><br/>""".format(
                prev_description=prev_description, description=self.description or None
            )
        if prev_category == self.category_id.name:
            message_body += """• Category of Risk: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}<br/>""".format(
                prev_category=prev_category, category=self.category_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Category of Risk: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}</span><br/>""".format(
                prev_category=prev_category, category=self.category_id.name
            )
        if prev_response == self.response_id.name:
            message_body += """• Response of Risk: {prev_response} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {response}<br/>""".format(
                prev_response=prev_response, response=self.response_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Response of Risk: {prev_response} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {response}</span><br/>""".format(
                prev_response=prev_response, response=self.response_id.name
            )
        if prev_type == self.type_id.name:
            message_body += """• Type of Risk: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}<br/>""".format(
                prev_type=prev_type, type=self.type_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Type of Risk: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}</span><br/>""".format(
                prev_type=prev_type, type=self.type_id.name
            )
        if prev_probability == self.probability:
            message_body += """• Probability: {prev_probability} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {probability}<br/>""".format(
                prev_probability=prev_probability, probability=self.probability
            )
        else:
            message_body += """<span style='color:red;'>• Probability: {prev_probability} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {probability}</span><br/>""".format(
                prev_probability=prev_probability, probability=self.probability
            )
        if prev_status == dict(self._fields['status'].selection).get(self.status):
            message_body += """• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}""".format(
                prev_status=prev_status, status=dict(self._fields['status'].selection).get(self.status)
            )
        else:
            message_body += """<span style='color:red;'>• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}</span>""".format(
                prev_status=prev_status, status=dict(self._fields['status'].selection).get(self.status)
            )
        # message_body = """<b>Risk Register</b><br/>
        #                 • Risk: {prev_risk} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {risk} <br/>
        #                 • Risk Impact: {prev_impact} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {impact}<br/>
        #                 • Description: {prev_description} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}<br/>
        #                 • Category of Risk: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}<br/>
        #                 • Response of Risk: {prev_response} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {response}<br/>
        #                 • Type of Risk: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}<br/>
        #                 • Probability: {prev_probability} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {probability}<br/>
        #                 • Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}"""\
        #     .format(prev_risk=prev_risk, risk="[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name,
        #             prev_impact=prev_impact, impact=self.risk_impact,
        #             prev_description=prev_description, description=self.description or '',
        #             prev_category=prev_category, category=self.category_id.name,
        #             prev_response=prev_response, response=self.response_id.name,
        #             prev_type=prev_type, type=self.type_id.name,
        #             prev_probability=prev_probability, probability=self.probability,
        #             prev_status=prev_status, status=dict(self._fields['status'].selection).get(self.status))
        self.project_id.message_post(body=message_body)
        return rec


class TaskRiskLine(models.Model):
    _name = 'task.risk.line'
    _description = 'Project Task Risk Line'
    _rec_name = 'task_id'

    task_id = fields.Many2one('project.task', string='Task Name', tracking=True)
    project_id = fields.Many2one('project.project', related="task_id.project_id", string='Project', tracking=True)
    project_risk_id = fields.Many2one('project.risk', string='Risk Name', tracking=True)
    description = fields.Text("Description")
    category_id = fields.Many2one('risk.category', string='Category of Risk', track_visibility='always')
    response_id = fields.Many2one('risk.response', string='Response of Risk', tracking=True)
    type_id = fields.Many2one('risk.type', string='Type of Risk', tracking=True)
    probability = fields.Float("Risk Probability(%)",tracking=True)
    risk_impact = fields.Char('Risk Impact', tracking=True)
    mitigation_type_id = fields.Many2one('mitigation.type', string='Mitigation Type')
    status = fields.Selection([
        ('accept', 'Accept'),
        ('reject', 'Reject')
    ], string='Status', tracking=True)

    @api.onchange('project_risk_id')
    def onchange_project_risk(self):
        if self.project_risk_id:
            self.risk_impact = self.project_risk_id.risk_impact
            self.description = self.project_risk_id.internal_note
            self.category_id = self.project_risk_id.risk_category_id or False
            self.response_id = self.project_risk_id.risk_response_id or False
            self.type_id = self.project_risk_id.risk_type_id or False

    def write(self, vals):
        prev_risk = "[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name
        prev_impact = self.risk_impact
        prev_description = self.description or None
        prev_category = self.category_id.name
        prev_response = self.response_id.name
        prev_type = self.type_id.name
        prev_probability = self.probability
        prev_status = dict(self._fields['status'].selection).get(self.status)
        rec = super(TaskRiskLine, self).write(vals)
        message_body = """<b>Risk Register</b><br/>"""
        if prev_risk == "[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name:
            message_body += """• Risk: {prev_risk} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {risk} <br/>""".format(
                prev_risk=prev_risk, risk="[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name
            )
        else:
            message_body += """<span style='color:red;'>• Risk: {prev_risk} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {risk}</span><br/>""".format(
                prev_risk=prev_risk, risk="[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name
            )
        if prev_impact == self.risk_impact:
            message_body += """• Risk Impact: {prev_impact} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {impact}<br/>""".format(
                prev_impact=prev_impact, impact=self.risk_impact
            )
        else:
            message_body += """<span style='color:red;'>• Risk Impact: {prev_impact} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {impact}</span><br/>""".format(
                prev_impact=prev_impact, impact=self.risk_impact
            )
        new_prev_description = self.description or None
        if prev_description == new_prev_description:
            message_body += """• Description: {prev_description} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}<br/>""".format(
                prev_description=prev_description, description=self.description or None
            )
        else:
            message_body += """<span style='color:red;'>• Description: {prev_description} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}</span><br/>""".format(
                prev_description=prev_description, description=self.description or None
            )
        if prev_category == self.category_id.name:
            message_body += """• Category of Risk: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}<br/>""".format(
                prev_category=prev_category, category=self.category_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Category of Risk: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}</span><br/>""".format(
                prev_category=prev_category, category=self.category_id.name
            )
        if prev_response == self.response_id.name:
            message_body += """• Response of Risk: {prev_response} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {response}<br/>""".format(
                prev_response=prev_response, response=self.response_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Response of Risk: {prev_response} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {response}</span><br/>""".format(
                prev_response=prev_response, response=self.response_id.name
            )
        if prev_type == self.type_id.name:
            message_body += """• Type of Risk: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}<br/>""".format(
                prev_type=prev_type, type=self.type_id.name
            )
        else:
            message_body += """<span style='color:red;'>• Type of Risk: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}</span><br/>""".format(
                prev_type=prev_type, type=self.type_id.name
            )
        if prev_probability == self.probability:
            message_body += """• Probability: {prev_probability} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {probability}<br/>""".format(
                prev_probability=prev_probability, probability=self.probability
            )
        else:
            message_body += """<span style='color:red;'>• Probability: {prev_probability} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {probability}</span><br/>""".format(
                prev_probability=prev_probability, probability=self.probability
            )
        if prev_status == dict(self._fields['status'].selection).get(self.status):
            message_body += """• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}""".format(
                prev_status=prev_status, status=dict(self._fields['status'].selection).get(self.status)
            )
        else:
            message_body += """<span style='color:red;'>• Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}</span>""".format(
                prev_status=prev_status, status=dict(self._fields['status'].selection).get(self.status)
            )
        # message_body = """<b>Risk Register</b><br/>
        #                 • Risk: {prev_risk} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {risk} <br/>
        #                 • Risk Impact: {prev_impact} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {impact}<br/>
        #                 • Description: {prev_description} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {description}<br/>
        #                 • Category of Risk: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}<br/>
        #                 • Response of Risk: {prev_response} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {response}<br/>
        #                 • Type of Risk: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}<br/>
        #                 • Probability: {prev_probability} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {probability}<br/>
        #                 • Status: {prev_status} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {status}"""\
        #     .format(prev_risk=prev_risk, risk="[" + self.project_risk_id.code + "] " + self.project_risk_id.risk_name,
        #             prev_impact=prev_impact, impact=self.risk_impact,
        #             prev_description=prev_description, description=self.description or '',
        #             prev_category=prev_category, category=self.category_id.name,
        #             prev_response=prev_response, response=self.response_id.name,
        #             prev_type=prev_type, type=self.type_id.name,
        #             prev_probability=prev_probability, probability=self.probability,
        #             prev_status=prev_status, status=dict(self._fields['status'].selection).get(self.status))
        self.task_id.message_post(body=message_body)
        return rec
