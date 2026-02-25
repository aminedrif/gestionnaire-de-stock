# -*- coding: utf-8 -*-
"""
Gestionnaire de point de vente (POS - Point Of Sale)
"""
from typing import Dict, Optional, List
from datetime import datetime
from database.db_manager import db
from core.logger import logger
from core.data_signals import data_signals
from modules.products.product_manager import product_manager
from .cart import Cart
import config


class POSManager:
    """Gestionnaire de point de vente"""
    
    def __init__(self):
        self.current_cart = Cart()
        self.held_carts = []  # List of held carts: [{id, cart, customer_name, timestamp}]
        self.held_cart_counter = 0
        self.register_number = 1  # Numéro de caisse
    
    def set_register_number(self, register_number: int):
        """Définir le numéro de caisse"""
        self.register_number = register_number
    
    def get_cart(self) -> Cart:
        """Obtenir le panier actuel"""
        return self.current_cart
    
    def new_sale(self):
        """Démarrer une nouvelle vente (réinitialiser le panier)"""
        self.current_cart = Cart()
    
    def hold_cart(self, customer_name: str = "", customer_data: Optional[Dict] = None) -> tuple[bool, str]:
        """
        Mettre le panier en attente (hold)
        
        Args:
            customer_name: Nom du client (optionnel)
            customer_data: Données du client (pour restauration)
            
        Returns:
            (success, message)
        """
        if self.current_cart.is_empty():
            return False, "Le panier est vide"
        
        self.held_cart_counter += 1
        held_cart = {
            'id': self.held_cart_counter,
            'cart': self.current_cart,
            'customer_name': customer_name or f"Client #{self.held_cart_counter}",
            'customer_data': customer_data,
            'timestamp': datetime.now(),
            'total': self.current_cart.get_total(),
            'item_count': self.current_cart.get_item_count()
        }
        self.held_carts.append(held_cart)
        
        # Start a new cart
        self.current_cart = Cart()
        
        logger.info(f"Panier mis en attente: #{held_cart['id']}")
        return True, f"Panier #{held_cart['id']} mis en attente"
    
    def get_held_carts(self) -> list:
        """Obtenir la liste des paniers en attente"""
        return self.held_carts
    
    def retrieve_cart(self, held_cart_id: int, current_customer_data: Optional[Dict] = None) -> tuple[bool, str, Optional[Dict]]:
        """
        Récupérer un panier en attente
        
        Args:
            held_cart_id: ID du panier en attente
            current_customer_data: Données du client du panier ACTUEL (pour sauvegarde si swap)
            
        Returns:
            (success, message, retrieved_customer_data)
        """
        # Check if current cart has items
        if not self.current_cart.is_empty():
            # Put current cart on hold first
            self.held_cart_counter += 1
            
            # Determine name for current cart being auto-held
            cust_name = f"Client #{self.held_cart_counter}"
            if current_customer_data:
                cust_name = current_customer_data.get('full_name', cust_name)
            
            held_current = {
                'id': self.held_cart_counter,
                'cart': self.current_cart,
                'customer_name': cust_name,
                'customer_data': current_customer_data,
                'timestamp': datetime.now(),
                'total': self.current_cart.get_total(),
                'item_count': self.current_cart.get_item_count()
            }
            self.held_carts.append(held_current)
        
        # Find and retrieve the requested cart
        for i, held in enumerate(self.held_carts):
            if held['id'] == held_cart_id:
                self.current_cart = held['cart']
                customer_data = held.get('customer_data')
                self.held_carts.pop(i)
                logger.info(f"Panier récupéré: #{held_cart_id}")
                return True, f"Panier #{held_cart_id} récupéré", customer_data
        
        return False, "Panier en attente introuvable", None
    
    def delete_held_cart(self, held_cart_id: int) -> tuple[bool, str]:
        """Supprimer un panier en attente"""
        for i, held in enumerate(self.held_carts):
            if held['id'] == held_cart_id:
                self.held_carts.pop(i)
                return True, "Panier supprimé"
        return False, "Panier introuvable"
    
    def add_product_by_barcode(self, barcode: str, quantity: float = 1.0) -> tuple[bool, str]:
        """
        Ajouter un produit au panier par code-barres
        
        Args:
            barcode: Code-barres du produit
            quantity: Quantité
            
        Returns:
            (success, message)
        """
        product = product_manager.get_product_by_barcode(barcode)
        
        if not product:
            return False, "Produit introuvable"
        
        return self.current_cart.add_item(product, quantity)
    
    def add_product_by_id(self, product_id: int, quantity: float = 1.0) -> tuple[bool, str]:
        """
        Ajouter un produit au panier par ID
        
        Args:
            product_id: ID du produit
            quantity: Quantité
            
        Returns:
            (success, message)
        """
        product = product_manager.get_product(product_id)
        
        if not product:
            return False, "Produit introuvable"
        
        return self.current_cart.add_item(product, quantity)
    
    def add_to_cart(self, product_id: int, quantity: float = 1.0, custom_price: float = None, product_name: str = None) -> tuple[bool, str]:
        """
        Ajouter un produit au panier (générique)
        
        Args:
            product_id: ID du produit (0 pour divers)
            quantity: Quantité
            custom_price: Prix personnalisé (optionnel)
            product_name: Nom personnalisé (optionnel)
            
        Returns:
            (success, message)
        """
        if product_id <= 0:
            # Produit temporaire / divers
            # Pour éviter erreur FOREIGN KEY, on doit utiliser un produit réel "Divers"
            prod_name = "Produit Divers"
            product = product_manager.get_product_by_name(prod_name)
            
            if not product:
                # Créer la catégorie "Divers" si nécessaire
                cat_res = db.fetch_one("SELECT id FROM categories WHERE name = 'Divers'")
                if cat_res:
                    cat_id = cat_res['id']
                else:
                    db.execute_update("INSERT INTO categories (name, description) VALUES (?, ?)", ("Divers", "Produits divers"))
                    cat_id_res = db.fetch_one("SELECT last_insert_rowid() as id")
                    cat_id = cat_id_res['id']
                
                # Créer le produit Divers
                product_manager.create_product(
                    name=prod_name,
                    barcode='DIVERS', # Code unique pour divers
                    category_id=cat_id,
                    purchase_price=0,
                    selling_price=0, # Prix variable
                    stock_quantity=999999,
                    min_stock_level=0,
                    # is_active=1 default
                )
                product = product_manager.get_product_by_name(prod_name)
            
            # On utilise l'ID réel du produit Divers
            # Mais on modifie le prix de vente pour cet ajout spécifique
            if custom_price is not None:
                # IMPORTANT: On ne modifie pas le produit en base, juste l'objet dictionnaire passé au cart
                # Le CartItem prendra ce prix
                product = dict(product) # Copie
                product['selling_price'] = custom_price
                if product_name:
                    product['name'] = product_name
                    
        else:
            product = product_manager.get_product(product_id)
            if not product:
                return False, "Produit introuvable"
                
            if custom_price is not None:
                product['selling_price'] = custom_price
        
        
        # Si c'est un produit personnalisé (ID <= 0), on ne veut pas fusionner les lignes
        # car ils peuvent avoir des prix différents, ou l'utilisateur veut les distinguer
        prevent_merge = (product_id <= 0)
        
        return self.current_cart.add_item(product, quantity, prevent_merge)

    def complete_sale(self, cashier_id: int, payment_method: str, total_amount: float, customer_id: int = None, credit_amount: float = None) -> tuple[bool, str, int]:
        """
        Finaliser la vente
        
        Args:
            cashier_id: ID du vendeur
            payment_method: Méthode de paiement ('cash', 'credit', 'partial')
            total_amount: Montant total
            customer_id: ID du client (optionnel)
            credit_amount: Montant à mettre en crédit (pour paiements partiels)
            
        Returns:
            (success, message, sale_id)
        """
        if not self.current_cart.items:
            return False, "Panier vide", 0
            
        try:
            # 1. Générer code de vente
            sale_code = f"SLE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 2. Insérer la vente
            # Use schema column names: sale_number (not code), cashier_id (not user_id)
            
            sale_query = """
                INSERT INTO sales (sale_number, cashier_id, customer_id, subtotal, total_amount, payment_method, sale_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'completed')
            """
            subtotal = total_amount  # For simplicity, subtotal = total (no tax/discount breakdown here)
            sale_id = db.execute_insert(sale_query, (
                sale_code, cashier_id, customer_id, subtotal, total_amount, payment_method, sale_date
            ))
            
            if not sale_id:
                return False, "Erreur lors de la création de la vente", 0
                
            # 3. Insérer les articles de vente et mettre à jour le stock
            for item in self.current_cart.items:
                product_id = item.product_id
                # Ensure we have a valid product ID to satisfy FOREIGN KEY and NOT NULL constraints
                # If product_id is invalid (custom/shortcut), use 'Produit Divers'
                if product_id and product_id > 0:
                     db_product_id = product_id
                else:
                     # Fallback to "Produit Divers"
                     divers = product_manager.get_product_by_name("Produit Divers")
                     if divers:
                         db_product_id = divers['id']
                     else:
                         # Emergency fallback if Divers database entry missing (should not happen)
                         # Try to find ANY valid product to attach to or fail gracefully
                         # For now, log error and try generic fallback if possible, else 1
                         logger.error("Produit Divers not found for custom item sale!")
                         db_product_id = 1 # Hope ID 1 exists
                
                # Double check to ensure we never have None or 0
                if not db_product_id or db_product_id <= 0:
                     db_product_id = 1
                product_name = item.product_name
                barcode = item.barcode
                quantity = item.quantity
                unit_price = item.unit_price  # Prix de vente unitaire
                purchase_price = item.purchase_price
                subtotal = item.get_subtotal()  # Calculé via méthode
                discount_percentage = item.discount_percentage
                discount_percentage = item.discount_percentage
                # Handle optional category_id
                category_id = getattr(item, 'category_id', None)
                # Ensure category_id is valid (None if 0 or falsey to avoid FK violation)
                if not category_id or category_id == 0:
                    category_id = None
                
                # Insertion article avec tous les champs requis
                item_query = """
                    INSERT INTO sale_items (sale_id, product_id, product_name, barcode, quantity, unit_price, discount_percentage, subtotal, purchase_price, category_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                db.execute_insert(item_query, (sale_id, db_product_id, product_name, barcode, quantity, unit_price, discount_percentage, subtotal, purchase_price, category_id))
                
                # Mise à jour stock with SMART TOBACCO LOGIC
                if product_id > 0: # Si ce n'est pas un produit divers
                    # Fetch product details including parent link
                    product_query = """
                        SELECT id, stock_quantity, parent_product_id, packing_quantity 
                        FROM products WHERE id = ?
                    """
                    product_res = db.fetch_one(product_query, (product_id,))
                    
                    if product_res:
                        current_stock = product_res['stock_quantity']
                        parent_id = product_res['parent_product_id']
                        packing_qty = product_res['packing_quantity'] or 20
                        
                        qty_to_deduct = quantity
                        
                        # SMART LOGIC: If this product has a parent (e.g., Single -> Pack)
                        if parent_id:
                            # Check if qty >= packing_quantity -> sell full packs directly
                            if quantity >= packing_qty:
                                # Sell full packs from parent
                                full_packs = int(quantity // packing_qty)
                                remaining_singles = quantity % packing_qty
                                
                                # Deduct full packs from parent
                                parent_stock_query = "SELECT stock_quantity FROM products WHERE id = ?"
                                parent_res = db.fetch_one(parent_stock_query, (parent_id,))
                                if parent_res and parent_res['stock_quantity'] >= full_packs:
                                    new_parent_stock = parent_res['stock_quantity'] - full_packs
                                    db.execute_update("UPDATE products SET stock_quantity = ? WHERE id = ?", 
                                                     (new_parent_stock, parent_id))
                                    logger.info(f"Sold {full_packs} packs from parent ID {parent_id}")
                                
                                # Handle remaining singles
                                qty_to_deduct = remaining_singles
                            
                            # If we still need singles and current stock is insufficient
                            if qty_to_deduct > 0 and current_stock < qty_to_deduct:
                                # Need to open packs
                                shortage = qty_to_deduct - current_stock
                                packs_needed = (shortage + packing_qty - 1) // packing_qty  # Ceiling division
                                
                                # Check parent has enough packs
                                parent_stock_query = "SELECT stock_quantity FROM products WHERE id = ?"
                                parent_res = db.fetch_one(parent_stock_query, (parent_id,))
                                
                                if parent_res and parent_res['stock_quantity'] >= packs_needed:
                                    # Deduct packs from parent
                                    new_parent_stock = parent_res['stock_quantity'] - packs_needed
                                    db.execute_update("UPDATE products SET stock_quantity = ? WHERE id = ?", 
                                                     (new_parent_stock, parent_id))
                                    
                                    # Add singles to this product (the opened packs)
                                    singles_added = packs_needed * packing_qty
                                    current_stock += singles_added
                                    logger.info(f"Auto-opened {packs_needed} pack(s), added {singles_added} singles to product {product_id}")
                        
                        # Final stock update for this product
                        new_stock = current_stock - qty_to_deduct
                        if new_stock < 0:
                            new_stock = 0  # Safety: never go negative
                        db.execute_update("UPDATE products SET stock_quantity = ? WHERE id = ?", 
                                         (new_stock, product_id))
            
            # 4. Gérer le crédit client si nécessaire
            # Handle partial payment: use credit_amount if provided, else full total for credit
            actual_credit = credit_amount if credit_amount is not None else total_amount
            
            if (payment_method in ('credit', 'mixed')) and customer_id and actual_credit > 0:
                # Mettre à jour la dette du client
                update_credit_query = "UPDATE customers SET current_credit = current_credit + ? WHERE id = ?"
                db.execute_update(update_credit_query, (actual_credit, customer_id))
                
                # Enregistrer la transaction de crédit
                credit_trans_query = """
                    INSERT INTO customer_credit_transactions (customer_id, transaction_type, amount, transaction_date, notes, processed_by)
                    VALUES (?, 'credit_sale', ?, ?, ?, ?)
                """
                cash_paid = total_amount - actual_credit
                note = f"Achat {sale_code}" if payment_method == 'credit' else f"Achat {sale_code} (Payé: {cash_paid:.2f} DA)"
                db.execute_insert(credit_trans_query, (
                    customer_id, actual_credit, sale_date, note, cashier_id
                ))

            # 5. Vider le panier
            self.new_sale()
            
            logger.info(f"Vente finalisée: {sale_code} (ID: {sale_id})")
            data_signals.sale_completed.emit()
            data_signals.sales_changed.emit()
            data_signals.inventory_changed.emit()
            data_signals.product_changed.emit()
            return True, f"Vente réussie: {sale_code}", sale_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la finalisation de la vente: {e}")
            return False, f"Erreur système: {str(e)}", 0

    def get_sale(self, sale_id: int) -> Optional[Dict]:
        """Récupérer détails d'une vente pour reçu"""
        try:
            query = """
                SELECT s.*, u.full_name as cashier_name, c.full_name as customer_name
                FROM sales s
                LEFT JOIN users u ON s.cashier_id = u.id
                LEFT JOIN customers c ON s.customer_id = c.id
                WHERE s.id = ?
            """
            sale = db.fetch_one(query, (sale_id,))
            if not sale: return None
            
            # Récupérer items
            items_query = """
                SELECT si.*, p.name as product_name, p.barcode
                FROM sale_items si
                LEFT JOIN products p ON si.product_id = p.id
                WHERE si.sale_id = ?
            """
            items = db.execute_query(items_query, (sale_id,))
            
            result = dict(sale)
            result['items'] = [dict(i) for i in items]
            return result
        except Exception as e:
            logger.error(f"Erreur get_sale: {e}")
            return None

    def get_sale_by_number(self, sale_number: str) -> Optional[Dict]:
        """Récupérer détails d'une vente par son numéro de ticket"""
        try:
            query = "SELECT id FROM sales WHERE sale_number = ?"
            res = db.fetch_one(query, (sale_number,))
            if res:
                return self.get_sale(res['id'])
            return None
        except Exception as e:
            logger.error(f"Erreur get_sale_by_number: {e}")
            return None


    def cancel_sale(self, sale_id: int, reason: str = "") -> tuple[bool, str]:
        """
        Annuler une vente
        
        Args:
            sale_id: ID de la vente
            reason: Raison de l'annulation
            
        Returns:
            (success, message)
        """
        try:
            # Vérifier que la vente existe
            sale_query = "SELECT * FROM sales WHERE id = ?"
            sale = db.fetch_one(sale_query, (sale_id,))
            
            if not sale:
                return False, "Vente introuvable"
            
            if sale['status'] != 'completed':
                return False, "Cette vente est déjà annulée ou retournée"
            
            db.begin_transaction()
            
            try:
                # Marquer la vente comme annulée
                update_query = "UPDATE sales SET status = 'cancelled' WHERE id = ?"
                db.execute_update(update_query, (sale_id,))
                
                # Restaurer le stock
                items_query = "SELECT product_id, quantity FROM sale_items WHERE sale_id = ?"
                items = db.execute_query(items_query, (sale_id,))
                
                for item in items:
                    product_manager.increase_stock(item['product_id'], item['quantity'])
                
                # Si c'était un paiement à crédit, ajuster le crédit client
                if sale['payment_method'] == 'credit' and sale['customer_id']:
                    credit_query = """
                        UPDATE customers 
                        SET current_credit = current_credit - ?
                        WHERE id = ?
                    """
                    db.execute_update(credit_query, (sale['total_amount'], sale['customer_id']))
                
                db.commit()
                
                logger.info(f"Vente annulée: {sale['sale_number']} - Raison: {reason}")
                data_signals.sale_cancelled.emit()
                data_signals.sales_changed.emit()
                return True, "Vente annulée avec succès"
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors de l'annulation: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_return(self, sale_id: int, items_to_return: List[Dict],
                      processed_by: int, reason: str = "") -> tuple[bool, str, Optional[int]]:
        """
        Traiter un retour de produits
        
        Args:
            sale_id: ID de la vente originale
            items_to_return: Liste des articles à retourner [{product_id, quantity}]
            processed_by: ID de l'utilisateur qui traite le retour
            reason: Raison du retour
            
        Returns:
            (success, message, return_id)
        """
        try:
            # Vérifier la vente
            sale_query = "SELECT * FROM sales WHERE id = ?"
            sale = db.fetch_one(sale_query, (sale_id,))
            
            if not sale:
                return False, "Vente introuvable", None
            
            db.begin_transaction()
            
            try:
                # Calculer le montant du retour
                return_amount = 0.0
                
                # Générer le numéro de retour
                return_number = self._generate_return_number()
                
                # Créer l'enregistrement de retour
                return_query = """
                    INSERT INTO returns (
                        return_number, original_sale_id, return_amount,
                        refund_method, processed_by, reason
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """
                
                return_id = db.execute_insert(return_query, (
                    return_number, sale_id, 0.0,  # Montant mis à jour après
                    sale['payment_method'], processed_by, reason
                ))
                
                # Traiter chaque article retourné
                for item_data in items_to_return:
                    product_id = item_data['product_id']
                    quantity = item_data['quantity']
                    
                    # Obtenir l'article de vente original
                    item_query = """
                        SELECT * FROM sale_items 
                        WHERE sale_id = ? AND product_id = ?
                    """
                    sale_item = db.fetch_one(item_query, (sale_id, product_id))
                    
                    if not sale_item:
                        raise Exception(f"Article introuvable dans la vente: {product_id}")
                    
                    if quantity > sale_item['quantity']:
                        raise Exception(f"Quantité de retour invalide pour le produit {product_id}")
                    
                    # Calculer le montant du retour pour cet article
                    unit_price = sale_item['unit_price'] * (1 - sale_item['discount_percentage'] / 100.0)
                    item_return_amount = unit_price * quantity
                    return_amount += item_return_amount
                    
                    # Insérer l'article de retour
                    return_item_query = """
                        INSERT INTO return_items (
                            return_id, sale_item_id, product_id,
                            quantity_returned, unit_price, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """
                    db.execute_insert(return_item_query, (
                        return_id, sale_item['id'], product_id,
                        quantity, unit_price, item_return_amount
                    ))
                    
                    # Restaurer le stock
                    product_manager.increase_stock(product_id, quantity)

                    # ============================================================
                    # MISE A JOUR DE LA VENTE ORIGINALE (HISTORIQUE)
                    # ============================================================
                    
                    # 1. Mettre à jour la ligne de vente (quantity, subtotal)
                    new_item_qty = sale_item['quantity'] - quantity
                    new_item_subtotal = new_item_qty * sale_item['unit_price'] * (1 - sale_item['discount_percentage'] / 100.0)
                    
                    update_item_query = """
                        UPDATE sale_items 
                        SET quantity = ?, subtotal = ?
                        WHERE id = ?
                    """
                    db.execute_update(update_item_query, (new_item_qty, new_item_subtotal, sale_item['id']))
                    
                # 2. Mettre à jour l'en-tête de vente (total_amount, subtotal)
                # On déduit le montant du retour du total de la vente
                update_sale_query = """
                    UPDATE sales 
                    SET total_amount = total_amount - ?,
                        subtotal = subtotal - ?
                    WHERE id = ?
                """
                # Note: On suppose que total_amount et subtotal sont réduits du même montant (hors taxe spécifique)
                # Si TVA gérée séparément, il faudrait aussi réduire tax_amount
                db.execute_update(update_sale_query, (return_amount, return_amount, sale_id))
                
                # Mettre à jour le montant du retour
                update_return_query = "UPDATE returns SET return_amount = ? WHERE id = ?"
                db.execute_update(update_return_query, (return_amount, return_id))
                
                # Ajuster le crédit client si nécessaire
                if sale['payment_method'] == 'credit' and sale['customer_id']:
                    credit_query = """
                        UPDATE customers 
                        SET current_credit = current_credit - ?
                        WHERE id = ?
                    """
                    db.execute_update(credit_query, (return_amount, sale['customer_id']))
                
                db.commit()
                
                logger.info(f"Retour traité: {return_number} - Montant: {return_amount} DA")
                data_signals.return_processed.emit()
                data_signals.returns_changed.emit()
                data_signals.sales_changed.emit()
                return True, f"Retour enregistré: {return_number}", return_id
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors du traitement du retour: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def get_return(self, return_id: int) -> Optional[Dict]:
        """
        Obtenir les détails d'un retour
        
        Args:
            return_id: ID du retour
            
        Returns:
            Dictionnaire avec les détails du retour
        """
        return_query = """
            SELECT r.*, u.full_name as cashier_name, s.sale_number as original_sale_number,
                   c.full_name as customer_name
            FROM returns r
            LEFT JOIN users u ON r.processed_by = u.id
            LEFT JOIN sales s ON r.original_sale_id = s.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE r.id = ?
        """
        ret = db.fetch_one(return_query, (return_id,))
        
        if not ret:
            return None
        
        # Obtenir les articles retournés
        items_query = """
            SELECT ri.*, p.name as product_name
            FROM return_items ri
            LEFT JOIN products p ON ri.product_id = p.id
            WHERE ri.return_id = ?
        """
        items = db.execute_query(items_query, (return_id,))
        
        result = dict(ret)
        result['items'] = [dict(item) for item in items]
        
        return result
    
    def get_sale(self, sale_id: int) -> Optional[Dict]:
        """
        Obtenir les détails d'une vente
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Dictionnaire avec les détails de la vente
        """
        sale_query = """
            SELECT s.*, u.full_name as cashier_name, c.full_name as customer_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        """
        sale = db.fetch_one(sale_query, (sale_id,))
        
        if not sale:
            return None
        
        # Obtenir les articles
        items_query = "SELECT * FROM sale_items WHERE sale_id = ?"
        items = db.execute_query(items_query, (sale_id,))
        
        result = dict(sale)
        result['items'] = [dict(item) for item in items]
        
        return result
    
    def _generate_sale_number(self) -> str:
        """Générer un numéro de vente unique"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"VNT-{timestamp}-{self.register_number}"
    
    def _generate_return_number(self) -> str:
        """Générer un numéro de retour unique"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"RET-{timestamp}"
    
    def _update_customer_credit(self, customer_id: int, amount: float, sale_id: int):
        """Mettre à jour le crédit d'un client"""
        # Augmenter le crédit actuel
        update_query = """
            UPDATE customers 
            SET current_credit = current_credit + ?
            WHERE id = ?
        """
        db.execute_update(update_query, (amount, customer_id))
        
        # Enregistrer la transaction de crédit
        transaction_query = """
            INSERT INTO customer_credit_transactions (
                customer_id, transaction_type, amount, sale_id, processed_by
            ) VALUES (?, 'credit_sale', ?, ?, ?)
        """
        # Note: processed_by devrait être le cashier_id, mais on ne l'a pas ici
        db.execute_insert(transaction_query, (customer_id, amount, sale_id, 1))
    
    def _update_customer_stats(self, customer_id: int, amount: float):
        """Mettre à jour les statistiques d'un client"""
        update_query = """
            UPDATE customers 
            SET total_purchases = total_purchases + ?,
                purchase_count = purchase_count + 1,
                last_purchase_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        db.execute_update(update_query, (amount, customer_id))


# Instance globale
pos_manager = POSManager()
