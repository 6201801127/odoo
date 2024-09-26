from odoo import fields, models, api

class CreateFolder(models.TransientModel):
    _name = 'part.file.wizard'
    _description = 'Wizard of Part File'

    deffolderid = fields.Many2one('folder.master')
    folder_id = fields.Many2many('folder.master', string="Select Part Files")
    description = fields.Text(string='Description')

    @api.multi
    def action_confirm_merge_file(self):
        file_tracker = self.env['smart_office.file.tracking']
        for file in self.folder_id:
            for correspondence in file.file_ids: # Correspondences (muk_dms.file)
                correspondence.folder_id = self.deffolderid.id
                self.deffolderid.file_ids_m2m = [[4,correspondence.id]]

            for dispatch_letter in file.document_dispatch: # Dispatch Letters
                dispatch_letter.write({'part_file_id':dispatch_letter.folder_id.id,'folder_id':self.deffolderid.id})

            for noting in file.noting_ids: # Dispatch Letters
                noting.folder_id = self.deffolderid.id
            file.button_close_part()

            # start : Add tracking information of merged_to_main_file to new model 28-December-2021
            file_tracker.create({
                'file_id':file.id,
                'action_stage_id':self.env.ref('smart_office.file_stage_merged_to_main_file').id,
                # 'action_to_user_id':self.employee.user_id.id,
                # 'previous_owner_user_id':file.current_owner_id.id,
                'remark':self.description,
            })
            # end : Add tracking information of merged_to_main_file to new model 28-December-2021
        
        # file_tracker.create({
        #         'file_id':self.deffolderid.id,
        #         'action_stage_id':self.env.ref('smart_office.file_stage_merged_with_part_file').id,
        #         'remark':self.description,
        #     })

        self.env.user.notify_success("Part file merged successfully.")