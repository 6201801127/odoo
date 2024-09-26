# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class KwAnnouncementController(http.Controller):

    def _prepare_comment_data(self, announcement_comments):
        created_user = announcement_comments.sudo().create_uid

        return dict(
            id=announcement_comments.id,
            comment=announcement_comments.comments,
            created_user_id=created_user.id,
            created_user_name=created_user.name,
            created_on=announcement_comments.create_date,
            lapse_time='',
        )

    @http.route('/kwannouncement/get_comment_list', type='json', auth='user')
    def get_comment_list(self, annuncement_id):
        if not annuncement_id:  # to check
            return {}
        annuncement_id = int(annuncement_id)

        Announcement = request.env['kw_announcement']
        # check and raise
        if not Announcement.check_access_rights('read', raise_exception=False):
            return {}
        try:
            Announcement.browse(annuncement_id).check_access_rule('read')
        except AccessError:
            return {}
        else:
            announcement_rec = Announcement.browse(annuncement_id)

        # compute employee data for org chart
        values = dict(
            posted_comments=[self._prepare_comment_data(comments) for comments in announcement_rec.comments_ids],
        )
        values['posted_comments'].reverse()
        return values

    @http.route('/kwannouncement/post_comment', type='json', auth='user')
    def post_comment(self, annuncement_id, comments):
        annuncement_id = int(annuncement_id)

        if not annuncement_id or not comments:  # to check
            return {}

        Announcement_cmnt = request.env['kw_announcement_comments']
        Announcement = request.env['kw_announcement']
        # check and raise
        if not Announcement_cmnt.check_access_rights('create', raise_exception=False):
            return {'error_msg': 'Don\'t have access to announcement module'}
        try:
            Announcement.browse(annuncement_id).check_access_rule('read')
        except AccessError:
            return {'error_msg': 'Don\'t have access to announcement comment module'}
        else:
            Announcement_cmnt.create({'announcement_id': annuncement_id, 'comments': comments})
            # announcement_rec = Announcement.browse(annuncement_id)
            values = self.get_comment_list(annuncement_id)
        return values
