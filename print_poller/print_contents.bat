
:loop

for %%f in (z:\telegram_bot\to_print*.doc) do (
"C:\Program Files\Microsoft Office\OFFICE11\WINWORD.EXE" "z:\telegram_bot\%%~nf.doc" /mPrintCloseDelete
)

if exist "z:\telegram_bot\to_print*" (
"C:\Program Files\Microsoft Office\OFFICE11\WINWORD.EXE" empty_receipt.doc /mappendPrintCloseDelete
)


ping 192.0.2.1 -n 1 -w 500 >nul

goto loop
@pause
