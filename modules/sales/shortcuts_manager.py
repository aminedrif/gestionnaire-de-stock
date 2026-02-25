# -*- coding: utf-8 -*-
"""
Gestionnaire des raccourcis POS
"""
from typing import List, Dict, Any, Optional
from database.db_manager import db
from core.logger import logger
from core.data_signals import data_signals


class ShortcutsManager:
    """Gestionnaire des raccourcis POS personnalisables"""
    
    def __init__(self):
        """Initialiser le gestionnaire"""
        pass
    
    def get_all_shortcuts(self) -> List[Dict[str, Any]]:
        """
        Récupérer tous les raccourcis triés par position
        
        Returns:
            Liste des raccourcis
        """
        try:
            query = """
                SELECT 
                    s.*,
                    p.name as product_name,
                    p.barcode as product_barcode
                FROM pos_shortcuts s
                LEFT JOIN products p ON s.product_id = p.id
                ORDER BY s.position ASC
            """
            results = db.execute_query(query)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des raccourcis: {e}")
            return []
    
    def get_shortcut(self, shortcut_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupérer un raccourci par son ID
        
        Args:
            shortcut_id: ID du raccourci
            
        Returns:
            Raccourci ou None
        """
        try:
            query = """
                SELECT 
                    s.*,
                    p.name as product_name,
                    p.barcode as product_barcode
                FROM pos_shortcuts s
                LEFT JOIN products p ON s.product_id = p.id
                WHERE s.id = ?
            """
            result = db.fetch_one(query, (shortcut_id,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du raccourci {shortcut_id}: {e}")
            return None
    
    def add_shortcut(self, product_id: Optional[int], label: str, 
                     image_path: Optional[str], unit_price: float, 
                     position: int, category_id: Optional[int] = None) -> tuple[bool, str, Optional[int]]:
        """
        Ajouter un nouveau raccourci
        
        Args:
            product_id: ID du produit (peut être None pour produit personnalisé)
            label: Libellé du raccourci
            image_path: Chemin de l'image (optionnel)
            unit_price: Prix unitaire
            position: Position du raccourci
            category_id: ID de la catégorie (pour produits personnalisés)
            
        Returns:
            (succès, message, shortcut_id)
        """
        try:
            # Vérifier que la position n'est pas déjà prise
            existing = db.fetch_one(
                "SELECT id FROM pos_shortcuts WHERE position = ?", 
                (position,)
            )
            
            if existing:
                return False, "Cette position est déjà occupée", None
            
            query = """
                INSERT INTO pos_shortcuts (product_id, label, image_path, unit_price, position, category_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            shortcut_id = db.execute_insert(
                query, 
                (product_id, label, image_path, unit_price, position, category_id)
            )
            
            logger.info(f"Raccourci ajouté: {label} à la position {position}")
            data_signals.shortcuts_changed.emit()
            return True, "Raccourci ajouté avec succès", shortcut_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du raccourci: {e}")
            return False, f"Erreur: {str(e)}", None
    
    def update_shortcut(self, shortcut_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un raccourci
        
        Args:
            shortcut_id: ID du raccourci
            **kwargs: Champs à mettre à jour (product_id, label, image_path, unit_price, position, category_id)
            
        Returns:
            (succès, message)
        """
        try:
            # Construire la requête dynamiquement
            fields = []
            values = []
            
            allowed_fields = ['product_id', 'label', 'image_path', 'unit_price', 'position', 'category_id']
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False, "Aucun champ à mettre à jour"
            
            # Vérifier si nouvelle position déjà occupée (par un autre raccourci)
            if 'position' in kwargs:
                existing = db.fetch_one(
                    "SELECT id FROM pos_shortcuts WHERE position = ? AND id != ?", 
                    (kwargs['position'], shortcut_id)
                )
                
                if existing:
                    return False, "Cette position est déjà occupée"
            
            values.append(shortcut_id)
            query = f"UPDATE pos_shortcuts SET {', '.join(fields)} WHERE id = ?"
            
            db.execute_update(query, tuple(values))
            
            logger.info(f"Raccourci {shortcut_id} mis à jour")
            data_signals.shortcuts_changed.emit()
            return True, "Raccourci mis à jour avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du raccourci: {e}")
            return False, f"Erreur: {str(e)}"
    
    def delete_shortcut(self, shortcut_id: int) -> tuple[bool, str]:
        """
        Supprimer un raccourci
        
        Args:
            shortcut_id: ID du raccourci
            
        Returns:
            (succès, message)
        """
        try:
            # 1. Récupérer la position du raccourci à supprimer
            shortcut = db.fetch_one("SELECT position FROM pos_shortcuts WHERE id = ?", (shortcut_id,))
            if not shortcut:
                return False, "Raccourci introuvable"
            
            position_to_remove = shortcut['position']
            
            # 2. Supprimer le raccourci
            query = "DELETE FROM pos_shortcuts WHERE id = ?"
            db.execute_update(query, (shortcut_id,))
            
            # 3. Décaler les positions suivantes (position - 1)
            update_query = "UPDATE pos_shortcuts SET position = position - 1 WHERE position > ?"
            db.execute_update(update_query, (position_to_remove,))
            
            logger.info(f"Raccourci {shortcut_id} supprimé et positions réorganisées")
            data_signals.shortcuts_changed.emit()
            return True, "Raccourci supprimé avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du raccourci: {e}")
            return False, f"Erreur: {str(e)}"
    
    def reorder_shortcuts(self, shortcut_positions: Dict[int, int]) -> tuple[bool, str]:
        """
        Réorganiser les positions des raccourcis
        
        Args:
            shortcut_positions: Dictionnaire {shortcut_id: nouvelle_position}
            
        Returns:
            (succès, message)
        """
        try:
            db.begin_transaction()
            
            for shortcut_id, position in shortcut_positions.items():
                db.execute_update(
                    "UPDATE pos_shortcuts SET position = ? WHERE id = ?",
                    (position, shortcut_id)
                )
            
            db.commit()
            db.commit()
            logger.info("Raccourcis réorganisés")
            data_signals.shortcuts_changed.emit()
            return True, "Raccourcis réorganisés avec succès"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la réorganisation des raccourcis: {e}")
            return False, f"Erreur: {str(e)}"
    
    def get_next_available_position(self) -> int:
        """
        Obtenir la prochaine position disponible
        
        Returns:
            Numéro de la prochaine position libre
        """
        try:
            # Récupérer toutes les positions occupées
            query = "SELECT position FROM pos_shortcuts ORDER BY position ASC"
            results = db.execute_query(query)
            occupied_positions = {row['position'] for row in results}
            
            # Trouver la première position libre (de 1 à 12 par défaut)
            for i in range(1, 13):
                if i not in occupied_positions:
                    return i
            
            # Si toutes les positions sont occupées, retourner la suivante
            return len(occupied_positions) + 1
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de position disponible: {e}")
            return 1


# Instance globale
shortcuts_manager = ShortcutsManager()
