# IBM4610_bot

Telegram bot and Windows scripts to automatically print text messages in Telegram on an IBM SureMark receipt printer.
This version of the SureMark 4610 unfortunately only has USB and a proprietary protocol, so it doesn't work natively on Linux. Therefore, the only way to get it to print anything is using some windows 32-bit executable.

I had an old crappy Windows Tablet lying around collecting dust, so I repurposed it.

Now it's a crappy tablet printing Word 2003 documents via Telegram Running Windows XP via Virtualbox in OpenBox on Arch Linux!


| The printer | The tablet |
|------------|-------------|
| ![IBM Printer](readme_images/SureMark.png) | ![Lamina Tablet](readme_images/Lamina.jpg) |

## Basic Setup

Linux machine running Windows XP (32 bit) in a VM, with a shared folder (`Z:\ in Windows`).

The Python telegram bot runs on Linux.
Whenever the user sends a text message, it creates a file `to_print.txt` in a shared folder.

The batch script `print_contents.bat` polls the folder every 500ms.
If it encounters `to_print.txt`, it starts Microsoft Word 2003 using a specific macro (`macro.vba`).

The macro reads the `to_print.txt` file and appends it to `empty_receipt.doc`.
The macro then prints the document, suppressing any errors or warnings (about margins).
Lastly it deletes the file and terminates Word.

The script `macro.vba` is embedded in the base template of the Microsoft Office installation, so the file is not necessarily present on the system.

## Instructions
Not necessarily in the correct order

* Install Windows XP and Office 2003 in the VM

* Install the IBM printer driver, and make it the default printer

* Embed the macro in Word by opening Word, pressing `Alt`+`F11` and pasting the code in a new script file.

* On Linux, install `pip`, and via that install `python-telegram-bot`.

* Place `print_poller` and its content on `C:\`

* Mount the VirtualBox shared folder on `Z:\`

* Create the directory `Z:\telegram_bot`

* Execute `C:\print_poller\print_contents.bat` when Windows starts (e.g. by placing a shortcut in `C:\Documents and Settings\Admin\Start Menu\Programs\Startup`).

* Place `suremark_tg_bot` in `/usr/bin/`, and `chmod 755` it.

* Place the `*.service` files in `/etc/systemd/system` and enable them.

## Installing Linux on the tablet
The Lamina tablet uses a cheap Atom-chipset that doesn't support the regular 64 bit EFI bootfiles.
This is the case for many of these no-name Chinese Windows tablets from the Windows 8 launch era.
Therefore, it is necessary to use a standalone GRUB IA32 EFI file to chainload the Linux installer.

See the Arch Wiki for details: https://wiki.archlinux.org/index.php/Unified_Extensible_Firmware_Interface#Booting_64-bit_kernel_on_32-bit_UEFI


## Notes
I don't own any rights to the IBM driver. Consider it abandonware.


