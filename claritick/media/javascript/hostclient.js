function delete_hostclient(host_id, clientid) {
    // on recupere la ligne a supprimer
    line=dojo.byId('del_'+host_id);
    // parent de la ligne dans la table
    tbody=dojo.byId('hostclient_tbody');
    // suppression de l'enregistrement et de la ligne
    dojo.xhrPost({
        headers: {
            'X-CSRFToken': dojo.cookie("csrftoken")
        },
        url: "/ticket/ajax_delete_host_client/",
        postData: "host_id=" + host_id
                + "&client_id="
                + clientid,
        handleAs: 'text',
        load: function (data) {
            tbody.removeChild(line);
        },
        error: function (error) {
            alert('en error occured...' + error);
        }
    });
}

function addNewClienthost(clientid) {
    // control si le Nom est non vide
    var name=dijit.byId("machine_name");
    var host_select=dijit.byId("host_id");
    if (name.isValid() === false) {
        name.focus();
        return;
    };
    // control si le select est non vide
    if (host_select.isValid() === false) {
        host_select.focus();
        return;
    };
    var host_id=dijit.byId("host_id").get("value").split(',')[0];
    // Ajout d un host pour un client
    dojo.xhrPost({
        headers: {
            'X-CSRFToken': dojo.cookie("csrftoken")
        },
        url: "/ticket/ajax_add_host_client/",
        postData: "host_id=" + host_id
                + "&client_id="
                + clientid
                + "&name="
                + name.get("value"),
        handleAs: 'json',
        load: function (data, ioArgs) {
            // if return is true, the user atempt to create two same hostclient
            // this protect integrity error to database
            if (data.error != 'true') {
                // construction d'une nouvelle ligne
                var table=dojo.byId("dataTable");
                var rowCount=table.rows.length;
                var row=table.insertRow(rowCount);
                row.id="del_" + host_id;
                // construction cellule 1
                var cell1=row.insertCell(0);
                cell1.style.width="260px";
                cell1.innerHTML=dojo.byId('machine_name').value;
                // construction cellule 2
                var cell2=row.insertCell(1);
                cell2.style.width="500px";
                cell2.innerHTML=dijit.byId("host_id").value.split(',')[1];
                // construction du boutton supprimer
                del_button=dojo.create('button');
                del_button.textContent='supprimer';
                row.appendChild(del_button);
                dojo.connect(del_button, "onclick", function () {
                    delete_hostclient(host_id, clientid);
                });
                // raz du champ nom
                name.textbox.value="";
                host_select.textbox.value="";
            }
        }
    });
}

