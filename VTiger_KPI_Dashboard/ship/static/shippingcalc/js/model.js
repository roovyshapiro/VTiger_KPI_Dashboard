import { CREDENTIALS } from "./config.js";
import { ADDRESS } from "./config.js";
import { BOXVOLS, CLEARSTATE } from "./helpers/helpers.js";

export const state = {
  /**
   * @description - App state. FilteredRates is the same as Published rate.
   */
  address: {},
  selectedProducts: [],
  packageWeight: 0,
  productVolume: 0,
  dimensions: {},
  rates: {},
  filteredRates: [],
  negotiatedRates: [],
  suggestedRate: [],
};

export const setAddressDetails = function (formData) {
  /**
   * @param {Object} formData - Ship to Address that the user submits
   * @description - Push Form Data API Object to state variable
   */
  state.address = formData;
};

export const setProductWeights = function (weights) {
  /**
   * @param {Array} weights - All the selected product weights
   * @constant {Array} weightsObject - push selected products to state. Return Array of all product total weights
   * @description - Reduce Method is called on weightsObject to calc total weight. Set that integer to state.
   */
  try {
    const weightsObject = weights
      .map((product) => {
        state.selectedProducts.push({
          productName: product.id,
          productWeight: +product.textContent,
          totalWeight: +product.textContent * product.dataset.weight,
        });
        return +product.textContent * product.dataset.weight;
      })
      .reduce((acc, cur) => acc + cur, 0);

    return (state.packageWeight = Math.ceil(weightsObject));
  } catch (err) {
    throw err;
  }
};

export const setPackageDimension = function (dimensions) {
  /**
   * @param {Array} dimensions - Array of all selected products including, weights, product Volume;
   * @param {Number} weight - Using weight as a safety net for 1 off scenarios where vol tries to ship with 9x5x5
   * @param {String} message - Error handling for the user to see. Displays a banner on the front end.
   * @constant {Array} productVol - map dimensions Array and calculate total product Volume.
   * @function CLEARSTATE - Clears our state variable on error so the user can re-adjust product quantites
   * @description - Calculate total product Volume. Pull Box Volumes and run checks to set box dimensions.
   */
  try {
    const productVol = dimensions
      .map((prod) => {
        return (
          +prod.dataset.length *
          +prod.dataset.width *
          +prod.dataset.height *
          +prod.textContent
        );
      })
      .reduce((acc, cur) => acc + cur, 0);

    state.productVolume = productVol;

    if (state.packageWeight <= 1)
      return (state.dimensions = { length: "9", width: "5", height: "5" });
    if (productVol < BOXVOLS.box2)
      return (state.dimensions = { length: "12", width: "9", height: "5" });
    if (productVol < BOXVOLS.box3)
      return (state.dimensions = { length: "14", width: "10", height: "10" });
    if (productVol < BOXVOLS.box4)
      return (state.dimensions = { length: "22", width: "18", height: "12" });
    if (productVol < BOXVOLS.box5)
      return (state.dimensions = { length: "30", width: "15", height: "15" });
    if (productVol < BOXVOLS.box6)
      return (state.dimensions = { length: "32", width: "18", height: "15" });
    if (productVol > BOXVOLS.box6)
      throw new Error(
        'Our largest box can handle 60lbs total, please lower your product count and click "check rates" again. Split your order into multiple shipments'
      );
  } catch (err) {
    CLEARSTATE(state);
    throw err;
  }
};

export const setUPSPackageDetails = async function () {
  /**
   * @description - Updates the ADDRESS object that we are going to be using for the API call
   */
  try {
    ADDRESS.RateRequest.Shipment.ShipTo.Address = state.address;
    ADDRESS.RateRequest.Shipment.Package.PackageWeight.Weight =
      state.packageWeight.toString();
    // ADDRESS.RateRequest.Shipment.ShipmentTotalWeight.Weight =
    //   state.packageWeight.toString();
    ADDRESS.RateRequest.Shipment.Package.Dimensions.Length =
      state.dimensions.length;
    ADDRESS.RateRequest.Shipment.Package.Dimensions.Width =
      state.dimensions.width;
    ADDRESS.RateRequest.Shipment.Package.Dimensions.Height =
      state.dimensions.height;
  } catch (err) {
    throw err;
  }
};

// let csrfcookie = function () {
//   let cookieValue = null,
//     name = "csrftoken";
//   if (document.cookie && document.cookie !== "") {
//     let cookies = document.cookie.split(";");
//     for (let i = 0; i < cookies.length; i++) {
//       let cookie = cookies[i].trim();
//       if (cookie.substring(0, name.length + 1) == name + "=") {
//         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//         break;
//       }
//     }
//   }
//   return cookieValue;
// };

// export const upsApiCall = async function (payload) {
//   /**
//    * @param {Object} - ADDRESS - The entire UPS Object we build throughout the app. Includes, weight, dims, shipTo, ShipFrom ect.
//    * @param {String} - UPS_URL - This is the URL we are making the "POST" http request to
//    * @constant CREDENTIALS - Our UPS Credentials which are saved in the config.js file
//    */

//   try {
//     const query = new URLSearchParams({
//       additionalinfo: "",
//     }).toString();

//     const token = await getToken();
//     const version = "v2403";
//     const requestoption = "Shop";
//     const resp = await fetch(
//       `https://wwwcie.ups.com/api/rating/${version}/${requestoption}?${query}`,
//       {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           // transId: "1",
//           transactionSrc: "testing",
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify(payload),
//       }
//     );

//     const data = await resp.json();
//     state.rates = data.RateResponse.RatedShipment;
//   } catch (err) {
//     CLEARSTATE(state);
//     throw err;
//   }
// };

export async function upsApiCall(payload) {
  try {
    const response = await fetch("https://fota-dev.eyeride.io/proxy", {
      method: "GET",
      headers: {
        Authorization: "Basic" + btoa("gmail:eyeride"),
      },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    state.rates = data.RateResponse.RatedShipment;
  } catch (err) {
    CLEARSTATE(state);
    console.log(err);
    throw err;
  }
}
/**
 *
 * @returns {Promise<string> | null } returns an access token to access the rest of the api, it only has a 14-15 seconds shelf life.
 */
// export async function getToken() {
//   try {
//     const resp = await fetch(`https://wwwcie.ups.com/security/v1/oauth/token`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/x-www-form-urlencoded",
//         "x-merchant-id": CREDENTIALS.ShipperNumber,
//         Authorization:
//           "Basic " +
//           btoa(`${CREDENTIALS.client_id}:${CREDENTIALS.client_secret}`),
//       },
//       body: new URLSearchParams({
//         grant_type: "client_credentials",
//       }).toString(),
//     });
//     const data = await resp.json();
//     return data?.access_token;
//   } catch (err) {
//     throw err;
//     return null;
//   }
// }

export function filterRateResults(obj, serviceType) {
  /**
   * @param {Object} - obj - This is the returned rates object from the UPS API call that we are filtering through
   * @param {Object} - serviceType - Object of all the service codes and what those codes equate to. example ("03" = "Ground")
   * @returns - A new Array into our state variable for Published, Negotiated and Suggested Rates.
   * @description - Manages our state variable for rates, this is important for our Rate Page HTML Mark up since we will be using the state values.
   */

  for (const rate of [...obj]) {
    state.filteredRates.push({
      Service: serviceType[rate.Service.Code],
      Price: +rate.TotalCharges.MonetaryValue,
    });
    state.negotiatedRates.push({
      Service: serviceType[rate.Service.Code],
      Price: +rate?.NegotiatedRateCharges?.TotalCharge?.MonetaryValue,
    });
    state.suggestedRate.push({
      Service: serviceType[rate.Service.Code],
      Price: Math.ceil(+rate.TotalCharges.MonetaryValue * 1.3),
    });
  }
  console.log(state);
}

export const searchKey = function (nameKey, rateArray) {
  /**
   * @param {String} nameKey - Shipping Service Type we are searching for
   * @param {Array} rateArray - This is the Array of Shipping Rate Objects that we are searching.
   * @description - Searches our State Rate Objects to find the corresponding service/price for markup function on the Front End. This is what supplies the front end (View) with the rate.
   */
  for (let i = 0; i < rateArray.length; i++) {
    if (rateArray[i].Service === nameKey) return rateArray[i].Price;
  }
};
