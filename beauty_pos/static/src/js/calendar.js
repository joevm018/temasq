odoo.define('beauty_pos.calendar', function (require) {
"use strict";
function isNullOrUndef(value) {
    return _.isUndefined(value) || _.isNull(value);
}
function is_virtual_id(id) {
    return typeof id === "string" && id.indexOf('-') >= 0;
}

var calendarView = require('web_calendar.CalendarView');
calendarView.include({
    open_quick_create: function(data_template){
        if (this.model != 'pos.order.line')
            {
                if (!isNullOrUndef(this.quick)) {
                    return this.quick.close();
                }
                var QuickCreate = this.get_quick_create_class();

                this.options.disable_quick_create =  this.options.disable_quick_create || !this.quick_add_pop;
                this.quick = new QuickCreate(this, this.dataset, true, this.options, data_template);
                this.quick.on('added', this, this.quick_created)
                        .on('slowadded', this, this.slow_created)
                        .on('closed', this, function() {
                            delete this.quick;
                            this.$calendar.fullCalendar('unselect');
                        });

                if(!this.options.disable_quick_create) {
                    this.quick.open();
                    this.quick.focus();
                } else {
                    this.quick.start();
                }
            }
    },
    update_record: function(id, data) {
    if (this.model != 'pos.order.line') {
    var r = confirm("Do you really want to update this record?");
    if (r == true) {
        var self = this;
        var event_id;
        delete(data.name); // Cannot modify actual name yet
        var index = this.dataset.get_id_index(id);
        if (index !== null) {
            event_id = this.dataset.ids[index];
            this.dataset.write(event_id, data, {context: {from_ui: true}}).always(function() {
                if (is_virtual_id(event_id)) {
                    // this is a virtual ID and so this will create a new event
                    // with an unknown id for us.
                    self.$calendar.fullCalendar('refetchEvents');
                } else {
                    // classical event that we can refresh
                    self.refresh_event(event_id);
                }
            });
        }
        return false;
    } else {
        location.reload();
    }

    } else {
        alert("Goto related order to update this record !");
        location.reload();
    }}

});
});