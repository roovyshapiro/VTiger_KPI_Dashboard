import * as model from './model.js';
import appView from './viewsjs/appview.js';
import { address } from './model.js';

const smoothScrolling = function () {
    const submits = document.querySelectorAll('input[type="submit"]');
    const newArray = Array.from(submits);
  
    newArray.map((submit) => {
      submit.addEventListener("click", function (e) {
        e.preventDefault();
        document.getElementById("footer__id").scrollIntoView({
          behavior: "smooth",
        });
      });
    });
  };


  const addressSubmission = async function () {
    // Function is building the UPS Address Object. This data will be used to submit API Call. 
    let { Address } = address.RateRequest.Shipment.ShipTo;
    const form__input = document.querySelectorAll(".form__input");
    form__input.forEach((input) =>
      input.addEventListener("change", (e) => {
        e.preventDefault();
        input.placeholder === "Street Address"
          ? (Address.AddressLine = input.value.toUpperCase())
          : input.placeholder === "City"
          ? (Address.City = input.value.toUpperCase())
          : input.placeholder === "State ID"
          ? (Address.StateProvinceCode = input.value.toUpperCase())
          : input.placeholder === "Zip Code"
          ? (Address.PostalCode = input.value)
          : null;
          console.log(Address);
      })
    );
  };

const init = function() {
    addressSubmission();
    smoothScrolling();
    // Runs Events in appViews.js
    appView.renderEvent();
}

init();