# IBM4610_bot

## Basic Setup:
Linux machine running Windows XP (32 bit) in a VM, with a shared folder (Z:\ in Windows).

The telegram bot sure_mark.py runs on Linux, from the shared Z:\telegram_bot.
Whenever the user sends a text message, it creates a file to_print.txt in the same folder.

The batch script print_contents.bat polls the folder every 500ms.
If it encounters to_print.txt, it starts Microsoft Word 2003 using a specific macro (macro.vba).
The macro reads the to_print.txt file and appends it to empty_receipt.dot.
The macro then prints the document, suppressing any errors.
Lastly it deletes the file and terminates Word.

The script macro.vba is embedded in the base template of the Microsoft Office installation, so the file is not necessarily present on the system.

## Instructions:
Embed the macro in word by opening Word, pressing Alt+F11 and pasting the code in a new script file.

Install pip, and via that install python-telegram-bot.

Place print_poller and its content on C:\
Mount the VirtualBox shared folder on Z:\
Create the directory Z:\telegram_bot
Place sure_mark.py in the telegram_bot directory, and run it from there.
Execute C:\print_poller\print_contents.bat when Windows starts.
Execute ~/path/to/shared/folder/sure_mark.py when Linux starts.
