odoo.define('kw_appraisal.kw_goal_template', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    var goals = {
        init: function () {
            this.dateRestrict('0');
            console.log('Came to Goal page successfully...')
            $(document).on("click", '#addRow', function () {
                if ($("#goal_name").val() == '') {
                    swal({ text: "Set goal first before adding the milestones...!", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else if ($("#milestone_name").val() == '') {
                    swal({ text: "Milestone can not be left blank.", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else if ($("#milestone_date").val() == '') {
                    swal({ text: "Target Date can not be left blank.", icon: "warning", buttons: { cancel: 'OK' } })
                }
                else {
                    goals.addMore();
                }
            });
            $(document).on("keydown keyup", "#actaul_score", function () {
                if (/[^\d.]/g.test(this.value)) this.value = this.value.replace(/[^\d.]/g, '')
            });
            $(document).on('click', '.chkboxes', function () {
                $(this).closest('tr').remove();
                if ($('.miltable tbody tr').length == 0) {
                    $(".miltable thead").hide();
                }
            });
            $(document).on('click', '.edit_row', function () {
                if ($("#milestone_name").val() == '' && $("#milestone_date").val() == '') {

                    var fst_td = $(this).closest('tr').find('td:first-child').html();
                    var sec_td = $(this).closest('tr').find('td:nth-child(2)').html();
                    $("#milestone_name").val(fst_td).change();
                    $("#milestone_date").val(sec_td)
                    $("#addRow").html("Update");
                    $("#addRow").prop('class', 'btn badge btn-success');
                    $(this).closest('tr').remove();
                }
                else{
                    swal({ text: "First add those milestone and milestone date then you can update any record.", icon: "warning", buttons: { cancel: 'OK' } })
                }
            });
            $(document).on('submit', '#goal_form', function () {
                goals.submit();
                return false
            });
            $(document).on('click', '#save_draft', function () {
                var draft = 'draft_call';
                goals.submit(draft);
            });
            $(document).ready(function () {
                if ($('.miltable tbody tr').length == 0) {
                    $(".miltable thead").hide();
                }
                else {
                    $(".miltable thead").show();
                }
                $(document).on('blur', '#actaul_score', function () {
                    var actual_score = parseFloat($(this).val())
                    var acheivement_score = (actual_score / 100) * 100
                    $("#kra_table").find('#achievement_score').html(acheivement_score.toFixed(2) + '%')
                });
            });

        },

        addMore: function () {
            var str = $("#milestone_name").val();
            var str_date = $("#milestone_date").val();
            // alert($('.miltable tbody tr').length)
            if (str != '' && str_date != '') {
                var markup = '<tr><td>' + str + '</td><td>' + str_date + '</td><td class="text-right"><i class="fa fa-edit edit_row text-right" style="font-size: large;" name="edit_record"></i></td><td class="text-right"><i class="fa fa-trash chkboxes text-right" style="font-size: large;" name="record"></i></td></tr>';
                if ($('.miltable tbody tr').length > 0) {
                    // alert('Non-Zero came')
                    $(markup).insertAfter('.miltable > tbody > tr:last');
                } else {
                    // alert('Zero came')
                    $(".miltable thead").show();
                    $(".miltable tbody").append(markup);
                }
                $("#milestone_name").val('');
                $("#milestone_date").val('');

                if ($("#addRow").html() == 'Update'){

                    $("#addRow").html("Add");
                    $("#addRow").prop('class', 'btn badge btn-primary');
                }
            }
            // alert($('.miltable tbody tr').length)
        },
        submit: function (draft) {
            var actual = $("#kra_table").find('#actaul_score').val();
            var achievement = $("#kra_table").find('#achievement_score').html();
            var goal_name = $("#goal_name").val();
            var milestone_values = []
            var milestone_date_values = []
            var values
            var date_values
            var someObj = [];

            $("input:checkbox").each(function () {
                var $this = $(this);

                if ($this.is(":checked")) {
                    someObj.push($this.attr("id"));
                }
            });
            if (!draft) {
                if ($('.miltable tbody tr').length > 0) {
                    $("#miltable tbody tr").each(function () {
                        values = $(this).find('td:first-child').html();
                        milestone_values.push(values)
                        date_values = $(this).find('td:nth-child(2)').html();
                        milestone_date_values.push(date_values)
                    })
                    console.log("Milestones: ", milestone_values)
                    console.log("Milestones: ", milestone_date_values)
                    if ($("#goal_data_vals").val() && someObj.length === 0 && !$("#manager_record").val() && !$("#collaborator_record").val()) {
                        console.log('Submitting goal data-1...')
                        swal({
                            text: "Are you sure want to submit without updating previous milestones ?",
                            icon: "warning",
                            dangerMode: true,
                            closeOnClickOutside: false,
                            closeModal: false,
                            buttons: {
                                confirm: { text: 'Yes, Submit', className: 'btn-info' },
                                cancel: 'No'
                            },
                        }).then(function (isConfirm) {
                            if (isConfirm) {
                                goals.final_submit(goal_name, someObj, draft, milestone_values, milestone_date_values, actual, achievement)
                            } else {
                                swal.close();
                            }
                        });
                    } else if ($("#manager_record").val() && $("#score").val() == null) {
                        console.log('Submitting goal data-2...')
                        swal({ text: "Please update your score", icon: "error", buttons: { cancel: 'OK' } })
                    } else {
                        console.log('Submitting goal data-3...')
                        goals.final_submit(goal_name, someObj, draft, milestone_values, milestone_date_values, actual, achievement)
                    }
                } else {
                    console.log('Add milestones...')
                    swal({
                        title: 'Please add at least one milestone against ' + '"' + $("#goal_name").val() + '"',
                        icon: "info",
                        closeOnClickOutside: false,
                        buttons: {
                            cancel: 'OK'
                        },
                    })
                }
            }
            else {
                if ($('.miltable tbody tr').length > 0) {
                    $("#miltable tbody tr").each(function () {
                        values = $(this).find('td:first-child').html();
                        milestone_values.push(values)
                        date_values = $(this).find('td:nth-child(2)').html();
                        milestone_date_values.push(date_values)
                    })
                }
                else if ($('.miltable tbody tr').length == 0) {
                    milestone_values = null
                    milestone_date_values = null
                }
                goals.final_submit(goal_name, someObj, draft, milestone_values, milestone_date_values, actual, achievement)
            }
        },
        dateRestrict: function (cnt) {
            var to = $("#milestone_date").datepicker({
                minDate: '0d',
                maxDate:'1y',
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true
            });

            $("#milestone_date").datepicker("option", "showAnim", "slideDown");

        },
        getDate: function (element) {
            var date;
            try {
                date = $(element).datepicker('getDate');
            } catch (error) {
                date = null;
            }
            return date;
        },
        final_submit: function (goal_name, someObj, draft, milestone_values, milestone_date_values, actual, achievement) {
            console.log('Came to Final submit...')
            var params = {
                actual: actual,
                achievement: achievement,
                someObj: someObj,
                draft: draft,
                milestones: milestone_values,
                milestone_dates: milestone_date_values,
                goal_name: goal_name,
                lm_score: $("#score").val(),
                lm_remark: $("#lm_remark").val(),
                ulm_remark: $("#ulm_remark").val(),
                survey: $("#goal_survey").val(),
                training: $("#training").val(),
                token: $("#token").val(),
                employee_name: parseInt($("#employee_name").val(), 10),
                appraisal_year: parseInt($("#appraisal_year").val(), 10),
                self_employee_id: $("#empl_id").val(),
                training_remark: $("#training_remark").val(),
            };
            console.log('Calling RPC...')
            rpc.query({
                model: 'kw_appraisal_goal',
                method: 'save_datas',
                args: [params],
            }).then(function (values) {
                // alert(values.length)
                if (values[0] == 'Self') {
                    window.location.href = '/web#action=kw_appraisal.self_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'
                }
                else if (values[0] == 'LM') {
                    window.location.href = '/web#action=kw_appraisal.lm_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'
                }
                else if (values[0] == 'ULM') {
                    window.location.href = '/web#action=kw_appraisal.ulm_actions_window&amp;model=hr_appraisal&amp;view_type=kanban&amp;menu_id=kw_appraisal.menu_hr_appraisal'
                }
                else if (values[0] != 'Self' || values[0] != 'LM' || values[0] != 'ULM' && values.length != 0) {
                    console.log('Going forword to fill the appraisal form...')
                    window.location.href = "/kw/survey/fill/" + values[0] + "/" + values[1]
                }
                if (values.length == 0) {
                    location.reload();
                }
            });
            console.log('RPC called success...')
        },
    };

    $(function () {
        goals.init();
    });
});