odoo.define('leaves_stpi.holiday_calendar', function(require) {
    "use strict";

    var core = require('web.core');
    var concurrency = require('web.concurrency');

    var AbstractAction = require('web.AbstractAction');
    var QWeb = core.qweb;

    var HolidayCalendarView = AbstractAction.extend({
        events: {
            "change #sel_branch_master": "_onBranchChange",
            "click #btnSearchHoliday": "_onSearchbuttonClick",
            "click #btnSearchMyHoliday": "_onMyHolidaybuttonClick",
            "change #showFilter": _.debounce(function() {
                $('#location_shift_filter').toggle();
                $('#employee_filter').toggle();
            }, 200, true),
        },
        init: function(parent, value) {
            this._super(parent, value);
            // var data = [];
            var self = this;
            var context = {}
            if ('context' in value){
                context = value['context']
            }
            // console.log(context)
            this.dm = new concurrency.DropMisordered();
            this.calendar = ''
            if (value.tag == 'leaves_stpi.holiday_calendar') {
                var branch_id = 0
                var shift_id = 0
                
                if('branch_id' in context) {
                    branch_id = parseInt(context['branch_id']);
                 }
                 if('shift_id' in context) {
                    shift_id = parseInt(context['shift_id']);
                 }

                var personal_calendar = 0 
                if (branch_id ==0 & shift_id==0){
                    personal_calendar = 1 
                }

                this._getCalendarMasterdata(branch_id, shift_id).then(function(result) {
                    
                    self.data = result;
                    self.render();
                    // console.log(self.data.default_branch)
                    setTimeout(function(){
                        self._create_calender(self.data.default_branch,self.data.default_shift,personal_calendar,0);
                    },0);

                });
                //in case of redirection from shift master, display the location wise filter and hide personalized filter
                // if ('branch_id' in context & 'shift_id' in context & personal_calendar == 0){
                    
                //     setTimeout(function(){ $('#showFilter').prop('checked', true);$('#location_shift_filter').show();
                //     $('#employee_filter').hide(); }, 1000);
                // }
            }

        },
        // willStart: function () {

        //     return $.when(ajax.loadLibs(this), this._super());            
        // },

        render: function() {
            var super_render = this._super;
            var self = this;
            $(".o_menu_apps").find('.dropdown-menu[role="menu"]').removeClass("show");
            var kw_calendar = QWeb.render('leaves_stpi.holiday_calendar', {
                master_data: self,
            });
            $(kw_calendar).prependTo(self.$el);
            // $('#location_shift_filter').hide();
            $('#sel_branch_master').val($('#sel_branch_master').attr('data-selected'));
            $('#sel_shift').val($('#sel_shift').attr('data-selected'));
            $('#sel_employee').val($('#sel_employee').attr('data-selected'));
            
            return kw_calendar;
        },
        _create_calender: function(branch_id, shift_id,personal_calendar,employee_id) {
            var currentYear = new Date().getFullYear();
            // var yearSave    = new Date().getFullYear();
            var calender = new Calendar('#holiday_calender', {
                style: 'custom',
                maxDate: new Date(currentYear, 11, 31),
                dataSource: [],
                customDataSourceRenderer: function(element, date, event) {
                    if(event[0].color == '#00A09D') { $(element).css('color', '#FFF');}
                    if(event[0].color == '#d83d2b') { $(element).css('color', '#FFF');}

                     //'color', '#FFF',

                    $(element).css('background-color', event[0].color);
                    $(element).css('border-radius', '0px');
                },
                mouseOnDay: function(e) {
                    if (e.events.length > 0) {
                        var content = '';
                        var color   = ''
                        for (var i in e.events) {
                            color  = e.events[i].prime_color

                            if(e.events[i].prime_color == '#ffffff'){color  = '#00A09D'}
                            content += '<div class="event-tooltip-content">' +
                                '<div class="event-name" style="color:' + color + '">' + e.events[i].name + '</div>'
                                // + '<div class="event-details">' + e.events[i].details + '</div>'
                                +
                                '</div>';
                        }
                        $(e.element).popover({
                            trigger: 'manual',
                            container: 'body',
                            html: true,
                            content: content
                        });

                        $(e.element).popover('show');

                    }
                },
                mouseOutDay: function(e) {
                    if (e.events.length > 0) {
                        $(e.element).popover('hide');
                    }
                },
                yearChanged: function(e) {

                    $('.holiday_year').hide()
                    $('.' + e.currentYear).show()
                        // $('#holiday_calender').data('calendar').setDataSource(dataSource);
                },

            });
           
            this._getHolidayData(branch_id, shift_id,personal_calendar,employee_id).then(function(result) {
                
                var max_date_holiday = new Date(currentYear, 11, 31)
                if (result) {
                    $('.holiday_year').hide()
                    $('.' +currentYear).show()
                    if(result.length >0) {
                        max_date_holiday = new Date(result[result.length-1].year, 11, 31)     
                    }
                }
                calender.setDataSource(result)
                calender.setMaxDate(max_date_holiday)
            });

            this._getHolidayDataNames(branch_id, shift_id,personal_calendar,employee_id).then(function(result) {
                $('.holidays').html('')
                console.log(result)
                if (result.holiday_calendar) {
                    var holiday_div = '<ul>'
                    $.each(result.holiday_calendar, function(key, value) {
                        // console.log(value)
                        if (value.week_off == 'gh') {
                            // $('.justify-content-center').after("<b> Name: </b>" + value.name + " <b>Start Date:</b> " + value.startDate + " <b>End Date:</b> " +value.endDate + "</br>");
                            holiday_div += '<li class="row ' + value.year + ' holiday_year mb-3"><span class="col-4 pr-0 font-weight-bold" style="color: #d83d2b">' + value.formatted_holiday_date + '</span><span class="col-8 pl-0">' + value.name + '</span></li>'
                        }
                        if (value.week_off == 'rh') {
                            // $('.justify-content-center').after("<b> Name: </b>" + value.name + " <b>Start Date:</b> " + value.startDate + " <b>End Date:</b> " +value.endDate + "</br>");
                            holiday_div += '<li class="row ' + value.year + ' holiday_year mb-3"><span class="col-4 pr-0 font-weight-bold" style="color: #00A09D">' + value.formatted_holiday_date + '</span><span class="col-8 pl-0">' + value.name + '</span></li>'
                        }
                        
                    });

                    holiday_div += '</ul>'
                    $('.holidays').html(holiday_div)
                }
            });

        },

        // },

        
        _getCalendarMasterdata: function(branch_id, shift_id) {

            return this._rpc({
                model   : 'resource.calendar.leaves',
                method  : 'get_calendar_master_data',
                args    : [branch_id, shift_id],
            }, []).then(function(result) {
                return result;
            });
        },

        _getHolidayData: function(branch_id, shift_id,personal_calendar,employee_id) {
            var self = this;

            return this.dm.add(this._rpc({
                model   : 'resource.calendar.leaves',
                method  : 'get_calendar_global_leaves',
                args    : [branch_id, shift_id,personal_calendar,employee_id],

            }, [])).then(function(result) {
                // console.log(result[0])
                if (result[0].holiday_calendar) {
                    return result[0].holiday_calendar.map(r => ({
                        startDate   : new Date(r.date_to),
                        endDate     : new Date(r.date_to),
                        name        : r.name,
                        week_off    : r.week_off,
                        color       : r.color,
                        year        : r.year,
                        holidayDate : r.formatted_holiday_date,
                        overlap_public_holiday:r.overlap_public_holiday,
                        prime_color :r.prime_color
                    }));
                }
                return [];

                // self.holiday_data = data;
            });
        },

        _getHolidayDataNames: function(branch_id, shift_id,personal_calendar,employee_id) {
            var self = this;

            return this.dm.add(this._rpc({
                model   : 'resource.calendar.leaves',
                method  : 'get_calendar_global_leaves',
                args    : [branch_id, shift_id,personal_calendar,employee_id],

            }, [])).then(function(result) {
                // console.log(result[0])
                
                return result[1];

                // self.holiday_data = data;
            });
        },
        _onSearchbuttonClick: function(event) {

            // event.preventDefault();

            var branch_id = $('#sel_branch_master').val();
            var shift_id = $('#sel_shift').val();
            // console.log(branch_id)

            if (typeof branch_id === 'undefined') {
                alert("Please select a branch ")
                return false
            } else if (typeof shift_id === 'undefined' || shift_id == null) {
                alert("Please select a shift")
                return false
            }

            this._create_calender(branch_id, shift_id,0,0)
        },
        _onMyHolidaybuttonClick:function(event){
            var employee_id = $('#sel_employee').val();
            if (typeof employee_id === 'undefined') {
                alert("Please select employee")
                return false
            } 

            this._create_calender(0,0,1,employee_id)
        },

        _onBranchChange: function(event) {

            // event.preventDefault();
            var self = this;
            var branch_id = $('#sel_branch_master').val();
           
            if (typeof branch_id === 'undefined') {
                alert("Please select a branch ")
                return False
            }
            this._getCalendarMasterdata(branch_id,0).then(function(result) {
                // console.log(result)
                self.data = result;

                var tabDiv = '';
                $(self.data.shift_master).each(function(j, shift_master) {

                    tabDiv += '<option value="' + shift_master.id + '" >';
                    tabDiv += shift_master.name;
                    tabDiv += '</option>';
                });
                // console.log(tabDiv)
                $("#sel_shift").html(tabDiv);

            });



        },
    });
    core.action_registry.add('leaves_stpi.holiday_calendar', HolidayCalendarView);
    return HolidayCalendarView;



});

$(document).ready(function() {

});