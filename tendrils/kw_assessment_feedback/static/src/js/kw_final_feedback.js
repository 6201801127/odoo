odoo.define('kw_assessment_feedback.final_feedback_form', function (require) {
    'use strict';
    
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var context = require('web_editor.context');
    var the_form = $('#kw_assessment_final_feedback_form');
    
    if(!the_form.length) {
        return $.Deferred().reject("DOM doesn't contain '#kw_assessment_final_feedback_form'");
    }
    
        console.debug("[Assessment Feedback] Custom JS for assesssment feedback is loading...");
    
        var prefill_controller = the_form.attr("data-prefill");

        // Pre-filling of the form with previous answers
        function prefill(){
            if (! _.isUndefined(prefill_controller)) {
                var prefill_def = $.ajax(prefill_controller, {dataType: "json"})
                    .done(function(json_data){
                        _.each(json_data, function(value, key){
    
                            var input = the_form.find("span[name=" + key + "]");
                            input.text(value);
                            var text_input = the_form.find("textarea[name=" + key + "]");
                            text_input.text(value);
                        });
                    })
                    .fail(function(){
                        console.warn("[Assessment Feedback] Unable to load prefill data");
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
    