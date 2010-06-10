/*
    Sauvegarde de l'etat de la barre de status
*/
var SaveStatusDivStatestatus_div;
var SaveStatusDivStateMybgColor;
var SaveStatusDivStateMyColor;
var SaveStatusDivStateMyText;
var ConcurrentAjaxRequests = 0;

function SaveStatusDivState()
    {
    SaveStatusDivStatestatus_div = dojo.byId('status');
    if (SaveStatusDivStatestatus_div) {
        SaveStatusDivStateMybgColor  = SaveStatusDivStatestatus_div.style.backgroundColor;
        SaveStatusDivStateMyColor    = SaveStatusDivStatestatus_div.style.color;
        SaveStatusDivStateMyText     = SaveStatusDivStatestatus_div.innerHTML;
    }
    }

dojo.addOnLoad(SaveStatusDivState)
//---------------------------------------------------------------------

/*
    exemple de comment on peut redéfinir une fonction javascript
    par exemple, si on veut transformer tous les "alert" en dialogues Dojo...

var defaultalertfunction = alert;
alert = function(arg)
    {
    defaultalertfunction('mon alerte');
    defaultalertfunction(arg);
    defaultalertfunction('fin mon alerte');
    }

*/

/*
    Wrapper Ajax generique
    TODO : voir a utiliser ca pour MCA2 aussi (comment ?)
*/
function SimpleAjax(ajax_service, ajax_request, callback, error_callback)
    {
    var xhr = new window.XMLHttpRequest();
    xhr.onreadystatechange = function()
        {
        if (xhr.readyState == 4)
            {
            var response_obj = false;
            if ((xhr.responseText) && (xhr.responseText != ""))
                {
                try
                    {
                    response_obj = eval('(' + xhr.responseText + ')');
                    }
                catch(err)
                    {
                    console.error("catched " + err + " -> " + xhr.responseText);
                    SaveStatusDivStatestatus_div.style.backgroundColor = "red";
                    SaveStatusDivStatestatus_div.style.color = "white";
                    SaveStatusDivStatestatus_div.innerHTML = "Exception (voir console)";
                    if (error_callback)
                        {
                        error_callback(xhr);
                        }
                    var w = window.open();
                    w.document.write(xhr.responseText);
                    w.document.close()
                    }
                }
            if (response_obj)
                {
                if (xhr.status == 200)
                    {
                    ConcurrentAjaxRequests -= 1;
                    if (ConcurrentAjaxRequests <= 0)
                        {
                        SaveStatusDivStatestatus_div.style.backgroundColor = SaveStatusDivStateMybgColor;
                        SaveStatusDivStatestatus_div.style.color = SaveStatusDivStateMyColor;
                        SaveStatusDivStatestatus_div.innerHTML = SaveStatusDivStateMyText;
                        }
                    callback(response_obj);
                    }
                else
                    {
                    SaveStatusDivStatestatus_div.style.backgroundColor = "red";
                    SaveStatusDivStatestatus_div.style.color = "white";
                    SaveStatusDivStatestatus_div.innerHTML = "Impossible d'executer la requete distante (Ajax). Message d'erreur : " + response_obj.error;
                    if (error_callback)
                        {
                        error_callback(xhr);
                        }
                    }
                }
            }
        }
    SaveStatusDivStatestatus_div.style.backgroundColor = "orange";
    SaveStatusDivStatestatus_div.style.color = "white";
    SaveStatusDivStatestatus_div.innerHTML = "Requete distante (Ajax) en cours...";
    ConcurrentAjaxRequests += 1;
    xhr.open("POST",ajax_service,true);
    xhr.setRequestHeader('Content-Type','application/x-www-form-urlencoded');
    xhr.setRequestHeader('X_REQUESTED_WITH','XMLHttpRequest');
    xhr.send(ajax_request);
    }

dojo.addOnLoad(function() {
         // Quand une requete AJAX part
         dojo.subscribe("/dojo/io/send", function(/*dojo.Deferrred*/dfd){
             SaveStatusDivStatestatus_div.style.backgroundColor = "orange";
             SaveStatusDivStatestatus_div.style.color = "white";
             SaveStatusDivStatestatus_div.innerHTML = "Requete distante (Ajax) en cours...";
         });

         // Quand une requete AJAX s'est terminée avec succes
         dojo.subscribe("/dojo/io/load", function(/*dojo.Deferrred*/dfd, 
/*Object*/response){
                        SaveStatusDivStatestatus_div.style.backgroundColor = SaveStatusDivStateMybgColor;
                        SaveStatusDivStatestatus_div.style.color = SaveStatusDivStateMyColor;
                        SaveStatusDivStatestatus_div.innerHTML = SaveStatusDivStateMyText;
         });

         // Quand une requete AJAX reviens en erreur
         dojo.subscribe("/dojo/io/error", 
function(/*dojo.Deferrred*/dfd, /*Object*/response){
                    SaveStatusDivStatestatus_div.style.backgroundColor = "red";
                    SaveStatusDivStatestatus_div.style.color = "white";
                    SaveStatusDivStatestatus_div.innerHTML = "Impossible d'executer la requete distante (Ajax). Message d'erreur : " + response.error;
             var w = window.open();
             w.document.write(dfd.ioArgs.xhr.responseText);
             w.document.close()
         });
     });
