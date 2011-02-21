dojo.addOnLoad(function(){dojo.parser.parse()});
dojo.addOnLoad(function(){typeChanged(dijit.byId('id_data_type'))});
// var classes_list = [false,'dj_admin_Text','dj_admin_Bool','dj_admin_Choix','dj_admin_Num','dj_admin_Date','dj_admin_Choix'];
function hide_fieldsets()
{
    dojo.forEach(['dj_admin_Text','dj_admin_Bool','dj_admin_Choix','dj_admin_Num','dj_admin_Date'], function(cur){
                dojo.query('.'+cur)[0].classList.add("dijitHidden");
            })
}
function show_fieldset(val){
    if(val){
        dojo.query('.'+[null,'dj_admin_Text','dj_admin_Bool','dj_admin_Choix','dj_admin_Num','dj_admin_Date','dj_admin_Choix'][val])[0].classList.remove("dijitHidden");
    }
}
function typeChanged(widget){
        hide_fieldsets();
        show_fieldset(widget.value);
    }
