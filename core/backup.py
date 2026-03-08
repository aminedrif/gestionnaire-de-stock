# -*- coding: utf-8 -*-
"""
Système de sauvegarde automatique et manuelle
"""
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
import config
from database.db_manager import db
from .logger import logger


class BackupManager:
    """Gestionnaire de sauvegardes"""
    
    def __init__(self):
        self.backup_dir = config.BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, destination: Optional[Path] = None) -> tuple[bool, str, Optional[Path]]:
        """
        Créer une sauvegarde de la base de données
        
        Args:
            destination: Dossier de destination (None = dossier par défaut)
            
        Returns:
            (success, message, backup_path)
        """
        try:
            # Générer le nom du fichier de sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"minimarket_backup_{timestamp}"
            
            # Déterminer le dossier de destination
            if destination is None:
                destination = self.backup_dir
            else:
                destination = Path(destination)
                destination.mkdir(parents=True, exist_ok=True)
            
            # Copier la base de données
            db_backup_path = destination / f"{backup_name}.db"
            
            # Utiliser la méthode de backup de SQLite pour éviter les corruptions
            success = db.backup_database(db_backup_path)
            
            if not success:
                return False, "Erreur lors de la copie de la base de données", None
            
            logger.log_backup(str(db_backup_path), True)
            return True, f"Sauvegarde créée: {db_backup_path.name}", db_backup_path
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def restore_backup(self, backup_path: Path) -> tuple[bool, str]:
        """
        Restaurer une sauvegarde
        
        Args:
            backup_path: Chemin de la sauvegarde (.db)
            
        Returns:
            (success, message)
        """
        try:
            if not backup_path.exists():
                return False, "Fichier de sauvegarde introuvable"
            
            # Créer une sauvegarde de la base actuelle avant restauration
            current_backup = config.DATA_DIR / f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            if config.DATABASE_PATH.exists():
                shutil.copy2(config.DATABASE_PATH, current_backup)
            
            # Restaurer
            success = db.restore_database(backup_path)
            
            if success:
                logger.info(f"Base de données restaurée depuis: {backup_path}")
                return True, "Restauration réussie"
            else:
                return False, "Erreur lors de la restauration"
                
        except Exception as e:
            error_msg = f"Erreur lors de la restauration: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def auto_backup(self) -> tuple[bool, str]:
        """
        Effectuer une sauvegarde automatique
        
        Returns:
            (success, message)
        """
        if not config.BACKUP_CONFIG['auto_backup']:
            return False, "Sauvegarde automatique désactivée"
        
        success, message, _ = self.create_backup()
        
        if success:
            # Nettoyer les anciennes sauvegardes
            self.cleanup_old_backups()
        
        return success, message
    
    def cleanup_old_backups(self):
        """Supprimer les sauvegardes anciennes"""
        try:
            keep_days = config.BACKUP_CONFIG['keep_backups_days']
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            # Lister tous les fichiers de sauvegarde
            backup_files = list(self.backup_dir.glob("minimarket_backup_*"))
            
            deleted_count = 0
            for backup_file in backup_files:
                # Obtenir la date de modification
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"{deleted_count} ancienne(s) sauvegarde(s) supprimée(s)")
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des sauvegardes: {e}")
    
    def list_backups(self) -> List[Dict]:
        """
        Lister toutes les sauvegardes disponibles (.xlsx et .db)
        
        Returns:
            Liste de dictionnaires avec infos sur les sauvegardes
        """
        backups = []
        
        # Collect all backup files (.xlsx auto backups + .db manual backups)
        all_files = []
        all_files.extend(self.backup_dir.glob("auto_backup_*.xlsx"))
        all_files.extend(self.backup_dir.glob("minimarket_backup_*.db"))
        
        for backup_file in sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True):
            stat = backup_file.stat()
            
            # Determine type
            if backup_file.suffix == '.xlsx':
                backup_type = 'Excel'
            else:
                backup_type = 'Base de données'
            
            # Format size
            size_bytes = stat.st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes} o"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} Ko"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.2f} Mo"
            
            backups.append({
                'path': backup_file,
                'name': backup_file.name,
                'type': backup_type,
                'size': size_bytes,
                'size_str': size_str,
                'created': datetime.fromtimestamp(stat.st_mtime),
                'created_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            })
        
        return backups
    
    def delete_backup(self, backup_path: Path) -> tuple[bool, str]:
        """
        Supprimer un fichier de sauvegarde
        
        Args:
            backup_path: Chemin du fichier à supprimer
            
        Returns:
            (success, message)
        """
        try:
            if not backup_path.exists():
                return False, "Fichier introuvable"
            
            backup_path.unlink()
            logger.info(f"Sauvegarde supprimée: {backup_path.name}")
            return True, f"Sauvegarde supprimée: {backup_path.name}"
            
        except Exception as e:
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_total_backup_size(self) -> str:
        """
        Calculer la taille totale des sauvegardes
        
        Returns:
            Taille formatée (ex: '15.3 Mo')
        """
        total = 0
        for f in self.backup_dir.iterdir():
            if f.is_file():
                total += f.stat().st_size
        
        if total < 1024:
            return f"{total} o"
        elif total < 1024 * 1024:
            return f"{total / 1024:.1f} Ko"
        else:
            return f"{total / (1024 * 1024):.1f} Mo"
    
    def export_to_usb(self, usb_path: Path) -> tuple[bool, str]:
        """
        Exporter une sauvegarde vers une clé USB
        
        Args:
            usb_path: Chemin de la clé USB
            
        Returns:
            (success, message)
        """
        if not usb_path.exists():
            return False, "Clé USB introuvable"
        
        # Créer un dossier pour les sauvegardes sur la clé
        usb_backup_dir = usb_path / "MiniMarket_Backups"
        usb_backup_dir.mkdir(exist_ok=True)
        
        # Créer la sauvegarde
        success, message, backup_path = self.create_backup(
            destination=usb_backup_dir
        )
        
        if success:
            return True, f"Sauvegarde exportée vers: {backup_path}"
        else:
            return False, message


# Instance globale
backup_manager = BackupManager()
