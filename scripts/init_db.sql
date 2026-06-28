-- 智扫通机器人智能客服 - 数据库初始化脚本
-- 使用方法: mysql -u root -p < scripts/init_db.sql

CREATE DATABASE IF NOT EXISTS zst_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zst_agent;

-- 删除已存在的表
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS login_logs;
DROP TABLE IF EXISTS users;

-- 创建用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NULL,
    avatar VARCHAR(255) NULL,
    phone VARCHAR(20) NULL,
    is_active TINYINT(1) DEFAULT 1,
    is_superuser TINYINT(1) DEFAULT 0,
    login_count INT DEFAULT 0,
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建登录日志表
CREATE TABLE login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(500) NULL,
    browser VARCHAR(100) NULL,
    os VARCHAR(100) NULL,
    location VARCHAR(200) NULL,
    status TINYINT(1) DEFAULT 1,
    message VARCHAR(200) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建聊天会话表
CREATE TABLE chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    title VARCHAR(100) DEFAULT '新对话',
    is_active TINYINT(1) DEFAULT 1,
    message_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建聊天消息表
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认管理员用户（密码: admin123）
INSERT INTO users (username, email, hashed_password, nickname, is_superuser, is_active)
VALUES ('admin', 'admin@zst.com', '$2b$12$ZxfaQGbh2mLqBhlLK1OdTehH3SHC.Ug/0R5QzPHON6x0hW96Tdv5y', '超级管理员', 1, 1);

SELECT '数据库初始化完成！默认账号: admin, 密码: admin123' as message;
