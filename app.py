import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Personel Güncelleyici", layout="wide")
st.title("⚖️ Adalet Bakanlığı Personel Güncelleme")

# Dosya Yükleme Alanı
c1, c2 = st.columns(2)
with c1:
    eski_file = st.file_uploader("1. Eski (Ana) Excel'i Yükle", type=["xlsx"])
with c2:
    yeni_file = st.file_uploader("2. Yeni Verili Excel'i Yükle", type=["xlsx"])

# İşlem ve İndirme Alanı (En Üstte)
if eski_file and yeni_file:
    try:
        df_eski = pd.read_excel(eski_file)
        df_yeni = pd.read_excel(yeni_file)

        # Temizlik: Sütun isimleri ve Sicil verileri
        df_eski.columns = [str(c).strip() for c in df_eski.columns]
        df_yeni.columns = [str(c).strip() for c in df_yeni.columns]
        
        anahtar = "Sicil"

        if anahtar in df_eski.columns and anahtar in df_yeni.columns:
            # Sicilleri eşleşme için standart hale getir
            df_eski[anahtar] = df_eski[anahtar].astype(str).str.strip()
            df_yeni[anahtar] = df_yeni[anahtar].astype(str).str.strip()

            df_final = df_eski.copy()
            rapor_verisi = []

            # Güncelleme Döngüsü
            for _, yeni_row in df_yeni.iterrows():
                sicil = yeni_row[anahtar]
                if sicil in df_final[anahtar].values:
                    # Yeni dosyada olan tüm kolonları eski dosyada güncelle (Sicil hariç)
                    for col in df_yeni.columns:
                        if col != anahtar and col in df_final.columns:
                            yeni_val = yeni_row[col]
                            eski_val = df_final.loc[df_final[anahtar] == sicil, col].values[0]

                            if str(eski_val).strip() != str(yeni_val).strip() and pd.notnull(yeni_val):
                                rapor_verisi.append({
                                    "Sicil": sicil,
                                    "Personel": df_final.loc[df_final[anahtar] == sicil, 'Personel'].values[0] if 'Personel' in df_final.columns else sicil,
                                    "Sütun": col,
                                    "Eski": eski_val,
                                    "Yeni": yeni_val
                                })
                                df_final.loc[df_final[anahtar] == sicil, col] = yeni_val

            # --- İNDİRME BUTONU (İŞLEM VARSA EN ÜSTTE) ---
            if rapor_verisi:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                
                st.success(f"✅ {len(rapor_verisi)} adet hücre güncellemesi yapıldı. Dosyanız hazır.")
                st.download_button(
                    label="📥 GÜNCEL EXCEL'İ İNDİR",
                    data=output.getvalue(),
                    file_name="guncellenmis_personel_listesi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Rapor Detayları (Alt Kısımda)
                with st.expander("Değişim Detaylarını Gör"):
                    st.table(pd.DataFrame(rapor_verisi))
            else:
                st.info("Eşleşen siciller bulundu ancak herhangi bir veri farkı tespit edilemedi.")
        else:
            st.error(f"Hata: Dosyalarda '{anahtar}' sütunu bulunamadı.")
            
    except Exception as e:
        st.error(f"Beklenmedik bir hata: {e}")
else:
    st.warning("Lütfen her iki dosyayı da yükleyin.")