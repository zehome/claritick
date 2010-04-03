dojo.require("dijit.Menu");
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
                if (widget.declaredClass == "dijit.Menu")
                    {
                    return widget;
                    }
                }
            }
        }
    return null;
    }

function Exportable(id_table, service_url)
    {
    var table = dojo.byId(id_table);
    var ligne_titres = dojo.query("thead > tr", table)[0];
    var titres = dojo.query(" > *", ligne_titres);
    var service_url = service_url;
    var l_exportable = this;
    var help_dialog = new dijit.Dialog({
        title : "Aide sur la manipulation des tableaux",
        content : "<h5>Certains tableaux comme celui-ci peuvent être exportés dans différents formats.</h5><p>En effectuant un clic-droit sur l'entête du tableau et en choisissant 'Exporter cette table' au format choisi, le contenu du tableau pourra être téléchargé et ouvert dans un tableur.</p></p><button dojoType=\"dijit.form.Button\" type=\"submit\">OK</button>",
        });
    dojo.forEach(titres, function(titre, index)
        {
        dojo.style(titre, "cursor", "pointer");
        menu = retrouver_menu(titre);
        if (menu)
            {
            menu.addChild(new dijit.MenuSeparator());
            }
        else
            {
            menu = new dijit.Menu({targetNodeIds: [titre]});
            }
        menu.addChild(new dijit.MenuItem({label:"Exporter cette table au format CSV", onClick: function()
            {
            l_exportable.exportcsv('exportcsv');
            }}));
        menu.addChild(new dijit.MenuItem({label:"Exporter cette table au format Microsoft Excel", onClick: function()
            {
            l_exportable.exportcsv('exportxls');
            }}));
        menu.addChild(new dijit.MenuItem({label:"Exporter cette table sur un serveur FTP", onClick: function()
            {
            l_exportable.exportdistant('ftp');
            }}));
        //~ TODO : à réactiver quand on aura codé la fonctionnalité
        //~ menu.addChild(new dijit.MenuItem({label:"Envoyer cette table par mail", onClick: function()
            //~ {
            //~ l_exportable.exportdistant('mail');
            //~ }}));
        menu.addChild(new dijit.MenuItem({label:"Aide", iconClass:'dijitHelpIcon', onClick: function()
            {
            help_dialog.show();
            }}));
        });

    this.exportdistant = function(export_action)
        {
        var iframe;
        iframe = dojo.byId('filedownloadiframe');
        if (!iframe)
            {
            iframe = document.createElement('iframe');
            iframe.name = 'filedownloadiframe';
            iframe.id = 'filedownloadiframe';
            dojo.style(iframe, "display", "none");
            dojo.body().appendChild(iframe);
            }
        var le_form = document.createElement('form');
        le_form.method = 'post';
        le_form.action = service_url;
        le_form.target = '_blank';
        dojo.style(le_form, "display", "none");
        var textarea = document.createElement('textarea');
        textarea.name = 'data';
        le_form.appendChild(textarea);
        var action = document.createElement('input');
        action.type = 'text';
        action.name = 'action';
        action.value = export_action;
        le_form.appendChild(action);
        var cle_table = document.createElement('input');
        cle_table.type = 'text';
        cle_table.name = 'cle_table';
        cle_table.value = table.id;
        le_form.appendChild(cle_table);
        table.parentNode.appendChild(le_form);
        var csv = "";
        var lignes = new Array();
        dojo.forEach(dojo.query("thead > tr, tbody > tr", table), function(ligne, index)
            {
            var cette_ligne = new Array();
            dojo.forEach(dojo.query("td, th", ligne), function(cellule, index)
                {
                if (dojo.style(cellule, "display") != "none")
                    {
                    if (dojo.attr(cellule, "value"))
                        {
                        cette_ligne.push(dojo.attr(cellule, "value"));
                        }
                    else if (cellule.innerHTML != "&nbsp;")
                        {
                        cette_ligne.push(cellule.innerHTML);
                        }
                    else
                        {
                        cette_ligne.push("");
                        }
                    }
                });
            lignes.push(cette_ligne.join(";"));
            });
        csv = lignes.join("\n");
        textarea.value = csv;
        le_form.submit();
        le_form.parentNode.removeChild(le_form);
        }

    this.exportcsv = function(export_action)
        {
        var iframe;
        iframe = dojo.byId('filedownloadiframe');
        if (!iframe)
            {
            iframe = document.createElement('iframe');
            iframe.name = 'filedownloadiframe';
            iframe.id = 'filedownloadiframe';
            dojo.style(iframe, "display", "none");
            dojo.body().appendChild(iframe);
            }
        var le_form = document.createElement('form');
        le_form.method = 'post';
        le_form.action = service_url;
        le_form.target = 'filedownloadiframe';
        dojo.style(le_form, "display", "none");
        var textarea = document.createElement('textarea');
        textarea.name = 'data';
        le_form.appendChild(textarea);
        var action = document.createElement('input');
        action.type = 'text';
        action.name = 'action';
        action.value = export_action;
        le_form.appendChild(action);
        var cle_table = document.createElement('input');
        cle_table.type = 'text';
        cle_table.name = 'cle_table';
        cle_table.value = table.id;
        le_form.appendChild(cle_table);
        table.parentNode.appendChild(le_form);
        var csv = "";
        var lignes = new Array();
        dojo.forEach(dojo.query("thead > tr, tbody > tr", table), function(ligne, index)
            {
            var cette_ligne = new Array();
            dojo.forEach(dojo.query("td, th", ligne), function(cellule, index)
                {
                if (dojo.style(cellule, "display") != "none")
                    {
                    if (dojo.attr(cellule, "value"))
                        {
                        cette_ligne.push(dojo.attr(cellule, "value"));
                        }
                    else if (cellule.innerHTML != "&nbsp;")
                        {
                        cette_ligne.push(cellule.innerHTML);
                        }
                    else
                        {
                        cette_ligne.push("");
                        }
                    }
                });
            lignes.push(cette_ligne.join(";"));
            });
        csv = lignes.join("\n");
        textarea.value = csv;
        le_form.submit();
        le_form.parentNode.removeChild(le_form);
        }
    }
