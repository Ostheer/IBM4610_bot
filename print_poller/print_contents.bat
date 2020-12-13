
:loop

for %%f in (z:\telegram_bot\print\*_direct.doc) do (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" "z:\telegram_bot\print\%%~nf.doc" /mPrintCloseDelete
)

for %%f in (z:\telegram_bot\print\*_direct.docx) do (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" "z:\telegram_bot\print\%%~nf.docx" /mPrintCloseDelete
)

if exist "z:\telegram_bot\print\*.docx" (
"C:\Program Files\Microsoft Office\OFFICE12\WINWORD.EXE" empty_receipt.doc /mappendPrintCloseDelete
)

CSCRIPT SLEEP.VBS 300

goto loop
@pause
