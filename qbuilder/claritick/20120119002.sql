drop view if exists nombre_tickets_fermes_journee;
create or replace view nombre_tickets_fermes_journee as
select
 date_trunc('day', date_open) as jour,
 count(*) as nombre,
 (case
    when date_close is null then 0
    when date_trunc('day', date_open) = date_trunc('day', date_close) then 2
    else 1 end) as statut_cloture,
 category_id = 46 as incident,
 client_is_child_of(ticket_ticket.client_id, 151) AS ticket_siemens

 from ticket_ticket

 where title != 'Invalid title'

 group by
 (case
    when date_close is null then 0
    when date_trunc('day', date_open) = date_trunc('day', date_close) then 2
    else 1 end),
    client_is_child_of(ticket_ticket.client_id, 151),
 category_id = 46,
 date_trunc('day', date_open)

 order by date_trunc('day', date_open);

update qbuilder_queryparameters set data = E'{"type_for_filter_1": "=", "type_for_filter_0": "date_gt_now_less", "type_for_filter_2": "=", "description": "Nombre de tickets ferm\u00c3\u00a9s dans la journ\u00c3\u00a9e/Nombre de tickets non ferm\u00c3\u00a9s (dans la journ\u00c3\u00a9e ou non ferm\u00c3\u00a9s)", "value_for_filter_2": false, "model_for_filter_2": "NombreTicketsCloturesOuPas", "model_for_filter_1": "NombreTicketsCloturesOuPas", "model_for_filter_0": "NombreTicketsCloturesOuPas", "yAxis_minorTickInterval": 1, "field_for_filter_0": "jour", "graph_type": "stackedcolumn", "yAxis_tickInterval": 1, "select_fields": ["nombre", "jour", "statut_cloture"], "model": "NombreTicketsCloturesOuPas", "value_for_filter_0": "3 month", "field_for_filter_2": "ticket_siemens", "value_for_filter_1": true, "whattodo": "select", "field_for_filter_1": "incident", "colors": "red,orange,green"}' where id = 12;

insert into qbuilder_queryparameters (name, data, status) values ('Incidents fermes dans la journee (Y)', E'{"type_for_filter_1": "=", "type_for_filter_0": "date_gt_now_less", "type_for_filter_2": "=", "description": "Nombre de tickets ferm\u00c3\u00a9s dans la journ\u00c3\u00a9e/Nombre de tickets non ferm\u00c3\u00a9s (dans la journ\u00c3\u00a9e ou non ferm\u00c3\u00a9s)", "value_for_filter_2": false, "model_for_filter_2": "NombreTicketsCloturesOuPas", "model_for_filter_1": "NombreTicketsCloturesOuPas", "model_for_filter_0": "NombreTicketsCloturesOuPas", "yAxis_minorTickInterval": 1, "field_for_filter_0": "jour", "graph_type": "stackedcolumn", "yAxis_tickInterval": 1, "select_fields": ["nombre", "jour", "statut_cloture"], "model": "NombreTicketsCloturesOuPas", "value_for_filter_0": "12 month", "field_for_filter_2": "ticket_siemens", "value_for_filter_1": true, "whattodo": "select", "field_for_filter_1": "incident", "colors": "red,orange,green"}', 0);
insert into qbuilder_queryparameters (name, data, status) values ('Tous fermes dans la journee (Y)', E'{"type_for_filter_1": "=", "type_for_filter_0": "date_gt_now_less", "description": "Nombre de tickets ferm\u00c3\u00a9s dans la journ\u00c3\u00a9e/Nombre de tickets non ferm\u00c3\u00a9s (dans la journ\u00c3\u00a9e ou non ferm\u00c3\u00a9s)", "model_for_filter_1": "NombreTicketsCloturesOuPas", "model_for_filter_0": "NombreTicketsCloturesOuPas", "yAxis_minorTickInterval": 1, "field_for_filter_0": "jour", "graph_type": "stackedcolumn", "yAxis_tickInterval": 1, "select_fields": ["nombre", "jour", "statut_cloture"], "model": "NombreTicketsCloturesOuPas", "value_for_filter_0": "3 month", "value_for_filter_1": false, "whattodo": "select", "field_for_filter_1": "ticket_siemens", "colors": "red,orange,green"}', 0);

