import View from './appview.js';

class RateView extends View {
  _parentElement = document.querySelector('.rates--wrapper');
  _errorMessage = 'Select a product!';
  _message = '';

  addHandlerRender(handler) {
    /**
     * @description - Our init function to execute the RateSubmission Controller
     */
    document.querySelector('.rates--button').addEventListener('click', handler);
  }

  _checkForProductSelection() {
    /**
     * @description - Display Error message if user does not select a product
     */
    if ([...document.querySelectorAll('.product__output--div')].length <= 0) throw this.renderError(this._errorMessage);
    return;
  }

  _renderProductWeights(handler) {
    /**
     * @param {Function} handler - setProductWeights function in the Model handles our total weight/volume
     * @constant selectedProducts - Array of all the users selected products that we pass to our handler
     */
    const selectedProducts = [
      ...document.querySelectorAll('.product__output--div > .output--quantity > .product--quantity'),
    ];
    return handler(selectedProducts);
  }

  _displayRateSection() {
    document.querySelector('.rates--wrapper').classList.remove('hide--section');
  }

  _generateMarkUp(handler, negotiated, published, suggested) {
    const ratesDiv = this._parentElement.closest('div').firstElementChild;

    const twoDayAM = `
        <div class="light--color">$${handler('TwoDayAM', negotiated)}</div>
        <div class="light--color">$${handler('TwoDayAM', suggested)}</div>
        <div class="light--color">$${handler('TwoDayAM', published)}</div>
        `;
    const twoDayAMNone = `
        <div class="light--color">Not Available</div>
        <div class="light--color">Not Available</div>
        <div class="light--color">Not Available</div>
        `;

    const html = `
        <div class="rates--description">
            <div>Service</div>
            <div>Negotiated</div>
            <div>Suggested</div>
            <div>Published</div>
        </div>
        <div class="rates--result ground">
            <div class="white">Ground</div>
            <div class="light--color">$${handler('Ground', negotiated)}</div>
            <div class="light--color">$${handler('Ground', suggested)}</div>
            <div class="light--color">$${handler('Ground', published)}</div>
        </div>
        <div class="rates--result threeday">
            <div class="white">3 Day</div>
            <div class="light--color">$${handler('ThreeDay', negotiated)}</div>
            <div class="light--color">$${handler('ThreeDay', suggested)}</div>
            <div class="light--color">$${handler('ThreeDay', published)}</div>
        </div>
        <div class="rates--result twoday">
            <div class="white">2 Day</div>
            <div class="light--color">$${handler('TwoDay', negotiated)}</div>
            <div class="light--color">$${handler('TwoDay', suggested)}</div>
            <div class="light--color">$${handler('TwoDay', published)}</div>
        </div>
        <div class="rates--result twodayAM">
            <div class="white">2 Day AM</div>
            ${handler('TwoDayAM', negotiated) ? twoDayAM : twoDayAMNone}
        </div>
        <div class="rates--result onedaysaver">
            <div class="white">1 Day Saver</div>
            <div class="light--color">$${handler('OneDaySaver', negotiated)}</div>
            <div class="light--color">$${handler('OneDaySaver', suggested)}</div>
            <div class="light--color">$${handler('OneDaySaver', published)}</div>
        </div>
        <div class="rates--result overnight">
            <div class="white">1 Day PM</div>
            <div class="light--color">$${handler('OneDayPM', negotiated)}</div>
            <div class="light--color">$${handler('OneDayPM', suggested)}</div>
            <div class="light--color">$${handler('OneDayPM', published)}</div>
        </div>
        <div class="rates--result overnightam">
            <div class="white">1 Day AM</div>
            <div class="light--color">$${handler('OneDayAM', negotiated)}</div>
            <div class="light--color">$${handler('OneDayAM', suggested)}</div>
            <div class="light--color">$${handler('OneDayAM', published)}</div>
        </div>
        `;
    return ratesDiv.insertAdjacentHTML('beforeend', html);
  }
}

export default new RateView();
