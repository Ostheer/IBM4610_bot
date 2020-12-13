Sub appendPrintCloseDelete()
    myPath = "Z:\telegram_bot\print\"
    
    'Scan for text files
    MyFile = Dir(myPath & "*.docx")
    If Len(MyFile) > 0 Then
        If InStr(MyFile, "_direct") > 0 Then
            Exit Sub
        End If
        add_text_from_docx myPath & MyFile
        print_now
        On Error GoTo CloseProgram:
            Kill myPath & MyFile
    End If

CloseProgram:
    'Close document without saving
    Application.Quit SaveChanges:=False
End Sub

Sub PrintCloseDelete()
    On Error GoTo ErrHandler1:
    print_now
    DeleteThisFile
    Application.Quit SaveChanges:=False
ErrHandler1:
    On Error GoTo ErrHandler2:
    DeleteThisFile
    Application.Quit SaveChanges:=False
ErrHandler2:
    Application.Quit SaveChanges:=False
End Sub

Sub DeleteThisFile()
    Dim MyFile As String
    MyFile = ActiveDocument.Path & "\" & ActiveDocument.Name
    ActiveDocument.Close (wdDoNotSaveChanges)
    Kill MyFile
End Sub

Sub add_text_from_docx(MyFile)
    On Error GoTo ErrHandler1:
        Selection.Collapse Direction:=wdCollapseEnd
        Selection.InsertFile FileName:=MyFile, Link:=False
ErrHandler1:
    Exit Sub
End Sub

Sub print_now()
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
End Sub


