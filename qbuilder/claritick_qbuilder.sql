create or replace view tickets_clarisys as (
    select
        *
    from ticket_ticket
    where not client_is_child_of(client_id, 151)
    );
create or replace view tickets_clarisys_siemens as (
    select
        *,
        client_is_child_of(client_id, 151) as ticket_siemens,
        date_close-date_open as temps_cloture
    from ticket_ticket
    );
create or replace view rapidite_cloture_siemens_ou_pas as (
    select
        date_trunc('week', date_open) as timestep,
        count(id) as ouverts,
        count((case when date_close-date_open<'24 hours'::interval then 1 else null end)) as clotures_rapidement,
        (case when count(id) = 0 then 100 else round((count((case when date_close-date_open<'24 hours'::interval then 1 else null end))::numeric / count(id)::numeric) * 100,1) end) as pourcentage,
        ticket_siemens
    from
        tickets_clarisys_siemens
    group by ticket_siemens, timestep
    );
create or replace view temps_cloture as (
    select 
        id, date_open,
        date_close,
        date_close-date_open as temps_cloture
    from ticket_ticket
    );
create or replace view clotures_dans_la_journee_month as (
    select
        timesteps.timestep as jour,
        ''::text as garde,
        tickets.ouverts as tickets_ouverts,
        tickets.clotures_rapidement as clotures_rapidement,
        (case when tickets.ouverts is null then 100 else round((tickets.clotures_rapidement::numeric / tickets.ouverts::numeric) * 100,1) end) as pourcentage
    from
        (select date_trunc('month', date_open) as timestep,
        count(id) as ouverts,
        count((case when date_close-date_open<'24 hours'::interval then 1 else null end)) as clotures_rapidement
        from tickets_clarisys
        group by timestep) as tickets
    right outer join
        (select timestep from generate_series(
            date_trunc('month', now() - '3 years'::interval),
            date_trunc('month', now()),
            '1 month'::interval) as timestep) as timesteps
        on tickets.timestep = timesteps.timestep
    order by jour
    );
create or replace view clotures_dans_la_journee_week as (
    select
        timesteps.timestep as jour,
        ''::text as garde,
        tickets.ouverts as tickets_ouverts,
        tickets.clotures_rapidement as clotures_rapidement,
        (case when tickets.ouverts is null then 100 else round((tickets.clotures_rapidement::numeric / tickets.ouverts::numeric) * 100,1) end) as pourcentage
    from
        (select date_trunc('week', date_open) as timestep,
        count(id) as ouverts,
        count((case when date_close-date_open<'24 hours'::interval then 1 else null end)) as clotures_rapidement
        from tickets_clarisys
        group by timestep) as tickets
    right outer join
        (select timestep from generate_series(
            date_trunc('week', now() - '3 years'::interval),
            date_trunc('week', now()),
            '1 week'::interval) as timestep) as timesteps
        on tickets.timestep = timesteps.timestep
    order by jour
    );
create or replace view clotures_dans_la_journee as (
    select
        timesteps.timestep as jour,
        (case when extract('dow' from timesteps.timestep) > 5 then 'weekend' else 'semaine' end) as garde,
        tickets.ouverts as tickets_ouverts,
        tickets.clotures_rapidement as clotures_rapidement,
        (case when tickets.ouverts is null then 100 else round((tickets.clotures_rapidement::numeric / tickets.ouverts::numeric) * 100,1) end) as pourcentage
    from
        (select date_trunc('day', date_open) as timestep,
        count(id) as ouverts,
        count((case when date_close-date_open<'24 hours'::interval then 1 else null end)) as clotures_rapidement
        from tickets_clarisys
        group by timestep) as tickets
    right outer join
        (select timestep from generate_series(
            date_trunc('day', now() - '3 years'::interval),
            date_trunc('day', now()),
            '1 day'::interval) as timestep) as timesteps
        on tickets.timestep = timesteps.timestep
    order by jour
    );
CREATE TABLE "qbuilder_queryparameters" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" text NOT NULL,
    "data" text NOT NULL,
    "status" integer NOT NULL DEFAULT 0
)
;
CREATE TABLE "qbuilder_result" (
    "id" serial NOT NULL PRIMARY KEY,
    "query_id" integer NOT NULL REFERENCES "qbuilder_queryparameters" ("id") DEFERRABLE INITIALLY DEFERRED,
    "data" text NOT NULL,
    "date" timestamp with time zone NOT NULL DEFAULT NOW()
)
;
create language plpgsql;
create or replace function client_is_child_of(_id_potential_child integer, _id_potential_parent integer)
    returns boolean
    language plpgsql
    as $$
    declare
        _current_parent integer;
    begin
        if _id_potential_child = _id_potential_parent then
            return true;
        end if;
        select parent_id into _current_parent from common_client where id = _id_potential_child;
        if _current_parent is null then
            return false;
        end if;
        if _current_parent = _id_potential_parent then
            return true;
        end if;
        return (select client_is_child_of(_current_parent, _id_potential_parent));
    end;
$$;
