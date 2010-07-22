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

function childManagement() {
    last_focused = dojo.byId("parent");
    fl = null; /* focus list */

    dojo.addOnLoad(function () {
            fl = dojo.query("div.child");
            fl.style("opacity", "0.5");
            fl.push(dojo.byId("parent"));
            fl.onclick(get_focus);
            if (dojo.doc.location.hash != '') {
                var node = dojo.query(dojo.doc.location.hash);
                if (node.length == 1) {
                    dojo.style(node[0], 'opacity', '1');
                    dojo.style(node[0].id + '_content', 'display', 'inline');
                    dojo.style('parent', 'opacity', '0.5');
                }
            }
            buttons = dojo.query("#save_buttons").query("button");
            });

}

function get_focus (ev) {
    fl.style("opacity", "0.5");
    dojo.style(this, "opacity", "1");
    last_focused = this;
}

function showDeletebox(input) {
    var tid = input.parentNode.getAttribute('ticket_id');
    if (tid) {
        var child = dojo.query('div#child'+tid);
        var title = child.query('input[name$="-title"]')[0];
        var text = child.query('textarea[name$="-text"]')[0];
        if (title.value == '' && text.value == '') {
            dojo.style('delete_child'+tid, 'display', 'inline');
        } else {
            dojo.style('delete_child'+tid, 'display', 'none');
        }
    }
}

function togglePlusMinus(img, content) {
    if (dojo.style(content, "display") == "inline") {
        dojo.style(content, "display", "none");
        img.src = "/media/images/plus.png";
    }
    else {
        dojo.style(content, "display", "inline");
        img.src = "/media/images/minus.png";
    }
}

function toggleMailImage(img) {
    var checkbox = dojo.query('input[name$="-diffusion"]', img.parentNode.parentNode)[0];
    if (checkbox.value == 'True') {
        dojo.attr(img, 'src', '/media/images/oxygen/nodiffusion.png');
        dojo.attr(checkbox, 'value', 'False');
    }
    else {
        dojo.attr(img, 'src', '/media/images/oxygen/diffusion.png');
        dojo.attr(checkbox, 'value', 'True');
    }
}

function toggleComment(checkbox) {
    var did = dojo.byId(checkbox.id+'-tooltip').children;
    if (checkbox.checked) {
        did[0].style.display = 'none';
        did[1].style.display = 'block';
    }
    else {
        did[0].style.display = 'block';
        did[1].style.display = 'none';
    }
}

function loadChild (url, add_ticket_full, state_new, state_closed, state_active) {
    var count = dojo.byId('id_form-TOTAL_FORMS');
    buttons.forEach(function (b) {
                dijit.byId(b.id).attr('disabled', true);
            });
    dojo.xhrGet({url: url+'?count='+count.value,
            load: function (data) {
                var childs;
                dojo.place(data, 'div_childs', 'last');
                last_focused = dojo.query('div.child:last-child')[0]
                fl.style('opacity', '0.5');
                fl.push(last_focused);
                dojo.connect(last_focused, 'onclick', get_focus);
                dojo.parser.parse(last_focused)

                if (add_ticket_full) {
                    dojo.attr('id_form-'+count.value+'-assigned_to', 'value', dojo.byId('id_assigned_to').value);
                    dojo.query('input[name="form-'+count.value+'-assigned_to"]')[0].value = dojo.query('input[name="assigned_to"]')[0].value;
                    dojo.forEach(['category', 'project', 'state'], function (e) {
                            if (e == 'state'  && dojo.byId('id_'+e).selectedIndex == state_closed) {
                                dojo.byId('id_'+e).selectedIndex = state_active;
                                dojo.byId('id_form-'+count.value+'-'+e).selectedIndex = state_new;
                            } else {
                                dojo.byId('id_form-'+count.value+'-'+e).selectedIndex = dojo.byId('id_'+e).selectedIndex;
                            }
                        });
                }

                count.value = parseInt(count.value)+1;
                buttons.forEach(function (b) {
                        dijit.byId(b.id).attr('disabled', false);
                    });

                /* aller vers le futur nouveau fils */
                var node;
                if ((node = dojo.byId('last_child'))) {
                    node.removeAttribute('id');
                }
                dojo.query('div.child:last-child')[0].setAttribute('id', 'last_child');
                dojo.doc.location.hash = '';
                dojo.doc.location.hash = 'last_child';
            }});
}


function setTicketAlarm(url) {
    dojo.xhrPost({
    url: url,
    postData: dojo.byId('id_alarm').value,
    handleAs: 'text',
    load: function (data) {
        dijit.byId('alarm_dialog').hide();
        var newclass = dojo.byId('id_alarm').value ? "claritickTicketAlarm" : "claritickNoTicketAlarm";
        dijit.byId('alarm_button').attr('iconClass', 'dijitEditorIcon '+newclass);
        dijit.byId('alarm_dialog').attr('title', data);
    }});
}

function viewTicketMailTraceDialog(url) {
    if (!ticketmailtrace)
    {
        dojo.xhrGet({
            url: url,
            load: function (data) {
                ticketmailtrace = data;
                dojo.parser.parse(ticketmailtrace);
                showTicketMailTraceDialog();
            }
        });
    } else {
        showTicketMailTraceDialog();
    }
}
function showTicketMailTraceDialog() {
    var dialog = new dijit.Dialog({
        title: 'Ticket Mail Trace',
        content: ticketmailtrace,
        draggable: false
    });
    dialog.show();
}

function deleteTmas(url, button, tma_id) {
    var confirm_string = "Supprimer ";
    confirm_string += (tma_id==0) ? "tous les" : "ce";
    confirm_string += " ticket mail action ?";
    if (confirm(confirm_string)) {
        dojo.xhrGet({
            url: url+'?tma_id='+tma_id
        });
        count = dojo.byId('dijit_tmas_label');
        count.innerHTML = parseInt(count.innerHTML)-1;
        if (count.innerHTML == 0) {
            dijit.byId("dijit_tmas").destroyRecursive();
        } else {
            button.destroyRecursive();
        }
    }
}

