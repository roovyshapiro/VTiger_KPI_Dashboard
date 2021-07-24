// Imports 

class AppView {
    packageWeight = 0;
    preVal;
    rateResponse;

    // HTML Headers
    form__section = document.getElementById('section__form');
    form_Fields = document.querySelectorAll('.form__field');
    product_Btn = document.querySelector('.form__submit--btn');
    product_Form = document.getElementById('product__form');
    footer = document.getElementById('footer__id');

    renderEvent(){
        this.highLightProductBtnEvent(this.form_Fields);
    }

    btnStyling() {
        const lengths = Array.from(this.form_Fields).every(input => input.value.length);
        if (!lengths) return;
        this.product_Btn.style.opacity = '1';
        this.product_Form.style.display = 'flex';
        this.footer.hidden = false;
    }

    highLightProductBtnEvent() {
        // Changes the Opactiy on the "Product Selection" button to 1 and updates the product selection section to a display of Flex once all input fields have a value greater then 0. 
        this.form__section.addEventListener("input", this.btnStyling.bind(this))
    }

    generateMarkup(){
        // Add Product Table As user selects products 
    }
}

export default new AppView();