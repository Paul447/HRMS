USE HRMS;
GO

CREATE OR ALTER PROCEDURE ResetUsedFamilyVerifiedSickLeave
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        PRINT '🔄 Starting reset of used family verified sick leave balances...';

        -- Reset used_FVSL to 0 for all users
        UPDATE sick_leave_balances
        SET used_FVSL = 0,
            updated_at = SYSDATETIMEOFFSET();

        PRINT 'Successfully reset used family verified sick leave balances for all users.';

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT 'Error resetting used family verified sick leave balances: ' + ERROR_MESSAGE();
    END CATCH
END;
GO
EXEC ResetUsedFamilyVerifiedSickLeave