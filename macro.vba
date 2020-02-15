Sub appendPrintCloseDelete()
    myPath = "Z:\telegram_bot\"
    
    'Scan for text files
    MyFile = Dir(myPath & "to_print*.txt")
    If Len(MyFile) > 0 Then
        add_text myPath & MyFile
        print_now
        On Error GoTo CloseProgram:
            Kill myPath & MyFile
    End If

    'Scan for images
    MyFile = Dir(myPath & "to_print*.bmp")
    myFile_src = Replace(MyFile, ".bmp", ".jpg")
    myCaption = Replace(MyFile, ".bmp", ".caption")
    If Len(MyFile) > 0 Then
        add_imag myPath & MyFile
        ActiveDocument.Content.InsertAfter text:=vbNewLine
        add_text myPath & myCaption
        print_now
        On Error GoTo CloseProgram:
            Kill myPath & MyFile
            Kill myPath & myFile_src
            Kill myPath & myCaption
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

Sub add_text(MyFile)
    On Error GoTo ErrHandler1:
        Dim objStream, strData
        Set objStream = CreateObject("ADODB.Stream")
        objStream.Charset = "utf-8"
        objStream.Open
        objStream.LoadFromFile (MyFile)
        strData = objStream.ReadText()
        ActiveDocument.Content.InsertAfter text:=strData
ErrHandler1:
    Exit Sub
End Sub

Sub add_imag(MyFile)
    On Error GoTo ErrHandler1:
        Selection.InlineShapes.AddPicture FileName:=MyFile, LinkToFile:=False, SaveWithDocument:=True
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
