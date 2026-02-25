# -*- coding: utf-8 -*-
"""
Centralized data change signals for real-time UI updates
"""
from PyQt5.QtCore import QObject, pyqtSignal


class DataSignals(QObject):
    """Global signals for data changes across the application"""
    
    # Product signals
    product_added = pyqtSignal()
    product_updated = pyqtSignal()
    product_deleted = pyqtSignal()
    products_changed = pyqtSignal()  # Generic product change
    product_changed = pyqtSignal()   # Alias for single product change
    inventory_changed = pyqtSignal() # Specific for stock updates
    
    # Customer signals
    customer_added = pyqtSignal()
    customer_updated = pyqtSignal()
    customer_deleted = pyqtSignal()
    customers_changed = pyqtSignal()  # Generic customer change
    
    # Supplier signals
    supplier_added = pyqtSignal()
    supplier_updated = pyqtSignal()
    supplier_deleted = pyqtSignal()
    suppliers_changed = pyqtSignal()  # Generic supplier change
    
    # Sale signals
    sale_completed = pyqtSignal()
    sale_cancelled = pyqtSignal()
    sales_changed = pyqtSignal()  # Generic sale change
    
    # Finance signals
    session_opened = pyqtSignal()
    session_closed = pyqtSignal()
    safe_transaction = pyqtSignal()
    finance_changed = pyqtSignal()  # Generic finance change
    
    # Category signals
    category_added = pyqtSignal()
    category_updated = pyqtSignal()
    category_deleted = pyqtSignal()
    categories_changed = pyqtSignal()  # Generic category change
    
    # Return signals
    return_processed = pyqtSignal()
    returns_changed = pyqtSignal()  # Generic return change
    
    # Shortcut signals
    shortcuts_changed = pyqtSignal()


# Global instance
data_signals = DataSignals()
