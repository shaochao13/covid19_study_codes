CREATE DATABASE IF NOT EXISTS coronavirus DEFAULT CHARSET utf8;


CREATE TABLE `tb_virus_history_data` (
    `countryShortCode_dateId` VARCHAR(20) NOT NULL COMMENT '数据唯一值',
    `dateId` VARCHAR(10) NOT NULL COMMENT '日期' ,
    `country_name` VARCHAR(30) NOT NULL COMMENT '国家中文名' ,
    `countryShortCode` VARCHAR(20) NOT NULL COMMENT '国家简称' ,
    `confirmedCount` INT NOT NULL DEFAULT '0' COMMENT '累积确诊人数' ,
    `currentConfirmedCount` INT NOT NULL DEFAULT '0' COMMENT '现存确诊人数' ,
    `curedCount` INT NOT NULL DEFAULT '0' COMMENT '治愈人数' ,
    `deadCount` INT NOT NULL DEFAULT '0' COMMENT '死亡人数' ,
    PRIMARY KEY (`countryShortCode_dateId`),
    INDEX `index_dateId` (`dateId`)
) ENGINE = InnoDB DEFAULT CHARSET=utf8 COMMENT '历史疫情数据';


CREATE TABLE `tb_virus_last_updated_data` (
    `countryShortCode` VARCHAR(20) NOT NULL COMMENT '国家简称' ,
    `provinceName` VARCHAR(30) NOT NULL COMMENT '国家中文名' ,
    `confirmedCount` INT NOT NULL DEFAULT '0' COMMENT '累积确诊人数' ,
    `currentConfirmedCount` INT NOT NULL DEFAULT '0' COMMENT '现存确诊人数' ,
    `curedCount` INT NOT NULL DEFAULT '0' COMMENT '治愈人数' ,
    `deadCount` INT NOT NULL DEFAULT '0' COMMENT '死亡人数' ,
    PRIMARY KEY (`countryShortCode`)
) ENGINE = InnoDB DEFAULT CHARSET=utf8 COMMENT '最新疫情数据';

