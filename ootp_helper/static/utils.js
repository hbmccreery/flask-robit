const ratingColorMap = function(lev1, lev2, lev3, lev4, value, ascending) {
    if(ascending === true) {
        if (value > lev1) {
            return ('#44bbdd')
        } else if (value > lev2) {
            return ('#117722')
        } else if (value > lev3) {
            return ('#eac117')
        } else if (value > lev4) {
            return ('#dd8033')
        } else {
            return ('#dd0000')
        }
    } else {
        if (value < lev1) {
            return ('#44bbdd')
        } else if (value < lev2) {
            return ('#117722')
        } else if (value < lev3) {
            return ('#eac117')
        } else if (value < lev4) {
            return ('#dd8033')
        } else {
            return ('#dd0000')
        }
    }
};