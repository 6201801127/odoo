import pytz
from datetime import date,datetime
import base64
import os,io
import tempfile
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from odoo import http
from odoo.http import request

class FileInfo(http.Controller):
    # Start: Helper Methods to process pdf or convert to pdf
    def process_notings(self,file_id,user_id,encoded=True):
        # make sure file has notings don't call this otherwise
        report = request.env.ref('smart_office.smart_office_noting_report')
        ctx = request.env.context.copy()
        ctx['flag'] = True
        
        file = request.env['folder.master'].sudo(user_id).browse(file_id)

        merger = PdfFileMerger(strict=False)
        temporary_files = []

        for noting in file.noting_ids:

            noting_file_desc, noting_store_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efilenoting{noting.id}.tmp.')
            os.close(noting_file_desc)

            temporary_files.append(noting_store_path)

            noting_b64_string = report.with_context(ctx).render_qweb_pdf(noting.id)[0]
            try:
                with open(noting_store_path, 'wb') as fp:
                    fp.write(noting_b64_string)

                with open(noting_store_path, 'rb') as fp:
                    pdf_reader_obj = PdfFileReader(fp)
                    number_of_pages = pdf_reader_obj.getNumPages()

                    writer = PdfFileWriter()
                    left = True
                    for pdf_page in range(number_of_pages):
                        x_axis_margin = 70 if left else -10
                        page = pdf_reader_obj.getPage(pdf_page)
                        new_page = writer.addBlankPage(page.mediaBox.getWidth(),page.mediaBox.getHeight())
                        new_page.mergeScaledTranslatedPage(page, 0.9, x_axis_margin, 0, expand=False)

                        left = not left
                    else:
                        if number_of_pages % 2 != 0: #if there is odd number of pages then add a blank page at last
                            writer.addBlankPage(page.mediaBox.getWidth(),page.mediaBox.getHeight())
                    modified_file_desc, modified_file_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efilenotingmodified{noting.id}.tmp.')
                    os.close(modified_file_desc)

                    temporary_files.append(modified_file_path)
                    
                    with open(modified_file_path, 'wb') as modified_pdf_file:
                        writer.write(modified_pdf_file)
                        
                merger.append(modified_file_path, import_bookmarks=False)
            except Exception:
                continue

        merged_notings_file_desc, merged_notings_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efileallnoting{file.id}.tmp.')
        os.close(merged_notings_file_desc)
        temporary_files.append(merged_notings_path)

        merger.write(merged_notings_path)
        merger.close()
       
        with open(merged_notings_path, 'rb') as pdf:
            enc_noting_str = encoded and base64.b64encode(pdf.read()) or pdf.read()
       
        # shutil.rmtree(notings_path)
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)

        return enc_noting_str
    
    def process_correspondences(self,file_id,user_id,encoded=True,page_number_only = False):
        # make sure file has correspondences don't call this method otherwise
        file = request.env['folder.master'].sudo(user_id).browse(file_id)
        temporary_files = []
        
        merger = PdfFileMerger(strict=False)

        for correspondence in file.file_ids.sorted(key=lambda r:r.attach_to_file_time,reverse=True):
            if correspondence.pdf_file:
                correspondence_b64_string = base64.b64decode(correspondence.pdf_file)
                
                correspondence_file_desc, correspondence_store_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efilecorrespondence{correspondence.id}.tmp.')
                os.close(correspondence_file_desc)

                temporary_files.append(correspondence_store_path)

                with open(correspondence_store_path, 'wb') as fp:
                    fp.write(correspondence_b64_string)

                merger.append(correspondence_store_path, import_bookmarks=False)

        merged_correspondence_file_desc, merged_correspondence_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efileallcorrespondence{file.id}.tmp.')
        os.close(merged_correspondence_file_desc)
        temporary_files.append(merged_correspondence_path)

        merger.write(merged_correspondence_path)
        merger.close()

        total_page = 0
        try:
            pdf = PdfFileReader(open(merged_correspondence_path, 'rb'))
            total_page = pdf.getNumPages()
        except Exception:
            pass
        if not page_number_only:
            with open(merged_correspondence_path, 'rb') as pdf:
                encoded_correspondence_str = encoded and base64.b64encode(pdf.read()) or pdf.read()
            
        # shutil.rmtree(correspondence_path)
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)

        return total_page  if page_number_only else encoded_correspondence_str
    
    def process_dispatch_letters(self,file_id,user_id,encoded=True):
        report = request.env.ref('smart_office.dispatch_document_status_print')
        ctx = request.env.context.copy()
        ctx['flag'] = True
        
        file = request.env['folder.master'].sudo(user_id).browse(file_id)
        temporary_files = []
        merger = PdfFileMerger(strict=False)
        
        for dispatch_letter in file.document_dispatch:
            dispatch_letter_file_desc, dispatch_letter_store_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efiledispatchletter{dispatch_letter.id}.tmp.')
            os.close(dispatch_letter_file_desc)

            temporary_files.append(dispatch_letter_store_path)

            dispatch_letter_b64_string = report.with_context(ctx).render_qweb_pdf(dispatch_letter.id)[0]
            try:
                with open(dispatch_letter_store_path, 'wb') as fp:
                    fp.write(dispatch_letter_b64_string)
                merger.append(dispatch_letter_store_path, import_bookmarks=False)
            except Exception:
                continue

        merged_dispatch_letter_file_desc, merged_dispatch_letter_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'efilealldispatchletters{file.id}.tmp.')
        os.close(merged_dispatch_letter_file_desc)
        temporary_files.append(merged_dispatch_letter_path)

        merger.write(merged_dispatch_letter_path)
        merger.close()
       
        with open(merged_dispatch_letter_path, 'rb') as pdf:
            enc_dispatch_letter_str = encoded and base64.b64encode(pdf.read()) or pdf.read()
            
        # shutil.rmtree(dispatch_letter_path)
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                print('Error when trying to remove file %s' % temporary_file)

        return enc_dispatch_letter_str
    # End: Helper Methods to process pdf or convert to pdf

    # @http.route(['/test/<corres_id>'], type='http', auth="none",cors="*",methods=["GET"], csrf=False)
    # def test_method(self,corres_id, **kwargs):
    #     correspondence = request.env['muk_dms.file'].sudo(6).browse(int(corres_id))
    #     pdf = base64.b64decode(correspondence.pdf_file)
    #     pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
    #     return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/note-page/<int:file_id>/<int:user_id>/<int:note_id>'], type='http', auth="none",cors="*",methods=["GET"], csrf=False)
    def download_note_page(self,file_id,user_id,note_id, **kwargs):
        note = request.env['smart_office.noting'].sudo(user_id).browse(note_id)
        report = request.env.ref('smart_office.smart_office_noting_report').sudo(user_id)
        ctx = request.env.context.copy()
        ctx['flag'] = True
        noting_b64_string = report.with_context(ctx).render_qweb_pdf(note.id)[0]
        data = io.BytesIO(noting_b64_string)
        return http.send_file(data, filename='Note.pdf', as_attachment=True)

    @http.route(['/file_info/<file_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def get_file_info(self,file_id, **kwargs):
        print("Inside file info route.")
        # print("PAYLOAD IS----->",kwargs)
        user_id = int(kwargs.get('user_id','0'))
        if user_id:
            user_obj = request.env['res.users'].sudo(user_id).browse(user_id)
            user_tz             = user_obj.tz or 'UTC'
            local               = pytz.timezone(user_tz)

            file = request.env['folder.master'].sudo(user_id).browse(int(file_id))
            if file.exists():
                notings = file.noting_ids.search([('folder_id','=',file.id)],order="id desc")
                submitted_notings = notings.filtered(lambda r:r.state == 'submitted')
                latest_noting = submitted_notings.filtered('is_last_sequence')[0:1]
                index_notings =  submitted_notings - latest_noting
                note_length = len(submitted_notings)

                response = {
                    'status':'success',
                    'file_info':{
                            'created_by':file.create_uid.name,
                            'company':file.create_uid.company_id.name,
                            'name':file.folder_name,
                            'date':file.date.strftime('%d/%m/%Y'),
                            'subject':file.subject.subject,
                            'number':file.number
                            },

                    'noting_info':[{'id':noting.id,
                                    'content':noting.content,
                                    'action_taken_by':noting.create_uid.employee_ids and noting.create_uid.employee_ids[0].name or '',
                                    'designation':noting.create_uid.employee_ids and noting.create_uid.employee_ids[0].job_title and noting.create_uid.employee_ids[0].job_title.name or '',
                                    'branch':noting.create_uid.default_branch_id.name.lower() in ["delhi",'new delhi'] and "Head Quarter" or noting.create_uid.default_branch_id.name,
                                    'action_taken_on':noting.forward_time and noting.forward_time.astimezone(local).strftime("%d/%m/%Y %H:%M %p") or noting.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                    'comments_enable':noting.is_last_sequence,
                                    'noting_date':noting.forward_time and noting.forward_time.astimezone(local).strftime("%d/%m/%Y") or noting.create_date.astimezone(local).strftime("%d/%m/%Y"),
                                    'subject':noting.subject or '',
                                    'sequence':'Noting '+str(note_length - index),
                                    'comments':[{
                                                'content':comment.name or '',
                                                'name':comment.create_uid.employee_ids and comment.create_uid.employee_ids[0].name or '',
                                                'designation':comment.create_uid.employee_ids and comment.create_uid.employee_ids[0].job_title and comment.create_uid.employee_ids[0].job_title.name or '',
                                                'action_taken_on':comment.forward_time and comment.forward_time.astimezone(local).strftime("%d/%m/%Y %H:%M %p") or comment.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                            } for comment in noting.comment_ids]
                                    } 
                                    for index,noting in enumerate(submitted_notings)],

                    'correspondence_info':[{'correspondence_id':correspond.id,
                                            'file_name':correspond.name,
                                            'correspondence_name':correspond.subject,
                                            'correspondence_number':correspond.letter_number,
                                            'correspondence_authority':correspond.create_uid.employee_ids and correspond.create_uid.employee_ids[0].name or '',
                                            'designation':correspond.create_uid.employee_ids and correspond.create_uid.employee_ids[0].job_title and correspond.create_uid.employee_ids[0].job_title.name or '',
                                            'action_taken_on':correspond.attach_to_file_time.astimezone(local).strftime("%d/%m/%Y"),
                                            'correspondence_type':correspond.letter_type.name,
                                            'removable':True if (not correspond.dispatch_id and correspond not in file.file_ids_m2m) else False,
                                            }
                                            for correspond in file.file_ids.filtered('attach_to_file_time').sorted('attach_to_file_time',reverse=True)],
                    
                }
                null_attach_to_file_time_correspondence = file.file_ids.filtered(lambda r:not r.attach_to_file_time)
                if null_attach_to_file_time_correspondence:
                    for correspond in null_attach_to_file_time_correspondence:
                        response['correspondence_info'].append({
                                            'correspondence_id':correspond.id,
                                            'file_name':correspond.name,
                                            'correspondence_name':correspond.subject,
                                            'correspondence_number':correspond.letter_number,
                                            'correspondence_authority':correspond.create_uid.employee_ids and correspond.create_uid.employee_ids[0].name or '',
                                            'designation':correspond.create_uid.employee_ids and correspond.create_uid.employee_ids[0].job_title and correspond.create_uid.employee_ids[0].job_title.name or '',
                                            'action_taken_on':correspond.create_date.astimezone(local).strftime("%d/%m/%Y"),
                                            'correspondence_type':correspond.letter_type.name,
                                            'removable':True if (not correspond.dispatch_id and correspond not in file.file_ids_m2m) else False,
                                            })

                if latest_noting:
                    response['latest_noting'] = {'id':latest_noting.id,
                                                'content':latest_noting.content,
                                                'action_taken_by':latest_noting.create_uid.employee_ids and latest_noting.create_uid.employee_ids[0].name or '',
                                                'designation':latest_noting.create_uid.employee_ids and latest_noting.create_uid.employee_ids[0].job_title and latest_noting.create_uid.employee_ids[0].job_title.name or '',
                                                'branch':latest_noting.create_uid.default_branch_id.name.lower() in ["delhi",'new delhi'] and "Head Quarter" or latest_noting.create_uid.default_branch_id.name,
                                                'action_taken_on':latest_noting.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                                'comments_enable':True,
                                                'noting_date':latest_noting.create_date.astimezone(local).strftime("%d/%m/%Y"),
                                                'subject':latest_noting.subject or '',
                                                'comments':[{
                                                            'content':comment.name or '',
                                                            'name':comment.create_uid.employee_ids and comment.create_uid.employee_ids[0].name or '',
                                                            'designation':comment.create_uid.employee_ids and comment.create_uid.employee_ids[0].job_title and comment.create_uid.employee_ids[0].job_title.name or '',
                                                        } for comment in latest_noting.comment_ids]
                                                }

                draft_noting = notings.filtered(lambda r:r.state =='draft' and r.create_uid == user_obj)[0:1]
                if draft_noting:
                    response['draft_data'] = {'id':draft_noting.id,
                                              'content':draft_noting.content,
                                              'type':2,
                                              'subject':draft_noting.subject or '',
                                              'comments_enable':False,
                                              'noting_date':draft_noting.forward_time and draft_noting.forward_time.astimezone(local).strftime("%d/%m/%Y") or draft_noting.create_date.astimezone(local).strftime("%d/%m/%Y"),
                                              'action_taken_by':draft_noting.create_uid.employee_ids and draft_noting.create_uid.employee_ids[0].name or '',
                                              'designation':draft_noting.create_uid.employee_ids and draft_noting.create_uid.employee_ids[0].job_title and draft_noting.create_uid.employee_ids[0].job_title.name or '',
                                              'branch':draft_noting.create_uid.default_branch_id.name.lower() in ["delhi",'new delhi'] and "Head Quarter" or draft_noting.create_uid.default_branch_id.name,
                                              'action_taken_on':draft_noting.forward_time and draft_noting.forward_time.astimezone(local).strftime("%d/%m/%Y %H:%M %p") or draft_noting.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                              'sequence':'Noting '+str(len(submitted_notings) + 1),
                                              'comments':[]
                                              }
                else:
                    latest_comments = latest_noting.comment_ids.search([('noting_id','=',latest_noting.id)])
                    draft_comment = latest_comments.filtered(lambda r:r.state == 'draft' and r.create_uid == user_obj)[0:1]
                    if draft_comment:
                        response['draft_data'] = {'id':draft_comment.id,
                                                  'content':draft_comment.name,
                                                  'type':1,
                                                  'noting_id':draft_comment.noting_id.id,
                                                  'note_details':{
                                                    'id':draft_comment.noting_id.id,
                                                    'content':draft_comment.noting_id.content,
                                                    'action_taken_by':draft_comment.noting_id.create_uid.employee_ids and draft_comment.noting_id.create_uid.employee_ids[0].name or '',
                                                    'designation':draft_comment.noting_id.create_uid.employee_ids and draft_comment.noting_id.create_uid.employee_ids[0].job_title and draft_comment.noting_id.create_uid.employee_ids[0].job_title.name or '',
                                                    'branch':draft_comment.noting_id.create_uid.default_branch_id.name.lower() in ["delhi",'new delhi'] and "Head Quarter" or draft_comment.noting_id.create_uid.default_branch_id.name,
                                                    'action_taken_on':draft_comment.noting_id.forward_time and draft_comment.noting_id.forward_time.astimezone(local).strftime("%d/%m/%Y %H:%M %p") or draft_comment.noting_id.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                                    'comments_enable':draft_comment.noting_id.is_last_sequence,
                                                    'noting_date':draft_comment.noting_id.forward_time and draft_comment.noting_id.forward_time.astimezone(local).strftime("%d/%m/%Y") or draft_comment.noting_id.create_date.astimezone(local).strftime("%d/%m/%Y"),
                                                    'subject':draft_comment.noting_id.subject or '',
                                                    'sequence':'Noting '+str(note_length),
                                                    'comments':[{
                                                                'id':comment.id,
                                                                'content':comment.name or '',
                                                                'name':comment.create_uid.employee_ids and comment.create_uid.employee_ids[0].name or '',
                                                                'designation':comment.create_uid.employee_ids and comment.create_uid.employee_ids[0].job_title and comment.create_uid.employee_ids[0].job_title.name or '',
                                                                'action_taken_on':comment.forward_time and comment.forward_time.astimezone(local).strftime("%d/%m/%Y %H:%M %p") or comment.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                                            } for comment in latest_comments]
                                                    },
                                                  'name':draft_comment.create_uid.employee_ids and draft_comment.create_uid.employee_ids[0].name or '',
                                                  'designation':draft_comment.create_uid.employee_ids and draft_comment.create_uid.employee_ids[0].job_title and draft_comment.create_uid.employee_ids[0].job_title.name or '',
                                                  'branch':draft_comment.create_uid.default_branch_id.name.lower() in ["delhi",'new delhi'] and "Head Quarter" or draft_comment.create_uid.default_branch_id.name,
                                                  'action_taken_on':draft_comment.forward_time and draft_comment.forward_time.astimezone(local).strftime("%d/%m/%Y %H:%M %p") or draft_comment.create_date.astimezone(local).strftime("%d/%m/%Y %H:%M %p"),
                                                  }
            else:
                response = {"status": "failed","message": f"Invalid file id {file_id}."}
        else:
            response = {"status": "failed","message": "missing parameter user_id"}
        # print("Response from file_info route-->",response)
        return response

    @http.route(['/noting_info/<int:file_id>'], type="json", auth="none",cors="*", methods=["POST"],csrf=False)
    # @http.route(['/noting_info/<int:file_id>/<int:user_id>'], type="json", auth="none",cors="*", methods=["POST"],csrf=False)
    def get_noting_info(self,file_id,**kwargs):
        # print("inside noting_info route",kwargs)
        response = {"status":"failed"}

        user_id = int(kwargs.get('user_id',0))

        user = request.env['res.users'].sudo(user_id).browse(int(user_id))
        file = request.env['folder.master'].sudo(user_id).browse(int(file_id))
        
        if file.exists() and user.exists():
            response.update({
                'status':'success',
                'company':user.company_id.name,
                'branch':user.default_branch_id.name.lower() in ["delhi",'new delhi'] and "Head Quarter" or user.default_branch_id.name,
                'file_number':file.number,
                'date':date.today().strftime("%d/%m/%Y"),
                'file_date':file.date.strftime('%d/%m/%Y'),
                'subject':file.subject.subject,
                'user_name':user.name,
                'designation':user.employee_ids and user.employee_ids.job_title.name or ""
                    })      
        else:
            response['message'] = "Invalid User/File."

        # print("final data",response)
        return response
    
    @http.route(['/correspondence_info/<int:correspondence_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def get_correspondence_info(self,correspondence_id, **kwargs):
        # print("correspondence info route called")
        correspondence = request.env['muk_dms.file'].sudo().browse(int(correspondence_id))
        if correspondence.exists():
            if not correspondence.other_extension_converted_to_pdf:
                correspondence.convert_or_assign_pdf_file()
            response = {
                'status':'success',
                'name':correspondence.name,
                'content_binary':correspondence.pdf_file,
                'extension':'pdf',
            }
        
        else:
            response = {"status": "failed","message": f"Invalid correspondence id {correspondence_id}."}
        return response
       
    @http.route(['/save_noting/<file_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def save_noting_data(self,file_id, **payload):
        # print("inside save noting route and payload id ",payload)
        user_id = int(payload.get('user_id','0'))
        if user_id:
            file = request.env['folder.master'].sudo(user_id).browse(int(file_id))
            if file.exists():
                if 'noting' in payload and payload['noting']:
                    note_id = 0
                    note = {'content':payload['noting'],'subject':payload.get('subject','')}

                    # if 'correspondence' in payload and payload['correspondence']:
                    #     # file.file_ids = [[4,id] for id in payload['correspondence']]
                    #     file.file_ids = [[6,0,payload['correspondence']]]

                    if 'noting_id' in payload and payload['noting_id']:
                        file.noting_ids = [[1,int(payload['noting_id']),note]]
                        note_id = int(payload['noting_id'])
                    else:
                        note['folder_id'] = int(file_id)
                        noting = request.env['smart_office.noting'].sudo(user_id).create(note)
                        note_id = noting.id
                    
                    response = {"id":note_id,"status":"success","message":"Noting added successfully"}
                    
                else:
                    response =  {"status": "failed","message": "Please add noting"}

            else:
                response = {"status": "failed","message": f"Invalid file id {file_id}."}
        else:
            response = {"status": "failed","message": "missing required parameter user_id"}
        # print("response is -->",response)
        return response

    @http.route(['/attach_correspondence/<file_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def add_correspondence(self,file_id, **payload):
        # print("inside attach_correspondence route and payload is------>",payload)
        user_id = int(payload.get('user_id','0'))
        if user_id:
            user = request.env['res.users'].sudo(user_id).browse(user_id)
            employee = user.employee_ids[0:1]
            file = request.env['folder.master'].sudo(user_id).browse(int(file_id))
            
            if file.exists():
                for corres_id in payload['selected_ids']:
                    correspondence = request.env['muk_dms.file'].sudo(user_id).browse(int(corres_id))
                    file.file_ids = [[4,int(corres_id)]]
                    # start: added on 15 December 2021
                    correspondence.write({'attach_to_file_date': datetime.now().date(),
                                          'attach_to_file_time': datetime.now()})
                    # start: added on 15 December 2021
                    request.env['smart_office.correspondence.tracking'].sudo(user_id).create({
                        'correspondence_id': correspondence.id,
                        'action_stage_id': request.env.ref('smart_office.corres_stage_attach_file_from_create_file').id,
                        'remark': ''
                    })
                    # request.env['file.tracker.report'].sudo(user_id).create({
                    #     'name': correspondence.name,
                    #     'type': 'Correspondence',
                    #     'number':correspondence.letter_number,
                    #     'assigned_by': user.name,
                    #     'assigned_by_dept': employee.department_id.name,
                    #     'assigned_by_jobpos': employee.job_id.name,
                    #     'assigned_by_branch': employee.branch_id.name,
                    #     'assigned_date': datetime.now().date(),
                    #     'action_taken': 'assigned_to_file',
                    #     'remarks': '',
                    #     'details': f"Correspondence attached to file {file.folder_name}"
                    # })

                response = {"status":"success","message":"Correspondence added successfully"}
            else:
                response = {"status": "failed","message": f"Invalid file id {file_id}."}
        else:
            response = {"status": "failed","message": "missing required parameter user_id"}

        return response

    @http.route(['/remove_noting/<noting_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def remove_noting(self,noting_id, **payload):
        # print("inside remove noting route and payload is----->",payload)
        user_id = int(payload.get('user_id','0'))
        if user_id:
            noting = request.env['smart_office.noting'].sudo(user_id).browse(int(noting_id))
            if noting.exists():
                if noting.create_uid.id == user_id and noting.state == 'draft':
                    noting.unlink()
                    response = {"status":"success","message":"Noting deleted successfully"}
                else:
                    response = {"status":"failed","message":"You must be the owner of the noting and noting must be in drfat state to delete a noting."}
            else:
                response = {"status": "failed","message": f"Invalid noting id {noting_id}."}
        else:
            response = {"status": "failed","message": "missing required parameter user_id"}

        return response
    
    @http.route(['/remove_comment/<int:comment_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def remove_comment(self,comment_id, **payload):
        # print("inside remove comment route and payload is----->",payload)
        user_id = int(payload.get('user_id','0'))
        if user_id:
            comment = request.env['smart_office.comment'].sudo(user_id).browse(comment_id)
            if comment.exists():
                if comment.create_uid.id == user_id and comment.state == 'draft':
                    comment.unlink()
                    response = {"status":"success","message":"Comment deleted successfully"}
                else:
                    response = {"status":"failed","message":"You must be the owner of the comment and comment must be in drfat state to delete a comment."}
            else:
                response = {"status": "failed","message": f"Invalid comment id {comment_id}."}
        else:
            response = {"status": "failed","message": "missing required parameter user_id"}

        return response

    @http.route(['/remove_correspondence/<file_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def remove_correspondence(self,file_id, **payload):
        # print("inside remove correspondence route and payload is----->",payload)
        user_id = int(payload.get('user_id','0'))
        if user_id:
            file = request.env['folder.master'].sudo(user_id).browse(int(file_id))
            if file.exists():
                if 'remove_id' not in payload or not payload['remove_id']:
                    response = {"status":"success","message":"Correspondence removed successfully"}
                else:
                    file.file_ids = [[3,int(payload['remove_id'])]]
                    
                    # end : Add tracking information of correspondence_attached to new model 28-December-2021
                    request.env['smart_office.correspondence.tracking'].sudo(user_id).create({
                        'correspondence_id': int(payload['remove_id']),
                        'action_stage_id': request.env.ref('smart_office.corres_stage_file_removed').id,
                        'remark': ''
                    })
                    response = {"status":"success","message":"Correspondence removed successfully"}
                    
            else:
                response = {"status": "failed","message": f"Invalid file id {file_id}."}
        else:
            response = {"status": "failed","message": "missing required parameter user_id"}

        return response
    
    @http.route(['/save_comment/<noting_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def save_comment(self,noting_id, **payload):
        # print("inside save comment route and payload is ",payload)
        user_id = int(payload.get('user_id','0'))
        if user_id:
            noting = request.env["smart_office.noting"].sudo(user_id).browse(int(noting_id))
            if noting.exists():
                if 'comment' in payload and payload['comment']:
                    comment_id = 0
                    if 'comment_id' in payload and payload['comment_id']:
                        noting.comment_ids = [[1,int(payload['comment_id']),{'name':payload['comment']}]]
                        comment_id = int(payload['comment_id'])
                    else:
                        comment = request.env['smart_office.comment'].sudo(user_id).create({'noting_id':noting.id,'name':payload['comment']})
                        comment_id = comment.id
                    response = {"id":comment_id,"status":"success","message":"Comment added successfully"}
                else:
                    response =  {"status": "failed","message": "Please add comment"}
            else:
                response = {"status": "failed","message": f"Invalid noting id {noting_id}."}
        else:
            response = {"status": "failed","message": "missing required parameter user_id inside params"}

        return response

    @http.route(['/correspondence_inbox/<int:user_id>'], type="json", auth="none",cors="*", methods=["POST"],csrf=False)
    def correspondence_inbox(self,user_id,**kwargs):
        # print("inside correspondence_inbox route",kwargs)
        filter_ids = []
        if 'ids' in kwargs:
            filter_ids = kwargs['ids']
        user_obj = request.env['res.users'].sudo(user_id).browse(user_id)
        user_tz  = user_obj.tz or 'UTC'
        local    = pytz.timezone(user_tz)
        response = []
        inbox_data = request.env['muk_dms.file'].sudo(user_id).search([('id','not in',filter_ids),('current_owner_id','=',user_id),('folder_id','=',False)])
        if 'deleted_ids' in kwargs and kwargs['deleted_ids']:
            inbox_data |= inbox_data.sudo().browse(kwargs['deleted_ids'])
        for correspond in inbox_data:
            response.append({'correspondence_id':correspond.id,
                            'file_name':correspond.name,
                            'correspondence_name':correspond.subject,
                            'correspondence_number':correspond.letter_number,
                            'correspondence_authority':correspond.create_uid.employee_ids and correspond.create_uid.employee_ids[0].name or '',
                            'designation':correspond.create_uid.employee_ids and correspond.create_uid.employee_ids[0].job_title and correspond.create_uid.employee_ids[0].job_title.name or '',
                            'action_taken_on':correspond.create_date.astimezone(local).strftime("%d/%m/%Y"),
                            'correspondence_type':correspond.letter_type.name,
                            'removable':True if (not correspond.dispatch_id and not correspond.folder_id) else False,
                            # 'noting_id':correspond.noting_id and correspond.noting_id.id or ''
                            })
        # print("final correspondence inbox data",response)
        return response

    @http.route(['/efile_notings/<int:file_id>/<int:user_id>'], type="http", auth="user", methods=["GET"])
    def download_notings(self,file_id,user_id, **payload):
        data = io.BytesIO(base64.b64decode(self.process_notings(int(file_id),user_id)))
        return http.send_file(data, filename='Notings.pdf', as_attachment=True)
    
    @http.route(['/efile_correspondences/<int:file_id>/<int:user_id>'], type="http", auth="none", methods=["GET","POST"])
    def download_correspondences(self,file_id,user_id, **payload):
        data = io.BytesIO(base64.b64decode(self.process_correspondences(int(file_id),user_id)))
        return http.send_file(data, filename='Correspondences.pdf', as_attachment=True)
    
    @http.route(['/efile_dispatch_letters/<int:file_id>/<int:user_id>'], type="http", auth="user", methods=["GET"])
    def download_dispatch_letters(self,file_id,user_id,**payload):
        data = io.BytesIO(base64.b64decode(self.process_dispatch_letters(int(file_id),user_id)))
        return http.send_file(data, filename='Dispatch_letters.pdf', as_attachment=True)
    
    @http.route(['/efile_file_download/<int:file_id>/<int:user_id>'], type="http", auth="user", methods=["GET"])
    def download_file(self,file_id,user_id, **payload):
        file = request.env['folder.master'].sudo(user_id).browse(int(file_id))
        temporary_files = []

        if file.exists() and (file.noting_ids or file.file_ids): # or file.document_dispatch):
                
            merger = PdfFileMerger(strict=False)
            
            # notings
            if file.noting_ids:
                noting_base64_string = self.process_notings(file.id,user_id,encoded=False)

                noting_file_desc, noting_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'filenotings{file.id}.tmp.')
                os.close(noting_file_desc)
                temporary_files.append(noting_path)
        
                with open(noting_path, 'wb') as fp:
                    fp.write(noting_base64_string)
                merger.append(noting_path,import_bookmarks=False)
                
            # correspondences 
            if file.file_ids:
                correspondence_base64_string = self.process_correspondences(file.id,user_id,encoded=False)
                correspondence_file_desc, correspondence_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'filecorrespondences{file.id}.tmp.')
                os.close(correspondence_file_desc)
                temporary_files.append(correspondence_path)
        
                with open(correspondence_path, 'wb') as fp:
                    fp.write(correspondence_base64_string)

                merger.append(correspondence_path,import_bookmarks=False)
                
            # dispatch letters
            # if file.document_dispatch:
            #     dispatchletter_b64_string = self.process_dispatch_letters(file.id,user_id,encoded=False)
            #     dispatch_letter_path = f'{file_path}/dispatchletters.pdf'
        
            #     with open(os.path.expanduser(dispatch_letter_path), 'wb') as fp:
            #         fp.write(dispatchletter_b64_string)
            #     merger.append(dispatch_letter_path,import_bookmarks=False)

            note_corres_merge_file_desc, note_corres_merge_path = tempfile.mkstemp(suffix=f'.pdf', prefix=f'filenotescorres{file.id}.tmp.')
            os.close(note_corres_merge_file_desc)
            temporary_files.append(note_corres_merge_path)

            merger.write(note_corres_merge_path)
            merger.close()
            
            with open(note_corres_merge_path, 'rb') as pdf:
                enc_merged_str = base64.b64encode(pdf.read())
            data = io.BytesIO(base64.b64decode(enc_merged_str))

            # Manual cleanup of the temporary files
            for temporary_file in temporary_files:
                try:
                    os.unlink(temporary_file)
                except (OSError, IOError):
                    print('Error when trying to remove file %s' % temporary_file)
            
            return http.send_file(data, filename=f'File {file.number}.pdf', as_attachment=True)
        else:
            return request.not_found()
    
    @http.route(['/correspondence_binary/<int:file_id>'], type="json", cors="*", auth="none", methods=["POST"], csrf=False)
    def get_correspondence_merged_binary(self,file_id, **kwargs):
        user_id = int(kwargs.get('user_id',0))
        file = request.env['folder.master'].sudo(user_id).browse(file_id)
        user = request.env['res.users'].sudo(user_id).browse(user_id)
        if file.exists() and user.exists():
            base64_data = file.file_ids and self.process_correspondences(file_id,user_id) or ''
            response = {"status": "success","content_binary":base64_data}
        else:
            response = {"status": "failed","message": f"Invalid file_id or user_id."}
        return response

    @http.route(['/correspondence_pages/<int:file_id>'], type="json", cors="*", auth="none", methods=["GET","POST"], csrf=False)
    def get_correspondence_pages(self,file_id, **kwargs):
        # print("correspondence_pages called..",kwargs)
        correspondence_id = int(kwargs.get('correspondence_id','0'))
        user_id = int(kwargs.get('user_id','0'))
        user = request.env['res.users'].sudo(user_id).browse(user_id)
        
        if user.exists():
            corres = request.env['muk_dms.file'].sudo(user_id).browse(correspondence_id)
            # print("corres",corres)
            file = request.env['folder.master'].sudo(user_id).browse(file_id)
            if file.exists():
                # print(file.file_ids)
                correspondence = file.file_ids.filtered(lambda r:r.id == corres.id).sorted(key=lambda r:r.attach_to_file_time,reverse=True)

                if correspondence:
                    if not correspondence.other_extension_converted_to_pdf:
                        correspondence.convert_or_assign_pdf_file()
                    response = {"status":"success","total_page":correspondence.pdf_total_page}
                else:
                    response = {"status":"failed","message":"Invalid correspondence ID"}
            else:
                response = {"status":"failed","message":"Invalid file ID"}
        else:
            response = {"status":"failed","message":"Invalid user ID"}
        # print("correspondence page response-->",response)

        return response
    
    @http.route(['/forward_employee_list'], type="json", auth="none",cors="*", methods=["POST"],csrf=False)
    def forward_employee_list(self,**kwargs):
        # print("inside forward_employee_list route",kwargs)
        user_id = int(kwargs.get('user_id','0'))
        user = request.env['res.users'].sudo(user_id).browse(user_id)
        response = {'status':'','message':'','employees':[]}
        if user.exists():
            # employees = request.env['hr.employee'].sudo(user_id).search([('user_id','!=',user_id)])
            employees = request.env['hr.employee'].sudo(user_id).search([])
            response['employees'] = [{'id':emp.id,'name':emp.name,'designation':emp.job_title.name,'department':emp.department_id.name} for emp in employees]
            response['status'] = 'success'
            response['message']='200'
        else:
            response['status'] ='failed'
            response['message'] = 'invalid user id'
        return response

    @http.route(['/forward_file'], type="json", auth="none",cors="*", methods=["POST"],csrf=False)
    def forward_file(self,**kwargs):
        # print("inside forward_employee_list route",kwargs)
        user_id = int(kwargs.get('user_id','0'))
        file_id = int(kwargs.get('file_id','0'))
        employee_id = int(kwargs.get('employee_id','0'))
        user = request.env['res.users'].sudo(user_id).browse(user_id)
        file = request.env['folder.master'].sudo(user_id).browse(file_id)
        response = {'status':'','message':''}
        if user.exists() and file.exists():
            employee = request.env['hr.employee'].sudo(user_id).browse(employee_id)
            if employee.exists() and employee.active:
                # code
                current_employee  = request.env['hr.employee'].sudo(user_id).search([('user_id', '=', user_id)], limit=1)
                if not employee.user_id:
                    response['status'] = 'failed'
                    response['message'] = f"{employee.name} is not linked with any user.Hence the file can't be forwarded to him."
                else:
                    if file.current_owner_id == user:
                        notings = file.noting_ids.sudo(user_id).search([('folder_id','=',file.id)])
                        if notings:
                            notings.write({'secondary_employee_ids':[[4,employee.id]]})
                            draft_noting = notings.filtered(lambda r:r.state == 'draft' and r.employee_id == current_employee)
                            if draft_noting:
                                draft_noting.sudo(user_id).write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                                # start : Add tracking information of file_forwarded to new model 28-December-2021
                                # request.env['smart_office.file.tracking'].sudo(user_id).create({
                                #     'file_id':file.id,
                                #     'action_stage_id':request.env.ref('smart_office.file_stage_noting_added').id,
                                #     'remark':'',
                                # })
                                # end : Add tracking information of correspondence_attached to new model 28-December-2021

                            comments = request.env['smart_office.comment'].sudo(user_id).search([('noting_id','in',notings.ids)])
                            draft_comment = comments.filtered(lambda r: r.employee_id == current_employee and  r.state=='draft')
                            if comments:
                                comments.write({'secondary_employee_ids':[[4,employee.id]]})
                            if draft_comment:
                                draft_comment.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                            
                            if not draft_noting and not draft_comment:
                                latest_note = notings.filtered(lambda r:r.is_last_sequence == True)[-1:]
                                new_comment = latest_note.comment_ids.create({'noting_id':latest_note.id,'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                                new_comment.secondary_employee_ids = [[4,employee_id]]
                            # start : Add tracking information of file_forwarded to new model 28-December-2021
                            # request.env['smart_office.file.tracking'].sudo(user_id).create({
                            #     'file_id':file.id,
                            #     'action_stage_id':request.env.ref('smart_office.file_stage_comment_added').id,
                            #     'remark':'',
                            # })
                            # end : Add tracking information of correspondence_attached to new model 28-December-2021

                        dispatch_documents = file.document_dispatch
                        if dispatch_documents:
                            dispatch_documents.write({'secondary_employee_ids':[[4,employee.id]]})
                            not_forwarded = dispatch_documents.filtered(lambda r: not r.forwarded)
                            if not_forwarded:
                                not_forwarded.sudo(user_id).write({'forwarded':True})
                            
                        # file.write({'file_ids_m2m': [[6,0,file.file_ids.ids]],
                        #             'previous_owner': [(4, file.current_owner_id.id)],
                        #             'sec_owner': [(4, file.current_owner_id.id)]})
                        
                        # file_count = 0
                        # sec_own = []

                        # file.last_owner_id = user.id
                        # file.current_owner_id = employee.user_id.id
                        # file.forwarded_by_employee_id = current_employee.id
                        # file.forwarded_to_employee_id = employee.id
                        # file.forwarded_date = date.today()

                        file.write({
                                    'file_ids_m2m': [[6,0,file.file_ids.ids]],
                                    'previous_owner': [(4, file.current_owner_id.id)],
                                    'sec_owner': [(4, file.current_owner_id.id)],
                                    'incoming_source':'forward',
                                    'action_by_uid':user_id,
                                    'action_time':datetime.now(),
                                    'action_date':datetime.now().date(),
                                    'file_mode':'inbox',
                                    
                                    'last_owner_id': user.id,
                                    'current_owner_id': employee.user_id.id,
                                    'forwarded_by_employee_id': current_employee.id,
                                    'forwarded_to_employee_id': employee.id,
                                    'forwarded_date': date.today(),
                                    })

                        # request.env['folder.tracking.information'].sudo(user_id).create({
                        #     'create_let_id': file.id,
                        #     'forwarded_date': date.today(),
                        #     'forwarded_to_user': employee.user_id.id,
                        #     'forwarded_to_dept': employee.department_id.id,
                        #     'job_pos': employee.job_id.id,
                        #     'forwarded_by': user.id,
                        #     'remarks': ''
                        # })
                        # start : Add tracking information of file_forwarded to new model 28-December-2021
                        request.env['smart_office.file.tracking'].sudo(user_id).create({
                            'file_id':file.id,
                            'action_stage_id':request.env.ref('smart_office.file_stage_file_forwarded').id,
                            'action_to_user_id':employee.user_id.id,
                            'remark':'',
                        })

                        # f_details = ""
                        # if file_count == 0:
                        #     f_details = "File forwarded with no correspondence"
                        # elif file_count == 1:
                        #     f_details = "File forwarded with single correspondence"
                        # elif file_count > 1:
                        #     f_details = "File forwarded with multiple Correspondence"
                        # request.env['file.tracker.report'].sudo(user_id).create({
                        #     'name': str(file.folder_name),
                        #     'number': str(file.number),
                        #     'type': 'File',
                        #     'forwarded_by': str(current_employee.user_id.name),
                        #     'forwarded_by_dept': str(current_employee.department_id.name),
                        #     'forwarded_by_jobpos': str(current_employee.job_id.name),
                        #     'forwarded_by_branch': str(current_employee.branch_id.name),
                        #     'forwarded_date': date.today(),
                        #     'forwarded_to_user': str(employee.name),
                        #     'forwarded_to_dept': str(employee.department_id.name),
                        #     'forwarded_to_branch': str(employee.user_id.branch_id.name),
                        #     'job_pos': str(employee.job_id.name),
                        #     'action_taken': 'file_forwarded',
                        #     'remarks': '',
                        #     'details': f_details
                        # })
                        # sec_own = []
                        # previous_owner = []
                        for file in file.file_ids:
                            file.write({
                                'last_owner_id': user.id,
                                'responsible_user_id': user.id,
                                'current_owner_id': employee.user_id.id,
                                'previous_owner' : [(4, user.id)],
                                'previous_owner_emp' : [(4,employee.id)],
                                'previous_owner_emp' : [(4,user.employee_ids.ids[0])],
                            })
                            # file_count+=1
                            # file.last_owner_id = user.id
                            # file.responsible_user_id = user.id
                            # file.current_owner_id = employee.user_id.id
                            # file.previous_owner = [(4, user.id)]
                            # file.previous_owner_emp = [(4,employee.id)]
                            # file.previous_owner_emp = [(4,file.user.employee_ids.ids[0])]
                            # for line in rec.sec_own_ids:
                            #     sec_own.append(line.employee.user_id.id)
                            # file.sec_owner = [(6, 0, sec_own)]
                            # previous_owner.append(rec.env.user.id)
                            # file.previous_owner = [(6, 0, previous_owner)]

                            # request.env['file.tracking.information'].sudo(user_id).create({
                            #     'create_let_id': file.id,
                            #     'forwarded_date': date.today(),
                            #     'forwarded_to_user': employee.user_id.id,
                            #     'forwarded_to_dept': employee.department_id.id,
                            #     'job_pos': employee.job_id.id,
                            #     'forwarded_by':user.id,
                            #     'remarks': ''
                            # })
                            # request.env['file.tracker.report'].sudo(user_id).create({
                            #     'name': str(file.name),
                            #     'number': str(file.letter_number),
                            #     'type': 'Correspondence',
                            #     'forwarded_by': str(current_employee.user_id.name),
                            #     'forwarded_by_dept': str(current_employee.department_id.name),
                            #     'forwarded_by_jobpos': str(current_employee.job_id.name),
                            #     'forwarded_by_branch': str(current_employee.branch_id.name),
                            #     'forwarded_date': date.today(),
                            #     'forwarded_to_user': str(employee.name),
                            #     'forwarded_to_dept': str(employee.department_id.name),
                            #     'job_pos': str(employee.job_id.name),
                            #     'forwarded_to_branch': str(employee.user_id.branch_id.name),
                            #     'action_taken': 'correspondence_forwarded',
                            #     'remarks': '',
                            #     'details': "Correspondence Forwarded through File"
                            # })
                        response['status'] = 'success'
                        response['message']='File forwarded successfully.'
                    else:
                        response['status'] = 'failed'
                        response['message'] = f"You are not the current owner of the file.Hence you can't forward this file."
            else:
                response['status'] = 'failed'
                response['message'] = 'Invalid Employee'
        else:
            response['status'] ='failed'
            response['message'] = 'Invalid user or file'
        return response