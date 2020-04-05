# The Mark Pipe
## If you want to be able to pipe any `stdout` to your printer, like `ls | mark`, do the following

### On the user's pc
* Create a folder where temporary text file (and perhaps the other files) can be stored, such as `~/.tg_bot_read_dir`
* Review `suremark_pipe.service` and place it in `/etc/systemd/system`
* Change folder location in `main.cpp` to point to the new folder
* Compile `main.cpp` to `mark`, and place it somewhere on your path. May be in the new folder, in that case add `export PATH="${PATH}:$HOME/.tg_bot_read_dir"` to your `.zshrc`.
* Review `send_poller`; change folder location and ssh host name
* Make sure you have ssh access to your server with a keypair
