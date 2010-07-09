dojo.require("dijit.Menu");
dojo.require("dojo.dnd.Source");
dojo.require("dijit.Dialog");
dojo.require("dijit.MenuSeparator");

function retrouver_menu(node)
    {
    var reg = dijit.registry._hash;
    for(var i in reg)
        {
        var widget = reg[i];
        for(var j in widget.targetNodeIds)
            {
            var widget_node = widget.targetNodeIds[j];
            if (node == widget_node)
                {
                if (widget.declaredClass == "dijit.menu")
                    {
                    return widget;
                    }
                }
            }
        }
    return null;
    }

function Trafiquable(id_table, service_url)
    {
    var matable = dojo.byId(id_table);
    if (dojo.isIE) { 
        dojo.byId('status').innerText = "<p>IE detected"+dojo.isIE+"</p>";
        return; 
    }
    var focused = dojo.query('*:focus', matable);
    var timeout_ordre_colonnes;
    var ligne_titres = dojo.query("thead > tr", matable)[0];
    var titres = dojo.query(" > *", ligne_titres);
    var service_url = service_url;
    var dndSource = new dojo.dnd.Source(ligne_titres, {horizontal: true, accept: [id_table]});
    var le_trafiquable = this;
    var help_dialog = new dijit.Dialog({
        title : "Aide sur la manipulation des tableaux",
        content : "<p><h5Certains tableaux comme celui-ci peuvent être personnalisés par l'utilisateur.</h5></p><p>Celui-ci peut décider de masquer certaines colonnes et peut choisir également l'ordre dans lequel les colonnes doivent s'afficher.</p><p><ul><li>Pour modifier l'ordre des colonnes, il suffit de déplacer celles-ci par 'glisser-déposer' (cliquer sur le titre d'une colonne, laisser le bouton de la souris enfoncé, déplacer la souris au nouvel emplacement et relacher le bouton).</li><li>En faisant un clic-droit sur le titre d'une colonne, un menu contextuel apparaît permettant de masquer cette colonne, de réafficher toutes les colonnes, de rétablir l'ordre par défaut des colonnes et de trier le tableau.</li></ul></p><button dojoType=\"dijit.form.Button\" type=\"submit\">OK</button>"
        });
    SimpleAjax(service_url,'action=get&id_table=' + id_table,function(ajax_response)
        {
        le_trafiquable.set_ordre_colonnes(ajax_response.ordre_colonnes);
        dojo.style(matable,"display","table");
        });
    dojo.forEach(titres, function(titre, index)
        {
        dndSource.insertNodes(false,[titre]);
        var menu = retrouver_menu(titre);
        if (menu)
            {
            menu.addChild(new dijit.MenuSeparator());
            }
        else
            {
            menu = new dijit.Menu({targetNodeIds: [titre]});
            }
        menu.addChild(new dijit.MenuItem({label:'Masquer cette colonne', iconClass: 'dijitEditorIcon dijitEditorIconCancel', onClick: function() {
            le_trafiquable.masquer_colonne(index);
            }}));
        menu.addChild(new dijit.MenuItem({label:'Réafficher les colonnes masquées', iconClass: 'dijitEditorIcon dijitEditorIconRedo', onClick: function() {
            le_trafiquable.reafficher_colonnes();
            }}));
        menu.addChild(new dijit.MenuItem({label:"Remettre l'ordre par défaut", iconClass: 'dijitEditorIcon dijitEditorIconInsertOrderedList', onClick: function()
            {
            le_trafiquable.remettre_ordre_defaut();
            }}));
        menu.addChild(new dijit.MenuItem({label:"Tri ascendant", onClick: function()
            {
            le_trafiquable.trier(index,true);
            }}));
        menu.addChild(new dijit.MenuItem({label:"Tri descendant", onClick: function()
            {
            le_trafiquable.trier(index,false);
            }}));
        menu.addChild(new dijit.MenuItem({label:"Aide", iconClass:'dijitHelpIcon', onClick: function()
            {
            help_dialog.show();
            }}));
        });
    dojo.forEach(dojo.query("tr", matable), function(le_tr)
        {
        dojo.forEach(dojo.query(" > *", le_tr), function(ce_td, index)
            {
            dojo.addClass(ce_td, "trafiquablecolonne" + index);
            });
        });

    this.handle_dnd = function(source, nodes, copy, target)
        {
        if ((source == dndSource) && (target == dndSource))
            {
            this.appliquer_ordre_colonnes(true);
            }
        }
        
    dojo.subscribe("/dnd/drop", this, this.handle_dnd);
    
    this.trier = function(index_colonne, asc)
        {
        var lignes = dojo.query("tbody > tr", matable);
        var cellules = new Array();
        dojo.forEach(lignes, function (ligne, index)
            {
            var la_cellule = dojo.query(" > *", ligne)[index_colonne];
            cellules.push(new Array(index, la_cellule, la_cellule.innerHTML));
            });
        cellules.sort(function (a,b) { if (asc) { return a[2] > b[2]; } else { return b[2] > a[2]; } });
        var tbody = dojo.query("tbody",matable)[0];
        tbody.innerHTML = "";
        dojo.forEach(cellules, function (info)
            {
            tbody.appendChild(lignes[info[0]]);
            });
        }

    this.remettre_ordre_defaut = function()
        {
        var ordre_colonnes = new Array();
        titres = dojo.query(" > *", ligne_titres);
        ligne_titres.innerHTML = "";
        dojo.forEach(titres, function(entete1, index1)
            {
            dojo.forEach(titres, function(entete2, index2)
                {
                dojo.forEach(entete2.className.split(" "), function (la_classe)
                    {
                    if (la_classe.indexOf("trafiquablecolonne") != -1)
                        {
                        if (parseFloat(la_classe.substr('trafiquablecolonne'.length)) == index1)
                            {
                            ligne_titres.appendChild(entete2);
                            }
                        }
                    });
                });
            });
        this.appliquer_ordre_colonnes(true);
        }

    this.set_ordre_colonnes = function(ordre_colonnes)
        {
        if ((typeof ordre_colonnes == 'undefined') || (ordre_colonnes.length == 0))
            {
            return;
            }
        titres = dojo.query(" > *", ligne_titres);
        var indexes = new Array();
        ligne_titres.innerHTML = "";
        dojo.forEach(ordre_colonnes, function(infos_colonne)
            {
            var user_index = infos_colonne[0];
            var user_actif = infos_colonne[1];
            var child = titres[user_index];
            dojo.style(child, "display", user_actif ? "table-cell" : "none");
            ligne_titres.appendChild(child);
            });
        this.appliquer_ordre_colonnes(false);
        }

    this.appliquer_ordre_colonnes = function(sauvegarder)
        {
        var focused = dojo.query('*:focus', matable);
        var liste_colonnes = new Array();
        var etat_colonnes_masquees = new Array();
        titres = dojo.query(" > *", ligne_titres);
        dojo.forEach(titres, function(le_th)
            {
            var classes = le_th.className.split(" ");
            dojo.forEach(classes, function(la_classe)
                {
                if (la_classe.indexOf("trafiquablecolonne") != -1)
                    {
                    liste_colonnes.push(la_classe);
                    etat_colonnes_masquees.push(dojo.style(le_th,"display"));
                    }
                });
            });
        dojo.forEach(dojo.query(" > thead > tr, > tbody > tr", matable), function(le_tr)
            {
            var les_td = dojo.query(" > *", le_tr);
            if (les_td.length == liste_colonnes.length)
                {
                le_tr.innerHTML = "";
                dojo.forEach(liste_colonnes, function(nom_colonne, index)
                    {
                    dojo.forEach(les_td, function(ce_td)
                        {
                        if (dojo.hasClass(ce_td, nom_colonne))
                            {
                            le_tr.appendChild(ce_td);
                            dojo.style(ce_td,"display",etat_colonnes_masquees[index]);
                            }
                        });
                    });
                }
            });
        if (typeof timeout_ordre_colonnes != "undefined")
            {
            window.clearTimeout(timeout_ordre_colonnes);
            }
        if (sauvegarder)
            {
            var liste_colonnes_pour_enregistrement = new Array();
            dojo.forEach(liste_colonnes, function(nom_colonne, index)
                {
                liste_colonnes_pour_enregistrement.push(new Array(parseFloat(nom_colonne.substr('trafiquablecolonne'.length)), etat_colonnes_masquees[index] == "table-cell"));
                });
            dojo.addClass(ligne_titres,"save-in-progess");
            timeout_ordre_colonnes = window.setTimeout(function() {le_trafiquable.ajaxer_ordre_colonnes(liste_colonnes_pour_enregistrement);},2000);
            }
        if (focused[0])
            {
            focused[0].focus();
            }
        }
    
    this.ajaxer_ordre_colonnes = function(liste_colonnes)
        {
        dojo.removeClass(ligne_titres,"save-in-progess");
        SimpleAjax(service_url, 'action=save&id_table=' + id_table + '&liste_colonnes=' + encodeURIComponent(dojo.toJson(liste_colonnes)), function() {});
        }

    this.masquer_colonne = function(num_colonne)
        {
        dojo.forEach(titres, function(entete)
            {
            if (dojo.hasClass(entete, 'trafiquablecolonne' + num_colonne))
                {
                dojo.style(entete,"display","none");
                }
            });
        this.appliquer_ordre_colonnes(true);
        }

    this.reafficher_colonnes = function()
        {
        dojo.forEach(titres, function(entete)
            {
            dojo.style(entete, "display", "table-cell");
            });
        this.appliquer_ordre_colonnes(true);
        }
    }
