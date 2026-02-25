# -*- coding: utf-8 -*-
"""
Gestionnaire des catégories
"""
from typing import List, Optional, Dict, Any
from database.db_manager import db
from core.logger import logger
from core.data_signals import data_signals

class CategoryManager:
    """Gestionnaire singleton des catégories"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CategoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """
        Obtenir toutes les catégories actives
        
        Returns:
            Liste de dictionnaires représentant les catégories
        """
        query = """
            SELECT * FROM categories 
            WHERE is_active = 1 
            ORDER BY name
        """
        return [dict(row) for row in db.execute_query(query)]

    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtenir une catégorie par son ID
        
        Args:
            category_id: ID de la catégorie
            
        Returns:
            Dictionnaire de la catégorie ou None
        """
        query = "SELECT * FROM categories WHERE id = ?"
        row = db.fetch_one(query, (category_id,))
        return dict(row) if row else None

    def create_category(self, name: str, name_ar: str = "", description: str = "", parent_id: int = None) -> (bool, str, int):
        """
        Créer une nouvelle catégorie
        
        Args:
            name: Nom de la catégorie
            name_ar: Nom en arabe
            description: Description
            parent_id: ID de la catégorie parente
            
        Returns:
            (success, message, category_id)
        """
        try:
            # Vérifier si le nom existe déjà
            existing = db.fetch_one("SELECT id FROM categories WHERE name = ?", (name.strip(),))
            if existing:
                return False, "Une catégorie avec ce nom existe déjà", -1
                
            query = """
                INSERT INTO categories (name, name_ar, description, parent_id)
                VALUES (?, ?, ?, ?)
            """
            category_id = db.execute_insert(query, (name.strip(), name_ar.strip(), description.strip(), parent_id))
            
            logger.info(f"Catégorie créée: {name} (ID: {category_id})")
            data_signals.category_added.emit()
            data_signals.categories_changed.emit()
            return True, "Catégorie créée avec succès", category_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la catégorie: {e}")
            return False, f"Erreur: {str(e)}", -1

    def update_category(self, category_id: int, **kwargs) -> (bool, str):
        """
        Mettre à jour une catégorie
        
        Args:
            category_id: ID de la catégorie
            **kwargs: Champs à mettre à jour
            
        Returns:
            (success, message)
        """
        try:
            valid_fields = ['name', 'name_ar', 'description', 'parent_id', 'is_active']
            updates = []
            params = []
            
            for key, value in kwargs.items():
                if key in valid_fields:
                    updates.append(f"{key} = ?")
                    params.append(value)
            
            if not updates:
                return False, "Aucune donnée à mettre à jour"
                
            # Vérifier unicité du nom si modifié
            if 'name' in kwargs:
                existing = db.fetch_one(
                    "SELECT id FROM categories WHERE name = ? AND id != ?", 
                    (kwargs['name'].strip(), category_id)
                )
                if existing:
                    return False, "Une catégorie avec ce nom existe déjà"
            
            query = f"UPDATE categories SET {', '.join(updates)} WHERE id = ?"
            params.append(category_id)
            
            db.execute_update(query, tuple(params))
            logger.info(f"Catégorie mise à jour: ID {category_id}")
            data_signals.category_updated.emit()
            data_signals.categories_changed.emit()
            return True, "Catégorie mise à jour avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la catégorie: {e}")
            return False, f"Erreur: {str(e)}"

    def delete_category(self, category_id: int) -> (bool, str):
        """
        Supprimer (désactiver) une catégorie
        
        Args:
            category_id: ID de la catégorie
            
        Returns:
            (success, message)
        """
        try:
            # Vérifier s'il y a des produits liés
            products_count = db.fetch_one(
                "SELECT COUNT(*) as count FROM products WHERE category_id = ? AND is_active = 1", 
                (category_id,)
            )['count']
            
            if products_count > 0:
                return False, f"Impossible de supprimer: {products_count} produits sont liés à cette catégorie"
            
            # Delete directly
            db.execute_update("DELETE FROM categories WHERE id = ?", (category_id,))
            
            logger.info(f"Catégorie supprimée: ID {category_id}")
            data_signals.category_deleted.emit()
            data_signals.categories_changed.emit()
            return True, "Catégorie supprimée avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la catégorie: {e}")
            return False, f"Erreur: {str(e)}"

# Instance globale
category_manager = CategoryManager()
