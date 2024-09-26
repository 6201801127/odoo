odoo.define('kw_surveys.survey_form', function (require) {
    'use strict';
    
    require('web.dom_ready');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var context = require('web_editor.context');
    var field_utils = require('web.field_utils');

    var the_form = $('#kw_work_from_home_survey_form');
    
    if(!the_form.length) {
        return $.Deferred().reject("DOM doesn't contain '#kw_work_from_home_survey_form'");
    }
    
        console.debug("[Tendrils Surveys] Custom JS for assessment feedback is loading...");

        // var submit_controller = the_form.attr("action");
        var prefill_controller = the_form.attr("data-prefill");

        // CKEDITOR.replaceClass = 'editorc';
        // $('#demo').click(function(){
        //     alert($('.editorc').val());
        // })
        // Custom code for right behavior of radio buttons with comments box
        // $('.cke_editable').on('change',function(){
        //     $('textarea').val($('.cke_contents_ltr').html());

        // });
        // $(".cke_editable").on("click", function(){ 
        //     alert("value changes");
        // }); 
        // $('iframe').contents().find('.cke_editable').on("change", function(){ 
        //     alert("value changes");
        // }); 
        
        $('.js_comments>input[type="text"]').focusin(function(){
            $(this).prev().find('>input').attr("checked","checked");
        });
        $('.js_radio input[type="radio"][data-oe-survey-otherr!="1"]').click(function(){
            // Temp Changes : Start
            //transportation($(this))
            vaccination($(this))
            // Temp Changes : End
            $(this).closest('.js_radio').find('.js_comments>input[type="text"]').val("");
        });
        $('.js_comments input[type="radio"]').click(function(){
            $(this).closest('.js_comments').find('>input[data-oe-survey-othert="1"]').focus();
        });
        // Custom code for right behavior of dropdown menu with comments
        $('.js_drop input[data-oe-survey-othert="1"]').hide();
        $('.js_drop select').change(function(){
            var other_val = $(this).find('.js_other_option').val();
            if($(this).val() === other_val){
                $(this).parent().removeClass('col-lg-12').addClass('col-lg-6');
                $(this).closest('.js_drop').find('input[data-oe-survey-othert="1"]').show().focus();
            }
            else{
                $(this).parent().removeClass('col-lg-6').addClass('col-lg-12');
                $(this).closest('.js_drop').find('input[data-oe-survey-othert="1"]').val("").hide();
            }
        });
        // Custom code for right behavior of checkboxes with comments box
        $('.js_ck_comments>input[type="text"]').focusin(function(){
            $(this).prev().find('>input').attr("checked","checked");
        });
        $('.js_ck_comments input[type="checkbox"]').change(function(){
            if (! $(this).prop("checked")){
                $(this).closest('.js_ck_comments').find('input[type="text"]').val("");
            }
        });
//        the_form.find('input[type="number"]').change(function(){
//            transportation_days($(this));
//        });

            
        // Pre-filling of the form with previous answers
        function prefill(){
            if (! _.isUndefined(prefill_controller)) {
                var prefill_def = $.ajax(prefill_controller, {dataType: "json"})
                    .done(function(json_data){
                        _.each(json_data, function(value, key){
    
                            // prefill of text/number/date boxes
                            var input = the_form.find(".form-control[name=" + key + "]");
                            if (input.attr('date')) {
                                // display dates in user timezone
                                var moment_date = field_utils.parse.date(value[0]);
                                value = field_utils.format.date(moment_date, null, {timezone: true});
                            }
                            input.val(value);
    
                            // special case for comments under multiple suggestions questions
                            if (_.string.endsWith(key, "_comment") &&
                                (input.parent().hasClass("js_comments") || input.parent().hasClass("js_ck_comments"))) {
                                input.siblings().find('>input').attr("checked","checked");
                            }
    
                            // checkboxes and radios
                            the_form.find("input[name^='" + key + "_'][type='checkbox']").each(function(){
                                $(this).val(value);
                            });
                            the_form.find("input[name=" + key + "][type!='text']").each(function(){
                                $(this).val(value);
                            });
                            if($("#cke_" + key).length > 0) {
                                $("#cke_" + key).contents().find('iframe').contents().find('body').html(value);
                            }
                        });
                    })
                    .fail(function(){
                        console.warn("[Assessment feedback] Unable to load prefill data");
                    });
                return prefill_def;
            }
        }


        // Parameters for form submission
        // $('#kw_work_from_home_survey_form').ajaxForm({
        //     url: submit_controller,
        //     type: 'POST',                       // submission type
        //     dataType: 'json',                   // answer expected type
        //     beforeSubmit: function(formData, $form, options){           // hide previous errmsg before resubmitting
        //         var date_fields = $form.find('div.date > input.form-control');

        //         var level = false;
        //         var flag = true;
        //         var err_message = "This question requires an answer.";
        //         $('.parent-block').find('.child-items').find('.js_errzone').hide();
        //         if(!$('.parent-block').find('.child-items:eq(0)').find('input:checked').length){
        //             $('.parent-block').find('.child-items:eq(0)').find('.js_errzone').show().html(err_message);
        //             flag = false;
        //         }else if($('.parent-block').find('.child-items:eq(0)').find('input:checked').length){
        //             level = $('.parent-block').find('.child-items:eq(0)').find('input:checked').next('span').html();
        //         }
        //         if(level == "1st dose"){
        //             if($('.parent-block').find('.child-items:eq(1)').find('input').val() == ''){
        //                 $('.parent-block').find('.child-items:eq(1)').find('.js_errzone').show().html(err_message);
        //                 flag = false;
        //             }

        //             if(!$('.parent-block').find('.child-items:eq(3)').find('input:checked').length){
        //                 $('.parent-block').find('.child-items:eq(3)').find('.js_errzone').show().html(err_message);
        //                 flag = false;
        //             }

        //         }else if(level == "2 doses"){
        //             if($('.parent-block').find('.child-items:eq(2)').find('input').val() == ''){
        //                 $('.parent-block').find('.child-items:eq(2)').find('.js_errzone').show().html(err_message);
        //                 flag = false;
        //             }
        //             if(!$('.parent-block').find('.child-items:eq(3)').find('input:checked').length){
        //                 $('.parent-block').find('.child-items:eq(3)').find('.js_errzone').show().html(err_message);
        //                 flag = false;
        //             }
        //         }else if(level == "Not yet taken"){
        //             if($('.parent-block').find('.child-items:eq(4)').find('input').val() == ''){
        //                 $('.parent-block').find('.child-items:eq(4)').find('.js_errzone').show().html(err_message);
        //                 flag = false;
        //             }
        //         }
        //         console.log("submit flag >> ", flag)
        //         if(!flag){
        //             return false;
        //         }

        //         for (var i=0; i < date_fields.length; i++) {
        //             var el = date_fields[i];
        //             var moment_date = el.value !== '' ? field_utils.parse.date(el.value) : '';
        //             if (moment_date) {
        //                 moment_date.toJSON = function () {
        //                     return this.clone().locale('en').format('YYYY-MM-DD');
        //                 };
        //             }
        //             var field_obj = _.findWhere(formData, {'name': el.name});
        //             field_obj.value = JSON.parse(JSON.stringify(moment_date));
        //         }
        //         $('.js_errzone').html("").hide();
        //         return true;
        //     },
        //     success: function(response, status, xhr, wfe){ // submission attempt
        //         if(_.has(response, 'errors')){  // some questions have errors
        //             _.each(_.keys(response.errors), function(key){
        //                 $("#" + key + '>.js_errzone').append('<p>' + response.errors[key] + '</p>').show();
        //             });
        //             return false;
        //         }
        //         else if (_.has(response, 'redirect')){      // form is ok
        //             window.location.replace(response.redirect);
        //             return true;
        //         }
        //         else {                                      // server sends bad data
        //             console.error("Incorrect answer sent by server");
        //             return false;
        //         }
        //     },
        //     timeout: 5000,
        //     error: function(jqXHR, textStatus, errorThrown){ // failure of AJAX request
        //         $('#AJAXErrorModal').modal('show');
        //     }
        // });
    
        // function load_locale(){
        //     var url = "/web/webclient/locale/" + context.get().lang || 'en_US';
        //     return ajax.loadJS(url);
        // }
    
        // var ready_with_locale = $.when(base.ready(), load_locale());
        // // datetimepicker use moment locale to display date format according to language
        // // frontend does not load moment locale at all.
        // // so wait until DOM ready with locale then init datetimepicker
        // ready_with_locale.then(function(){
        //      _.each($('.input-group.date'), function(date_field){
        //         var minDate = $(date_field).data('mindate') || moment({ y: 1900 });
        //         var maxDate = $(date_field).data('maxdate') || moment().add(200, "y");
        //         $('#' + date_field.id).datetimepicker({
        //             format : time.getLangDateFormat(),
        //             minDate: minDate,
        //             maxDate: maxDate,
        //             calendarWeeks: true,
        //             icons: {
        //                 time: 'fa fa-clock-o',
        //                 date: 'fa fa-calendar',
        //                 next: 'fa fa-chevron-right',
        //                 previous: 'fa fa-chevron-left',
        //                 up: 'fa fa-chevron-up',
        //                 down: 'fa fa-chevron-down',
        //             },
        //             locale : moment.locale(),
        //             allowInputToggle: true,
        //             keyBinds: null,
        //         });
        //     });
        //     // Launch prefilling
        //     prefill();
        // });
    
        console.debug("[survey] Custom JS for survey loaded!");


        // temp code for vaccination start
        function vaccination(el){
            setTimeout(function(){
                var txt = $(el).next('span').html();
                console.log(txt);
                // if (txt == 'Own Vehicle-Two wheeler (Motorcycle/Scooter)' || txt == 'Own Vehicle-Four wheeler (Car)'){
                //     $('.parent-block').find('.child-items:eq(1)').show().find('input').attr('required',true);
                //     $('.parent-block').find('.child-items:eq(2)').hide();
                //     $('.parent-block').find('.child-items:eq(3)').hide();
                    //$('.parent-block').find('.child-items:eq(2)').show().find('input').attr('required',true);
                    //$('.parent-block').find('.child-items:eq(3)').show().find('input').attr('required',true);

                    // $('.parent-block').find('.child-items:eq(2)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    // $('.parent-block').find('.child-items:eq(3)').find('input[type= "text"]').eq(0).val('NA');
                    // //$('.parent-block').find('.child-items:eq(3)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    //$('.parent-block').find('.child-items:eq(4)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    // $('.parent-block').find('.child-items:eq(5)').find('input[type= "radio"]').eq(0).prop('checked',false);
                // }
                    
                // else if(txt == 'Carpooling with colleagues'){
                //     $('.parent-block').find('.child-items:eq(1)').hide();
                //     $('.parent-block').find('.child-items:eq(2)').show().find('input[type= "radio"]').eq(0).prop('checked',true);
                //     $('.parent-block').find('.child-items:eq(3)').hide();//.find('input');//.attr('required',true);
                    //$('.parent-block').find('.child-items:eq(3)').hide();//.find('input');//.attr('required',true);
                    //$('.parent-block').find('.child-items:eq(4)').hide();//.find('input');//.attr('required',true);
                    // $('.parent-block').find('.child-items:eq(5)').hide();//.find('input');//.attr('required',true);
                    //$('.parent-block').find('.child-items:eq(2)').find('input[type= "text"]').eq(0).val('10/17/2023 6:49 PM');
                    //$('.parent-block').find('.child-items:eq(3)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    //$('.parent-block').find('.child-items:eq(4)').find('input[type= "radio"]');
                    // $('.parent-block').find('.child-items:eq(5)').find('input[type= "radio"]').eq(0).prop('checked',true);
          
                if (txt == 'Yes'){
                    $('.parent-block').find('.child-items:eq(1)').show().find('input').attr('required',true);
                    $('.parent-block').find('.child-items:eq(2)').show().find('input');
                    $('.parent-block').find('.child-items:eq(3)').hide();
                    $('.parent-block').find('.child-items:eq(4)').show().find('input').attr('required',true);
                }
              
                else if(txt == 'No'){
                    $('.parent-block').find('.child-items:eq(1)').hide();//.find('input');//.attr('required',true);
                    $('.parent-block').find('.child-items:eq(2)').hide();//.find('input');//.attr('required',true);
                    $('.parent-block').find('.child-items:eq(3)').hide();//.find('input');//.attr('required',true);
                    $('.parent-block').find('.child-items:eq(4)').hide();
                    $('.parent-block').find('.child-items:eq(1)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    $('.parent-block').find('.child-items:eq(2)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    $('.parent-block').find('.child-items:eq(3)').find('input[type= "radio"]').eq(0).prop('checked',false);
                    $('.parent-block').find('.child-items:eq(4)').find('input[type= "radio"]').eq(0).prop('checked',false);
                }
                else if(txt == 'Others'){
                    $('.parent-block').find('.child-items:eq(3)').show().find('input').attr('required',true);
                }
               
            }, 200);
        }
        setTimeout(function(){
            // $('.parent-block').find('.child-items:eq(0)').hide().find('input').attr('required', false);
            // $('.parent-block').find('.child-items:eq(1)').hide().find('input').attr('required', false);
            //$('button').each(function(){if($(this).text().trim() == 'Back'){$(this).hide()}})
            // $('.parent-block').find('.child-items:gt(1)').find('input[name$="_comment"]').on('change', function(){
                // var _el = $(this);
                // if(!$.isNumeric(_el.val()) || ($.isNumeric(_el.val()) && parseInt(_el.val())>5)){
                //     _el.val('');
                //     _el.closest('.child-items').find('.js_errzone').show().html('Please enter between 0 to 5.');
                // }else{
                //     _el.closest('.child-items').find('.js_errzone').hide();
                // }
            // });
            $('.survey_label_counter').hide();
            $('.parent-block').find('.child-items:gt(0)').hide();
            // $('.parent-block').find('.child-items:eq(1)').hide();
            // $('.parent-block').find('.child-items:eq(2)').hide();
            // $('.parent-block').find('.child-items:eq(3)').hide();
            // var checkedRadio = $('.parent-block').find('.child-items:eq(0)').find('input[type="radio"]:checked');
            // if (checkedRadio.length > 0) {
            //     vaccination(checkedRadio);
            // }

            // vaccination($('.parent-block').find('.child-items:eq(0)').find('input[type="radio"]:checked'));

        }, 500);
        // temp code for vaccination end
});
    
