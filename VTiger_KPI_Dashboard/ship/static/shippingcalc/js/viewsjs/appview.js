export default class View {
    _data;
    _mainDiv = document.querySelector('main');
    _bannerDiv = document.querySelector('.banner--div');
    _message;
    _errorMessage;
  
    render(data) {
      if (!data) return;
      this._data = data;
    }
  
    _renderEventHandler(selector, ev, handle) {
      document.querySelector(selector).addEventListener(ev, handle);
    }
  
    renderError(message = this._errorMessage) {
      const markup = `
          <div class="banner--div alert">
              <span class="close--btn center" onclick="this.parentElement.style.display='none'">&times;</span>
              ${message}
          </div>
          `;
      document.querySelector('.banner--div').remove();
      document.querySelector('main').insertAdjacentHTML('beforeend', markup);
    }
  
    renderMessage(message = this._message) {
      const markup = `
          <div class="banner--div sucess">
              <span class="close--btn center" onclick="this.parentElement.style.display='none'">&times;</span>
              ${message}
          </div>
          `;
      document.querySelector('.banner--div').remove();
      document.querySelector('main').insertAdjacentHTML('beforeend', markup);
    }
  
    _toggleSections(selectors) {
      selectors = document.querySelectorAll(selectors);
      this._mainDiv.querySelector('.btn__slide--div').addEventListener('click', function (e) {
        return Array.from(selectors).map((nodeList) => nodeList.classList.toggle('hide--section'));
      });
    }
  
    _hideSections(hideSection, showSection) {
      hideSection = document.querySelectorAll(hideSection);
      showSection = document.querySelectorAll(showSection);
      [...hideSection].map((element) => element.classList.add('hide--section'));
      [...showSection].map((element) => element.classList.remove('hide--section'));
    }

    _unhideSections(showSection) {
      showSection = document.querySelectorAll(showSection);
      [...showSection].map((element) => element.classList.remove('hide--section'));
    }
  
    _spinningWheel() {
      document.querySelector('.spinning--wheel').classList.remove('hide--section');
    }
  }
  