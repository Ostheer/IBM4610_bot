Sub appendPrintCloseDelete()
    myPath = "Z:\telegram_bot\"
    
    'Scan for text files
    myFile = Dir(myPath & "to_print*.txt")
    If Len(myFile) > 0 Then
        add_text myPath & myFile
        print_now
        On Error GoTo CloseProgram:
            Kill myPath & myFile
    End If

    'Scan for images
    myFile = Dir(myPath & "to_print*.bmp")
    myCaption = Replace(myFile, ".bmp", ".caption")
    If Len(myFile) > 0 Then
        add_imag myPath & myFile
        ActiveDocument.Content.InsertAfter text:=vbNewLine
        add_text myPath & myCaption
        print_now
        On Error GoTo CloseProgram:
            Kill myPath & myFile
            Kill myPath & myCaption
    End If

CloseProgram:
    'Close document without saving
    Application.Quit SaveChanges:=False
End Sub

Sub add_text(myFile)
    On Error GoTo ErrHandler1:
        Dim objStream, strData
        Set objStream = CreateObject("ADODB.Stream")
        objStream.Charset = "utf-8"
        objStream.Open
        objStream.LoadFromFile (myFile)
        strData = objStream.ReadText()
        ActiveDocument.Content.InsertAfter text:=strData
ErrHandler1:
    Exit Sub
End Sub

Sub add_imag(myFile)
    On Error GoTo ErrHandler1:
        Selection.InlineShapes.AddPicture FileName:=myFile, LinkToFile:=False, SaveWithDocument:=True
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
