odoo.define('scheduler_extended_tres_jolie.SchedulerExtended', function(require){
    "use strict";

    var GrouppedCalendar = require("calendar_scheduler.GrouppedCalendar");
    var Model = require('web.DataModel');
    var core = require('web.core');
    var utils = require('web.utils');
    var session = require('web.session');

    var Qweb = core.qweb;
    var _t = core._t;

    var STATE_MAP = ['Booked', 'Confirmed'];

    function isNullOrUndef(value) {
        return _.isUndefined(value) || _.isNull(value);
    }

    GrouppedCalendar.include({
        willStart: function () {
            var self = this;
            return this._super().then(function () {
                var context = session.user_context;
                context.view_origin = "scheduler_state_map";
                new Model('pos.order.line').call('get_formview_id', [[''], context]).then(function (view_id) {
                    self.context_menu_popup = view_id;
                });
            });
        },
        get_fc_init_options: function () {
            var self = this;
            var options = this._super();
            options['eventRender'] = function (event, element, view) {
                element.find('.fc-event-title').html(event.title + event.attendee_avatars);
                self.updateSessionIndicator(element, event);
            };
            options['stateCtrl'] = function (ev1, ev2) {
                var curr_state = ev1.state_appt;
                if (!_.contains(STATE_MAP, curr_state))
                    return false;
                if (curr_state == 'Confirmed' && ev1.checkin == true)
                    return false
                return self.do_action({
                    type:'ir.actions.act_window',
                    res_id: ev1.id,
                    res_model: 'pos.order.line',
                    views: [[self.context_menu_popup, 'form']],
                    target: 'new',
                    context: self.dataset.context || {},
                    name: "Modify Appointment",
                }, {
                    on_close: function (result) {
                        self.$calendar.fullCalendar2('refetchEvents');
                    }
                });
            };
            return options;
        },

        updateSessionIndicator: function ($el, data) {
            if (data.is_last_session != true)
                return
            $el.addClass("show_session_indicator");
            $el.prepend("<div class='session_indicator'/>");
        },
        event_data_transform: function(evt) {
            var data = this._super(evt);
            data.is_last_session = evt.is_last_session;
            return data;
        }
    });
});
