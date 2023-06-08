CREATE TABLE `global_links` (
	`added_date` DATETIME NOT NULL,
	`project_domain` VARCHAR(50) NOT NULL COLLATE 'utf8_general_ci',
	`project_family` VARCHAR(50) NOT NULL COLLATE 'utf8_general_ci',
	`page_id` INT(10) NOT NULL,
	`rev_id` INT(10) NOT NULL,
	`user_text` VARCHAR(100) NOT NULL COLLATE 'utf8_general_ci',
	`link_url` VARCHAR(500) NOT NULL COLLATE 'utf8_general_ci',
	`base_domain` VARCHAR(255) NOT NULL COLLATE 'utf8_general_ci',
	`domain_ip` VARCHAR(20) NOT NULL COLLATE 'utf8_general_ci',
	PRIMARY KEY (`link_url`) USING BTREE,
	INDEX `base_domain` (`base_domain`) USING BTREE,
	INDEX `domain_ip` (`domain_ip`) USING BTREE,
	INDEX `user_text` (`user_text`) USING BTREE
)
COLLATE='utf8_general_ci'
;
