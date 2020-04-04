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
        
        
       makeBars
       makeBold
ErrHandler1:
    Exit Sub
End Sub

Sub makeBars()
    Dim StartWord As String, EndWord As String
    Dim Find1stRange As Range, FindEndRange As Range
    Dim DelRange As Range, DelStartRange As Range, DelEndRange As Range, BarRange As Range
    'Setting up the Ranges
    Set Find1stRange = ActiveDocument.Range
    Set FindEndRange = ActiveDocument.Range
    Set DelRange = ActiveDocument.Range
    Set BarRange = ActiveDocument.Range
    'Set your Start and End Find words here to cleanup the script
    StartWord = "<BAR>"
    EndWord = "</BAR>"
    'Starting the Find First Word
    With Find1stRange.Find
        .text = StartWord
        .Replacement.text = ""
        .Forward = True
        .Wrap = False
        .Format = False
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    
        'Execute the Find
        Do While .Execute
            'If Found then do extra script
            If .Found = True Then
                'Setting the Found range to the DelStartRange
                Set DelStartRange = Find1stRange
                
                'Setting the FindEndRange up for the remainder of the document form the end of the StartWord
                FindEndRange.Start = DelStartRange.End
                FindEndRange.End = ActiveDocument.Content.End
    
                'Setting the Find to look for the End Word
                With FindEndRange.Find
                    .text = EndWord
                    .Execute
    
                    'If Found then do extra script
                    If .Found = True Then
                        'Setting the Found range to the DelEndRange
                        Set DelEndRange = FindEndRange
                    End If
    
                End With
                'Selecting the delete range
                DelRange.Start = DelStartRange.Start
                BarRange.Start = DelStartRange.End
                DelRange.End = DelEndRange.End
                BarRange.End = DelEndRange.Start

                'Change to barcode font
                BarRange.Select
                BarRange.Font.Name = "JAN 13 (EAN-13)"
                BarRange.Font.Size = 15
                
                'Delete tags
                DelRange.Start = DelStartRange.Start
                DelRange.End = DelStartRange.End
                DelRange.Delete
                DelRange.Start = DelEndRange.Start
                DelRange.End = DelEndRange.End
                DelRange.Delete
    
            End If      'Ending the If Find1stRange .Found = True
        Loop        'Ending the Do While .Execute Loop
    End With    'Ending the Find1stRange.Find With Statement
End Sub

Sub makeBold()
    Dim StartWord As String, EndWord As String
    Dim Find1stRange As Range, FindEndRange As Range
    Dim DelRange As Range, DelStartRange As Range, DelEndRange As Range, BarRange As Range
    'Setting up the Ranges
    Set Find1stRange = ActiveDocument.Range
    Set FindEndRange = ActiveDocument.Range
    Set DelRange = ActiveDocument.Range
    Set BarRange = ActiveDocument.Range
    'Set your Start and End Find words here to cleanup the script
    StartWord = "<BF>"
    EndWord = "</BF>"
    'Starting the Find First Word
    With Find1stRange.Find
        .text = StartWord
        .Replacement.text = ""
        .Forward = True
        .Wrap = False
        .Format = False
        .MatchCase = True
        .MatchWholeWord = False
        .MatchWildcards = False
        .MatchSoundsLike = False
        .MatchAllWordForms = False
    
        'Execute the Find
        Do While .Execute
            'If Found then do extra script
            If .Found = True Then
                'Setting the Found range to the DelStartRange
                Set DelStartRange = Find1stRange
                
                'Setting the FindEndRange up for the remainder of the document form the end of the StartWord
                FindEndRange.Start = DelStartRange.End
                FindEndRange.End = ActiveDocument.Content.End
    
                'Setting the Find to look for the End Word
                With FindEndRange.Find
                    .text = EndWord
                    .Execute
    
                    'If Found then do extra script
                    If .Found = True Then
                        'Setting the Found range to the DelEndRange
                        Set DelEndRange = FindEndRange
                    End If
    
                End With
                'Selecting the delete range
                DelRange.Start = DelStartRange.Start
                BarRange.Start = DelStartRange.End
                DelRange.End = DelEndRange.End
                BarRange.End = DelEndRange.Start

                'Change to barcode font
                BarRange.Select
                BarRange.Font.Bold = True
                
                'Delete tags
                DelRange.Start = DelStartRange.Start
                DelRange.End = DelStartRange.End
                DelRange.Delete
                DelRange.Start = DelEndRange.Start
                DelRange.End = DelEndRange.End
                DelRange.Delete
    
            End If      'Ending the If Find1stRange .Found = True
        Loop        'Ending the Do While .Execute Loop
    End With    'Ending the Find1stRange.Find With Statement
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
