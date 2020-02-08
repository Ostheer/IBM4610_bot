Sub appendPrintCloseDelete()
    myFile = "Z:\telegram_bot\to_print.txt"

    'Add the text from the file
    On Error GoTo ErrHandler1:
        Open myFile For Input As #1
        Do Until EOF(1)
            Line Input #1, textline
            Text = Text & textline & vbNewLine
        Loop
        Close #1
        ActiveDocument.Content.InsertAfter Text:=Text
        
    'Print the file without margins warning
    With Application
        'Turn off DisplayAlerts
        .DisplayAlerts = wdAlertsNone
        'Print document
        'Background print must be turned off to prevent message
        .PrintOut Background:=False
        'Turn on DisplayAlerts again
        .DisplayAlerts = wdAlertsAll
    End With
    
    'Delete the file
    On Error GoTo ErrHandler1:
        Kill myFile

CloseProgram:
    'Close document without saving
    Application.Quit SaveChanges:=False

    Exit Sub
ErrHandler1:
    'if file cannot be opened (not present)
    MsgBox "er is iets foutgegaan"
    GoTo CloseProgram
End Sub
