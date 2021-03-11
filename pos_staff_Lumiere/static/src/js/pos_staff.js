odoo.define('pizza_pos.pizza', function (require) {
"use strict";


var models = require('point_of_sale.models');
var db = require('point_of_sale.DB');
var screens = require('point_of_sale.screens');
var PopupWidget=require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var models = require('point_of_sale.models');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var _t = core._t;
var formats = require('web.formats');
var utils = require('web.utils');
var round_di = utils.round_decimals;
var round_pr = utils.round_precision;

var DomCache = core.Class.extend({
    init: function(options){
        options = options || {};
        this.max_size = options.max_size || 2000;

        this.cache = {};
        this.access_time = {};
        this.size = 0;
    },
    cache_node: function(key,node){
        var cached = this.cache[key];
        this.cache[key] = node;
        this.access_time[key] = new Date().getTime();
        if(!cached){
            this.size++;
            while(this.size >= this.max_size){
                var oldest_key = null;
                var oldest_time = new Date().getTime();
                for(key in this.cache){
                    var time = this.access_time[key];
                    if(time <= oldest_time){
                        oldest_time = time;
                        oldest_key  = key;
                    }
                }
                if(oldest_key){
                    delete this.cache[oldest_key];
                    delete this.access_time[oldest_key];
                }
                this.size--;
            }
        }
        return node;
    },
    clear_node: function(key) {
        var cached = this.cache[key];
        if (cached) {
            delete this.cache[key];
            delete this.access_time[key];
            this.size --;
        }
    },
    get_node: function(key){
        console.log(key, "key......get.........................this.cache",this.cache)
        console.log(key, "key......get.........................this.cache",this.cache[11])
        var cached = this.cache[key];
        console.log(cached, "cashed......1.......>>>>>>>")
        if(cached){
            this.access_time[key] = new Date().getTime();
        }
//        console.log(cached, "cashed......2.......>>>>>>>")
        return cached;
    },
});

db.include({
     init: function(parent, args) {
        this._super(parent, args);
        this.options = {};

        this.staff_search_string = "";
        this.staff_by_id = {};


    },

    search_staff: function(query){
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(' ','.+');
            var re = RegExp("([0-9]+):.*?"+query,"gi");
        }catch(e){
            return [];
        }
        var results = [];
        for(var i = 0; i < this.limit; i++){
            var r = re.exec(this.staff_search_string);
            if(r){
                var id = Number(r[1]);
                results.push(this.get_staff_by_id(id));
            }else{
                break;
            }
        }
        return results;
    },
    _staff_search_string: function(staff){
        var str =  staff.name;
//        if(staff.barcode){
//            str += '|' + staff.barcode;
//        }
        str = '' + staff.id + ':' + str.replace(':','') + '\n';
        return str;
    },

    add_staffs: function(staffs){
        var updated_count = 0;
        var new_write_date = '';
        var staff;
        for(var i = 0, len = staffs.length; i < len; i++){
            staff = staffs[i];
            this.staff_by_id[staff.id] = staff;
            updated_count += 1;
        }
        if (updated_count) {
            this.staff_search_string = "";
            for (var id in this.staff_by_id) {
                staff = this.staff_by_id[id];
//                partner.address = (partner.name || '');
                this.staff_search_string += this._staff_search_string(staff);
            }
        }
        return updated_count;
    },
    get_staff_by_id: function(id){
        return this.staff_by_id[id];
    },

});


models.load_models({
    model: 'hr.employee',
    fields: ['id','name'],
    loaded: function(self, delivery_mode){
        self.db.add_staffs(delivery_mode);
        self.delivery_mode_db = []
        self.current_delivery_mode = {}
        self.delivery_mode_by_name = {}
        self.delivery_mode_by_id = {}
     for ( var i =0 ;  i <delivery_mode.length; i++){
                                    delivery_mode[i]['start'] = ""
                                    delivery_mode[i]['stop'] = ""
                                    delivery_mode[i]['no'] = i
                                   self.delivery_mode_db.push(delivery_mode[i])
                                   self.delivery_mode_by_name[delivery_mode[i].name] = delivery_mode[i]
                                   self.delivery_mode_by_id[delivery_mode[i].id] = delivery_mode[i]
                                }
    },
});

models.load_models({
    model:  'res.company',
    fields: [ 'currency_id', 'wifi_pswd', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id', 'tax_calculation_rounding_method'],
//    ids:    function(self){ return [self.user.company_id[0]]; },
    loaded: function(self,companies){ self.company = companies[0]; },
});


var OrderSuper = models.Order;
models.Order = models.Order.extend({
    initialize: function(attributes,options){
        var order = OrderSuper.prototype.initialize.call(this, attributes,options);
        return order;
    },
    init_from_JSON: function(json) {
        OrderSuper.prototype.init_from_JSON.call(this, json);
    },
    export_as_JSON: function() {
        var json_new = OrderSuper.prototype.export_as_JSON.call(this);
        return json_new;
    },
    export_for_printing: function(){
        var orderlines = [];
        var self = this;

        this.orderlines.each(function(orderline){
            orderlines.push(orderline.export_for_printing());
        });

        var paymentlines = [];
        this.paymentlines.each(function(paymentline){
            paymentlines.push(paymentline.export_for_printing());
        });
        var client  = this.get('client');
        var cashier = this.pos.cashier || this.pos.user;
        var company = this.pos.company;
        var shop    = this.pos.shop;
        var date    = new Date();

        function is_xml(subreceipt){
            return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
        }

        function render_xml(subreceipt){
            if (!is_xml(subreceipt)) {
                return subreceipt;
            } else {
                subreceipt = subreceipt.split('\n').slice(1).join('\n');
                var qweb = new QWeb2.Engine();
                    qweb.debug = core.debug;
                    qweb.default_dict = _.clone(QWeb.default_dict);
                    qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');

                return qweb.render('subreceipt',{'pos':self.pos,'widget':self.pos.chrome,'order':self, 'receipt': receipt}) ;
            }
        }

        var receipt = {
            orderlines: orderlines,
            paymentlines: paymentlines,
            subtotal: this.get_subtotal(),
            total_with_tax: this.get_total_with_tax(),
            total_without_tax: this.get_total_without_tax(),
            total_tax: this.get_total_tax(),
            total_paid: this.get_total_paid(),
            total_discount: this.get_total_discount(),
            tax_details: this.get_tax_details(),
            change: this.get_change(),
            name : this.get_name(),
            client: client ? client.name : null ,
            invoice_id: null,   //TODO
            cashier: cashier ? cashier.name : null,
            precision: {
                price: 2,
                money: 2,
                quantity: 3,
            },
            date: {
                year: date.getFullYear(),
                month: date.getMonth(),
                date: date.getDate(),       // day of the month
                day: date.getDay(),         // day of the week
                hour: date.getHours(),
                minute: date.getMinutes() ,
                isostring: date.toISOString(),
                localestring: date.toLocaleString(),
            },
            company:{
                email: company.email,
                wifi_pswd: company.wifi_pswd,
                website: company.website,
                company_registry: company.company_registry,
                contact_address: company.partner_id[1],
                vat: company.vat,
                name: company.name,
                phone: company.phone,
                logo:  this.pos.company_logo_base64,
            },
            shop:{
                name: shop.name,
            },
            currency: this.pos.currency,
        };

        if (is_xml(this.pos.config.receipt_header)){
            receipt.header = '';
            receipt.header_xml = render_xml(this.pos.config.receipt_header);
        } else {
            receipt.header = this.pos.config.receipt_header || '';
        }

        if (is_xml(this.pos.config.receipt_footer)){
            receipt.footer = '';
            receipt.footer_xml = render_xml(this.pos.config.receipt_footer);
        } else {
            receipt.footer = this.pos.config.receipt_footer || '';
        }

        return receipt;
    },
});


var ToppingButton = screens.ActionButtonWidget.extend({
    'template': 'ToppingButton',
    button_click: function(){
        self = this
        self.click_assign_staff()
    },


    click_assign_staff: function(){
          var list= []
          var options = {};
          for (var i = 0; i < self.pos.delivery_mode_db.length; i++) {
                var objDeliveryMode = self.pos.delivery_mode_db[i];
                list.push({
                    'label': objDeliveryMode.name,
                    'id': objDeliveryMode.id,
                    'item':  objDeliveryMode,
                    'image': window.location.origin + '/web/image?model=hr.employee&field=image_small&id='+objDeliveryMode.id
                });

        };
        this.gui.show_popup('delivery_mode_selection',{
            'title': options.title || 'Select Staff Details ',
            list: list,
            confirm: function(user){
        var objOrder = self.pos.get_order()
             var line = this.pos.get_order().get_selected_orderline()
             if (line){
                     line.set_offer_string(user.name, user.start, user.stop)
             }
             },

            cancel:  function(){ def.reject(); },
        })

    },

    });

var DmPopupWidget = PosBaseWidget.extend({
    template: 'DmPopupWidget',
    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};
    },
    events: {
        'click .button.cancel':  'click_cancel',
        'click .btn-default':  'click_close',
        'click .img-responsive': 'click_confirm',
        'click .thumb-inner': 'click_item',
        'click .save-offer': 'click_save',
        'click .btn-primary-add-topping': 'click_topping',
    },

    // show the popup !
    show: function(options){
        if(this.$el){
            this.$el.removeClass('oe_hidden');
        }

        if (typeof options === 'string') {
            this.options = {title: options};
        } else {
            this.options = options || {};
        }

        this.renderElement();


    },

    // called before hide, when a popup is closed.
    // extend this if you want a custom action when the
    // popup is closed.
    close: function(){
        if (this.pos.barcode_reader) {
            this.pos.barcode_reader.restore_callbacks();
        }
    },


    hide: function(){
        if (this.$el) {
            this.$el.addClass('oe_hidden');
        }
    },
    click_close: function(){

    },
    click_topping: function(event){},


    // what happens when we click cancel
    // ( it should close the popup and do nothing )
    click_cancel: function(){
        this.gui.close_popup();
        if (this.options.cancel) {
            this.options.cancel.call(this);
        }
    },

    // what happens when we confirm the action
    click_confirm: function(){
        this.gui.close_popup();
        if (this.options.confirm) {
            this.options.confirm.call(this);
        }
    },

    // Since Widget does not support extending the events declaration
    // we declared them all in the top class.
    click_item: function(){},
    click_numad: function(){},
    click_offer_item: function(){},
    click_save: function(){},
});
gui.define_popup({name:'alert', widget: DmPopupWidget});

var DeliveryModeSelectionPopupWidget = DmPopupWidget.extend({
    template: 'DeliveryModeSelectionPopupWidget',
    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};

        this.staff_cache = new DomCache();
        this.click_staff_handler = function(){
            console.log("click_staff_handler...........>>>")
            var staff = self.pos.db.get_product_by_id(this.dataset.productId);
//            args.click_product_action(staff);
        };


    },
    show: function(options){
        options = options || {};
        var self = this;
        this._super(options);

        this.list    = options.list    || [];
        this.renderElement();

        this.$('.back').click(function(){
            self.gui.close_popup();
        });

        var search_timeout = null;
        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
            this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
        }
        this.$('.searchbox input').on('keydown',function(event){
            clearTimeout(search_timeout);
            console.log("fff", this)
            console.log("value", this.value)
            var query = this.value;
            console.log("qry==44444===", query);

            search_timeout = setTimeout(function(){
            console.log("qry=====", query);
                self.perform_search(query,event.which === 13);
            },70);
        });
        this.$('.searchclear').click(function(){

            self.clear_search();
        });

    },
    clear_search: function(){
//        console.log("clear search")
        var staffs = this.list;
//        this.product_list_widget.set_product_list(staffs);
        var input = this.el.querySelector('.searchbox input');
            input.value = '';
            input.focus();
    },
    perform_search: function(query, buy_result){
        var staffs;
        if(query){
            staffs = this.pos.db.search_staff(query);
            console.log(query, "query",staffs, "staffs....")
            if(buy_result && staffs.length === 1){
                    this.pos.get_order().add_product(staffs[0]);
                    this.clear_search();
            }else{
                //this.render_list(staffs);
                var contents = this.$el[0].querySelector('#staff_list');
                contents.innerHTML = "";
                var staff_div = "";
                for(var i = 0, len = staffs.length; i < len; i++) {
                    var item = staffs[i];
                    staff_div = "<div class='thumb-item'>";
                    staff_div += "<img src="+this.get_staff_image_url(item)+" />"+
                                "<div class='thumb-inner' data-item-index="+i+">"+
                                    item.name +
                                "</div>"+
                                "<input id="+item.id+" placeholder='Job No' />"+
                                "<input class='start' name='start' type='time'/>"+
                                "<input class='stop' name='stop' type='time'/>"+
                                "</div>";
                    contents.innerHTML += staff_div;
                }
                //var popup_section = this.$el[0].querySelector('#popup_section');
                //popup_section.innerHTML = "";
                //this.render_list(staffs);
//                this.product_list_widget.set_product_list(staffs);
            }
        }else{
//            staffs = this.pos.db.get_product_by_category(this.id);
//            staffs = this.list;
            console.log("p...", this.list)
            //var staff_list =
            //var contents = this.$el[0].querySelector('.client-list-contents');
            //contents.innerHTML = "";
//            this.product_list_widget.set_product_list(staffs);
        }
    },
    get_staff_image_url: function(staff){
        return window.location.origin + '/web/image?model=hr.employee&field=image_medium&id='+staff.id;
    },
    render_staff: function(staff){
        var cached = this.staff_cache.get_node(staff.id);
        console.log(cached, "cached.......")
        if(!cached){
            var image_url = this.get_staff_image_url(staff);
//            var olist = []
//            olist.push({
//                    'label': staff.name,
//                    'id': staff.id,
//                    'item':  staff,
//                    'image': window.location.origin + '/web/image?model=hr.employee&field=image_small&id='+staff.id
//                });

            var staff_html = QWeb.render('DeliveryModeSelectionPopupWidget',{
                    widget:  this,
//                    item: staff,
                    list: staff,
//                    item_index: staff,
                    image_url: this.get_staff_image_url(staff),
                });
//            console.log("staff_html..", staff_html)

            var staff_node = document.createElement('div');
            staff_node.innerHTML = staff_html;
            console.log("........staff_node.id ........", staff_node.childNodes[1].childNodes[1].childNodes[3].childNodes[1].children[staff.id])
//            staff_node = staff_node.childNodes[1];
            staff_node = staff_node.childNodes[1].childNodes[1].childNodes[3].childNodes[1].children[staff.id];
            this.staff_cache.cache_node(staff.id, staff_node);
            return staff_node;
        }
        return cached;
    },
    render_list: function(staff){
//        var el_html = QWeb.render("VariantListWidget", {widget: this});
        var el_str  = QWeb.render("DeliveryModeSelectionPopupWidget", {widget: this});
        var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];

        if(this.el && this.el.parentNode){
            this.el.parentNode.replaceChild(el_node,this.el);
        }
            this.el = el_node;
            var list_container = el_node.querySelector('.thumbs-flex-wrapper');
//            var list_container = el_node.querySelector('.thumb-item');
            for(var i = 0, len = staff.length; i < len; i++){
                var staff_node = this.render_staff(staff[i]);
                if (staff_node) {
                    staff_node.addEventListener('click',this.click_staff_handler);
                    list_container.appendChild(staff_node);
                }
            }
    },
    click_item : function(event) {
        this.gui.close_popup();
        if (this.options.confirm) {
            var start= this.$('.modal-lg .popup-selection .thumb-item .start');
            var stop= this.$('.modal-lg .popup-selection .thumb-item .stop');
            var item = this.list[parseInt($(event.target).data('item-index'))];
            item = item ? item.item : item;
            var itemm = false;
            for ( var j =0 ;  j <this.list.length; j++){
            if (this.list[j].id == event.target.nextSibling.id){
                    var itemm = this.list[j];
                    itemm = itemm ? itemm.item : itemm;
                }
            }
            if (itemm) {
            var i = item.no;
                itemm.start = start.prevObject["0"].childNodes[1].childNodes[3].childNodes[1].children[i].children[3].value
                itemm.stop = stop.prevObject["0"].childNodes[1].childNodes[3].childNodes[1].children[i].children[4].value
                this.options.confirm.call(self,itemm);
            }else {
                var i = item.no;
                item.start = start.prevObject["0"].childNodes[1].childNodes[3].childNodes[1].children[i].children[3].value
                item.stop = stop.prevObject["0"].childNodes[1].childNodes[3].childNodes[1].children[i].children[4].value
                this.options.confirm.call(self,item);
            }
        }
    },


});

gui.define_popup({name:'delivery_mode_selection', widget: DeliveryModeSelectionPopupWidget});


var _super_orderline = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    initialize: function(attr, options) {
        _super_orderline.initialize.call(this,attr,options)
        this.offer_string = this.offer_string || "";
        this.procedure_start_val = this.procedure_start_val || "";
        this.procedure_stop_val = this.procedure_stop_val || "";
    },
    show: function(options){
        options = options || {};
        var self = this;
        this._super(options);
    },
    set_offer_string: function(offer_string,start,stop){
        this.offer_string = offer_string + '--' + $('#'+this.pos.delivery_mode_by_name[offer_string].id).val();
        this.current_staff_assigned_id = this.pos.delivery_mode_by_name[offer_string].name
        this.staff_assigned_id = this.pos.delivery_mode_by_name[offer_string].id
        this.order.selected_orderline.procedure_start_val = start
        this.order.selected_orderline.procedure_stop_val = stop
        this.trigger('change',this);
    },
    get_staff_string: function(){
        return this.current_staff_assigned_id;
    },
    get_new_get_unit_price_qty_decimal_2:    function(){
        var rounding = this.pos.currency.rounding;
//        var decimals = this.pos.dp['Product Price'];
        var decimals = 1;
        return formats.format_value(round_di(this.get_unit_price() * this.get_quantity(), decimals), { type: 'float', digits: [69, decimals]});
    },
    get_display_price_decimal_2:    function(){
        var rounding = this.pos.currency.rounding;
//        var decimals = this.pos.dp['Product Price'];
        var decimals = 1;
        return formats.format_value(round_di(this.get_display_price(), decimals), { type: 'float', digits: [69, decimals]});
    },
    get_new_get_unit_price_qty:    function(){
        var rounding = this.pos.currency.rounding;
        return round_pr(this.get_unit_price() * this.get_quantity(), rounding);
    },
    get_offer_string: function(){
        return this.offer_string.split('\n');
    },
    get_start_time: function(){
    if (this.procedure_start_val == "") {
        return "--:--";
        }
    else{
        return this.procedure_start_val;
        }
    },
    get_stop_time: function(){
    if (this.procedure_stop_val == "") {
        return "--:--";
        }
    else{
        return this.procedure_stop_val;
        }
    },
    export_as_JSON: function(){
        var json = _super_orderline.export_as_JSON.call(this);
        json.offer_string = this.offer_string;
        json.staff_assigned_id = this.staff_assigned_id;
        json.procedure_start_val = this.procedure_start_val;
        json.procedure_stop_val = this.procedure_stop_val;
        return json;
    },
    init_from_JSON: function(json){
        _super_orderline.init_from_JSON.apply(this,arguments);
        if (!json.staff_assigned_id){
            this.offer_string = json.offer_string || "";
            this.staff_assigned_id = null;
        }
        else{
            this.offer_string = json.offer_string
            this.staff_assigned_id = json.staff_assigned_id
        }
        if (!json.procedure_start_val){
            this.procedure_start_val = null;
        }
        else{
            this.procedure_start_val = json.procedure_start_val
        }
        if (!json.procedure_stop_val){
            this.procedure_stop_val = null;
        }
        else{
            this.procedure_stop_val = json.procedure_stop_val
        }
    },

});


screens.define_action_button({
    'name': 'submit-topping',
    'widget': ToppingButton,
});

});