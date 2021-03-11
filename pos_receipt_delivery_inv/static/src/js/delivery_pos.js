odoo.define('pos_receipt_invoice.delivery_detail', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var core = require('web.core');
var formats = require('web.formats');
var utils = require('web.utils');
var PosBaseWidget = require('point_of_sale.BaseWidget');

var QWeb = core.qweb;
var round_di = utils.round_decimals;
var round_pr = utils.round_precision;
var _t = core._t;

screens.ActionpadWidget.include({
        renderElement: function() {
        var self = this;
        this._super();
        this.$('.enter_delivery_details').click(function(){
            self.gui.show_popup('delivery_details_widget')
        });
    }
});
var _super_order = models.Order.prototype;
var OrderSuper = models.Order;
models.Order = models.Order.extend({
    initialize: function(attributes,options){
        var order = OrderSuper.prototype.initialize.call(this, attributes,options);
        order.to_print_bill = false;
        order.delivery_note = '';
        order.delivery_category = '';
        return order;
    },
    init_from_JSON: function(json) {
        OrderSuper.prototype.init_from_JSON.call(this, json);
        this.to_print_bill = json.to_print_bill;
        this.delivery_note = json.delivery_note;
        this.delivery_category = json.delivery_category;
    },
    export_as_JSON: function() {
        var json_new = _super_order.export_as_JSON.apply(this,arguments);
        json_new.delivery_note = this.get_delivery_note_order();
        json_new.delivery_category = this.get_delivery_category_order();
        return json_new;
    },
    export_for_printing: function() {
        var receipt = _super_order.export_for_printing.apply(this,arguments);
        receipt.delivery_note = this.get_delivery_note_order();
        receipt.delivery_category = this.get_delivery_category_order();
        return receipt;
    },
    set_to_print_bill: function(to_print_bill) {
        this.assert_editable();
        this.to_print_bill = to_print_bill;
    },
    is_to_print_bill: function(){
        return this.to_print_bill;
    },
    set_delivery_note_order: function(deliv_note){
        this.delivery_note = deliv_note;
        this.trigger('change',this);
    },
    get_delivery_note_order: function(){
        return this.delivery_note;
    },
    set_delivery_category_order: function(deliv_category){
        this.delivery_category = deliv_category;
        this.trigger('change',this);
    },
    get_delivery_category_order: function(){
        return this.delivery_category;
    },
});

screens.PaymentScreenWidget.include({
    click_print_bill: function(){
        var order = this.pos.get_order();
        order.set_to_print_bill(!order.is_to_print_bill());
        if (order.is_to_print_bill()) {
            this.$('.js_print_bill').addClass('highlight');
        } else {
            this.$('.js_print_bill').removeClass('highlight');
        }
    },
    renderElement: function() {
        var self = this;
        this._super();
        this.$('.js_print_bill').click(function(){
            self.click_print_bill();
        });
    },
    finalize_validation: function() {
        var self = this;
        var order = this.pos.get_order();

        if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {

                this.pos.proxy.open_cashbox();
        }

        order.initialize_validation_date();

        if (order.is_to_invoice()) {
            var invoiced = this.pos.push_and_invoice_order(order);
            this.invoicing = true;

            invoiced.fail(function(error){
                self.invoicing = false;
                if (error.message === 'Missing Customer') {
                    self.gui.show_popup('confirm',{
                        'title': _t('Please select the Customer'),
                        'body': _t('You need to select the customer before you can invoice an order.'),
                        confirm: function(){
                            self.gui.show_screen('clientlist');
                        },
                    });
                } else if (error.code < 0) {        // XmlHttpRequest Errors
                    self.gui.show_popup('error',{
                        'title': _t('The order could not be sent'),
                        'body': _t('Check your internet connection and try again.'),
                    });
                } else if (error.code === 200) {    // OpenERP Server Errors
                    self.gui.show_popup('error-traceback',{
                        'title': error.data.message || _t("Server Error"),
                        'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                    });
                } else {                            // ???
                    self.gui.show_popup('error',{
                        'title': _t("Unknown Error"),
                        'body':  _t("The order could not be sent to the server due to an unknown error"),
                    });
                }
            });

            invoiced.done(function(){
                self.invoicing = false;
                self.gui.show_screen('receipt');
            });
        }
        else {
            if(order.is_to_print_bill()){
                this.pos.push_print_order(order);
            }
            else{
                this.pos.push_order(order);
            }
            this.gui.show_screen('receipt');
        }

    },

});
models.PosModel = models.PosModel.extend({
    push_print_order: function(order, opts) {
            opts = opts || {};
        var self = this;

        if(order){
            var order_id = this.db.add_order(order.export_as_JSON());
        }
        var pushed = new $.Deferred();

        this.flush_mutex.exec(function(){
            var flushed = self._flush_orders(self.db.get_orders(order_id), opts);

            flushed.always(function(ids){
                pushed.resolve();
            });
            flushed.pipe(function(order_server_id){
                // generate the pdf and download it
                self.chrome.do_action('point_of_sale.pos_invoice_report',{additional_context:{
                    active_ids:order_server_id,
                }});
            });

            return flushed;
        });
        return pushed;
    },
});
screens.OrderWidget.include({
    update_summary: function(){
        this._super();
        var order = this.pos.get_order();
        var delivery_note   = (order && order.get_delivery_note_order()) ? order.get_delivery_note_order() : '';
        if (this.el.querySelector('.summary .total .subentry .value_delivery_note')){
            if (delivery_note) {
                this.el.querySelector('.summary .total .subentry .value_delivery_note').textContent = "Delivery note: " + delivery_note ;
            }
            else {
                this.el.querySelector('.summary .total .subentry .value_delivery_note').textContent = "";
            }
        }
        var delivery_category   = (order && order.get_delivery_category_order()) ? order.get_delivery_category_order() : '';
        if (this.el.querySelector('.summary .total .subentry .value_delivery_category')){
            if (delivery_category) {
                this.el.querySelector('.summary .total .subentry .value_delivery_category').textContent = "Category: " + delivery_category ;
            }
            else {
                this.el.querySelector('.summary .total .subentry .value_delivery_category').textContent = "";
            }
        }
    },
});

var DeliveryNotePopupWidget = PosBaseWidget.extend({
    template: 'DeliveryNotePopupWidget',
    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};

    },
    events: {
        'click .button.cancel':  'click_cancel',
        'click .button.confirm': 'click_confirm',
    },
    show: function(options){
        options = options || {};
        this._super(options);
        this.renderElement();
        this.$('input,textarea').focus();
    },
     close: function(){
    },
    click_cancel: function(){
        this.gui.close_popup();
    },
    click_confirm: function(){
        var order = this.pos.get_order();
        var delivery_note = this.$('input,textarea').val();
        order.set_delivery_note_order(delivery_note);
        var delivery_category = this.$('select.delivery_category').val();
        order.set_delivery_category_order(delivery_category);
        this.gui.close_popup();
    },

});
gui.define_popup({name:'delivery_details_widget', widget: DeliveryNotePopupWidget});

});


