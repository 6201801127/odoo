import re
import os
import shutil
import base64
from os import system
from PyPDF2 import PdfFileMerger
from mimetypes import guess_extension
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations
from odoo.tools.mimetypes import guess_mimetype
import datetime


class ApplicantFeedback(models.TransientModel):
    _name = "kw_applicant_feedback"
    _description = "Applicant Feedback Print Wizard"

    def default_meeting_id(self):
        # print("Context Inside", self._context)
        return self.env['kw_meeting_events'].browse(self._context.get('active_id'))

    @api.model
    def get_applicant_domain(self):
        meeting_id = self.env['kw_meeting_events'].browse(self._context.get('active_id'))
        applicant_ids = meeting_id and meeting_id.applicant_ids and meeting_id.applicant_ids.ids or []
        return [('id', 'in', applicant_ids)]

    meeting_id = fields.Many2one("kw_meeting_events", string="Meeting", default=default_meeting_id)
    applicant_id = fields.Many2one("hr.applicant", "Applicant", domain=get_applicant_domain)

    # @api.multi
    # def print_applicant_feedback_report(self):
    #     applicant_id = self.applicant_id.id
    #     meeting_id = self.meeting_id.id

    #     applicant_feedbacks = self.env['survey.user_input'].search(
    #         [('kw_meeting_id', '=', meeting_id), ('applicant_id','=',applicant_id),('state','!=','new')])
    #     if applicant_feedbacks:
    #         report = self.env['ir.actions.report']._get_report_from_name(
    #             'kw_recruitment.kw_print_feedback_report')

    #         self.env.user.notify_success("Feedback report is downloaded.")
    #         return report.report_action(applicant_feedbacks, config=False)

    #     self.env.user.notify_info("No Feedback is given for this applicant.")

    @api.multi
    def print_applicant_feedback_report(self):
        survey_feedbacks = self.env['survey.user_input'].sudo().search([('applicant_id', '=', self.applicant_id.id)],
                                                                       order="id desc")
        given_feedbacks = survey_feedbacks.filtered(lambda r: r.state != 'new')

        if not given_feedbacks:
            raise ValidationError("No feedbacks found.")

        report = self.env.ref('kw_recruitment.kw_recruitment_interview_feedback_report')
        ctx = self.env.context.copy()
        ctx['flag'] = True

        applicant_path = f'applicant_docs/{self.id}'
        if not os.path.exists(applicant_path):
            os.makedirs(applicant_path)

        full_path = os.path.join(os.getcwd() + f'/{applicant_path}')
        try:
            merge_list = []
            for index, feedback in enumerate(given_feedbacks, start=1):
                feedback_b64_string = report.with_context(ctx).render_qweb_pdf(feedback.id)[0]
                feedback_path = f'{full_path}/{index}.pdf'

                with open(os.path.expanduser(feedback_path), 'wb') as fp:
                    fp.write(feedback_b64_string)
                    merge_list.append(feedback_path)

            # Assuming all feedback pdfs are generated
            # convert applicant document to pdf format if this is other than pdf format
            # Loop over the cvs of applicant and convert them one by one
            for index, cv in enumerate(self.applicant_id.attachment_ids):

                if cv.datas:
                    cv_b64_string = base64.b64decode(cv.datas)
                    # get extension of cv
                    cv_extension = guess_extension(guess_mimetype(cv_b64_string))

                    # If cv is in pdf no need to convert just write the file
                    if cv_extension == '.pdf':
                        cv_store_path = f'{full_path}/cv{index}.pdf'
                        with open(os.path.expanduser(cv_store_path), 'wb') as fp:
                            fp.write(cv_b64_string)
                            # merge_list.insert(0,cv_store_path)
                            merge_list.append(cv_store_path)

                    else:
                        # first write the file with its extension i.e cv.docx,cv.doc etc
                        with open(os.path.expanduser(f'{full_path}/cv{index}{cv_extension}'), 'wb') as fp:
                            fp.write(cv_b64_string)

                        # convert to pdf using unoconv with system command
                        cv_store_path = f'{full_path}/cv{index}{cv_extension}'
                        cv_converted_path = f'{full_path}/cv{index}.pdf'
                        try:
                            system(
                                f'unoconv -f pdf {cv_store_path}')  # system coammand that will generate cv.pdf internally
                            # merge_list.insert(0, cv_converted_path)
                            merge_list.append(cv_converted_path)
                        except Exception:
                            pass

            # merge all pdf to a single file named finaloutput.pdf
            merger = PdfFileMerger()
            full_path_output = f'{full_path}/finaloutput.pdf'

            for pdf in merge_list:
                merger.append(pdf)

            merger.write(full_path_output)
            merger.close()

            feedback = self.env['kw_recruitment_consolidated_feedback'].create({
                'binary_file': base64.b64encode(open(full_path_output, "rb").read()),
                'file_name': f'{self.applicant_id.partner_name}_feedback_consolidated.pdf',
                'applicant_id': self.applicant_id.id
            })

            # Clean the directory
            shutil.rmtree(applicant_path)

            return {
                'view_mode': 'form',
                'res_model': 'kw_recruitment_consolidated_feedback',
                'res_id': feedback.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': self.env.context,
                'nodestroy': True,
            }
        except Exception:
            # Clean the directory
            shutil.rmtree(applicant_path)
            raise ValidationError(
                f"Unable to convert applicant document to pdf.\nPlease try with a different extension.\n")
