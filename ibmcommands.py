import telegram

class commandhandler:
    def __init__(self, clearance, manager):
        self.clearance = clearance
        self.manager = manager
    
    def do(self, update, context):
        if self.manager.accesslevel(update.effective_chat.id) >= self.clearance:
            self.callback(update, context)
        else:
            self.manager.send_message(update, context, "unauthorized")
    
    def callback(self, update, context):
        self.manager.send_message(update, context, "not_implemented")


class start(commandhandler):
    def callback(self, update, context):
        self.manager.send_message(update, context, "start_reply")
        self.manager.tell_daddy(context, str(update.effective_chat.first_name) + " (ID "+str(update.effective_chat.id)+") " + self.manager.lang["start_request"], raw=True)
        self.manager.db.table("strangers").insert({"name":str(update.effective_chat.first_name)+" "+str(update.effective_chat.last_name), "id":str(update.effective_chat.id)})


class cancel(commandhandler):
    def callback(self, update, context):
        if self.manager.state != "normal":
            self.manager.tell_daddy(context, "cancelled", reply_markup=telegram.ReplyKeyboardRemove())
            self.manager.state = "normal"
        else:
            self.manager.tell_daddy(context, "cancel_failed")


class register(commandhandler):
    def callback(self, update, context):
        if self.manager.state == "normal":
            custom_keyboard = [[self.manager.lang["register_allow"]], [self.manager.lang["register_block"]], [self.manager.lang["register_remove"]]]
            custom_keyboard.append(["/cancel"])
            self.manager.tell_daddy(context, "request_what", reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard))
            self.manager.state = "register"


class template(commandhandler):
    def callback(self, update, context):
        try:
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(self.manager.cf["RESOURCES"]["template_doc"], 'rb'))
            self.manager.send_message(update, context, "template_doc_sent")
        except FileNotFoundError as e:
            self.manager.send_message(update, context, "error_user")
            self.manager.tell_daddy(context, "error_admin")
            self.manager.tell_daddy(context, str(e), raw=True)


class sleep(commandhandler):
    def callback(self, update, context):
        self.manager.toggle_sleep(update, context, send_messages=True)


class database(commandhandler):
    def callback(self, update, context):
        if self.manager.state == "normal":
            custom_keyboard = [[self.manager.lang["database_load"]], [self.manager.lang["database_dump"]]]
            custom_keyboard.append(["/cancel"])
            self.manager.tell_daddy(context, "request_what", reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard))
            self.manager.state = "database_modify"


class qr(commandhandler):
    def callback(self, update, context):
        self.manager.handle_print(update, context, doctype="qr")
