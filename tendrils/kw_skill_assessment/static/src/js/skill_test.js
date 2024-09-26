odoo.define('kw_skill_assessment.skill_test', function (require) {
    'use strict';
    var Widget = require('web.Widget');
    var session = require('web.session');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var skill = {
        ans: [],
        answers: [],
        questions: [],
        quest_id: 0,
        quest_index: 0,
        el: $('#question_block'),
        endtime: 0,
        startdateTime: 0,
        enddateTime: 0,
        start: 0,
        end: 0,
        timegap: 0,
        count: 0,
        ans_id: 0,
        m_review: 0,
        not_attended: 0,
        q_index: 0,
        attended: 0,
        init: function () {
            //start timer
            skill.countdown_timer();
            // check tab change event
            skill.tab_change();
            $('#quest_buttons').find('button').click(function () {
                skill.render_question($(this));
            });
            skill.render_question($('#quest_buttons').find('button').eq(0));
            $('#quest_prev').click(function () {
                skill.render_question($('#quest_buttons').find('button').eq(--skill.quest_index));
            });
            $('#quest_next').click(function () {
                skill.render_question($('#quest_buttons').find('button').eq(++skill.quest_index));
            });

            this.el.find('input[type="radio"]').change(function () {
                skill.saveForm();
            });
            $('#mark_review').click(function () {
                skill.checkReview();
            });

            $(document).keydown(function(e){
                e.preventDefault();
            });
            $('body').disableSelection();
            $(document).bind("contextmenu",function(e){
                return false;
            });

            $('#submit').click(function () {

                skill.m_review = $(".review").length - 1;
                skill.not_attended_ques();
                var msg_str = ''
                msg_str += parseInt(skill.not_attended) > 0 ? skill.not_attended + " no of question"+(parseInt(skill.not_attended) > 1?"s":"")+", you have not attempted." : ''
                msg_str += ($.trim(msg_str) != '' ? '\n' : '') + (parseInt(skill.m_review) > 0 ? skill.m_review + " no of question"+(parseInt(skill.m_review) > 1 ?"s":"")+", you have marked as review." : '')
                swal({
                    title: "Are you sure want to submit?",
                    text: msg_str,
                    content: "hello",
                    icon: "warning",
                    dangerMode: true,
                    buttons: {
                        confirm: { text: 'Yes, Submit', className: 'btn-success' },
                        cancel: 'No'
                    },
                })
                    .then(function (isConfirm) {
                        if (isConfirm) {
                            return fetch(skill.submit());
                        } else {
                            swal.close();
                        }
                    });
            });
        },
        checkReview: function () {
            if ($('#quest_buttons').find('button').eq(skill.quest_index).hasClass('review')) {
                $('#quest_buttons').find('button').eq(skill.quest_index).removeClass('review');
                $('#mark_review').text('Mark Review');
            } else {
                $('#quest_buttons').find('button').eq(skill.quest_index).addClass('review');
                $('#mark_review').text('UnMark Review');
            }
            skill.m_review = $(".review").length - 1;
        },
        countdown_timer: function () {
            var timer;
            function startTimer(sec) {
                var now = new Date().getTime();
                var targetTime = sec * 1000;
                var expected_end_time = targetTime + now;
                timer = setInterval(function () {
                    var now = new Date().getTime();
                    var distance = expected_end_time - now;
                    var hours = Math.floor((distance / (1000 * 60 * 60)) % 24);
                    var minutes = Math.floor(((distance / 1000) / 60) % 60);
                    var seconds = Math.floor((distance / 1000) % 60);
                    var hoursHTML = $("<span>").addClass('timer-block').text(hours);
                    var minutesHTML = $("<span>").addClass('timer-block').text(minutes);
                    var secondsHTML = $("<span>").addClass('timer-block').text(seconds);
                    var duration = (hoursHTML[0].outerHTML + " : ") + (minutes > 0 ? minutesHTML[0].outerHTML + " : " : "") + secondsHTML[0].outerHTML;
                    $("#time_left").html(duration);

                    skill.endtime = duration;

                    if (distance < 0) {
                        clearInterval(timer);
                        $("#time_left").html("TIME EXPIRED");
                        skill.submit();
                    }
                });
            }
            function closeTimer() {
                clearInterval(timer);
            }
            var today = new Date();
            var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
            var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
            skill.startdateTime = date + ' ' + time;
            skill.start = new Date(skill.startdateTime);
            $('#kw_start_time').val(skill.start);
            startTimer($('#time_left').attr('value'));
        },


        render_question: function (el) {
            this.quest_index = el.index();
            this.quest_id = el.attr('id');
            this.question_id = el.attr('qid');
            this.skillset_id = $('#skill_set_id').val();

            this.navStatus();
            this.resetForm();
            el.addClass('active');
            return rpc.query({
                model: 'kw_skill_question_set_config',
                method: 'get_questions',
                args: [{
                    questionid: skill.question_id,
                    skillset_id: skill.skillset_id,
                    answer_id: $('#kw_skill_answer_id').val(),
                    time_start: skill.start
                }],
            }).then(function (val) {
                if (val[5] == 0) {
                    window.location.href = "/web#action=kw_skill_assessment.kw_my_skill_action_window&amp;model=kw_skill_answer_master&amp;view_type=kanban"
                }
                if (val[6] == 0) {
                    window.location.href = "/web#action=kw_skill_assessment.kw_my_skill_action_window&amp;model=kw_skill_answer_master&amp;view_type=kanban"
                }
                $('button.active').attr('qid', skill.question_id);
                $('.number').text(skill.quest_id);
                $('.q_question').html(val[0]);
                $('#option1').next(".q_option_a").html(val[1]);
                $('#option2').next(".q_option_b").html(val[2]);
                $('.ans-opt').eq(0).show();
                $('.ans-opt').eq(1).show();
                if (typeof val[3] != 'undefined') {
                    $('#option3').next(".q_option_c").html(val[3]);
                    $('.ans-opt').eq(2).show();
                }
                if (typeof val[4] != 'undefined') {
                    $('#option4').next(".q_option_d").html(val[4]);
                    $('.ans-opt').eq(3).show();
                }
                $('#kw_skill_answer_id').html(val[5]);

                skill.ans_id = $('#kw_skill_answer_id').text();
                if (skill.ans[skill.quest_index]) {
                    skill.el.find('input[type="radio"][value="' + skill.ans[skill.quest_index] + '"]').prop('checked', true);
                }
                if ($('#quest_buttons').find('button').eq(skill.quest_index).hasClass('review')) {
                    $('#mark_review').text('Unmark Review');
                } else {
                    $('#mark_review').text('Mark Review');
                }
                skill.not_attended_ques();
            });
        },

        tab_change: function () {
            $(window).focus(function () {
                skill.count = skill.count + 1;
                var master_answerid = $('#kw_skill_answer_id').attr('value');
                var parameters = {
                    current_qid: skill.question_id,
                    master_answer_id: master_answerid,
                };
                return rpc.query({
                    model: 'kw_skill_answer_child',
                    method: 'change_current_qid',
                    args: [parameters],
                }).then(function (val) {
                    skill.question_id = val[0];
                    $('button.active').attr('qid', skill.question_id);

                    $('.q_question').html(val[1]);
                    $('#option1').next(".q_option_a").html(val[2]);
                    $('#option2').next(".q_option_b").html(val[3]);
                    $('.ans-opt').eq(0).show();
                    $('.ans-opt').eq(1).show();
                    if (typeof val[4] != 'undefined') {
                        $('#option3').next(".q_option_c").html(val[4]);
                        $('.ans-opt').eq(2).show();
                    }
                    if (typeof val[5] != 'undefined') {
                        $('#option4').next(".q_option_d").html(val[5]);
                        $('.ans-opt').eq(3).show();
                    }
                    if ($('#quest_buttons').find('button').eq(skill.quest_index).hasClass('attended')) {
                        if (skill.ans[skill.quest_index]) {
                            skill.ans[skill.quest_index] = '';
                            $('input[type="radio"]').prop('checked', false);
                            $('#quest_buttons').find('button').eq(skill.quest_index).removeClass('attended');
                        }
                    }
                    if ($('#quest_buttons').find('button').eq(skill.quest_index).hasClass('review')) {
                        $('#quest_buttons').find('button').eq(skill.quest_index).removeClass('review');
                        $('#mark_review').text('Mark Review');
                    }
                    // $('#quest_buttons').find('button').removeClass('attended');
                    // skill.ans = [];
                    // swal({title: "Notice!",
                    //         text: "Your session has been reset due to tab switch!",
                    //         icon: "warning", 
                    //         dangerMode: true});
                });
            });
        },
        not_attended_ques: function () {
            skill.q_index = $(".q_index").length;
            skill.not_attended = skill.q_index - ($('.attended').length - 1);
        },
        resetForm: function () {
            this.el.find('input[type="radio"]').attr('checked', false);
            this.el.find('.ans-opt').hide();
            $('#quest_buttons').find('button').removeClass('active');
        },
        saveForm: function () {
            var selected = this.el.find('input[type="radio"]:checked').val();
            this.ans[this.quest_index] = selected;

            $('#quest_buttons').find('button').eq(skill.quest_index).addClass('attended');
            skill.not_attended_ques();

            var params = {
                qid: skill.question_id,
                ans: selected,
                uid: session.user_id,
                skill_set_id: $('#skill_set_id').val(),
                answer_id: $('#kw_skill_answer_id').attr('value'),
            };
            var rpc = require('web.rpc');
            rpc.query({
                model: 'kw_skill_answer_master',
                method: 'save_answer',
                args: [params],
            });
        },
        navStatus: function () {
            $('#quest_prev').attr('disabled', skill.quest_index == 0)
            $('#quest_next').attr('disabled', skill.quest_index == ($('#quest_buttons').find('button').size() - 1))
            $('#submit').hide()
            if (skill.quest_index == ($('#quest_buttons').find('button').size() - 1)) {
                $('#submit').show()
                $('#quest_next').hide()
            }
            else {
                $('#quest_next').show()
            }
        },
        submit: function (el) {
            var today = new Date();
            var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
            var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
            skill.enddateTime = date + ' ' + time;
            skill.end = new Date(skill.enddateTime);

            skill.timetaken = skill.end.getTime() - skill.start.getTime();
            var seconds = Math.floor((skill.timetaken / 1000));

            skill.timegap = seconds;
            var parameters = {
                uid: session.user_id,
                skill_set_id: $('#skill_set_id').val(),
                timetaken: skill.timegap,
                master_answer_id: $('#kw_skill_answer_id').attr('value'),
                tab_change_no: skill.count,
                mark_reviews: skill.m_review,
            };
            var question_set_id = $('#skill_set_id').val();
            var master_answerid = $('#kw_skill_answer_id').attr('value');

            var rpc = require('web.rpc');
            rpc.query({
                model: 'kw_skill_answer_master',
                method: 'calculate_marks',
                args: [parameters],
            }).then(function () {
                window.location.href = "/result?user_id=" + session.user_id + "&ques_set_id=" + question_set_id + "&answer_master_id=" + master_answerid;
            });
        },
    };
    $(function () {
        skill.init();
    }); //end of ready function
}); // End of module

// $(document).ready(function () {
//     if (window.IsDuplicate()) {
//       alert("This is duplicate window\n\n Closing...");
//       window.close();
//     }
//   });



