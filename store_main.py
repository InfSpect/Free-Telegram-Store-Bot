from datetime import datetime, timedelta
import time
import logging
import telebot
from telebot import types
import random
import os
import os.path
import re
from html import escape as html_escape
from database import *
from purchase import *
from categories import *
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot connection
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
store_currency = os.getenv('STORE_CURRENCY', 'USD')

if not bot_token:
    logger.error("Missing required environment variable: TELEGRAM_BOT_TOKEN")
    exit(1)

bot = telebot.TeleBot(bot_token, threaded=False)

# Set up polling (no ngrok needed!)
logger.info("Shop Started! Using polling mode...")

# Create main keyboard
def create_main_keyboard():
    """Create the main user keyboard"""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    key1 = types.KeyboardButton(text="Shop Items")
    key2 = types.KeyboardButton(text="My Orders")
    key3 = types.KeyboardButton(text="Support")
    keyboard.add(key1)
    keyboard.add(key2, key3)
    return keyboard

keyboard = create_main_keyboard()


################## WELCOME MESSAGE + BUTTONS START #########################
#Function to list Products and Categories
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handle callback queries from inline keyboards"""
    try:
        if call.data.startswith("pay_accept_"):
            approve_manual_payment(call)
        elif call.data.startswith("pay_deny_"):
            deny_manual_payment(call)
        elif call.data.startswith("wallet_"):
            choose_payment_wallet(call)
        elif call.data.startswith("getcats_"):
            input_catees = call.data.replace('getcats_','')
            CategoriesDatas.get_category_products(call, input_catees)
        elif call.data.startswith("getproduct_"):
            input_cate = call.data.replace('getproduct_','')
            UserOperations.purchase_a_products(call, input_cate)
        elif call.data.startswith("managecats_"):
            input_cate = call.data.replace('managecats_','')
            manage_categoriesbutton(call, input_cate)
        else:
            logger.warning(f"Unknown callback data: {call.data}")
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        bot.send_message(call.message.chat.id, "An error occurred. Please try again.")


#Function to list Products
def is_product_command(message):
    """Check if message is a product command"""
    try:
        pattern = r'/\d{8}$'
        return bool(re.match(pattern, message))
    except Exception as e:
        logger.error(f"Error checking product command: {e}")
        return False
@bot.message_handler(content_types=["text"], func=lambda message: is_product_command(message.text))
def products_get(message):
    """Handle product selection"""
    try:
        product_id = message.text.lstrip("/")
        UserOperations.purchase_a_products(message, product_id)
    except Exception as e:
        logger.error(f"Error processing product selection: {e}")
        bot.send_message(message.chat.id, "Error processing your request. Please try again.")

# DANGEROUS COMMAND

# @bot.message_handler(commands=['addadmin'])
# def add_admin_command(message):
#     """Development-only command to add an admin."""
#     try:
#         requester_id = message.from_user.id
#         requester_username = message.from_user.username or message.from_user.first_name
#         admins = GetDataFromDB.GetAdminIDsInDB() or []
#         admin_ids = {int(admin[0]) for admin in admins}

#         if admin_ids and requester_id not in admin_ids:
#             bot.send_message(message.chat.id, "Only an existing admin can add another admin.")
#             return

#         command_parts = message.text.split()

#         if message.reply_to_message:
#             target_user = message.reply_to_message.from_user
#             admin_id = target_user.id
#             username = target_user.username or target_user.first_name
#         elif len(command_parts) >= 2:
#             try:
#                 admin_id = int(command_parts[1])
#             except ValueError:
#                 bot.send_message(message.chat.id, "Usage: /addadmin <telegram_id> [username]")
#                 return
#             username = command_parts[2].lstrip("@") if len(command_parts) >= 3 else None
#         else:
#             admin_id = requester_id
#             username = requester_username

#         username = username or str(admin_id)
#         if admin_id in admin_ids:
#             bot.send_message(message.chat.id, f"{username} ({admin_id}) is already an admin.")
#             return

#         CreateDatas.AddAdmin(admin_id, username)
#         bot.send_message(message.chat.id, f"Admin added: {username} ({admin_id})")
#     except Exception as e:
#         logger.error(f"Error adding admin from command: {e}")
#         bot.send_message(message.chat.id, "Error adding admin. Please try again.")

#Start command handler and function
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Home")
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Home")
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        try:
            id = message.from_user.id
            usname = message.chat.username
            admins = GetDataFromDB.GetAdminIDsInDB()
            user_s = GetDataFromDB.AllUsers()
            for a_user_s in user_s:
                all_user_s = a_user_s[0]
            admin_s = GetDataFromDB.AllAdmins()
            for a_admin_s in admin_s:
                all_admin_s = a_admin_s[0]
            product_s = GetDataFromDB.AllProducts()
            for a_product_s in product_s:
                all_product_s = a_product_s[0]
            orders_s = GetDataFromDB.AllOrders()
            for a_orders_s in orders_s:
                all_orders_s = a_orders_s[0]
            
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            
            if admins == []:
                users = GetDataFromDB.GetUserIDsInDB()
                if f"{id}" not in f"{users}":
                    CreateDatas.AddAuser(id,usname)
                user_type = "Shop Admin"
                CreateDatas.AddAdmin(id,usname)
                key0 = types.KeyboardButton(text="Manage Products")
                key1 = types.KeyboardButton(text="Manage Categories")
                key2 = types.KeyboardButton(text="Manage Orders")
                key3 = types.KeyboardButton(text="Payment Methods")
                key4 = types.KeyboardButton(text="News To Users")
                key5 = types.KeyboardButton(text="Switch To User")
                keyboardadmin.add(key0)
                keyboardadmin.add(key1, key2)
                keyboardadmin.add(key3, key4)
                keyboardadmin.add(key5)
                store_statistics = f"Store's Statistics \n\n\nTotal Users : {all_user_s}\n\nTotal Admins : {all_admin_s}\n\nTotal Products : {all_product_s}\n\nTotal Orders : {all_orders_s}\n\n\n"
                user_data = "0"
                bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/V5dLSjV/Untitled-design.png", caption=f"Dear {user_type},\n\nYour Wallet Balance: $ {user_data}  \n\n{store_statistics}", reply_markup=keyboardadmin)
            elif f"{id}" in f"{admins}":
                keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                keyboardadmin.row_width = 2
                users = GetDataFromDB.GetUserIDsInDB()
                if f"{id}" not in f"{users}":
                    CreateDatas.AddAuser(id,usname)
                user_type = "Shop Admin"
                key0 = types.KeyboardButton(text="Manage Products")
                key1 = types.KeyboardButton(text="Manage Categories")
                key2 = types.KeyboardButton(text="Manage Orders")
                key3 = types.KeyboardButton(text="Payment Methods")
                key4 = types.KeyboardButton(text="News To Users")
                key5 = types.KeyboardButton(text="Switch To User")
                keyboardadmin.add(key0)
                keyboardadmin.add(key1, key2)
                keyboardadmin.add(key3, key4)
                keyboardadmin.add(key5)

                store_statistics = f"Store's Statistics \n\n\nTotal Users : {all_user_s}\n\nTotal Admins : {all_admin_s}\n\nTotal Products : {all_product_s}\n\nTotal Orders : {all_orders_s}\n\n\n"
                user_data = "0"
                bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/V5dLSjV/Untitled-design.png", caption=f"Dear {user_type},\n\nWelcome! \n\n{store_statistics}", reply_markup=keyboardadmin)

            else:
                users = GetDataFromDB.GetUserIDsInDB()
                if f"{id}" in f"{users}":
                    user_type = "Customer"
                    user_data = GetDataFromDB.GetUserWalletInDB(id)
                else:
                    CreateDatas.AddAuser(id,usname)
                    user_type = "Customer"
                    user_data = GetDataFromDB.GetUserWalletInDB(id)
                bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/V5dLSjV/Untitled-design.png", caption=f"Dear {user_type},\n\nWelcome! \n\nBrowse our products, make purchases, and enjoy fast delivery! \nType /browse to start shopping. \n\n Need help? \nContact our support team anytime.", reply_markup=keyboard)
        except Exception as e:
            print(e)
            admin_switch_user(message)
    except Exception as e:
        print(e)
        
#Switch admin to user handler
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Switch To User")
def admin_switch_user(message):
    id = message.from_user.id
    usname = message.chat.username
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    
    users = GetDataFromDB.GetUserIDsInDB()
    if f"{id}" in f"{users}":
        user_type = "Customer"
        key1 = types.KeyboardButton(text="Shop Items")
        key2 = types.KeyboardButton(text="My Orders")
        key3 = types.KeyboardButton(text="Support")
        key4 = types.KeyboardButton(text="Home")
        keyboard.add(key1)
        keyboard.add(key2, key3)
        keyboard.add(key4)
        user_data = GetDataFromDB.GetUserWalletInDB(id)
    else:
        CreateDatas.AddAuser(id,usname)
        user_type = "Customer"
        key1 = types.KeyboardButton(text="Shop Items")
        key2 = types.KeyboardButton(text="My Orders")
        key3 = types.KeyboardButton(text="Support")
        key4 = types.KeyboardButton(text="Home")
        keyboard.add(key1)
        keyboard.add(key2, key3)
        keyboard.add(key4)
        user_data = GetDataFromDB.GetUserWalletInDB(id)
    bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/V5dLSjV/Untitled-design.png", caption=f"Dear {user_type},\n\nYour Wallet Balance: $ {user_data}  \n\nBrowse our products, make purchases, and enjoy fast delivery! \nType /browse to start shopping. \n\n Need help? \nContact our support team anytime.", reply_markup=keyboard)
    bot.send_message(id, "You are on User Mode \nSend /start command or press Home button to switch back to Admin Mode", reply_markup=keyboard)

#Command handler to manage products
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Manage Products")
def ManageProducts(message):
    id = message.from_user.id
    name = message.from_user.first_name
    usname = message.chat.username
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="Add New Product")
        key2 = types.KeyboardButton(text="List Product")
        key3 = types.KeyboardButton(text="Delete Product")
        key4 = types.KeyboardButton(text="Home")
        keyboardadmin.add(key1)
        keyboardadmin.add(key2, key3)
        keyboardadmin.add(key4)

        bot.send_message(id, "Choose an action to perform.", reply_markup=keyboardadmin)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Command handler to add product
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Add New Product")
def AddProductsMNG(message):
    id = message.from_user.id
    name = message.from_user.first_name
    usname = message.chat.username
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        msg = bot.send_message(id, "Reply With Your Product Name or Title: ")
        new_product_number = random.randint(10000000,99999999)
        productnumber = f"{new_product_number}"
        CreateDatas.AddProduct(productnumber, id, usname)
        global productnumbers
        productnumbers = productnumber
        bot.register_next_step_handler(msg, add_a_product_name)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product name
def add_a_product_name(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        try:
            id = message.from_user.id
            productname = message.text
            msg = bot.send_message(id, "Reply With Your Product Description: ")
            CreateDatas.UpdateProductName(productname, productnumbers)
            bot.register_next_step_handler(msg, add_a_product_decription)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, add_a_product_name)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product describtion
def add_a_product_decription(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        try:
            id = message.from_user.id
            description = message.text
            msg = bot.send_message(id, "Reply With Your Product Price: ")
            CreateDatas.UpdateProductDescription(description, productnumbers)
            bot.register_next_step_handler(msg, add_a_product_price)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, add_a_product_decription)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product price
def add_a_product_price(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        try:
            id = message.from_user.id
            price = message.text
            msg = bot.send_message(id, "Attach Your Product Photo: ")
            CreateDatas.UpdateProductPrice(price, productnumbers)
            bot.register_next_step_handler(msg, add_a_product_photo_link)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, add_a_product_price)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product photo
def add_a_product_photo_link(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        try:
            id = message.from_user.id
            if message.photo:
                image_link = message.photo[-1].file_id
            elif message.text and message.text.startswith(("http://", "https://")):
                image_link = message.text.strip()
            else:
                msg = bot.send_message(id, "Please send a product photo or an image URL that starts with http:// or https://")
                bot.register_next_step_handler(msg, add_a_product_photo_link)
                return
            all_categories = GetDataFromDB.GetCategoryIDsInDB()
            if all_categories == []:
                msg = bot.send_message(id, "Please reply with a new category's name")
                CreateDatas.UpdateProductproductimagelink(image_link, productnumbers)
                bot.register_next_step_handler(msg, add_a_product_category)
            else:
                bot.send_message(id, f"CATEGORIES ")
                for catnum, catname in all_categories:
                    bot.send_message(id, f"{catname} - ID: /{catnum} ")

                msg = bot.send_message(id, "Click on a Category ID to select Category for this Product: \n\nOr Write A New Category", reply_markup=types.ReplyKeyboardRemove())
                CreateDatas.UpdateProductproductimagelink(image_link, productnumbers)
                bot.register_next_step_handler(msg, add_a_product_category)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, add_a_product_photo_link)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product category
def add_a_product_category(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        id = message.from_user.id
        input_cat = message.text
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        input_cate = input_cat[1:99]

        categories = []
        for catnum, catname in all_categories:
            catnames = catname.upper()
            categories.append(catnames)
            
        def checkint():
            try:
                input_cat = int(input_cate)
                return input_cat
            except:
                return input_cate

        input_category = checkint() 
        if isinstance(input_category, int) == True:
            product_cate = GetDataFromDB.Get_A_CategoryName(input_category)
            product_category = product_cate.upper()
            if f"{product_category}" not in f"{categories}" or f"{product_category}" == "NONE":
                msg = bot.send_message(id, "Please reply with a new category's name", reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, add_a_product_category)
            elif f"{product_category}" in f"{categories}":
                msg = bot.send_message(id, "Attach Your Producy Keys In A Text File: \n\n Please Arrange Your Product Keys In the Text File, One Product Key Per Line In The File\n\n\n Reply With Skip to skip this step if this Product has no Product Keys")
                CreateDatas.UpdateProductCategory(product_category, productnumbers)
                bot.register_next_step_handler(msg, add_a_product_keys_file)
        else:
            new_category_number = random.randint(1000,9999)
            input_cate = input_cat.upper()
            CreateDatas.AddCategory(new_category_number, input_cate)
            bot.send_message(id, f"New Category created successfully  - {input_cat}")
            msg = bot.send_message(id, "Attach Your Producy Keys In A Text File: \n\n Please Arrange Your Product Keys In the Text File, One Product Key Per Line In The File\n\n\n Reply With Skip to skip this step if this Product has no Product Keys")
            CreateDatas.UpdateProductCategory(input_cate, productnumbers)
            bot.register_next_step_handler(msg, add_a_product_keys_file)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product file for keys
def add_a_product_keys_file(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        try:
            id = message.from_user.id
            if message.text and message.text.upper() == "SKIP":
                msg = bot.send_message(id, "Reply With Download Link For This Product\n\nThis will be the Link customer will have access to after they have paid: \n\n\n Reply With Skip to skip this step if this Product has no Product Download Link")
                bot.register_next_step_handler(msg, add_a_product_download_link)
            elif message.document:
                keys_folder = "Keys"
                if not "Keys" in  os.listdir():
                    try:
                        os.mkdir("Keys")
                    except Exception as e:
                        print(e)
                else:
                    pass
                KeysFiles = f"{keys_folder}/{productnumbers}.txt"
                file = message.document
                file_info = bot.get_file(file.file_id)
                file_path = file_info.file_path
                file_name = os.path.join(f"{KeysFiles}")
                downloaded_file = bot.download_file(file_path)
                with open(file_name, 'wb') as new_file:
                    new_file.write(downloaded_file)
                bot.reply_to(message, f'File f"{productnumbers}.txt" saved successfully.')
                CreateDatas.UpdateProductKeysFile(KeysFiles, productnumbers)
                quantity = open(file_name, 'r').read().splitlines()
                with open(file_name, 'r') as all:
                    all_quantity = all.read()
                all_quantities = len(all_quantity.split('\n'))
                CreateDatas.UpdateProductQuantity(all_quantities, productnumbers)
                msg = bot.send_message(id, "Reply With Download Link For This Product\n\nThis will be the Link customer will have access to after they have paid: \n\n\n Reply With Skip to skip this step if this Product has no Product Download Link")
                bot.register_next_step_handler(msg, add_a_product_download_link)
            else:
                msg = bot.send_message(id, "Error 404, try again with corrected input.")
                bot.register_next_step_handler(msg, add_a_product_keys_file)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, add_a_product_keys_file)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Function to add product download link
def add_a_product_download_link(message):
    try:
        id = message.from_user.id
        download_link = message.text
        if message.text and message.text.upper() == "SKIP":
            bot.send_message(id, "Download Link Skipped ")
        else:
            CreateDatas.UpdateProductproductdownloadlink(download_link, productnumbers)
            CreateDatas.UpdateProductQuantity(int(100), productnumbers)
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="Add New Product")
        key2 = types.KeyboardButton(text="List Product")
        key3 = types.KeyboardButton(text="Delete Product")
        key4 = types.KeyboardButton(text="Home")
        keyboardadmin.add(key1)
        keyboardadmin.add(key2, key3)
        keyboardadmin.add(key4)
        productimage = GetDataFromDB.GetProductImageLink(productnumbers)
        productname = GetDataFromDB.GetProductName(productnumbers)
        productnumber = GetDataFromDB.GetProductNumber(productnumbers)
        productdescription = GetDataFromDB.GetProductDescription(productnumbers)
        productprice = GetDataFromDB.GetProductPrice(productnumbers)
        productquantity = GetDataFromDB.GetProductQuantity(productnumbers)
        captions = f"\n\n\nProduct Tittle: {productname}\n\n\nProduct Number: `{productnumber}`\n\n\nProduct Price: {productprice} {store_currency} \n\n\nQuantity Available: {productquantity} \n\n\nProduct Description: {productdescription}"
        bot.send_photo(chat_id=message.chat.id, photo=f"{productimage}", caption=f"{captions}", parse_mode='Markdown')
        bot.send_message(id, "Product Successfully Added.\n\nWhat will you like to do next ?", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_download_link)

#Command handler and functions to delete product
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Delete Product")
def DeleteProductsMNG(message):
    try:
        id = message.from_user.id
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        productnumber_name = GetDataFromDB.GetProductNumberName()
        if f"{id}" in f"{admins}":
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row_width = 2
            if productnumber_name ==  []:
                msg = bot.send_message(id, "No product available, please send /start command to start creating products")
                bot.register_next_step_handler(msg, send_welcome)
            else:
                bot.send_message(id, f"Product ID --- Product Name")
                for pid, tittle in productnumber_name:
                    bot.send_message(id, f"/{pid} - `{tittle}`", parse_mode="Markdown")
                msg = bot.send_message(id, "Click on a Product ID of the product you want to delete: ", parse_mode="Markdown")
                bot.register_next_step_handler(msg, delete_a_product)
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        pass
def delete_a_product(message):
    #try:
    id = message.from_user.id
    productnu = message.text
    productnumber = productnu[1:99]
    productnum = GetDataFromDB.GetProductIDs()
    productnums = []
    for productn in productnum:
        productnums.append(productn[0])
    print(productnums)
    if int(productnumber) in productnums:
        try:
            global productnumbers
            productnumbers = productnumber
        except Exception as e:
            print(e)
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        if f"{id}" in f"{admins}":
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            key1 = types.KeyboardButton(text="Add New Product")
            key2 = types.KeyboardButton(text="List Product")
            key3 = types.KeyboardButton(text="Delete Product")
            key4 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1)
            keyboardadmin.add(key2, key3)
            keyboardadmin.add(key4)
            CleanData.delete_a_product(productnumber)
            msg = bot.send_message(id, "Deleted successfully.\n\n\nWhat will you like to do next ?\n\nSelect one of buttons ", reply_markup=keyboardadmin, parse_mode="Markdown")
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    else:
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, delete_a_product)
        pass
    #except Exception as e:
        #print(e)
        #msg = bot.send_message(id, "Error 404, try again with corrected input.")
        #bot.register_next_step_handler(msg, delete_a_product)
        #pass

#Command handler and fucntion to shop Items
@bot.message_handler(commands=['browse'])
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Shop Items")
def shop_items(message):
    UserOperations.shop_items(message)


# Manual crypto payment flow
pending_receipt_orders = {}
MAX_RECEIPT_SIZE = int(os.getenv("MAX_RECEIPT_SIZE_MB", "5")) * 1024 * 1024
RECEIPT_FOLDER = os.getenv("RECEIPT_FOLDER", "receipts")
ALLOWED_RECEIPT_MAGIC = {
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".png": [b"\x89PNG\r\n\x1a\n"],
    ".webp": [b"RIFF"],
}


def get_payment_wallets():
    wallet_config = os.getenv("PAYMENT_WALLETS", "")
    wallets = []
    for raw_wallet in wallet_config.split(";"):
        parts = [part.strip() for part in raw_wallet.split("|")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            continue
        wallets.append({
            "label": parts[0],
            "address": parts[1],
            "qr_path": parts[2] if len(parts) >= 3 and parts[2] else None,
        })
    return wallets


def display_value(value):
    if value is None:
        return ""
    value = str(value).strip()
    if value.upper() in {"", "NIL", "NONE", "NO", "HTTPS://NIL.NIL"}:
        return ""
    return value


def html_bold(label, value):
    clean_value = display_value(value)
    if not clean_value:
        return None
    return f"<b>{html_escape(label)}:</b> {html_escape(clean_value)}"


def create_payment_keyboard():
    payment_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    payment_keyboard.row_width = 2
    payment_keyboard.add(types.KeyboardButton(text="I Paid"))
    payment_keyboard.add(types.KeyboardButton(text="Home"))
    return payment_keyboard


def create_wallet_choice_keyboard(wallets):
    wallet_keyboard = types.InlineKeyboardMarkup()
    for index, wallet in enumerate(wallets):
        wallet_keyboard.add(types.InlineKeyboardButton(
            text=f"Pay with {wallet['label']}",
            callback_data=f"wallet_{index}"
        ))
    return wallet_keyboard


def get_pending_receipt_order(user_id):
    pending = pending_receipt_orders.get(user_id)
    if pending:
        return pending
    pending_orders = GetDataFromDB.GetPendingReceiptOrdersUser(user_id)
    if not pending_orders:
        return None
    ordernumber, payment_deadline = pending_orders[-1]
    return {"ordernumber": ordernumber, "expires_at": payment_deadline}


def payment_deadline_passed(pending):
    expires_at = pending.get("expires_at")
    if not expires_at:
        return False
    try:
        return datetime.now() > datetime.fromisoformat(expires_at)
    except ValueError:
        return False


def receipt_extension(file_name):
    _, extension = os.path.splitext(file_name or "")
    return extension.lower()


def receipt_is_safe(file_path, extension):
    if extension not in ALLOWED_RECEIPT_MAGIC:
        return False
    if os.path.getsize(file_path) > MAX_RECEIPT_SIZE:
        return False
    with open(file_path, "rb") as file:
        header = file.read(16)
    if extension == ".webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    return any(header.startswith(signature) for signature in ALLOWED_RECEIPT_MAGIC[extension])


def save_receipt_file(message, ordernumber):
    if message.content_type == "photo":
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name = f"{ordernumber}.jpg"
    elif message.content_type == "document":
        document = message.document
        file_name = document.file_name or f"{ordernumber}"
        file_info = bot.get_file(document.file_id)
    else:
        raise ValueError("Please send a receipt screenshot as a photo or image file.")

    if getattr(file_info, "file_size", 0) and file_info.file_size > MAX_RECEIPT_SIZE:
        raise ValueError("Receipt file is too large.")

    extension = receipt_extension(file_name)
    if extension not in ALLOWED_RECEIPT_MAGIC:
        raise ValueError("Receipt must be JPG, PNG, or WEBP.")

    os.makedirs(RECEIPT_FOLDER, exist_ok=True)
    receipt_path = os.path.join(RECEIPT_FOLDER, f"{ordernumber}_{message.from_user.id}{extension}")
    downloaded_file = bot.download_file(file_info.file_path)
    with open(receipt_path, "wb") as file:
        file.write(downloaded_file)

    if not receipt_is_safe(receipt_path, extension):
        try:
            os.remove(receipt_path)
        except OSError:
            pass
        raise ValueError("Receipt file failed security checks.")
    return receipt_path


def take_product_key(productnumber):
    keys_location = os.path.join("Keys", f"{productnumber}.txt")
    try:
        with open(keys_location, "r", encoding="utf-8") as file:
            keys = [line.strip() for line in file.readlines() if line.strip()]
        if not keys:
            return "NIL"
        product_key = keys[0]
        with open(keys_location, "w", encoding="utf-8") as file:
            for key in keys[1:]:
                file.write(f"{key}\n")
        return product_key
    except OSError:
        return "NIL"


def build_order_message(order_details, title="YOUR ORDER"):
    buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber = order_details
    lines = [
        f"<b>{html_escape(title)}</b>",
        "",
        html_bold("Order ID", ordernumber),
        html_bold("Order Date", orderdate),
        html_bold("Product", productname),
        html_bold("Product ID", productnumber),
        html_bold("Price", f"{productprice} {store_currency}"),
        html_bold("Payment", paidmethod),
        html_bold("Product Keys", productkeys),
        html_bold("Download", productdownloadlink),
    ]
    return "\n".join(line for line in lines if line is not None)


def notify_admins_for_payment(ordernumber, receipt_path):
    order_details = GetDataFromDB.GetOrderDetailsAnyStatus(ordernumber)
    if not order_details:
        return
    details = order_details[0]
    buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber = details
    admin_keyboard = types.InlineKeyboardMarkup()
    admin_keyboard.add(
        types.InlineKeyboardButton(text="Accept", callback_data=f"pay_accept_{ordernumber}"),
        types.InlineKeyboardButton(text="Deny", callback_data=f"pay_deny_{ordernumber}")
    )
    msg = (
        "Payment receipt needs review\n\n"
        f"Order ID: {ordernumber}\n"
        f"Buyer: @{buyerusername or buyerid}\n"
        f"Product: {productname}\n"
        f"Amount: {productprice} {store_currency}\n"
        "Status: awaiting admin approval"
    )
    admins = GetDataFromDB.GetAdminIDsInDB() or []
    for admin in admins:
        admin_id = admin[0]
        try:
            with open(receipt_path, "rb") as receipt:
                bot.send_photo(admin_id, receipt, caption=msg, reply_markup=admin_keyboard)
        except Exception:
            bot.send_message(admin_id, msg, reply_markup=admin_keyboard)


def fulfill_order(ordernumber):
    order_details = GetDataFromDB.GetOrderDetailsAnyStatus(ordernumber)
    if not order_details:
        return False

    details = order_details[0]
    buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber = details
    product_key = take_product_key(productnumber)
    CreateDatas.UpdateOrderPurchasedKeys(product_key, ordernumber)
    CreateDatas.UpdateOrderPaymentMethod("Manual Crypto", ordernumber)
    CreateDatas.UpdateOrderReviewStatus("approved", ordernumber)

    product_list = GetDataFromDB.GetProductInfoByPName(productnumber)
    if product_list:
        productquantity = product_list[0][6]
        try:
            CreateDatas.UpdateProductQuantity(max(int(productquantity) - 1, 0), productnumber)
        except (TypeError, ValueError):
            pass

    completed_details = GetDataFromDB.GetOrderDetailsAnyStatus(ordernumber)[0]
    bot.send_message(buyerid, "Payment approved. Your order is complete.")
    bot.send_message(buyerid, build_order_message(completed_details), reply_markup=keyboard, parse_mode="HTML")
    return True


def approve_manual_payment(call):
    ordernumber = call.data.replace("pay_accept_", "")
    review_status = GetDataFromDB.GetOrderReviewStatus(ordernumber)
    if review_status == "approved":
        bot.answer_callback_query(call.id, "Already approved.")
        return
    if fulfill_order(ordernumber):
        bot.answer_callback_query(call.id, "Payment approved.")
        bot.send_message(call.message.chat.id, f"Order {ordernumber} approved.")
    else:
        bot.answer_callback_query(call.id, "Order not found.")


def deny_manual_payment(call):
    ordernumber = call.data.replace("pay_deny_", "")
    order_details = GetDataFromDB.GetOrderDetailsAnyStatus(ordernumber)
    if not order_details:
        bot.answer_callback_query(call.id, "Order not found.")
        return
    buyerid = order_details[0][0]
    CreateDatas.UpdateOrderReviewStatus("denied", ordernumber)
    bot.answer_callback_query(call.id, "Payment denied.")
    bot.send_message(call.message.chat.id, f"Order {ordernumber} denied.")
    bot.send_message(buyerid, f"Your receipt for order {ordernumber} was denied. Contact support if this is a mistake.", reply_markup=keyboard)


def create_manual_order(user_id, username, order_info):
    ordernumber = random.randint(10000, 99999)
    while GetDataFromDB.GetOrderDetailsAnyStatus(ordernumber):
        ordernumber = random.randint(10000, 99999)

    orderdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    productdownloadlink = GetDataFromDB.GetProductDownloadLink(order_info[0])
    CreateDatas.AddOrder(
        user_id,
        username,
        order_info[1],
        order_info[2],
        orderdate,
        "NO",
        productdownloadlink,
        "NIL",
        ordernumber,
        order_info[0],
        f"manual-{ordernumber}"
    )
    CreateDatas.UpdateOrderReviewStatus("awaiting_receipt", ordernumber)
    deadline = datetime.now() + timedelta(minutes=30)
    CreateDatas.UpdateOrderPaymentDeadline(deadline.isoformat(timespec="seconds"), ordernumber)
    return ordernumber, deadline


def send_wallet_payment_instructions(user_id, ordernumber, deadline, order_info, wallet):
    pending_receipt_orders[user_id] = {
        "ordernumber": ordernumber,
        "expires_at": deadline.isoformat(timespec="seconds"),
        "wallet": wallet["label"]
    }
    payment_text = (
        f"<b>Order {html_escape(str(ordernumber))}</b>\n\n"
        f"<b>Amount:</b> {html_escape(str(order_info[2]))} {html_escape(store_currency)}\n"
        f"<b>Wallet:</b> {html_escape(wallet['label'])}\n"
        f"<b>Time limit:</b> 30 minutes, until {html_escape(deadline.strftime('%H:%M'))}\n\n"
        f"<b>Address</b>\n<code>{html_escape(wallet['address'])}</code>\n\n"
        "After payment, press <b>I Paid</b> and send a receipt screenshot."
    )
    qr_path = wallet.get("qr_path")
    if qr_path and os.path.exists(qr_path):
        with open(qr_path, "rb") as qr_file:
            bot.send_photo(
                user_id,
                qr_file,
                caption=payment_text,
                reply_markup=create_payment_keyboard(),
                parse_mode="HTML"
            )
        return

    bot.send_message(user_id, payment_text, reply_markup=create_payment_keyboard(), parse_mode="HTML")


@bot.message_handler(content_types=["text"], func=lambda message: message.text.startswith("Bitcoin"))
def bitcoin_pay_command(message):
    user_id = message.from_user.id
    wallets = get_payment_wallets()
    order_info = UserOperations.orderdata()

    if not order_info:
        bot.send_message(user_id, "No order found.", reply_markup=keyboard)
        return
    if int(f"{order_info[6]}") < 1:
        bot.send_message(user_id, "This item is sold out.", reply_markup=keyboard)
        return
    if not wallets:
        bot.send_message(user_id, "Payment wallets are not configured yet. Please contact support.", reply_markup=keyboard)
        return

    bot.send_message(
        user_id,
        "<b>Choose a payment wallet</b>\n\nSelect one wallet for this order.",
        reply_markup=create_wallet_choice_keyboard(wallets),
        parse_mode="HTML"
    )


def choose_payment_wallet(call):
    user_id = call.from_user.id
    username = call.from_user.username
    wallets = get_payment_wallets()
    order_info = UserOperations.orderdata()

    try:
        wallet_index = int(call.data.replace("wallet_", ""))
        wallet = wallets[wallet_index]
    except (ValueError, IndexError):
        bot.answer_callback_query(call.id, "Wallet is not available.")
        return

    pending = get_pending_receipt_order(user_id)
    if pending and not payment_deadline_passed(pending):
        bot.answer_callback_query(call.id, "You already have a pending payment.")
        bot.send_message(user_id, "You already have a pending payment. Press I Paid after sending payment, or wait for the window to expire.", reply_markup=create_payment_keyboard())
        return

    if not order_info:
        bot.answer_callback_query(call.id, "No order found.")
        bot.send_message(user_id, "No order found. Please choose the product again.", reply_markup=keyboard)
        return
    if int(f"{order_info[6]}") < 1:
        bot.answer_callback_query(call.id, "Sold out.")
        bot.send_message(user_id, "This item is sold out.", reply_markup=keyboard)
        return

    ordernumber, deadline = create_manual_order(user_id, username, order_info)
    bot.answer_callback_query(call.id, f"{wallet['label']} selected.")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except Exception:
        pass
    send_wallet_payment_instructions(user_id, ordernumber, deadline, order_info, wallet)


@bot.message_handler(content_types=["text"], func=lambda message: message.text == "I Paid")
def ask_for_receipt(message):
    pending = get_pending_receipt_order(message.from_user.id)
    if not pending:
        bot.send_message(message.chat.id, "No pending payment found. Please start checkout again.", reply_markup=keyboard)
        return
    if payment_deadline_passed(pending):
        CreateDatas.UpdateOrderReviewStatus("expired", pending["ordernumber"])
        pending_receipt_orders.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "This payment window has expired. Please start checkout again.", reply_markup=keyboard)
        return
    msg = bot.send_message(message.chat.id, "Send the payment receipt screenshot now. JPG, PNG, or WEBP only. Max 5 MB.", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, receive_payment_receipt)


def receive_payment_receipt(message):
    pending = get_pending_receipt_order(message.from_user.id)
    if not pending:
        bot.send_message(message.chat.id, "No pending payment found.", reply_markup=keyboard)
        return
    ordernumber = pending["ordernumber"]
    if payment_deadline_passed(pending):
        CreateDatas.UpdateOrderReviewStatus("expired", ordernumber)
        pending_receipt_orders.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "This payment window has expired. Please start checkout again.", reply_markup=keyboard)
        return
    try:
        receipt_path = save_receipt_file(message, ordernumber)
    except ValueError as e:
        msg = bot.send_message(message.chat.id, f"{e}\nPlease send another receipt screenshot.")
        bot.register_next_step_handler(msg, receive_payment_receipt)
        return
    except Exception as e:
        logger.error(f"Error saving receipt for order {ordernumber}: {e}")
        bot.send_message(message.chat.id, "Could not save receipt. Please try again.", reply_markup=create_payment_keyboard())
        return

    CreateDatas.UpdateOrderReceipt(receipt_path, ordernumber)
    CreateDatas.UpdateOrderReviewStatus("awaiting_admin", ordernumber)
    pending_receipt_orders.pop(message.from_user.id, None)
    notify_admins_for_payment(ordernumber, receipt_path)
    bot.send_message(message.chat.id, f"Receipt received for order {ordernumber}. An admin will review it shortly.", reply_markup=keyboard)
#Command handler and function to List My Orders
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "My Orders")
def MyOrdersList(message):
    id = message.from_user.id
    
    
    my_orders = GetDataFromDB.GetOrderIDs_Buyer(id)
    if my_orders == [] or my_orders == "None":
        bot.send_message(id, "You have not completed any order yet, please purchase an Item now", reply_markup=keyboard)
    else:
        for my_order in my_orders:
            order_details = GetDataFromDB.GetOrderDetails(my_order[0])
            for order_detail in order_details:
                bot.send_message(
                    id,
                    text=build_order_message(order_detail, "YOUR ORDER"),
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

#Command handler and function to list Store Supports 
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Support")
def ContactSupport(message):
    id = message.from_user.id
    admin_usernames = GetDataFromDB.GetAdminUsernamesInDB()
    for usernames in admin_usernames:
        bot.send_message(id, f"Contact us @{usernames[0]}", reply_markup=keyboard)

#Command handler and function to add New Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Add New Category")
def AddNewCategoryMNG(message):
    try:
        id = message.from_user.id
        admins = GetDataFromDB.GetAdminIDsInDB()
        if f"{id}" in f"{admins}":
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row_width = 2
            msg = bot.send_message(id, "Reply with name you want to name your new category", reply_markup=keyboard)
            bot.register_next_step_handler(msg, manage_categories)
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, AddNewCategoryMNG)

#Command handler and function to List Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "List Categories")
def ListCategoryMNG(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        try:
            id = message.from_user.id
            all_categories = GetDataFromDB.GetCategoryIDsInDB()
            key1 = types.KeyboardButton(text="Add New Category")
            key2 = types.KeyboardButton(text="List Categories")
            key3 = types.KeyboardButton(text="Edit Category Name")
            key4 = types.KeyboardButton(text="Delete Category")
            key5 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1, key2)
            keyboardadmin.add(key3, key4)
            keyboardadmin.add(key5)
            if all_categories == []:
                msg = bot.send_message(id, "No Category in your Store !!!", reply_markup=keyboardadmin)
            else:
                keyboardadmin = types.InlineKeyboardMarkup()
                for catnum, catname in all_categories:
                    text_but = f" {catname}"
                    text_cal = f"listcats_{catnum}"
                    keyboardadmin.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
                bot.send_message(id, f"List of Categories:", reply_markup=keyboardadmin)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, ManageCategoryMNG)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Command handler and function to Delete Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Delete Category")
def AddNewCategoryMNG(message):
    try:
        id = message.from_user.id
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        if f"{id}" in f"{admins}":
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            key1 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1)
            try:
                nen_category_name = "Deleted"
                try:
                    CreateDatas.Update_All_ProductCategory(nen_category_name, product_cate)
                except Exception as e:
                    print(e)
                product_cate = GetDataFromDB.Get_A_CategoryName(category_number)
                msg = bot.send_message(id, f"{product_cate} successfully deleted ", reply_markup=keyboardadmin)
                CleanData.delete_a_category(category_number)
                bot.register_next_step_handler(msg, send_welcome)

            except:
                msg = bot.send_message(id, "Category not found !!!", reply_markup=keyboardadmin)
                bot.register_next_step_handler(msg, send_welcome)

        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, AddNewCategoryMNG)

#Command handler and functions to Edit Category Name
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Edit Category Name")
def EditCategoryNameMNG(message):
    try:
        id = message.from_user.id
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        if f"{id}" in f"{admins}":
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            key1 = types.KeyboardButton(text="Add New Category")
            key2 = types.KeyboardButton(text="List Categories")
            key4 = types.KeyboardButton(text="Delete Category")
            key5 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1, key2)
            keyboardadmin.add(key4)
            keyboardadmin.add(key5)
            try:
                product_cate = GetDataFromDB.Get_A_CategoryName(category_number)
                msg = bot.send_message(id, f"Current Category's Name: {product_cate} \n\n\nReply with your new Category's name")
                bot.register_next_step_handler(msg, edit_a_category_name)
            except:
                msg = bot.send_message(id, "Category to edit not found !!!", reply_markup=keyboardadmin)
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, EditCategoryNameMNG)
def edit_a_category_name(message):
    try:
        id = message.from_user.id
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        if f"{id}" in f"{admins}":
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            key1 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1)
            try:
                nen_category_n = message.text
                nen_category_name = nen_category_n.upper()
                product_cate = GetDataFromDB.Get_A_CategoryName(category_number)
                try:
                    CreateDatas.Update_All_ProductCategory(nen_category_name, product_cate)
                except Exception as e:
                    print(e)
                CreateDatas.Update_A_Category(nen_category_name, category_number)
                msg = bot.send_message(id, "Category's name successfully updated: ", reply_markup=keyboardadmin)
                bot.register_next_step_handler(msg, send_welcome)

            except:
                msg = bot.send_message(id, "Category not found !!!", reply_markup=keyboardadmin)
                bot.register_next_step_handler(msg, send_welcome)
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, AddNewCategoryMNG)

#Command handler and function to Manage Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Manage Categories")
def ManageCategoryMNG(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        try:
            id = message.from_user.id
            all_categories = GetDataFromDB.GetCategoryIDsInDB()
            if all_categories == []:
                msg = bot.send_message(id, "No Category in your Store !!!\n\n\nPlease reply with a new category's name to create Category")
                bot.register_next_step_handler(msg, manage_categories)
            else:
                keyboardadmin = types.InlineKeyboardMarkup()
                for catnum, catname in all_categories:
                    text_but = f" {catname}"
                    text_cal = f"managecats_{catnum}"
                    keyboardadmin.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
                bot.send_message(id, f"List of Categories:", reply_markup=keyboardadmin)
                
                keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                keyboard1.row_width = 2
                key1 = types.KeyboardButton(text="Add New Category")
                key2 = types.KeyboardButton(text="Home")
                keyboard1.add(key1)
                keyboard1.add(key2)
                msg = bot.send_message(id, "Select Category you want to manage: \n\nOr Create new Category", reply_markup=keyboard1)
        except Exception as e:
            print(e)
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, ManageCategoryMNG)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

def manage_categories(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        input_cat = message.text
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        input_cate = input_cat
        categories = []
        for catnum, catname in all_categories:
            catnames = catname.upper()
            categories.append(catnames)

        def checkint():
            try:
                input_cat = int(input_cate)
                return input_cat
            except:
                return input_cate

        input_category = checkint() 
        if isinstance(input_category, int) == True:
            product_cate = GetDataFromDB.Get_A_CategoryName(input_category)
            product_category = product_cate.upper()
            if f"{product_category}" not in f"{categories}" or f"{product_category}" == "NONE":
                msg = bot.send_message(id, "Category not found !!!\n\n\nPlease reply with a new category's name to create category")
                bot.register_next_step_handler(msg, manage_categories)
            elif f"{product_category}" in f"{categories}":
                category_num = input_cate
                key1 = types.KeyboardButton(text="Add New Category")
                key2 = types.KeyboardButton(text="List Categories")
                key3 = types.KeyboardButton(text="Edit Category Name")
                key4 = types.KeyboardButton(text="Delete Category")
                key5 = types.KeyboardButton(text="Home")
                keyboardadmin.add(key1, key2)
                keyboardadmin.add(key3, key4)
                keyboardadmin.add(key5)
                bot.send_message(id, f"What will you like to do next ?", reply_markup=keyboardadmin)
        else:
            new_category_number = random.randint(1000,9999)
            input_cate = input_cat.upper()
            CreateDatas.AddCategory(new_category_number, input_cate)
            key1 = types.KeyboardButton(text="Add New Category")
            key2 = types.KeyboardButton(text="Manage Categories")
            key3 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1)
            keyboardadmin.add(key2)
            keyboardadmin.add(key3)
            bot.send_message(id, f"New Category {input_cat} created successfully\n\n\nWhat will you like to do next ?", reply_markup=keyboardadmin)
            category_num = new_category_number
        global category_number
        category_number = category_num

    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

def manage_categoriesbutton(message, input_c):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        id = message.from_user.id
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        input_cate = input_c
        categories = []
        for catnum, catname in all_categories:
            catnames = catname.upper()
            categories.append(catnames)
        input_category = input_cate
        product_cate = GetDataFromDB.Get_A_CategoryName(input_category)
        product_category = product_cate.upper()
        if f"{product_category}" not in f"{categories}" or f"{product_category}" == "NONE":
            msg = bot.send_message(id, "Category not found !!!\n\n\nPlease reply with a new category's name to create category")
            bot.register_next_step_handler(msg, manage_categoriesbutton)
        elif f"{product_category}" in f"{categories}":
            category_num = input_cate
            key1 = types.KeyboardButton(text="Add New Category")
            key2 = types.KeyboardButton(text="List Categories")
            key3 = types.KeyboardButton(text="Edit Category Name")
            key4 = types.KeyboardButton(text="Delete Category")
            key5 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1, key2)
            keyboardadmin.add(key3, key4)
            keyboardadmin.add(key5)
            bot.send_message(id, f"What will you like to do next ?", reply_markup=keyboardadmin)
            
        global category_number
        category_number = category_num
        print(category_number)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Command handler and function to List Product
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "List Product")
def LISTProductsMNG(message):
    id = message.from_user.id
    keyboarda = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboarda.row_width = 2
    admins = GetDataFromDB.GetAdminIDsInDB()
    productinfos = GetDataFromDB.GetProductInfos()
    if f"{id}" in f"{admins}":
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        if productinfos ==  []:
            msg = bot.send_message(id, "No product available, please send /start command to start creating products")
            bot.register_next_step_handler(msg, send_welcome)
        else:
            keyboard = types.InlineKeyboardMarkup()
            for pid, tittle, price in productinfos:
                text_but = f" {tittle} - {price} {store_currency}"
                text_cal = f"getproductig_{pid}"
                keyboard.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
            bot.send_message(id, f"List of Products: (JUST A LIST, NON CLICKABLE)", reply_markup=keyboard)
            key1 = types.KeyboardButton(text="Add New Product")
            key2 = types.KeyboardButton(text="List Product")
            key3 = types.KeyboardButton(text="Delete Product")
            key4 = types.KeyboardButton(text="Home")
            keyboarda.add(key1)
            keyboarda.add(key2, key3)
            keyboarda.add(key4)

    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Command handler and functions to  Message All Store Users
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "News To Users")
def MessageAllUsers(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        msg = bot.send_message(id, f"This Bot is about to Broadcast mesage to all Shop Users\n\n\nReply with the message you want to Broadcast: ")
        bot.register_next_step_handler(msg, message_all_users)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
def message_all_users(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}":
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        try:
            key1 = types.KeyboardButton(text="Manage Products")
            key2 = types.KeyboardButton(text="Manage Orders")
            key3 = types.KeyboardButton(text="Payment Methods")
            key4 = types.KeyboardButton(text="News To Users")
            key5 = types.KeyboardButton(text="Switch To User")
            keyboardadmin.add(key1, key2)
            keyboardadmin.add(key3, key4)
            keyboardadmin.add(key5)
            input_message = message.text
            all_users = GetDataFromDB.GetUsersInfo()
            if all_users ==  []:
                msg = bot.send_message(id, "No user available in your store, /start", reply_markup=keyboardadmin)
            else:
                bot.send_message(id, "Now Broadcasting Message To All Users: ")
                for uid, uname, uwallet in all_users:
                    try:
                        bot.send_message(uid, f"{input_message}")
                        bot.send_message(id, f"Message successfully sent  To: @`{uname}`")
                        time.sleep(0.5)
                    except:
                        pass
        except Exception as e:
            print(e)
            bot.send_message(id, "Error 404, try again with corrected input.")
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)


#Command handler and function to Manage Orders
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Manage Orders")
def ManageOrders(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    
    if f"{id}" in f"{admins}": # 
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="List Orders")
        key2 = types.KeyboardButton(text="Delete Order")
        key3 = types.KeyboardButton(text="Home")
        keyboardadmin.add(key1)
        keyboardadmin.add(key2, key3)
        bot.send_message(id, "Choose an action to perform.", reply_markup=keyboardadmin)
    else:
        bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)

#Command handler and function to List All Orders
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "List Orders")
def ListOrders(message):
    try:
        id = message.from_user.id
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        all_orders = GetDataFromDB.GetOrderInfo()
        if f"{id}" in f"{admins}":
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            if all_orders ==  []:
                bot.send_message(id, "No Order available in your store, /start")
            else:
                bot.send_message(id, "Your Oders List: ")
                bot.send_message(id, f" OrderID - ProductName - BuyerUserName")
                for ordernumber, productname, buyerusername in all_orders:
                    import time
                    time.sleep(0.5)
                    bot.send_message(id, f"`{ordernumber}` - `{productname}` - @{buyerusername}")
            key1 = types.KeyboardButton(text="List Orders")
            key2 = types.KeyboardButton(text="Delete Order")
            key3 = types.KeyboardButton(text="Home")
            keyboardadmin.add(key1)
            keyboardadmin.add(key2, key3)
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        bot.send_message(id, "Error 404, try again with corrected input.")


#Command handler and functions to Delete Order
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Delete Order")
def DeleteOrderMNG(message):
    try:
        id = message.from_user.id
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        all_orders = GetDataFromDB.GetOrderInfo()
        if f"{id}" in f"{admins}":
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            if all_orders ==  []:
                key1 = types.KeyboardButton(text="List Orders")
                key2 = types.KeyboardButton(text="Home")
                keyboardadmin.add(key1)
                keyboardadmin.add(key2)
                bot.send_message(id, "No Order available in your store, /start", reply_markup=keyboardadmin)
            else:
                bot.send_message(id, f" OrderID - ProductName - BuyerUserName ")
                for ordernumber, productname, buyerusername in all_orders:
                    bot.send_message(id, f"/{ordernumber} - `{productname}` - @{buyerusername}", parse_mode="Markdown")
                msg = bot.send_message(id, "Click on an Order ID of the order you want to delete: ", parse_mode="Markdown")
                bot.register_next_step_handler(msg, delete_an_order)
        else:
            bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, DeleteOrderMNG)
def delete_an_order(message):
    try:
        id = message.from_user.id
        ordernu = message.text
        ordernumber = ordernu[1:99]
        ordernum = GetDataFromDB.GetOrderIDs()
        ordernumbers = []
        for ordern in ordernum:
            ordernumbers.append(ordern[0])
        if f"{ordernumber}" in f"{ordernumbers}":
            try:
                global ordernums
                ordernums = ordernumber
            except Exception as e:
                print(e)
            
            
            admins = GetDataFromDB.GetAdminIDsInDB()
            if f"{id}" in f"{admins}":
                keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                keyboardadmin.row_width = 2
                key1 = types.KeyboardButton(text="List Orders")
                key2 = types.KeyboardButton(text="Home")
                keyboardadmin.add(key1)
                keyboardadmin.add(key2)
                CleanData.delete_an_order(ordernumber)
                msg = bot.send_message(id, "Deleted successfully.\n\n\nWhat will you like to do next ?\n\nSelect one of buttons ", reply_markup=keyboardadmin, parse_mode="Markdown")
            else:
                bot.send_message(id, " Only Admin can use this command.", reply_markup=keyboard)
        else:
            msg = bot.send_message(id, "Error 404, try again with corrected input.")
            bot.register_next_step_handler(msg, delete_an_order)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404, try again with corrected input.")
        bot.register_next_step_handler(msg, delete_an_order)

# Command handler and function to view configured manual payment wallets
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Payment Methods")
def PaymentMethodMNG(message):
    user_id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB() or []

    if f"{user_id}" not in f"{admins}":
        bot.send_message(user_id, "Only Admin can use this command.", reply_markup=keyboard)
        return

    wallets = get_payment_wallets()
    if not wallets:
        bot.send_message(user_id, "No wallets configured. Add PAYMENT_WALLETS in config.env.", reply_markup=keyboard)
        return

    wallet_lines = []
    for wallet in wallets:
        qr_path = wallet.get("qr_path") or "no QR path"
        wallet_lines.append(f"{wallet['label']}\nAddress: {wallet['address']}\nQR: {qr_path}")
    bot.send_message(user_id, "Configured manual payment wallets:\n\n" + "\n\n".join(wallet_lines), reply_markup=keyboard)
if __name__ == '__main__':
    try:
        logger.info("Starting bot with polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        exit(1)
