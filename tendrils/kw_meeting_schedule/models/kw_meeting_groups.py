from odoo import models, fields, api


class kw_meeting_user_groups(models.Model):
    _name = 'kw_meeting_user_groups'
    _description = 'Meeting Groups'


    name = fields.Char(string="Group Name", required=True, translate=True)
    parent_path = fields.Char(string="Parent Path", index=True)
    count_users = fields.Integer(string="Users", store=True, compute='_compute_users')
    meeting_type_id = fields.Many2one('calendar.event.type',string="Meeting Type")

    @api.model
    def _add_magic_fields(self):
        super(kw_meeting_user_groups, self)._add_magic_fields()

        def add(name, field):
            if name not in self._fields:
                self._add_field(name, field)

        add('parent_group',
            fields.Many2one(
                _module=self._module,
                comodel_name=self._name,
                string='Parent Group',
                ondelete='cascade',
                auto_join=True,
                index=True,
                automatic=True))
        add('child_groups', fields.One2many(
            _module=self._module,
            comodel_name=self._name,
            inverse_name='parent_group',
            string='Child Groups',
            automatic=True))
        add('groups',
            fields.Many2many(
                _module=self._module,
                comodel_name='res.groups',
                relation='%s_groups_rel' % (self._table),
                column1='gid',
                column2='rid',
                string='Groups',
                automatic=True))
        add('explicit_users', fields.Many2many(
            _module=self._module,
            comodel_name='res.users',
            relation='%s_explicit_users_rel' % (self._table),
            column1='gid',
            column2='uid',
            string='Explicit Users',
            automatic=True))
        add('users',
            fields.Many2many(
                _module=self._module,
                comodel_name='res.users',
                relation='%s_users_rel' % (self._table),
                column1='gid',
                column2='uid',
                string='Group Users',
                compute='_compute_users',
                store=True,
                automatic=True))

    @api.model
    def default_get(self, fields_list):
        res = super(kw_meeting_user_groups, self).default_get(fields_list)
        if not self.env.context.get('groups_no_autojoin'):
            if 'explicit_users' in res and res['explicit_users']:
                res['explicit_users'] = res['explicit_users'] + [self.env.uid]
            else:
                res['explicit_users'] = [self.env.uid]
        return res

    # ----------------------------------------------------------
    # Read, View
    # ----------------------------------------------------------

    @api.depends('parent_group', 'parent_group.users', 'groups', 'groups.users', 'explicit_users')
    def _compute_users(self):
        for record in self:
            users = record.mapped('groups.users')
            users |= record.mapped('explicit_users')
            users |= record.mapped('parent_group.users')
            record.update({'users': users, 'count_users': len(users)})
