use HRMS;
GO
CREATE OR ALTER PROCEDURE UpdateYearsOfExperience
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Update experience_years table
        UPDATE e
        SET e.years_of_experience = CAST(
            ROUND(
                (
                    (DATEDIFF(YEAR, u.date_joined, GETDATE()) * 12)
                    + (MONTH(GETDATE()) - MONTH(u.date_joined))
                ) / 12.0,
                2
            ) AS DECIMAL(5,2)
        )
        FROM experience_years e
        INNER JOIN auth_user u ON e.user_id = u.id
        WHERE u.date_joined IS NOT NULL
          AND DATEDIFF(MONTH, u.date_joined, GETDATE()) >= 0;

        COMMIT TRANSACTION;

        PRINT 'Years of experience updated successfully.';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT 'Error: ' + ERROR_MESSAGE();
    END CATCH
END;
GO
