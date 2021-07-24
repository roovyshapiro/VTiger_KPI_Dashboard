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

const setAddressWeight = function(totalPackageWeight) {
    // Updates UPS Address Object
    address.RateRequest.Shipment.Package.PackageWeight.Weight = totalPackageWeight.toString();
    address.RateRequest.Shipment.ShipmentTotalWeight.Weight = totalPackageWeight.toString();
}

const renderProductData = function() {
    // <select></select> Element from Product Drop down 
    const product_Selection = document.getElementById("product_dropdown");

    // Manage State for Total Product Selection Weight, need last value as well (preWeight); 
    let { packageWeight } = model.state;
    let { preWeight } = model.state;
    product_Selection.addEventListener("change", function(e) {
        // On each product selection "change" event we are grabbing ahold of that element and manipulating the data. 
        let selectedProduct = e.target.value;
        let productWeight = +e.target.options[e.target.selectedIndex].dataset.weight;

        // Generate HTML Mark Up from App View.js to display the table we see pop up after a product is selected
        appView.generateMarkUp(selectedProduct, productWeight);

        // Grab every quantity input field to calculate total weight 
        const quantityValue = document.querySelectorAll('.quantity__value--input');

        // Keep Track of last weight amount before current weight "change" event
        Array.from(quantityValue).map(input => input.addEventListener('focus', function(e) {
            preWeight = e.target.value;
        }))

        // Updated Weight, this will subtract/add to packageWeight 
        Array.from(quantityValue).forEach(input => {
            input.addEventListener('change', function(e) {
                if (selectedProduct === input.name) 
                packageWeight += (e.target.value - preWeight) * productWeight;
                // Sets Weight on UPS Object we are building
                setAddressWeight(packageWeight);
            })
        })
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