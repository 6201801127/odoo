import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import registry as registry_get
import odoo.addons.calendar.controllers.main as main


class RecruitmentCalendarController(main.CalendarController):

    @http.route('/calendar/meeting/view', type='http', auth="calendar")
    def view(self, db, token, action=None, id=0, view='calendar'):
        registry = registry_get(db)
        with registry.cursor() as cr:
            # Since we are in auth=none, create an env with SUPERUSER_ID
            env = Environment(cr, SUPERUSER_ID, {})
            attendee = env['calendar.attendee'].search([('access_token', '=', token), ('event_id', '=', int(id))])
            if not attendee:
                return request.not_found()
            timezone = attendee.partner_id.tz
            lang = attendee.partner_id.lang or 'en_US'
            event = env['calendar.event'].with_context(tz=timezone, lang=lang).browse(int(id))

            # If user is internal and logged, redirect to form view of event
            # otherwise, display the simplified web page with event information
            # added on 27-Apr-2020 (gouranga) to redirect by recruitment action uid for viewing the feedback forms
            if event.applicant_id and request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
                recruitment_calendar_action = request.env.ref('kw_recruitment.action_calendar_attendee_recruitment_meeting_view').id
                return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=calendar.event&action=%s' % (db, id, recruitment_calendar_action))
            # added on 27-Apr-2020 (gouranga) to redirect by recruitment action uid for viewing the feedback forms
            if request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
                return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=calendar.event' % (db, id))

            # NOTE : we don't use request.render() since:
            # - we need a template rendering which is not lazy, to render before cursor closing
            # - we need to display the template in the language of the user (not possible with
            #   request.render())
            response_content = env['ir.ui.view'].with_context(lang=lang).render_template(
                'calendar.invitation_page_anonymous', {
                    'event': event,
                    'attendee': attendee,
                })
            return request.make_response(response_content, headers=[('Content-Type', 'text/html')])
