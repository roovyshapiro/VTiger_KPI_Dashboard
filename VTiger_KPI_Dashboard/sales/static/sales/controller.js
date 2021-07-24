import * as model from './model.js';
import appView from './viewsjs/appview.js';
import { address } from './model.js';

const smoothScrolling = function () {
    const submits = document.querySelectorAll('input[type="submit"]');
    const newArray = Array.from(submits);
  
    newArray.map((submit) => {
      submit.addEventListener("click", function (e) {
          e.preventDefault();
          console.log(address);
        document.getElementById("footer__id").scrollIntoView({
          behavior: "smooth",
        });
      });
    });
  };

const renderProductData = function() {
    const product_Selection = document.getElementById("product_dropdown");
    // Manage State for Total Product Selection Weight, need last value as well (preWeight); 
    let { packageWeight } = model.state;
    let { preWeight } = model.state;
    product_Selection.addEventListener("change", function(e) {
        let selectedProduct = e.target.value;
        let productWeight = +e.target.options[e.target.selectedIndex].dataset.weight;

        // Generate HTML Mark Up from App View.js 
        appView.generateMarkUp(selectedProduct, productWeight);

        // Grab Each Quantity Input Field to manage State of Weight 
        const quantityValue = document.querySelectorAll('.quantity__value--input');

        // Keep Track of last weight amount before current weight 'change'
        Array.from(quantityValue).map(input => input.addEventListener('focus', function(e) {
            preWeight = e.target.value;
        }))

        // Updated Weight, this will subtract/add to packageWeight 
        Array.from(quantityValue).forEach(input => {
            input.addEventListener('change', function(e) {
                if (selectedProduct === input.name) 
                return packageWeight += (e.target.value - preWeight) * productWeight;
            })
        })
        console.log(packageWeight);
    })
}

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
      })
    );
  };

const init = function() {
    addressSubmission();
    smoothScrolling();
    // Runs Events in appViews.js
    appView.renderEvent();
    renderProductData();
}

init();