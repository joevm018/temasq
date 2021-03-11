odoo.define('calendar_scheduler.widgets', function(require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var form_common = require('web.form_common');
var Widget = require('web.Widget');
var Model = require('web.DataModel');

var _t = core._t;
var QWeb = core.qweb;

Date.prototype.addMinutes = function(minute) {
   this.setTime(this.getTime() + (minute*60*1000));
   return this;
}

/**
 * Quick creation view.
 *
 * Triggers a single event "added" with a single parameter "name", which is the
 * name entered by the user
 *
 * @class
 * @type {*}
 */
var QuickCreate = Dialog.extend({
    events: {
//        'change .staff': 'change_staff',
        'change .services': 'change_services',
        'change .customer_type': 'change_customer_type',
        'click .add_new_order': 'add_new_order',
        'click .delete_order': 'delete_order',
        'click .add_new_customer': 'add_new_customer',
        'click .delete_new_customer_class': 'delete_new_customer_class',
//        'click .create_new_customer_class': 'create_new_customer_class',
    },
    init: function(parent, dataset, buttons, options, data_template) {
        this.dataset = dataset;
        this._buttons = buttons || false;
        this.options = options;
        this.customer_by_name = [];
        this.services = [];
        this.config_staff_type = [];
        this.staffs = [];
        this.startt = [];
        this.staff_assigned = [];
        this.operation_id = 0;
        this.customer_by_id = [];

        // Can hold data pre-set from where you clicked on agenda
        this.data_template = data_template || {};
        this.$input = $();
        var sel_start, temp;
        try {
            temp = data_template.procedure_start.split(" ");
            sel_start = temp[1].slice(0, -3)
        }
        catch (err) {}

        var self = this;

        if (parent.time_schedule) {
            self.services = parent.services;
//            var first_duration = 0;
//            if (parent.services){
//                  var duation_get = new Model('product.product').call('get_duration_in_min', [parent.services[0].id])
//                    .then(function (duration_product) {
//                          first_duration = duration_product;
//                          console.log(duration_product, "===========15==")
//                    });
//            }
            self.staffs = parent.resources;
            self.staff_assigned = parseInt(self.data_template.staff_assigned_id);
            self.customer_by_name = parent.customer_by_name;
            self.config_staff_type = parent.config_staff_type;
            self.customer_by_id = parent.customer_by_id;
            self.startt = sel_start;
            var options = {
                time_schedule: parent.time_schedule,
                scheduler_hour: parent.scheduler_hour,
                scheduler_minute: parent.scheduler_minute,
                start_minute: sel_start.split(":")[0],
                start_second: sel_start.split(":")[1],
                start: sel_start,
                staff: parent.resources,
                staff_assigned: parseInt(self.data_template.staff_assigned_id),
                services: parent.services,
                config_staff_type: parent.config_staff_type,
            };
            this._super(parent, {
                title: this.get_title(),
                size: 'large',
                buttons: this._buttons ? [
                    {
                        text: _t("Create"), classes: 'btn-primary', click: function () {
                        if (!self.quick_add_saloon()) {
                            self.focus();
                        }
                    }
                    },
//                    {
//                        text: _t("Edit"), click: function () {
//                        self.slow_add();
//                    }
//                    },
                    {text: _t("Cancel"), close: true},
                ] : [],
                $content: QWeb.render('CalendarView2.quick_create', {
                    widget: this,
                    options: options
                })
            });
        }
        else {
            this._super(parent, {
                title: this.get_title(),
                size: 'small',
                buttons: this._buttons ? [
                    {
                        text: _t("Create"), classes: 'btn-primary', click: function () {
                        if (!self.quick_add()) {
                            self.focus();
                        }
                    }
                    },
                    {
                        text: _t("Edit"), click: function () {
                        self.slow_add();
                    }
                    },
                    {text: _t("Cancel"), close: true},
                ] : [],
                $content: QWeb.render('CalendarView.quick_create', {
                    widget: this,
                })
            });
        }
    },
    find_time_schedule: function(start, end) {
            /*Will return the time duration for the day
            * as 15 minute slots */
            function n(n){
                return n > 9 ? "" + n: "0" + n;
            }
            var schedule = [], temp;
            for (var i=start; i<end; i++) {
                for (var j=0;j<4;j++) {
                    temp = n(i) + ':' + n(j * 15);
                    schedule.push(temp);
                }
            }
            return schedule;
        },
    find_scheduler_hour_schedule: function(start, end) {
            function n(n){
                return n > 9 ? "" + n: "0" + n;
            }
            var schedule = [], temp;
            for (var i=start; i<end; i++) {

                    temp = n(i) ;
                    schedule.push(temp);

            }
            return schedule;
        },
    delete_order: function (e) {
       var str = e.currentTarget.id;
       var curr_sl_no = str.split("delete_order_")[1]
        var for_curr_sl_no = parseInt(curr_sl_no)+1;
        var for_operation_id = this.operation_id+1;
        for (var i=for_curr_sl_no;i<=for_operation_id;i++) {
            var i_minus = i-1;
            var id_border_class = document.getElementById('border_class_' + i);
            id_border_class.id = 'border_class_' + i_minus;
            var id_sl_no = document.getElementById('sl_no_' + i);
            id_sl_no.id = 'sl_no_' + i_minus;
            id_sl_no.value = i_minus;
            var id_delete_order = document.getElementById('delete_order_' + i);
            id_delete_order.id = 'delete_order_' + i_minus;
            var id_modal_scheduler_hour = document.getElementById('modal_scheduler_hour_' + i);
            id_modal_scheduler_hour.id = 'modal_scheduler_hour_' + i_minus;
            var id_modal_scheduler_minute = document.getElementById('modal_scheduler_minute_' + i);
            id_modal_scheduler_minute.id = 'modal_scheduler_minute_' + i_minus;
            var id_duration = document.getElementById('duration_' + i);
            id_duration.id = 'duration_' + i_minus;
            var id_staff = document.getElementById('staff_' + i);
            id_staff.id = 'staff_' + i_minus;
            var id_services = document.getElementById('services_' + i);
            id_services.id = 'services_' + i_minus;
        }
        this.operation_id -=1;
        var del_div_border_class = document.getElementById('border_class_' + curr_sl_no);
        del_div_border_class.parentNode.removeChild(del_div_border_class);
        for (var i=1;i<=this.operation_id+1;i++) {
            var id_modal_scheduler_hour = document.getElementById('modal_scheduler_hour_' + i);
            var id_modal_scheduler_minute = document.getElementById('modal_scheduler_minute_' + i);
            var id_duration = document.getElementById('duration_' + i);

            if (i!=1){
                var prev_operation_id = i-1;
                var modal_scheduler_hour_prev = document.getElementById('modal_scheduler_hour_' + prev_operation_id);
                var modal_scheduler_minute_prev = document.getElementById('modal_scheduler_minute_' + prev_operation_id);
                var duration_prev = document.getElementById('duration_' + prev_operation_id);
                if((modal_scheduler_minute_prev && modal_scheduler_hour_prev) && duration_prev){
                    var modal_scheduler_hour_prevValue = modal_scheduler_hour_prev.options[modal_scheduler_hour_prev.selectedIndex].value;
                    var modal_scheduler_minute_prevValue = modal_scheduler_minute_prev.options[modal_scheduler_minute_prev.selectedIndex].value;
                    var duration_prevValue = duration_prev.value;
                    var p_start_date = this.data_template.procedure_start;
                    var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(":")
                    var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(modal_scheduler_minute_prevValue)
                    var time_d = modal_scheduler_hour_prevValue.concat(":00")
                    var p_start_time = p_start_date.split(" ")[0].concat(" ")
                    p_start_time = p_start_time.concat(time_d)
                    var start_time = new Date(p_start_time);
                    start_time.addMinutes(duration_prevValue);
                    var hours = start_time.getHours()
                    if (hours < 10) {
                        hours = "0" + hours;
                    }
                    var Minutes = start_time.getMinutes()
                    if (Minutes < 10) {
                        Minutes = "0" + Minutes;
                    }
                    hours = hours.toString();
                    var hours_Minutes = hours.concat(":")
                    hours_Minutes = hours_Minutes.concat(Minutes)
                    id_modal_scheduler_hour.value = hours;
                    id_modal_scheduler_minute.value = Minutes;
                    }
            }
        }
    },
    add_new_customer: function (e) {
        $('input.customer_type').prop("checked", false).trigger("change", false);
        $('.add_new_customer').css('visibility', 'hidden');
        $('.delete_new_customer_class').css('visibility', 'visible');
    },
    delete_new_customer_class: function (e) {
        $('input.customer_type').prop("checked", true).trigger("change", true);
        $('.delete_new_customer_class').css('visibility', 'hidden');
        $('.add_new_customer').css('visibility', 'visible');
    },
    add_new_order: function (e) {
        this.time_schedule = this.find_time_schedule(0, 24);
        this.scheduler_hour = this.find_scheduler_hour_schedule(0, 24);
        this.scheduler_minute = this.find_scheduler_hour_schedule(0, 60);
        this.operation_id +=1;
        var table_str = '';
        var sl_no = this.operation_id + 1
        table_str += '<div class="one" id="border_class_'+ sl_no +'">';
        table_str += '<div class="border_class">';
        table_str += '<div class="service_start_t">';
        table_str += '<input class="sl_no" readonly="1" type="text"  value="' + sl_no +'" id="sl_no_'+ sl_no +'"/>';
        table_str += '<button class="delete_order" id="delete_order_'+ sl_no +'">';
        table_str += '<img style="pointer-events: none;" class="close_icon" src="/calendar_scheduler/static/src/img/close.png" width="28" height="28" />';
        table_str += '</button>';
        table_str += '</div>';
        table_str += '<div class="service_start">';
        table_str += '<div class="start_icon_div">';
        table_str += '<div class="timer">';
        table_str += '<img style="pointer-events: none;" src="/calendar_scheduler/static/src/img/timeicon.png" width="32" height="32" />';
        table_str += '</div>';
        table_str += '</div>';
        table_str += '<div class="start_div">';

        table_str += '<select class="modal_scheduler_hour" id="modal_scheduler_hour_'+ sl_no +'">';
        for (var j=0;j<this.scheduler_hour.length;j++) {
            var prev_operation_id = this.operation_id;
            var modal_scheduler_hour_prev = document.getElementById('modal_scheduler_hour_' + prev_operation_id);
            var modal_scheduler_minute_prev = document.getElementById('modal_scheduler_minute_' + prev_operation_id);
            var duration_prev = document.getElementById('duration_' + prev_operation_id);
            if((modal_scheduler_minute_prev && modal_scheduler_hour_prev) && duration_prev){
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prev.options[modal_scheduler_hour_prev.selectedIndex].value;
                var modal_scheduler_minute_prevValue = modal_scheduler_minute_prev.options[modal_scheduler_minute_prev.selectedIndex].value;
                var duration_prevValue = duration_prev.value;
                var p_start_date = this.data_template.procedure_start;
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(":")
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(modal_scheduler_minute_prevValue)
                var time_d = modal_scheduler_hour_prevValue.concat(":00")
                var p_start_time = p_start_date.split(" ")[0].concat(" ")
                p_start_time = p_start_time.concat(time_d)
                var start_time = new Date(p_start_time);
                start_time.addMinutes(duration_prevValue);
                var hours = start_time.getHours()
                if (hours < 10) {
                    hours = "0" + hours;
                }
                var Minutes = start_time.getMinutes()
                if (Minutes < 10) {
                    Minutes = "0" + Minutes;
                }
                hours = hours.toString();
                var hours_Minutes = hours.concat(":")
                hours_Minutes = hours_Minutes.concat(Minutes)
                if (hours == this.scheduler_hour[j]) {
                  table_str += '<option selected="True" value="' + hours +'">' + hours +'</option>';
                }
                else{
                    table_str += '<option value="' + this.scheduler_hour[j] +'">' + this.scheduler_hour[j] +'</option>';
                }
                }
            else{
                    table_str += '<option value="' + this.scheduler_hour[j] +'">' + this.scheduler_hour[j] +'</option>';
                }
        }
        table_str += '</select>';
        table_str += '<select class="modal_scheduler_minute" id="modal_scheduler_minute_'+ sl_no +'">';
        for (var j=0;j<this.scheduler_minute.length;j++) {
            var prev_operation_id = this.operation_id;
            var modal_scheduler_hour_prev = document.getElementById('modal_scheduler_hour_' + prev_operation_id);
            var modal_scheduler_minute_prev = document.getElementById('modal_scheduler_minute_' + prev_operation_id);
            var duration_prev = document.getElementById('duration_' + prev_operation_id);
            if((modal_scheduler_minute_prev && modal_scheduler_hour_prev) && duration_prev){
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prev.options[modal_scheduler_hour_prev.selectedIndex].value;
                var modal_scheduler_minute_prevValue = modal_scheduler_minute_prev.options[modal_scheduler_minute_prev.selectedIndex].value;
                var duration_prevValue = duration_prev.value;
                var p_start_date = this.data_template.procedure_start;
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(":")
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(modal_scheduler_minute_prevValue)
                var time_d = modal_scheduler_hour_prevValue.concat(":00")
                var p_start_time = p_start_date.split(" ")[0].concat(" ")
                p_start_time = p_start_time.concat(time_d)
                var start_time = new Date(p_start_time);
                start_time.addMinutes(duration_prevValue);
                var hours = start_time.getHours()
                if (hours < 10) {
                    hours = "0" + hours;
                }
                var Minutes = start_time.getMinutes()
                if (Minutes < 10) {
                    Minutes = "0" + Minutes;
                }
                hours = hours.toString();
                var hours_Minutes = hours.concat(":")
                hours_Minutes = hours_Minutes.concat(Minutes)
                if (Minutes == this.scheduler_minute[j]) {
                  table_str += '<option selected="True" value="' + Minutes +'">' + Minutes +'</option>';
                }
                else{
                    table_str += '<option value="' + this.scheduler_minute[j] +'">' + this.scheduler_minute[j] +'</option>';
                }
                }
            else{
                    table_str += '<option value="' + this.scheduler_minute[j] +'">' + this.scheduler_minute[j] +'</option>';
                }

        }
        table_str += '</select>';

        table_str += '</div>';
        table_str += '<div class="duration_icon_div">';
        table_str += '<div class="duration_icon">';
        table_str += '<img style="pointer-events: none;" src="/calendar_scheduler/static/src/img/duration.jpg" width="32" height="32" />';
        table_str += '</div>';
        table_str += '</div>';
        table_str += '<div class="duration_div">';
//        var sl_no = this.operation_id + 1
        table_str += '<input class="duration" type="text" value="0" id="duration_'+ sl_no +'">';
        table_str += '</div>';
        table_str += '</div>';
        table_str += '<div class="staff_service">';
        table_str += '<div class="staff_icon_div">';
        table_str += '<div class="staff_icon">';
        table_str += '<img style="pointer-events: none;" src="/calendar_scheduler/static/src/img/staff.png" width="32" height="32" />';
        table_str += '</div>';
        table_str += '</div>';
        table_str += '<div class="staff_div">';
        table_str += '<select class="staff" id="staff_'+ sl_no +'">';
        if(this.config_staff_type == 'service_based_staff'){
            for (var j=0;j<this.staffs.length;j++) {
                var service_no_1 = ""
                if(this.services){
                    service_no_1 = this.services[0]
                }
                for (var staf=0;staf<service_no_1.staff_ids.length;staf++) {
                    if(service_no_1.staff_ids[staf]==this.staffs[j].id){
                        var staff_prev = document.getElementById('staff_' + prev_operation_id);
                        if(staff_prev){
                            var staff_prevValue = staff_prev.options[staff_prev.selectedIndex].value;
                            if (staff_prevValue == this.staffs[j].id) {
                              var staff_dict = this.staffs[j]
                              table_str += '<option  selected="True" value="' + this.staffs[j].id +'">' + this.staffs[j].name +'</option>';
                            }
                            else{
                                table_str += '<option value="' + this.staffs[j].id +'">' + this.staffs[j].name +'</option>';
                            }
                        }
                        else{
                            table_str += '<option value="' + this.staffs[j].id +'">' + this.staffs[j].name +'</option>';
                        }
                    }
                }
            }
        }
        else{
            for (var j=0;j<this.staffs.length;j++) {
                var staff_prev = document.getElementById('staff_' + prev_operation_id);
                if(this.staffs[j].is_beautician){
                    if(staff_prev){
                        var staff_prevValue = staff_prev.options[staff_prev.selectedIndex].value;
            //            if (this.staff_assigned == this.staffs[j].id) {
                        if (staff_prevValue == this.staffs[j].id) {
                          var staff_dict = this.staffs[j]
                          table_str += '<option  selected="True" value="' + this.staffs[j].id +'">' + this.staffs[j].name +'</option>';
                        }
                        else{
                            table_str += '<option value="' + this.staffs[j].id +'">' + this.staffs[j].name +'</option>';
                        }
                    }
                    else{
                          table_str += '<option value="' + this.staffs[j].id +'">' + this.staffs[j].name +'</option>';
                        }
                    }
            }
        }
        table_str += '</select>';
        table_str += '</div>';
        table_str += '<div class="existing_service_icon">';
        table_str += '<img style="pointer-events: none;" src="/calendar_scheduler/static/src/img/service_icon.png" width="32" height="32" />';
        table_str += '</div>';
        table_str += '<div class="service_div">';
        table_str += '<select class="services" name="states[] placeholder="Services" id="services_'+ sl_no +'">';
        for (var j=0;j<this.services.length;j++) {
//            if (staff_dict) {
//                for (var serv=0;serv<staff_dict.service_ids.length;serv++){
//                   if (staff_dict.service_ids[serv] == this.services[j].id) {
                        table_str += '<option value="' + this.services[j].id +'">' + this.services[j].name +'</option>';
//                    }
//                }
//
//            }
        }
        table_str += '</select>';
        table_str += '</div>';
        table_str += '</div>';
        table_str += '</div>';
        table_str += '</div>';
		$('#progres_table').append(table_str);
		this.change_services()
		this.$('#services_'+ sl_no + '').select2();
		this.$('#staff_'+ sl_no + '').select2();
    },
    change_staff: function (event) {
        var class_event = event.target.id;
        var op_id_here = class_event.split("staff_")[1];
        var staff = document.getElementById('staff_' + parseInt(op_id_here));
        var services_here = document.getElementById('services_' + parseInt(op_id_here));
        if (staff){
            var staff_service_str = ''
            var staffValue = staff.options[staff.selectedIndex].value;
            for (var staf=0;staf<this.staffs.length;staf++) {
                if(this.staffs[staf].id == staffValue){
                    for (var staf_serv=0;staf_serv<this.staffs[staf].service_ids.length;staf_serv++) {
                        for (var serv=0;serv<this.services.length;serv++) {
                            if (this.staffs[staf].service_ids[staf_serv] == this.services[serv].id) {
                            if(staff_service_str){
                                staff_service_str += '<option value="' + this.services[serv].id +'">' + this.services[serv].name +'</option>';
                            }
                            else{
                                staff_service_str += '<option selected="True" value="' + this.services[serv].id +'">' + this.services[serv].name +'</option>';
                            }
                            }
                        }
                    }
                }
            }
//            $('#services_'+ op_id_here).attr('selected', '');
//            $('#services_'+ op_id_here).removeAttr('selected');
//            $('#services_'+ op_id_here).val = '';
//            console.log($('#services_'+ op_id_here).selectedIndex)
//            console.log(services_here.value)
//            services_here.innerHTML = ""
//            $('#services_'+ op_id_here)[0].selectedIndex = 0

//            $('#services_'+ op_id_here)[0].selectedIndex = -1;
//            services_here.val = -1;
//            console.log(services_here.value)

//            $('#services_'+ op_id_here).removeAttr('selected')
//            $('#services_'+ op_id_here).find("option:selected").removeAttr("selected");

//            services_here.value = '';
//            services_here.options[services_here.selectedIndex].value;
//            console.log($('#services_'+ op_id_here).find('option'))
//            $('#services_'+ op_id_here).find('option').remove().end().append(staff_service_str)
            $('#services_'+ op_id_here).empty().append(staff_service_str)
        }
    },
    change_services: function () {
        var op_id_here = this.operation_id+1;
        var services = document.getElementById('services_' + parseInt(op_id_here));
        if(services.options[services.selectedIndex]){
            var servicesValue = services.options[services.selectedIndex].value;
            var duration = document.getElementById('duration_' + parseInt(op_id_here));
            var duation_get = new Model('product.product').call('get_duration_in_min', [servicesValue])
                .then(function (duration_product) {
                      duration.value = duration_product;
                });
            var service = document.getElementById('services_' + parseInt(op_id_here));
            var staff_here = document.getElementById('staff_' + parseInt(op_id_here));
            if(this.config_staff_type == 'service_based_staff'){
                if (service){
                    var service_staff_str = ''
                    var serviceValue = service.options[service.selectedIndex].value;
                    for (var servi=0;servi<this.services.length;servi++) {
                        if(this.services[servi].id == serviceValue){
                            for (var staf_serv=0;staf_serv<this.services[servi].staff_ids.length;staf_serv++) {
                                for (var stafs=0;stafs<this.staffs.length;stafs++) {
                                    if (this.services[servi].staff_ids[staf_serv] == this.staffs[stafs].id) {
                                        var prev_operation_id = op_id_here-1;
                                        var staff_prev = document.getElementById('staff_' + prev_operation_id);
                                        if(staff_prev){
                                            var staff_prevValue = staff_prev.options[staff_prev.selectedIndex].value;
                                            if (staff_prevValue == this.staffs[stafs].id) {
    //                                          var staff_dict = this.staffs[stafs]
                                              service_staff_str += '<option selected="True" value="' + this.staffs[stafs].id +'">' + this.staffs[stafs].name +'</option>';
                                            }
                                            else{
                                                service_staff_str += '<option value="' + this.staffs[stafs].id +'">' + this.staffs[stafs].name +'</option>';
                                            }
                                        }
                                        else{
                                            service_staff_str += '<option value="' + this.staffs[stafs].id +'">' + this.staffs[stafs].name +'</option>';
                                        }
                                    }
                                }
                            }
                        }
                    }
                    $('#staff_'+ op_id_here).empty().append(service_staff_str)
                }
            }
        }
    },
    change_customer_type: function () {
        var checked = $('input.customer_type').prop("checked");
        if (checked == true) {
            $('.customer_new_name').val('');
            $('.customer_new_phone').val('');
            $('.customer_new_dob_day').val('');
            $('.customer_new_dob_month').val('');
            $('.customer_name').css('visibility', 'visible');
            $('.customer_new_name').css('visibility', 'hidden');
            $('.customer_new_phone').css('visibility', 'hidden');
            $('.customer_new_dob_day').css('visibility', 'hidden');
            $('.customer_new_dob_month').css('visibility', 'hidden');
        }
        else{
            $('.customer_name').val('');
            $('.customer_new_name').css('visibility', 'visible');
            $('.customer_new_phone').css('visibility', 'visible');
            $('.customer_new_dob_day').css('visibility', 'visible');
            $('.customer_new_dob_month').css('visibility', 'visible');
            $('.customer_name').css('visibility', 'hidden');
        }
    },
    get_title: function () {
        var parent = this.getParent();
        if (_.isUndefined(parent)) {
            return _t("Mark Booking");
        }
        var title = (_.isUndefined(parent.field_widget)) ?
                (parent.title || parent.string || parent.name) :
                (parent.field_widget.string || parent.field_widget.name || '');
        return _t("Create: ") + title;
    },
    start: function () {
        var self = this;

        if (this.options.disable_quick_create) {
            this.slow_create();
            return;
        }
        this.on('added', this, function() {
            self.close();
        });

        function split(val) {
            return val.split(/,\s*/);
        }
        function extractLast(term) {
            return split(term).pop();
        }
        this.$input = this.$('input').keydown(function enterHandler (e) {
            if ($(this).attr('class') == 'customer_name') {
                $(this).autocomplete({
                    select: function (event, ui) {
                        var terms = split(this.value);
                        // remove the current input
                        terms.pop();
                        // add the selected item
                        terms.push(ui.item.label);
                        this.value = terms;
                        $(this).attr('data-id', ui.item.value);
                        return false;
                    },
                    source: function (request, response) {
                        // delegate back to autocomplete, but extract the last term
//                        if (reg_patient === true) {
                            var res = $.ui.autocomplete.filter(
                                self.customer_by_name, extractLast(request.term));
                            response(res);
                    }
                });
            }
        });
        /*OLD KEYUP AND ENTER KEY EVENTS, MAY NEED FIX , NEED TO TEST THOROUGHLY*/
        this.$input = this.$('input').keyup(function enterHandler (e) {
            if ($(this).attr('class') != 'customer_name') {
                if(e.keyCode === $.ui.keyCode.ENTER) {
                    self.$input.off('keyup', enterHandler);
                    if (!self.quick_add()){
                        self.$input.on('keyup', enterHandler);
                    }
                } else if (e.keyCode === $.ui.keyCode.ESCAPE && self._buttons) {
                    self.close();
                }
            }
        });
        /*enables multiple selection for services*/
        this.$('#services_1').select2();
        this.$('#staff_1').select2();
        this.$('#customer_dob_month').select2();
        this.$('#customer_dob_day').select2();
        return this._super();
    },
    focus: function() {
        this.$input.focus();
    },

    /**
     * Gathers data from the quick create dialog a launch quick_create(data) method
     */
    quick_add: function() {
        var val = this.$input.val().trim();
        return (val)? this.quick_create({'name': val}) : false;
    },
    /*get_customer_by_name: function (name) {
    var self = this;
        $.each(self.customer_by_name, function(p) {

        });
    },*/
    quick_add_saloon: function() {
        var create_vals = {}, temp, self = this, lines;
        var checked = $('input.customer_type').prop("checked");
        var notes_remarks = $('input.notes_remarks').val();
        var duation_get = new Model('pos.order')
            .call('get_current_session').then(function (have_session) {
                  create_vals['session_id'] = have_session;
//                  if (have_session==false){
//
//                    alert("There is no open session right now. You have to open one session to make payment !!!")
//                    return false;
//                  }
             });
        if (checked == true) {
            if ($('.customer_name').val()) {
                temp = parseInt($('input.customer_name').attr('data-id'));
                if (!temp) {
                    alert("Invalid customer")
                    return false;
                }
                create_vals['partner_id'] = temp ? temp : false;
            }
            else{
                if (! $('.customer_name').val()) {
                    alert("Select customer")
                    return false;
                }
            }
        }
        if (checked == false) {
            if (($('.customer_new_name').val()) &&
                    ($('.customer_new_phone').val())) {
                var customer_new_name = $('.customer_new_name').val();
                var customer_new_phone = $('.customer_new_phone').val();
                var customer_new_dob_month = document.getElementById('customer_dob_month');
                var customer_new_dob_monthValue = customer_new_dob_month.options[customer_new_dob_month.selectedIndex].value;
                var customer_new_dob_day = document.getElementById('customer_dob_day');
                var customer_new_dob_dayValue = customer_new_dob_day.options[customer_new_dob_day.selectedIndex].value;
                create_vals = _.extend({}, create_vals, {
                    'customer_new_name': customer_new_name ? customer_new_name : false,
                    'customer_new_phone': customer_new_phone ? customer_new_phone : false,
                    'customer_new_dob_month': customer_new_dob_monthValue ? customer_new_dob_monthValue : false,
                    'customer_new_dob_day': customer_new_dob_dayValue ? customer_new_dob_dayValue : false,
                });            }
            else{
                if (! $('.customer_new_name').val()) {
                    alert("Enter customer name")
                    return false;
                }
                if (! $('.customer_new_phone').val()) {
                    alert("Enter customer phone")
                    return false;
                }
            }
        }
        if (create_vals) {
            create_vals = _.extend({}, create_vals, {
                lines: [],
                date_order: false,
                date_start: false,
                note: notes_remarks,
            });
            var ser_no = this.operation_id + 1;
            for (var j=1;j<=ser_no;j++) {
                var staff = document.getElementById('staff_' + j);
                if (staff){
                    if(staff.selectedIndex == -1){
                        var services_here = document.getElementById('services_' + j);
                        var servicesValue_here = services_here.options[services_here.selectedIndex].label;
                        var error_msg = "Select a proper staff for service " + ": " + servicesValue_here;
                        alert(error_msg)
                        return false;
                    }
                    var staffValue = staff.options[staff.selectedIndex].value;
                    var duration = document.getElementById('duration_' + j);
                    var durationValue = duration.value;
                    var services = document.getElementById('services_' + j);
                    var servicesValue = services.options[services.selectedIndex].value;
                    var modal_scheduler_hour = document.getElementById('modal_scheduler_hour_' + j);
                    var modal_scheduler_hourValue = modal_scheduler_hour.options[modal_scheduler_hour.selectedIndex].value;
                    var modal_scheduler_minute = document.getElementById('modal_scheduler_minute_' + j);
                    var modal_scheduler_minuteValue = modal_scheduler_minute.options[modal_scheduler_minute.selectedIndex].value;

                    var stop_time, start_time, duration;

                    temp = servicesValue;

                    let dt_arr = self.data_template.procedure_start.split(/[- :]/);
                    start_time = new Date(
                        dt_arr[0], dt_arr[1]-1, dt_arr[2],
                        modal_scheduler_hourValue, modal_scheduler_minuteValue, 0);

                    start_time.addMinutes(0);
                    stop_time = new Date(
                        dt_arr[0], dt_arr[1]-1, dt_arr[2],
                        modal_scheduler_hourValue, modal_scheduler_minuteValue, 0);

                    stop_time = stop_time.addMinutes(durationValue);

                    create_vals['date_stop'] = stop_time.toUTCString();
                    if(create_vals['date_order']==false){
                        create_vals['date_order'] = start_time.toUTCString()
                    }
                    if(create_vals['date_start']==false){
                        create_vals['date_start'] = start_time.toUTCString()
                    }
                    create_vals['lines'].push([0, 0, {
                        'product_id': parseInt(temp),
                        'staff_assigned_id': staffValue ? parseInt(staffValue) : false,
                        'procedure_start': start_time.toUTCString(),
                        'procedure_stop': stop_time.toUTCString(),
                    }]);
                }
            }
        }
        return create_vals ? this.quick_create_appointment(create_vals) : false;
    },

    slow_add: function() {
        var val = this.$input.val().trim();
        this.slow_create(_.isEmpty(val) ? {} : {'name': val});
    },

    /**
     * Handles saving data coming from quick create box
     */
    quick_create: function(data, options) {
        var self = this;
        return this.dataset.create($.extend({}, this.data_template, data), options)
            .then(function(id) {
                self.trigger('added', id);
                self.$input.val("");
            }, function(r, event) {
                event.preventDefault();
                // This will occurs if there are some more fields required
                self.slow_create(data);
            });
    },

    quick_create_appointment: function(data) {
        var self = this;
        return new Model('calender.config').call('add_appointment', [data]).then(function(ids) {
            var parent = self.getParent();
            parent.$calendar.fullCalendar2('refetchEvents');
            self.close();
            self.trigger("closed");
        });
    },

    slow_create: function(_data) {
        //if all day, we could reset time to display 00:00:00
        if (_data['session_id']==false){
                alert("There is no open session right now. You have to open one session to mark booking !!!")
                this.close();
                return false;
              }
        var self = this;
        var def = $.Deferred();
        var defaults = {};
        var created = false;

        _.each($.extend({}, this.data_template, _data), function(val, field_name) {
            defaults['default_' + field_name] = val;
        });

        var pop = new form_common.FormViewDialog(this, {
            res_model: this.dataset.model,
            context: this.dataset.get_context(defaults),
            title: this.get_title(),
            disable_multiple_selection: true,
            // Ensuring we use ``self.dataset`` and DO NOT create a new one.
            create_function: function(data, options) {
                return self.dataset.create(data, options).fail(function (r) {
                   if (!r.data.message) { //else manage by openerp
                        throw new Error(r);
                   }
                });
            },
            read_function: function() {
                return self.dataset.read_ids.apply(self.dataset, arguments).fail(function (r) {
                    if (!r.data.message) { //else manage by openerp
                        throw new Error(r);
                    }
                });
            }
        }).open();
        pop.on('closed', self, function() {
            if (def.state() === "pending") {
                def.resolve();
            }
        });
        pop.on('create_completed', self, function() {
            created = true;
            self.trigger('slowadded');
        });
        def.then(function() {
            if (created) {
                var parent = self.getParent();
                parent.$calendar.fullCalendar2('refetchEvents');
            }
            self.close();
            self.trigger("closed");
        });
        return def;
    },
});

/**
 * Common part to manage any field using calendar view
 */
var Sidebar = Widget.extend({
    template: 'CalendarView.sidebar',

    start: function() {
        this.filter = new SidebarFilter(this, this.getParent());
        return $.when(this._super(), this.filter.appendTo(this.$el));
    }
});
var SidebarFilter = Widget.extend({
    events: {
        'click .o_calendar_contact': 'on_click',
        'click .update_time': 'update_time'
    },
    template: 'CalendarView.sidebar.filters',
    update_time: function (e) {
        var start = $('.duration_start').val();
        var end = $('.duration_end').val();
        var self = this;
        var time_def = new Model('calender.config').call('update_calendar_schedule',
            [[start, end]]);
        return $.when(time_def).then(function (result) {
                self.schedule_start = start ? start : "08:00";
                self.schedule_end = end ? end : "23:00";
                location.reload();
            });
    },

    init: function(parent, view) {
        this._super(parent);
        this.view = view;
    },
    render: function() {
        var self = this;
        var filters = _.filter(this.view.get_all_filters_ordered(), function(filter) {
            return _.contains(self.view.now_filter_ids, filter.value);
        });
        var works = false;
        if (self.view.title && self.view.title == 'Works') {
            works = true;
        }

        this.$('.o_calendar_contacts').html(QWeb.render('CalendarView.sidebar.contacts', {
            filters: filters,
            works: works,
            time_schedule: self.view.time_schedule ? self.view.time_schedule:[],
            start: self.view.schedule_start ? self.view.schedule_start : false,
            end: self.view.schedule_end ? self.view.schedule_end : false
        }));
    },
    on_click: function(e) {
        if (e.target.tagName !== 'INPUT') {
            $(e.currentTarget).find('input').click();
            return;
        }
        this.view.all_filters[e.target.value].is_checked = e.target.checked;
        this.trigger_up('reload_events');
    },
});

return {
    QuickCreate: QuickCreate,
    Sidebar: Sidebar,
    SidebarFilter: SidebarFilter
};

});
