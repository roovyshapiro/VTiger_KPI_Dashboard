export const BOXVOLS = {
    box1: 9 * 5 * 5,
    box2: 12 * 9 * 5,
    box3: 14 * 10 * 10,
    box4: 22 * 18 * 12,
    box5: 30 * 15 * 15,
    box6: 32 * 18 * 15,
  };
  
  export const CLEARSTATE = function (state) {
    state.selectedProducts = [];
    state.packageWeight = 0;
    state.productVolume = 0;
    state.dimensions = {}
  };
  