from datetime import *
import telebot
from telebot import types
import os
from database import *
from dotenv import load_dotenv
load_dotenv('config.env')

# Bot connection
bot = telebot.TeleBot(f"{os.getenv('TELEGRAM_BOT_TOKEN')}", threaded=False)
StoreCurrency = f"{os.getenv('STORE_CURRENCY')}"

class CategoriesDatas:
    def get_category_products(message, input_cate):
        id = message.from_user.id
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        categories = []
        for catname in all_categories:
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
            product_category = product_cate.upper() if product_cate else None
            if product_category in categories:
                product_list = GetDataFromDB.GetProductInfoByCTGName(product_category)
                print(product_list)
                if product_list == []:
                    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    keyboard.row_width = 2
                    key1 = types.KeyboardButton(text="Shop Items")
                    key2 = types.KeyboardButton(text="My Orders")
                    key3 = types.KeyboardButton(text="Support")
                    keyboard.add(key1)
                    keyboard.add(key2, key3)
                    bot.send_message(id, f"No Product in the store", reply_markup=keyboard)
                else:
                    bot.send_message(id, f"{product_cate} Gategory's Products")
                    for productnumber, productname, productprice, productdescription, productimagelink in product_list:
                        product_keyboard = types.InlineKeyboardMarkup()
                        product_keyboard.add(types.InlineKeyboardButton(text="Buy Now", callback_data=f"getproduct_{productnumber}"))
                        bot.send_photo(id, photo=f"{productimagelink}", caption=f"Product ID: {productnumber}\n\nName: {productname}\n\nPrice: {productprice} {StoreCurrency}\n\nDescription: {productdescription}", reply_markup=product_keyboard)
            else:
                bot.send_message(id, "Category not found.")