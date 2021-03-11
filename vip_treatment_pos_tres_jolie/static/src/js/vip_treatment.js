odoo.define('vip_treatment_pos.vip', function (require) {
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

screens.ActionpadWidget.include({
        renderElement: function() {
        var self = this;
        this._super();
        this.$('.vip_treatment').click(function(){
            self.gui.show_popup('vip_percentage_widget')
        });
    }
});
var _super_order = models.Order.prototype;
var OrderSuper = models.Order;
models.Order = models.Order.extend({
    initialize: function(attributes,options){
        var order = OrderSuper.prototype.initialize.call(this, attributes,options);
        order.vip_percent = 0;
        return order;
    },
    init_from_JSON: function(json) {
        OrderSuper.prototype.init_from_JSON.call(this, json);
        this.vip_percent = json.vip_percent;
    },
    export_as_JSON: function() {
        var json_new = _super_order.export_as_JSON.apply(this,arguments);
        json_new.vip_percent = this.get_vip_percent_order();
        return json_new;
    },
    export_for_printing: function() {
        var receipt = _super_order.export_for_printing.apply(this,arguments);
        receipt.vip_percent = this.get_vip_percent_order();
        return receipt;
    },
    set_vip_percent_order: function(vip_perc){
        var vip_percentage = Math.min(Math.max(parseFloat(vip_perc) || 0, 0),100);
        this.vip_percent = vip_percentage;
        this.trigger('change',this);
    },
    get_vip_percent_order: function(){
        return this.vip_percent;
    },
    get_vip_total: function(){
        var total_fixed_disc = this.get_discount_total_order();
        var total_percent_disc = this.get_discount_percent_order();
        var total_percent_vip = this.get_vip_percent_order();
        var temp_1 = round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        if (total_percent_vip) {
           return temp_1 * total_percent_vip / 100;
        }
        return 0;
    },
    get_total_without_tax: function() {
        var total_fixed_disc = this.get_discount_total_order();
        var total_percent_disc = this.get_discount_percent_order();
        var total_percent_vip = this.get_vip_percent_order();
        var temp_1 = round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        var temp = round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        if (total_fixed_disc) {
            temp =  temp_1 - total_fixed_disc ;
         }
        if (total_percent_disc) {
           temp =  (temp_1 - (temp_1 * total_percent_disc / 100));
        }
        if (total_percent_vip) {
           temp =  (temp + (temp_1 * total_percent_vip / 100));
        }
        return temp;
    },
    get_total_without_vip_tax: function() {
        var total_fixed_disc = this.get_discount_total_order();
        var total_percent_disc = this.get_discount_percent_order();
        var total_percent_vip = this.get_vip_percent_order();
        var temp = round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        if (total_fixed_disc) {
            temp =  temp - total_fixed_disc ;
         }
        if (total_percent_disc) {
           temp =  (temp - (temp * total_percent_disc / 100));
        }
        return temp;
    },
    get_total_discount: function() {
        var sum = OrderSuper.prototype.get_total_discount.call(this);
        sum = 0.0;
        var disc = 0.0;
        for (var i = 0; i < this.orderlines.length; i++) {
            var NewOrder = this.orderlines.models[i];
            disc +=  (NewOrder.quantity * NewOrder.price);
            if (NewOrder.discountStr == 'fixed') {
                sum +=  parseFloat(NewOrder.discount_fixed);
            }
            else {
                sum +=  NewOrder.quantity * NewOrder.price * (parseFloat(NewOrder.discount) / 100);
            }
        }
        if (this.discount_total) {
            sum +=  parseFloat(this.discount_total);
            }
        if (this.discount_percent) {
            disc -= parseFloat(this.get_total_without_vip_tax() + sum);
            sum +=  disc;
        }
        return sum;

    },
});

screens.OrderWidget.include({
    update_summary: function(){
        this._super();
        var order = this.pos.get_order();
        var vip_percent   = (order && order.get_vip_percent_order() > 0) ? order.get_vip_percent_order() : 0;
        if (this.el.querySelector('.summary .total .subentry .value_vip_percent')){
            if (vip_percent > 0) {
                this.el.querySelector('.summary .total .subentry .value_vip_percent').textContent = "VIP Treatment: " + vip_percent + " %";
            }
            else {
                this.el.querySelector('.summary .total .subentry .value_vip_percent').textContent = "";
            }
        }
    },
});

var VipPercentagePopupWidget = PosBaseWidget.extend({
    template: 'VipPercentagePopupWidget',
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
//        if (this.options.cancel) {
//            this.options.cancel.call(this);
//        }
    },
    click_confirm: function(){
        var value = this.$('input,textarea').val();
        if (value >100) {
            alert("Percentage should not be greater than 100")
            return false;
        }
        if (value < 0) {
            alert("Percentage should not be negative")
            return false;
        }
        var order = this.pos.get_order();
        order.set_vip_percent_order(value);
        this.gui.close_popup();
    },

});
gui.define_popup({name:'vip_percentage_widget', widget: VipPercentagePopupWidget});

});


