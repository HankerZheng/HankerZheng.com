-- schema.sql

drop database if exists myblog;

create database myblog;

use myblog;

grant select, insert, update, delete on myblog.* to 'myblogbytranswarp'@'localhost';

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
    `title` varchar(50) not null,
    `tags` varchar(100) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `cr_year` smallint not null,
    `cr_month` tinyint not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table photos (
    `id` varchar(50) not null,
    `title` varchar(50) not null,
    `descript` varchar(200) not null,
    `path` varchar(100) not null,
    `loc_name` varchar(50) not null,
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


INSERT INTO `myblog`.`users` (`id`, `password`, `admin`, `name`, `created_at`) VALUES ('blog_admin', 'a0d2207bbdf539d2243d37790a485a75', '1', 'admin', '0');
INSERT INTO `myblog`.`blogs` (`id`, `title`, `tags`, `summary`, `content`, `cr_year`, `cr_month`, `created_at`) VALUES ('first_blog', 'Blog Test', '["test"]','This is my first blog and it is just a test', 'This is my first blog and it is just a test','1969', '12', '0');
INSERT INTO `myblog`.`tags` (`tag_name`, `blogs`, `count`, `created_at`) VALUES ('test', '["first_blog"]', '1', '0');