alter TABLE user CHARACTER SET utf8;  // set character format

set foreign_key_checks = 0;  // un check foreign_key

INSERT INTO user (id, password, mobile, email, name, source_id, login_count, last_login_time, created_at, updated_at, active, creator_id, last_editor_id, last_edited_at) (s
elect p.id, u.password, u.mobile, u.email, ifnull(u.name,u.nickname), u.source_id, ifnull(u.login_count,0), u.last_login_time, u.created_at, u.updated_at, u.active, 1, 1, u
.updated_at from rouchi_dev.parents as p, rouchi_dev.users as u where u.id=p.user_id and ifnull(u.name, u.nickname) is not NULL and u.mobile);

// notice the method of `ifnull` and multiple tables.

set foreign_key_checks = 1;
