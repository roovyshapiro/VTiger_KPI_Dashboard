import * as model from './model.js';
import appView from './viewsjs/appview.js';
import { address } from './model.js';


const addressSubmission = async function() {
    let { Address } = address.RateRequest.Shipment.ShipTo;
    const form__input = document.querySelectorAll('.form__input');
    form__input.forEach(input => input.addEventListener('change', e => {
        e.preventDefault();
        if (input.placeholder === 'Street Address') Address.AddressLine = input.value.toUpperCase();
        if (input.placeholder === 'City') Address.City = input.value.toUpperCase();
        if (input.placeholder === 'State ID') Address.StateProvinceCode = input.value.toUpperCase();
        if (input.placeholder === 'Zip Code') Address.PostalCode = input.value;
    }))
}

// Init Function 
const init = function() {
    addressSubmission();
    appView.renderEvent();
}

init();