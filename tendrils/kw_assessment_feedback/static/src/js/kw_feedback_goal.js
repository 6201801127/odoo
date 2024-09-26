odoo.define('kw_assessment_feedback.kw_feedback_goal_template', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    var goals = {
        init: function () {
            // this.dateRestrict('0');
            // console.log('Came to Goal page successfully...')

            //  Add new row : Start
            $(document).on("click", '#addRow', function () {
                if ($("#goal_name").val() == '') {
                    swal({ text: "Set goal first before adding the milestones...!", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else if ($("#milestone_name").val() == '') {
                    swal({ text: "Milestone can not be left blank.", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else if ($("#score").val() == '') {
                    swal({ text: "Progress can not be left blank.", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else {
                    goals.addMore();
                }
            });

            $(document).on("click", '#nextaddRow', function () {
                if ($("#next_goal_name").val() == '') {
                    swal({ text: "Set next period goal first before adding the milestones...!", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else if ($("#next_milestone_name").val() == '') {
                    swal({ text: "Milestone for next period can not be left blank.", icon: "warning", buttons: { cancel: 'OK' } })
                }
                // else if ($("#next_score").val() == '') {
                //     swal({ text: "Progress for next period can not be left blank.", icon: "warning", buttons: { cancel: 'OK' } })
                // }
                else {
                    goals.nextaddMore();
                }
            });
            //  Add new row : End

            // Get weightage value according to score : Start
            $(document).on("change", "#score", function () {
                if ($("#score").val()) {
                    rpc.query({
                        model: 'kw_feedback_weightage_master',
                        method: 'search',
                        args: [[['from_range', '<=', $("#score").val()], ['to_range', '>=', $("#score").val()]]]
                    }).then(function (data) {
                        $("#weightage_id").val(data);
                    });
                }
                else {
                    $("#weightage_id").val('');
                }
            });

            // $(document).on("change", "#next_score", function () {
            //     if ($("#next_score").val()) {
            //         rpc.query({
            //             model: 'kw_feedback_weightage_master',
            //             method: 'search',
            //             args: [[['from_range', '<=', $("#next_score").val()], ['to_range', '>=', $("#next_score").val()]]]
            //         }).then(function (data) {
            //             $("#next_weightage_id").val(data);
            //         });
            //     }
            //     else {
            //         $("#next_weightage_id").val('')
            //     }
            // });
            // Get weightage value according to score : End

            // Validate Score : Start 
            $(document).on("keydown keyup", ".score", function () {
                if ($(this).val() > 100) {
                    alert("Score must be less than 100");
                    $(this).val('100');
                }
            });
            // Validate Score : End

            // Delete row : Start 
            $(document).on('click', '#record', function () {
                $(this).closest('tr').remove();
                if ($('#miltable tbody tr').length == 0) {
                    $("#miltable thead").hide();
                }
            });

            $(document).on('click', '#next_record', function () {
                $(this).closest('tr').remove();
                if ($('#next_miltable tbody tr').length == 0) {
                    $("#next_miltable thead").hide();
                }
            });
            // Delete row : End

            $(document).on('submit', '#assessment_goal_form', function () {
                goals.submit()
                return false
            });
            $(document).on('click', '#edit_row', function () {
                if ($("#milestone_name").val() == '' && $("#score").val() == '') {

                    var fst_td = $(this).closest('tr').find('td:first-child').html();
                    var sec_td = $(this).closest('tr').find('td:nth-child(2)').html();
                    $("#milestone_name").val(fst_td).change();
                    $("#score").val(sec_td)
                    if ($("#score").val()) {
                        rpc.query({
                            model: 'kw_feedback_weightage_master',
                            method: 'search',
                            args: [[['from_range', '<=', $("#score").val()], ['to_range', '>=', $("#score").val()]]]
                        }).then(function (data) {
                            $("#weightage_id").val(data);
                        });
                    }
                    else {
                        $("#weightage_id").val('');
                    }
                    $("#addRow").html("Update");
                    $("#addRow").prop('class', 'btn badge btn-success');
                    $(this).closest('tr').remove();
                }
                else {
                    swal({ text: "First add those milestone and score then you can update any record.", icon: "warning", buttons: { cancel: 'OK' } })
                }
            });
            $(document).ready(function () {
                if ($('#miltable tbody tr').length == 0) {
                    $("#miltable thead").hide();
                }
                else {
                    $("#miltable thead").show();
                }

                if ($('#next_miltable tbody tr').length == 0) {
                    $("#next_miltable thead").hide();
                }
                else {
                    $("#next_miltable thead").show();
                }
            });

            $(document).on("click", '#back_home', function () {
                window.location.href = '/web#action=kw_assessment_feedback.kw_feedback_final_config_action&amp;model=kw_feedback_final_config&amp;view_type=kanban&amp;menu_id=kw_assessment_feedback.kw_assessment_final_config_add_feedback'

            });

        },
        addMore: function () {
            var str = $("#milestone_name").val();
            var int_score = $("#score").val();
            var weightage = $("#weightage_id").val();
            var weightage_text = $("#weightage_id option:selected").text();
            if (str != '' && int_score != '') {
                var markup = '<tr><td>' + str + '</td><td>' + int_score + '</td><td>' + weightage_text + '</td><input type="hidden" name="wightage" id="wightage" value=' + weightage + '><td class="text-right"><i class="fa fa-edit text-right" style="font-size: large;" id="edit_row" name="edit_record"/></td><td class="text-right"><i class="fa fa-trash text-right" style="font-size: large;" id="record" name="record"></i></td></tr>';
                if ($('#miltable tbody tr').length > 0) {
                    $(markup).insertAfter('#miltable > tbody > tr:last');
                } else {
                    $("#miltable thead").show();
                    $("#miltable tbody").append(markup);
                }
                $("#milestone_name").val('').change();
                $("#score").val('');
                $("#weightage_id").val('');

                if ($("#addRow").html() == 'Update') {

                    $("#addRow").html("Add");
                    $("#addRow").prop('class', 'btn badge btn-primary');
                }

            }
        },
        nextaddMore: function () {
            var str = $("#next_milestone_name").val();
            // var int_score = 0;
            // var weightage = '';
            // var weightage_text = '';
            // if ($("#next_score").val()) {
            //     int_score = $("#next_score").val()
            //     weightage = $("#next_weightage_id").val();
            //     weightage_text = $("#next_weightage_id option:selected").text();
            // }
            if (str != '') {
                // var markup = '<tr><td>' + str + '</td><td>' + int_score + '</td><td>' + weightage_text + '</td><input type="hidden" name="next_weightage" id="next_weightage" value=' + weightage + '><td class="text-right"><i class="fa fa-trash text-right" style="font-size: large;" id="next_record" name="next_record"></i></td></tr>';
                var markup = '<tr><td>' + str + '</td><td class="text-right"><i class="fa fa-trash text-right" style="font-size: large;" id="next_record" name="next_record"></i></td></tr>';
                if ($('#next_miltable tbody tr').length > 0) {
                    $(markup).insertAfter('#next_miltable > tbody > tr:last');
                } else {
                    $("#next_miltable thead").show();
                    $("#next_miltable tbody").append(markup);
                }
                $("#next_milestone_name").val('').change();
                // $("#next_score").val('');
                // $("#next_weightage_id").val('');

            }
        },
        get_current_goal_details: function () {
            var current_goal = {}
            var goal_name = $("#goal_name").val();
            var milestones = []

            if ($('#miltable tbody tr').length > 0) {
                $("#miltable tbody tr").each(function () {
                    var milestone_values = {}
                    var milestone_name = $(this).find('td:first-child').html();
                    var score = $(this).find('td:nth-child(2)').html();
                    var weightage = $(this).find('input:hidden#wightage').val();
                    if (weightage != '') {
                        // alert('No weightage')
                        milestone_values["milestone_name"] = milestone_name
                        milestone_values["score"] = score
                        milestone_values["weightage_id"] = weightage
                        milestones.push(milestone_values)
                    }
                })
                console.log("Current Milestones: ", milestones)
            }
            current_goal['goal_name'] = goal_name
            current_goal['milestones'] = milestones

            return current_goal
        },
        get_next_goal_details: function () {
            var next_goal = {}
            var goal_name = $("#next_goal_name").val();
            var milestones = []

            if ($('#next_miltable tbody tr').length > 0) {
                $("#next_miltable tbody tr").each(function () {
                    var milestone_values = {}
                    milestone_values["milestone_name"] = $(this).find('td:first-child').html();
                    // milestone_values["score"] = $(this).find('td:nth-child(2)').html();
                    // milestone_values["weightage_id"] = $(this).find('input:hidden#next_weightage').val();
                    milestones.push(milestone_values)
                })
                console.log("Next Milestones: ", milestones)
            }
            next_goal['goal_name'] = goal_name
            next_goal['milestones'] = milestones

            return next_goal
        },
        submit: function () {

            var c_goal = $("#c_goal").val();
            var n_goal = $("#n_period").val();
            // alert(n_goal)
            var current_goal_data = false
            var next_goal_data = false

            if (c_goal) {
                current_goal_data = goals.get_current_goal_details();
            }

            if (n_goal) {
                next_goal_data = goals.get_next_goal_details();
            }

            console.log(current_goal_data)
            console.log(next_goal_data)
            if (c_goal && current_goal_data.length != 0 && $('#miltable tbody tr').length === 0) {
                swal({ text: "Minimum one milestone for current period is mandatory.", icon: "error", buttons: { cancel: 'OK' } })
            }
            else if (c_goal && current_goal_data.length != 0 && $('#miltable tbody tr').length > 0 && $('#miltable tbody tr').length != current_goal_data['milestones'].length) {
                swal({ text: "Some milestone's score of current period contains Zero.", icon: "warning", buttons: { cancel: 'OK' } })
            }
            else if (n_goal && next_goal_data.length != 0 && next_goal_data['goal_name'] && next_goal_data['milestones'].length === 0) {
                swal({ text: "Must have to update the milestones for next period.", icon: "warning", buttons: { cancel: 'OK' } })
            }
            else if (n_goal && next_goal_data.length != 0 && next_goal_data['goal_name'] === '' && next_goal_data['milestones'].length === 0) {
                swal({
                    text: "Are you sure want to submit without giving next period milestones?",
                    icon: "warning",
                    dangerMode: true,
                    closeOnClickOutside: false,
                    closeModal: false,
                    buttons: {
                        confirm: { text: 'Yes, Submit', className: 'btn-success' },
                        cancel: 'No'
                    },
                }).then(function (isConfirm) {
                    if (isConfirm) {
                        goals.final_submit(current_goal_data, next_goal_data)
                    } else {
                        swal.close();
                    }
                });

            }
            else {
                goals.final_submit(current_goal_data, next_goal_data)
            }
        },
        final_submit: function (current_goal_data, next_goal_data) {
            console.log("Current period", current_goal_data)
            console.log("Next period", next_goal_data)
            var params = {
                feedback_details: $('#feedback').val(),
                feedback_details_id: $('#feedback_id').val(),
                token: $("#token").val(),
                current_goal_data: current_goal_data,
                next_goal_data: next_goal_data,
            };

            rpc.query({
                model: 'kw_feedback_goal_and_milestone',
                method: 'save_goal_data',
                args: [params],
            }).then(function (values) {
                console.log(values)
                if (values.length < 2) {
                    location.reload();
                }
                else {
                    window.location.href = "/kw/feedback/begin/" + values[0] + "/" + values[1]
                }
            });
        },
    };

    $(function () {
        goals.init();
    });
});