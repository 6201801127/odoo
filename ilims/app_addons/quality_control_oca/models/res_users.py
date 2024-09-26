from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        rec = super(ResUsers, self).create(vals)
        if rec:
            if rec.has_group('gts_groups.group_quality_management_can_create') and not rec.has_group(
                    'quality_control_oca.group_quality_control_user'):
                raise ValidationError(_(
                    'Cannot give access of Quality Can Create until user has access of Quality Control App (User/Manager)'))
            if rec.has_group('gts_groups.group_quality_management_can_approve') and not rec.has_group(
                    'quality_control_oca.group_quality_control_user'):
                raise ValidationError(_(
                    'Cannot give access of Quality Can Approve until user has access of Quality Control App (User/Manager)'))
        return rec

    def write(self, vals):
        rec = super(ResUsers, self).write(vals)
        for record in self:
            if record.has_group('gts_groups.group_quality_management_can_create') and not record.has_group(
                    'quality_control_oca.group_quality_control_user'):
                raise ValidationError(_(
                    'Cannot give access of Quality Can Create until user has access of Quality Control App (User/Manager)'))
            if record.has_group('gts_groups.group_quality_management_can_approve') and not record.has_group(
                    'quality_control_oca.group_quality_control_user'):
                raise ValidationError(_(
                    'Cannot give access of Quality Can Approve until user has access of Quality Control App (User/Manager)'))
        return rec
