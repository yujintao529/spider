-- we don't know how to generate schema spider (class Schema) :(
create table note
(
	id int auto_increment
		primary key,
	create_time timestamp default CURRENT_TIMESTAMP null,
	title varchar(50) not null,
	constraint note_id_uindex
		unique (id),
	constraint note_title_uindex
		unique (title)
)
comment '小说'
;

create table chapter
(
	id int auto_increment
		primary key,
	title varchar(100) null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
	state int default '0' not null,
	path varchar(200) null,
	content longtext null,
	num int default '-1' null,
	note_id int not null comment 'note的主键',
	constraint chapter_id_uindex
		unique (id),
	constraint chapter_note_id_fk
		foreign key (note_id) references note (id)
)
comment '章节'
;

create index chapter_note_id_fk
	on chapter (note_id)
;

