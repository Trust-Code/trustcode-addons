odoo.define('website_sale_currency_convert.UsdPriceValue', function (require) {
    "use strict";

var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
var sAnimations = require('website.content.snippets.animation');


sAnimations.registry.WebsiteSale.include({
    /**
     * Adds the stock checking to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination: function (ev, $parent, combination){

        $parent
            .find('.span-dolar-price')
            .first()
            .text('$ ' + this._priceToStr(combination.usd_list_price));

        this._super.apply(this, arguments);
    }
});

return ProductConfiguratorMixin;

});