# added by gouranga 27-Dec-2021 to maintain file tracking information properly
# tracking scenarios :-
'''
file_create
file_forward
correspondence_attach
correspondence_remove
noting_add
comment_add
dispatch_letter_attach
dispacth_letter_revise
dispatch_letter_approve
dispatch_letter_deleted
file_put_in_shelf
file_pull_from_shelf
transferred_to_another_user
pull_from_others_inbox
part_file_create
merge_with_part_file
merge_to_main_file
close_request_submit
close_request_cancel
close_request_approve
close_request_reject
reopen_request_submit
reopen_request_cancel
reopen_request_approve
reopen_request_reject
'''

from odoo import models,fields,api

class FileTracking(models.Model):

    _name = 'smart_office.file.tracking'
    _description = 'Stores tracking information of files.'
    _rec_name = "action_stage_id"

    file_id = fields.Many2one("folder.master","File",required=True,ondelete="cascade")

    action_date = fields.Date("Date",required=True,default=fields.Date.context_today)
    action_time = fields.Datetime("Action Taken On",required=True,default=fields.Datetime.now)

    action_by_user_id = fields.Many2one("res.users","Action By",required=True,default=lambda self:self.env.user)
    action_stage_id = fields.Many2one("smart_office.file.stage","Action Taken",required=True)
    previous_owner_user_id = fields.Many2one("res.users","Previous Owner")
    action_to_user_id = fields.Many2one("res.users","Action To")
    remark = fields.Text("Remark")

    visible_user_ids = fields.Many2many(comodel_name='res.users',string="Visible Users")


'''
    corres_create
    corres_forward
    attach_from_create_file
    attach_from_existing_file
    file_removed
    corres_transfer
    corres_pull_inbox
'''

class CorrespondenceTracking(models.Model):

    _name = 'smart_office.correspondence.tracking'
    _description = 'Stores tracking information of correspondences.'
    _rec_name = "action_stage_id"

    correspondence_id = fields.Many2one("muk_dms.file","Correspondence",required=True,ondelete="cascade")

    action_date = fields.Date("Date",required=True,default=fields.Date.context_today)
    action_time = fields.Datetime("Action Taken On",required=True,default=fields.Datetime.now)

    action_by_user_id = fields.Many2one("res.users","Action By",required=True,default=lambda self:self.env.user)
    action_stage_id = fields.Many2one("smart_office.correspondence.stage","Action Taken",required=True)
    current_owner_id = fields.Many2one("res.users","Current Owner")

    action_to_user_id = fields.Many2one("res.users","Action To")
    remark = fields.Text("Remark")

    visible_user_ids = fields.Many2many(comodel_name='res.users',string="Visible Users")

class UserwiseCorrespondenceTracking(models.Model):

    _name = 'userwise.correspondence.tracking'
    _description = 'Stores userwise tracking information of correspondences.'
    _rec_name = "action_stage_id"

    @api.depends('correspondence_id')
    def _compute_pending_days(self):
        for rec in self:
            rec.pending_days = (rec.action_date - fields.Date.today()).days

    correspondence_id = fields.Many2one("muk_dms.file","Correspondence",required=True,ondelete="cascade")
    action_date = fields.Date("Date",required=True,default=fields.Date.context_today)
    action_time = fields.Datetime("Time",required=True,default=fields.Datetime.now)
    action_by_user_id = fields.Many2one("res.users","Action By",required=True,default=lambda self:self.env.user)
    action_stage_id = fields.Many2one("correspondence.userwise.stage","Action Taken",required=True)
    user_id = fields.Many2one("res.users","User")
    action_to_user_id = fields.Many2one("res.users","Action To")
    remark = fields.Text("Remark")
    visible_user_ids = fields.Many2many(comodel_name='res.users',string="Visible Users")
    pending_days = fields.Integer("Pending Days", compute="_compute_pending_days")