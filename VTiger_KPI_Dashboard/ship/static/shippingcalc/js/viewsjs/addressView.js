import View from './appview.js';

class AddressView extends View {
  _parentElement = document.querySelector('form');
  _wrapperElement = document.querySelector('.address--wrapper');
  _errorMessage = 'Please double check your address and try again';
  _message = 'Address Submitted Successfully, now add products';

  addHandlerRender(ev) {
    window.addEventListener('load', ev);
  }

  addFormRender(handler, error = this._errorMessage, success = this._message) {
    this._parentElement.addEventListener('submit', function (e) {
      e.preventDefault();
      const dataArray = [...new FormData(this)];
      const checkArray = dataArray.flat().filter((val) => val.length > 0);
      if (checkArray.length < 8) return View.prototype.renderError(error);
      const data = Object.fromEntries(dataArray);
      data.CountryCode = 'US';
      View.prototype.renderMessage(success);
      handler(data);
      View.prototype._hideSections('.address--wrapper', '.product--wrapper');
      View.prototype._hideSections('.product--heading', '.address--heading');
      View.prototype._unhideSections('.intro--wrapper')
    });
  }
}

export default new AddressView();
