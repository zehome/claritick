function toggleFadding(element, onBeginFadeInCallback, onEndFadeInCallback, onBeginFadeOutCallback, onEndFadeOutCallback) {
    if (dojo.style(element, "display") == "none") {
        dojo.fadeIn({
            node: element,
            duration: 100,
            onBegin: function() {
                dojo.style(element, "display", "block");
                if (onBeginFadeInCallback)
                    onBeginFadeInCallback();
            },
            onEnd: onEndFadeInCallback
        }).play();
    } else {
        dojo.fadeOut({
            node: element,
            duration: 100,
            onBegin: onBeginFadeOutCallback,
            onEnd: function() {
                dojo.style(element, "display", "none");
                if (onEndFadeOutCallback)
                    onEndFadeOutCallback();
            }
        }).play();
    }
}

dojo.addOnLoad(function() {
    if (MENU_CAN_HIDE) {
        var pixel_width = dojo.style("gauche", "width") + dojo.style("gauche-spin", "width");

        // F2 pour ouvrir/fermer le menu
        dojo.connect(dojo.global, "onkeypress", function(evt) {
            if (evt.charOrCode == dojo.keys.F2)
                toggleFadding("gauche", null, null, null, null);
        });

        // Click sur le bandeau a gauche
        dojo.connect(dojo.byId("gauche-spin"), "onclick", function(evt) {
            toggleFadding("gauche", null, null, null, null);
        });

        // Si click en dehors du menu, on le ferme
        dojo.connect(dojo.global, "onclick", function(evt) {
            if (evt.clientX > pixel_width)
                dojo.fadeOut({
                node: "gauche",
                duration: 200,
                onEnd: function() {
                    dojo.style("gauche", "display", "none");
                }
            }).play();
        });
    }
});
