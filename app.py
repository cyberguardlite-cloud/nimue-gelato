from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    session,
    redirect,
    url_for,
)
import io
import re
import os
import stripe



from gelato_engine import genera_ricetta_testo, get_substitutions

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from flask import Response
from flask import request, abort
from flask import jsonify
from flask import Flask, render_template, request, session, redirect, url_for


app = Flask(__name__)
app.secret_key = "CAMBIA_QUESTA_CHIAVE_CON_UNA_TUA"  # metti una stringa lunga e casuale
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")




# ==========================
#     TRADUZIONI / TESTI
# ==========================
TRANSLATIONS = {
    "it": {
        "app_title": "Nimue Gelato Artigianale",
        "subtitle": "Home Edition",
        "studio": "AI Studio",
        "tagline": "Tradizione artigianale, precisione intelligente.",

        "language": "Lingua",
        "create": "Crea una ricetta",
        "helper": "Scrivi il gusto e la quantità. Se vuoi, scegli un profilo e un metodo.",
        "flavour": "Gusto",
        "quantity": "Quantità (kg)",
        "profile": "Profilo",
        "method": "Metodo",
        "generate": "Genera ricetta",
        "recipe_generated": "Ricetta generata",
        "no_recipe": "Nessuna ricetta generata",
        "copy": "Copia testo",
        "pdf": "Scarica PDF",
        "ingredients": "Ingredienti",
        "col_ing": "Ingrediente",
        "col_qty": "Quantità (g)",

        "pdf_title": "Nimue Gelato Artigianale – AI Studio",
        "pdf_flavour": "Gusto",
        "pdf_amount": "Quantità",
        "pdf_profile": "Profilo",
        "pdf_method": "Metodo",
        "footer_pdf": "© 2026 Nimue Gelato Artigianale · Tutti i diritti riservati · Creato da Gianni Di Prete",

        "footer_app_l1": "Nimue Gelato Artigianale · AI Studio",
        "footer_app_l2": "© 2026 Tutti i diritti riservati.",
        "footer_app_l3": "Creato da Gianni Di Prete",
        "footer_contact_label" : "Contatti",


        # Nota sotto la tabella ingredienti
        "note_pdf": "Per la procedura e le variazioni di ingredienti acquista e scarica il PDF.",

        # --- LANDING ---
        "landing_eyebrow": "Dove la cucina diventa laboratorio",
        "landing_h1": "Crea ricette di gelato bilanciate, in pochi minuti.",
        "landing_p": "Nimue AI Studio – Home Edition ti aiuta a costruire ricette chiare e ripetibili, con ingredienti semplici, procedimento passo-passo e PDF esportabile.",
        "landing_cta_primary": "Crea la tua ricetta",
        "landing_cta_secondary": "Come funziona",
        "landing_note": "Nessun account. Paghi solo se vuoi il PDF completo (una tantum).",
        "landing_payment_trust = Pagamento sicuro con Stripe"


        "landing_for_who_title": "Per chi è",
        "landing_for_who_1_title": "Appassionati",
        "landing_for_who_1_desc": "Vuoi fare un gelato migliore a casa, senza improvvisare.",
        "landing_for_who_2_title": "Curiosi",
        "landing_for_who_2_desc": "Vuoi capire metodo e passaggi, non solo “dosi a caso”.",
        "landing_for_who_3_title": "Chi vuole crescere",
        "landing_for_who_3_desc": "Vuoi una base seria oggi, e passare alla Pro domani.",

        "landing_get_title": "Cosa ottieni",
        "landing_get_1": "Ricette bilanciate per uso domestico",
        "landing_get_2": "Profili (classica, vegana, senza uova, light, gourmet)",
        "landing_get_3": "Metodo guidato (con/ senza gelatiera)",
        "landing_get_4": "Multilingua",
        "landing_get_5": "PDF esportabile",

        "landing_what_title": "Cosa fa",
        "landing_what_1": "Ti guida dal gusto alla ricetta completa.",
        "landing_what_2": "Tabella ingredienti chiara (grammi) e procedimento lineare.",
        "landing_what_3": "Consigli di lavorazione e conservazione pensati per casa.",

        "landing_not_title": "Cosa non è",
        "landing_not_box": "Nimue non è un generatore casuale di ricette e non è un blog. È uno strumento artigianale: semplice da usare, serio nei risultati.",

        "landing_bottom_title": "Pronto per Nimue AI Studio?",

        "profile_opts": {
            "": "Standard",
            "classica": "Classica",
            "senza uova": "Senza uova",
            "light": "Light",
            "vegana": "Vegana",
            "gourmet": "Gourmet",
        },
        "method_opts": {
            "": "Automatico",
            "con gelatiera": "Con gelatiera",
            "senza gelatiera": "Senza gelatiera",
            "pacojet": "Pacojet",
        },

        "err_flavour": "Inserisci il gusto del gelato.",
        "err_qty_zero": "La quantità deve essere maggiore di zero.",
        "err_qty_invalid": "Inserisci una quantità valida in kg (es. 1 oppure 1,5).",
        "err_no_recipe": "Nessuna ricetta da esportare in PDF.",
    },

    "en": {
        "app_title": "Nimue Artisanal Gelato",
        "subtitle": "Home Edition",
        "studio": "AI Studio",
        "tagline": "Artisanal tradition, intelligent precision.",

        "language": "Language",
        "create": "Create a recipe",
        "helper": "Enter flavor and quantity. Optionally choose a profile and a method.",
        "flavour": "Flavor",
        "quantity": "Quantity (kg)",
        "profile": "Profile",
        "method": "Method",
        "generate": "Generate recipe",
        "recipe_generated": "Generated recipe",
        "no_recipe": "No recipe generated",
        "copy": "Copy text",
        "pdf": "Download PDF",
        "ingredients": "Ingredients",
        "col_ing": "Ingredient",
        "col_qty": "Quantity (g)",

        "pdf_title": "Nimue Artisanal Gelato – AI Studio",
        "pdf_flavour": "Flavor",
        "pdf_amount": "Quantity",
        "pdf_profile": "Profile",
        "pdf_method": "Method",
        "footer_pdf": "© 2026 Nimue Artisanal Gelato · All rights reserved · Created by Gianni Di Prete",

        "footer_app_l1": "Nimue Artisanal Gelato · AI Studio",
        "footer_app_l2": "© 2026 All rights reserved.",
        "footer_app_l3": "Created by Gianni Di Prete",
        "footer_contact_label": "Contact",

        "note_pdf": "To get the full procedure and ingredient variations, purchase and download the PDF.",

        "landing_eyebrow": "Where your kitchen becomes a lab",
        "landing_h1": "Create balanced gelato recipes in minutes.",
        "landing_p": "Nimue AI Studio – Home Edition helps you create clear, repeatable recipes with simple ingredients, step-by-step instructions, and exportable PDFs.",
        "landing_cta_primary": "Create your recipe",
        "landing_cta_secondary": "How it works",
        "landing_note": "No account. You only pay if you want the full PDF (one-time).",
        "landing_payment_trust": "Secure payment with Stripe",

        "landing_for_who_title": "Who it’s for",
        "landing_for_who_1_title": "Enthusiasts",
        "landing_for_who_1_desc": "You want better gelato at home, without guessing.",
        "landing_for_who_2_title": "Curious makers",
        "landing_for_who_2_desc": "You want method and steps, not random quantities.",
        "landing_for_who_3_title": "Those who want to grow",
        "landing_for_who_3_desc": "You want a solid base today and Pro tools tomorrow.",

        "landing_get_title": "What you get",
        "landing_get_1": "Balanced recipes for home use",
        "landing_get_2": "Profiles (classic, vegan, egg-free, light, gourmet)",
        "landing_get_3": "Guided method (with / without ice cream maker)",
        "landing_get_4": "Multilingual",
        "landing_get_5": "Exportable PDF",

        "landing_what_title": "What it does",
        "landing_what_1": "Guides you from flavor to a complete recipe.",
        "landing_what_2": "Clear ingredient table (grams) and a clean procedure.",
        "landing_what_3": "Practical tips for processing, serving, and storage at home.",

        "landing_not_title": "What it’s not",
        "landing_not_box": "Nimue is not a random recipe generator and not a blog. It’s a crafted tool: simple to use, serious in results.",

        "landing_bottom_title": "Ready to try Nimue AI Studio?",

        "profile_opts": {
            "": "Standard",
            "classica": "Classic",
            "senza uova": "Egg-free",
            "light": "Light",
            "vegana": "Vegan",
            "gourmet": "Gourmet",
        },
        "method_opts": {
            "": "Automatic",
            "con gelatiera": "With ice cream maker",
            "senza gelatiera": "Without ice cream maker",
            "pacojet": "Pacojet",
        },

        "err_flavour": "Please enter a flavor.",
        "err_qty_zero": "Quantity must be greater than zero.",
        "err_qty_invalid": "Enter a valid quantity in kg (e.g., 1 or 1.5).",
        "err_no_recipe": "No recipe to export as PDF.",
    },

    "es": {
        "app_title": "Nimue Helado Artesanal",
        "subtitle": "Edición Hogar",
        "studio": "AI Studio",
        "tagline": "Tradición artesanal, precisión inteligente.",

        "language": "Idioma",
        "create": "Crear una receta",
        "helper": "Escribe el sabor y la cantidad. Si quieres, elige perfil y método.",
        "flavour": "Sabor",
        "quantity": "Cantidad (kg)",
        "profile": "Perfil",
        "method": "Método",
        "generate": "Generar receta",
        "recipe_generated": "Receta generada",
        "no_recipe": "No se generó ninguna receta",
        "copy": "Copiar texto",
        "pdf": "Descargar PDF",
        "ingredients": "Ingredientes",
        "col_ing": "Ingrediente",
        "col_qty": "Cantidad (g)",

        "pdf_title": "Nimue Helado Artesanal – AI Studio",
        "pdf_flavour": "Sabor",
        "pdf_amount": "Cantidad",
        "pdf_profile": "Perfil",
        "pdf_method": "Método",
        "footer_pdf": "© 2026 Nimue Helado Artesanal · Todos los derechos reservados · Creado por Gianni Di Prete",

        "footer_app_l1": "Nimue Helado Artesanal · AI Studio",
        "footer_app_l2": "© 2026 Todos los derechos reservados.",
        "footer_app_l3": "Creado por Gianni Di Prete",
        "footer_contact_label": "Contacto",

        "note_pdf": "Para obtener el procedimiento y las variaciones de ingredientes, compra y descarga el PDF.",

        "landing_eyebrow": "Donde la cocina se convierte en laboratorio",
        "landing_h1": "Crea recetas de helado equilibradas en pocos minutos.",
        "landing_p": "Nimue AI Studio – Edición Hogar te ayuda a crear recetas claras y repetibles, con ingredientes sencillos, pasos guiados y PDF exportable.",
        "landing_cta_primary": "Crea tu receta",
        "landing_cta_secondary": "Cómo funciona",
        "landing_note": "Sin cuenta. Solo pagas si quieres el PDF completo (pago único).",
        "landing_payment_trust": "Pago seguro con Stripe",

        "landing_for_who_title": "Para quién es",
        "landing_for_who_1_title": "Aficionados",
        "landing_for_who_1_desc": "Quieres un helado mejor en casa, sin improvisar.",
        "landing_for_who_2_title": "Curiosos",
        "landing_for_who_2_desc": "Quieres método y pasos, no cantidades al azar.",
        "landing_for_who_3_title": "Quienes quieren mejorar",
        "landing_for_who_3_desc": "Quieres una base sólida hoy y herramientas Pro mañana.",

        "landing_get_title": "Qué obtienes",
        "landing_get_1": "Recetas equilibradas para uso doméstico",
        "landing_get_2": "Perfiles (clásica, vegana, sin huevo, light, gourmet)",
        "landing_get_3": "Método guiado (con / sin heladera)",
        "landing_get_4": "Multilingüe",
        "landing_get_5": "PDF exportable",

        "landing_what_title": "Qué hace",
        "landing_what_1": "Te guía del sabor a la receta completa.",
        "landing_what_2": "Tabla clara (gramos) y procedimiento ordenado.",
        "landing_what_3": "Consejos prácticos de elaboración, servicio y conservación en casa.",

        "landing_not_title": "Qué no es",
        "landing_not_box": "Nimue no es un generador aleatorio de recetas ni un blog. Es una herramienta artesanal: fácil de usar, seria en los resultados.",

        "landing_bottom_title": "¿Listo para probar Nimue AI Studio?",

        "profile_opts": {
            "": "Estándar",
            "classica": "Clásica",
            "senza uova": "Sin huevo",
            "light": "Ligera",
            "vegana": "Vegana",
            "gourmet": "Gourmet",
        },
        "method_opts": {
            "": "Automático",
            "con gelatiera": "Con heladera",
            "senza gelatiera": "Sin heladera",
            "pacojet": "Pacojet",
        },

        "err_flavour": "Por favor, introduce un sabor.",
        "err_qty_zero": "La cantidad debe ser mayor que cero.",
        "err_qty_invalid": "Introduce una cantidad válida en kg (p. ej., 1 o 1,5).",
        "err_no_recipe": "No hay receta para exportar a PDF.",
    },

    "fr": {
        "app_title": "Nimue Glace Artisanale",
        "subtitle": "Édition Maison",
        "studio": "AI Studio",
        "tagline": "Tradition artisanale, précision intelligente.",

        "language": "Langue",
        "create": "Créer une recette",
        "helper": "Saisis le parfum et la quantité. Optionnel : profil et méthode.",
        "flavour": "Parfum",
        "quantity": "Quantité (kg)",
        "profile": "Profil",
        "method": "Méthode",
        "generate": "Générer la recette",
        "recipe_generated": "Recette générée",
        "no_recipe": "Aucune recette générée",
        "copy": "Copier le texte",
        "pdf": "Télécharger le PDF",
        "ingredients": "Ingrédients",
        "col_ing": "Ingrédient",
        "col_qty": "Quantité (g)",

        "pdf_title": "Nimue Glace Artisanale – AI Studio",
        "pdf_flavour": "Parfum",
        "pdf_amount": "Quantité",
        "pdf_profile": "Profil",
        "pdf_method": "Méthode",
        "footer_pdf": "© 2026 Nimue Glace Artisanale · Tous droits réservés · Créé par Gianni Di Prete",

        "footer_app_l1": "Nimue Glace Artisanale · AI Studio",
        "footer_app_l2": "© 2026 Tous droits réservés.",
        "footer_app_l3": "Créé par Gianni Di Prete",
        "footer_contact_label": "Contact",

        "note_pdf": "Pour obtenir la procédure complète et les variantes d’ingrédients, achetez et téléchargez le PDF.",

        "landing_eyebrow": "Là où la cuisine devient un laboratoire",
        "landing_h1": "Créez des recettes de glace équilibrées en quelques minutes.",
        "landing_p": "Nimue AI Studio – Édition Maison vous aide à créer des recettes claires et reproductibles, avec des ingrédients simples, un pas-à-pas et un PDF exportable.",
        "landing_cta_primary": "Créer ta recette",
        "landing_cta_secondary": "Comment ça marche",
        "landing_note": "Aucun compte. Tu ne paies que si tu veux le PDF complet (paiement unique).",
        "landing_payment_trust": "Paiement sécurisé avec Stripe",

        "landing_for_who_title": "Pour qui",
        "landing_for_who_1_title": "Passionnés",
        "landing_for_who_1_desc": "Vous voulez une meilleure glace à la maison, sans improviser.",
        "landing_for_who_2_title": "Curieux",
        "landing_for_who_2_desc": "Vous voulez une méthode et des étapes, pas des quantités au hasard.",
        "landing_for_who_3_title": "Ceux qui veulent progresser",
        "landing_for_who_3_desc": "Vous voulez une base solide aujourd’hui et des outils Pro demain.",

        "landing_get_title": "Ce que vous obtenez",
        "landing_get_1": "Recettes équilibrées pour la maison",
        "landing_get_2": "Profils (classique, végane, sans œufs, light, gourmet)",
        "landing_get_3": "Méthode guidée (avec / sans sorbetière)",
        "landing_get_4": "Multilingue",
        "landing_get_5": "PDF exportable",

        "landing_what_title": "Ce que ça fait",
        "landing_what_1": "Vous guide du parfum à la recette complète.",
        "landing_what_2": "Tableau clair (grammes) et procédure propre.",
        "landing_what_3": "Conseils pratiques pour la préparation, le service et la conservation à la maison.",

        "landing_not_title": "Ce que ce n’est pas",
        "landing_not_box": "Nimue n’est pas un générateur aléatoire de recettes ni un blog. C’est un outil artisanal : simple à utiliser, sérieux dans les résultats.",

        "landing_bottom_title": "Prêt à essayer Nimue AI Studio ?",

        "profile_opts": {
            "": "Standard",
            "classica": "Classique",
            "senza uova": "Sans œufs",
            "light": "Light",
            "vegana": "Végane",
            "gourmet": "Gourmet",
        },
        "method_opts": {
            "": "Automatique",
            "con gelatiera": "Avec sorbetière",
            "senza gelatiera": "Sans sorbetière",
            "pacojet": "Pacojet",
        },

        "err_flavour": "Veuillez saisir un parfum.",
        "err_qty_zero": "La quantité doit être supérieure à zéro.",
        "err_qty_invalid": "Veuillez saisir une quantité valide en kg (ex. 1 ou 1,5).",
        "err_no_recipe": "Aucune recette à exporter en PDF.",
    },

    "de": {
        "app_title": "Nimue Handwerkliches Gelato",
        "subtitle": "Home Edition",
        "studio": "AI Studio",
        "tagline": "Handwerkliche Tradition, intelligente Präzision.",

        "language": "Sprache",
        "create": "Rezept erstellen",
        "helper": "Geschmack und Menge eingeben. Optional: Profil und Methode wählen.",
        "flavour": "Geschmack",
        "quantity": "Menge (kg)",
        "profile": "Profil",
        "method": "Methode",
        "generate": "Rezept generieren",
        "recipe_generated": "Rezept generiert",
        "no_recipe": "Kein Rezept generiert",
        "copy": "Text kopieren",
        "pdf": "PDF herunterladen",
        "ingredients": "Zutaten",
        "col_ing": "Zutat",
        "col_qty": "Menge (g)",

        "pdf_title": "Nimue Handwerkliches Gelato – AI Studio",
        "pdf_flavour": "Geschmack",
        "pdf_amount": "Menge",
        "pdf_profile": "Profil",
        "pdf_method": "Methode",
        "footer_pdf": "© 2026 Nimue Handwerkliches Gelato · Alle Rechte vorbehalten · Erstellt von Gianni Di Prete",

        "footer_app_l1": "Nimue Handwerkliches Gelato · AI Studio",
        "footer_app_l2": "© 2026 Alle Rechte vorbehalten.",
        "footer_app_l3": "Erstellt von Gianni Di Prete",
        "footer_contact_label": "Kontakt",

        "note_pdf": "Um die vollständige Anleitung und Zutatenvarianten zu erhalten, kaufe und lade das PDF herunter.",

        "landing_eyebrow": "Wo die Küche zum Labor wird",
        "landing_h1": "Erstelle ausgewogene Gelato-Rezepte in wenigen Minuten.",
        "landing_p": "Nimue AI Studio – Home Edition hilft dir, klare und reproduzierbare Rezepte zu erstellen – mit einfachen Zutaten, Schritt-für-Schritt-Anleitung und exportierbarem PDF.",
        "landing_cta_primary": "Rezept erstellen",
        "landing_cta_secondary": "So funktioniert’s",
        "landing_note": "Kein Konto. Du zahlst nur, wenn du das vollständige PDF willst (einmalig).",
        "landing_payment_trust": "Sichere Zahlung mit Stripe",


        "landing_for_who_title": "Für wen",
        "landing_for_who_1_title": "Fans",
        "landing_for_who_1_desc": "Du willst zu Hause besseres Gelato, ohne zu raten.",
        "landing_for_who_2_title": "Neugierige",
        "landing_for_who_2_desc": "Du willst Methode und Schritte – keine Zufalls-Mengen.",
        "landing_for_who_3_title": "Wer sich verbessern will",
        "landing_for_who_3_desc": "Du willst heute eine solide Basis und morgen Pro-Tools.",

        "landing_get_title": "Was du bekommst",
        "landing_get_1": "Ausgewogene Rezepte für den Hausgebrauch",
        "landing_get_2": "Profile (klassisch, vegan, ohne Ei, light, gourmet)",
        "landing_get_3": "Geführte Methode (mit / ohne Eismaschine)",
        "landing_get_4": "Mehrsprachig",
        "landing_get_5": "Exportierbares PDF",

        "landing_what_title": "Was es macht",
        "landing_what_1": "Führt dich vom Geschmack zum vollständigen Rezept.",
        "landing_what_2": "Klare Zutatenliste (Gramm) und sauberer Ablauf.",
        "landing_what_3": "Praktische Tipps für Zubereitung, Servieren und Aufbewahrung zu Hause.",

        "landing_not_title": "Was es nicht ist",
        "landing_not_box": "Nimue ist kein zufälliger Rezeptgenerator und kein Blog. Es ist ein handwerkliches Tool: einfach zu nutzen, seriös in den Ergebnissen.",

        "landing_bottom_title": "Bereit, Nimue AI Studio zu testen?",

        "profile_opts": {
            "": "Standard",
            "classica": "Klassisch",
            "senza uova": "Ohne Ei",
            "light": "Light",
            "vegana": "Vegan",
            "gourmet": "Gourmet",
        },
        "method_opts": {
            "": "Automatisch",
            "con gelatiera": "Mit Eismaschine",
            "senza gelatiera": "Ohne Eismaschine",
            "pacojet": "Pacojet",
        },

        "err_flavour": "Bitte gib einen Geschmack ein.",
        "err_qty_zero": "Die Menge muss größer als null sein.",
        "err_qty_invalid": "Bitte gib eine gültige Menge in kg ein (z.B. 1 oder 1,5).",
        "err_no_recipe": "Kein Rezept zum PDF-Export.",
    },
}


# ==========================
#        LINGUA
# ==========================
def get_lang():
    lang = (
        request.args.get("lang")
        or request.form.get("lang")
        or session.get("lang")
        or "it"
    ).strip()

    if lang not in TRANSLATIONS:
        lang = "it"

    session["lang"] = lang
    return lang, TRANSLATIONS[lang]


# ==========================
#     FUNZIONI PDF
# ==========================
def draw_footer(c, width, bottom_margin, footer_text):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, bottom_margin - 18, footer_text)
    c.restoreState()


def wrap_text_to_lines(text, font_name, font_size, max_width):
    if not text:
        return [""]
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip() if current else w
        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
            continue
        if current:
            lines.append(current)
            current = w
        else:
            chunk = ""
            for ch in w:
                test2 = chunk + ch
                if stringWidth(test2, font_name, font_size) <= max_width:
                    chunk = test2
                else:
                    if chunk:
                        lines.append(chunk)
                    chunk = ch
            current = chunk
    if current:
        lines.append(current)
    return lines


# ==========================
#         ROUTES
# ==========================
@app.route("/app", methods=["GET", "POST"])
def app_page():
    lang, t = get_lang()

    recipe = None
    error = None
    flavour = ""
    quantity = ""
    profilo = ""
    metodo = ""

    pdf_unlocked = session.get("pdf_unlocked", False)

    if request.method == "POST":
        flavour = request.form.get("flavour", "").strip()
        quantity = request.form.get("quantity", "").strip()
        profilo = request.form.get("profilo", "").strip()
        metodo = request.form.get("metodo", "").strip()

        # nuova ricetta => reset sblocco PDF
        session["pdf_unlocked"] = False
        pdf_unlocked = False

        if not flavour:
            error = t["err_flavour"]

        quantita_kg = None
        if not error:
            try:
                quantita_kg = float(quantity.replace(",", "."))
                if quantita_kg <= 0:
                    error = t["err_qty_zero"]
            except ValueError:
                error = t["err_qty_invalid"]

        if not error:
            # qui chiami il modello (quando avrai di nuovo la chiave attiva)
            recipe = genera_ricetta_testo(
                flavour,
                quantita_kg,
                profilo or None,
                metodo or None,
                lang=lang,
            )

            if recipe:
                session["last_recipe"] = recipe
                session["last_flavour"] = flavour
                session["last_quantity"] = quantity
                session["last_profilo"] = profilo
                session["last_metodo"] = metodo


    return render_template(
        "index.html",
        recipe=recipe,
        error=error,
        flavour=flavour,
        quantity=quantity,
        profilo=profilo,
        metodo=metodo,
        lang=lang,
        t=t,
        pdf_unlocked=pdf_unlocked,
    )


@app.route("/", methods=["GET"])
def landing():
    lang, t = get_lang()
    return render_template("landing.html", lang=lang, t=t)


@app.route("/api/genera_ricetta", methods=["POST"])
def api_genera_ricetta():
    lang = (request.args.get("lang") or session.get("lang") or "it").strip()
    if lang not in TRANSLATIONS:
        lang = "it"

    data = request.get_json(silent=True) or {}
    gusto = data.get("gusto", "").strip()
    quantita = data.get("quantita_kg", None)
    profilo = data.get("profilo") or None
    metodo = data.get("metodo") or None

    if not gusto:
        return jsonify({"error": "Missing 'gusto'"}), 400

    try:
        quantita_kg = float(str(quantita).replace(",", "."))
        if quantita_kg <= 0:
            return jsonify({"error": "Invalid quantity"}), 400
    except Exception:
        return jsonify({"error": "Invalid quantity"}), 400

    recipe = genera_ricetta_testo(gusto, quantita_kg, profilo, metodo, lang=lang)
    return jsonify({"recipe": recipe, "lang": lang})


@app.route("/download_pdf", methods=["GET", "POST"])
def download_pdf():
    # lang: se GET lo prendi da querystring, se POST dal form
    lang = (
        request.args.get("lang")
        or request.form.get("lang")
        or session.get("lang")
        or "it"
    ).strip()
    t = TRANSLATIONS.get(lang, TRANSLATIONS["it"])

    # 🔒 BLOCCO ACCESSO PDF SE NON PAGATO
    if not session.get("pdf_unlocked", False):
        return redirect(url_for("app_page", lang=lang, keep=1))

    # Se arrivi in GET (dopo pagamento), prendi tutto dalla sessione
    if request.method == "GET":
        recipe_text = (session.get("last_recipe") or "").strip()
        flavour = (session.get("last_flavour") or "Gelato").strip()
        quantity = (session.get("last_quantity") or "").strip()
        profilo = (session.get("last_profilo") or "").strip()
        metodo = (session.get("last_metodo") or "").strip()
    else:
        # Se arrivi dal bottone "PDF sbloccato", prendi dal form (come già fai)
        recipe_text = (request.form.get("recipe_text") or "").strip()
        flavour = (request.form.get("flavour") or "").strip() or "Gelato"
        quantity = (request.form.get("quantity") or "").strip()
        profilo = (request.form.get("profilo") or "").strip()
        metodo = (request.form.get("metodo") or "").strip()


    if not recipe_text:
        return render_template(
            "index.html",
            recipe=None,
            error=t["err_no_recipe"],
            flavour="",
            quantity="",
            profilo="",
            metodo="",
            lang=lang,
            t=t,
            pdf_unlocked=False,
        )

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 72
    right_margin = 72
    top_margin = height - 72
    bottom_margin = 72
    max_text_width = width - left_margin - right_margin

    c.setTitle(t["pdf_title"])

    def new_page():
        c.showPage()
        draw_footer(c, width, bottom_margin, t["footer_pdf"])

    draw_footer(c, width, bottom_margin, t["footer_pdf"])

    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, top_margin, t["pdf_title"])

    c.setFont("Helvetica", 11)
    y = top_margin - 20

    subtitle = f"{t['pdf_flavour']}: {flavour}"
    if quantity:
        subtitle += f"    ·    {t['pdf_amount']}: {quantity} kg"
    c.drawString(left_margin, y, subtitle)

    y -= 16
    details = []
    if profilo:
        profilo_label = t.get("profile_opts", {}).get(profilo, profilo)
        details.append(f"{t['pdf_profile']}: {profilo_label}")
    if metodo:
        metodo_label = t.get("method_opts", {}).get(metodo, metodo)
        details.append(f"{t['pdf_method']}: {metodo_label}")

    if details:
        c.drawString(left_margin, y, " · ".join(details))
        y -= 20
    else:
        y -= 10

    righe = recipe_text.splitlines()

    start_idx = None
    end_idx = None

    for i, line in enumerate(righe):
        s = line.strip()
        if s.startswith("|") and s.count("|") >= 2:
            start_idx = i
            break

    if start_idx is not None:
        j = start_idx
        while j < len(righe):
            s = righe[j].strip()
            if s.startswith("|") and s.count("|") >= 2:
                j += 1
                continue
            if s == "":
                j += 1
                continue
            break
        end_idx = j

    table_block = (
        righe[start_idx:end_idx]
        if (start_idx is not None and end_idx is not None)
        else []
    )

    rows = []
    for raw in table_block:
        s = raw.strip()
        if not (s.startswith("|") and s.count("|") >= 2):
            continue
        if set(s.replace("|", "").strip()) <= set("- "):
            continue
        parts = [x.strip() for x in s.strip("|").split("|")]
        if len(parts) >= 2:
            rows.append([parts[0], parts[1]])

    tabella = rows[1:] if len(rows) >= 2 else []

    if tabella:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, y, t["ingredients"])
        y -= 18

        data = [[t["col_ing"], t["col_qty"]]] + tabella
        table = Table(data, colWidths=[340, 100])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2d9c2")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        w, h = table.wrap(0, 0)
        if y - h < bottom_margin + 30:
            new_page()
            y = height - 72

        table.drawOn(c, left_margin, y - h)
        y = y - h - 18

    remaining = righe[:]
    if start_idx is not None and end_idx is not None and end_idx > start_idx:
      remaining = righe[:start_idx] + righe[end_idx:]

    font_name = "Helvetica"
    font_size = 10
    leading = 13

    for line in remaining:
        raw = (line or "").rstrip()

        if raw.strip() == "":
            y -= leading * 0.6
            if y <= bottom_margin + 30:
                new_page()
                y = height - 72
            continue

        is_heading = raw.strip().startswith("###")
        text_line = raw.replace("###", "").strip() if is_heading else raw

        if is_heading:
            c.setFont("Helvetica-Bold", 11)
            for wl in wrap_text_to_lines(
                text_line, "Helvetica-Bold", 11, max_text_width
            ):
                if y <= bottom_margin + 30:
                    new_page()
                    y = height - 72
                    c.setFont("Helvetica-Bold", 11)
                c.drawString(left_margin, y, wl)
                y -= 14
            y -= 4
            c.setFont(font_name, font_size)
            continue

        c.setFont(font_name, font_size)
        for wl in wrap_text_to_lines(
            text_line, font_name, font_size, max_text_width
        ):
            if y <= bottom_margin + 30:
                new_page()
                y = height - 72
                c.setFont(font_name, font_size)
            c.drawString(left_margin, y, wl)
            y -= leading

    c.save()
    buffer.seek(0)

    # ogni volta che scarica il PDF, richiudi lo sblocco
    session["pdf_unlocked"] = False

    filename = f"Nimue_AI_Studio_{lang}_{flavour.replace(' ', '_')}.pdf"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )



@app.route("/buy_pdf", methods=["POST"])
def buy_pdf():
    """
    Paywall finto: marca il PDF come sbloccato.
    In produzione qui ci andrà Stripe Checkout o simile.
    """
    lang = (request.form.get("lang") or session.get("lang") or "it").strip()
    if lang not in TRANSLATIONS:
        lang = "it"

    session["pdf_unlocked"] = True
    return redirect(url_for("app_page", lang=lang))


@app.route("/api/sostituzioni", methods=["POST"])
def api_sostituzioni():
    data = request.json or {}
    ingredient = (data.get("ingredient") or "").strip()

    if not ingredient:
        return jsonify({"error": "Ingrediente mancante"}), 400

    options = get_substitutions(ingredient)

    return jsonify({"ingredient": ingredient, "substitutions": options})

@app.route("/pay_pdf", methods=["POST"])
def pay_pdf():
    lang, t = get_lang()

    if not session.get("last_recipe"):
        # niente ricetta => torna indietro
        return redirect(url_for("app_page", lang=lang))

    # qui poi sostituiremo con Stripe
    return redirect(url_for("paywall_page", lang=lang, keep=1))

@app.route("/paywall")
def paywall_page():
    lang, t = get_lang()
    if not session.get("last_recipe"):
        return redirect(url_for("app_page", lang=lang))
    return render_template("paywall.html", lang=lang)

@app.route("/stripe/checkout", methods=["POST"])
def stripe_checkout():
    lang, t = get_lang()

    if not session.get("last_recipe"):
        return redirect(url_for("app_page", lang=lang))

    if not stripe.api_key or not STRIPE_PRICE_ID:
        return "Stripe non configurato", 500

    success_url = (
        url_for("stripe_success", _external=True)
        + "?session_id={CHECKOUT_SESSION_ID}&lang="
        + lang
    )
    cancel_url = url_for("app_page", _external=True, lang=lang, keep=1)

    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return redirect(checkout_session.url, code=303)



@app.route("/stripe/success", methods=["GET"])
def stripe_success():
    lang, t = get_lang()
    session_id = request.args.get("session_id", "").strip()

    if not session.get("last_recipe"):
        return redirect(url_for("app_page", lang=lang))

    if not session_id:
        return redirect(url_for("app_page", lang=lang, keep=1))

    try:
        s = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return redirect(url_for("app_page", lang=lang, keep=1))

    if s.get("payment_status") == "paid" or s.get("status") == "complete":
        session["pdf_unlocked"] = True
        return redirect(url_for("app_page", lang=lang, keep=1, dl=1))

    return redirect(url_for("app_page", lang=lang, keep=1))

@app.route("/pay_ok", methods=["POST"])
def pay_ok():
    lang, t = get_lang()

    if not session.get("last_recipe"):
        return redirect(url_for("app_page", lang=lang))

    session["pdf_unlocked"] = True
    return redirect(url_for("download_pdf", lang=lang))

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        return "Webhook secret missing", 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Payload non valido
        abort(400)
    except stripe.error.SignatureVerificationError:
        # Firma non valida
        abort(400)

    # ✅ EVENTO PRINCIPALE
    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]

        # Qui puoi usare metadata se vuoi in futuro
        # user_id = session_obj.get("metadata", {}).get("user_id")

        # Per ora logghiamo e basta
        print("✅ Pagamento confermato via webhook:", session_obj["id"])

        # Qui in futuro potrai:
        # - salvare su DB
        # - inviare email
        # - sbloccare download persistenti

    return "", 200


@app.get("/health")
def health():
    return jsonify(ok=True)

@app.get("/version")
def version():
    import os
    return jsonify(
        version="2026-01-04 webhook-step-1",
        render_commit=os.environ.get("RENDER_GIT_COMMIT", "unknown")
    )

@app.route("/blog")
def blog_index():
    lang, t = get_lang()
    return render_template("blog/index.html", lang=lang, t=t)

@app.route("/blog/why-homemade-ice-cream-turns-icy")
def blog_post_icy():
    lang, t = get_lang()
    return render_template("blog/why-homemade-ice-cream-turns-icy.html", lang=lang, t=t)



if __name__ == "__main__":
    app.run(debug=True)
