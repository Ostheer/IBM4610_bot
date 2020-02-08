:loop

if exist "z:\telegram_bot\to_print.txt" (
"C:\Program Files\Microsoft Office\OFFICE11\WINWORD.EXE" empty_receipt.doc /mappendPrintCloseDelete
)

ping 192.0.2.1 -n 1 -w 500 >nul

goto loop
@pause