import json
import logging
import os
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_FILE = "shop_data.json"
db_lock = threading.Lock()

DEFAULT_DATA = {
    "users": [],
    "admins": [],
    "products": [],
    "orders": [],
    "categories": [],
    "payment_methods": []
}


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _load_data():
    if not os.path.exists(DATA_FILE):
        return {key: value[:] for key, value in DEFAULT_DATA.items()}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error loading JSON data: {e}")
        return {key: value[:] for key, value in DEFAULT_DATA.items()}

    for key, value in DEFAULT_DATA.items():
        data.setdefault(key, value[:])
    return data


def _save_data(data):
    temp_file = f"{DATA_FILE}.tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    os.replace(temp_file, DATA_FILE)


def _next_id(items):
    return max((int(item.get("id", 0)) for item in items), default=0) + 1


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _find(items, key, value):
    value = _as_int(value)
    for item in items:
        if _as_int(item.get(key)) == value:
            return item
    return None


def _rows(items, fields):
    return [tuple(item.get(field) for field in fields) for item in items]


def _distinct_rows(items, fields):
    seen = set()
    results = []
    for row in _rows(items, fields):
        if row not in seen:
            seen.add(row)
            results.append(row)
    return results


class CreateTables:
    """Compatibility shim for the old SQLite table setup."""

    @staticmethod
    def create_all_tables():
        with db_lock:
            data = _load_data()
            _save_data(data)
        logger.info("JSON data store is ready")


CreateTables.create_all_tables()


class CreateDatas:
    """JSON data creation and update operations."""

    @staticmethod
    def add_user(user_id, username):
        try:
            with db_lock:
                data = _load_data()
                if not _find(data["users"], "user_id", user_id):
                    data["users"].append({
                        "id": _next_id(data["users"]),
                        "user_id": int(user_id),
                        "username": username,
                        "wallet": 0,
                        "created_at": _now()
                    })
                    _save_data(data)
                return True
        except Exception as e:
            logger.error(f"Error adding user {username}: {e}")
            return False

    @staticmethod
    def add_admin(admin_id, username):
        try:
            with db_lock:
                data = _load_data()
                if not _find(data["admins"], "admin_id", admin_id):
                    data["admins"].append({
                        "id": _next_id(data["admins"]),
                        "admin_id": int(admin_id),
                        "username": username,
                        "wallet": 0,
                        "created_at": _now()
                    })
                    _save_data(data)
                return True
        except Exception as e:
            logger.error(f"Error adding admin {username}: {e}")
            return False

    @staticmethod
    def add_product(productnumber, admin_id, username):
        try:
            with db_lock:
                data = _load_data()
                if _find(data["products"], "productnumber", productnumber):
                    return True
                data["products"].append({
                    "id": _next_id(data["products"]),
                    "productnumber": int(productnumber),
                    "admin_id": int(admin_id),
                    "username": username,
                    "productname": "NIL",
                    "productdescription": "NIL",
                    "productprice": 0,
                    "productimagelink": "NIL",
                    "productdownloadlink": "https://nil.nil",
                    "productkeysfile": "NIL",
                    "productquantity": 0,
                    "productcategory": "Default Category",
                    "created_at": _now()
                })
                _save_data(data)
                return True
        except Exception as e:
            logger.error(f"Error adding product {productnumber}: {e}")
            return False

    @staticmethod
    def AddAuser(user_id, username):
        return CreateDatas.add_user(user_id, username)

    @staticmethod
    def AddAdmin(admin_id, username):
        return CreateDatas.add_admin(admin_id, username)

    @staticmethod
    def AddProduct(productnumber, admin_id, username):
        return CreateDatas.add_product(productnumber, admin_id, username)

    @staticmethod
    def AddOrder(buyer_id, username, productname, productprice, orderdate, paidmethod,
                 productdownloadlink, productkeys, ordernumber, productnumber, payment_id):
        try:
            with db_lock:
                data = _load_data()
                if _find(data["orders"], "ordernumber", ordernumber):
                    return True
                data["orders"].append({
                    "id": _next_id(data["orders"]),
                    "buyerid": int(buyer_id),
                    "buyerusername": username,
                    "productname": productname,
                    "productprice": productprice,
                    "orderdate": orderdate,
                    "paidmethod": paidmethod,
                    "productdownloadlink": productdownloadlink,
                    "productkeys": productkeys,
                    "buyercomment": "NIL",
                    "ordernumber": int(ordernumber),
                    "productnumber": int(productnumber),
                    "payment_id": payment_id,
                    "created_at": _now()
                })
                _save_data(data)
                return True
        except Exception as e:
            logger.error(f"Error adding order {ordernumber}: {e}")
            return False

    @staticmethod
    def AddCategory(categorynumber, categoryname):
        with db_lock:
            data = _load_data()
            if not _find(data["categories"], "categorynumber", categorynumber):
                data["categories"].append({
                    "id": _next_id(data["categories"]),
                    "categorynumber": int(categorynumber),
                    "categoryname": categoryname,
                    "created_at": _now()
                })
                _save_data(data)

    @staticmethod
    def AddEmptyRow():
        CreateDatas.AddPaymentMethod("None", "None", "None")

    @staticmethod
    def AddCryptoPaymentMethod(id, username, token_keys_clientid, secret_keys, method_name):
        with db_lock:
            data = _load_data()
            method = _find(data["payment_methods"], "method_name", method_name)
            if not method:
                method = {"id": _next_id(data["payment_methods"]), "method_name": method_name, "created_at": _now()}
                data["payment_methods"].append(method)
            method.update({
                "admin_id": id,
                "username": username,
                "token_keys_clientid": token_keys_clientid,
                "secret_keys": secret_keys,
                "activated": "NO"
            })
            _save_data(data)

    @staticmethod
    def AddPaymentMethod(id, username, method_name):
        with db_lock:
            data = _load_data()
            if not _find(data["payment_methods"], "method_name", method_name):
                data["payment_methods"].append({
                    "id": _next_id(data["payment_methods"]),
                    "admin_id": id,
                    "username": username,
                    "method_name": method_name,
                    "token_keys_clientid": None,
                    "secret_keys": None,
                    "activated": "YES",
                    "created_at": _now()
                })
                _save_data(data)

    @staticmethod
    def _update_one(collection, key, value, updates):
        with db_lock:
            data = _load_data()
            item = _find(data[collection], key, value)
            if item:
                item.update(updates)
                _save_data(data)

    @staticmethod
    def _update_many(collection, key, value, updates):
        with db_lock:
            data = _load_data()
            changed = False
            for item in data[collection]:
                if _as_int(item.get(key)) == _as_int(value):
                    item.update(updates)
                    changed = True
            if changed:
                _save_data(data)

    @staticmethod
    def UpdateOrderConfirmed(paidmethod, ordernumber):
        CreateDatas.UpdateOrderPaymentMethod(paidmethod, ordernumber)

    @staticmethod
    def UpdatePaymentMethodToken(id, username, token_keys_clientid, method_name):
        CreateDatas._update_one("payment_methods", "method_name", method_name, {
            "admin_id": id,
            "username": username,
            "token_keys_clientid": token_keys_clientid
        })

    @staticmethod
    def UpdatePaymentMethodSecret(id, username, secret_keys, method_name):
        CreateDatas._update_one("payment_methods", "method_name", method_name, {
            "admin_id": id,
            "username": username,
            "secret_keys": secret_keys
        })

    @staticmethod
    def Update_A_Category(categoryname, categorynumber):
        CreateDatas._update_one("categories", "categorynumber", categorynumber, {"categoryname": categoryname})

    @staticmethod
    def UpdateOrderComment(buyercomment, ordernumber):
        CreateDatas._update_one("orders", "ordernumber", ordernumber, {"buyercomment": buyercomment})

    @staticmethod
    def UpdateOrderPaymentMethod(paidmethod, ordernumber):
        CreateDatas._update_one("orders", "ordernumber", ordernumber, {"paidmethod": paidmethod})

    @staticmethod
    def UpdateOrderPurchasedKeys(productkeys, ordernumber):
        CreateDatas._update_one("orders", "ordernumber", ordernumber, {"productkeys": productkeys})

    @staticmethod
    def UpdateProductName(productname, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productname": productname})

    @staticmethod
    def UpdateProductDescription(productdescription, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productdescription": productdescription})

    @staticmethod
    def UpdateProductPrice(productprice, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productprice": productprice})

    @staticmethod
    def UpdateProductproductimagelink(productimagelink, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productimagelink": productimagelink})

    @staticmethod
    def UpdateProductproductdownloadlink(productdownloadlink, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productdownloadlink": productdownloadlink})

    @staticmethod
    def UpdateProductKeysFile(productkeysfile, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productkeysfile": productkeysfile})

    @staticmethod
    def UpdateProductQuantity(productquantity, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productquantity": productquantity})

    @staticmethod
    def UpdateProductCategory(productcategory, productnumber):
        CreateDatas._update_one("products", "productnumber", productnumber, {"productcategory": productcategory})

    @staticmethod
    def Update_All_ProductCategory(new_category, productcategory):
        CreateDatas._update_many("products", "productcategory", productcategory, {"productcategory": new_category})


class GetDataFromDB:
    """JSON query operations. Method names are kept for compatibility."""

    @staticmethod
    def _get_one(collection, key, value, field, default=None):
        with db_lock:
            item = _find(_load_data()[collection], key, value)
            return item.get(field) if item else default

    @staticmethod
    def GetUserWalletInDB(userid):
        return GetDataFromDB._get_one("users", "user_id", userid, "wallet", 0)

    @staticmethod
    def GetUserNameInDB(userid):
        return GetDataFromDB._get_one("users", "user_id", userid, "username", "")

    @staticmethod
    def GetAdminNameInDB(userid):
        return GetDataFromDB._get_one("admins", "admin_id", userid, "username", "")

    @staticmethod
    def GetUserIDsInDB():
        return _rows(_load_data()["users"], ["user_id"])

    @staticmethod
    def GetProductName(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productname")

    @staticmethod
    def GetProductDescription(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productdescription")

    @staticmethod
    def GetProductPrice(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productprice")

    @staticmethod
    def GetProductImageLink(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productimagelink")

    @staticmethod
    def GetProductDownloadLink(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productdownloadlink")

    @staticmethod
    def GetProductNumber(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productnumber")

    @staticmethod
    def GetProductQuantity(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productquantity")

    @staticmethod
    def GetProduct_A_Category(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "productcategory")

    @staticmethod
    def Get_A_CategoryName(categorynumber):
        return GetDataFromDB._get_one("categories", "categorynumber", categorynumber, "categoryname")

    @staticmethod
    def GetCategoryIDsInDB():
        return _rows(_load_data()["categories"], ["categorynumber", "categoryname"])

    @staticmethod
    def GetCategoryNumProduct(productcategory):
        count = sum(1 for product in _load_data()["products"] if product.get("productcategory") == productcategory)
        return [(count,)]

    @staticmethod
    def GetProduct_A_AdminID(productnumber):
        return GetDataFromDB._get_one("products", "productnumber", productnumber, "admin_id")

    @staticmethod
    def GetAdminIDsInDB():
        return _rows(_load_data()["admins"], ["admin_id"])

    @staticmethod
    def GetAdminUsernamesInDB():
        return _rows(_load_data()["admins"], ["username"])

    @staticmethod
    def GetProductNumberName():
        return _distinct_rows(_load_data()["products"], ["productnumber", "productname"])

    @staticmethod
    def GetProductInfos():
        return _distinct_rows(_load_data()["products"], ["productnumber", "productname", "productprice"])

    @staticmethod
    def GetProductInfo():
        return _distinct_rows(_load_data()["products"], [
            "productnumber", "productname", "productprice", "productdescription",
            "productimagelink", "productdownloadlink", "productquantity", "productcategory"
        ])

    @staticmethod
    def GetProductInfoByCTGName(productcategory):
        products = [p for p in _load_data()["products"] if p.get("productcategory") == productcategory]
        return _distinct_rows(products, [
            "productnumber", "productname", "productprice", "productdescription",
            "productimagelink", "productdownloadlink", "productquantity", "productcategory"
        ])

    @staticmethod
    def GetProductInfoByPName(productnumber):
        products = [p for p in _load_data()["products"] if _as_int(p.get("productnumber")) == _as_int(productnumber)]
        return _distinct_rows(products, [
            "productnumber", "productname", "productprice", "productdescription",
            "productimagelink", "productdownloadlink", "productquantity", "productcategory"
        ])

    @staticmethod
    def GetUsersInfo():
        return _distinct_rows(_load_data()["users"], ["user_id", "username", "wallet"])

    @staticmethod
    def AllUsers():
        return [(len(_load_data()["users"]),)]

    @staticmethod
    def AllAdmins():
        return [(len(_load_data()["admins"]),)]

    @staticmethod
    def AllProducts():
        return [(len(_load_data()["products"]),)]

    @staticmethod
    def AllOrders():
        return [(len(_load_data()["orders"]),)]

    @staticmethod
    def GetAdminsInfo():
        return _distinct_rows(_load_data()["admins"], ["admin_id", "username", "wallet"])

    @staticmethod
    def GetOrderInfo():
        return _distinct_rows(_load_data()["orders"], ["ordernumber", "productname", "buyerusername"])

    @staticmethod
    def GetPaymentMethods():
        return _distinct_rows(_load_data()["payment_methods"], ["method_name", "activated", "username"])

    @staticmethod
    def GetPaymentMethodsAll(method_name):
        methods = [m for m in _load_data()["payment_methods"] if m.get("method_name") == method_name]
        return _distinct_rows(methods, ["method_name", "token_keys_clientid", "secret_keys"])

    @staticmethod
    def GetPaymentMethodTokenKeysCleintID(method_name):
        return GetDataFromDB._get_one("payment_methods", "method_name", method_name, "token_keys_clientid")

    @staticmethod
    def GetPaymentMethodSecretKeys(method_name):
        return GetDataFromDB._get_one("payment_methods", "method_name", method_name, "secret_keys")

    @staticmethod
    def GetAllPaymentMethodsInDB():
        return _distinct_rows(_load_data()["payment_methods"], ["method_name"])

    @staticmethod
    def GetProductCategories():
        return _distinct_rows(_load_data()["products"], ["productcategory"])

    @staticmethod
    def GetProductIDs():
        return _rows(_load_data()["products"], ["productnumber"])

    @staticmethod
    def GetOrderDetails(ordernumber):
        orders = [
            o for o in _load_data()["orders"]
            if _as_int(o.get("ordernumber")) == _as_int(ordernumber) and o.get("paidmethod") != "NO"
        ]
        return _distinct_rows(orders, [
            "buyerid", "buyerusername", "productname", "productprice", "orderdate",
            "paidmethod", "productdownloadlink", "productkeys", "buyercomment",
            "ordernumber", "productnumber"
        ])

    @staticmethod
    def GetOrderIDs_Buyer(buyerid):
        orders = [
            o for o in _load_data()["orders"]
            if _as_int(o.get("buyerid")) == _as_int(buyerid) and o.get("paidmethod") != "NO"
        ]
        return _rows(orders, ["ordernumber"])

    @staticmethod
    def GetOrderIDs():
        return _rows(_load_data()["orders"], ["ordernumber"])

    @staticmethod
    def GetAllUnfirmedOrdersUser(buyerid):
        orders = [
            o for o in _load_data()["orders"]
            if _as_int(o.get("buyerid")) == _as_int(buyerid)
            and o.get("paidmethod") == "NO"
            and str(o.get("payment_id")) != str(o.get("ordernumber"))
        ]
        return _distinct_rows(orders, ["ordernumber", "productname", "buyerusername", "payment_id", "productnumber"])


class CleanData:
    @staticmethod
    def _delete(collection, key=None, value=None):
        with db_lock:
            data = _load_data()
            if key is None:
                data[collection] = []
            else:
                data[collection] = [item for item in data[collection] if _as_int(item.get(key)) != _as_int(value)]
            _save_data(data)

    @staticmethod
    def CleanShopUserTable():
        CleanData._delete("users")

    @staticmethod
    def CleanShopProductTable():
        CleanData._delete("products")

    @staticmethod
    def delete_an_order(*args):
        ordernumber = args[-1]
        CleanData._delete("orders", "ordernumber", ordernumber)

    @staticmethod
    def delete_a_product(productnumber):
        CleanData._delete("products", "productnumber", productnumber)

    @staticmethod
    def delete_a_payment_method(method_name):
        CleanData._delete("payment_methods", "method_name", method_name)

    @staticmethod
    def delete_a_category(categorynumber):
        CleanData._delete("categories", "categorynumber", categorynumber)
