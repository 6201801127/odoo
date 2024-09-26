odoo.define('kw_workstation.seat_map', function (require) {
    'use strict';
    var Widget = require('web.Widget');
    var session = require('web.session');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    var QWeb = core.qweb;

    var seatmap = {
        svg_id : '',
        branch_id : 'all',
        unit_id : 'all',
        infra_id : 'all',
        infra_name : $('#infraSelect > option:selected').text(),
        assigned: '#108fbb',
        //not_assigned: '#faa635',
        not_assigned: '#ff0800',
        project_colour: '#FF33FF',
        project_sbu_colour: '#0000FF',
        //not_mapped: '#d7182a',
        not_mapped: '#cccccc',
        wfo: '#228b22',
        wfh: '#ffc30b',
        reserved: '#4b0076',
        contractual: '#33b5e5',
        hybrid: '#b7ff00',
//        contractual: '#62628B',
        bk: '',
        bk_el: '',
        employee_list:[],
        init: function(){
            var self = this;
            // $('path.workstation').removeAttr('style');
            seatmap.setParams();
            //seatmap.fetchInfra();
            setTimeout(function(){
                seatmap.get_infrastructure();
            },1000);
            seatmap._get_context();

            // seatmap.get_workstations();
            $('.btn-wfo').css({'background-color':seatmap.wfo});
            $('.btn-wfo').closest('tr').find('path').css({'fill': seatmap.wfo, 'stroke': seatmap.wfo});

            $('.btn-wfh').css({'background-color':seatmap.wfh});
            $('.btn-wfh').closest('tr').find('path').css({'fill': seatmap.wfh, 'stroke': seatmap.wfh});

            $('.btn-not-assigned').css({'background-color':seatmap.not_assigned,});
            $('.btn-not-assigned').closest('tr').find('path').css({'fill': seatmap.not_assigned, 'stroke': seatmap.not_assigned});

            $('.btn-reserved').css({'background-color':seatmap.reserved,});
            $('.btn-reserved').closest('tr').find('path').css({'fill': seatmap.reserved, 'stroke': seatmap.reserved});

            $('.btn-contractual').css({'background-color':seatmap.contractual,});
            $('.btn-contractual').closest('tr').find('path').css({'fill': seatmap.contractual, 'stroke': seatmap.contractual});

            $('.btn-hybrid').css({'background-color':seatmap.hybrid,});
            $('.btn-hybrid').closest('tr').find('path').css({'fill': seatmap.hybrid, 'stroke': seatmap.hybrid});

            $('.btn-project-horizontal').css({'background-color':seatmap.project_colour,});
            $('.btn-project-sbu').css({'background-color':seatmap.project_sbu_colour,});

//            $('.btn-assigned').css({'background-color':seatmap.assigned});
//            $('.btn-not-mapped').css({'background-color':seatmap.not_mapped});
            $('select.select2').select2({
                placeholder: "Select an employee",
                maximumSelectionSize: 2,
            });
            //multiple:true,
            $('path.workstation').dblclick(function(e){
                seatmap.showResource( $(this), e);
            });
            $('#btn-ws-tag-save').click(function(){
                seatmap.saveResource();
            });
            $('#btn-ws-tag-cancel').click(function(){
                seatmap.resetResource();
            });

            $('#branchSelect').change(function(){
                seatmap.branch_id = $(this).val();
//                seatmap.unit_id = $('#branchUnitSelect').val();
//                seatmap.infra_id = $('#infraSelect').val();
//                seatmap.infra_name = $('#infraSelect > option:selected').text();
                window.location.href = "/seat-map?branch="+seatmap.branch_id+"&unit=all&code=all";
//                window.location.href = "/seat-map?branch="+seatmap.branch_id+"&unit="+seatmap.unit_id+"&code="+seatmap.infra_id;
            });

            $('#infraSelect').change(function(){
                seatmap.infra_id = $(this).val();
//                seatmap.unit_id = $('#branchUnitSelect').val();
                seatmap.infra_name = $('#infraSelect > option:selected').text();
                window.location.href = "/seat-map?branch="+seatmap.branch_id+"&unit="+seatmap.unit_id+"&code="+seatmap.infra_id;
            });
            $('#branchUnitSelect').change(function(){
                seatmap.unit_id = $(this).val();
                //seatmap.fetchInfra();
                window.location.href = "/seat-map?branch="+seatmap.branch_id+"&unit="+seatmap.unit_id+"&code=all";
            });

            $('#EmployeeSelect').change(function(e){
                var _el = $(this);
                if(_el.val() > 0){
//                    seatmap.get_infrastructure();
                    seatmap.highlight_employee(_el.val());
                }else{
                    seatmap.get_infrastructure();
                }
            });

            $('#projectSelect').change(function(e){
                seatmap.project = $('#projectSelect').val();
                seatmap.get_infrastructure("project");
            });

        },
        setParams:function(){
            var url = new URL(window.location.href);
            seatmap.branch_id = url.searchParams.get("branch") ? url.searchParams.get("branch") : 'all';
            seatmap.unit_id = url.searchParams.get("unit") ? url.searchParams.get("unit") : 'all';
            seatmap.infra_id = url.searchParams.get("code") ? url.searchParams.get("code") : 'sixth-c';
            $('#branchSelect').val(seatmap.branch_id);
            $('#branchUnitSelect').val(seatmap.unit_id);
            $('#infraSelect').val(seatmap.infra_id);
            seatmap.infra_name = $('#infraSelect > option:selected').text();
        },
        fetchInfra: function(){
            var unit_id = $('#branchUnitSelect').val();
            if(unit_id!=''){
                ajax.jsonRpc("/infrastructurefilter", 'call', {'branch_id': unit_id})
                    .then(function (values) {
                        $("#infraSelect").empty();
                        if (values !="None"){
                            $.each( values, function( key, value ) {
                                $("#infraSelect").append('<option value='+key+'>'+value+'</option>');
                            });
                            $("#infraSelect").append('<option value="all">All</option>');
                            $("#infraSelect").val($("#infraSelect").attr('rel'));
                            seatmap.infra_name = $('#infraSelect > option:selected').text();
                        } else {
                            $("#infraSelect").append('<option value="all">All</option>');
                        }
                });
            }
        },
        refresh: function(){
            seatmap.get_infrastructure();
        },
        get_workstations: function(){
            //if($('#infraSelect').val() != 0){
            if(seatmap.infra_id != ''){
                return rpc.query({
                    model: 'kw_workstation_master',
                    method: 'get_workstations',
                    args: [{infra_id: $('#infraSelect > option:selected').attr('id')}],
                }).then(function (val) {
                    $('select.select2').select2({
                        placeholder: "Select an employee",
                        //multiple:true,
                        maximumSelectionSize: 2,
                    });
                    $.each(val, function(k, v){
                        $('select.select2').attr(k,v);
                    });
                });
            }
        },
        get_infrastructure: function(filters){
            //if($('#infraSelect').val() != 0){
            // debugger;
            //console.log(seatmap.infra_id);
            seatmap.setParams();
            var params = {'infra_id': seatmap.infra_id, 'branch_id': seatmap.branch_id, 'unit_id': seatmap.unit_id}
            if (filters == 'project') {
                params.project = seatmap.project;
                //{'project': seatmap.project}
            }
//            console.log("params------------",params,seatmap.infra_id, seatmap.infra_name);
            if(seatmap.infra_id != ''){
                var infra_code = $('#infraSelect > option:selected').val();
                if(infra_code == 'all'){
                    var branch_unit_name = $('#branchUnitSelect > option:selected').val() != 'all' ? $('#branchUnitSelect > option:selected').text() : '';
                    $('#infraSelect > option').each(function(k,v){
                        var _e = $(this);
                        $(".txt_floor_name_" + _e.val()).text(branch_unit_name != _e.text() ? branch_unit_name + ' ' + _e.text() : _e.text());
                    });
                }else{
                    var branch_unit_name = $('#branchUnitSelect > option:selected').val() != 'all' ? $('#branchUnitSelect > option:selected').text() : '';
                    $(".txt_floor_name").text(branch_unit_name != seatmap.infra_name ? branch_unit_name+' '+seatmap.infra_name : seatmap.infra_name);
                }
                var employee_list = [];
                seatmap.showLoading();
                return rpc.query({
                    model: 'kw_workstation_master',
                    method: 'get_seat_map',
                    args: [params],
                }).then(function (val) {
                    var infra = '';
                    $('path.workstation').css({ 'fill': seatmap.not_mapped, 'stroke': seatmap.not_mapped});
//                    console.log(val.seats)
//                    var employee_ids = [];
                    var employee_list = [];
                    var project_list_ids = [];
                    var project_list = [];
                    $.each(val.seats, function(k, v){
                        infra = v.infrastructure;
                        //console.log('is blocked >> ', v.is_blocked, typeof(v.is_blocked))
                        if(typeof v.path_id != 'undefined' && v.path_id != ''){
                            var _el = $('path#'+v.path_id);
                            var _assign = v.is_hybrid == true ? seatmap.hybrid : (v.is_wfh.length ? seatmap.wfh : seatmap.wfo);
                            console.log('_assign  ', _assign, v.is_hybrid, typeof(v.is_hybrid));
//                            if(typeof(v.is_contractual) == 'boolean' && v.is_contractual == true){
//                                var _title = 'Contractual || ' + (v.note ? v.note + ' || ' : '') + v.name;
//                            } else if(typeof(v.is_blocked) == 'boolean' && v.is_blocked == true){
//                                var _title = 'Reserved || ' + (v.note ? v.note + ' || ' : '') + v.name;
//                            }else{
//                                var _title = (v.emp_name != '' ? '<b>'+v.emp_name+'</b> || ' : 'Not Assigned || ') + v.name;
//                            }
                            var _title = v.name;
                            if (v.emp_ids != ''){
                                if(v.emp_ids.length > 1){
                                    $.each(v.emp_ids, function(ke, va){
//                                        employee_ids.push(va);
                                        employee_list.push({'name': v.emp_name[ke][0].trim(), 'id': va});
                                    });
                                }else{
//                                    employee_ids.push(v.emp_ids[0]);
                                    employee_list.push({'name': v.emp_name[0][0].trim(), 'id': v.emp_ids[0]});
                                }
                            }
                            if (v.project_ids != ''){
                                if(v.project_ids.length > 1){
                                    $.each(v.project_ids, function(ke, va){
                                        if (project_list_ids.indexOf(va[0]) == -1){
                                            project_list_ids.push(va[0]);
                                            project_list.push({'id':va[0], 'name':va[1]});
                                        }
                                    });
                                }else{
                                    if (project_list_ids.indexOf(v.project_ids[0][0]) == -1){
                                        project_list_ids.push(v.project_ids[0][0]);
                                        project_list.push({'id':v.project_ids[0][0], 'name':v.project_ids[0][1]});
                                    }
                                }
                            }
//                            var uniqueProjectIds = project_list_ids.filter(function(item, i, project_list_ids) {
//                                return i == project_list_ids.indexOf(item);
//                            });
                             //console.log(uniqueProjectIds,"---------",project_list_ids)
                            _el.attr({
                                'title': _title,
                                'emp_ids': v.emp_ids,
                                'station_id': v.station_id,
                                'is_blocked': v.is_blocked,
                                'is_contractual': v.is_contractual,
                                'is_hybrid': v.is_hybrid,
                                'note': v.note
                            });
                            if(typeof(v.is_contractual) == 'boolean' && v.is_contractual == true){
                                _el.css({'fill': seatmap.contractual, 'stroke': seatmap.contractual});
                            } else if(typeof(v.is_blocked) == 'boolean' && v.is_blocked == true){
                                _el.css({'fill': seatmap.reserved, 'stroke': seatmap.reserved});
                            }else{
//                                if(typeof(v.project) == 'boolean' && v.project == true) {
                                if((typeof(v.project) == 'boolean' && v.project != false) || (typeof(v.project) != 'boolean' && v.project != '')) {
                                    _el.css({
                                        'fill': v.project == 'sbu' ? seatmap.project_sbu_colour : seatmap.project_colour,
                                        'stroke': v.project == 'sbu' ? seatmap.project_sbu_colour : seatmap.project_colour
                                    });
                                } else {
                                    _el.css({
                                        'fill': v.emp_name != '' ? _assign : seatmap.not_assigned,
                                        'stroke': v.emp_name != '' ? _assign : seatmap.not_assigned
                                    });
                                }
                            }
                        }
                    });
                    console.log('projects >>> ', project_list)
                    $('#projectSelect').find('option:gt(0)').remove();
                    $.each(project_list, function(ke, ve){
                        $('#projectSelect').append('<option value="'+ve.id+'">'+ve.name+'</option>');
                    });
//                    $('#projectSelect').find('option').each(function(index, element) {
//                        var option = $(element);
//                        var projectId = parseInt(option.val());
//                        if (index > 0 && project_list_ids.indexOf(projectId) === -1) {
//                            option.remove();
//                        }
//                    });
                    console.log('employee_list >>> ', employee_list)
                    $('#EmployeeSelect').find('option:gt(0)').remove();
                    $.each(employee_list, function(ke, ve){
                        $('#EmployeeSelect').append('<option value="'+ve.id+'">'+ve.name+'</option>');
                    });

                    var tot_ws = 0 ;
                    var tot_ws_assigned = 0 ;
                    var tot_ws_not_assigned = 0 ;

                    $('#tot_wfo').html(parseInt(val.stat.total_wfo));
                    $('#tot_wfo_ico').html(parseInt(val.stat.total_wfo));
                    $('#tot_wfh').html(parseInt(val.stat.total_wfh));
                    $('#tot_wfh_ico').html(parseInt(val.stat.total_wfh));
                    $('#tot_people').html(parseInt(val.stat.total_wfo) + parseInt(val.stat.total_wfh));

                    tot_ws_assigned += parseInt(val.stat.total_cont) + parseInt(val.stat.total_reserved)
                    tot_ws_not_assigned -= parseInt(val.stat.total_cont) + parseInt(val.stat.total_reserved)
                    $('#tot_contract').html(parseInt(val.stat.total_cont));
                    $('#tot_contract_ico').html(parseInt(val.stat.total_cont));
                    $('#tot_reserved').html(parseInt(val.stat.total_reserved));
                    $('#tot_reserved_ico').html(parseInt(val.stat.total_reserved));
                    $('#tot_hybrid_ico').html(parseInt(val.stat.total_hybrid));

                    $('#tot_assigned_ws').html(parseInt(val.stat.total_wfo) + parseInt(val.stat.total_wfh) + parseInt(val.stat.total_cont) + parseInt(val.stat.total_reserved));

                    // cabins
                    tot_ws += parseInt(val.stat.total_chamber)
                    tot_ws_assigned += parseInt(val.stat.asgn_chamber)
                    tot_ws_not_assigned += parseInt(val.stat.total_chamber) - parseInt(val.stat.asgn_chamber)
                    $('#tot_ws_cabin').html(parseInt(val.stat.total_chamber));
                    $('#tot_ws_cabin_assign').html(parseInt(val.stat.asgn_chamber));
                    $('#tot_ws_cabin_notassign').html(parseInt(val.stat.total_chamber) - parseInt(val.stat.asgn_chamber));

                    //senior ws
                    tot_ws += parseInt(val.stat.total_srws)
                    tot_ws_assigned += parseInt(val.stat.asgn_srws)
                    tot_ws_not_assigned += parseInt(val.stat.total_srws) - parseInt(val.stat.asgn_srws)
                    $('#tot_ws_sr').html(parseInt(val.stat.total_srws));
                    $('#tot_ws_sr_assign').html(parseInt(val.stat.asgn_srws));
                    $('#tot_ws_sr_notassign').html(parseInt(val.stat.total_srws) - parseInt(val.stat.asgn_srws));

                    //mid ws
                    tot_ws += parseInt(val.stat.total_midws)
                    tot_ws_assigned += parseInt(val.stat.asgn_midws)
                    tot_ws_not_assigned += parseInt(val.stat.total_midws) - parseInt(val.stat.asgn_midws)
                    $('#tot_ws_mid').html(parseInt(val.stat.total_midws));
                    $('#tot_ws_mid_assign').html(parseInt(val.stat.asgn_midws));
                    $('#tot_ws_mid_notassign').html(parseInt(val.stat.total_midws) - parseInt(val.stat.asgn_midws));

                    //running ws
                    tot_ws += parseInt(val.stat.total_runningws)
                    tot_ws_assigned += parseInt(val.stat.asgn_runningws)
                    tot_ws_not_assigned += parseInt(val.stat.total_runningws) - parseInt(val.stat.asgn_runningws)
                    $('#tot_ws_running').html(parseInt(val.stat.total_runningws));
                    $('#tot_ws_run_assign').html(parseInt(val.stat.asgn_runningws));
                    $('#tot_ws_run_notassign').html(parseInt(val.stat.total_runningws) - parseInt(val.stat.asgn_runningws));

                    //intern ws
                    tot_ws += parseInt(val.stat.total_interns)
                    tot_ws_assigned += parseInt(val.stat.asgn_interns)
                    tot_ws_not_assigned += parseInt(val.stat.total_interns) - parseInt(val.stat.asgn_interns)
                    $('#tot_ws_intern').html(parseInt(val.stat.total_interns));
                    $('#tot_ws_intern_assign').html(parseInt(val.stat.asgn_interns));
                    $('#tot_ws_intern_notassign').html(parseInt(val.stat.total_interns) - parseInt(val.stat.asgn_interns));

                    //reception ws
                    tot_ws += parseInt(val.stat.total_reception)
                    tot_ws_assigned += parseInt(val.stat.asgn_reception)
                    tot_ws_not_assigned += parseInt(val.stat.total_reception) - parseInt(val.stat.asgn_reception)
                    $('#tot_reception_ws').html(parseInt(val.stat.total_reception));
                    $('#tot_reception_ws_assign').html(parseInt(val.stat.asgn_reception));
                    $('#tot_reception_ws_notassign').html(parseInt(val.stat.total_reception) - parseInt(val.stat.asgn_reception));

                    $('#tot_ws_assigned').html(tot_ws_assigned);
					$('#tot_assigned').html(tot_ws_assigned);

                    $('#tot_ws_notassigned').html(tot_ws_not_assigned);
                    $('#tot_not_assigned').html(tot_ws_not_assigned);
                    $('#tot_not_assigned_ico').html(tot_ws_not_assigned);

                    $('#tot_ws').html(tot_ws);
					$('#total_work_station').html(tot_ws);

                    //occupied
                    $('#tot_sr_occupied').html(parseInt(val.stat.occupied_srws));
                    $('#tot_cab_occupied').html(parseInt(val.stat.occupied_chamber));
                    $('#tot_mid_occupied').html(parseInt(val.stat.occupied_midws));
                    $('#tot_run_occupied').html(parseInt(val.stat.occupied_runningws));
                    $('#tot_int_occupied').html(parseInt(val.stat.occupied_interns));
                    $('#tot_rec_occupied').html(parseInt(val.stat.occupied_reception));
                    var total_occupied = parseInt(val.stat.occupied_srws) + parseInt(val.stat.occupied_chamber) + parseInt(val.stat.occupied_midws)
                                + parseInt(val.stat.occupied_runningws) + parseInt(val.stat.occupied_interns) + parseInt(val.stat.occupied_reception);
                    $('#total_occupied').html(total_occupied);

                    /* System Status*/
                    $('#tot_laptop').html(parseInt(val.stat.total_laptop));
                    $('#tot_desktop').html(parseInt(val.stat.total_pc));
                    $('#tot_onpremise').html(parseInt(val.stat.pc_office));
                    $('#tot_remote').html(parseInt(val.stat.pc_home));

                    seatmap.hideLoading();
                });
            }
        },
        _get_context: function(){
            $('.hovertext').hide();
            $(".close_hovertext").click(function(e) {$(".hovertext").hide();});
            $("path.workstation").click(function(e) {
                $(".hovertext").hide();
                var _el = jQuery(this);
                _el.css({ 'cursor':'pointer'});
//                console.log(_el.attr('is_blocked'), typeof _el.attr('is_blocked'))
//                console.log(_el.attr('is_contractual'), typeof _el.attr('is_contractual'))
//                if(_el.attr('title') != '' && typeof _el.attr('title') != 'undefined') {
                if(_el.attr('emp_ids') != '' && typeof _el.attr('emp_ids') != 'undefined') {
                    seatmap.get_employee_details(_el)
//                    $(".hovertext").html(_el.attr('title').replaceAll('||','<br/>').replace(',','<br/>'));
//                    $(".hovertext").html($("#kw_workstation_employee_information_block").html());
//                    var rendered_html = QWeb.render('kw_workstation.employee_information');
//                    console.log(rendered_html);
//                    $(".hovertext").html($(QWeb.render('kw_workstation.employee_information', {})));
                    $("#kw_workstation_employee_information_block").css({'top': e.pageY - 160, 'left': e.pageX + 20}).fadeIn('fast');
                    //_el.css({ 'fill': _el.attr('title').split('||').length > 1 ? seatmap.assigned : seatmap.not_assigned});
                } else if(_el.attr('is_blocked') != '' && typeof _el.attr('is_blocked') != 'undefined' && _el.attr('is_blocked') == 'true'){
                    $('#ws_blocked_title').html('Reserved');
                    $('#ws_blocked_workstation').html(_el.attr('title'));
                    $('#ws_blocked_note').html(_el.attr('note') != 'false' ? _el.attr('note') : '');
                    $("#kw_workstation_blocked_block").css({'top': e.pageY - 20, 'left': e.pageX + 20}).fadeIn('fast');
                } else if(_el.attr('is_contractual') != '' && typeof _el.attr('is_contractual') != 'undefined' && _el.attr('is_contractual') == 'true'){
                    $('#ws_blocked_title').html('Contractual');
                    $('#ws_blocked_workstation').html(_el.attr('title'));
                    $('#ws_blocked_note').html(_el.attr('note') != 'false' ? _el.attr('note') : '');
                    $("#kw_workstation_blocked_block").css({'top': e.pageY - 20, 'left': e.pageX + 20}).fadeIn('fast');
                } else if(_el.attr('title') != '' && _el.attr('emp_ids') == ''){
                    $('#ws_blocked_title').html('Not Assigned');
                    $('#ws_blocked_workstation').html(_el.attr('title'));
                    $('#ws_blocked_note').html('');
                    $("#kw_workstation_blocked_block").css({'top': e.pageY - 20, 'left': e.pageX + 20}).fadeIn('fast');
                } else {
                    $(".hovertext").fadeOut('fast');
                    //_el.css({ 'fill': seatmap.not_mapped});
                }
            });
//            $("path.workstation").mouseout(function(e){
//                var _el = jQuery(this);
//                _el.css({'cursor':'initial'});
//                //_el.css({'fill': ''});
//                $(".hovertext").fadeOut('fast');
//            });
        },
        showResource: function(_el, event){
            seatmap.resetResource();
            seatmap.svg_id = _el;
            // console.log(_el.attr('id'))
            var is_blocked = _el.attr('is_blocked');
            var is_contractual = _el.attr('is_contractual');
            //console.log('is_blocked  >>> ', is_blocked, typeof(is_blocked))
            if((typeof is_blocked != 'undefined' && is_blocked == 'true') || (typeof is_contractual != 'undefined' && is_contractual == 'true')){
                $('.ws-employee-field').hide();
            }else{
                $('.ws-employee-field').show();
                var emp_ids = _el.attr('emp_ids');
                if(typeof emp_ids != 'undefined' && emp_ids != ''){
                    $('#ws-employee-tag').val(_el.attr('emp_ids').split(',')).trigger('change');
                }
            }
            var station_id = _el.attr('station_id');
            if(typeof station_id != 'undefined' && station_id != ''){
                $('#ws-workstation-tag').val(_el.attr('station_id')).trigger('change');
            }
            // console.log(_el.position())
            var offset = _el.offset();
            _el.css({'stroke-width':4});
            $('#ws-employee-tag-block').addClass('active').css({'top':offset.top+50, 'left':offset.left});
        },
        resetResource: function(){
            seatmap.svg_id = '';
            $('path.workstation').css({'stroke-width':''});
            $('#ws-employee-tag-block').removeClass('active');
            $('#ws-employee-tag').val('').trigger('change');
            $('#ws-workstation-tag').val('').trigger('change');
            $('#ws-employee-tag-msg, #ws-workstation-tag-msg').removeClass('active');
        },
        saveResource: function(override){
            var override = override | false;
            var status = '';
            if($('#ws-employee-wfh').prop("checked") == true){
                status = true;
            }else{
                status = false;
            }
            var params = {
                svg_id : seatmap.svg_id.attr('id'),
                emp_ids : $('#ws-employee-tag').val(),
                ws_id : $('#ws-workstation-tag').val(),
                wfh_status : status,
                override : override,
            };
            var flag = false;
            $('#ws-employee-tag-msg, #ws-workstation-tag-msg').removeClass('active');
            /*if(params.emp_ids == '' || params.emp_ids == null){
                $('#ws-employee-tag-msg').addClass('active');
                flag = true;
            }*/

            if(params.ws_id == ''){
                $('#ws-workstation-tag-msg').addClass('active');
                flag = true;
            }

            if(flag === true){
                return false;
            }

            seatmap._save(params);
        },
        _save: function(params){
            // console.log(params);
            return rpc.query({
                    model: 'kw_workstation_master',
                    method: 'save_seat_map',
                    args: [params],
                }).then(function (response) {
                    $('#ws-employee-tag-block').removeClass('active');
//                    console.log('then.....');
//                    console.log(response);
                    seatmap.refresh();
                    //seatmap.alert({'type':'success', 'text':'Workstation details updated successfully.'});
                    seatmap.notify({'type':'success', 'text':'Workstation details updated successfully.'});
                    $('path.workstation').css({'stroke-width':''});
                }).fail(function(response){
//                    console.log('fail.....');
                    seatmap.alert({'type':'error',
                        'text':response.data.arguments[0],
                        'title':"Are you sure to continue?",
                        'ok_callback':function(){seatmap.saveResource(true);}});
                    //seatmap.notify({'type':'error', 'text':response.data.arguments[0]});
                    //seatmap.alert({'type':'error', 'text':response.data.message});
//                    console.log(response.data.arguments[0]);
//                    console.log(this);
                });
        },
        alert: function(params){
            var config = {
              title: params.text,
              //text: params.text,
              // type: params.type || "warning",
              confirmButtonText: "Ok",
              confirmButtonClass: "btn-primary btn-sm",
              showCancelButton: true,
              cancelButtonText: "Cancel",
              cancelButtonClass: "btn-danger btn-sm",
              // closeOnConfirm: false,
              // closeOnCancel: false
            };
            params.title = params.title || false
            if(params.title){
                config.title = params.title || "Are you sure?";
                config.text = params.text
            }
            swal(config,
            function(isConfirm) {
              if (isConfirm) {
//                console.log('Ok')
                    params.ok_callback();
//                seatmap.saveResource(true);
                //swal("Deleted!", "Your imaginary file has been deleted.", "success");
              } else {
//                console.log('Cancel')
                //swal("Cancelled", "Your imaginary file is safe :)", "error");
              }
            });
        },
        notify:function(params){
            var dict = {'success':'md-toast-success','error':'md-toast-error','info':'md-toast-info','warning':'md-toast-warning'};

            /*
            <div class="md-toast md-toast-warning">
                <button type="button" class="close">x</button>
                <div class="md-toast-message">I was launched via jQuery!</div>
            </div>
            */
            var close = $('<button>').attr({'type':'button'}).addClass('close').text('x');
            var message = $('<div>').addClass('md-toast-message').text(params.text);
            var toast = $('<div>').attr('class', 'md-toast').addClass(dict[params.type]).append(message);//.append(close)
            $('div#toast-container').append(toast);
            setTimeout(function(){
                toast.slideUp('slow').remove();
            }, 5000);
            //$(document).on('click', close, function(){$(this).closest('.md-toast').slideUp('slow');});
        },
        showLoading: function(){
            $.blockUI({
                message:'Loading...',
                fadeIn:700,
                fadeOut:1000,
                centerY:true,
                showOverlay:true,
                css:$.blockUI.defaults.grow1CSS
            });
        },
        hideLoading: function(){
            $.unblockUI();
        },
        get_employee_details: function(el){
            var emp_ids = el.attr('emp_ids');
            if (emp_ids != ''){
                if(seatmap.employee_list[emp_ids] === undefined){
                    var params = {'emp_id': el.attr('emp_ids')}
                    return rpc.query({
                            model: 'kw_workstation_master',
                            method: 'get_employee_information',
                            args: [{emp_id: emp_ids}],
                        }).then(function (response) {
                            seatmap.employee_list[emp_ids] = response;
                            seatmap.update_employee_info(response, el);
                        });
                }else{
                    seatmap.update_employee_info(seatmap.employee_list[emp_ids], el);
                }
            }
        },
        update_employee_info: function(response, el){
            var width = response.length == 2 ? '600px' : '400px';
            $('.employee_information_block').css({'width':width})
            $("#emp_info_workstation").html(el.attr('title'));
            $.each(response[0], function(k, v){
                if(k == 'image'){
                    $("#emp_info_"+k).attr("src", v);
                }else{
                    $("#emp_info_"+k).html(v);
                }
            });
            $(".emp_info_items_ex").hide();
            if(typeof response[1] != 'undefined'){
                $(".emp_info_items_ex").show();
                $("#emp_info2_workstation").html(el.attr('title'));
                $.each(response[1], function(k, v){
                    if(k == 'image'){
                        $("#emp_info2_"+k).attr("src", v)
                    }else{
                        $("#emp_info2_"+k).html(v);
                    }
                });
            }
        },
        highlight_employee: function(emp_id){
//            console.log(seatmap.bk, seatmap.bk_el);
            if(seatmap.bk != ''){
                seatmap.bk_el.css({'fill': seatmap.bk, 'stroke': seatmap.bk});
            }
            var employee_ids = [];
            $('.workstation').each(function(){
                var _el = $(this);
                var ws_emp_id = '';
                if(typeof _el.attr('emp_ids') != 'undefined' && _el.attr('emp_ids') != ''){
//                    console.log(_el.attr('emp_ids'), typeof _el.attr('emp_ids'), _el.attr('emp_ids').indexOf(','));
                    if(_el.attr('emp_ids').indexOf(',') > -1){
                        ws_emp_id = _el.attr('emp_ids').split(',');
//                        $.each(_el.attr('emp_ids').split(','), function(ke, va){
//                            employee_ids.push(va);
//                        });
                    }else{
                        ws_emp_id = _el.attr('emp_ids');
//                        employee_ids.push(_el.attr('emp_ids'));
                    }
//                    console.log(emp_id, ws_emp_id, typeof ws_emp_id, $.inArray(emp_id, ws_emp_id));
                    if(typeof ws_emp_id == 'string' && ws_emp_id == emp_id){
                        seatmap.bk = _el.css('fill');
                        seatmap.bk_el = _el;
                        _el.css({'fill': seatmap.project_colour, 'stroke': seatmap.project_colour});
                    }else if(typeof ws_emp_id == 'object' && $.inArray(emp_id, ws_emp_id) > -1){
                        seatmap.bk = _el.css('fill');
                        seatmap.bk_el = _el;
                        _el.css({'fill': seatmap.project_colour, 'stroke': seatmap.project_colour});
                    }
                }
            });
//            console.log(employee_ids);

        }
    };
    
    $(function(){
        seatmap.init();
    });
});