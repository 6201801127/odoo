odoo.define('hr_applicant_portal.hr_applicant_portal', function (require) {
'use strict';

var sAnimation = require('website.content.snippets.animation');;
var core = require('web.core');
var Qweb = core.qweb;
var ajax = require('web.ajax');
ajax.loadXML('/hr_applicant_portal/static/src/xml/template.xml', Qweb);


sAnimation.registry.HrJobLine = sAnimation.Class.extend({
    selector: '.apply4jobs_form',
    events: {
        'click #add_move_line_ids': '_onClickAddressButton',
        'click #add_employeement_ids': '_onClickAddButton',
        'click #education_line_ids': '_onClickEducationButton',
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickAddressButton: function () {
        var self = this
        ajax.jsonRpc("/get/type", 'call', {})
        .then(function(modal){
            var $state_ids = modal.state_ids
            var $country_ids = modal.country_ids
            var $address_type_ids = modal.address_type_ids
            var $AddressLine = $(Qweb.render("AddressRows", {'id': ($('.address_row').length + 1), 'state_ids': $state_ids, 'country_ids': $country_ids, 'address_type_ids': $address_type_ids}));
        $('.o_add_an_item_tr').before($AddressLine);
        $('#address_rec').val($('.address_row').length);
        $AddressLine.find('.line_address_delete span').on('click', function () {
            $(this).parents('tr').remove();
            $('#address_rec').val($('.address_row').length);
            $('table#previous_academic_info').find('tr.address_row').each(function (index, element) {
                var $address_type = $(element).find('.address_type select');
                var $street = $(element).find('.street input');
                var $street2 = $(element).find('.street2 input');
                var $city = $(element).find('.city input');
                var $state = $(element).find('.state select');
                var $country = $(element).find('.country select');
                var $zip = $(element).find('.zip input');
                var $isCorrespondence = $(element).find('.isCorrespondence input');
                $address_type.attr('name', 'address_type_' + (index + 1))
                $street.attr('name', 'street_' + (index + 1))
                $street2.attr('name', 'street2_' + (index + 1))
                $city.attr('name', 'city_' + (index + 1))
                $state.attr('name', 'state_' + (index + 1))
                $country.attr('name', 'country_' + (index + 1))
                $zip.attr('name', 'zip_' + (index + 1))
                $isCorrespondence.attr('name', 'isCorrespondence_' + (index + 1))
            });
        })
        // $AddressLine.find('.state_id').on('change', function (ev) {
        //         console.log($(ev).closest('.name'))
        //         alert($(ev.currentTarge).val())
        //     });
        // $AddressLine.find('.country_id').on('change', function (ev) {
        //         console.log($(ev).closest('.name'))
        //         alert($(ev.currentTarge).val())
        //     });
        });
    },
    _onClickAddButton: function () {
        var $EmployeeLine = $(Qweb.render("EmployeeRows", {'id': ($('.employee_row').length + 1)}));
        $('.o_add_an_employee_tr').before($EmployeeLine);
        $('#employee_rec').val($('.employee_row').length);
        $EmployeeLine.find('.line_record_delete span').on('click', function () {
            $(this).parents('tr').remove();
            $('#employee_rec').val($('.employee_row').length);
            $('table#employeement_info').find('tr.employee_row').each(function (index, element) {
                var $from_date = $(element).find('.from_date input');
                var $to_date = $(element).find('.to_date input');
                var $position = $(element).find('.position input');
                var $organization = $(element).find('.organization input');
                var $ref_name = $(element).find('.ref_name input');
                var $ref_position = $(element).find('.ref_position input');
                var $ref_phone = $(element).find('.ref_phone input');
                $from_date.attr('name', 'from_date_' + (index + 1))
                $to_date.attr('name', 'to_date_' + (index + 1))
                $ref_name.attr('name', 'ref_name_' + (index + 1))
                $position.attr('name', 'position_' + (index + 1))
                $organization.attr('name', 'organization_' + (index + 1))
                $ref_position.attr('name', 'ref_position_' + (index + 1))
                $ref_phone.attr('name', 'ref_phone_' + (index + 1))
            });
        })
    },
     _onClickEducationButton: function () {
        var self = this
        ajax.jsonRpc("/get/type", 'call', {})
        .then(function(modal){
            var $line_type_ids = modal.line_type_ids
            var $EducationLine = $(Qweb.render("EducationRows", {'id': ($('.education_row').length + 1), 'line_type_ids': $line_type_ids}));
            $('.o_add_education_tr').before($EducationLine);
            $('#education_rec').val($('.education_row').length);
            $EducationLine.find('.education_delete span').on('click', function () {
                $(this).parents('tr').remove();
                $('#education_rec').val($('.education_row').length);
                $('table#education_line_info').find('tr.education_row').each(function (index, element) {
                    var $line_type_id = $(element).find('.line_type_id select');
                    var $date_start = $(element).find('.date_start input');
                    var $date_end = $(element).find('.date_end input');
                    var $description = $(element).find('.description input');
                    var $name = $(element).find('.name input');
                    var $specialization = $(element).find('.specialization input');
                    $line_type_id.attr('name', 'line_type_id_' + (index + 1))
                    $date_start.attr('name', 'date_start_' + (index + 1))
                    $name.attr('name', 'name_' + (index + 1))
                    $date_end.attr('name', 'date_end_' + (index + 1))
                    $description.attr('name', 'description_' + (index + 1))
                    $specialization.attr('name', 'specialization_' + (index + 1))
                });
            })
            // $EducationLine.find('.line_type_id').on('change', function (ev) {
            //     console.log($(ev).closest('.name'))
            //     alert($(ev.currentTarge).val())
            // });
        });
    },
    });
});
