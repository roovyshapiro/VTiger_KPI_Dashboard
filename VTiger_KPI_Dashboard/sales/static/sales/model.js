import { UPS_URL } from "./config.js";
import { CREDENTIALS } from "./config.js";
import { ADDRESS } from "./config.js";

export const state = {
  ratedShipment: {},
  packageWeight: 0,
  preWeight: 0,
  publishedRate: {},
  negotiatedRate: {},
  suggestedRate: {},
};

export let address = ADDRESS;

export const upsRateRequest = async function (addressObject) {
  try {
    const response = await fetch(UPS_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        AccessLicenseNumber: `${CREDENTIALS.accessLicenseNumber}`,
        Username: `${CREDENTIALS.upsUserName}`,
        Password: `${CREDENTIALS.upsPassword}`,
      },
      body: JSON.stringify(addressObject),
    });
    if (!response.ok)
      throw new Error("Please confirm shipping address and try again");

    const result = await response.json();
    return (state.ratedShipment = result.RateResponse.RatedShipment);
  } catch (err) {
    alert(err);
  }
};

export const filterRateResults = function (serviceCode, arr, method) {
  const filtered = Array.from(arr).filter(
    (rate) => rate.Service.Code === serviceCode
  );
  const rate = +filtered[0].RatedPackage.TotalCharges.MonetaryValue.toString();

  // Present all 3 options of rates, Negotitated, Published, Suggested
  if (method === "discount")
    return filtered[0].NegotiatedRateCharges.TotalCharge.MonetaryValue;
  if (method === "eyeriderate") return Math.round(rate * 0.3 + rate);
  return filtered[0].RatedPackage.TotalCharges.MonetaryValue;
};