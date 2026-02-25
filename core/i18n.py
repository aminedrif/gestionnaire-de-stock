# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal

class I18nManager(QObject):
    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_language = 'fr'  # Default to French
        
        # Translation Dictionary
        self.translations = {
            'fr': {
                # General
                'app_title': 'DamDev POS',
                'slogan': 'La gestion de stock\nsimple et intelligente.',
                'version': 'v{}',
                
                # Login
                'welcome_back': 'Bon retour ! 👋',
                'enter_credentials': 'Veuillez entrer vos identifiants.',
                'username': "Nom d'utilisateur",
                'password': 'Mot de passe',
                'login_btn': 'Se connecter',
                'login_loading': 'Connexion...',
                'default_creds': 'Admin par défaut: admin / admin123',
                'login_error': 'Erreur lors de la connexion',
                'system_error': 'Erreur système: {}',
                'msg_login_failed': "Nom d'utilisateur ou mot de passe incorrect",
                'msg_account_disabled': "Ce compte est désactivé",
                
                # Sidebar / Menu
                'menu_home': '🏠  Accueil (F1)',
                'menu_pos': '🛒  Caisse (F2)',
                'menu_products': '📦  Produits (F3)',
                'menu_customers': '👥  Clients (F4)',
                'menu_suppliers': '🏭  Fournisseurs (F5)',
                'menu_reports': '📊  Rapports (F6)',
                'menu_returns': '↩️  Retours (F7)',
                'menu_history': '📜  Historique (F8)',
                'menu_settings': '⚙️  Paramètres (F10)',
                'menu_logout': '🚪  Déconnexion',
                'confirm_logout_title': 'Déconnexion',
                'confirm_logout_msg': 'Se déconnecter ?',

                # Finance (Caisse & Coffre)
                'finance_title': '💰 Gestion Caisse & Coffre',
                'finance_caisse': 'Caisse',
                'finance_coffre': 'Coffre',
                'finance_caisse_closed': 'Fermée',
                'btn_open_session': '🔓 Ouvrir Caisse',
                'btn_close_session': '🔒 Fermer Caisse',
                'btn_deposit_safe': '💵 Dépôt Coffre',
                'finance_history_sessions': '📋 Historique Sessions',
                'finance_history_safe': '🏦 Mouvements Coffre',
                'finance_session_id': 'ID',
                'finance_session_user': 'Utilisateur',
                'finance_session_start': 'Début',
                'finance_session_end': 'Fin',
                'finance_session_fund': 'Fond',
                'finance_session_sales': 'Ventes',
                'finance_session_diff': 'Différence',
                'finance_trans_date': 'Date',
                'finance_trans_type': 'Type',
                'finance_trans_amount': 'Montant',
                'finance_trans_desc': 'Description',
                'dialog_open_session_title': 'Ouvrir une Session Caisse',
                'dialog_open_session_label': 'Entrez le montant initial de la caisse:',
                'dialog_open_session_fund': 'Fond de Caisse:',
                'dialog_close_session_title': 'Fermer la Session Caisse',
                'dialog_close_session_info': 'Session en cours:',
                'dialog_close_session_fund_initial': 'Fond Initial:',
                'dialog_close_session_sales_cash': 'Ventes Espèces:',
                'dialog_close_session_theoretical': 'Total Théorique:',
                'dialog_close_session_real': '💵 Montant Réel Compté:',
                'dialog_close_session_to_safe': '🏦 Verser au Coffre:',
                'dialog_close_session_notes': 'Notes:',
                'dialog_close_session_btn': '✓ Fermer & Transférer',
                'dialog_deposit_title': 'Dépôt au Coffre',
                'dialog_deposit_amount': 'Montant:',
                'dialog_deposit_desc': 'Description:',
                'dialog_deposit_placeholder': 'Raison du dépôt...',
                'dialog_deposit_btn': '✓ Déposer',
                'msg_session_opened': 'Session ouverte avec succès',
                'msg_session_closed': 'Session fermée. Différence: {} DA',
                'msg_session_already_open': 'Une session est déjà ouverte',
                'msg_no_session_open': 'Aucune session ouverte',
                'msg_deposit_success': 'Dépôt effectué',
                'msg_invalid_amount': 'Montant invalide',
                'msg_insufficient_balance': 'Solde insuffisant. Disponible: {} DA',
                
                # Finance - Expense (New)
                'btn_expense': '💸 Dépense',
                'dialog_expense_title': '💸 Enregistrer une Dépense',
                'label_expense_category': 'Catégorie:',
                'label_expense_amount': 'Montant:',
                'label_expense_desc': 'Description:',
                'placeholder_expense_desc': 'Détails de la dépense...',
                'btn_expense_save': '✓ Enregistrer',
                'msg_expense_success': 'Dépense de {:.2f} DA enregistrée',
                'expense_cat_supplies': 'Fournitures',
                'expense_cat_transport': 'Transport',
                'expense_cat_food': 'Repas',
                'expense_cat_cleaning': 'Nettoyage',
                'expense_cat_repair': 'Réparation',
                'expense_cat_other': 'Autre',
                
                # Finance - Improved Close Session
                'dialog_close_recap': '📋 Récapitulatif Session',
                'label_expenses': 'Dépenses:',
                'label_expected_total': 'Total Attendu:',
                'label_keep_fund': '📌 Fond à Garder (demain):',
                'label_to_safe': '🏦 Vers Coffre:',
                'msg_keep_exceeds': 'Le montant à garder ne peut pas dépasser le montant compté',
                'msg_report_generated': '📊 Rapport journalier généré!',

                # Home Page
                'dashboard_title': 'Tableau de Bord',
                'greeting_morning': 'Bonjour',
                'greeting_afternoon': 'Bon après-midi',
                'greeting_evening': 'Bonsoir',
                
                'stats_sales': 'Ventes Aujourd\'hui',
                'stats_turnover': 'Chiffre d\'affaires',
                'stats_products': 'Produits',
                'stats_in_stock': 'En stock',
                'stats_expiration': 'Expiration',
                'stats_expiring_soon': 'Expire bientôt',
                'stats_alerts': 'Alertes',
                'stats_low_stock': 'Stock faible',
                
                'scan_title': 'Scan Rapide',
                'scan_subtitle': 'Scannez un produit pour l\'ajouter au panier',
                'scan_placeholder': 'Code-barres...',
                'scan_btn': '🛒 Ajouter',
                
                'quick_access_title': '🚀 Accès Rapide',
                'qa_pos_title': 'Caisse',
                'qa_pos_sub': 'Vente rapide',
                'qa_products_title': 'Produits',
                'qa_products_sub': 'Gérer stock',
                'qa_customers_title': 'Clients',
                'qa_customers_sub': 'Fidélité',
                'qa_suppliers_title': 'Fournisseurs',
                'qa_suppliers_sub': 'Dettes',
                'qa_reports_title': 'Rapports',
                'qa_reports_sub': 'Statistiques',
                'qa_finance_title': 'Caisse & Coffre',
                'qa_finance_sub': 'Gérer les fonds',
                
                # Date
                'date_format': '%Y/%m/%d',

                # POS Page
                'pos_title': 'Point de Vente',
                'receipt_preview_title': 'Aperçu Ticket #{}',
                'btn_print': '🖨️ Imprimer',
                'btn_close': 'Fermer',
                'msg_success': 'Succès',
                'msg_error': 'Erreur',
                
                'return_dialog_title': 'Gestion des Retours / Annulations',
                'label_sale': 'Vente:',
                'btn_search': '🔍 Rechercher',
                'placeholder_search_sale': 'ID Vente ou Numéro Ticket...',
                'col_product': 'Produit',
                'col_qty_bought': 'Qté Achetée',
                'col_unit_price': 'Prix Unit.',
                'col_qty_return': 'Qté Retour',
                'col_selection': 'Sélection',
                'btn_cancel_sale': '🗑️ Annuler TOUTE la vente',
                'btn_return_selected': '↩️ Retourner les articles sélectionnés',
                'btn_reprint_ticket': '🖨️ Réimprimer Ticket',
                'msg_sale_not_found': 'Vente introuvable',
                'label_sale_info': 'Vente #{} - Total: {} DA - Date: {}',
                'confirm_cancel_sale_title': 'Confirmer',
                'confirm_cancel_sale_msg': 'Annuler TOTALEMENT cette vente ? Le stock sera restauré.',
                'msg_no_selection': 'Aucun article sélectionné ou quantité nulle',
                
                'label_total': 'TOTAL: {:.2f} DA',
                'label_discount': 'Remise: {:.2f} DA',
                'group_scan': 'Scanner Code-Barres',
                'placeholder_scan': 'Scanner ou entrer le code-barres...',
                'group_search_product': 'Recherche Produit',
                'placeholder_search_product': 'Rechercher par nom...',
                'table_headers_products': ["Code", "Nom", "Prix", "Stock", "Action"],
                'group_calculator': '🧮 Calculatrice (Montant Libre)',
                'btn_add_to_cart': '✅ AJOUTER AU PANIER',
                'group_customer': '👤 Client',
                'placeholder_customer': '🔍 Rechercher un client (optionnel)...',
                'label_cart': '🛒 Panier',
                'table_headers_cart': ["Produit", "Prix", "Qté", "Total", "❌"],
                'group_payment': '💳 Paiement',
                'payment_cash': '💵 Espèces',
                'payment_credit': '📝 Crédit',
                'checkbox_print_ticket': '🖨️ Imprimer le ticket',
                'btn_pay': '💰 PAYER (F9)',
                'btn_clear_cart': '🗑️ Vider',
                'btn_discount': '🏷️ Remise',
                'btn_returns': '↩️ Retour',
                'msg_cart_cleared': 'Panier vidé',
                'msg_confirm_clear': 'Voulez-vous vraiment vider le panier ?',
                'msg_payment_success': 'Paiement effectué avec succès !',
                'msg_add_product_success': 'Produit ajouté',
                'msg_stock_error': 'Stock insuffisant',
                
                # Hold/Retrieve Cart
                'btn_hold': '⏸️ En Attente',
                'btn_retrieve': '📋 Récupérer',
                'btn_retrieve_selected': '✅ Récupérer',
                'btn_delete_selected': '🗑️ Supprimer',
                'msg_cart_empty': 'Le panier est vide',
                'msg_enter_customer_name': 'Nom du client (optionnel):',
                'msg_no_held_carts': 'Aucun panier en attente',
                'title_held_carts': '📋 Paniers en Attente',
                'col_id': 'ID',
                'col_customer': 'Client',
                'col_items': 'Articles',
                'col_total': 'Total',
                'title_info': 'Information',

                # Reports
                'tab_categories': 'Catégories',
                'table_headers_categories_report': ["Catégorie", "Chiffre d'affaires", "Bénéfice", "Meilleur Produit", "Qté"],
                'table_headers_daily': ["Date", "Ventes T.", "Dont Crédit", "Coût", "Bénéfice"],
                'table_headers_products_report': ["Produit", "Qté", "Ventes", "Coût", "Bénéfice"],
                'table_headers_users_report': ["Utilisateur", "Ventes T.", "Dont Crédit", "Coût", "Bénéfice", "Nb Ventes"],
                'label_period': 'Période:',
                'label_to': 'à',
                'btn_refresh_report': 'Actualiser',
                'kpi_turnover': "Chiffre d'Affaires",
                'kpi_net_profit': "Bénéfice Net",
                'kpi_margin': "Marge",
                'kpi_sale_count': "Nombre Ventes",
                'kpi_total_credit': "Crédit Client Total",
                'tab_daily_sales': "Ventes Journalières",
                'tab_top_products': "Top Produits",
                'tab_user_sales': "Par Vendeur",
                'tab_closure': "Clôture (Z)",
                'label_closure_info': "Résumé de la clôture...",
                'btn_print_closure': "🖨️ Imprimer Clôture (Ticket Z)",
                
                # Custom Product Dialog
                'custom_product_title': '➕ Ajouter un Produit Personnalisé',
                'label_product_name': 'Nom du produit:',
                'label_unit_price': 'Prix unitaire:',
                'label_quantity': 'Quantité:',
                'placeholder_product_name': 'Ex: Service, Réparation, Article divers...',
                'btn_cancel': 'Annuler',
                'msg_enter_product_name': 'Veuillez entrer un nom de produit',
                'msg_valid_price': 'Veuillez entrer un prix valide',
                'msg_added_to_cart': '{} x{} ajouté au panier',
                
                # Payment & Messages
                'msg_cart_empty_pay': 'Ajoutez des produits avant de payer',
                'msg_client_required_credit': 'Vous devez sélectionner un client pour un paiement à crédit',
                'msg_credit_limit_exceeded': '⚠️ Limite de Crédit Dépassée',
                'msg_credit_limit_details': "Ce client a atteint sa limite de crédit!\n\nLimite: {:.2f} DA\nCrédit Actuel: {:.2f} DA\nCette Vente: {:.2f} DA\nNouveau Total: {:.2f} DA\n\nContactez un administrateur pour autoriser cette vente.",
                'msg_override_credit': '⚠️ Limite Dépassée - Confirmer?',
                'msg_override_credit_details': "Attention: Ce client dépasse sa limite de crédit!\n\nLimite: {:.2f} DA\nNouveau Total: {:.2f} DA\n\nVoulez-vous autoriser cette vente exceptionnellement?",
                'msg_sale_recorded': 'Vente #{} enregistrée avec succès!',
                'msg_amount_positive': 'Le montant doit être supérieur à 0',
                'product_misc': 'Produit Divers',
                'title_success': '✅ Succès',
                'title_warning': 'Attention',
                'title_error': 'Erreur',
                
                # Customers Page
                'customers_title': '👥 Gestion des Clients',
                'customers_subtitle': 'Gérez vos clients et leur crédit',
                'placeholder_search_customer': '🔍 Rechercher client...',
                'filter_all_customers': 'Tous les clients',
                'filter_with_debt': 'Avec dettes (Crédit > 0)',
                'filter_best_customers': 'Meilleurs clients',
                'btn_new_customer': '➕ Nouveau Client',
                'table_headers_customers': ["Code", "Nom", "Téléphone", "Dette (Crédit)", "Total Achats", "Actions"],
                'btn_edit': '✏️',
                'btn_pay_debt': '💰',
                'btn_delete': '🗑️',
                'btn_history': '📜',
                'tooltip_edit': 'Modifier',
                'tooltip_pay_debt': 'Régler Dette',
                'tooltip_delete': 'Supprimer',
                'tooltip_history': 'Historique Achats',
                'confirm_delete_customer_title': 'Confirmer',
                'confirm_delete_customer_msg': 'Voulez-vous vraiment supprimer ce client ?',
                'msg_delete_error': 'Impossible de supprimer',
                
                # Customer Dialog
                'customer_dialog_new': 'Nouveau Client',
                'customer_dialog_edit': 'Modifier Client',
                'label_fullname': 'Nom Complet *:',
                'label_phone': 'Téléphone:',
                'label_email': 'Email:',
                'label_address': 'Adresse:',
                'label_credit_limit': 'Limite de Crédit:',
                
                # Categories
                'menu_categories': '🏷️  Catégories',
                'setup_categories_title': '🗂️ Gestion des Catégories',
                'setup_categories_subtitle': 'Organisez vos produits par familles',
                'placeholder_search_category': '🔍 Rechercher catégorie...',
                'btn_add_category': '➕ Nouvelle Catégorie',
                'col_name': 'Nom',
                'col_name_ar': 'Nom Arabe',
                'col_description': 'Description',
                'col_actions': 'Actions',
                'action_edit': 'Modifier',
                'action_delete': 'Supprimer',
                'category_dialog_new': 'Nouvelle Catégorie',
                'category_dialog_edit': 'Modifier Catégorie',
                'label_name': 'Nom *:',
                'label_name_ar': 'Nom Arabe:',
                'label_description': 'Description:',
                'combo_no_category': 'Aucune catégorie',
                'label_category': 'Catégorie:',
                'msg_name_required': 'Le nom est obligatoire',
                'confirm_delete_title': 'Confirmer suppression',
                'confirm_delete_msg': 'Voulez-vous vraiment supprimer cette catégorie ?',
                'btn_save': 'Enregistrer',
                'msg_name_required': 'Le nom est obligatoire.',
                
                # Payment Dialog
                'payment_dialog_title': 'Règlement Crédit: {}',
                'label_current_credit': 'Crédit actuel: {:g} DA',
                'label_amount_pay': 'Montant à régler:',
                'label_note': 'Note:',
                'placeholder_note': 'Note optionnelle...',
                'label_new_balance': 'Nouveau solde: {:g} DA',
                'checkbox_print_payment': '🖨️ Imprimer reçu de paiement',
                'btn_validate_payment': 'Valider Paiement',
                'receipt_item_payment': 'Règlement Crédit',
                'default_payment_note': 'Paiement crédit client',
                
                # Partial Payment / New Credit Dialog
                'dialog_credit_details_title': 'Détails du Crédit',
                'label_total_to_pay': 'Total à payer: {:.2f} DA',
                'label_cash_paid_now': '💰 Versé maintenant (Espèces):',
                'label_remaining_credit': 'Restant en Crédit: {:.2f} DA',
                'label_payment_complete': 'Paiement Complet (Cash)',

                # Products Page
                'products_title': '📦 Gestion des Produits',
                'products_subtitle': 'Gérez votre stock, prix et promotions',
                'products_count': '{} Produits',
                'placeholder_search_product_page': '🔍 Rechercher (Nom, Code-barres)...',
                'filter_all_products': 'Tous les produits',
                'filter_low_stock': 'Stock faible',
                'filter_promo': 'En promotion',
                'filter_expiring': 'Expire bientôt',
                'btn_new_product': '➕ Nouveau Produit',
                'btn_import': '📥 Importer',
                'btn_order_report': '📑 Commande',
                'tooltip_order_report': 'Générer une liste de commande pour le stock faible',
                'table_headers_products_page': ["Code", "Nom", "Prix Vente", "Stock", "Expiration", "Promotion", "Actions"],
                'tooltip_print_barcode': 'Imprimer le code-barres',
                'msg_confirm_delete_product': 'Supprimer ce produit ?',
                'msg_no_barcode': "Ce produit n'a pas de code-barres",
                'msg_reportlab_missing': "Le module 'reportlab' est requis pour l'impression des codes-barres.\n\nInstallez-le avec: pip install reportlab",
                'title_missing_module': 'Module manquant',

                # Product Dialog
                'product_dialog_new': 'Nouveau Produit',
                'product_dialog_edit': 'Modifier Produit',
                'tab_general': 'Général',
                'tab_price_stock': 'Prix & Stock',
                'label_barcode': 'Code-barres:',
                'label_name_ar': 'Nom (Arabe):',
                'label_supplier': 'Fournisseur:',
                'label_description': 'Description:',
                'combo_no_supplier': '--- Aucun ---',
                'label_purchase_price': "Prix d'achat:",
                'label_selling_price': "Prix de vente *:",
                'label_initial_stock': "Stock initial:",
                'label_min_stock': "Alert Stock Min:",
                'checkbox_expiry_date': "Date d'expiration ?",
                'msg_name_price_required': "Le nom et le prix de vente sont obligatoires.",
                
                # Tutorial
                'tutorial_content': """
                <h2>📖 Guide d'utilisation v1.0</h2>
                
                <h3>🛒 Caisse & Paiement</h3>
                <ul>
                    <li><b>Scanner</b> : Utilisez la douchette ou tapez le code.</li>
                    <li><b>Produits Divers</b> : Ajoutez des articles hors stock rapidement.</li>
                    <li><b>Paiement Mixte</b> : Sélectionnez "Crédit" pour payer une partie en espèces et le reste à crédit.</li>
                    <li><b>Ticket</b> : Cochez la case pour imprimer ou désactiver l'impression.</li>
                </ul>
                
                <h3>⚡ Raccourcis Rapides (F9)</h3>
                <ul>
                    <li><b>Accès</b> : Appuyez sur F9 ou cliquez sur le bouton "Raccourcis".</li>
                    <li><b>Gestion</b> : Ajoutez vos produits fréquents avec des <b>Photos</b>.</li>
                    <li><b>Images</b> : Les images sont sauvegardées et affichées en caisse.</li>
                </ul>
                
                <h3>💾 Sauvegardes & Sécurité</h3>
                <ul>
                    <li><b>ZIP Complet</b> : Le système crée une sauvegarde complète (.zip) incluant Base de Données + Photos.</li>
                    <li><b>Excel</b> : Un fichier .xlsx est aussi créé pour consulter vos listes facilement.</li>
                    <li><b>Auto</b> : La sauvegarde est automatique (par défaut toutes les 5h).</li>
                </ul>
                
                <h3>👥 Clients & Dettes</h3>
                <ul>
                    <li><b>Suivi</b> : Historique complet des achats et crédits.</li>
                    <li><b>Alertes</b> : Notification si la limite de crédit est dépassée.</li>
                    <li><b>Remboursement</b> : Dans "Clients", cliquez sur 💰 pour régler une dette.</li>
                </ul>
                """,

                # Suppliers Page
                'suppliers_title': '🏭 Gestion des Fournisseurs',
                'suppliers_subtitle': 'Gérez vos fournisseurs et vos dettes',
                'placeholder_search_supplier': '🔍 Rechercher fournisseur...',
                'filter_all_suppliers': 'Tous les fournisseurs',
                'filter_debt_suppliers': 'Avec dettes',
                'btn_new_supplier': '➕ Nouveau Fournisseur',
                'table_headers_suppliers': ["Code", "Entreprise", "Contact", "Téléphone", "Total Achats", "Dettes à payer", "Actions"],
                'btn_edit': 'Modifier',
                'btn_delete': 'Supprimer',
                'btn_add_purchase': 'Ajouter Achat',
                'btn_pay_debt': 'Régler Dette',
                'msg_confirm_delete_supplier': "Voulez-vous vraiment supprimer ce fournisseur ?\n(Impossible s'il a des produits ou des dettes)",
                
                # Supplier Dialog
                'supplier_dialog_new': 'Nouveau Fournisseur',
                'supplier_dialog_edit': 'Modifier Fournisseur',
                'label_company': 'Entreprise *:',
                'label_contact': 'Contact:',
                'label_phone': 'Téléphone:',
                'label_email': 'Email:',
                'label_address': 'Adresse:',
                'msg_company_required': "Le nom de l'entreprise est obligatoire.",

                # Debt Dialog
                'debt_dialog_title': 'Règlement Dette: {}',
                'label_current_debt': 'Dette actuelle: {} DA',
                'label_payment_amount': 'Montant à régler:',
                'label_payment_note': 'Description:',
                'placeholder_payment_note': 'Description du paiement...',
                'btn_validate_payment': 'Valider Paiement',

                # Purchase Dialog (Advanced)
                'purchase_dialog_title': 'Ajouter Achat: {}',
                'purchase_search_group': '🔍 Recherche Produit',
                'placeholder_search_scan': 'Scanner code-barres ou taper nom...',
                'table_header_product': 'Produit',
                'table_header_stock': 'Stock',
                'table_header_purchase_price': 'Prix Achat',
                'table_header_action': 'Action',
                'group_cart': "🛒 Panier d'achat - {}",
                'table_header_qty': 'Qté',
                'table_header_unit_price': 'Prix U.',
                'table_header_total': 'Total',
                'group_payment': '💳 Paiement & Validation',
                'label_total_to_pay': 'TOTAL À PAYER:',
                'label_payment_source': 'Source de Paiement:',
                'opt_safe': 'Coffre (Espèces)',
                'opt_credit': 'Crédit (Dette)',
                'opt_other': 'Autre (Caisse)',
                'label_amount_paid': 'Montant Payé:',
                'label_remaining_debt': 'Reste (Dette):',
                'label_notes': 'Notes (Ref. Facture):',
                'btn_validate_purchase': '✓ Valider Achat',
                'msg_cart_empty': 'Le panier est vide',
                'msg_paid_exceeds_total': 'Le montant payé ne peut pas dépasser le total',
                'msg_confirm_purchase': 'Valider l\'achat de {} articles pour {:.2f} DA ?',
                'msg_purchase_success': 'Achat enregistré avec succès',
                'msg_amount_warning': "Le montant doit être supérieur à 0",

                # Sales History Page
                'sales_history_title': '📜 Historique des Ventes',
                'sales_history_subtitle': 'Consultez et gérez toutes vos transactions passées',
                'btn_export_excel': '📂 Exporter Excel',
                'placeholder_search_sales': 'Rechercher Ticket # ou Client...',
                'label_date_from': 'Du:',
                'label_date_to': 'Au:',
                'filter_status_all': 'Tous les statuts',
                'filter_status_completed': 'Complétée',
                'filter_status_cancelled': 'Annulée',
                'filter_status_returned': 'Retournée',
                'table_headers_sales': ["ID", "Num Ticket", "Date", "Client", "Vendeur", "Total", "Statut", "Bénéfice"],
                'btn_view_details': '👁️ Voir Détails',
                'btn_reprint': '🖨️ Réimprimer',
                'btn_return_action': '↩️ Retourner',
                'summary_total_ca': 'Total CA: {:.2f} DA',
                'summary_total_profit': 'Bénéfice Est.: {:.2f} DA',
                'msg_export_success': 'Historique exporté vers:\n{}',
                'msg_print_sent': 'Ticket envoyé à l\'imprimante.',
                
                # Sale Details Dialog
                'sale_details_title': 'Détails de la Vente #{}',
                'label_loading': 'Chargement...',
                'table_headers_sale_items': ["Produit", "Quantité", "Prix Unit.", "Sous-total"],
                'label_dialog_total': 'Total: {:.2f} DA',
                'btn_close_dialog': 'Fermer',
                'label_sale_info_detailed': "Date: {}\nClient: {}\nVendeur: {}\nStatut: {}",
                'msg_sale_not_found_dialog': "Vente introuvable",

                # Settings Page
                'settings_title': '⚙️ Paramètres',
                'settings_subtitle': 'Configuration générale et gestion des utilisateurs',
                'tab_users': '👥 Utilisateurs',
                'tab_data': '💾 Données',
                'tab_store': '🏪 Magasin',
                'label_store_name': 'Nom du magasin:',
                'label_store_phone': 'Téléphone:',
                'label_store_address': 'Adresse:',
                'label_store_city': 'Ville:',
                'label_store_nif': 'NIF:',
                'label_store_nis': 'NIS:',
                'label_store_rc': 'RC:',
                'label_store_ai': 'AI:',
                'label_expiry_days': 'Alerte Expiration (Jours):',
                'suffix_days': 'Jours',
                'btn_save_store': '💾 Enregistrer',
                'msg_store_saved': 'Paramètres du magasin enregistrés',
                'tab_tutorial': '📚 Tutoriel',
                'tab_about': 'ℹ️ À propos',
                'group_backup_config': 'Configuration Sauvegarde Auto',
                'check_auto_backup': 'Activer la sauvegarde automatique',
                'suffix_hours': 'heures',
                'label_interval': 'Intervalle:',
                'btn_save_config': 'Enregistrer Config',
                'group_export': 'Exportation Manuelle',
                'label_export_info': 'Créez une sauvegarde complète de la base de données.',
                'btn_create_backup': 'Créer une sauvegarde',
                'group_import': 'Importation / Restauration',
                'label_import_info': 'Restaurez les données depuis un fichier .db ou .sql.',
                'btn_restore_backup': 'Restaurer une sauvegarde',
                'group_reset': '⚠️ Zone de Danger',
                'label_reset_info': 'ATTENTION: Cette action effacera toutes les ventes, produits et clients !',
                'btn_reset_all': '🗑️ Réinitialiser TOUTES les données',
                'label_user_list': 'Liste des utilisateurs',
                'table_headers_users': ['ID', 'Nom Utilisateur', 'Nom Complet', 'Rôle', 'Dernière Connexion', 'État', 'Actions'],
                'btn_refresh': 'Actualiser',
                'group_add_user': 'Ajouter / Modifier Utilisateur',
                'role_cashier': 'Caissier',
                'role_admin': 'Administrateur',
                'label_username': 'Nom d\'utilisateur:',
                'label_password': 'Mot de passe:',
                'label_fullname_user': 'Nom Complet:',
                'label_role': 'Rôle:',
                'btn_create_user': 'Créer Utilisateur',
                # Tutorial
                'tutorial_content': """
                <h2>📖 Guide d'utilisation v1.0</h2>
                
                <h3>🛒 Caisse & Paiement</h3>
                <ul>
                    <li><b>Scanner</b> : Utilisez la douchette ou tapez le code.</li>
                    <li><b>Produits Divers</b> : Ajoutez des articles hors stock rapidement.</li>
                    <li><b>Paiement Mixte</b> : Sélectionnez "Crédit" pour payer une partie en espèces et le reste à crédit.</li>
                    <li><b>Ticket</b> : Cochez la case pour imprimer ou désactiver l'impression.</li>
                </ul>
                
                <h3>⚡ Raccourcis Rapides (F9)</h3>
                <ul>
                    <li><b>Accès</b> : Appuyez sur F9 ou cliquez sur le bouton "Raccourcis".</li>
                    <li><b>Gestion</b> : Ajoutez vos produits fréquents avec des <b>Photos</b>.</li>
                    <li><b>Images</b> : Les images sont sauvegardées et affichées en caisse.</li>
                </ul>
                
                <h3>💾 Sauvegardes & Sécurité</h3>
                <ul>
                    <li><b>ZIP Complet</b> : Le système crée une sauvegarde complète (.zip) incluant Base de Données + Photos.</li>
                    <li><b>Excel</b> : Un fichier .xlsx est aussi créé pour consulter vos listes facilement.</li>
                    <li><b>Auto</b> : La sauvegarde est automatique (par défaut toutes les 5h).</li>
                </ul>
                
                <h3>👥 Clients & Dettes</h3>
                <ul>
                    <li><b>Suivi</b> : Historique complet des achats et crédits.</li>
                    <li><b>Alertes</b> : Notification si la limite de crédit est dépassée.</li>
                    <li><b>Remboursement</b> : Dans "Clients", cliquez sur 💰 pour régler une dette.</li>
                </ul>
                </ul>
                
                <h3>🛡️ Administration (Nouveau)</h3>
                <ul>
                    <li><b>Ajouter Admin/Caissier</b> : Dans "Paramètres > Utilisateurs".</li>
                    <li><b>Permissions</b> : Cliquez sur le bouclier 🛡️ pour choisir ce que chaque utilisateur peut faire (Supprimer, voir les prix, etc.).</li>
                </ul>
                """,
                'perm_make_sales': 'Effectuer des ventes',
                'perm_process_returns': 'Effectuer des retours',
                'perm_manage_products': 'Gérer les produits (Ajout/Modif)',
                'perm_view_products': 'Voir les produits',
                'perm_manage_categories': 'Gérer les catégories',
                'perm_manage_customers': 'Gérer les clients',
                'perm_view_customers': 'Voir les clients',
                'perm_manage_suppliers': 'Gérer les fournisseurs',
                'perm_view_suppliers': 'Voir les fournisseurs',
                'perm_manage_users': 'Gérer les utilisateurs',
                'perm_view_reports': 'Voir les rapports',
                'perm_manage_settings': 'Modifier les paramètres',
                'perm_manage_backups': 'Gérer les sauvegardes',
                'perm_view_audit_log': "Voir le journal d'audit",
                'perm_manage_shortcuts': 'Gérer les raccourcis POS',
                'perm_view_sales_history': 'Voir l\'historique des ventes',
                'perm_cancel_sales': 'Annuler une vente complète',
                'perm_manage_reset': 'Réinitialiser l\'application (Danger)',
                'perm_override_credit_limit': 'Outrepasser la limite de crédit',
                
                # Returns Page
                'tab_new_return': 'Nouveau Retour',
                'tab_history_returns': 'Historique des Retours',
                'table_history_headers_returns': ["N° Retour", "Vente Originale", "Date", "Montant", "Caissier", "Raison"],
                'btn_refresh': 'Actualiser',
                'btn_reprint_ticket_history': 'Réimprimer le Ticket',
                
                # POS
                'placeholder_search_product': 'Rechercher un produit (Nom/Code)',
                
                # POS Product Search
                'placeholder_search_product_extended': 'Rechercher un produit (Nom, Code-barres)...',
                'table_headers_product_search': ["Code-barres", "Nom", "Prix", "Stock", "Action"],
                'btn_close': 'Fermer',
                
                # Shortcuts
                'tooltip_edit': 'Modifier',
                'tooltip_delete': 'Supprimer',
                'msg_access_denied': 'Accès refusé',
                'msg_perm_required_shortcuts': 'Permission requise: manage_shortcuts',
                
                'msg_config_saved': 'Configuration enregistrée !',
                'msg_backup_success': 'Sauvegarde créée avec succès:\n{}',
                'msg_confirm_import': 'Voulez-vous vraiment écraser la base de données actuelle ?\nCette action est irréversible.',
                'msg_import_success': 'Base de données restaurée avec succès.\n{}',
                'msg_confirm_reset_1': 'ÊTES-VOUS SÛR ?\nCela va supprimer TOUTES les données !',
                'title_password_check': 'Vérification',
                'msg_password_check': 'Entrez le mot de passe Admin pour confirmer:',
                'msg_reset_success': 'L\'application a été réinitialisée avec succès.',
                
                # Tobacco & Units
                'checkbox_is_tobacco': 'Produit Tabac/Chema',
                'label_parent_product': 'Produit Parent (Paquet):',
                'label_packing_qty': 'Unités par paquet:',
                'combo_no_parent': 'Aucun (produit indépendant)',
                'tab_tobacco': 'Tabac / Liaison',
                'section_auto_create': "Création automatique d'Unités:",
                'checkbox_auto_create': "Créer aussi le produit Unité",
                'label_unit_price_tobacco': "Prix Unité:",
                'section_manual_link': "🔗 Liaison manuelle:",
                'msg_pack_unit_created': "Paquet + Unité créés avec succès!",
                'tab_tobacco_report': "Situation Tabac",
                'tobacco_report_title': "Situation Tabac vs Autres ({} au {})",
                'col_category': "Catégorie",
                'col_revenue': "Chiffre d'Affaires",
                'col_cost': "Coût Achat",
                'col_net_profit': "Bénéfice Net",
                'col_margin': "Marge %",
                'row_tobacco': "🚬 Tabac / Cigarettes / Chema",
                'row_others': "🛍️ Autres Produits",
                'row_others': "🛍️ Autres Produits",
                'row_total': "TOTAL GÉNÉRAL",

                # Unit Auto-Create
                'unit_of': "Unité de {}",
                'unit_suffix_fr': " (Unité)",
                'unit_suffix_ar': " (وحدة)",
                
                # Reorder Report
                'reorder_report_title': "Liste de Commande Fournisseur",
                'reorder_generated_on': "Généré le: {}",
                'unknown_supplier': "Fournisseur Inconnu",
                'col_product': "Produit",
                'col_current_stock': "Stock Actuel",
                'col_min_stock': "Stock Min",
                'col_qty_to_order': "Qté à Commander",

                # Customer History
                'history_title_customer': 'Historique: {}',
                'label_current_debt': 'Dette Actuelle',
                'tab_financial_history': 'Historique Financier',
                'tab_purchase_history': 'Historique des Achats',
                'col_date': 'Date',
                'col_type': 'Type',
                'col_amount': 'Montant',
                'col_notes': 'Notes',
                'col_user': 'Utilisateur',
                'type_payment': 'Paiement',
                'type_credit': 'Crédit',
                'col_sale_no': 'N° Vente',
                'col_payment_method': 'Mode Paiement',
                'col_cashier': 'Caissier',

            # Returns Page
                'returns_title': '↩️ Gestion des Retours',
                'returns_subtitle': 'Gérer les remboursements et retours de stock',
                'placeholder_search_return': 'Entrez le numéro de ticket (ex: VNT-...) ou l\'ID de vente',
                'btn_search_return': '🔍 Rechercher',
                'btn_reprint_ticket_return': '🖨️ Réimprimer Ticket',
                'btn_cancel_sale_return': '🗑️ Annuler toute la vente',
                'btn_process_return': '↩️ Valider le Retour',
                'table_headers_returns': ['Produit', 'Quantité Achetée', 'Prix Unit.', 'Qté à Retourner', 'Sélection'],
                'msg_select_items_return': 'Veuillez sélectionner au moins un article avec une quantité supérieure à 0.',
                'msg_confirm_partial_return': 'Voulez-vous valider ce retour partiel ?',
                'msg_return_success': 'Retour effectué avec succès !',
                'confirm_cancel_sale_msg': 'Voulez-vous vraiment annuler toute la vente ?\nTous les articles seront remis en stock.',

                # Reports Page
                'reports_title': '📊 Rapports & Statistiques',
                'label_period': '📅 Période:',
                'label_to': ' à ',
                'btn_refresh_report': '🔄 Actualiser',
                'kpi_turnover': "Chiffre d'Affaires",
                'kpi_net_profit': 'Bénéfice Net',
                'kpi_margin': 'Marge',
                'kpi_sale_count': 'Nombre de Ventes',
                'table_headers_daily': ['Date', 'Ventes', 'Coût', 'Bénéfice'],
                'tab_daily_sales': '📅 Ventes par Jour',
                'table_headers_products_report': ['Produit', 'Qté Vendue', 'CA', 'Bénéfice', 'Marge'],
                'tab_top_products': '📦 Top Produits',
                'table_headers_users_report': ['Utilisateur', 'Rôle', 'Nb Ventes', 'CA Total', 'Bénéfice'],
                'tab_user_sales': '👤 Ventes par Utilisateur',
                'label_closure_info': 'Sélectionnez une période et cliquez sur Actualiser',
                'btn_print_closure': '🖨️ Imprimer Résumé de Clôture',
                'tab_closure': '💰 Résumé de Clôture',
                'closure_summary_title': 'Résumé Financier ({} au {})',
                'closure_cash': 'Ventes Comptant (Cash):',
                'closure_credit': 'Ventes à Crédit:',
                'closure_other': 'Autres Paiements:',
                'closure_total': "CHIFFRE D'AFFAIRES TOTAL:",
                'closure_returns': 'Total Retours / Remboursements:',
                
                # Shortcuts Management (New)
                'shortcuts_mgmt_title': 'Gestion des Raccourcis',
                'shortcuts_mgmt_subtitle': "Configurez les boutons d'accès rapide",
                'btn_new_shortcut': '➕ Nouveau Raccourci',
                'no_shortcuts_found': "Aucun raccourci configuré.\nCliquez sur 'Nouveau Raccourci' pour commencer.",
                'confirm_delete_shortcut': 'Voulez-vous vraiment supprimer ce raccourci ?',
                'shortcut_edit_title': 'Modifier Raccourci',
                'shortcut_new_title': 'Nouveau Raccourci',
                'config_section': 'Configuration',
                'scan_barcode_placeholder': 'Scanner code-barres...',
                'barcode_label': 'Code-barres:',
                'product_label': 'Produit:',
                'category_label': 'Catégorie:',
                'label_input_label': 'Libellé:',
                'price_label': 'Prix unitaire:',
                'select_product_default': '-- Produit Personnalisé --',
                'image_section': 'Image (Optionnel)',
                'btn_upload': '📂 Choisir',
                'btn_clear': '❌ Effacer',
                'btn_cancel': 'Annuler',
            },
            'ar': {
                # General
                'app_title': 'DamDev POS',
                'slogan': 'إدارة المخزون\nبسيطة وذكية.',
                'version': 'نسخة {}',
                
                # Login
                'welcome_back': 'مرحباً بعودتك ! 👋',
                'enter_credentials': 'الرجاء إدخال بيانات الدخول.',
                'username': 'اسم المستخدم',
                'password': 'كلمة المرور',
                'login_btn': 'تسجيل الدخول',
                'login_loading': 'جاري الاتصال...',
                'default_creds': 'المدير الافتراضي: admin / admin123',
                'login_error': 'خطأ في تسجيل الدخول',
                'system_error': 'خطأ في النظام: {}',
                'msg_login_failed': 'اسم المستخدم أو كلمة المرور غير صحيحة',
                'msg_account_disabled': 'هذا الحساب معطل',
                
                # Sidebar / Menu
                'menu_home': '🏠  الرئيسية (F1)',
                'menu_pos': '🛒  نقطة البيع (F2)',
                'menu_products': '📦  المنتجات (F3)',
                'menu_customers': '👥  العملاء (F4)',
                'menu_suppliers': '🏭  الموردين (F5)',
                'menu_reports': '📊  التقارير (F6)',
                'menu_returns': '↩️  المرتجعات (F7)',
                'menu_history': '📜  السجل (F8)',
                'menu_settings': '⚙️  الإعدادات (F10)',
                'menu_logout': '🚪  تسجيل الخروج',
                'confirm_logout_title': 'تسجيل الخروج',
                'confirm_logout_msg': 'هل تريد تسجيل الخروج؟',

                # Finance (خزينة و صندوق)
                'finance_title': '💰 إدارة الخزينة و الصندوق',
                'finance_caisse': 'الخزينة',
                'finance_coffre': 'الصندوق',
                'finance_caisse_closed': 'مغلقة',
                'btn_open_session': '🔓 فتح الخزينة',
                'btn_close_session': '🔒 إغلاق الخزينة',
                'btn_deposit_safe': '💵 إيداع في الصندوق',
                'finance_history_sessions': '📋 سجل الجلسات',
                'finance_history_safe': '🏦 حركات الصندوق',
                'finance_session_id': 'المعرّف',
                'finance_session_user': 'المستخدم',
                'finance_session_start': 'البداية',
                'finance_session_end': 'النهاية',
                'finance_session_fund': 'رأس المال',
                'finance_session_sales': 'المبيعات',
                'finance_session_diff': 'الفرق',
                'finance_trans_date': 'التاريخ',
                'finance_trans_type': 'النوع',
                'finance_trans_amount': 'المبلغ',
                'finance_trans_desc': 'الوصف',
                'dialog_open_session_title': 'فتح جلسة خزينة',
                'dialog_open_session_label': 'أدخل مبلغ رأس مال الخزينة:',
                'dialog_open_session_fund': 'رأس مال الخزينة:',
                'dialog_close_session_title': 'إغلاق جلسة الخزينة',
                'dialog_close_session_info': 'الجلسة الحالية:',
                'dialog_close_session_fund_initial': 'رأس المال الأولي:',
                'dialog_close_session_sales_cash': 'مبيعات نقدية:',
                'dialog_close_session_theoretical': 'الإجمالي النظري:',
                'dialog_close_session_real': '💵 المبلغ الفعلي المحسوب:',
                'dialog_close_session_to_safe': '🏦 إيداع في الصندوق:',
                'dialog_close_session_notes': 'ملاحظات:',
                'dialog_close_session_btn': '✓ إغلاق و تحويل',
                'dialog_deposit_title': 'إيداع في الصندوق',
                'dialog_deposit_amount': 'المبلغ:',
                'dialog_deposit_desc': 'الوصف:',
                'dialog_deposit_placeholder': 'سبب الإيداع...',
                'dialog_deposit_btn': '✓ إيداع',
                'msg_session_opened': 'تم فتح الجلسة بنجاح',
                'msg_session_closed': 'تم إغلاق الجلسة. الفرق: {} د.ج',
                'msg_session_already_open': 'توجد جلسة مفتوحة بالفعل',
                'msg_no_session_open': 'لا توجد جلسة مفتوحة',
                'msg_deposit_success': 'تم الإيداع بنجاح',
                'msg_invalid_amount': 'مبلغ غير صالح',
                'msg_insufficient_balance': 'رصيد غير كاف. المتوفر: {} د.ج',
                
                # Finance - Expense (New)
                'btn_expense': '💸 مصروف',
                'dialog_expense_title': '💸 تسجيل مصروف',
                'label_expense_category': 'الفئة:',
                'label_expense_amount': 'المبلغ:',
                'label_expense_desc': 'الوصف:',
                'placeholder_expense_desc': 'تفاصيل المصروف...',
                'btn_expense_save': '✓ حفظ',
                'msg_expense_success': 'تم تسجيل مصروف {:.2f} د.ج',
                'expense_cat_supplies': 'لوازم',
                'expense_cat_transport': 'نقل',
                'expense_cat_food': 'وجبات',
                'expense_cat_cleaning': 'تنظيف',
                'expense_cat_repair': 'إصلاح',
                'expense_cat_other': 'أخرى',
                
                # Finance - Improved Close Session
                'dialog_close_recap': '📋 ملخص الجلسة',
                'label_expenses': 'المصاريف:',
                'label_expected_total': 'الإجمالي المتوقع:',
                'label_keep_fund': '📌 المبلغ المحتفظ به (غداً):',
                'label_to_safe': '🏦 إلى الصندوق:',
                'msg_keep_exceeds': 'المبلغ المحتفظ به لا يمكن أن يتجاوز المبلغ المحسوب',
                'msg_report_generated': '📊 تم إنشاء التقرير اليومي!',

                # Categories
                'menu_categories': '🏷️  الفئات',
                'setup_categories_title': '🗂️ إدارة الفئات',
                'setup_categories_subtitle': 'تنظيم المنتجات حسب العائلة',
                'placeholder_search_category': '🔍 بحث عن فئة...',
                'btn_add_category': '➕ فئة جديدة',
                'col_name': 'الاسم',
                'col_name_ar': 'الاسم بالعربية',
                'col_description': 'الوصف',
                'col_actions': 'إجراءات',
                'action_edit': 'تعديل',
                'action_delete': 'حذف',
                'category_dialog_new': 'فئة جديدة',
                'category_dialog_edit': 'تعديل الفئة',
                'label_name': 'الاسم *:',
                'label_name_ar': 'الاسم بالعربية:',
                'label_description': 'الوصف:',
                'combo_no_category': 'بدون فئة',
                'label_category': 'الفئة:',
                'msg_name_required': 'الاسم مطلوب.',
                'confirm_delete_title': 'تأكيد الحذف',
                'confirm_delete_msg': 'هل أنت متأكد من حذف هذه الفئة؟',
                
                # Permissions & Reset (New)
                'perm_manage_finance': 'Gérer la Trésorerie (Caisse/Coffre)',
                'msg_confirm_reset_1': "Êtes-vous sûr de vouloir réinitialiser la base de données ?\n\nCETTE ACTION EST IRRÉVERSIBLE !\nToutes les ventes, produits et clients seront supprimés.",
                'title_password_check': "Vérification Requis",
                'msg_password_check': "Veuillez entrer votre mot de passe pour confirmer l'action :",
                
                # Home Page
                'dashboard_title': 'لوحة القيادة',
                'greeting_morning': 'صباح الخير',
                'greeting_afternoon': 'مساء الخير',
                'greeting_evening': 'مساء الخير',
                
                'stats_sales': 'مبيعات اليوم',
                'stats_turnover': 'إجمالي المبيعات',
                'stats_products': 'المنتجات',
                'stats_in_stock': 'في المخزن',
                'stats_expiration': 'انتهاء الصلاحية',
                'stats_expiring_soon': 'تنتهي قريباً',
                'stats_alerts': 'التحذيرات',
                'stats_low_stock': 'المخزون المنخفض',
                
                'scan_title': 'مسح سريع',
                'scan_subtitle': 'امسح المنتج لإضافته إلى السلة',
                'scan_placeholder': 'الباركود...',
                'scan_btn': '🛒 إضافة',
                
                'quick_access_title': '🚀 وصول سريع',
                'qa_pos_title': 'نقطة البيع',
                'qa_pos_sub': 'بيع سريع',
                'qa_products_title': 'المنتجات',
                'qa_products_sub': 'إدارة المخزون',
                'qa_customers_title': 'العملاء',
                'qa_customers_sub': 'إدارة العملاء',
                'qa_suppliers_title': 'الموردين',
                'qa_suppliers_sub': 'إدارة الموردين',
                'qa_reports_title': 'التقارير',
                'qa_reports_sub': 'عرض الإحصائيات',
                'qa_finance_title': 'الخزينة والصندوق',
                'qa_finance_sub': 'إدارة الأموال',
                
                # Date
                'date_format': '%Y/%m/%d',

                # POS Page
                'pos_title': 'نقطة البيع',
                'receipt_preview_title': 'معاينة الإيصال #{}',
                'btn_print': '🖨️ طباعة',
                'btn_close': 'إغلاق',
                'msg_success': 'العملية ناجحة',
                'msg_error': 'خطأ',
                
                'return_dialog_title': 'إدارة المرتجعات / الإلغاء',
                'label_sale': 'البيع:',
                'btn_search': '🔍 بحث',
                'placeholder_search_sale': 'رقم البيع أو التذكرة...',
                'col_product': 'المنتج',
                'col_qty_bought': 'الكمية المشتراة',
                'col_unit_price': 'سعر الوحدة',
                'col_qty_return': 'كمية الإرجاع',
                'col_selection': 'تحديد',
                'btn_cancel_sale': '🗑️ إلغاء البيع بالكامل',
                'btn_return_selected': '↩️ إرجاع المنتجات المحددة',
                'btn_reprint_ticket': '🖨️ إعادة طباعة التذكرة',
                'msg_sale_not_found': 'البيع غير موجود',
                'label_sale_info': 'البيع #{} - الإجمالي: {} د.ج - التاريخ: {}',
                'confirm_cancel_sale_title': 'تأكيد',
                'confirm_cancel_sale_msg': 'هل أنت متأكد من إلغاء هذا البيع بالكامل؟ سيتم استعادة المخزون.',
                'msg_no_selection': 'لم يتم تحديد أي عنصر أو الكمية صفر',
                
                'label_total': 'الإجمالي: {:.2f} د.ج',
                'label_discount': 'الخصم: {:.2f} د.ج',
                'group_scan': 'ماسح الكود',
                'placeholder_scan': 'امسح أو أدخل الكود...',
                'group_search_product': 'بحث عن منتج',
                'placeholder_search_product': 'البحث بالاسم...',
                'table_headers_products': ["الكود", "الاسم", "السعر", "المخزون", "الإجراء"],
                'group_calculator': '🧮 الآلة الحاسبة (مبلغ حر)',
                'btn_add_to_cart': '✅ إضافة إلى السلة',
                'group_customer': '👤 العميل',
                'placeholder_customer': '🔍 بحث عن عميل (اختياري)...',
                'label_cart': '🛒 السلة',
                'table_headers_cart': ["المنتج", "السعر", "الكمية", "الإجمالي", "❌"],
                'group_payment': '💳 الدفع',
                'payment_cash': '💵 نقداً',
                'payment_credit': '📝 أجل (كريدي)',
                'checkbox_print_ticket': '🖨️ طباعة التذكرة',
                'btn_pay': '💰 دفع (F9)',
                'btn_clear_cart': '🗑️ تفريغ',
                'btn_discount': '🏷️ خصم',
                'btn_returns': '↩️ إرجاع',
                'msg_cart_cleared': 'تم تفريغ السلة',
                'msg_confirm_clear': 'هل أنت متأكد من تفريغ السلة؟',
                'msg_payment_success': 'تم الدفع بنجاح!',
                'msg_add_product_success': 'تمت إضافة المنتج',
                'msg_stock_error': 'المخزون غير كاف',
                
                # Hold/Retrieve Cart
                'btn_hold': '⏸️ انتظار',
                'btn_retrieve': '📋 استرداد',
                'btn_retrieve_selected': '✅ استرداد',
                'btn_delete_selected': '🗑️ حذف',
                'msg_cart_empty': 'السلة فارغة',
                'msg_enter_customer_name': 'اسم العميل (اختياري):',
                'msg_no_held_carts': 'لا توجد سلات منتظرة',
                'title_held_carts': '📋 السلات المنتظرة',
                'col_id': 'المعرف',
                'col_customer': 'العميل',
                'col_items': 'العناصر',
                'col_total': 'الإجمالي',
                'title_info': 'معلومات',
                
                # Custom Product Dialog
                'custom_product_title': '➕ إضافة منتج مخصص',
                'label_product_name': 'اسم المنتج:',
                'label_unit_price': 'سعر الوحدة:',
                'label_quantity': 'الكمية:',
                'placeholder_product_name': 'مثال: خدمة، إصلاح، منتج متنوع...',
                'btn_cancel': 'إلغاء',
                'msg_enter_product_name': 'الرجاء إدخال اسم المنتج',
                'msg_valid_price': 'الرجاء إدخال سعر صالح',
                'msg_added_to_cart': '{} x{} تمت إضافته إلى السلة',
                
                # Payment & Messages
                'msg_cart_empty_pay': 'أضف منتجات قبل الدفع',
                'msg_client_required_credit': 'يجب اختيار عميل للدفع بالدين',
                'msg_credit_limit_exceeded': '⚠️ تم تجاوز حد الائتمان',
                'msg_credit_limit_details': "هذا العميل وصل إلى حد الائتمان!\n\nالحد: {:.2f} د.ج\nالائتمان الحالي: {:.2f} د.ج\nهذا البيع: {:.2f} د.ج\nالإجمالي الجديد: {:.2f} د.ج\n\nاتصل بالمدير للموافقة على هذا البيع.",
                'msg_override_credit': '⚠️ تجاوز الحد - تأكيد؟',
                'msg_override_credit_details': "تنبيه: هذا العميل يتجاوز حد الائتمان!\n\nالحد: {:.2f} د.ج\nالإجمالي الجديد: {:.2f} د.ج\n\nهل تريد السماح بهذا البيع استثنائياً؟",
                'msg_sale_recorded': 'تم تسجيل البيع #{} بنجاح!',
                'msg_amount_positive': 'يجب أن يكون المبلغ أكبر من 0',
                'product_misc': 'منتج متنوع',
                'title_success': '✅ نجاح',
                'title_warning': 'تنبيه',
                'title_error': 'خطأ',
                
                # Customers Page
                'customers_title': '👥 إدارة العملاء',
                'customers_subtitle': 'إدارة عملائك وديونهم',
                'placeholder_search_customer': '🔍 بحث عن عميل...',
                'filter_all_customers': 'جميع العملاء',
                'filter_with_debt': 'عليهم ديون (ائتمان > 0)',
                'filter_best_customers': 'أفضل العملاء',
                'btn_new_customer': '➕ عميل جديد',
                'table_headers_customers': ["الكود", "الاسم", "الهاتف", "الدين (كريدي)", "المبيعات", "الإجراءات"],
                'tooltip_edit': 'تعديل',
                'tooltip_pay_debt': 'دفع الدين',
                'tooltip_delete': 'حذف',
                'tooltip_history': 'سجل المشتريات',
                'confirm_delete_customer_title': 'تأكيد الحذف',
                'confirm_delete_customer_msg': 'هل أنت متأكد من حذف هذا العميل؟',
                'msg_delete_error': 'لا يمكن الحذف',
                
                # Customer Dialog
                'customer_dialog_new': 'عميل جديد',
                'customer_dialog_edit': 'تعديل العميل',
                'label_fullname': 'الاسم الكامل *:',
                'label_phone': 'الهاتف:',
                'label_email': 'البريد:',
                'label_address': 'العنوان:',
                'label_credit_limit': 'حد الائتمان:',
                'btn_save': 'حفظ',
                'msg_name_required': 'الاسم مطلوب.',
                
                # Payment Dialog
                'payment_dialog_title': 'دفع الديون: {}',
                'label_current_credit': 'الدين الحالي: {:g} د.ج',
                'label_amount_pay': 'المبلغ المدفوع:',
                'label_note': 'ملاحظة:',
                'placeholder_note': 'ملاحظة اختيارية...',
                'label_new_balance': 'الباقي: {:g} د.ج',
                'checkbox_print_payment': '🖨️ طباعة إيصال الدفع',
                'btn_validate_payment': 'تأكيد الدفع',
                'receipt_item_payment': 'دفع ديون',
                'default_payment_note': 'دفع دين عميل',

                # Partial Payment / New Credit Dialog
                'dialog_credit_details_title': 'تفاصيل الدفع بالائتمان',
                'label_total_to_pay': 'الإجمالي للدفع: {:.2f} د.ج',
                'label_cash_paid_now': '💰 مدفوع الآن (نقداً):',
                'label_remaining_credit': 'الباقي ديناً: {:.2f} د.ج',
                'label_payment_complete': 'دفع كامل (نقداً)',

                # Products Page
                'products_title': '📦 إدارة المنتجات',
                'products_subtitle': 'إدارة المخزون، الأسعار والعروض',
                'products_count': '{} منتجات',
                'placeholder_search_product_page': '🔍 بحث (الاسم، الباركود)...',
                'filter_all_products': 'جميع المنتجات',
                'filter_low_stock': 'مخزون منخفض',
                'filter_promo': 'في العرض',
                'filter_expiring': 'تنتهي صلاحيته قريباً',
                'btn_new_product': '➕ منتج جديد',
                'btn_import': '📥 استيراد',
                'btn_order_report': '📑 طلبية',
                'tooltip_order_report': 'إنشاء قائمة طلبية للمخزون المنخفض',
                'table_headers_products_page': ["الكود", "الاسم", "سعر البيع", "المخزون", "الصلاحية", "عرض", "إظهار"],
                'tooltip_print_barcode': 'طباعة الباركود',
                'msg_confirm_delete_product': 'حذف هذا المنتج؟',
                'msg_no_barcode': "هذا المنتج لا يحتوي على باركود",
                'msg_reportlab_missing': "وحدة 'reportlab' مطلوبة لطباعة الباركود.\n\nقم بتثبيتها عبر: pip install reportlab",
                'title_missing_module': 'وحدة مفقودة',

                # Product Dialog
                'product_dialog_new': 'منتج جديد',
                'product_dialog_edit': 'تعديل المنتج',
                'tab_general': 'عام',
                'tab_price_stock': 'السعر والمخزون',
                'label_barcode': 'الباركود:',
                'label_name_ar': 'الاسم (بالعربية):',
                'label_supplier': 'المورد:',
                'label_description': 'الوصف:',
                'combo_no_supplier': '--- لا يوجد ---',
                'label_purchase_price': "سعر الشراء:",
                'label_selling_price': "سعر البيع *:",
                'label_initial_stock': "المخزون الأولي:",
                'label_min_stock': "تنبيه الحد الأدنى:",
                'checkbox_expiry_date': "تاريخ انتهاء الصلاحية؟",
                'msg_name_price_required': "الاسم وسعر البيع مطلوبان.",

                # Suppliers Page
                'suppliers_title': '🏭 إدارة الموردين',
                'suppliers_subtitle': 'إدارة الموردين والديون',
                'placeholder_search_supplier': '🔍 بحث عن مورد...',
                'filter_all_suppliers': 'جميع الموردين',
                'filter_debt_suppliers': 'مع ديون',
                'btn_new_supplier': '➕ مورد جديد',
                'table_headers_suppliers': ["الكود", "الشركة", "جهة الاتصال", "الهاتف", "إجمالي المشتريات", "الديون المستحقة", "إجراءات"],
                'btn_edit': 'تعديل',
                'btn_delete': 'حذف',
                'btn_add_purchase': 'إضافة شراء',
                'btn_pay_debt': 'دفع دين',
                'msg_confirm_delete_supplier': "هل أنت متأكد من حذف هذا المورد؟\n(لا يمكن الحذف إذا كان لديه منتجات أو ديون)",
                
                # Supplier Dialog
                'supplier_dialog_new': 'مورد جديد',
                'supplier_dialog_edit': 'تعديل مورد',
                'label_company': 'الشركة *:',
                'label_contact': 'جهة الاتصال:',
                'label_phone': 'الهاتف:',
                'label_email': 'البريد الإلكتروني:',
                'label_address': 'العنوان:',
                'msg_company_required': "اسم الشركة مطلوب.",

                # Debt Dialog
                'debt_dialog_title': 'تسديد الدين: {}',
                'label_current_debt': 'الدين الحالي: {} د.ج',
                'label_payment_amount': 'المبلغ للدفع:',
                'label_payment_note': 'الوصف:',
                'placeholder_payment_note': 'وصف الدفع...',
                'btn_validate_payment': 'تأكيد الدفع',

                # Purchase Dialog (Advanced)
                'purchase_dialog_title': 'إضافة شراء: {}',
                'purchase_search_group': '🔍 البحث عن المنتج',
                'placeholder_search_scan': 'مسح الباركود أو كتابة الاسم...',
                'table_header_product': 'المنتج',
                'table_header_stock': 'المحزون',
                'table_header_purchase_price': 'سعر الشراء',
                'table_header_action': 'إجراء',
                'group_cart': "🛒 سلة المشتريات - {}",
                'table_header_qty': 'الكمية',
                'table_header_unit_price': 'سعر الوحدة',
                'table_header_total': 'المجموع',
                'group_payment': '💳 الدفع والتأكيد',
                'label_total_to_pay': 'المجموع الكلي:',
                'label_payment_source': 'طريقة الدفع:',
                'opt_safe': 'الصندوق (نقد)',
                'opt_credit': 'آجل (دين)',
                'opt_other': 'أخرى (الخزينة)',
                'label_amount_paid': 'المبلغ المدفوع:',
                'label_remaining_debt': 'الباقي (دين):',
                'label_notes': 'ملاحظات (رقم الفاتورة):',
                'btn_validate_purchase': '✓ تأكيد الشراء',
                'msg_cart_empty': 'السلة فارغة',
                'msg_paid_exceeds_total': 'المبلغ المدفوع لا يمكن أن يتجاوز المجموع',
                'msg_confirm_purchase': 'تأكيد شراء {} منتجات بمبلغ {:.2f} د.ج؟',
                'msg_purchase_success': 'تم تسجيل الشراء بنجاح',
                'msg_amount_warning': "يجب أن يكون المبلغ أكبر من 0",

                # Purchase Dialog
                'purchase_dialog_title': 'إضافة شراء: {}',
                'label_supplier_info': 'المورد: {}',
                'label_purchase_amount': "إجمالي مبلغ الشراء:",
                'label_debt_to_add': "الديون للإضافة:",
                'placeholder_purchase_note': "وصف الشراء...",
                'info_purchase_msg': "💡 سيتم إضافة المبلغ الإجمالي إلى المشتريات.\nسيتم إضافة الدين إلى الدين الحالي.",
                'btn_save_purchase': "✅ حفظ الشراء",
                'msg_amount_warning': "المبلغ يجب أن يكون أكبر من 0",

                # Sales History Page
                'sales_history_title': '📜 سجل المبيعات',
                'sales_history_subtitle': 'عرض وإدارة جميع معاملاتك السابقة',
                'btn_export_excel': '📂 تصدير إكسل',
                'placeholder_search_sales': 'بحث عن تذكرة # أو عميل...',
                'label_date_from': 'من:',
                'label_date_to': 'إلى:',
                'filter_status_all': 'جميع الحالات',
                'filter_status_completed': 'مكتملة',
                'filter_status_cancelled': 'ملغاة',
                'filter_status_returned': 'مرتجعة',
                'table_headers_sales': ["المعرف", "رقم التذكرة", "التاريخ", "العميل", "البائع", "المجموع", "الحالة", "الربح"],
                'btn_view_details': '👁️ عرض التفاصيل',
                'btn_reprint': '🖨️ إعادة طباعة',
                'btn_return_action': '↩️ إرجاع',
                'summary_total_ca': 'إجمالي المبيعات: {:.2f} د.ج',
                'summary_total_profit': 'الربح المقدر: {:.2f} د.ج',
                'msg_export_success': 'تم تصدير السجل إلى:\n{}',
                'msg_print_sent': 'تم إرسال التذكرة إلى الطابعة.',

                # Tobacco & Units
                'checkbox_is_tobacco': 'منتج تبغ / شمة',
                'label_parent_product': 'المنتج الأصلي (العلبة):',
                'label_packing_qty': 'وحدات في العلبة:',
                'combo_no_parent': 'لا يوجد (منتج مستقل)',
                'tab_tobacco': 'تبغ / ربط',
                'section_auto_create': "🚬 إنشاء تلقائي للوحدات:",
                'checkbox_auto_create': "إنشاء منتج الوحدة أيضاً",
                'label_unit_price_tobacco': "سعر الوحدة:",
                'section_manual_link': "🔗 ربط يدوي:",
                'msg_pack_unit_created': "تم إنشاء العلبة والوحدة بنجاح!",
                'tab_tobacco_report': "🚬 تقرير التبغ",
                'tobacco_report_title': "🚬 تقرير التبغ مقابل المنتجات الأخرى ({} إلى {})",
                'col_category': "الفئة",
                'col_revenue': "إجمالي المبيعات",
                'col_cost': "تكلفة الشراء",
                'col_net_profit': "الربح الصافي",
                'col_margin': "هامش الربح %",
                'row_tobacco': "🚬 تبغ / سجائر / شمة",
                'row_others': "🛍️ منتجات أخرى",
                'row_others': "🛍️ منتجات أخرى",
                'row_total': "الإجمالي العام",
                
                # Customer History
                'history_title_customer': 'السجل: {}',
                'label_current_debt': 'الديون الحالية',
                'tab_financial_history': 'سجل المدفوعات',
                'tab_purchase_history': 'سجل المشتريات',
                'col_date': 'التاريخ',
                'col_type': 'النوع',
                'col_amount': 'المبلغ',
                'col_notes': 'ملاحظات',
                'col_user': 'المستخدم',
                'type_payment': 'دفعة / تسديد',
                'type_credit': 'كريدي / دين',
                'col_sale_no': 'رقم البيع',
                'col_payment_method': 'طريقة الدفع',
                'col_cashier': 'الكاشير',

                # Sale Details Dialog
                'sale_details_title': 'تفاصيل البيع #{}',
                'label_loading': 'جاري التحميل...',
                'table_headers_sale_items': ["المنتج", "الكمية", "سعر الوحدة", "المجموع الفرعي"],
                'label_dialog_total': 'المجموع: {:.2f} د.ج',
                'btn_close_dialog': 'إغلاق',
                'label_sale_info_detailed': "التاريخ: {}\nالعميل: {}\nالبائع: {}\nالحالة: {}",
                'msg_sale_not_found_dialog': "البيع غير موجود",

                # Settings Page
                'settings_title': '⚙️ الإعدادات',
                'settings_subtitle': 'الإعدادات العامة وإدارة المستخدمين',
                'tab_users': '👥 المستخدمين',
                'tab_data': '💾 البيانات',
                'tab_store': '🏪 المتجر',
                'tab_tutorial': '📚 التعليمات',
                'tab_about': 'ℹ️ حول البرنامج',
                'group_backup_config': 'إعدادات النسخ الاحتياطي التلقائي',
                'check_auto_backup': 'تفعيل النسخ الاحتياطي التلقائي',
                'suffix_hours': 'ساعات',
                'label_interval': 'الفاصل الزمني:',
                'btn_save_config': 'حفظ الإعدادات',
                'group_export': 'تصدير يدوي',
                'label_export_info': 'إنشاء نسخة احتياطية كاملة لقاعدة البيانات.',
                'btn_create_backup': 'إنشاء نسخة احتياطية',
                'group_import': 'استيراد / استعادة',
                'label_import_info': 'استعادة البيانات من ملف .db أو .sql.',
                'btn_restore_backup': 'استعادة نسخة احتياطية',
                'group_reset': '⚠️ منطقة الخطر',
                'label_reset_info': 'تحذير: هذا الإجراء سيحذف جميع المبيعات والمنتجات والعملاء!',
                'btn_reset_all': '🗑️ إعادة تعيين جميع البيانات',
                
                 # Shortcuts Management (New)
                'shortcuts_mgmt_title': 'إدارة الاختصارات',
                'shortcuts_mgmt_subtitle': "تكوين أزرار الوصول السريع",
                'btn_new_shortcut': '➕ اختصار جديد',
                'no_shortcuts_found': "لم يتم تكوين أي اختصارات.\nانقر على 'اختصار جديد' للبدء.",
                'confirm_delete_shortcut': 'هل أنت متأكد من حذف هذا الاختصار؟',
                'shortcut_edit_title': 'تعديل الاختصار',
                'shortcut_new_title': 'اختصار جديد',
                'config_section': 'إعدادات',
                'scan_barcode_placeholder': 'مسح الباركود...',
                'barcode_label': 'الباركود:',
                'product_label': 'المنتج:',
                'category_label': 'الفئة:',
                'label_input_label': 'التسمية:',
                'price_label': 'سعر الوحدة:',
                'select_product_default': '-- منتج مخصص --',
                'image_section': 'صورة (اختياري)',
                'btn_upload': '📂 اختيار',
                'btn_clear': '❌ مسح',
                'btn_cancel': 'إلغاء',
                'label_user_list': 'قائمة المستخدمين',
                'table_headers_users': ['المعرف', 'اسم المستخدم', 'الاسم الكامل', 'الدور', 'آخر اتصال', 'الحالة', 'إجراءات'],
                'btn_refresh': 'تحديث',
                'group_add_user': 'إضافة / تعديل مستخدم',
                'role_cashier': 'كاشير',
                'role_admin': 'مسؤول',
                'label_username': 'اسم المستخدم:',
                'label_password': 'كلمة المرور:',
                'label_fullname_user': 'الاسم الكامل:',
                'label_role': 'الدور:',
                'btn_create_user': 'إنشاء مستخدم',
                'perm_make_sales': 'إجراء المبيعات',
                'perm_process_returns': 'إجراء المرجعات',
                'perm_manage_products': 'إدارة المنتجات (إضافة/تعديل)',
                'perm_view_products': 'عرض المنتجات',
                'perm_manage_categories': 'إدارة الفئات',
                'perm_manage_customers': 'إدارة العملاء',
                'perm_view_customers': 'عرض العملاء',
                'perm_manage_suppliers': 'إدارة الموردين',
                'perm_view_suppliers': 'عرض الموردين',
                'perm_manage_users': 'إدارة المستخدمين',
                'perm_view_reports': 'عرض التقارير',
                'perm_manage_settings': 'تعديل الإعدادات',
                'perm_manage_backups': 'إدارة النسخ الاحتياطي',
                'perm_view_audit_log': 'عرض سجل التدقيق',
                'perm_manage_shortcuts': 'إدارة اختصارات الكاشير',
                'perm_view_sales_history': 'عرض سجل المبيعات',
                'perm_cancel_sales': 'إلغاء بيع كامل',
                'perm_manage_reset': 'إعادة ضبط التطبيق (خطر)',
                'perm_override_credit_limit': 'تجاوز حد الائتمان',

                # Returns Page
                'tab_new_return': 'إرجاع جديد',
                'tab_history_returns': 'سجل المرجعات',
                'table_history_headers_returns': ["رقم الإرجاع", "المبيعة الأصلية", "التاريخ", "المبلغ", "الكاشير", "السبب"],
                'btn_refresh': 'تحديث',
                'btn_reprint_ticket_history': 'إعادة طباعة التذكرة',
                
                # POS
                'placeholder_search_product': 'بحث عن منتج (اسم/كود)',

                # POS Product Search
                'placeholder_search_product_extended': 'البحث عن منتج (الاسم، الباركود)...',
                'table_headers_product_search': ["الباركود", "الاسم", "السعر", "المخزون", "إجراء"],
                'btn_close': 'إغلاق',

                # Shortcuts
                'tooltip_edit': 'تعديل',
                'tooltip_delete': 'حذف',
                'msg_access_denied': 'تم رفض الوصول',
                'msg_perm_required_shortcuts': 'الإذن مطلوب: إدارة الاختصارات',

                'msg_config_saved': 'تم حفظ الإعدادات!',
                'msg_backup_success': 'تم إنشاء النسخة الاحتياطية بنجاح:\n{}',
                'msg_confirm_import': 'هل أنت متأكد من استبدال قاعدة البيانات الحالية؟\nهذا الإجراء لا رجعة فيه.',
                'msg_import_success': 'تم استعادة قاعدة البيانات بنجاح.\n{}',
                'msg_confirm_reset_1': 'هل أنت متأكد؟\nسيؤدي هذا إلى حذف جميع البيانات!',
                'title_password_check': 'التحقق',
                'msg_password_check': 'أدخل كلمة مرور المسؤول للتأكيد:',
                'msg_reset_success': 'تم إعادة تعيين التطبيق بنجاح.',

            # Returns Page
                'returns_title': '↩️ إدارة المرتجعات',
                'returns_subtitle': 'إدارة المبالغ المستردة وإرجاع المخزون',
                'placeholder_search_return': 'أدخل رقم التذكرة (مثال: VNT-...) أو معرف البيع',
                'btn_search_return': '🔍 بحث',
                'btn_reprint_ticket_return': '🖨️ إعادة طباعة التذكرة',
                'btn_cancel_sale_return': '🗑️ إلغاء البيع بالكامل',
                'btn_process_return': '↩️ تأكيد الإرجاع',
                'table_headers_returns': ['المنتج', 'الكمية المشتراة', 'سعر الوحدة', 'كمية الإرجاع', 'تحديد'],
                'msg_select_items_return': 'يرجى تحديد عنصر واحد على الأقل بكمية أكبر من 0.',
                'msg_confirm_partial_return': 'هل تريد تأكيد هذا الإرجاع الجزئي؟',
                'msg_return_success': 'تم الإرجاع بنجاح!',
                'confirm_cancel_sale_msg': 'هل أنت متأكد من إلغاء البيع بالكامل؟\nسيتم إرجاع جميع العناصر إلى المخزون.',

                # Reports Page
                'reports_title': '📊 التقارير والإحصائيات',
                'label_period': '📅 الفترة:',
                'label_to': ' إلى ',
                'btn_refresh_report': '🔄 تحديث',
                'kpi_turnover': 'رقم الأعمال',
                'kpi_net_profit': 'صافي الربح',
                'kpi_margin': 'الهامش',
                'kpi_sale_count': 'عدد المبيعات',
                'kpi_total_credit': "إجمالي ديون العملاء",
                'table_headers_daily': ['التاريخ', 'المبيعات', 'منها آجل', 'التكلفة', 'الربح'],
                'tab_daily_sales': '📅 المبيعات اليومية',
                'table_headers_products_report': ['المنتج', 'الكمية المباعة', 'رقم الأعمال', 'الربح', 'الهامش'],
                'tab_top_products': '📦 أفضل المنتجات',
                'table_headers_categories_report': ["الفئة", "المبيعات", "الربح", "أفضل منتج", "الكمية"],
                'tab_categories': 'الفئات',
                'table_headers_users_report': ['المستخدم', 'المبيعات', 'منها آجل', 'التكلفة', 'الربح', 'عدد المبيعات'],
                'tab_user_sales': '👤 مبيعات المستخدمين',
                'label_closure_info': 'حدد فترة وانقر على تحديث',
                'btn_print_closure': '🖨️ طباعة ملخص الإغلاق',
                'tab_closure': '💰 ملخص الإغلاق',
                'closure_summary_title': 'الملخص المالي ({} إلى {})',
                'closure_cash': 'مبيعات نقدية (كاش):',
                'closure_credit': 'مبيعات آجلة (كريدي):',
                'closure_other': 'مدفوعات أخرى:',
                'closure_total': "إجمالي المبيعات:",
                'closure_returns': 'إجمالي المرتجعات:',
                
                # Settings - Store Tab (Missing AR)
                'tab_store': '🏪 المتجر',
                'label_store_name': 'اسم المتجر:',
                'label_store_phone': 'هاتف المتجر:',
                'label_store_address': 'عنوان المتجر:',
                'label_store_city': 'المدينة:',
                'label_store_nif': 'رقم التعريف الجبائي (NIF):',
                'label_store_nis': 'رقم ال NIS:',
                'label_store_rc': 'رقم السجل التجاري (RC):',
                'label_store_ai': 'رقم AI:',
                'label_expiry_days': 'تنبيه انتهاء الصلاحية (أيام):',
                'suffix_days': 'أيام',
                'btn_save_store': '💾 حفظ',
                'msg_store_saved': 'تم حفظ معلومات المتجر',
                
                # Returns Page (Missing AR)
                'returns_title': '↩️ إدارة المرتجعات',
                'returns_subtitle': 'إدارة المبالغ المستردة ومخزون المرتجعات',
                'placeholder_search_return': 'أدخل رقم التذكرة (مثال: VNT-...) أو معرف البيع',
                'btn_search_return': '🔍 بحث',
                'btn_reprint_ticket_return': '🖨️ إعادة طباعة التذكرة',
                'btn_cancel_sale_return': '🗑️ إلغاء البيع بالكامل',
                'btn_process_return': '↩️ تأكيد الإرجاع',
                'table_headers_returns': ['المنتج', 'الكمية المشتراة', 'سعر الوحدة', 'الكمية للإرجاع', 'اختيار'],
                'msg_select_items_return': 'يرجى تحديد عنصر واحد على الأقل بكمية أكبر من 0.',
                'msg_confirm_partial_return': 'هل تريد تأكيد هذا الإرجاع الجزئي؟',
                'msg_return_success': 'تم الإرجاع بنجاح!',
                'tab_return_history': '📜 سجل المرتجعات',
                'table_headers_return_history': ['رقم الإرجاع', 'رقم البيع الأصلي', 'المبلغ', 'التاريخ', 'السبب'],
                
                # Shortcuts Management (Missing AR)
                # Tutorial
                'tutorial_content': """
                <div dir="rtl" style="text-align: right;">
                <h2>📖 دليل الاستخدام v1.0</h2>
                
                <h3>🛒 نقطة البيع والدفع</h3>
                <ul>
                    <li><b>مسح الباركود</b> : استخدم القارئ أو اكتب الكود.</li>
                    <li><b>منوعات</b> : إضافة منتجات غير مخزنة بسرعة.</li>
                    <li><b>دفع مختلط/جزئي</b> : اختر "كريدي" لدفع جزء نقداً والباقي يُسجل كدين.</li>
                    <li><b>التذكرة</b> : تفعيل أو تعطيل الطباعة التلقائية.</li>
                </ul>
                
                <h3>⚡ الاختصارات السريعة (F9)</h3>
                <ul>
                    <li><b>الوصول</b> : اضغط F9 أو زر الاختصارات.</li>
                    <li><b>الإدارة</b> : أضف منتجاتك الأكثر مبيعاً مع <b>الصور</b>.</li>
                    <li><b>الصور</b> : يتم حفظ الصور وعرضها في الكاشير.</li>
                </ul>
                
                <h3>💾 النسخ الاحتياطي والأمان</h3>
                <ul>
                    <li><b>ملف ZIP كامل</b> : يقوم النظام بـحفظ كل شيء (قاعدة بيانات + صور).</li>
                    <li><b>ملف Excel</b> : يتم إنشاء ملف إكسل للقراءة السهلة.</li>
                    <li><b>تلقائي</b> : النسخ الاحتياطي يعمل تلقائياً (كل 5 ساعات).</li>
                </ul>
                
                <h3>👥 العملاء والديون</h3>
                <ul>
                    <li><b>متابعة</b> : سجل كامل للمشتريات والديون.</li>
                    <li><b>تنبيهات</b> : تحذير عند تجاوز حد الدين المسموح.</li>
                    <li><b>تسديد</b> : في صفحة "العملاء"، اضغط 💰 لتسديد الدين.</li>
                </ul>
                </ul>
                
                <h3>🛡️ الإدارة والصلاحيات (جديد)</h3>
                <ul>
                    <li><b>إضافة مستخدم</b> : في "الإعدادات > المستخدمين".</li>
                    <li><b>الصلاحيات</b> : اضغط على الدرع 🛡️ لتحديد ما يمكن للمستخدم فعله (الحذف، رؤية الأسعار، إلخ).</li>
                </ul>
                </div>
                """,
                'shortcuts_mgmt_title': 'إدارة الاختصارات',
                'shortcuts_mgmt_subtitle': 'إدارة أزرار الاختصارات السريعة لنقطة البيع',
                'btn_add_shortcut': '➕ إضافة اختصار',
                'shortcut_dialog_new': 'اختصار جديد',
                'shortcut_dialog_edit': 'تعديل الاختصار',
                'label_shortcut_label': 'اسم الاختصار:',
                'label_shortcut_price': 'السعر (اختياري):',
                'label_shortcut_image': 'الصورة:',
                'btn_choose_image': '📷 اختيار صورة',
                'label_shortcut_product': 'ربط بمنتج:',
                'label_shortcut_category': 'أو ربط بفئة:',
                'msg_label_required': 'اسم الاختصار مطلوب',

                # Permissions & Reset (New)
                'perm_manage_finance': 'إدارة الخزينة (الصندوق والخزنة)',
                'msg_confirm_reset_1': "هل أنت متأكد أنك تريد إعادة تعيين قاعدة البيانات؟\n\nهذا الإجراء لا رجعة فيه!\nسيتم حذف جميع المبيعات والمنتجات والعملاء.",
                'title_password_check': "التحقق مطلوب",
                'msg_password_check': "الرجاء إدخال كلمة المرور لتأكيد الإجراء:",

                # Tobacco & Units (New)
                'checkbox_is_tobacco': 'منتج تبغ/شيماء',
                'label_parent_product': 'المنتج الأصلي (العلبة):',
                'label_packing_qty': 'وحدات لكل علبة:',
                'combo_no_parent': 'لا يوجد (منتج مستقل)',
                'tab_tobacco': 'تبغ / ربط',
                'section_auto_create': "إنشاء تلقائي للوحدات:",
                'checkbox_auto_create': "إنشاء منتج بالوحدة أيضاً",
                'label_unit_price_tobacco': "سعر الوحدة:",
                'section_manual_link': "🔗 ربط يدوي:",
                'msg_pack_unit_created': "تم إنشاء العلبة + الوحدة بنجاح!",
                'tab_tobacco_report': "وضع التبغ",
                'tobacco_report_title': "تقرير التبغ مقابل المنتجات الأخرى ({} إلى {})",
                'col_category': "الفئة",
                'col_revenue': "رقم الأعمال",
                'col_cost': "تكلفة الشراء",
                'col_net_profit': "الربح الصافي",
                'col_margin': "الهامش %",
                'row_tobacco': "🚬 تبغ / سجائر / شيماء",
                'row_others': "🛍️ منتجات أخرى",
                'row_total': "الإجمالي العام",

                # Unit Auto-Create
                'unit_of': "وحدة من {}",
                'unit_suffix_fr': " (Unité)",
                'unit_suffix_ar': " (وحدة)",
                
                # Reorder Report
                'reorder_report_title': "قائمة طلبات المورد",
                'reorder_generated_on': "تم الإنشاء في: {}",
                'unknown_supplier': "مورد غير معروف",
                'col_product': "المنتج",
                'col_current_stock': "المخزون الحالي",
                'col_min_stock': "الحد الأدنى",
                'col_qty_to_order': "الكمية المطلوبة",
            },
        }

    def get(self, key, default=None):
        """Get translated string"""
        val = self.translations.get(self.current_language, {}).get(key)
        if val is None:
            # Fallback to French if not found
            val = self.translations.get('fr', {}).get(key, default or key)
        return val

    def set_language(self, lang):
        """Set language ('fr' or 'ar')"""
        if lang in self.translations:
            self.current_language = lang
            self.language_changed.emit(lang)

    def toggle_language(self):
        """Toggle between FR and AR"""
        new_lang = 'ar' if self.current_language == 'fr' else 'fr'
        self.set_language(new_lang)
        return new_lang

    def is_rtl(self):
        """Check if current language is RTL"""
        return self.current_language == 'ar'

# Global Instance
i18n_manager = I18nManager()
