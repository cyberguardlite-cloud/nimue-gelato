import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SUPPORTED_LANGS = {"it", "en", "es", "fr", "de"}


def _system_prompt(lang: str) -> str:
    lang = (lang or "it").lower().strip()
    if lang not in SUPPORTED_LANGS:
        lang = "it"

    base_rules_it = """
REGOLE IMPORTANTI:
- Lavora sempre per quantità totali (es. 1 kg, 1.5 kg, 2 kg).
- Usa ingredienti facilmente reperibili (latte intero, panna, zucchero, tuorli, latte in polvere, destrosio, miele, ecc.).
- Stabilizzanti solo semplici e opzionali se necessari (es. farina di semi di carrube).
- Bilanciamento realistico (zuccheri 16–22%, grassi 6–10%, ecc.).
- Adatta allo STILE e al METODO se specificati.
- Se il profilo è "vegana", la ricetta deve essere 100% vegana (no latticini/uova/derivati animali).

FORMATO (IMPORTANTISSIMO):
1) Titolo
2) Quantità totale
3) Tabella ingredienti MARKDOWN con ESATTAMENTE 2 colonne (ingredient / grams)
4) Procedimento passo-passo
5) Varianti e sostituzioni (SOLO se nella ricetta hai usato ingredienti “non comuni”):
- Se hai usato farina di semi di carrube (carruba/E410): indica 2–3 alternative reperibili (gomma di guar, xantano, maizena) con rapporto di sostituzione e una nota sull'effetto.
- Se hai usato olio di cocco: indica 2 alternative e come cambia la texture/gusto.
- Se hai usato pasta di pistacchio/nocciola: indica alternative (pistacchi/nocciole 100% frullati, crema 100% frutta secca, ecc.) e una nota su come aggiustare lo zucchero.
- Se hai usato destrosio/sciroppo di glucosio/latte in polvere: indica alternative da supermercato e cosa cambia.
- Limita ogni ingrediente a massimo 2–3 alternative.
- Scrivi questa sezione in modo pratico e breve.
- Non aggiungere una nuova tabella.
- Non modificare la ricetta principale: le varianti sono SOLO suggerimenti.
- Spiega le sostituzioni come consiglio pratico per casa, non come regola tecnica.
- Scrivi la sezione "Varianti e sostituzioni" nella stessa lingua della ricetta, usando nomi comuni nel paese dell’utente.
- Grammi nella seconda colonna
- Header tabella come PRIMA riga
- Nessuna colonna extra
""".strip()

    if lang == "fr":
        return f"""
Tu es un maître glacier. Langue de sortie: Français.
N'utilise PAS l'italien. Si tu t'écartes, réécris entièrement en Français.

{base_rules_it}
""".strip()

    if lang == "de":
        return f"""
Du bist ein Gelato-Meister. Ausgabesprache: Deutsch.
Verwende KEIN Italienisch. Wenn du abweichst, schreibe vollständig auf Deutsch neu.

{base_rules_it}
""".strip()

    if lang == "en":
        return f"""
You are a gelato master. Output language: English.
Do NOT use Italian. If you drift, rewrite fully in English.

{base_rules_it}
""".strip()

    if lang == "es":
        return f"""
Eres un maestro heladero. Idioma de salida: Español.
NO uses italiano. Si te desvías, reescribe todo en Español.

{base_rules_it}
""".strip()

    # it
    return f"""
Sei un maestro gelatiere italiano. Lingua di output: Italiano.

{base_rules_it}
""".strip()


def _vegan_constraints(lang: str) -> str:
    lang = (lang or "it").lower().strip()
    if lang not in SUPPORTED_LANGS:
        lang = "it"

    if lang == "en":
        return (
            "Vegan constraints: NO dairy (milk, cream, milk powder, whey), NO eggs, "
            "NO animal-derived ingredients. Use plant-based alternatives (soy/oat/almond drink), "
            "vegetable fats (deodorized coconut oil or cocoa butter), and plant stabilizers "
            "(carob/guar)."
        )
    if lang == "fr":
        return (
            "Contraintes véganes : PAS de produits laitiers (lait, crème, lait en poudre, lactosérum), "
            "PAS d’œufs, PAS d’ingrédients d’origine animale. Utilise des alternatives végétales "
            "(boisson soja/avoine/amande), graisses végétales (huile de coco désodorisée ou beurre de cacao) "
            "et stabilisants végétaux (caroube/guar)."
        )
    if lang == "de":
        return (
            "Vegan-Vorgaben: KEINE Milchprodukte (Milch, Sahne, Milchpulver, Molke), KEINE Eier, "
            "KEINE tierischen Zutaten. Nutze pflanzliche Alternativen (Soja/Hafer/Mandel-Drink), "
            "pflanzliche Fette (desodoriertes Kokosöl oder Kakaobutter) und pflanzliche Stabilisatoren "
            "(Johannisbrot/Guar)."
        )
    if lang == "es":
        return (
            "Restricciones veganas: NO lácteos (leche, nata, leche en polvo, suero), NO huevos, "
            "NO ingredientes de origen animal. Usa alternativas vegetales (bebida de soja/avena/almendra), "
            "grasas vegetales (aceite de coco desodorizado o manteca de cacao) y estabilizantes vegetales "
            "(algarrobo/guar)."
        )

    # it
    return (
        "Vincoli vegani: NIENTE latticini (latte, panna, latte in polvere, siero), NIENTE uova, "
        "NESSUN ingrediente di origine animale. Usa alternative vegetali (bevanda di soia/avena/mandorla), "
        "grassi vegetali (olio di cocco deodorato o burro di cacao) e stabilizzanti vegetali (carrube/guar)."
    )


def _user_prompt_localized(
    gusto: str,
    quantita_kg: float,
    profilo: str | None,
    metodo: str | None,
    lang: str
) -> str:
    lang = (lang or "it").lower().strip()
    if lang not in SUPPORTED_LANGS:
        lang = "it"

    profilo_txt = (profilo or "").strip()
    metodo_txt = (metodo or "").strip()

    vegan_block = ""
    if profilo_txt.lower() == "vegana":
        vegan_block = "\n\n" + _vegan_constraints(lang)

    if lang == "fr":
        pref = []
        if profilo_txt:
            pref.append(f"Style: {profilo_txt}.")
        if metodo_txt:
            pref.append(f"Méthode: {metodo_txt}.")
        pref_block = ("\nPréférences:\n- " + "\n- ".join(pref)) if pref else ""
        return (
            f"Je veux préparer une glace (gelato) au goût: {gusto}.\n"
            f"Quantité totale: {quantita_kg} kg de mélange.\n"
            f"{pref_block}"
            f"{vegan_block}\n\n"
            "Génère une recette complète en respectant les règles du système.\n"
            "Inclue une table d’ingrédients en MARKDOWN avec EXACTEMENT 2 colonnes.\n"
            "La 2e colonne doit être en grammes (g)."
        )

    if lang == "de":
        pref = []
        if profilo_txt:
            pref.append(f"Stil/Profil: {profilo_txt}.")
        if metodo_txt:
            pref.append(f"Methode: {metodo_txt}.")
        pref_block = ("\nPräferenzen:\n- " + "\n- ".join(pref)) if pref else ""
        return (
            f"Ich möchte Gelato mit Geschmack: {gusto} zubereiten.\n"
            f"Gesamtmenge: {quantita_kg} kg Mischung.\n"
            f"{pref_block}"
            f"{vegan_block}\n\n"
            "Erstelle ein vollständiges Rezept gemäß den Systemregeln.\n"
            "Füge eine Zutaten-Tabelle in MARKDOWN mit GENAU 2 Spalten ein.\n"
            "Die 2. Spalte muss Gramm (g) enthalten."
        )

    if lang == "en":
        pref = []
        if profilo_txt:
            pref.append(f"Style/profile: {profilo_txt}.")
        if metodo_txt:
            pref.append(f"Method: {metodo_txt}.")
        pref_block = ("\nPreferences:\n- " + "\n- ".join(pref)) if pref else ""
        return (
            f"I want to make homemade gelato with flavor: {gusto}.\n"
            f"Total batch size: {quantita_kg} kg of mix.\n"
            f"{pref_block}"
            f"{vegan_block}\n\n"
            "Generate a complete recipe following the system rules.\n"
            "Include a MARKDOWN ingredients table with EXACTLY 2 columns.\n"
            "Second column must be grams (g)."
        )

    if lang == "es":
        pref = []
        if profilo_txt:
            pref.append(f"Estilo/perfil: {profilo_txt}.")
        if metodo_txt:
            pref.append(f"Método: {metodo_txt}.")
        pref_block = ("\nPreferencias:\n- " + "\n- ".join(pref)) if pref else ""
        return (
            f"Quiero preparar helado (gelato) con sabor: {gusto}.\n"
            f"Cantidad total: {quantita_kg} kg de mezcla.\n"
            f"{pref_block}"
            f"{vegan_block}\n\n"
            "Genera una receta completa siguiendo las reglas del sistema.\n"
            "Incluye una tabla de ingredientes en MARKDOWN con EXACTAMENTE 2 columnas.\n"
            "La segunda columna debe estar en gramos (g)."
        )

    # it
    pref = []
    if profilo_txt:
        pref.append(f"Stile/profilo ricetta: {profilo_txt}.")
    if metodo_txt:
        pref.append(f"Metodo di preparazione preferito: {metodo_txt}.")
    pref_block = ("\n\nPreferenze utente:\n- " + "\n- ".join(pref)) if pref else ""
    return (
        f"Voglio preparare a casa un gelato al gusto: {gusto}.\n"
        f"Quantità totale desiderata: {quantita_kg} kg di miscela.\n"
        f"{pref_block}"
        f"{vegan_block}\n\n"
        "Genera una ricetta completa seguendo le regole del sistema.\n"
        "Includi una tabella ingredienti in MARKDOWN con ESATTAMENTE 2 colonne.\n"
        "La seconda colonna deve essere in grammi (g)."
    )


def _looks_italian(text: str) -> bool:
    # euristica semplice: se trovi molte parole funzionali italiane, probabile drift
    it_hits = re.findall(
        r"\b(il|lo|la|gli|le|un|una|che|per|con|senza|poi|quindi|maturazione|mantecazione)\b",
        (text or "").lower()
    )
    return len(it_hits) >= 6


def genera_ricetta_testo(
    gusto: str,
    quantita_kg: float,
    profilo: str | None = None,
    metodo: str | None = None,
    lang: str = "it",
) -> str:
    lang = (lang or "it").lower().strip()
    if lang not in SUPPORTED_LANGS:
        lang = "it"

    sys_prompt = _system_prompt(lang)
    user_prompt = _user_prompt_localized(gusto, quantita_kg, profilo, metodo, lang)

    # 1° tentativo
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
    )
    text = completion.choices[0].message.content or ""

    # retry “anti-italiano” per fr/de/en/es se necessario
    if lang in {"fr", "de", "en", "es"} and _looks_italian(text):
        stricter = sys_prompt + "\n\nSTRICT RULE: If any Italian appears, rewrite the entire recipe in the output language."
        completion2 = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": stricter},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        text2 = completion2.choices[0].message.content or ""
        if text2.strip():
            return text2

    return text
