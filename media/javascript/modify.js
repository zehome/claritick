/*
 * Change la classe du node 'id' de 'before_class' à 'after_class'
 * lorsque que l'on est en dessus de 'yoffset' pixels du début de page.
 */
function changeClassOnScroll(yoffset, id, before_class, after_class)
{
    dojo.addOnLoad(function () {
            /* 
             * pour éviter de toujours exécuter
             * dojo.query(id) si pageYOffset <= yoffset
             * on met un booléen et il le fait qu'une seule
             * fois
             */
            var was_fixed = false;
            dojo.connect(dojo.global, 'scroll', function () {
                if (dojo.global.pageYOffset > yoffset) {
                    dojo.query(id).attr('class', after_class);
                    was_fixed = true;
                }
                else if (was_fixed) {
                    dojo.query(id).attr('class', before_class);
                    was_fixed = false;
                }
            });
    });
}

/*
 * Crée un menu dijit à 2 dimensions avec des données reçue en ajax formatée json
 * url -> url à requêter
 * query_string -> paramètre la requête
 * container -> le menu apparaitra dans ce container id
 * json_key -> la clé des données dans le json reçu
 * id_input0 -> l'id de l'input numéro 1
 * id_input1 -> l'id de l'input numéro 2
 *
 * Le json doit être comme ceci :
 * { json_key : [["value0", "value1", "chaine du menu"], [...] ...] }
 */
var foo;
function ajaxMenu2D(url, query_string, container, id_menu, json_key, id_input0, id_input1) {
    var menu;
    SimpleAjax(url, query_string, function (res) {
            if (!res)
                return;
            if ((menu = dojo.byId(id_menu)))
                menu.destroyRecursive();
            else {
                var data;
                menu = new dijit.Menu ({id: id_menu });
                dojo.forEach(res[json_key], function (data) {
                    var menuItem = new dijit.MenuItem({
                        label: data[2],
                        onClick: function () {
                            dojo.byId(id_input0).value = data[0];
                            dojo.byId(id_input1).value = data[1];
                            menu.destroyRecursive();
                    }});
                    menu.addChild(menuItem);
                });
                dojo.byId(container).appendChild(menu.domNode);
                menu.focus();
            }
    });
}

