import logging


def heartbeat_resolver(obj, info):
    try:
        info.context["heartbeat"].ping_database()
        payload = {"success": True}
    except Exception as error:
        logging.error("Failed to ping database", exc_info=error)
        payload = {"success": False, "errors": [str(error)]}
    return payload


def get_quote_resolver(obj, info, user_id):
    try:
        quote = info.context["quotes"].get_quote(user_id)
        payload = {"success": True, "quote": quote}
    except Exception as error:
        logging.error("Failed to get quote", exc_info=error)
        payload = {"success": False, "errors": [str(error)]}
    return payload


def get_same_quote_resolver(obj, info, user_id, quote_id):
    try:
        quote = info.context["quotes"].get_same_quote(user_id, quote_id)
        payload = {"success": True, "quote": quote}
    except Exception as error:
        logging.error("Failed to get same quote", exc_info=error)
        payload = {"success": False, "errors": [str(error)]}
    return payload


def like_quote_resolver(obj, info, user_id, quote_id):
    try:
        info.context["quotes"].like_quote(user_id, quote_id)
        payload = {"success": True}
    except Exception as error:
        logging.error("Failed to like quote", exc_info=error)
        payload = {"success": False, "errors": [str(error)]}
    return payload
