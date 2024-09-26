from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RiskType(models.Model):
    _name = 'risk.type'
    _description = 'Risk Type'

    name = fields.Char("Risk Name", track_visibility='always')
    code = fields.Char(string='Code', copy=False, readonly=True, track_visibility='always',
                       index=True, default=lambda self: _(''))
    internal_note = fields.Text("")

    def unlink(self):
        for order in self:
            if order.name:
                raise UserError(_('You cannot Delete Risk Type  record'))
        return super(RiskType, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('seq.sh_risk_type') or _('New')
        result = super(RiskType, self).create(vals)
        return result


class RiskCategory(models.Model):
    _name = 'risk.category'
    _description = 'Risk category'

    name = fields.Char("Category Name", track_visibility='always')
    code = fields.Char(string='Code', copy=False, readonly=True, track_visibility='always',
                       index=True, default=lambda self: _(''))
    internal_note = fields.Text("")

    def unlink(self):
        for order in self:
            if order.name:
                raise UserError(_('You cannot Delete Risk Category  record'))
        return super(RiskCategory, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('seq.sh_risk_category') or _('New')
        result = super(RiskCategory, self).create(vals)
        return result


class RiskResponse(models.Model):
    _name = 'risk.response'
    _description = 'Risk response'

    name = fields.Char('Response Name', track_visibility='always')
    code = fields.Char(string='Code', copy=False, readonly=True, track_visibility='always',
                       index=True, default=lambda self: _(''))
    internal_note = fields.Text("")

    def unlink(self):
        for order in self:
            if order.name:
                raise UserError(_('You cannot Delete Risk Response  record'))
        return super(RiskResponse, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('seq.sh_risk_responce') or _('New')
        result = super(RiskResponse, self).create(vals)
        return result


class MitigationType(models.Model):
    _name = 'mitigation.type'
    _description = 'Mitigation Type'

    name = fields.Char('Name')
