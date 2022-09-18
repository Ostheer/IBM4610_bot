Sub appendPrintCloseDeleteTxt()
    myPath = "Z:\suremark\pipe\"
    
    'Scan for text files
    MyFile = Dir(myPath & "to_print*.txt")
    If Len(MyFile) > 0 Then
        add_text myPath & MyFile
        print_now
        On Error GoTo CloseProgram:
            Kill myPath & MyFile
    End If

CloseProgram:
    'Close document without saving
    Application.Quit SaveChanges:=False
End Sub

Sub appendPrintCloseDelete()
    myPath = "Z:\suremark\print\"
    
    'Scan for text files
    MyFile = Dir(myPath & "*.docx")
    If Len(MyFile) > 0 Then
        If InStr(MyFile, "_direct") > 0 Then
            Application.Quit SaveChanges:=False
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

Sub add_text(MyFile)
    On Error GoTo ErrHandler1:
        Dim objStream, strData
        Set objStream = CreateObject("ADODB.Stream")
        objStream.Charset = "utf-8"
        objStream.Open
        objStream.LoadFromFile (MyFile)
        strData = objStream.ReadText()
        ActiveDocument.Content.InsertAfter Text:=strData
        ActiveDocument.Range.Select
        ActiveDocument.Range.Font.Name = "Font A"
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
