odoo.define('kw_usability.usability_tree_view_buttons', function (require){
    "use strict";
    
    var ListController  = require('web.ListController');
    var rpc = require('web.rpc');

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (typeof this !== "undefined" && this.hasOwnProperty('modelName')){
                if (this.modelName === "kw_discuss_usability") {

                    this.$buttons.find('button.o_button_import').hide();
                    this.$buttons.find('button.o-kanban-button-new').hide();
                    this.$buttons.find('button.o_list_button_add').hide();
                    var self = this;
                    this.$buttons.on('click', '.o_list_search_button_all', function () {
                        var year = $("#years").val();
                        var month = $("#months").val();
                        if (year==0 || month == 0){
                            alert("Please choose year and month.");
                        } else{
                            rpc.query({
                                model: 'kw_discuss_usability',
                                method: 'action_search_usability',
                                args:[{'year':year,'month':month}]
                            }).then(function (result) {
                                if (result!="None"){
                                     $('.o_view_controller').empty();
                                     $(".o_view_controller:last").append("<div class='table-responsive'><table class='data-table table table-bordered table-striped fixed_headers table-hover'>\
                                            <thead class='report_thead'><tr class='rpt_heading'>\
                                                <th class='text-center' rowspan='2' width='40'> SL# </th> \
                                                <th class='text-center' rowspan='2'> Date  </th> \
                                                <th class='text-center' rowspan='2'> # Users Logged In </th> \
                                                <th class='text-center' rowspan='2'> # Users Participated in Chat </th> \
                                                <th class='text-center' colspan='3'> Message Posted </th> \
                                                <th class='text-center' colspan='2'>Channels</th>\
                                                <th class='text-center' rowspan='2'> Most Active Member </th> \
                                                <th class='text-center' rowspan='2'> Most Active Group </th> \
                                            </tr>\
                                            <tr class='rpt_heading'>\
                                                <th class='text-center'>Direct Message </th>\
                                                <th class='text-center'>Group Message</th>\
                                                <th class='text-center'>Total</th>\
                                                <th class='text-center'>Groups Created </th>\
                                                <th class='text-center'>Total Active Groups</th>\
                                            </tr> </thead>\
                                            <tbody class='report_tbody'> </tbody>\
                                            </table></div>\
                                        ");

                                    result.forEach(function (item, index) {
                                        $('.data-table .report_tbody').append("<tr><td width='40'>"+(index+1)+"</td>\
                                            <td>"+item[0]+"</td>\
                                            <td>"+item[1]+"</td>\
                                            <td>"+item[2]+"</td>\
                                            <td>"+item[3]+"</td>\
                                            <td>"+item[4]+"</td>\
                                            <td>"+item[5]+"</td>\
                                            <td>"+item[6]+"</td>\
                                            <td>"+item[7]+"</td>\
                                            <td>"+item[8]+"</td>\
                                            <td>"+item[9]+"</td></tr>");
                                    });
                                }else{
                                    $('.o_view_controller').empty();
                                    $('.o_view_controller').html("<center><h1>No records found.</h1></center>");
                                }
                            });
                        }
                    });
                    var dt = new Date();
                    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

                    setTimeout(function(){
                        var i;
                        $("#years").find('option:gt(0)').remove();
                        for(i=dt.getFullYear(); i >= 2019; i--){
                            $("#years").append('<option value="'+i+'">'+i+'</option>');
                        }
                        $("#years").val(dt.getFullYear());
                        $("#months").val(months[dt.getMonth()]);
                        $('.o_list_search_button_all').click();
                    },1000);
                }
            }
        },
    };
    ListController.include(includeDict);
});


