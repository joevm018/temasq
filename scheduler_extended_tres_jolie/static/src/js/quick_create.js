odoo.define('scheduler_extended_tres_jolie.QuickCreateExtended', function(require){
    "use strict";

    var QuickCreate = require("calendar_scheduler.widgets").QuickCreate;
    var Model = require('web.DataModel');
    var core = require('web.core');
    var time = require('web.time');

    var Qweb = core.qweb;
    var _t = core._t;

    QuickCreate.include({
        events: _.extend({}, QuickCreate.prototype.events, {
            'click div.combo_session_ctrl .choose_combo': '_onChooseCombo'
        }),
        /*overwriting start method*/
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
                            self.onChangeCustomer(ui.item.value);
                            return false;
                        },
                        source: function (request, response) {
                            // delegate back to autocomplete, but extract the last term
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

        /*events*/
        delete_order: function (e) {
            let combo_id = $(e.currentTarget).closest("div.one");

            combo_id = combo_id.length > 0 ? combo_id.data('combo_id') : "";
            if (combo_id) {
                this.combo[combo_id].selected = false;
                this.combo[combo_id].staff_id = null;
            }
            this._super(e);
        },
        _onChooseCombo: function (ev) {
            var self = this;
            let new_combo = {};
            _.each(this.combo, function (c) {
                if (c.selected != true) {
                    c.staff_id = self.data_template.staff_assigned_id;
                    new_combo[c.id] = c;
                }
            });
            var $combo_modal = $(Qweb.render("scheduler_extended_tres_jolie.comboModal", {
                combo: new_combo,
                staffs: this.staffs
            }));
            $combo_modal.find("select").select2();
            _.each($combo_modal.find("tr.session_line"), function (tr) {
                $(tr).find("select.staff_id").val(self.combo[$(tr).data("id")].staff_id, null);
                $(tr).find("select.staff_id").trigger("change");
            });

            $combo_modal.modal();
            $combo_modal.show();

            $combo_modal.find("input,select").on("change", function (ev) {
                var $el = $(ev.currentTarget);
                self.updateComboLine($el)
            });
            $combo_modal.find("button.apply").on("click", function (ev) {
                self.updateServiceLines();
            });
        },
        updateServiceLines: function () {
            /*add or remove service lines based on combo selection*/
            var self = this;
            var line_ids = [];
            _.each(this.$("div.one"), function (line) {
                if ($(line).data('combo_id'))
                    line_ids.push($(line).data('combo_id'));
            });
            _.each(this.combo, function (c) {
                if (c.selected == true && !_.contains(line_ids, c.id)) {
                    /*need to add new line*/
                    self.addNewSession(c);
                }
            });
        },
        updateComboLine: function ($el) {
            var self = this, id = $el.closest("tr").data("id");
            switch ($el.attr("name")) {
                case 'selected': {
                    self.combo[id].selected = $el.is(":checked");
                    break;
                };
                case 'staff_id': {
                    let ids = [];
                    _.each($el.val(), function (i) {
                        ids.push(parseInt(i));
                    })
                    self.combo[id][$el.attr("name")] = ids;
                    break;
                };
                default: self.combo[id][$el.attr("name")] = $el.val();
            };
        },
        onChangeCustomer: function (id) {
            let search_domain = this.getComboDomain(id);
            let search_fields = this.getComboFields();
            var self = this;
            new Model('combo.session').call('search_read_session',
                    [search_domain, search_fields]).then(function (combo) {
                self.updateComboInfo(combo);
            });
        },
        updateComboInfo: function (combo) {
            var self = this;
            let $combo = this.$("div.combo_session_ctrl");
            $combo.addClass("o_hidden");
            if (!combo || combo.length == 0)
                return
            this.combo = {};
            let c_data = {};
            _.each(combo, function (c) {
                c_data[c.id] = _.extend({}, c, {
                    selected: false,
                    staff_id: []
                });
            });
            this.combo = c_data;
            $combo.removeClass("o_hidden");
        },
        getComboDomain: function (id) {
            return [['customer_id', '=', id], ['state', '=', 'draft']];
        },
        getComboFields: function () {
            return ["order_id", "combo_id", "product_id", "total_paid", "total_balance"];
        },

        /*updated version for adding service lines*/
        addNewSession: function (item) {
            this.time_schedule = this.find_time_schedule(0, 24);
            this.scheduler_hour = this.find_scheduler_hour_schedule(0, 24);
            this.scheduler_minute = this.find_scheduler_hour_schedule(0, 60);

            this.operation_id +=1;

            var prev_operation_id = this.operation_id;
            var hours = "", Minutes = "";
            var modal_scheduler_hour_prev = document.getElementById('modal_scheduler_hour_' + prev_operation_id);
            var modal_scheduler_minute_prev = document.getElementById('modal_scheduler_minute_' + prev_operation_id);
            let $prev_service = document.getElementById('services_' + prev_operation_id);
            let prev_service = _.filter(this.services, function (s) {
                return s.id == $prev_service.value;
            });
            let prev_duration = prev_service.length > 0 ? prev_service[0].duration : 30;
            let current_service = _.filter(this.services, function (s) {
                return s.id == item.product_id[0];
            });
            let current_duration = current_service.length > 0 ? current_service[0].duration : 30;
            if(modal_scheduler_minute_prev && modal_scheduler_hour_prev){
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prev.options[modal_scheduler_hour_prev.selectedIndex].value;
                var modal_scheduler_minute_prevValue = modal_scheduler_minute_prev.options[modal_scheduler_minute_prev.selectedIndex].value;
                var p_start_date = this.data_template.procedure_start;
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(":")
                var modal_scheduler_hour_prevValue = modal_scheduler_hour_prevValue.concat(modal_scheduler_minute_prevValue)
                var time_d = modal_scheduler_hour_prevValue.concat(":00")
                var p_start_time = p_start_date.split(" ")[0].concat(" ")
                p_start_time = p_start_time.concat(time_d)
                var start_time = new Date(p_start_time);
                start_time.addMinutes(prev_duration);
                hours = start_time.getHours()
                if (hours < 10) {
                    hours = "0" + hours;
                }
                Minutes = start_time.getMinutes()
                if (Minutes < 10) {
                    Minutes = "0" + Minutes;
                }
                hours = hours.toString();
                var hours_Minutes = hours.concat(":")
                hours_Minutes = hours_Minutes.concat(Minutes)
            }
            var staff_prev = document.getElementById('staff_' + prev_operation_id);

            var sl_no = this.operation_id + 1;
            var table_str = Qweb.render("service_line_box", {
                item: item,
                sl_no: sl_no,
                scheduler_hour: this.scheduler_hour,
                scheduler_minute: this.scheduler_minute,
                hours: hours,
                minutes: Minutes,
                config_staff_type: this.config_staff_type,
                staffs: this.staffs,
                service_no_1: this.services ? this.services[0] : "",
                staff_prev: staff_prev,
                services: this.services,
                current_duration: current_duration,
            });

            $('#progres_table').append(table_str);
            this.change_services()
            this.$('#services_'+ sl_no).val(item.product_id[0]);
            this.$('#services_'+ sl_no).select2();
            item.staff_id ? this.$('#staff_'+ sl_no).val(item.staff_id) : null;
            this.$('#staff_'+ sl_no).select2();
        },

        /*overwriting this function also*/
        quick_add_saloon: function() {
            var create_vals = {}, temp, self = this, lines;
            var checked = $('input.customer_type').prop("checked");
            var notes_remarks = $('input.notes_remarks').val();
            var duation_get = new Model('pos.order')
                .call('get_current_session').then(function (have_session) {
                    create_vals['session_id'] = have_session;
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
                    });
                }
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
                    if (staff) {
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
                        if(create_vals['date_order'] == false){
                            create_vals['date_order'] = start_time.toUTCString()
                        }
                        if(create_vals['date_start'] == false){
                            create_vals['date_start'] = start_time.toUTCString()
                        }
                        var $tr = $(staff).closest("div.one");
                        let c_session = $tr.length > 0 ? $tr.data('combo_id') : null;
                        let c_vals = {
                            'product_id': parseInt(temp),
                            'staff_assigned_id': staffValue ? parseInt(staffValue) : false,
                            'procedure_start': start_time.toUTCString(),
                            'procedure_stop': stop_time.toUTCString(),
                            'combo_session_id': c_session
                        };
                        if (c_session)
                            c_vals['price_unit'] = 0;
                        create_vals['lines'].push([0, 0, c_vals]);
                    }
                }
            }
            return create_vals ? this.quick_create_appointment(create_vals) : false;
        },

        /*overwriting*/
        change_services: function () {
            var op_id_here = this.operation_id+1;
            var services = document.getElementById('services_' + parseInt(op_id_here));
            if(services.options[services.selectedIndex]){
                var servicesValue = services.options[services.selectedIndex].value;
                var duration = document.getElementById('duration_' + parseInt(op_id_here));

                var service = document.getElementById('services_' + parseInt(op_id_here));
                var staff_here = document.getElementById('staff_' + parseInt(op_id_here));
                var serviceValue = service.options[service.selectedIndex].value;
                let current_service = _.filter(this.services, function (s) {
                    return s.id == serviceValue;
                });
                duration.value = current_service.length > 0 ? current_service[0].duration : 30;
                if(this.config_staff_type == 'service_based_staff'){
                    if (service){
                        var service_staff_str = ''
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
    });
});
