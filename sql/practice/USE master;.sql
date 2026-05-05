USE master;
GO

-- Enable mixed mode authentication
EXEC xp_instance_regwrite 
    N'HKEY_LOCAL_MACHINE', 
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'LoginMode', 
    REG_DWORD, 
    2;
GO

-- Drop login if exists from previous attempt
IF EXISTS (SELECT name FROM sys.server_principals WHERE name = 'pos_user')
    DROP LOGIN pos_user;
GO

-- Recreate login
CREATE LOGIN pos_user 
    WITH PASSWORD    = 'YourPassword123!',
    CHECK_POLICY     = OFF,
    CHECK_EXPIRATION = OFF;
GO

-- Create database user
USE pos_db;
GO

IF EXISTS (SELECT name FROM sys.database_principals WHERE name = 'pos_user')
    DROP USER pos_user;
GO

CREATE USER pos_user FOR LOGIN pos_user;
GO

ALTER ROLE db_owner ADD MEMBER pos_user;
GO

-- Verify
SELECT name, type_desc, is_disabled 
FROM sys.server_principals 
WHERE name = 'pos_user';
GO