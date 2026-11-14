# Импортируем напрямую из файлов, а не через подпакеты
from database.tables.entities.employee import Employee
from database.tables.entities.merch_item import MerchItem
from database.tables.junctions.purchase import Purchase
from database.tables.junctions.transfer import Transfer

__all__ = ["Employee", "MerchItem", "Purchase", "Transfer"]