dojo.addOnLoad(function(){
    dojo.query('#paramadditionnalfield_set-group .module table>thead>tr>th')[0].attributes.removeNamedItem('colspan');
    list = dojo.query('.module table>tbody>tr .data_type');
    for( i in list)
    {
        if(! isNaN(parseInt(i))){
            list[i].innerHTML="<a href='/admin/clariadmin/paramadditionnalfield/"+list[i].parentNode.children[0].children[1].value+"'>"+list[i].innerHTML+"</a>";
        }
    }
    dojo.connect(dojo.byId("#paramadditionnalfield_set-group"),"onmouseover",function(){
            dojo.query('#paramadditionnalfield_set-group .module .add-row>td')[0].innerHTML = "<a id='id='add_id_truc' class='add-another' onclick='return showAddAnotherPopup(this);' href='/admin/clariadmin/paramadditionnalfield/add/?host_type="+dojo.byId('id_paramadditionnalfield_set-__prefix__-host_type').value+"'>Ajouter un objet Définition De Champs Complémentaires supplémentaire</a>";}
        )

});

