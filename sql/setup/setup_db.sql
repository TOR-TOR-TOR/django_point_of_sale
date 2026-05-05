-- ============================================
-- CREATE DATABASE
-- ============================================
CREATE DATABASE pos_db;
GO

-- ============================================
-- CREATE SERVER-LEVEL LOGIN
-- ============================================
USE master;
GO

CREATE LOGIN pos_user WITH PASSWORD = 'Pos123!';
GO

-- ============================================
-- CREATE DATABASE-LEVEL USER & GRANT ROLE
-- ============================================
USE pos_db;
GO

CREATE USER pos_user FOR LOGIN pos_user;
GO

ALTER ROLE db_owner ADD MEMBER pos_user;
GO

-- ============================================
-- VERIFY EVERYTHING
-- ============================================
SELECT name, create_date, collation_name 
FROM sys.databases 
WHERE name = 'pos_db';

SELECT name, type_desc 
FROM sys.server_principals 
WHERE name = 'pos_user';

USE pos_db;
SELECT name, type_desc 
FROM sys.database_principals 
WHERE name = 'pos_user';



-- Enable mixed authentication mode (Windows + SQL Server)
EXEC xp_instance_regwrite
    N'HKEY_LOCAL_MACHINE',
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'LoginMode',
    REG_DWORD,
    2;
GO