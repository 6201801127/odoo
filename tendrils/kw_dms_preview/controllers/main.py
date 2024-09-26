
import logging

from odoo import _, http

from odoo.addons.kw_dms_utils.tools.rst import rst2html

_logger = logging.getLogger(__name__)
    
class ReStructuredTextController(http.Controller):
    
    @http.route('/preview/convert/rst', auth="user", type='http')
    def preview(self, content, **kw):
        return rst2html(content)
    