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

dojo.addOnLoad(SaveStatusDivState);

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
