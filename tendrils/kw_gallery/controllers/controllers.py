# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class Gallery(http.Controller):
    @http.route(['/gallery'], auth="public", website=True)
    def gallery(self, **kwargs):
        data = dict()
        data['gallery'] = request.env['kw_image_albums'].sudo().search([])
        return request.render("kw_gallery.gallery_template", data)

    # @http.route(['/gallery-details-<model("kw_image_albums"):album>'], auth="public", methods=['GET'], website=True)
    @http.route(['/gallery-details-<string:album_id>'], auth="public", methods=['GET'], website=True)
    def gallery_images(self, **kwargs):
        values = dict(kwargs)
        data = dict()
        data['gallery'] = gallery = request.env['kw_image_albums'].sudo().search(
            [('id', '=', values['album_id']), ('gallery_id.image_status', '!=', '2')])
        # for image in gallery.gallery_id:
        #     print(image.attachment_id)
        # album.gallery_id = album.gallery_id.filtered(lambda x: x.image_status == '1')
        # data['gallery'] = gallery = album
        # print(f"data >>>> {gallery.gallery_id.mapped('image_status')}")
        return request.render("kw_gallery.gallery_detail_template", data)

    '''
       controller is used for provide the album data.
   '''

    @http.route(['/gallery-details'], type="json", cors='*', auth="none", methods=["POST"], csrf=False)
    def gallery_details(self, **kwargs):
        data_dict = {}
        try:
            album_data_objs = request.env['kw_image_albums'].sudo().search([])
            kw_img_id = request.env['kw_images'].sudo().search([])

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not album_data_objs:
                data_dict['status_code'] = 200
                data_dict['message'] = "Successful"
                json.dumps(data_dict)
            if album_data_objs:
                data_dict['status_code'] = 200
                data_dict['message'] = "Successful"
                data_list_category = []
                data_list_sub_category = []
                data_list_gallery = []
                for allbum_data in album_data_objs:
                    # for rec in album_data.gallery_id:
                    data_dict_category = {}
                    data_dict_category['INT_CATEGORY_ID'] = allbum_data.category_name.id
                    data_dict_category['VCH_CATEGORY_NAME'] = allbum_data.category_name.name
                    data_dict_category['VCH_IMAGE'] = ''
                    data_dict_category['DTM_CREATED_ON'] = str(allbum_data.category_name.create_date)
                    data_dict_category['DTM_UPDATED_ON'] = str(allbum_data.category_name.write_date)
                    data_dict_category['BIT_DELETED_FLAG'] = ''
                    data_dict_category['INT_TYPE'] = ''
                    data_list_category.append(data_dict_category)

                    data_dict_sub_category = {}
                    data_dict_sub_category['INT_SUBCATEGORY_ID'] = allbum_data.id
                    data_dict_sub_category['VCH_SUBCATEGORY_NAME'] = allbum_data.name
                    data_dict_sub_category['INT_CATEGORY_ID'] = allbum_data.category_name.id
                    data_dict_sub_category['VCH_IMAGE'] = ''
                    data_dict_sub_category['DTM_CREATED_ON'] = str(allbum_data.create_date)
                    data_dict_sub_category['DTM_UPDATED_ON'] = str(allbum_data.write_date)
                    data_dict_sub_category['BIT_DELETED_FLAG'] = ''
                    data_dict_sub_category['INT_TYPE'] = ''

                    data_list_sub_category.append(data_dict_sub_category)

                for rec in kw_img_id:
                    data_dict_gallery = {}
                    data_dict_gallery['INT_GALLERY_ID'] = rec.id
                    data_dict_gallery['VCH_HEADLINE_E'] = rec.title if rec.title else ''
                    data_dict_gallery['INT_CATEGORY_ID'] = rec.image_id.category_name.id
                    data_dict_gallery['INT_SUBCATEGORY_ID'] = rec.image_id.id
                    data_dict_gallery['VCH_VIDEO_URL'] = rec.video if rec.video else ''
                    data_dict_gallery['VCH_THUMB_IMAGE'] = '%s/web/image/%s' % (base_url, rec.attachment_id)
                    data_dict_gallery['DTM_CREATED_ON'] = str(rec.create_date)
                    data_dict_gallery['DTM_UPDATED_ON'] = str(rec.write_date)
                    data_dict_gallery['BIT_DELETED_FLAG'] = ''
                    data_dict_gallery['INT_TYPE'] = rec.upload_status if rec.upload_status else ''
                    data_list_gallery.append(data_dict_gallery)

                data_dict['category'] = data_list_category
                data_dict['album'] = data_list_sub_category
                data_dict['gallery'] = data_list_gallery

                return data_dict

        except Exception as e:
            msg_dic = {
                "code": 500,
                "message": str(e)
            }
