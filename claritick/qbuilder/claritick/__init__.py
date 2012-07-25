#
# A sample model declaration for the demonstration of Query Builder
#
# In order to use Query Builder with your own database, you need to
# define your models as in this sample. (Create a folder named by
# you application or copy the sample folder).

from qbuilder.claritick.models import VueTicketsTempsCloture, Tickets, CloturesDansLaJournee, CloturesDansLaJourneeSemaine, CloturesDansLaJourneeMois, TickUser, Priority, Category, State, RapiditeClotureSiemensOuPas, TicketsClarisysSiemens, NombreTicketsCloturesOuPas
QBSelectables = ['VueTicketsTempsCloture', 'Tickets', 'CloturesDansLaJournee', 'CloturesDansLaJourneeSemaine', 'CloturesDansLaJourneeMois', 'TickUser', 'Priority', 'Category', 'State', 'RapiditeClotureSiemensOuPas', 'TicketsClarisysSiemens', 'NombreTicketsCloturesOuPas']
QBEventsConfig = {
    'model' : None,
    'partition_field' : None,
    'event_type' : None,
    'event_date' : None,
    }
