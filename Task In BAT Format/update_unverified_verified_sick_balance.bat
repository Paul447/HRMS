USE HRMS;
GO

CREATE OR ALTER PROCEDURE UpdateUnverifiedVerifiedSickLeave
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Reference date: start of the biweekly pay period.
        -- Determines when one period ends and the next begins.
        -- On Sundays, balances will be updated for all users based on these rules.
        -- Logic is adaptable; adjustments can be made if required.
        -- Verify against the payroll calendar for accuracy.
        DECLARE @reference_date DATE = '2025-06-29';
        DECLARE @today DATE = '2025-09-21';
        DECLARE @days_since INT = DATEDIFF(DAY, @reference_date, @today);

        -- Run update only on biweekly intervals
        IF @days_since % 14 = 0
        BEGIN
            PRINT 'Running biweekly sick leave update';

            -- Load constants from the university-defined configuration
            DECLARE 
                @accrued_rate NUMERIC(11,10),   -- Default accrual rate (biweekly)
                @threshold_FVSL NUMERIC(5,2);   -- Max annual FVSL usage, capped at 96 hrs

            SELECT TOP 1
                @accrued_rate = accrued_rate,
                @threshold_FVSL = threshold_FVSL
            FROM sick_leave_constants
            ORDER BY id DESC;

            -- Cursor for row-by-row update (logic depends on remaining accrual per row)
            -- JOIN with sick_leave_prorated_values to get each employee's prorated limits
            DECLARE balance_cursor CURSOR FOR
            SELECT 
                b.id, 
                b.unverified_sick_balance, 
                b.verified_sick_balance, 
                p.id AS sick_prorated_id,                    -- Prorated record reference
                p.prorated_unverified_sick_leave,           -- Max unverified sick leave for this employee
                p.prorated_upfront_verified                 -- Max upfront verified sick leave
            FROM sick_leave_balances b
            LEFT JOIN sick_leave_prorated_values p
                ON b.sick_prorated_id = p.id
            FOR UPDATE OF b.unverified_sick_balance, b.verified_sick_balance;

            -- Variables for row processing
            DECLARE 
                @id BIGINT,
                @unverified NUMERIC(13,10),
                @verified NUMERIC(14,10),
                @prorated_id BIGINT,
                @prorated_unverified NUMERIC(5,2),
                @prorated_verified NUMERIC(5,2),
                @accrual NUMERIC(11,10),
                @room NUMERIC(13,10),
                @to_add NUMERIC(13,10);

            OPEN balance_cursor;
            FETCH NEXT FROM balance_cursor 
                INTO @id, @unverified, @verified, @prorated_id, @prorated_unverified, @prorated_verified;

            -- Loop through each row to apply accruals
            WHILE @@FETCH_STATUS = 0
            BEGIN
                SET @accrual = @accrued_rate;

                -- Fill unverified balance first using prorated limit
                IF @unverified < @prorated_unverified
                BEGIN
                    SET @room = @prorated_unverified - @unverified;
                    SET @to_add = CASE WHEN @room < @accrual THEN @room ELSE @accrual END;
                    SET @unverified += @to_add;
                    SET @accrual -= @to_add;
                END

                -- Remaining accrual goes to verified balance
                IF @accrual > 0
                BEGIN
                    SET @verified += @accrual;
                END

                -- Update balances in the table
                UPDATE sick_leave_balances
                SET 
                    unverified_sick_balance = @unverified,
                    verified_sick_balance = @verified,
                    updated_at = SYSDATETIMEOFFSET()
                WHERE id = @id;

                -- Print detailed update info
                PRINT 'Updated SickLeaveBalance ID ' + CAST(@id AS VARCHAR) +
                      ' (Prorated ID: ' + CAST(@prorated_id AS VARCHAR) + ')' +
                      ' → Unverified: ' + CAST(@unverified AS VARCHAR(20)) +
                      ', Verified: ' + CAST(@verified AS VARCHAR(20));

                FETCH NEXT FROM balance_cursor 
                    INTO @id, @unverified, @verified, @prorated_id, @prorated_unverified, @prorated_verified;
            END

            CLOSE balance_cursor;
            DEALLOCATE balance_cursor;

            PRINT 'Sick leave balances updated successfully';
        END
        ELSE
        BEGIN
            PRINT '⏩ Skipping update: Not a biweekly day';
        END

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT 'Error: ' + ERROR_MESSAGE();
    END CATCH
END;
GO

-- Execute the procedure
EXEC UpdateUnverifiedVerifiedSickLeave;
