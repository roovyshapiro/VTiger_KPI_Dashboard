"use strict";

class AppView {
  packageWeight = 0;
  preVal;
  rateResponse;

  // Form Elements
  form__input = document.querySelectorAll(".form__input");
  form_Fields = document.querySelectorAll(".form__field");
  product_Selection = document.getElementById("product_dropdown");
  // Table Elements
  table__main = document.querySelector("table");
  box__icon = document.querySelector(".shipping__icon");
  table__heading = document.querySelector("th");
  table__body = document.querySelector(".table__body");
  
  //BTNS
  product_Btn = document.querySelector(".form__submit--btn");
  checkRateBtn = document.querySelector(".address__submit--btn");
  
  // Main Element Sections
  product_Form = document.getElementById("product__form");
  form__section = document.getElementById("section__form");
  rates__Section = document.getElementById("rates__section");
  renderEvent() {
    this.highLightBtns();
    this.smoothScrolling(this.product_Btn, this.product_Form);
  }

  btnStyling() {
    const lengths = Array.from(this.form_Fields).every(
      (input) => input.value.length
    );
    if (!lengths) return;
    this.product_Btn.style.opacity = "1";
    this.product_Form.style.display = "flex";
  }

  highLightBtns() {
    // Changes the opactiy on the "Product Selection" & "Check Rates" Buttons from "0" to "1"
    this.form__section.addEventListener("input", this.btnStyling.bind(this));
    this.table__main.addEventListener(
      "change",
      this.highLightRateCheckBtn.bind(this)
    );
  }

  highLightRateCheckBtn() {
    if (!this.table__main.rows.length >= 2) return;
    this.checkRateBtn.style.opacity = "1";
  }

  generateMarkUp(product, productWeight) {
    const html = `<tr class="product-row">
        <td data-name="${product}" class="table__data table__product">${product}</td>
        <td class="table__data table__quantity"><input name="${product}" class="quantity__value--input" type="number" placeholder="Quantity" value="0"></td>
        <td class="table__data">${productWeight} lbs</td>
        <td class="table__data"><a href="#" class="minus__aTag"><i class="far fa-minus-square minus__icon fa-2x"></i></a></td>
      </tr>`;

    if (!product.length) return;
    this.table__main.classList.add("table__main");
    this.box__icon.classList.add("box-icon");
    this.table__heading.hidden = false;
    this.table__body.insertAdjacentHTML("beforeend", html);
  }

  generateRateMarkUp(nRate, pub, eyerideRate) {
    const html = `<tr>
        <td class="table__data--rates trans__time">Ground 3-5 Days</td>
        <td class="table__data--rates negot__rates">$${nRate["_ground"]}</td>
        <td class="table__data--rates pub__rates">$${pub["_ground"]}</td>
        <td class="table__data--rates eyeride__rates">$${eyerideRate["_ground"]}</td>
        </tr>
        <tr>
        <td class="table__data--rates trans__time">3 Business Days</td>
        <td class="table__data--rates negot__rates">$${nRate["_3day"]}</td>
        <td class="table__data--rates pub__rates">$${pub["_3day"]}</td>
        <td class="table__data--rates eyeride__rates">$${eyerideRate["_3day"]}</td>
        </tr>
        <tr>
        <td class="table__data--rates trans__time">2 Business Days</td>
        <td class="table__data--rates negot__rates">$${nRate["_2day"]}</td>
        <td class="table__data--rates pub__rates">$${pub["_2day"]}</td>
        <td class="table__data--rates eyeride__rates">$${eyerideRate["_2day"]}</td>
        </tr>
        <tr>
        <td class="table__data--rates trans__time">1 Business Day</td>
        <td class="table__data--rates negot__rates">$${nRate["_1daypm"]}</td>
        <td class="table__data--rates pub__rates">$${pub["_1daypm"]}</td>
        <td class="table__data--rates eyeride__rates">$${eyerideRate["_1daypm"]}</td>
        </tr>
        <tr>
        <td class="table__data--rates trans__time">1 Business Day *AM</td>
        <td class="table__data--rates negot__rates">$${pub["_1dayam"]}</td>
        <td class="table__data--rates pub__rates">$${pub["_1dayam"]}</td>
        <td class="table__data--rates eyeride__rates">$${eyerideRate["_1dayam"]}</td>
        </tr>`;
    return document
      .getElementById("rates__table__body")
      .insertAdjacentHTML("beforeend", html);
  }

  changeDisplay(element, displayValue) {
    return (element.style.display = displayValue);
  }

  smoothScrolling(btn, destination) {
      return btn.addEventListener('click', function(e) {
          e.preventDefault();
          destination.scrollIntoView({ behavior: "smooth" });
      })
  }
}

export default new AppView();
