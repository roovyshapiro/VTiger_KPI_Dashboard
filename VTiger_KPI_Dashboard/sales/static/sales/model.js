import { UPS_URL } from "./config.js";
import { CREDENTIALS } from "./config.js";
import { ADDRESS } from "./config.js";

export const state = {
    ratedShipment: {},
};

export let address = ADDRESS;

export const upsRateRequest = async function(addressObject) {
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
        })
        if (!response.ok) throw new Error('Please confirm shipping address and try again');

        const result = await response.json();
        state.ratedShipment = result.RateResponse.RatedShipment;
        return result;
    }catch(err) {
        alert(err);
    }
}