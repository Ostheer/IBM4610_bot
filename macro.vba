Sub appendPrintCloseDelete()
    myFile = "Z:\telegram_bot\to_print.txt"

    'Add the text from the file
    On Error GoTo ErrHandler1:
        Dim objStream, strData
        Set objStream = CreateObject("ADODB.Stream")
        objStream.Charset = "utf-8"
        objStream.Open
        objStream.LoadFromFile (myFile)
        strData = objStream.ReadText()
        ActiveDocument.Content.InsertAfter Text:=strData
        
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
