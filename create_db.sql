create database db_triggers;
create user db_triggers;
grant all permission on db_triggers to db_triggers;
grant all on db_triggers to db_triggers;
grant all on database db_triggers to db_triggers;
alter role db_triggers with password 'db_triggers';
alter role db_triggers createdb;
alter role db_triggers superuser;
