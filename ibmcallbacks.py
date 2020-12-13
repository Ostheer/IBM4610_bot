import telegram
import ibmprint
import datetime
from tinydb import Query
import tinydb.operations as tdop
from tinydb import where

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
        #TODO: also check if name has been updated

        if len(r) == 0:
            #add new user
            t.insert({"name":name, "id":user_id, "type":utype, "added":nows(), "N":0})
            #remove from strangers
            self.db.table("strangers").remove(where("id") == user_id)
            return False,
        elif len(r) == 1:
            #user already registered
            if r[0]["type"] != utype:
                #check if we're not blocking the main admin
                if not user_id == self.cf["ADMIN"]["admin_id"]:
                    #update user type
                    t.update(tdop.set("type", utype), User.id == user_id)
                    return False,
                else:
                    return True, "register_block_error_admin"
        else:
            return True, "error_user_duplicate" #TODO: duplicate entry, should not occur, consider sending a warning
    
    def deluser(self, user_id):
        user_id = str(user_id)
        User = Query()
        t = self.db.table("users")
        r = t.search(User.id == user_id)

        if len(r) == 0:
            return True, "error_invalid_id"
        elif len(r) > 0:
            if not user_id == self.cf["ADMIN"]["admin_id"]:
                t.remove(User.id == user_id)
                return False,
            else:
                return True, "register_block_error_admin"
    
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
            return True, "error_sending_message_id"

        if not raw:
            try:
                tosend = self.lang[string]
            except KeyError:
                tosend = "Invalid key: " + string
        else:
            tosend = string

        try:
            if "reply_markup" in kwargs:
                context.bot.send_message(chat_id=id, text=tosend, reply_markup=kwargs["reply_markup"])
            else:
                context.bot.send_message(chat_id=id, text=tosend)
        except telegram.error.BadRequest:
            return True, "error_invalid_id"
        except:
            return True, "error_sending_message_general"
        
        return False,
        
    def tell_daddy(self, context, string, **kwargs):
        return self.send_message(None, context, string, direct_id=self.cf["ADMIN"]["admin_id"], **kwargs)


    def command_start(self, update, context):
        self.send_message(update, context, "start_reply")
        self.tell_daddy(context, str(update.effective_chat.first_name) + " (ID "+str(update.effective_chat.id)+") " + self.lang["start_request"], raw=True)
        self.db.table("strangers").insert({"name":str(update.effective_chat.first_name)+" "+str(update.effective_chat.last_name), "id":str(update.effective_chat.id)})
    
    def command_cancel(self, update, context):
        if self.accesslevel(update.effective_chat.id) == 2:
            if self.state != "normal":
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
                custom_keyboard.append(["/cancel"])
                reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                self.tell_daddy(context, "request_what", reply_markup=reply_markup)
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

    def command_database(self, update, context):
        if self.accesslevel(update.effective_chat.id) == 2:
            if self.state == "normal":
                custom_keyboard = [[self.lang["database_load"]], [self.lang["database_dump"]]]
                custom_keyboard.append(["/cancel"])
                reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                self.tell_daddy(context, "request_what", reply_markup=reply_markup)
                self.state = "database_modify"
        else:
            self.send_message(update, context, "unauthorized")
    
    def handle(self, update, context):
        if self.state.startswith("register") and self.accesslevel(update.effective_chat.id) == 2:
            self.register(update, context)

        elif self.state.startswith("database_modify") and self.accesslevel(update.effective_chat.id) == 2:
            self.modify_database(update, context)

        else:
            if self.accesslevel(update.effective_chat.id) >= 1:
                self.handle_print(update, context)
            elif self.accesslevel(update.effective_chat.id) == 0:
                self.send_message(update, context, "request_reply_unknown_user")
                self.tell_daddy(context, str(update.effective_chat.first_name) + " (ID "+str(update.effective_chat.id)+") " + self.lang["print_attempt"], raw=True)
                self.handle_print(update, context, tentative=True)
                self.db.table("strangers").insert({"name":str(update.effective_chat.first_name)+" "+str(update.effective_chat.last_name), "id":str(update.effective_chat.id)})
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
            mkb = lambda s: "Name: {0}\n ID: {1}".format(s["name"], s["id"])

            if update.message.text == self.lang["register_allow"]:
                self.tell_daddy(context, "register_allow_who", reply_markup=telegram.ReplyKeyboardRemove())
                users = self.db.table("strangers").all()
                users.extend(self.db.table("users").search(where("type") == "blocked"))
                custom_keyboard = [[mkb(users[i])] for i in range(len(users))]
                custom_keyboard.append(["/cancel"])
                self.tell_daddy(context, "register_allow_choose", reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard))
                self.state = "register_allow"
            elif update.message.text == self.lang["register_block"]:
                self.tell_daddy(context, "register_block_who", reply_markup=telegram.ReplyKeyboardRemove())
                users = self.db.table("strangers").all()
                users.extend(self.db.table("users").all())
                custom_keyboard = [[mkb(users[i])] for i in range(len(users))]
                custom_keyboard.append(["/cancel"])
                self.tell_daddy(context, "register_block_choose", reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard))
                self.state = "register_block"
            elif update.message.text == self.lang["register_remove"]:
                self.tell_daddy(context, "register_remove_who", reply_markup=telegram.ReplyKeyboardRemove())
                users = self.db.table("users").all()
                custom_keyboard = [[mkb(users[i])] for i in range(len(users))]
                custom_keyboard.append(["/cancel"])
                self.tell_daddy(context, "register_remove_choose", reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard))
                self.state = "register_remove"

        else:
            removekeyboard = telegram.ReplyKeyboardRemove()
            try:
                user_name = update.message.text.split("\n ID: ")[0].split("Name: ")[1].strip()
                user_id = update.message.text.split("\n ID: ")[1].strip()
            except IndexError:
                user_name = "Unknown"
                user_id = update.message.text.strip()

            if self.state == "register_allow":
                r = self.send_message(update, context, "register_granted", direct_id=user_id)
                if not r[0]:
                    self.moduser(str(user_name), str(user_id), "user")
                    self.tell_daddy(context, "register_allow_success", reply_markup=removekeyboard)
                else:
                    self.tell_daddy(context, r[1], reply_markup=removekeyboard)
                self.state = "normal"

            elif self.state == "register_block":
                r = self.moduser(str(user_name), str(user_id), "blocked")
                if not r[0]:
                    self.send_message(update, context, "register_denied", direct_id=user_id)
                    self.tell_daddy(context, "register_block_success", reply_markup=removekeyboard)
                else:
                    self.tell_daddy(context, r[1], reply_markup=removekeyboard)
                self.state = "normal"

            elif self.state == "register_remove":
                r = self.deluser(user_id)
                if not r[0]:
                    self.tell_daddy(context, "register_remove_success", reply_markup=removekeyboard)
                else:
                    self.tell_daddy(context, r[1], reply_markup=removekeyboard)
                self.state = "normal"
            else:
                self.command_cancel(update, context)
    
    def modify_database(self, update, context):
        def dump_db(self, update, context):
            if self.accesslevel(update.effective_chat.id) == 2:
                context.bot.send_document(chat_id=update.effective_chat.id, document=open(self.cf["ADMIN"]["database_file"], 'rb'))
        
        def load_db(self, update, context):
            if self.accesslevel(update.effective_chat.id) == 2:
                if fileExtenstion(update) == "json":
                    #TODO: check if JSON is valid
                    context.bot.get_file(update.message.document.file_id).download(self.cf["ADMIN"]["database_file"])
                    return False,
                else:
                    return True, "database_new_invalid"

        if self.accesslevel(update.effective_chat.id) != 2:
            self.send_message(update, context, "register_unauthorized")
            return

        if self.state == "database_modify":
            if update.message.text == self.lang["database_load"]:
                self.state = "database_modify_load"
                self.tell_daddy(context, "confirm_ask", reply_markup=telegram.ReplyKeyboardMarkup([[self.lang["confirm_pos"]], [self.lang["confirm_neg"]]]))    
            elif update.message.text == self.lang["database_dump"]:
                self.tell_daddy(context, "here_you_go", reply_markup=telegram.ReplyKeyboardRemove())
                dump_db(self, update, context)
                self.state = "normal"
            else:
                self.command_cancel(update, context)

        elif self.state == "database_modify_load":
            if update.message.text == self.lang["confirm_pos"]:
                self.state = "database_modify_load_confirmed"
            elif update.message.text == self.lang["confirm_neg"]:
                self.command_cancel(update, context)
            else:
                self.command_cancel(update, context)

        elif self.state == "database_modify_load_confirmed":
            r = load_db(self, update, context)
            if not r[0]:
                self.tell_daddy(context, "database_new_loaded", reply_markup=telegram.ReplyKeyboardRemove())
            else:
                self.tell_daddy(context, r[1], reply_markup=telegram.ReplyKeyboardRemove())
            self.state = "normal"
