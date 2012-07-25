BEGIN;
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
CREATE INDEX "qbuilder_result_query_id" ON "qbuilder_result" ("query_id");
COMMIT;
