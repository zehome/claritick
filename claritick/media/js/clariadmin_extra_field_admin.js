dojo.addOnLoad(function(){dojo.parser.parse()});
dojo.addOnLoad(function(){typeChanged(dijit.byId('id_data_type'))});
function hide_fieldsets()
{
    dojo.forEach(['dj_admin_Text','dj_admin_Bool','dj_admin_Choix','dj_admin_Num','dj_admin_Date'], function(cur){
                dojo.query('.'+cur)[0].classList.add("dijitHidden");
            })
}
function show_fieldset(val){
    if(val){
        dojo.query('.'+['dj_admin_Text','dj_admin_Bool','dj_admin_Choix','dj_admin_Num','dj_admin_Date','dj_admin_Choix'][val-1])[0].classList.remove("dijitHidden");
    }
}
function typeChanged(widget){
    hide_fieldsets();
    show_fieldset(widget.value);
}
