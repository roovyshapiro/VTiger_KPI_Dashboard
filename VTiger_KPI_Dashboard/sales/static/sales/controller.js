import * as model from "./model.js";
import appView from "./viewsjs/appview.js";
import { address } from "./model.js";

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

const setAddressWeight = function (totalPackageWeight) {
  // Updates UPS Address Object
  address.RateRequest.Shipment.Package.PackageWeight.Weight =
    totalPackageWeight.toString();
  address.RateRequest.Shipment.ShipmentTotalWeight.Weight =
    totalPackageWeight.toString();
};

const checkTotalWeight = function (number) {
  // Logic for checking total package weight to determine box dimensions
  return (
    address.RateRequest.Shipment.Package.PackageWeight.Weight &&
    address.RateRequest.Shipment.ShipmentTotalWeight.Weight <= number
  );
};

const collectPackageDimension = function (len, wid, height) {
  // Using the helper function above, this will set the dimensions
  address.RateRequest.Shipment.Package.Dimensions.Length = `${len}`;
  address.RateRequest.Shipment.Package.Dimensions.Width = `${wid}`;
  address.RateRequest.Shipment.Package.Dimensions.Height = `${height}`;
};

const setPackageDimension = function () {
  // Finalizing dimension functions, alerts user if over 60lbs
  checkTotalWeight(5)
    ? collectPackageDimension(12, 9, 5)
    : checkTotalWeight(10)
    ? collectPackageDimension(14, 11, 10)
    : checkTotalWeight(20)
    ? collectPackageDimension(22, 18, 12)
    : checkTotalWeight(60)
    ? collectPackageDimension(30, 21, 16)
    : window.alert(
        "Please lower the quantity of products to reduce risk of damage while in transit. The weight limit on our largest box is 60lbs"
      );
};

const renderProductData = function () {
  // Manage State for Total Product Selection Weight, need last value as well (preWeight);
  let { packageWeight } = model.state;
  let { preWeight } = model.state;
  appView.product_Selection.addEventListener("change", function (e) {
    // On each product selection "change" event we are grabbing ahold of that element and manipulating the data.
    let selectedProduct = e.target.value;
    let productWeight =
      +e.target.options[e.target.selectedIndex].dataset.weight;

    // Generate HTML Mark Up from App View.js to display the table we see pop up after a product is selected
    appView.generateMarkUp(selectedProduct, productWeight);

    // Grab every quantity input field to calculate total weight
    const quantityValue = document.querySelectorAll(".quantity__value--input");

    // Keep Track of last weight amount before current weight "change" event
    Array.from(quantityValue).map((input) =>
      input.addEventListener("focus", function (e) {
        preWeight = e.target.value;
      })
    );

    // Updated Weight, this will subtract/add to packageWeight
    Array.from(quantityValue).forEach((input) => {
      input.addEventListener("change", function (e) {
        if (selectedProduct === input.name)
          packageWeight += (e.target.value - preWeight) * productWeight;
        // Sets Weight on UPS Object we are building
        setAddressWeight(packageWeight);
        // Sets Dimensions on UPS Object
        setPackageDimension();
      });
    });
  });
};

const addressSubmission = function () {
  // Function is building the UPS Address Object. This data will be used to submit API Call.
  let { Address } = address.RateRequest.Shipment.ShipTo;
  appView.form__input.forEach((input) =>
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

const apiCall = async function () {
  await model.upsRateRequest(address);
  // Add Filter Function here from Model
  setRateStateObject();
};

const submitUPSObject = function () {
  appView.checkRateBtn.addEventListener("click", function (e) {
    e.preventDefault();
    appView.changeDisplay(appView.rates__Section, "flex");
    appView.smoothScrolling(appView.footer);
    apiCall();
  });
};

const setRateStateObject = function() {
    let { negotiatedRate, publishedRate, suggestedRate, ratedShipment } = model.state;
    // Taking filtered API response and building a rate table. This does not effect UI yet
    negotiatedRate._3day = model.filterRateResults("12", ratedShipment, 'discount');
    negotiatedRate._ground = model.filterRateResults("03", ratedShipment, 'discount');
    negotiatedRate._2day = model.filterRateResults("02", ratedShipment, 'discount');
    negotiatedRate._1daypm = model.filterRateResults("01", ratedShipment, 'discount');
    negotiatedRate._1dayam = model.filterRateResults("14", ratedShipment, 'discount');

    publishedRate._3day = model.filterRateResults("12", ratedShipment, 'published');
    publishedRate._ground = model.filterRateResults("03", ratedShipment, 'published');
    publishedRate._2day = model.filterRateResults("02", ratedShipment, 'published');
    publishedRate._1daypm = model.filterRateResults("01", ratedShipment, 'published');
    publishedRate._1dayam = model.filterRateResults("14", ratedShipment, 'published');

    suggestedRate._3day = model.filterRateResults("12", ratedShipment, 'eyeriderate');
    suggestedRate._ground = model.filterRateResults("03", ratedShipment, 'eyeriderate');
    suggestedRate._2day = model.filterRateResults("02", ratedShipment, 'eyeriderate');
    suggestedRate._1daypm = model.filterRateResults("01", ratedShipment, 'eyeriderate');
    suggestedRate._1dayam = model.filterRateResults("14", ratedShipment, 'eyeriderate');

    console.log(negotiatedRate);
    console.log(publishedRate);
    console.log(suggestedRate);
}

const init = function () {
  addressSubmission();
  smoothScrolling();
  // Runs Events in appViews.js
  appView.renderEvent();
  renderProductData();
  submitUPSObject();
};

init();