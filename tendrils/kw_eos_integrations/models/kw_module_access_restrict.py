from odoo import _, models, fields, api
from odoo.exceptions import ValidationError


class kw_resignation(models.Model):
    _inherit = "kw_resignation"

    def check_user_resign_status(self):
        offboard_rec = False
        if self.env.user.employee_ids:
            offboard_rec = self.env['kw_resignation'].sudo().search(
                [('applicant_id', '=', self.env.user.employee_ids.id), ('offboarding_type.code', '=', 'reg'),
                 ('state', 'not in', ['exemployee', 'reject', 'cancel'])])
        # 'apply', 'forward',
        return offboard_rec or False


class kw_visiting_card(models.Model):
    _inherit = "kw_visiting_card_apply"

    @api.model
    def default_get(self, fields):
        res = super(kw_visiting_card, self).default_get(fields)
        offboard_rec = self.env['kw_resignation'].check_user_resign_status()
        if offboard_rec:
            raise ValidationError(
                _(f'You can not apply for visiting card, as you have already applied {offboard_rec.offboarding_type.name}.'))
        return res


# class kw_tour_apply(models.Model):
#     _inherit = "kw_tour"

#     @api.model
#     def default_get(self, fields):
#         res = super(kw_tour_apply, self).default_get(fields)
#         offboard_rec = self.env['kw_resignation'].check_user_resign_status()
#         if offboard_rec:
#             raise ValidationError(
#                 _(f'You can not apply for tour, as you have already applied {offboard_rec.offboarding_type.name}.'))
#         return res


class kw_leave_apply(models.Model):
    _inherit = "hr.leave"

    @api.model
    def default_get(self, fields):
        res = super(kw_leave_apply, self).default_get(fields)
        offboard_rec = self.env['kw_resignation'].check_user_resign_status()
        if offboard_rec:
            raise ValidationError(
                _(f'You can not apply for leave, as you have already applied {offboard_rec.offboarding_type.name}.'))
        return res


class kw_salary_advance(models.Model):
    _inherit = "kw_advance_apply_salary_advance"

    @api.model
    def default_get(self, fields):
        res = super(kw_salary_advance, self).default_get(fields)
        offboard_rec = self.env['kw_resignation'].check_user_resign_status()
        if offboard_rec:
            raise ValidationError(
                _(f'You can not apply for Salary Advance, as you have already applied {offboard_rec.offboarding_type.name}.'))
        return res


class kw_petty_cash(models.Model):
    _inherit = "kw_advance_apply_petty_cash"

    @api.model
    def default_get(self, fields):
        res = super(kw_petty_cash, self).default_get(fields)
        offboard_rec = self.env['kw_resignation'].check_user_resign_status()
        if offboard_rec:
            raise ValidationError(
                _(f'You can not apply for Petty Cash, as you have already applied {offboard_rec.offboarding_type.name}.'))
        return res


# class kw_claim(models.Model):
#     _inherit = "kw_advance_claim_settlement"

#     @api.model
#     def default_get(self, fields):
#         res = super(kw_claim, self).default_get(fields)
#         offboard_rec = self.env['kw_resignation'].check_user_resign_status()
#         if offboard_rec:
#             raise ValidationError(
#                 _(f'You can not apply for Claim Settlement, as you have already applied {offboard_rec.offboarding_type.name}.'))
#         return res


class kwKtView(models.Model):
    _inherit = "kw_kt_view"

    @api.model
    def default_get(self, fields):
        res = super(kwKtView, self).default_get(fields)
        offboard_rec = self.env['kw_resignation'].check_user_resign_status()
        if offboard_rec:
            raise ValidationError(
                _(f'You can not apply for KT, as you have already applied {offboard_rec.offboarding_type.name}.'))
        return res
