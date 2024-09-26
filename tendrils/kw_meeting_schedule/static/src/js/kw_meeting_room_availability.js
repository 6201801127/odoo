odoo.define('kw_meeting_schedule.meeting_room_onchange', function (require) {

    var AbstractField   = require('web.AbstractField');
    var concurrency     = require('web.concurrency');
    var core            = require('web.core');
    // var field_registry  = require('web.field_registry');
    var QWeb            = core.qweb;
    var registry        = require('web.field_registry');
    var relational_fields   = require('web.relational_fields');
    var FieldMany2One       = relational_fields.FieldMany2One;

    var FieldMeetingRoomChange = FieldMany2One.extend({
        //    template: null, 
        //    className: 'o_field_many2one',
         
            custom_events: _.extend({}, AbstractField.prototype.custom_events, {
                'field_changed': '_onFieldChanged',
            }),
            /**
             * @constructor
             * @override
             */
            init: function () {
                this._super.apply(this, arguments);
                this.dm = new concurrency.DropMisordered();
            }, 
            /**
             * Get the chart data through a rpc call.
             *
             * @private
             * @param {integer} meeting_id
             * @returns {Deferred}
             */
            _getMeetingData: function (meeting_data) {
                var self = this;
                // console.log(meeting_data)
                return this.dm.add(this._rpc({
                    route: '/calendar/meeting/check_recurring',
                    params: {
                        meeting_data: meeting_data,
                    },
                })).then(function (data) {
                   // console.log(data)
                   self.meeting_data = data;
                });
            },

            //--------------------------------------------------------------------------
            // Handlers
            //--------------------------------------------------------------------------

            _onFieldChanged: function (ev) {
                console.log('onchange drop down---')

                var self = this;
                // console.log(self.record.data)
                //console.log(self)

                var newValue = ev.data.changes[this.name];
                // console.log()
                if (newValue) {
                    //console.log(self)

                    //interval/ count /month_by /day /byday /week_list /final_date /end_type/ rrule_type /start/recurrency/location_id/meeting_room_id/
                    // console.log(self)

                    //var self = this;
                    setTimeout(function(){
                        _obj = self
                       // console.log(_obj)

                        if (typeof _obj.record.data.start === 'undefined' || typeof _obj.record.data.kw_start_meeting_time === 'undefined') {
                            alert("Please select start datetime ")
                            return False
                        }    
                        else if (typeof _obj.record.data.duration === 'undefined') {
                            alert("Please enter duration ")
                            return False
                        }  
                        /*else if (typeof _obj.record.data.location_id.data === 'undefined') {
                            alert("Please select location ")
                        }   */
                        else if (typeof _obj.record.data.location_id.data === 'undefined') {
                            alert("Please select location ")
                            return False
                        }
                        else if (typeof newValue === 'undefined') {
                            alert("Please select meeting room ")
                            return False
                        }

                        if (_obj.record.data.duration !='' && _obj.record.data.location_id.data.id !='' && newValue.id !='' && _obj.record.data.start !='' && _obj.record.data.kw_start_meeting_time !='') {

                            var meeting_data ={"res_id":_obj.res_id,
                                "interval":_obj.record.data.interval,
                                "count":_obj.record.data.count,
                                "month_by":_obj.record.data.month_by,
                                "day":_obj.record.data.day,
                                "byday":_obj.record.data.byday,
                                "week_list":_obj.record.data.week_list,
                                "final_date":_obj.record.data.final_date,
                                "end_type":_obj.record.data.end_type,
                                "rrule_type":_obj.record.data.rrule_type,
                                "start":_obj.record.data.start,
                                "recurrency":_obj.record.data.recurrency,
                                "location_id":_obj.record.data.location_id.data.id,
                                "meeting_room_id":newValue.id,
                                'mo':_obj.record.data.mo, 'tu':_obj.record.data.tu, 'we':_obj.record.data.we, 'th':_obj.record.data.th,
                                'fr':_obj.record.data.fr, 'sa':_obj.record.data.sa, 'su':_obj.record.data.su,
                                'duration':_obj.record.data.duration
                            }
                            self._getMeetingData(meeting_data).then(function () {

                                $('#meeting_room_availability_status').html(QWeb.render("kwmeeting_room_availability", {
                                    recurring_event_data    :self.meeting_data.recurring_event_data,
                                    event_data              :self.meeting_data.event_data,
                                    room_master_data        :self.meeting_data.room_master_data,
                                    selected_room_id        :newValue.id
                                }));

                                if (!_obj.record.data.recurrency) {
                                    var top_pos = $('.scroll_pos').eq(0).position().top - 68;
                                    $('.meeting_tbody').animate({ scrollTop: top_pos }, 'slow');
                                }
                            });  
                        }else{
                            alert("Please select meeting details. ")
                        }
                    },1000);
                }
            },
    });

    registry.add('form.kwmeeting_room_onchange', FieldMeetingRoomChange);
    return FieldMeetingRoomChange;
});
