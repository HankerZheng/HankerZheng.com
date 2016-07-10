-- schema.sql

drop database if exists myblog;

create database myblog;

use myblog;

grant select, insert, update, delete on myblog.* to 'www-data'@'localhost';

create table users (
    `id` varchar(50) not null,
    `password` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `title` varchar(150) not null,
    `tags` varchar(150) not null,
    `summary` mediumtext not null,
    `content` mediumtext not null,
    `cr_year` smallint not null,
    `cr_month` tinyint not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table photos (
    `id` varchar(50) not null,
    `title` varchar(150) not null,
    `descript` varchar(200) not null,
    `path` varchar(100) not null,
    `loc_name` varchar(150) not null,
    `loc_lat` float(10,6) not null,
    `loc_lng` float(10,6) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table tags (
    `tag_name` varchar(50) not null,
    `blogs` text not null,
    `count` smallint not null,
    `created_at` real not null,
    key `idx_tag_name` (`tag_name`),
    primary key (`tag_name`)
) engine=innodb default charset=utf8;


INSERT INTO `myblog`.`users` (`id`, `password`, `admin`, `name`, `created_at`) VALUES ('blog_admin', 'bf5b3672782891803f304bc27916c3ac', '1', 'admin', '0');