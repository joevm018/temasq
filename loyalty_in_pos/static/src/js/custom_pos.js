odoo.define('loyalty_in_pos.loyalty_card', function (require) {
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
        this.$('.loyalty_card').click(function(){
            self.gui.show_popup('LoyaltyCard')
        });
    }
});
var LoyaltyCardPopupWidget = PosBaseWidget.extend({
    template: 'LoyaltyCardPopupWidget',

    init: function(parent, args) {
        this._super(parent, args);
        this.options = {};
    },
    events: {
        'click .card_cancel':  'click_cancel',
        'click .card_confirm': 'click_confirm',
    },
    show: function(options){
        options = options || {};
        this._super(options);
        this.renderElement();
        this.$('input,textarea').val('').focus();
    },
    close: function(){
    },
    click_cancel: function(){
    	this.gui.close_popup();
    },
    click_confirm: function(){
    	var value = this.$('input,textarea').val();
    	if (this.pos.db.get_partner_by_barcode(value)) {
    		var partner = this.pos.db.get_partner_by_barcode(value);
            this.new_client = partner;
            var self = this;
        	var order = this.pos.get_order();
			order.set_client(this.new_client);
        }
        else {
            this.new_client = false;
            var self = this;
        	var order = this.pos.get_order();
			order.set_client(this.new_client);
			alert("No customer with given barcode found !!");
        }
        /*
        var order = this.pos.get_client();
        order.set_vip_percent_order(value);*/
        this.gui.close_popup();
    },

});
gui.define_popup({name:'LoyaltyCard', widget: LoyaltyCardPopupWidget});
});