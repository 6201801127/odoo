import base64
from odoo.http import Controller, request, route
from werkzeug.utils import redirect
import odoo.http as http

DEFAULT_IMAGE = '/kwantify_theme/static/src/img/apps-bg.jpg'


class DasboardBackground(Controller):

    @route(['/dashboard'], type='http', auth='user', website=False)
    def dashboard(self, **post):
        user = request.env.user
        company = user.company_id
        if company.dashboard_background:
            image = base64.b64decode(company.dashboard_background)
        else:
            return redirect(DEFAULT_IMAGE)

        return request.make_response(
            image, [('Content-Type', 'image')])

    @route(['/forbidden-page'], type='http', auth='public', website=False)
    def forbidden_page(self, **post):
        # print("post----11111111111111111111111111111111111------",self,post)
        return http.request.render('kwantify_theme.forbidden_page')
