-- This is a sample database to demonstrate Query Builder

begin;
create schema qbuilder;

set search_path to qbuilder, public, pg_catalog;

create table product_category (
    id_product_category serial not null primary key,
    name text not null,
    unique(name)
    );

create table product (
    id_product serial not null primary key,
    name text not null,
    base_price float not null default 0,
    id_product_category integer not null references product_category(id_product_category)
    );

create table customer (
    id_customer serial not null primary key,
    name text not null,
    discount float not null default 1
    );

create table ordering (
    id_ordering serial not null primary key,
    id_customer integer not null references customer(id_customer),
    create_date timestamp with time zone not null default now(),
    payment_date timestamp with time zone,
    shipment_date timestamp with time zone,
    status integer not null default 0);

create table product_ordering (
    id_product_ordering serial not null primary key,
    id_ordering integer not null references ordering(id_ordering),
    id_product integer not null references product(id_product),
    price float not null default 0
    );

create table ordering_history (
    id_ordering_history serial not null primary key,
    id_ordering integer not null references ordering(id_ordering),
    -- 0 : ordering creation
    -- 1 : product added to ordering
    -- 2 : ordering modification
    -- 3 : payment
    -- 4 : shipment
    event_type integer not null default 0,
    event_date timestamp with time zone not null default now()
    );
commit;

begin;

insert into product_category (name) values
    ('tool'),('toy'),('stuff');

insert into product (name, id_product_category, base_price) values
    ('hammer', (select id_product_category from product_category where name = 'tool'), 10),
    ('saw', (select id_product_category from product_category where name = 'tool'), 12),
    ('screwdriver', (select id_product_category from product_category where name = 'tool'), 13),
    ('driller', (select id_product_category from product_category where name = 'tool'), 59),
    ('duck', (select id_product_category from product_category where name = 'toy'), 9),
    ('teddy', (select id_product_category from product_category where name = 'toy'), 17),
    ('chessboard', (select id_product_category from product_category where name = 'toy'), 32),
    ('ball', (select id_product_category from product_category where name = 'toy'), 5),
    ('carpet', (select id_product_category from product_category where name = 'stuff'), 150),
    ('table', (select id_product_category from product_category where name = 'stuff'), 120),
    ('book', (select id_product_category from product_category where name = 'stuff'), 7),
    ('keyboard', (select id_product_category from product_category where name = 'stuff'), 12);

insert into customer (name, discount) values
    ('joe', 1),
    ('albert', 0.8),
    ('tom', 1),
    ('jim', 0.95);

insert into ordering (id_customer, create_date, payment_date, shipment_date, status) values
    ((select id_customer from customer where name = 'joe'), '2011-07-01 14:00', '2011-07-02 16:00', '2011-07-04 09:00', 2),
    ((select id_customer from customer where name = 'albert'), '2011-07-02 12:00', '2011-07-02 13:00', null, 1),
    ((select id_customer from customer where name = 'tom'), '2011-07-04 11:00', null, null, 0),
    ((select id_customer from customer where name = 'jim'), '2011-07-06 14:00', '2011-07-06 19:00', '2011-07-07 13:00', 2);

insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'joe' and p.name='hammer');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'joe' and p.name='screwdriver');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'joe' and p.name='duck');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'joe' and p.name='keyboard');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'albert' and p.name='keyboard');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'albert' and p.name='ball');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'albert' and p.name='chessboard');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'albert' and p.name='saw');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'tom' and p.name='keyboard');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'tom' and p.name='carpet');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'tom' and p.name='hammer');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'jim' and p.name='book');
insert into product_ordering (id_ordering, id_product, price)
    (select o.id_ordering, p.id_product, p.base_price * c.discount from ordering as o join customer as c using (id_customer), product as p where c.name = 'jim' and p.name='book');

insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 0, '2011-07-01 14:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-01 15:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-01 16:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-01 16:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-01 17:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-01 17:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-02 09:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-02 10:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-02 13:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 3, '2011-07-02 14:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 3, '2011-07-02 16:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 4, '2011-07-04 09:00' from ordering as o join customer as c using (id_customer) where c.name = 'joe');

insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 0, '2011-07-02 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'albert');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-02 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'albert');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-02 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'albert');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-02 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'albert');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-02 13:00' from ordering as o join customer as c using (id_customer) where c.name = 'albert');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 3, '2011-07-02 13:00' from ordering as o join customer as c using (id_customer) where c.name = 'albert');

insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 0, '2011-07-04 11:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-04 11:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-04 11:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-04 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-04 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-04 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-04 12:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-04 13:00' from ordering as o join customer as c using (id_customer) where c.name = 'tom');

insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 0, '2011-07-06 14:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-06 15:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-06 16:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-06 16:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-06 17:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-06 17:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 2, '2011-07-06 17:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 1, '2011-07-06 18:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 3, '2011-07-06 19:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');
insert into ordering_history (id_ordering, event_type, event_date) (select o.id_ordering, 4, '2011-07-07 13:00' from ordering as o join customer as c using (id_customer) where c.name = 'jim');

commit;
