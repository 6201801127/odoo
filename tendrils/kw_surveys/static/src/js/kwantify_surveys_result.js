odoo.define('kw_surveys.survey_form_view', function (require) {
    'use strict';
    
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var context = require('web_editor.context');
    var the_form = $('#kw_work_from_home_survey_form_view');
    
    if(!the_form.length) {
        return $.Deferred().reject("DOM doesn't contain '#kw_work_from_home_survey_form_view'");
    }
    
        console.debug("[Assessment Feedback] Custom JS for assesssment feedback is loading...");
    
        var prefill_controller = the_form.attr("data-prefill");
        $('#kw_work_from_home_survey_form_view :input').prop('disabled', true);


        CKEDITOR.replaceClass = 'editorc';
        // Custom code for right behavior of radio buttons with comments box
        $('.js_comments>input[type="text"]').focusin(function(){
            $(this).prev().find('>input').attr("checked","checked");
        });
        $('.js_radio input[type="radio"][data-oe-survey-otherr!="1"]').click(function(){
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

            
        // Pre-filling of the form with previous answers
        function prefill(){
            if (! _.isUndefined(prefill_controller)) {
                var prefill_def = $.ajax(prefill_controller, {dataType: "json"})
                    .done(function(json_data){
                        _.each(json_data, function(value, key){
                            console.log(key +''+value)
    
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
        function load_locale(){
            var url = "/web/webclient/locale/" + context.get().lang || 'en_US';
            return ajax.loadJS(url);
        }
    
        var ready_with_locale = $.when(base.ready(), load_locale());
        ready_with_locale.then(function(){
            // Launch prefilling
            prefill();
        });
    
        console.debug("[Assessment Feedback] Custom JS for assessment feedback loaded!");
    });
    