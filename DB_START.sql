-- 그룹 테이블 생성
CREATE TABLE schedule_groups (
group_id int(11) NOT NULL AUTO_INCREMENT,
group_name varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
description varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
PRIMARY KEY (group_id)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 그룹 데이터 입력
INSERT INTO schedule_groups (group_id, group_name, description)
VALUES
(1, 'Team_1', '센터 Team_1 그룹'),
(2, 'Team_1', '센터 Team_2 그룹'),
(3, 'Team_1', '센터 Team_3 그룹');

-- 직원 테이블 생성
CREATE TABLE schedule_employees (
employee_id int(11) NOT NULL AUTO_INCREMENT,
name varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
employee_code varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
email varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
group_id int(11) NOT NULL,
PRIMARY KEY (employee_id),
FOREIGN KEY (group_id) REFERENCES schedule_groups (group_id)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 직원 데이터 입력 (본인 이름 넣어야함)
INSERT INTO schedule_employees (employee_id, name, employee_code, email , group_id)
VALUES
-- Team_1 그룹
(1, '본인이름', 'Team_1-01', '본인 이메일', 1),
(2, '이승민', 'Team_1-02', 'efgh986@eadh.net', 1),
(3, '박지훈', 'Team_1-03', 'hijq2222@easdh.net', 1),
(4, '최민수', 'Team_1-04', 'ab3dd98764@gdah.com', 1),
(5, '김동현', 'Team_1-05', 'yoibcd134@sdh.net', 1),
(6, '이재영', 'Team_1-06', 'ank145555@epiop.com', 1),
(7, '박성진', 'Team_1-07', 'ursddy5444@eio.com', 1),
(8, '최현석', 'Team_1-08', 'asdsdd45h@eqwq.com', 1),
(9, '김민수', 'Team_1-09', 'hvbnd53257@qwegh.net', 1),
(10, '이동현', 'Team_1-10', 'uyyrd8888@nnsh.com', 1),

-- Team_2 그룹
(11, '김재석', 'Team_2-01', 'cvxv8567@wtqe.com', 2),
(12, '이승진', 'Team_2-02', 'ttttd1457@wet.com', 2),
(13, '박지영', 'Team_2-03', 'qweqe13332@qweqh.net', 2),
(14, '최민호', 'Team_2-04', 'utryh17997@mhgh.com', 2),
(15, '김동석', 'Team_2-05', 'kljhl657@ncncv.net', 2),
(16, '이재민', 'Team_2-06', 'qwe7784@wqeqq.net', 2),
(17, '박성호', 'Team_2-07', 'xcv1221@poup.com', 2),
(18, '최현진', 'Team_2-08', 'dsfxc3458@zvaaa.com', 2),
(19, '김민호', 'Team_2-09', 'cvbfsd9998@uliu.net', 2),
(20, '이동석', 'Team_2-10', 'ruoiu4564@popip.com', 2),

-- Team_3 그룹
(21, '김재현', 'Team_3-01', 'qkjb1596@qeqeq.comnet', 3),
(22, '이승민', 'Team_3-02', 'utyre6587@qoqoq.com', 3),
(23, '박지훈', 'Team_3-03', 'cgdd3145@aajrd.net', 3),
(24, '최민수', 'Team_3-04', 'ikkt6698@bsdsd.com', 3),
(25, '김동현', 'Team_3-05', 'qwefb4554@shsfgh.com', 3),
(26, '이재영', 'Team_3-06', 'opupu7844@piupu.com', 3),
(27, '박성진', 'Team_3-07', 'puumr2434@wrvxa.net', 3),
(28, '최현석', 'Team_3-08', 'bbbdf9787@jyyt.com', 3),
(29, '김민수', 'Team_3-09', 'yrrt1793@vfbrweq.com', 3),
(30, '이동현', 'Team_3-10', 'vbsas6854@tuoy.net', 3);

-- 프로젝트 테이블 생성
CREATE TABLE schedule_projects (
project_id int(11) NOT NULL AUTO_INCREMENT,
project_name varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
group_id int(11) NOT NULL,
description varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
start_date date DEFAULT NULL,
end_date date DEFAULT NULL,
duration int(11) DEFAULT NULL,
PRIMARY KEY (project_id),
FOREIGN KEY (group_id) REFERENCES schedule_groups (group_id)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Main_Task 테이블 생성
CREATE TABLE schedule_Main_Task (
Main_Task_id int(11) NOT NULL AUTO_INCREMENT,
project_id int(11) NOT NULL,
Main_Task_name varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
Main_Task_start_date date DEFAULT NULL,
Main_Task_end_date date DEFAULT NULL,
duration int(11) DEFAULT NULL,
description varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
PRIMARY KEY (Main_Task_id),
FOREIGN KEY (project_id) REFERENCES schedule_projects (project_id)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sub_Task 테이블 생성
CREATE TABLE schedule_Sub_Task (
Sub_Task_id int(11) NOT NULL AUTO_INCREMENT,
project_id int(11) NOT NULL,
Main_Task_name varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
offset_days int(11) DEFAULT NULL,
Sub_Task_name varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
description varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
name varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
calculated_start_date date DEFAULT NULL,
calculated_end_date date DEFAULT NULL,
duration int(11) DEFAULT NULL,
PRIMARY KEY (Sub_Task_id),
FOREIGN KEY (project_id) REFERENCES schedule_projects (project_id)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
