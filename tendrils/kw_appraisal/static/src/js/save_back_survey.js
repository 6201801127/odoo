odoo.define('kw_appraisal.not', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var the_form = $('.js_surveyform');
    var submit_controller = the_form.attr("data-back");
    var survey = {
        init: function () {
            $(document).on("click", '#save_and_back', function () {
                const total_questions = $('#total_questions').val();
                if(total_questions > 0){
                    for(let i = 1 ; i <= total_questions ; i ++){
                        if($('#self_score_'+i+'').val() == ""){
                            const ques_txt= $('#question_txt_'+i+'').text(); 
                            alert('Score is missing for '+ques_txt+'');
                        return false;
                    }
                    for(let j = 1 ; j <= total_questions ; j ++){
                    if($('#justify'+j+'').val() == ''){
                        const ques_txt= $('#question_txt_'+j+'').text(); 
                        alert('Kindly justify for '+ques_txt+'');
                    return false;
                    }
                    }

                    }
                }
                if($('#training_user_text').val() == ''){
                    alert('Kindly justify for Training');
                    return false;
                }
                const total_questions_lm = $('#total_questions_lm').val();
                if(total_questions_lm > 0){
                    for(let i = 1 ; i <= total_questions_lm ; i ++){
                        if($('#lm_score_'+i+'').val() == ""){
                                const ques_txt= $('#question_txt_'+i+'').text(); 
                                alert('Score is missing for '+ques_txt+'');
                            return false;
                        }
                    // for(let j = 1 ; j <= total_questions_lm ; j ++){
                        if($('#justify_'+i+'').val() == ''){
                            const ques_txt= $('#question_txt_'+i+'').text(); 
                            alert('Kindly justify for '+ques_txt+'');
                        return false;
                        }
                    // }

                    }
                }
                const total_num_questions_ulm = $('#total_num_questions_ulm').val();
                if(total_num_questions_ulm > 0){
                    for(let m = 1 ; m <= total_num_questions_ulm ; m ++){
                        if($('#ulm_score_'+m+'').val() == ""){
                                const ques_txt= $('#question_txt_'+m+'').text(); 
                                alert('Score is missing for '+ques_txt+'');
                            return false;
                        }
                    // for(let j = 1 ; j <= total_questions_lm ; j ++){
                        if($('#justify_'+m+'').val() == ''){
                            const ques_txt= $('#question_txt_'+m+'').text(); 
                            alert('Kindly justify for '+ques_txt+'');
                        return false;
                        }
                    // }

                    }
                }
                const total_questions_ulm = $('#total_questions_ulm').val();
                if(total_questions_ulm > 0){
                    for(let k = 1 ; k <= total_questions_ulm ; k ++){
                        if($('#justify_'+k+'').val() == ''){
                            const ques_txt= $('#question_txt_'+k+'').text(); 
                            alert('Kindly justify for '+ques_txt+'');
                        return false;
                        }
                    }
                }
                var prevs = ''
                survey.ajax_call(prevs);
            });
            $(document).on("click", '#prevs', function () {
                const total_questions = $('#total_questions').val();
                if(total_questions > 0){
                    for(let i = 1 ; i <= total_questions ; i ++){
                        if($('#self_score_'+i+'').val() == ""){
                            const ques_txt= $('#question_txt_'+i+'').text(); 
                            alert('Score is missing for '+ques_txt+'');
                        return false;
                    }
                    for(let j = 1 ; j <= total_questions ; j ++){
                    if($('#justify'+j+'').val() == ""){
                        const ques_txt= $('#question_txt_'+j+'').text(); 
                        alert('Kindly justify for '+ques_txt+'');
                    return false;
                    }
                    }

                    }
                }
                const total_questions_lm = $('#total_questions_lm').val();
                if(total_questions_lm > 0){
                    for(let i = 1 ; i <= total_questions_lm ; i ++){
                        if($('#lm_score_'+i+'').val() == ""){
                                const ques_txt= $('#question_txt_'+i+'').text(); 
                                alert('Score is missing for '+ques_txt+'');
                            return false;
                        }
                    // for(let j = 1 ; j <= total_questions_lm ; j ++){
                        if($('#justify_'+i+'').val() == ''){
                            const ques_txt= $('#question_txt_'+i+'').text(); 
                            alert('Kindly justify for '+ques_txt+'');
                        return false;
                        }
                    // }

                    }
                }
                const total_questions_ulm = $('#total_questions_ulm').val();
                if(total_questions_ulm > 0){
                    for(let k = 1 ; k <= total_questions_ulm ; k ++){
                        if($('#justify_'+k+'').val() == ''){
                            const ques_txt= $('#question_txt_'+k+'').text(); 
                            alert('Kindly justify for '+ques_txt+'');
                        return false;
                        }
                    }
                }
                var prevs = 'prevs'
                survey.ajax_call(prevs);
            });
            $(document).on("change", '.usr_input_val', function () {
                survey.validate_score(this);
            });
        },
        validate_score: function(el){
            var max = $(el).closest('tr').attr('valmax');
            var val = $(el).val();
            if (parseFloat(val) > parseFloat(max))
                {
                    alert("Please insert valid score");
                    return false;
                }
            else if (parseFloat(val)<=0){
                alert("Please insert valid score");
                return false;
            }
            else {
                return true
            }
                },
        ajax_call: function (prevs) {
            // alert(prevs)
            var result = {};
            $.each($('#kw_survey_form').serializeArray(), function () {
                result[this.name] = this.value;
            });
            ajax.jsonRpc(submit_controller, 'call', {
                'kw_survey_form':result,
                'prevs':prevs,
            }).then(function (data) {
                // alert(data)
                if (data['redirect'] == 'self') {
                    window.location.href = '/web#action=kw_appraisal.self_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'
                }
                else if(data['redirect'] == 'lm'){
                    window.location.href =  '/web#action=kw_appraisal.lm_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'                        

                }
                else if(data['redirect'] == 'ulm'){
                    window.location.href = '/web#action=kw_appraisal.ulm_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'                        

                }
                else if(data['redirect'] == 'lm_reassign'){
                    window.location.href = '/web#action=kw_appraisal.lm_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'                                            

                }
                else if(data['redirect'] == 'prevs'){
                    window.location.href ="/kw/survey/start/"+data['survey_id']+'/'+data['token']
                }
            });
        },
    };

    $(function () {
        survey.init();
    });
});