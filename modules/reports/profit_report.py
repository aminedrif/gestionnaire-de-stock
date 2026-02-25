# -*- coding: utf-8 -*-
"""
Gestionnaire de rapports de bénéfices
"""
from typing import List, Dict, Any
from datetime import datetime
from database.db_manager import db
from core.logger import logger


class ProfitReportManager:
    """Gestionnaire de rapports de bénéfices"""
    
    def get_profit_by_period(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Calculer le bénéfice par période
        
        Args:
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Dictionnaire avec les statistiques de bénéfice
        """
        query = """
            SELECT 
                SUM(si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0)) as total_revenue,
                SUM(si.quantity * si.purchase_price) as total_cost,
                COUNT(DISTINCT s.id) as sale_count,
                SUM(si.quantity) as total_items_sold
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
        """
        
        result = db.fetch_one(query, (start_date, end_date))
        
        if result and result['total_revenue']:
            total_revenue = round(result['total_revenue'], 2)
            total_cost = round(result['total_cost'], 2) if result['total_cost'] else 0.0
            net_profit = round(total_revenue - total_cost, 2)
            profit_margin = round((net_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0.0
        else:
            total_revenue = 0.0
            total_cost = 0.0
            net_profit = 0.0
            profit_margin = 0.0
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'sale_count': result['sale_count'] if result else 0,
            'total_items_sold': result['total_items_sold'] if result else 0,
        }
    
    def get_daily_profit(self, date: str = None) -> Dict[str, Any]:
        """
        Calculer le bénéfice du jour
        
        Args:
            date: Date (YYYY-MM-DD), None = aujourd'hui
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return self.get_profit_by_period(date, date)
    
    def get_monthly_profit(self, year: int, month: int) -> Dict[str, Any]:
        """
        Calculer le bénéfice du mois
        
        Args:
            year: Année
            month: Mois (1-12)
            
        Returns:
            Dictionnaire avec les statistiques
        """
        from datetime import timedelta
        
        start_date = f"{year}-{month:02d}-01"
        
        # Calculer le dernier jour du mois
        if month == 12:
            end_date = f"{year}-12-31"
        else:
            next_month = datetime(year, month + 1, 1)
            last_day = next_month - timedelta(days=1)
            end_date = last_day.strftime('%Y-%m-%d')
        
        return self.get_profit_by_period(start_date, end_date)
    
    def get_profit_by_product(self, start_date: str, end_date: str,
                             limit: int = 20) -> List[Dict]:
        """
        Obtenir le bénéfice par produit
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre de produits à retourner
            
        Returns:
            Liste des produits avec bénéfices
        """
        query = """
            SELECT 
                p.id,
                p.name,
                p.name_ar,
                SUM(si.quantity) as quantity_sold,
                SUM(si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0)) as revenue,
                SUM(si.quantity * si.purchase_price) as cost,
                SUM(si.quantity * (si.unit_price * (1 - si.discount_percentage / 100.0) - si.purchase_price)) as profit
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
            GROUP BY p.id, p.name, p.name_ar
            ORDER BY profit DESC
            LIMIT ?
        """
        
        results = db.execute_query(query, (start_date, end_date, limit))
        
        products = []
        for row in results:
            product = dict(row)
            product['revenue'] = round(product['revenue'], 2)
            product['cost'] = round(product['cost'], 2)
            product['profit'] = round(product['profit'], 2)
            
            if product['revenue'] > 0:
                product['profit_margin'] = round((product['profit'] / product['revenue']) * 100, 2)
            else:
                product['profit_margin'] = 0.0
            
            products.append(product)
        
        return products
    
    def get_profit_by_category(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtenir le bénéfice par catégorie
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des catégories avec bénéfices
        """
        query = """
            SELECT 
                c.id,
                c.name as category_name,
                c.name_ar as category_name_ar,
                SUM(si.quantity) as quantity_sold,
                SUM(si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0)) as revenue,
                SUM(si.quantity * si.purchase_price) as cost,
                SUM(si.quantity * (si.unit_price * (1 - si.discount_percentage / 100.0) - si.purchase_price)) as profit
            FROM sale_items si
            LEFT JOIN products p ON si.product_id = p.id
            JOIN categories c ON COALESCE(si.category_id, p.category_id) = c.id
            JOIN sales s ON si.sale_id = s.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
            GROUP BY c.id, c.name, c.name_ar
            ORDER BY profit DESC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        
        categories = []
        for row in results:
            category = dict(row)
            category['revenue'] = round(category['revenue'], 2)
            category['cost'] = round(category['cost'], 2)
            category['profit'] = round(category['profit'], 2)
            
            if category['revenue'] > 0:
                category['profit_margin'] = round((category['profit'] / category['revenue']) * 100, 2)
            else:
                category['profit_margin'] = 0.0
            
            categories.append(category)
        
        return categories
    
    def get_daily_profit_trend(self, start_date: str, end_date: str, category_id: int = None) -> List[Dict]:
        """
        Obtenir la tendance des bénéfices jour par jour (optionnel: filtrer par catégorie)
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            category_id: ID de la catégorie (optionnel)
            
        Returns:
            Liste des bénéfices par jour
        """
        params = [start_date, end_date]
        
        # Base query setup
        join_clause = "JOIN sales s ON si.sale_id = s.id"
        where_clause = "WHERE date(s.sale_date) BETWEEN ? AND ? AND s.status = 'completed'"
        
        if category_id is not None:
             join_clause += " LEFT JOIN products p ON si.product_id = p.id"
             where_clause += " AND COALESCE(si.category_id, p.category_id) = ?"
             params.append(category_id)
        
        query = f"""
            SELECT 
                date(s.sale_date) as date,
                SUM(si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0)) as revenue,
                SUM(CASE WHEN s.payment_method = 'credit' OR s.payment_method = 'dette' THEN 
                    si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0) 
                    ELSE 0 END) as credit_revenue,
                SUM(si.quantity * si.purchase_price) as cost,
                SUM(si.quantity * (si.unit_price * (1 - si.discount_percentage / 100.0) - si.purchase_price)) as profit
            FROM sale_items si
            {join_clause}
            {where_clause}
            GROUP BY date(s.sale_date)
            ORDER BY date(s.sale_date)
        """
        
        results = db.execute_query(query, tuple(params))
        
        trend = []
        for row in results:
            day = dict(row)
            day['revenue'] = round(day['revenue'], 2)
            day['credit_revenue'] = round(day['credit_revenue'], 2) if day['credit_revenue'] else 0.0
            day['cost'] = round(day['cost'], 2)
            day['profit'] = round(day['profit'], 2)
            
            if day['revenue'] > 0:
                day['profit_margin'] = round((day['profit'] / day['revenue']) * 100, 2)
            else:
                day['profit_margin'] = 0.0
            
            trend.append(day)
        
        return trend
    
    def get_loss_making_products(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtenir les produits vendus à perte
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des produits à perte
        """
        query = """
            SELECT 
                p.id,
                p.name,
                p.name_ar,
                SUM(si.quantity) as quantity_sold,
                SUM(si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0)) as revenue,
                SUM(si.quantity * si.purchase_price) as cost,
                SUM(si.quantity * (si.unit_price * (1 - si.discount_percentage / 100.0) - si.purchase_price)) as profit
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
            GROUP BY p.id, p.name, p.name_ar
            HAVING profit < 0
            ORDER BY profit ASC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        
        products = []
        for row in results:
            product = dict(row)
            product['revenue'] = round(product['revenue'], 2)
            product['cost'] = round(product['cost'], 2)
            product['profit'] = round(product['profit'], 2)
            products.append(product)
        
        return products
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """
        Obtenir les statistiques globales
        
        Returns:
            Dictionnaire avec les statistiques
        """
        # Bénéfice total
        query = """
            SELECT 
                SUM(si.quantity * si.unit_price * (1 - si.discount_percentage / 100.0)) as total_revenue,
                SUM(si.quantity * si.purchase_price) as total_cost
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.status = 'completed'
        """
        
        result = db.fetch_one(query)
        
        if result and result['total_revenue']:
            total_revenue = round(result['total_revenue'], 2)
            total_cost = round(result['total_cost'], 2) if result['total_cost'] else 0.0
            total_profit = round(total_revenue - total_cost, 2)
        else:
            total_revenue = 0.0
            total_cost = 0.0
            total_profit = 0.0
        
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
        }



    def get_category_performance_report(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtenir le rapport de performance par catégorie avec le meilleur produit
        """
        # 1. Get basic category stats
        stats = self.get_profit_by_category(start_date, end_date)
        
        # 2. For each category, find top product
        for cat in stats:
            cat_id = cat['id']
            # Query for top product in this category for this period
            query = """
                SELECT p.name, SUM(si.quantity) as qty
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE p.category_id = ?
                  AND date(s.sale_date) BETWEEN ? AND ?
                  AND s.status = 'completed'
                GROUP BY p.id, p.name
                ORDER BY qty DESC
                LIMIT 1
            """
            top_prod = db.fetch_one(query, (cat_id, start_date, end_date))
            if top_prod:
                cat['top_product'] = top_prod['name']
                cat['top_product_qty'] = top_prod['qty']
            else:
                cat['top_product'] = "-"
                cat['top_product_qty'] = 0
                
        return stats


# Instance globale
profit_report_manager = ProfitReportManager()
