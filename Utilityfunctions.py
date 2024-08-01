import logging
import re


class Iutility:
    def get_uuid_str(self,string):
        pattern = r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"

        # Extracting the UUID value
        match = re.search(pattern, string)
        if match:
            uuid_str = match.group(0)
            # print("UUID as string:", uuid_str)
            return uuid_str
        else:
            print("No UUID found in the string")


    def con_add_validation(self,coin_qty,coin_name):
        bstatus = False
        if coin_qty >=0 and len(coin_name.strip())!=0:
            if coin_name.isalpha():
                bstatus = True
                logging.info("Everything is right")
            else:
                logging.info("Invalid Coin name")
        elif coin_qty<=0:
            logging.info("Coin qty is negative not allowed")
        elif len(coin_name.strip())==0:
            logging.info("coin Name is invalid")

        return bstatus




