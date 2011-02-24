var add_row = null;
dojo.addOnLoad(function(){
    dojo.query('#paramadditionnalfield_set-group .module table>thead>tr>th')[0].attributes.removeNamedItem('colspan');
    list = dojo.query('#paramadditionnalfield_set-group .module table>tbody>tr .data_type');
    for( i in list)
    {
        if(! isNaN(parseInt(i))){
            list[i].innerHTML="<a href='javascript:void(0)' onclick='return showPopup(\"/admin/clariadmin/paramadditionnalfield/"+list[i].parentNode.children[0].children[1].value+"\")'>"+list[i].innerHTML+"</a>";
        }
    }
    dojo.connect(dojo.byId("#paramadditionnalfield_set-group"),"onmouseover",function(){
        if (add_row == null){
            add_row = dojo.query('#paramadditionnalfield_set-group .module .add-row>td')[0]
            add_row.style.textAlign="center";
            normal_text = "<span><img src='/adm_media/img/admin/icon_addlink.gif' alt='Add'>Cliquez ici pour ajouter une entrée.</span>";
            over_text = "<span>﻿</span>"
            add_row.innerHTML = normal_text ;
            dojo.connect(add_row, "onclick",function(){
                addParameterField("/admin/clariadmin/paramadditionnalfield/add/?host_type="+dojo.byId('id_paramadditionnalfield_set-__prefix__-host_type').value);});
            dojo.connect(add_row, "onmouseover",function(){
                add_row.innerHTML = over_text;
                add_row.style.background="#E1FFE1 url(/adm_media/img/admin/icon_addlink.gif) center center no-repeat";
            });
            dojo.connect(add_row, "onmouseout",function(){
                add_row.innerHTML = normal_text;
                add_row.style.background="#E1E1E1 url(/adm_media/img/admin/nav-bg.gif) center center repeat-x";
            });
        }
    })


});
function showPopup(url){
        var win = window.open( url , name, 'height=500,width=800,resizable=yes,scrollbars=yes');
        win.focus();
        return false;
}

