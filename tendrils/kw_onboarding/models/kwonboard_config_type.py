from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwonboard_config_type_master(models.Model):
    _name = 'kwonboard_config_type_master'
    _description = "A master model for the configuration type."

    name = fields.Char('Name')
    code = fields.Char('Code')
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        record = super(kwonboard_config_type_master, self).create(values)
        if record:
            self.env.user.notify_success(message='Configuration has been Created Successfully.')
        return record

    @api.multi
    def write(self, values):
        self.ensure_one()
        record = super(kwonboard_config_type_master, self).write(values)
        self.env.user.notify_info(message='Configuration has been Updated Successfully.')
        return record

    @api.multi
    def unlink(self):
        for rec in self:
            if self.env['kwonboard_config_type'].sudo().search([('configuration_type_id','=',rec.id)]):
                raise ValidationError(f"{rec.name} can not be removed!")
        return super(kwonboard_config_type_master, self).unlink()

    @api.constrains('name','code')
    def check_constrains(self):
        for rec in self:
            if self.env['kwonboard_config_type_master'].search([('name','=',rec.name)]) - self:
                raise ValidationError(f'Name {rec.name} already exists!')
            if self.env['kwonboard_config_type_master'].search([('code','=',rec.code)]) - self:
                raise ValidationError(f'Code {rec.code} already exists!')

class kwonboard_config_type(models.Model):
    _name = 'kwonboard_config_type'
    _description = "A master model for the internal environment configuration  of employees according to groups."
    _rec_name = 'configuration_type_id'

    # ***do not modify the selection values without consulting the author: Ketaki
    configuration_type_id = fields.Many2one('kwonboard_config_type_master', string="Configuration Type", required=False)
    # configuration_type = fields.Selection(string="Configuration Type",
    #                                       selection=[('1', 'ID Card Creation'), ('2', 'Budget Tagging'),
    #                                                  ('3', 'Outlook ID Creation'), ('4', 'Biometric ID Creation'),
    #                                                  ('5', 'System Domain Config'), ('6', 'EPBX Setting'), ],
    #                                       required=False)

    authorized_group = fields.Many2many('res.groups', ondelete='cascade', required=True)

    # config_option_type= fields.Selection(string="Type",selection=[('1', 'Compulsory'),('2', 'Optional'),],)

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         record_name = dict(self._fields['configuration_type'].selection).get(
    #             self.configuration_type)  # record.movie + ' - ' + record.seat_number
    #         result.append((record.id, record_name))
    #     return result

    @api.constrains('config_option_type', 'authorized_group')
    def validate_configuration(self):
        for record in self:
            if not (record.authorized_group):
                raise ValidationError("Please add at least one authorized group.")
        record = self.env['kwonboard_config_type'].sudo().search([]) - self
        for data in record:
            if data.configuration_type_id == self.configuration_type_id:
                raise ValidationError("This configuration type is already exists.")

    # method to override the create method and inherit the groups as per the responsible groups
    @api.model
    def create(self, vals):
        config_record = super(kwonboard_config_type, self).create(vals)
        if config_record.authorized_group:
            # add the group to the inherited group list
            if config_record.configuration_type_id.code == 'idcard':
                config_record.authorized_group.sudo().write(
                    {'implied_ids': [[4, self.env.ref('kw_onboarding.group_kw_onboarding_admin').id, False]]})

            elif config_record.configuration_type_id.code == 'budget':
                config_record.authorized_group.sudo().write(
                    {'implied_ids': [[4, self.env.ref('kw_onboarding.group_kw_onboarding_finance').id, False]]})

            elif config_record.configuration_type_id.code in ['outlookid', 'biometric', 'system', 'epbx']:
                config_record.authorized_group.sudo().write(
                    {'implied_ids': [[4, self.env.ref('kw_onboarding.group_kw_onboarding_nsa').id, False]]})
            elif config_record.configuration_type_id.code in ['sbu']:
                config_record.authorized_group.sudo().write(
                    {'implied_ids': [[4, self.env.ref('kw_onboarding.group_kw_onboarding_rcm').id, False]]})


        if config_record:
            self.env.user.notify_success(message='Configuration type created successfully')
        else:
            self.env.user.notify_danger(message='Configuration type creation failed')

        return config_record

    @api.multi
    def write(self, vals):

        old_grp_rec_set = self.authorized_group
        config_record = super(kwonboard_config_type, self).write(vals)

        # check groups those are deleted
        del_grp_recset = old_grp_rec_set - self.authorized_group

        # get the id of publisher group
        admin_grp_id = self.env.ref('kw_onboarding.group_kw_onboarding_admin').id
        finance_grp_id = self.env.ref('kw_onboarding.group_kw_onboarding_finance').id
        nsa_grp_id = self.env.ref('kw_onboarding.group_kw_onboarding_nsa').id
        rcm_group_id = self.env.ref('kw_onboarding.group_kw_onboarding_rcm')

        # add the group to the inherited group list
        if self.authorized_group:
            if self.configuration_type_id.code == 'idcard':
                self.authorized_group.sudo().write({'implied_ids': [[4, admin_grp_id, False]]})

            elif self.configuration_type_id.code == 'budget':
                self.authorized_group.sudo().write({'implied_ids': [[4, finance_grp_id, False]]})

            elif self.configuration_type_id.code in ['outlookid', 'biometric', 'system', 'epbx']:
                self.authorized_group.sudo().write({'implied_ids': [[4, nsa_grp_id, False]]})
            elif self.configuration_type_id.code in  ['sbu']:
                self.authorized_group.sudo().write({'implied_ids': [[4, rcm_group_id, False]]})
              

                # removes  group from the inherited group list
        if len(del_grp_recset) > 0:
            if self.configuration_type_id.code == 'idcard':
                del_grp_recset.sudo().write({'implied_ids': [[3, admin_grp_id, False]]})

            elif self.configuration_type_id.code == 'budget':
                del_grp_recset.sudo().write({'implied_ids': [[3, finance_grp_id, False]]})

            elif self.configuration_type_id.code in ['outlookid', 'biometric', 'system', 'epbx']:
                del_grp_recset.sudo().write({'implied_ids': [[3, nsa_grp_id, False]]})
            elif self.configuration_type_id.code in ['sbu']:
                del_grp_recset.sudo().write({'implied_ids': [[3, rcm_group_id, False]]})

        if config_record:
            self.env.user.notify_success(message='Configuration type updated successfully')
        else:
            self.env.user.notify_danger(message='Configuration type update failed')

        return True
