Class Sample.Test
{
    ClassMethod trap()
    {
        Set $ZT="ERR"
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
        Write "Bye"
    }
}
