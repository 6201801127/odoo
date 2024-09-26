from odoo import http
from odoo.http import request, content_disposition

class UseCaseController(http.Controller):

    @http.route('/web/binary/download_use_case_excel', type='http', auth="user")
    def download_use_case_excel(self, **kwargs):
        model = request.env['kw_project_use_case_master']
        file_content, file_type, file_name = model.action_download_excel()
        
        return request.make_response(
            file_content,
            headers=[
                ('Content-Disposition', content_disposition(file_name)),
                ('Content-Type', file_type)
            ]
        )
    @http.route('/milestone/project_milestones_list_panel', auth='user', type='json')
    def get_milestone_panel_data(self):
        project_id = request.env.context.get('project_id')
        print("project id=================================",project_id)
       
        workorder_value = 8988988
        exchange_rate = 4  # Replace with actual logic
        rest_amount = 34556  # Replace with actual logic
        milestone_sum = 8999
        currency = 'INR'  # Replace with actual logic

        vals = {
            'workorder_value': workorder_value if workorder_value else 0,
            'exchange_rate': exchange_rate if exchange_rate else 0,
            'rest_amount': rest_amount if rest_amount else 0,
            'milestone_sum': milestone_sum if milestone_sum else 0,
            'currency': currency if currency else ''
        }
        return {
            'html': request.env.ref('kw_project_monitoring.view_milestones_template').render({
                'object': request.env['kw_project_milestone'],
                'values': vals
            })
        }


