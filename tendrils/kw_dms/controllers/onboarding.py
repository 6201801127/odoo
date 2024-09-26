

from odoo import http
from odoo.http import request

class OnboardingController(http.Controller):
    
    @http.route('/dms/document_onboarding/directory', auth='user', type='json')
    def document_onboarding_directory(self):
        company = request.env.user.company_id
        closed = company.documents_onboarding_state == 'closed'
        check = request.env.user.has_group('kw_dms.group_dms_manager')
        if check and not closed:
            return {
                'html': request.env.ref('kw_dms.document_onboarding_directory_panel').render({
                    'state': company.get_and_update_documents_onboarding_state(),
                    'company': company,
                })
            }
        return {}   
    
    @http.route('/dms/document_onboarding/file', auth='user', type='json')
    def document_onboarding_file(self):
        company = request.env.user.company_id
        closed = company.documents_onboarding_state == 'closed'
        check = request.env.user.has_group('kw_dms.group_dms_manager')
        if check and not closed:
            return {
                'html': request.env.ref('kw_dms.document_onboarding_file_panel').render({
                    'state': company.get_and_update_documents_onboarding_state(),
                    'company': company,
                })
            }
        return {}   
    
    