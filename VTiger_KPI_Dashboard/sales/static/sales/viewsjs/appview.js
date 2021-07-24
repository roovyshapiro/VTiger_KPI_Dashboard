// Imports

class AppView {
    packageWeight = 0;
    preVal;
    rateResponse;
  
    // HTML Headers
    form__section = document.getElementById("section__form");
    form_Fields = document.querySelectorAll(".form__field");
    product_Btn = document.querySelector(".form__submit--btn");
    product_Form = document.getElementById("product__form");
    product_Selection = document.getElementById("product_dropdown");
    // Table Elements
    table__main = document.querySelector('table');
    box__icon = document.querySelector('.shipping__icon');
    table__heading = document.querySelector('th');
    table__body = document.querySelector('.table__body');
    // Main Elements
    footer = document.getElementById("footer__id");
  
    renderEvent() {
      this.highLightProductBtnEvent(this.form_Fields);
    }
  
    btnStyling() {
      const lengths = Array.from(this.form_Fields).every(
        (input) => input.value.length
      );
      if (!lengths) return;
      this.product_Btn.style.opacity = "1";
      this.product_Form.style.display = "flex";
      this.footer.hidden = false;
    }
  
    highLightProductBtnEvent() {
      // Changes the Opactiy on the "Product Selection" button to 1 and updates the product selection section to a display of Flex once all input fields have a value greater then 0.
      this.form__section.addEventListener("input", this.btnStyling.bind(this));
    }

    generateMarkUp(product, productWeight) {
        const html = `<tr class="product-row">
        <td data-name="${product}" class="table__data table__product">${product}</td>
        <td class="table__data table__quantity"><input name="${product}" class="quantity__value--input" type="number" placeholder="Quantity" value="0"></td>
        <td class="table__data">${productWeight} lbs</td>
        <td class="table__data"><a href="#" class="minus__aTag"><i class="far fa-minus-square minus__icon fa-2x"></i></a></td>
      </tr>`;

      if (!product.length) return;
        this.table__main.classList.add('table__main');
        this.box__icon.classList.add('box-icon');
        this.table__heading.hidden = false;
        this.table__body.insertAdjacentHTML('beforeend', html);
    }
  }
  
  export default new AppView();