import telegram
import ibmprint
import datetime
from tinydb import Query
import tinydb.operations as tdop

def nows():
    return str(datetime.datetime.now())

def fileExtenstion(update):
    try:
        return update.message.document.file_name.split('.')[-1]
    except IndexError:
        return "no_extension"
    except AttributeError:
        return "no_file"

class manager:
    def __init__(self, database, config):
        self.db = database
        self.cf = config
        self.printer = ibmprint.pronter(print_directory=self.cf["ADMIN"]["print_dir"],
                                        queue_directory=self.cf["ADMIN"]["queue_dir"],
                                        fonts = self.cf["FONTS"],
                                        tags = self.cf["TAGS"],
                                        db = self.db,
                                        max_time_pending = self.cf["ADMIN"]["max_time_pending"])
        self.state = "normal"
        self.lang = self.cf["LANG"]
        self.asleep = False
        self.missed_messages = 0

        if not "users" in self.db.tables():
            users = self.db.table("users")
            users.insert({"name":"admin", "id":self.cf["ADMIN"]["admin_id"], "type":"admin", "added":nows(), "N":0})
            #TODO: check if admin ID has been updated in config file


    ### helper functions
    def moduser(self, name, user_id, utype):
        user_id = str(user_id)
        User = Query()
        t = self.db.table("users")
        r = t.search(User.id == user_id)

        if len(r) == 0:
            #add new user
            t.insert({"name":name, "id":user_id, "type":utype, "added":nows(), "N":0})
            return False
        elif len(r) == 1:
            #user already registered
            if r[0]["type"] != utype:
                #update user type
                t.update(tdop.set("type", utype), User.id == user_id)
                return False
            #else do nothing
        else:
            return True #TODO: duplicate entry, should not occur, consider sending a warning
    
    def deluser(self, user_id):
        user_id = str(user_id)
        User = Query()
        t = self.db.table("users")
        r = t.search(User.id == user_id)

        if len(r) == 0:
            return True #no such user, cannot delete
        elif len(r) > 0:
            t.remove(User.id == user_id)
            return False
    
    def accesslevel(self, user_id):
        """
        -1: banned
         0: stranger
         1: allowed
         2: admin
        """
        user_id = str(user_id)
        t = self.db.table("users")
        r = t.search(Query().id == user_id)

        if len(r) == 0:
            return 0
        elif len(r) == 1:
            utype = r[0]["type"]

            if utype == "blocked":
                return -1
            elif utype == "user":
                return 1
            elif utype == "admin":
                return 2
    
    def send_message(self, update, context, string, raw=False, **kwargs):
        try:
            if "direct_id" in kwargs:
                id = kwargs["direct_id"]    
            else:
                id = update.effective_chat.id
        except KeyError:
            return True,

        try:
            if "reply_markup" in kwargs:
                rm = kwargs["reply_markup"]
                if not raw:
                    context.bot.send_message(chat_id=id, text=self.lang[string], reply_markup=rm)
                else:
                    context.bot.send_message(chat_id=id, text=string, reply_markup=rm)
            else:
                if not raw:
                    context.bot.send_message(chat_id=id, text=self.lang[string])
                else:
                    context.bot.send_message(chat_id=id, text=string)
        except telegram.error.BadRequest:
            return True, "message_invalid_id"
        except:
            return True, "unknown_error"
        
        return False,
        
    def tell_daddy(self, context, string, **kwargs):
        return self.send_message(None, context, string, direct_id=self.cf["ADMIN"]["admin_id"], **kwargs)


    def command_start(self, update, context):
        self.send_message(update, context, "start_reply")
        self.tell_daddy(context, str(update.effective_chat.first_name) + " (ID "+str(update.effective_chat.id)+") " + self.lang["start_request"], raw=True)

    def command_cancel(self, update, context):
        if self.accesslevel(update.effective_chat.id) == 2:
            if self.state == "register":
                self.tell_daddy(context, "cancelled", reply_markup=telegram.ReplyKeyboardRemove())
                self.state = "normal"
            else:
                self.tell_daddy(context, "cancel_failed")
        else:
            self.send_message(update, context, "unauthorized")

    def command_register(self, update, context):
        if self.accesslevel(update.effective_chat.id) == 2:
            if self.state == "normal":
                custom_keyboard = [[self.lang["register_allow"]], [self.lang["register_block"]], [self.lang["register_remove"]]]
                reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                self.tell_daddy(context, "register_how", reply_markup=reply_markup)
                self.state = "register"
        else:
            self.send_message(update, context, "unauthorized")

    def command_template(self, update, context):
        if self.accesslevel(update.effective_chat.id) >= 1:
            try:
                context.bot.send_document(chat_id=update.effective_chat.id, document=open(self.cf["RESOURCES"]["template_doc"], 'rb'))
                self.send_message(update, context, "template_doc_sent")
            except FileNotFoundError as e:
                self.send_message(update, context, "error_user")
                self.tell_daddy(context, "error_admin")
                self.tell_daddy(context, str(e), raw=True)
        else:
            self.send_message(update, context, "unauthorized")

    def command_sleep(self, update, context):
        if self.accesslevel(update.effective_chat.id) == 2:
            if self.asleep:
                self.tell_daddy(context, "sleep_state_left")
                self.tell_daddy(context, self.lang["sleep_state_left_summary"].replace("NUM_MISSED_MESSAGES", str(self.missed_messages)), raw=True)
                #TODO: Tell who sent you a fax
                self.missed_messages = 0
                self.printer.flushqueue()
                self.asleep = False
            else:
                self.tell_daddy(context, "sleep_state_entered")
                self.asleep = True
        else:
            self.send_message(update, context, "unauthorized")


    def handle(self, update, context):
        if self.state.startswith("register") and self.accesslevel(update.effective_chat.id) == 2:
            self.register(update, context)

        else:
            if self.accesslevel(update.effective_chat.id) >= 1:
                self.handle_print(update, context)
            elif self.accesslevel(update.effective_chat.id) == 0:
                self.send_message(update, context, "request_reply_unknown_user")
                self.tell_daddy(context, str(update.effective_chat.first_name) + " (ID "+str(update.effective_chat.id)+") " + self.lang["print_attempt"], raw=True)
                self.handle_print(update, context, tentative=True)
            elif self.accesslevel(update.effective_chat.id) == -1:
                self.send_message(update, context, "request_reply_blocked_user") #HAHA LOSER
        
    def handle_print(self, update, context, tentative=False):
        try:
            newFile = context.bot.get_file(update.message.sticker.file_id)
            r = self.printer.new_job(newFile, doctype="photo", user_id=update.effective_chat.id)
        except AttributeError:
            pass
        
        try:
            newFile = context.bot.get_file(update.message.photo[-1].file_id)
            r = self.printer.new_job(newFile, doctype="photo", caption=update.message.caption, user_id=update.effective_chat.id)
        except (IndexError, AttributeError):
            pass

        if fileExtenstion(update) == "doc":
            newFile = context.bot.get_file(update.message.document.file_id)
            r = self.printer.new_job(newFile, doctype="doc", user_id=update.effective_chat.id)
        elif  fileExtenstion(update) == "docx":
            newFile = context.bot.get_file(update.message.document.file_id)
            r = self.printer.new_job(newFile, doctype="docx", user_id=update.effective_chat.id)
        elif  fileExtenstion(update) == "png":
            newFile = context.bot.get_file(update.message.document.file_id)
            r = self.printer.new_job(newFile, doctype="photo", user_id=update.effective_chat.id)
        elif fileExtenstion(update) == "no_extension":
            r = True,
        
        if not "r" in locals():
            r = self.printer.new_job(update.message.text, doctype="text", user_id=update.effective_chat.id)

        if not r[0]:
            if not tentative:
                self.send_message(update, context, "print_started")
            
            self.db.table("users").update(tdop.increment("N"), Query().id == str(update.effective_chat.id))

            if not self.asleep:
                self.printer.flushqueue()
            else:
                self.missed_messages += 1 
        else:
            if not tentative:
                self.send_message(update, context, "print_failed")

    def register(self, update, context):
        if self.accesslevel(update.effective_chat.id) != 2:
            self.send_message(update, context, "register_unauthorized")
            return

        if self.state == "register":
            reply_markup = telegram.ReplyKeyboardRemove()
            if update.message.text == self.lang["register_allow"]:
                self.tell_daddy(context, "register_allow_who", reply_markup=reply_markup)
                self.state = "register_allow"
            elif update.message.text == self.lang["register_block"]:
                self.tell_daddy(context, "register_block_who", reply_markup=reply_markup)
                self.state = "register_block"
            elif update.message.text == self.lang["register_remove"]:
                self.tell_daddy(context, "register_remove_who", reply_markup=reply_markup)
                self.state = "register_remove"

        elif self.state == "register_allow":
            r = self.send_message(update, context, "register_granted", direct_id=update.message.text)
            if not r[0]:
                self.moduser(str(update.effective_chat.full_name), str(update.effective_chat.id), "user")
                self.tell_daddy(context, "register_allow_success")
            else:
                self.tell_daddy(context, r[1])
            self.state = "normal"

        elif self.state == "register_block":
            r = self.send_message(update, context, "register_denied", direct_id=update.message.text)
            if not r[0]:
                self.moduser(str(update.effective_chat.full_name), str(update.effective_chat.id), "blocked")
                self.tell_daddy(context, "register_block_success")
            else:
                self.tell_daddy(context, r[1])
            self.state = "normal"

        elif self.state == "register_remove":
            self.deluser(str(update.effective_chat.id))
            self.tell_daddy(context, "register_remove_success")
            self.state = "normal"