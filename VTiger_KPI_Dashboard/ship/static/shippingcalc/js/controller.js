import * as model from './model.js';
import View from './viewsjs/appview.js';
import addressView from './viewsjs/addressView.js';
import productView from './viewsjs/productView.js';
import rateView from './viewsjs/rateView.js';
import { ADDRESS, SERVICECODES } from './config.js';

const controlAddressSubmission = async () => {
  /**
   * @function _toggleSections - Toggles view from Address Form to Product Selection Page
   * @function addFormRender - Sets the Address Form results to our state variable
   */
  try {
    addressView._toggleSections(['.address--heading', '.product--heading', '.address--wrapper', '.product--wrapper']);
    addressView.addFormRender(model.setAddressDetails);
  } catch (err) {
    throw err;
  }
};

const controlProductSubmission = async () => {
  /**
   * @function _handleProductSelection - Listens for "change" event on the product dropdown
   * @function _generateMarkup - Grabs the selected product and renders HTML mark up in the DOM
   * @function _renderProductQuantity - Handles our quantity increase/decrease per btn click on selected product.
   */
  try {
    productView._handleProductSelection(productView._generateMarkup, productView._renderProductQuantity);
  } catch (err) {
    throw err;
  }
};

const controlRateSubmission = async () => {
  try {
    rateView._checkForProductSelection();
    rateView._renderProductWeights(model.setProductWeights);
    rateView._renderProductWeights(model.setPackageDimension, model.state.packageWeight);
    await model.setUPSPackageDetails();
    await controlApiCall();
  } catch (err) {
    rateView.renderError(
      'Please ensure products are selected, if they are, adjust your product quantites. Our largest box can hold 60lbs safely. Perhaps split up your order and click "Check Rates" again'
    );
  }
};

const controlApiCall = async () => {
  try {
    rateView._spinningWheel();
    await model.upsApiCall(ADDRESS);
    await model.filterRateResults(model.state.rates, SERVICECODES);
    rateView._hideSections('.intro--wrapper', '.reset--btn');
    rateView._generateMarkUp(
      model.searchKey,
      model.state.negotiatedRates,
      model.state.filteredRates,
      model.state.suggestedRate
    );
    rateView._displayRateSection();
  } catch (err) {
    rateView.renderError('Please refresh the page and double check your Address');
  }
};

const init = function () {
  addressView.addHandlerRender(controlAddressSubmission);
  controlProductSubmission();
  rateView.addHandlerRender(controlRateSubmission);
};

init();
