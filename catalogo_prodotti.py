import streamlit as st
import pandas as pd
import csv
import os

# 📥 Carica prodotti da CSV
def carica_catalogo_da_csv(file_csv='prodotti.csv'):
    prodotti = []
    if os.path.exists(file_csv):
        with open(file_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prodotto = {
                    "chiave": row["chiave"],
                    "nome": row["nome"],
                    "codice": row["codice"],
                    "colore": row["colore"],
                    "azienda": row["azienda"],
                    "vaso": row["vaso"],
                    "macchine": [int(m.strip()) for m in row["macchine"].split(",") if m.strip().isdigit()],
                    "ubicazioni": [u.strip() for u in row["ubicazioni"].split(",") if u.strip()]
                }
                prodotti.append(prodotto)
    return prodotti

# 💾 Salva un nuovo prodotto nel CSV
def salva_prodotto_su_csv(prodotto, file_csv='prodotti.csv'):
    file_esiste = os.path.exists(file_csv)
    with open(file_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_esiste:
            writer.writerow(["chiave", "nome", "codice", "colore", "azienda", "vaso", "macchine", "ubicazioni"])
        writer.writerow([
            prodotto["chiave"],
            prodotto["nome"],
            prodotto["codice"],
            prodotto["colore"],
            prodotto["azienda"],
            prodotto["vaso"],
            ",".join(map(str, prodotto["macchine"])),
            ",".join(prodotto["ubicazioni"])
        ])

# 📁 Carica i prodotti salvati nel dizionario "prodotti"
prodotti_salvati = carica_catalogo_da_csv()
prodotti = {prod.get("chiave", f"OBEN{str(i).zfill(3)}"): prod for i, prod in enumerate(prodotti_salvati, start=1)}

# 📥 Formulario per aggiungere prodotti
with st.expander("➕ Aggiungi nuovo prodotto al catalogo (CSV)"):
    nome = st.text_input("📦 Nome del Prodotto")
    codice = st.text_input("🏷️ Codice Interno")
    colore = st.selectbox("🎨 Colore", ["Neutro", "Bianco"])
    azienda = st.text_input("🏢 Azienda produttrice")
    vaso = st.text_input("🧫 Tipo di Vaso")
    macchine_str = st.text_input("🔧 Macchine (es. 1,2,3,4)")
    ubicazioni_str = st.text_input("📍 Ubicazioni (es. Stanza 1,Stanza 2,...)")

    ultimo_numero = 0
    for chiave in prodotti.keys():
        if chiave.startswith("OBEN"):
            try:
                numero = int(chiave.replace("OBEN", ""))
                if numero > ultimo_numero:
                    ultimo_numero = numero
            except:
                pass
    chiave_suggerita = f"OBEN{str(ultimo_numero + 1).zfill(3)}"
    st.markdown(f"🔎 **Chiave suggerita:** `{chiave_suggerita}`")

    chiave_input = st.text_input("🔢 Numero OBEN", value=chiave_suggerita)

    if st.button("✅ Salva Prodotto (CSV)"):
        if not all([nome, codice, colore, azienda, vaso, macchine_str, ubicazioni_str, chiave_input]):
            st.warning("⚠️ Tutti i campi sono obbligatori.")
        elif chiave_input in prodotti:
            st.error("❌ Questa chiave OBEN esiste già. Scegli un altro numero.")
        else:
            macchine = [int(m.strip()) for m in macchine_str.split(",") if m.strip().isdigit()]
            ubicazioni = [u.strip() for u in ubicazioni_str.split(",") if u.strip()]
            if len(ubicazioni) < 1:
                st.warning("⚠️ Inserisci almeno una ubicazione.")
            elif not macchine:
                st.warning("⚠️ Inserisci almeno una macchina valida (es. 1,2,3,4).")
            else:
                prodotto_nuovo = {
                    "chiave": chiave_input,
                    "nome": nome,
                    "codice": codice,
                    "colore": colore,
                    "azienda": azienda,
                    "vaso": vaso,
                    "macchine": macchine,
                    "ubicazioni": ubicazioni
                }
                prodotti[chiave_input] = prodotto_nuovo
                salva_prodotto_su_csv(prodotto_nuovo)
                st.success(f"✅ Prodotto {chiave_input} salvato nel file CSV. 🎉")

# 📊 Visualizza ultimi prodotti salvati
with st.expander("📋 Prodotti salvati nel CSV"):
    if prodotti:
        ultimi_prodotti = list(prodotti.items())[-5:]
        df_visuale = [{**v, "chiave": k} for k, v in ultimi_prodotti]
        df = pd.DataFrame(df_visuale)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ℹ️ Nessun prodotto salvato al momento.")

# 🔄 Aggiorna ubicazioni e registra movimenti
with st.expander("🔄 Aggiorna ubicazioni di un prodotto esistente"):
    chiavi_disponibili = list(prodotti.keys())
    chiave_selezionata = st.selectbox("🔢 Seleziona la chiave OBEN da modificare", chiavi_disponibili)

    prodotto_corrente = prodotti.get(chiave_selezionata)
    if prodotto_corrente:
        st.markdown(f"**Ubicazioni attuali:** `{', '.join(prodotto_corrente['ubicazioni'])}`")
        nuove_ubicazioni_str = st.text_input("📍 Nuove ubicazioni (es. Stanza 3,Stanza 2,...)", value=",".join(prodotto_corrente["ubicazioni"]))

        if st.button("💾 Aggiorna ubicazioni"):
            nuove_ubicazioni = [u.strip() for u in nuove_ubicazioni_str.split(",") if u.strip()]
            if len(nuove_ubicazioni) < 1:
                st.warning("⚠️ Inserisci almeno una nuova ubicazione.")
            else:
                # Registra il movimento nel file movimenti.csv
                with open('movimenti.csv', 'a', newline='', encoding='utf-8') as f_mov:
                    writer_mov = csv.writer(f_mov)
                    if f_mov.tell() == 0:
                        writer_mov.writerow(["chiave", "vecchie_ubicazioni", "nuove_ubicazioni", "timestamp"])
                    writer_mov.writerow([
                        chiave_selezionata,
                        ",".join(prodotto_corrente["ubicazioni"]),
                        ",".join(nuove_ubicazioni),
                        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])

                # Aggiorna il prodotto in memoria
                prodotto_corrente["ubicazioni"] = nuove_ubicazioni

                # Sovrascrive tutto il CSV con i prodotti aggiornati
                with open('prodotti.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["chiave", "nome", "codice", "colore", "azienda", "vaso", "macchine", "ubicazioni"])
                    for prod in prodotti.values():
                        writer.writerow([
                            prod["chiave"],
                            prod["nome"],
                            prod["codice"],
                            prod["colore"],
                            prod["azienda"],
                            prod["vaso"],
                            ",".join(map(str, prod["macchine"])),
                            ",".join(prod["ubicazioni"])
                        ])
                st.success(f"✅ Ubicazioni per {chiave_selezionata} aggiornate con successo e movimento registrato.")
