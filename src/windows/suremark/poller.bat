:loop

for %%f in (z:\suremark\print\*_direct.doc) do (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" "z:\suremark\print\%%~nf.doc" /mPrintCloseDelete
)

for %%f in (z:\suremark\print\*_direct.docx) do (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" "z:\suremark\print\%%~nf.docx" /mPrintCloseDelete
)

if exist "z:\suremark\print\*.docx" (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" empty_receipt.doc /mappendPrintCloseDelete
)

if exist "z:\suremark\pipe\*.txt" (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" empty_receipt.doc /mappendPrintCloseDeleteTxt
)

sleep -m 500

goto loop
@pause

