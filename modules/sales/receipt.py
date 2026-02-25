# -*- coding: utf-8 -*-
"""
Génération de tickets de caisse
"""
from typing import Dict, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from pathlib import Path
import config


class ReceiptGenerator:
    """Générateur de tickets de caisse"""
    
    def __init__(self):
        self.store_config = config.STORE_CONFIG
        self.language = config.LANGUAGE_CONFIG['default_language']
    
    def set_language(self, language: str):
        """Définir la langue du ticket"""
        self.language = language
    
    def generate_text_receipt(self, sale_data: Dict) -> str:
        """
        Générer un ticket en format texte (pour imprimantes thermiques)
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            Ticket en format texte
        """
        lines = []
        width = 42  # Largeur pour imprimante 80mm
        
        # En-tête
        lines.append("=" * width)
        lines.append(self.store_config['name'].center(width))
        lines.append(self.store_config['address'].center(width))
        lines.append(self.store_config['phone'].center(width))
        if self.store_config.get('tax_id'):
            lines.append(f"NIF: {self.store_config['tax_id']}".center(width))
        if self.store_config.get('nis'):
            lines.append(f"NIS: {self.store_config['nis']}".center(width))
        if self.store_config.get('rc'):
            lines.append(f"RC: {self.store_config['rc']}".center(width))
        if self.store_config.get('ai'):
            lines.append(f"AI: {self.store_config['ai']}".center(width))
        lines.append("=" * width)
        lines.append("")
        
        # Informations de vente
        lines.append(f"N° Vente: {sale_data['sale_number']}")
        lines.append(f"Date: {sale_data.get('sale_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
        lines.append(f"Caissier: {sale_data.get('cashier_name', 'N/A')}")
        if sale_data.get('customer_name'):
            lines.append(f"Client: {sale_data['customer_name']}")
        lines.append(f"Caisse N°: {sale_data.get('register_number', 1)}")
        lines.append("-" * width)
        lines.append("")
        
        # Articles
        lines.append("Articles:")
        lines.append("-" * width)
        
        for item in sale_data['items']:
            name = item['product_name'][:30]  # Tronquer si trop long
            qty = item['quantity']
            price = item['unit_price']
            subtotal = item['subtotal']
            
            # Ligne produit
            lines.append(name)
            
            # Ligne quantité et prix
            qty_price = f"{qty} x {price:.2f} DA"
            total_str = f"{subtotal:.2f} DA"
            spacing = width - len(qty_price) - len(total_str)
            lines.append(f"{qty_price}{' ' * spacing}{total_str}")
            
            # Réduction si applicable
            if item.get('discount_percentage', 0) > 0:
                lines.append(f"  Promo: -{item['discount_percentage']}%")
            
            lines.append("")
        
        lines.append("-" * width)
        
        # Totaux
        subtotal = sale_data['subtotal']
        discount = sale_data.get('discount_amount', 0)
        total = sale_data['total_amount']
        
        lines.append(f"Sous-total:{' ' * (width - 20)}{subtotal:>10.2f} DA")
        
        if discount > 0:
            lines.append(f"Réduction:{' ' * (width - 20)}{discount:>10.2f} DA")
        
        lines.append("=" * width)
        lines.append(f"TOTAL:{' ' * (width - 16)}{total:>10.2f} DA")
        lines.append("=" * width)
        lines.append("")
        
        # Paiement
        payment_method = sale_data.get('payment_method', 'cash')
        payment_labels = {
            'cash': 'Espèces',
            'card': 'Carte',
            'credit': 'Crédit',
            'mixed': 'Mixte'
        }
        
        lines.append(f"Mode: {payment_labels.get(payment_method, payment_method)}")
        
        if payment_method != 'credit':
            paid = sale_data.get('amount_paid', total)
            change = sale_data.get('change_amount', 0)
            
            lines.append(f"Payé:{' ' * (width - 16)}{paid:>10.2f} DA")
            if change > 0:
                lines.append(f"Rendu:{' ' * (width - 16)}{change:>10.2f} DA")
        
        lines.append("")
        lines.append("-" * width)
        
        # Pied de page
        footer_msg = config.DEFAULT_MESSAGES.get(self.language, {}).get(
            'receipt_footer', 'Merci pour votre visite !'
        )
        lines.append(footer_msg.center(width))
        lines.append("")
        lines.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(width))
        lines.append("=" * width)
        
        return "\n".join(lines)
    
    def generate_pdf_receipt(self, sale_data: Dict, output_path: Path) -> bool:
        """
        Générer un ticket en format PDF (80mm x 80mm)
        
        Args:
            sale_data: Données de la vente
            output_path: Chemin du fichier PDF
            
        Returns:
            True si succès
        """
        try:
            # Créer le PDF - Format ticket 80mm x 80mm
            c = canvas.Canvas(str(output_path), pagesize=(80*mm, 80*mm))
            
            # Position de départ
            y = 74 * mm
            x_center = 40 * mm
            
            # En-tête
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(x_center, y, self.store_config['name'])
            y -= 4.5 * mm
            
            c.setFont("Helvetica", 6)
            c.drawCentredString(x_center, y, self.store_config['address'])
            y -= 3 * mm
            c.drawCentredString(x_center, y, self.store_config['phone'])
            y -= 3 * mm
            
            if self.store_config.get('tax_id'):
                c.drawCentredString(x_center, y, f"NIF: {self.store_config['tax_id']}")
                y -= 3 * mm
            if self.store_config.get('nis'):
                c.drawCentredString(x_center, y, f"NIS: {self.store_config['nis']}")
                y -= 3 * mm
            if self.store_config.get('rc'):
                c.drawCentredString(x_center, y, f"RC: {self.store_config['rc']}")
                y -= 3 * mm
            if self.store_config.get('ai'):
                c.drawCentredString(x_center, y, f"AI: {self.store_config['ai']}")
                y -= 3 * mm
            
            # Ligne de séparation
            y -= 1 * mm
            c.line(3*mm, y, 77*mm, y)
            y -= 3 * mm
            
            # Informations de vente
            c.setFont("Helvetica", 6)
            c.drawString(3*mm, y, f"N°: {sale_data['sale_number']}")
            c.drawRightString(77*mm, y, f"{sale_data.get('sale_date', datetime.now().strftime('%d/%m/%Y %H:%M'))}")
            y -= 3 * mm
            c.drawString(3*mm, y, f"Caissier: {sale_data.get('cashier_name', 'N/A')}")
            y -= 3 * mm
            
            if sale_data.get('customer_name'):
                c.drawString(3*mm, y, f"Client: {sale_data['customer_name']}")
                y -= 3 * mm
            
            # Ligne de séparation
            y -= 1 * mm
            c.line(3*mm, y, 77*mm, y)
            y -= 3 * mm
            
            # Articles
            c.setFont("Helvetica", 6)
            for item in sale_data['items']:
                name = item['product_name'][:30]
                c.drawString(3*mm, y, name)
                y -= 2.5 * mm
                
                qty_price = f"{item['quantity']} x {item['unit_price']:.2f}"
                total_str = f"{item['subtotal']:.2f} DA"
                c.drawString(5*mm, y, qty_price)
                c.drawRightString(77*mm, y, total_str)
                y -= 3 * mm
                
                if item.get('discount_percentage', 0) > 0:
                    c.drawString(5*mm, y, f"Promo: -{item['discount_percentage']}%")
                    y -= 2.5 * mm
            
            # Ligne de séparation
            y -= 1 * mm
            c.line(3*mm, y, 77*mm, y)
            y -= 3 * mm
            
            # Totaux
            c.setFont("Helvetica", 7)
            c.drawString(3*mm, y, "Sous-total:")
            c.drawRightString(77*mm, y, f"{sale_data['subtotal']:.2f} DA")
            y -= 3 * mm
            
            if sale_data.get('discount_amount', 0) > 0:
                c.drawString(3*mm, y, "Réduction:")
                c.drawRightString(77*mm, y, f"-{sale_data['discount_amount']:.2f} DA")
                y -= 3 * mm
            
            # Total
            c.setFont("Helvetica-Bold", 9)
            c.drawString(3*mm, y, "TOTAL:")
            c.drawRightString(77*mm, y, f"{sale_data['total_amount']:.2f} DA")
            y -= 4 * mm
            
            # Paiement
            c.setFont("Helvetica", 6)
            payment_method = sale_data.get('payment_method', 'cash')
            payment_labels = {
                'cash': 'Espèces',
                'card': 'Carte',
                'credit': 'Crédit',
                'mixed': 'Mixte'
            }
            
            c.drawString(3*mm, y, f"Mode: {payment_labels.get(payment_method, payment_method)}")
            y -= 3 * mm
            
            if payment_method != 'credit':
                paid = sale_data.get('amount_paid', sale_data['total_amount'])
                change = sale_data.get('change_amount', 0)
                
                c.drawString(3*mm, y, f"Payé: {paid:.2f} DA")
                if change > 0:
                    c.drawRightString(77*mm, y, f"Rendu: {change:.2f} DA")
                y -= 3 * mm
            
            # Pied de page
            y -= 2 * mm
            c.setFont("Helvetica", 6)
            footer_msg = config.DEFAULT_MESSAGES.get(self.language, {}).get(
                'receipt_footer', 'Merci pour votre visite !'
            )
            c.drawCentredString(x_center, y, footer_msg)
            y -= 3 * mm
            c.setFont("Helvetica", 5)
            c.drawCentredString(x_center, y, datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            
            # Sauvegarder le PDF
            c.save()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération du PDF: {e}")
            return False
    
    def generate_html_receipt(self, sale_data: Dict) -> str:
        """
        Générer un ticket en format HTML (pour aperçu)
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            HTML du ticket
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    width: 300px;
                    margin: 20px auto;
                    padding: 10px;
                    border: 1px solid #ccc;
                }}
                .header {{
                    text-align: center;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .separator {{
                    border-top: 1px dashed #000;
                    margin: 10px 0;
                }}
                .item {{
                    margin: 5px 0;
                }}
                .item-name {{
                    font-weight: bold;
                }}
                .item-details {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.9em;
                }}
                .totals {{
                    margin-top: 10px;
                }}
                .total-line {{
                    display: flex;
                    justify-content: space-between;
                    margin: 3px 0;
                }}
                .grand-total {{
                    font-weight: bold;
                    font-size: 1.2em;
                    border-top: 2px solid #000;
                    padding-top: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 15px;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div style="font-size: 1.2em;">{self.store_config['name']}</div>
                <div>{self.store_config['address']}</div>
                <div>{self.store_config['phone']}</div>
                {'<div>NIF: ' + self.store_config.get('tax_id', '') + '</div>' if self.store_config.get('tax_id') else ''}
            </div>
            
            <div class="separator"></div>
            
            <div>
                <div>N° Vente: {sale_data['sale_number']}</div>
                <div>Date: {sale_data.get('sale_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}</div>
                <div>Caissier: {sale_data.get('cashier_name', 'N/A')}</div>
                {'<div>Client: ' + sale_data.get('customer_name', '') + '</div>' if sale_data.get('customer_name') else ''}
                <div>Caisse N°: {sale_data.get('register_number', 1)}</div>
            </div>
            
            <div class="separator"></div>
            
            <div>
                <strong>Articles:</strong>
        """
        
        # Articles
        for item in sale_data['items']:
            discount_html = f"<div style='color: red; font-size: 0.8em;'>Promo: -{item['discount_percentage']}%</div>" if item.get('discount_percentage', 0) > 0 else ""
            
            html += f"""
                <div class="item">
                    <div class="item-name">{item['product_name']}</div>
                    <div class="item-details">
                        <span>{item['quantity']} x {item['unit_price']:.2f} DA</span>
                        <span>{item['subtotal']:.2f} DA</span>
                    </div>
                    {discount_html}
                </div>
            """
        
        # Totaux
        payment_labels = {
            'cash': 'Espèces',
            'card': 'Carte',
            'credit': 'Crédit',
            'mixed': 'Mixte'
        }
        
        discount_html = f"""
            <div class="total-line">
                <span>Réduction:</span>
                <span>-{sale_data['discount_amount']:.2f} DA</span>
            </div>
        """ if sale_data.get('discount_amount', 0) > 0 else ""
        
        payment_html = ""
        if sale_data.get('payment_method') != 'credit':
            paid = sale_data.get('amount_paid', sale_data['total_amount'])
            change = sale_data.get('change_amount', 0)
            payment_html = f"""
                <div class="total-line">
                    <span>Payé:</span>
                    <span>{paid:.2f} DA</span>
                </div>
            """
            if change > 0:
                payment_html += f"""
                <div class="total-line">
                    <span>Rendu:</span>
                    <span>{change:.2f} DA</span>
                </div>
                """
        
        html += f"""
            </div>
            
            <div class="totals">
                <div class="total-line">
                    <span>Sous-total:</span>
                    <span>{sale_data['subtotal']:.2f} DA</span>
                </div>
                {discount_html}
                <div class="total-line grand-total">
                    <span>TOTAL:</span>
                    <span>{sale_data['total_amount']:.2f} DA</span>
                </div>
            </div>
            
            <div class="separator"></div>
            
            <div>
                <div>Mode: {payment_labels.get(sale_data.get('payment_method', 'cash'), 'Espèces')}</div>
                {payment_html}
            </div>
            
            <div class="footer">
                <div>{config.DEFAULT_MESSAGES.get(self.language, {}).get('receipt_footer', 'Merci pour votre visite !')}</div>
                <div style="font-size: 0.8em; margin-top: 5px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
        </body>
        </html>
        """
        
        return html

    def generate_return_text_receipt(self, return_data: Dict) -> str:
        """
        Générer un ticket de RETOUR en format texte
        """
        lines = []
        width = 42
        
        # En-tête
        lines.append("=" * width)
        lines.append(self.store_config['name'].center(width))
        lines.append("TICKET DE RETOUR".center(width))
        lines.append("=" * width)
        lines.append("")
        
        # Infos Retour
        lines.append(f"N° Retour: {return_data['return_number']}")
        lines.append(f"Origine: {return_data.get('original_sale_number', 'N/A')}")
        lines.append(f"Date: {return_data.get('return_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
        lines.append(f"Caissier: {return_data.get('cashier_name', 'N/A')}")
        if return_data.get('customer_name'):
            lines.append(f"Client: {return_data['customer_name']}")
        
        lines.append("-" * width)
        lines.append("Articles Retournés:")
        lines.append("-" * width)
        
        for item in return_data['items']:
            name = item['product_name'][:30]
            # Utiliser quantity_returned si disponible, sinon quantity (compatibilité)
            qty = item.get('quantity_returned', item.get('quantity', 0))
            price = item['unit_price']
            # Utiliser subtotal (nom dans return_items) ou return_amount
            total = item.get('subtotal', item.get('return_amount', 0)) 
            
            lines.append(name)
            qty_price = f"{qty} x {price:.2f} DA"
            total_str = f"-{total:.2f} DA" # Montant négatif pour indiquer remboursement
            
            spacing = width - len(qty_price) - len(total_str)
            lines.append(f"{qty_price}{' ' * spacing}{total_str}")
            lines.append("")
            
        lines.append("-" * width)
        
        # Total
        total_refund = return_data['return_amount']
        lines.append("=" * width)
        lines.append(f"TOTAL REMBOURSÉ:{' ' * (width - 25)}-{total_refund:.2f} DA")
        lines.append("=" * width)
        lines.append("")
        
        # Raison
        if return_data.get('reason'):
            lines.append(f"Raison: {return_data['reason']}")
            lines.append("")
            
        lines.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(width))
        lines.append("=" * width)
        
        return "\n".join(lines)

    def generate_return_html_receipt(self, return_data: Dict) -> str:
        """
        Générer un ticket de RETOUR en HTML
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    width: 300px;
                    margin: 20px auto;
                    padding: 10px;
                    border: 1px solid #ef4444; /* Bordure rouge pour retour */
                    background-color: #fef2f2;
                }}
                .header {{
                    text-align: center;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .title {{
                    font-size: 1.2em;
                    color: #dc2626;
                    margin: 5px 0;
                }}
                .separator {{
                    border-top: 1px dashed #000;
                    margin: 10px 0;
                }}
                .item {{ margin: 5px 0; }}
                .item-details {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.9em;
                }}
                .total-line {{
                    display: flex;
                    justify-content: space-between;
                    font-weight: bold;
                    font-size: 1.2em;
                    color: #dc2626;
                    border-top: 2px solid #000;
                    padding-top: 5px;
                    margin-top: 10px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 15px;
                    font-size: 0.8em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>{self.store_config['name']}</div>
                <div class="title">TICKET DE RETOUR</div>
            </div>
            
            <div class="separator"></div>
            
            <div>
                <div>N° Retour: {return_data['return_number']}</div>
                <div>Origine: {return_data.get('original_sale_number', 'N/A')}</div>
                <div>Date: {return_data.get('return_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}</div>
                <div>Caissier: {return_data.get('cashier_name', 'N/A')}</div>
                {'<div>Client: ' + return_data.get('customer_name', '') + '</div>' if return_data.get('customer_name') else ''}
            </div>
            
            <div class="separator"></div>
            
            <div>
                <strong>Articles Retournés:</strong>
        """
        
        for item in return_data['items']:
            # Utiliser quantity_returned si disponible
            qty = item.get('quantity_returned', item.get('quantity', 0))
            # Utiliser subtotal si disponible
            item_total = item.get('subtotal', item.get('return_amount', 0))
            
            html += f"""
                <div class="item">
                    <div>{item['product_name']}</div>
                    <div class="item-details">
                        <span>{qty} x {item['unit_price']:.2f} DA</span>
                        <span>-{item_total:.2f} DA</span>
                    </div>
                </div>
            """
            
        html += f"""
            </div>
            
            <div class="total-line">
                <span>TOTAL REMBOURSÉ:</span>
                <span>-{return_data['return_amount']:.2f} DA</span>
            </div>
            
            <div class="separator"></div>
            
            <div>
                <div>Raison: {return_data.get('reason', 'N/A')}</div>
            </div>
            
            <div class="footer">
                <div>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
        </body>
        </html>
        """
        return html

    def generate_return_pdf_receipt(self, return_data: Dict, output_path: Path) -> bool:
        """
        Générer un ticket de RETOUR en PDF
        
        Args:
            return_data: Données du retour
            output_path: Chemin du fichier PDF
            
        Returns:
            True si succès
        """
        try:
            # Créer le PDF
            c = canvas.Canvas(str(output_path), pagesize=(80*mm, 297*mm))
            
            # Position de départ
            y = 280 * mm
            x_center = 40 * mm
            
            # En-tête
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(x_center, y, self.store_config['name'])
            y -= 7 * mm
            
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(x_center, y, "TICKET DE RETOUR")
            y -= 10 * mm
            
            # Ligne de séparation
            c.line(5*mm, y, 75*mm, y)
            y -= 5 * mm
            
            # Informations
            c.setFont("Helvetica", 8)
            c.drawString(5*mm, y, f"N° Retour: {return_data['return_number']}")
            y -= 4 * mm
            c.drawString(5*mm, y, f"Origine: {return_data.get('original_sale_number', 'N/A')}")
            y -= 4 * mm
            c.drawString(5*mm, y, f"Date: {return_data.get('return_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
            y -= 4 * mm
            c.drawString(5*mm, y, f"Caissier: {return_data.get('cashier_name', 'N/A')}")
            y -= 4 * mm
            
            if return_data.get('customer_name'):
                c.drawString(5*mm, y, f"Client: {return_data['customer_name']}")
                y -= 4 * mm
            
            # Ligne de séparation
            y -= 2 * mm
            c.line(5*mm, y, 75*mm, y)
            y -= 5 * mm
            
            # Articles
            c.setFont("Helvetica-Bold", 9)
            c.drawString(5*mm, y, "Articles Retournés")
            y -= 5 * mm
            
            c.setFont("Helvetica", 7)
            for item in return_data['items']:
                # Nom du produit
                name = item['product_name'][:35]
                c.drawString(5*mm, y, name)
                y -= 3.5 * mm
                
                # Quantité, prix unitaire et total
                # Utiliser quantity_returned si disponible
                qty = item.get('quantity_returned', item.get('quantity', 0))
                # Utiliser subtotal si disponible
                item_total = item.get('subtotal', item.get('return_amount', 0))
                
                qty_price = f"{qty} x {item['unit_price']:.2f} DA"
                total_str = f"-{item_total:.2f} DA"
                
                c.drawString(8*mm, y, qty_price)
                c.drawRightString(75*mm, y, total_str)
                y -= 4 * mm
            
            # Ligne de séparation
            y -= 2 * mm
            c.line(5*mm, y, 75*mm, y)
            y -= 5 * mm
            
            # Totaux
            y -= 1 * mm
            c.setFont("Helvetica-Bold", 11)
            c.drawString(5*mm, y, "TOTAL REMBOURSÉ:")
            c.drawRightString(75*mm, y, f"-{return_data['return_amount']:.2f} DA")
            y -= 6 * mm
            
            # Raison
            if return_data.get('reason'):
                c.setFont("Helvetica", 8)
                c.drawString(5*mm, y, f"Raison: {return_data['reason']}")
                y -= 5 * mm
            
            # Pied de page
            y -= 10 * mm
            c.setFont("Helvetica", 7)
            c.drawCentredString(x_center, y, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Sauvegarder le PDF
            c.save()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération du PDF retour: {e}")
            return False


# Instance globale
receipt_generator = ReceiptGenerator()
