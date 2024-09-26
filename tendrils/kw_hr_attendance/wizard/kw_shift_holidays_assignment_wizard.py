from datetime import date,datetime,time
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwShiftHolidays(models.TransientModel):
    _name           = 'kw_shift_holidays_wizard'
    _description    = 'Kwantify Branch Holiday Manage Wizard'

    
    branch_id               = fields.Many2one('kw_res_branch',string="Branch/SBU")
    public_holiday_id       = fields.Many2one('hr.holidays.public',string="Year",required=True)
    shift_holidays_ids = fields.Many2many(
        string='Public Holidays',
        comodel_name='hr.holidays.public.line',
        relation='shift_holidays_include_public_calendar_rel',
        column1='public_holiday_id',
        column2='wizard_holiday_id',
    )

    @api.constrains('shift_holidays_ids')
    def validate_holidays(self):
        for record in self:
            if not record.shift_holidays_ids:
                raise ValidationError("Please select at least one holiday to include from list")

    # domain="[('year_id','=',public_holiday_id),'|',('branch_ids','=',False),('branch_ids','not in',[branch_id])]"

    @api.onchange('branch_id','public_holiday_id')
    def _get_public_holidays(self):
        for record in self:
            if record.public_holiday_id and record.branch_id:
                record.shift_holidays_ids = record.public_holiday_id.line_ids.filtered(lambda rec:record.branch_id.id in rec.branch_ids.ids)

    @api.model
    def create(self, vals):
        new_record = super(KwShiftHolidays, self).create(vals)
        record = self._manage_public_holidays(new_record)
        return new_record
    
    @api.multi
    def write(self,vals):
        update_record = super(KwShiftHolidays, self).write(vals)
        record = self._manage_public_holidays(self)
        return update_record
    
    @api.model
    def _manage_public_holidays(self,values):
        line_ids = values.public_holiday_id.line_ids
        current_ids = values.shift_holidays_ids  # # New created ids
        filtered_ids = line_ids.filtered(lambda rec:values.branch_id.id in rec.branch_ids.ids)  # # exisiting ids
        if current_ids.ids != filtered_ids.ids:
            diff_new_created = [item for item in current_ids.ids if item not in filtered_ids.ids]  # # (List comprehension current_ids - filtered_ids)
            if len(diff_new_created) > 0:
                for diff_new_created_ids in diff_new_created:
                    browsed_data = line_ids.browse(diff_new_created_ids).write({
                        'branch_ids':[(4,values.branch_id.id,0)]
                    })
            diff_search_filtered = [item for item in filtered_ids.ids if item not in current_ids.ids]  # # (List comprehension filtered_ids - current_ids)
            if len(diff_search_filtered) > 0:
                for diff_search_filtered_ids in diff_search_filtered:
                    browsed_data = line_ids.browse(diff_search_filtered).write({
                        'branch_ids':[(3,values.branch_id.id,0)]
                    })
        self.env.user.notify_success(message='Shift Holidays Assigned successfully.')
        return values

