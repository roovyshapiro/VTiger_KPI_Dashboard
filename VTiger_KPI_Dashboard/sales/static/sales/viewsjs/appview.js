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

    highLightProductBtnEvent(nodeList) {
        this.form__section.addEventListener('input', function(e) {
            const lengths = Array.from(nodeList).every(input => input.value.length);
            e.preventDefault();
            if (!lengths) return;
            // Maybe build event listener in controller and update styles here. 
            // this.product_Btn.style.opacity = '1';
            // this.product_Form.style.display = 'flex';
            // this.footer.hidden = false;
        })
    }
}

export default new AppView();