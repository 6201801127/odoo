from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwLeaveEntitlements(models.Model):
    _name = 'kw_leave_entitlements'
    _description = "LeaveEntitlements sheet"
    _rec_name = "branch_id"

    @api.model
    def _get_default_entitlement_ids(self):
        records = self.env['hr.leave.type'].search([])
        data = []
        for info in records:
            data.append((0, 0, {'leave_type_id': info.id, 'quantity': 0}))
        return data

    branch_id = fields.Many2one('kw_res_branch', string="Branch")
    grade_id = fields.Many2many('kwemp_grade', string="Grade", required=True)
    entitlement_ids = fields.One2many(
        'kw_leave_entitlements_type', 'entitlement_value_ids', default=_get_default_entitlement_ids)

    @api.constrains('branch_id', 'grade_id')
    def validate_location(self):
        record = self.env['kw_leave_entitlements'].search([('branch_id','=',self.branch_id.id)]) - self
        datas = record.mapped('grade_id')
        for data in datas:
            if data in self.grade_id:
                raise ValidationError(
                "The grade with same branch already exists.")

    @api.constrains('branch_id', 'entitlement_ids')
    def validate_entitlement(self):
        for data in self:
            if data.branch_id and not data.entitlement_ids:
                raise ValidationError(
                    "The Leave Type and its quantity can not be empty .")


class KwLeaveEntitlementsLeaveType(models.Model):
    _name = 'kw_leave_entitlements_type'
    _description = 'Leave Entitlement Type'
    entitlement_value_ids = fields.Many2one(
        'kw_leave_entitlements', string='Entitlement', ondelete="cascade")
    leave_type_id = fields.Many2one(
        'hr.leave.type', string="Leave Type", required=True)
    quantity = fields.Integer(string='Quantity')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = f"{record.leave_type_id.name} - { record.quantity}"
            result.append((record.id, record_name))
        return result

    @api.constrains('leave_type_id')
    def check_leave_type(self):
        for record in self:
            existing_leave_type = self.env['kw_leave_entitlements_type'].search(
                [('leave_type_id', '=', record.leave_type_id.id)]) - record
            if existing_leave_type:
                raise ValidationError("The leave type is already exists.")
