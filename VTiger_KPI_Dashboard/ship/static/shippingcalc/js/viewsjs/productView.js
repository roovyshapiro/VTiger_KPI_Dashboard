import View from './appview.js';

class ProductView extends View {
  _parentElement = document.querySelector('.output--div');
  _errorMessage = 'Check your product selection and try again';
  _message = 'Select your products in drop down below';

  _handleProductSelection(genMarkUp, handleQuantityCounts) {
    /**
     * @event _handleProductSelection - Listening for change event on the product drop down. Each time a product is clicked, ev is fired.
     * @param {String} genMarkUp - HTML Mark up string to display each selected Product
     * @param handleQuantityCounts - passing productString data towards this._renderProductQuantity function.
     * @function genMarkUp - Adds the selected product HTML mark up on each change event that is fired
     * @let checkSelectedOptions - Array for checking duplicate selections. Those dups will not render HTML markup.
     * @function filteredOptions - checks the "checkSelectedOptions" array for duplicates, returns if length is > 1
     * @constant {String} productString - Saving productName to use as ID selector on .product--quantity class. Keeps our function dynamic.
     */
    let checkSelectedOptions = [];
    document.querySelector('.product--options').addEventListener('change', function (e) {
      checkSelectedOptions.push(e.target.selectedIndex);
      const filteredOptions = checkSelectedOptions.filter((node) => node === e.target.selectedIndex);
      if (filteredOptions.length > 1) return;

      const productString = e.target.value.split(' ').join('');

      genMarkUp(
        e.currentTarget.value,
        e.target.options[e.target.selectedIndex].dataset.weight,
        e.target.options[e.target.selectedIndex].dataset.length,
        e.target.options[e.target.selectedIndex].dataset.width,
        e.target.options[e.target.selectedIndex].dataset.height
      );

      handleQuantityCounts(productString);
    });
  }

  _generateMarkup(product, weight, length, width, height) {
    /**
     * @param {String} product - This is the product ID we dynamically created from _handleProductSelection
     * @param {Number} weight - Integer used to set the data-weight attribute on our <p> Tag in the markup
     * @param {Number} length - Integer used to set the data-length attribute on our <p> Tag in the markup
     * @param {Number} width - Integer used to set the data-width attribute on our <p> Tag in the markup
     * @param {Number} height - Integer used to set the data-height attribute on our <p> Tag in the markup
     * @constant {String} joinedProductString - removing all spaces from product variable so that we can use this to search in our quantity func
     */
    const joinedProductString = product.split(' ').join('');
    const html = `
        <div id="${joinedProductString}" class="product__output--div">
            <div class="output--icon">
                    <i class="fas fa-bus-alt white"></i>
            </div>
            <div class="output--product white">
                    <p class="product--title white center product">${product}</p>
            </div>
            <div class="output--quantity">
                    <p id="${product}" data-weight="${weight}" data-length="${length}" data-width="${width}"  data-height="${height}" class="product--quantity white">1</p>
                    <a href="#" class="addition"><i class="fas fa-plus white"></i></a>
                    <a href="#" class="subtraction"><i class="fas fa-minus white"></i></a>
            </div>
            </div>
            `;
    return document.querySelector('.output--div').insertAdjacentHTML('beforeend', html);
  }

  _renderProductQuantity(pid) {
    /**
     * @param {String} pid (Product ID) - using this to grab ahold of the current selected "add" "subtract" buttons.
     * @description - keep each btn seperate from the other btns that have the same class names, we use currentTarget and the PID to do this.
     */
    const outPutQuantityDiv = document.getElementById(pid).lastElementChild;
    outPutQuantityDiv.querySelectorAll('.fas').forEach((btn) => {
      btn.addEventListener('click', function (e) {
        const productQuantity = e.currentTarget.closest('div').parentElement.lastElementChild.firstElementChild;
        let currentQuantity =
          +e.currentTarget.closest('div').parentElement.lastElementChild.firstElementChild.textContent;
        if (e.currentTarget.classList.contains('fa-plus')) {
          productQuantity.textContent = currentQuantity + 1;
        } else if (productQuantity.textContent > 0) {
          productQuantity.textContent = currentQuantity - 1;
        }
      });
    });
  }
}

export default new ProductView();
