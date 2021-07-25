// Imports

class AppView {
    packageWeight = 0;
    preVal;
    rateResponse;
  
    // Form Elements
    form__input = document.querySelectorAll(".form__input");
    form__section = document.getElementById("section__form");
    form_Fields = document.querySelectorAll(".form__field");
    product_Form = document.getElementById("product__form");
    product_Selection = document.getElementById("product_dropdown");
    // Table Elements
    table__main = document.querySelector('table');
    box__icon = document.querySelector('.shipping__icon');
    table__heading = document.querySelector('th');
    table__body = document.querySelector('.table__body');
    
    //BTNS
    product_Btn = document.querySelector(".form__submit--btn");
    checkRateBtn = document.querySelector('.address__submit--btn');
    
    // Main Element Sections
    rates__Section = document.getElementById('rates__section');
    footer = document.getElementById("footer__id");
  
    renderEvent() {
      this.highLightBtns();
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
  
    highLightBtns() {
        // Changes the opactiy on the "Product Selection" & "Check Rates" Buttons from "0" to "1" and changes the footer display to "flex"
      this.form__section.addEventListener("input", this.btnStyling.bind(this));
      this.table__main.addEventListener("change", this.highLightRateCheckBtn.bind(this));
    }

    highLightRateCheckBtn() {
        if (!this.table__main.rows.length >= 2) return
        this.checkRateBtn.style.opacity = '1';
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

    changeDisplay(element, displayValue) {
        return element.style.display = displayValue;
    }

    smoothScrolling(destination) {
        return destination.scrollIntoView({behavior: 'smooth'})
    }
  }
  
  export default new AppView();