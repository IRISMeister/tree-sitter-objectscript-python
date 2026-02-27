Class Sample.Test
{
    ClassMethod trap()
    {
        Set $ZT="ERR"
        Set var=1
        Set ^glo=1
        Quit
ERR
        Quit
    }
    ClassMethod Hello()
    {
        Write "Hello"
        GOTO END
END
        Quit
    }
    ClassMethod Bye()
    {
        Set XYZ=1
        Set aBC=1
        Write "Bye"
    }
    ClassMethod TryCatch()
    {
        Try {
            Set a=3/0
        }
        Catch(e) {
            Write "Error trapped"
        }
    }
    ClassMethod TryCatch2()
    {
        Try {
            Set a=3/0
        }
        Catch(e) {
            Write "Error trapped"
            throw e
        }
    }
}
