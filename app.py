import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Personel Güncelleyici & Raporlayıcı", layout="wide")

st.title("🚀 Personel Veri Güncelleme ve Raporlama")
st.markdown("Sicil üzerinden eşleştirme yapar ve değişimleri raporlar.")

col1, col2 = st.columns(2)
with col1:
    eski_file = st.file_uploader("1. Eski (Ana) Excel'i Yükle", type=["xlsx"])
with col2:
    yeni_file = st.file_uploader("2. Yeni Verili Excel'i Yükle", type=["xlsx"])

keys_input = st.text_input("Eşleşecek Sütunlar (Örn: Sicil veya Sicil, Personel)", value="Sicil")

if st.button("Güncelle ve Rapor Oluştur", type="primary"):
    if eski_file and yeni_file:
        try:
            df_eski = pd.read_excel(eski_file)
            df_yeni = pd.read_excel(yeni_file)

            # Sütun isimlerini temizle
            df_eski.columns = [str(c).strip() for c in df_eski.columns]
            df_yeni.columns = [str(c).strip() for c in df_yeni.columns]
            
            anahtar_sutunlar = [s.strip() for s in keys_input.split(",")]

            if all(c in df_eski.columns and c in df_yeni.columns for c in anahtar_sutunlar):
                # Eşleşme hazırlığı
                df_eski_temp = df_eski.copy()
                df_yeni_temp = df_yeni.copy()
                
                # Eşleşme anahtarını oluştur
                df_eski_temp['match_key'] = df_eski_temp[anahtar_sutunlar].astype(str).sum(axis=1).str.lower().str.strip()
                df_yeni_temp['match_key'] = df_yeni_temp[anahtar_sutunlar].astype(str).sum(axis=1).str.lower().str.strip()

                # Mükerrerleri temizle
                df_eski_temp = df_eski_temp.drop_duplicates('match_key')
                df_yeni_temp = df_yeni_temp.drop_duplicates('match_key')

                # Karşılaştırma için birleştir
                df_merge = pd.merge(df_eski_temp, df_yeni_temp, on='match_key', suffixes=('_eski', '_yeni'))

                # --- RAPORLAMA MANTIĞI ---
                rapor_listesi = []
                guncellenen_df = df_eski.copy()
                guncellenen_df['match_key'] = guncellenen_df[anahtar_sutunlar].astype(str).sum(axis=1).str.lower().str.strip()
                
                degisim_sayisi = 0

                for index, row in df_merge.iterrows():
                    degisim_notu = []
                    # Sadece belirli kolonlardaki değişimlere bak (Örn: Görev Yeri, Unvan)
                    for col in df_yeni.columns:
                        if col not in anahtar_sutunlar and col in df_eski.columns:
                            eski_val = str(row[f"{col}_eski"])
                            yeni_val = str(row[f"{col}_yeni"])
                            
                            if eski_val != yeni_val and yeni_val != "nan":
                                degisim_notu.append(f"{col}: {eski_val} ➡️ {yeni_val}")
                                # Ana dosyayı güncelle
                                guncellenen_df.loc[guncellenen_df['match_key'] == row['match_key'], col] = row[f"{col}_yeni"]

                    if degisim_notu:
                        degisim_sayisi += 1
                        rapor_listesi.append({
                            "Personel": row.get('Personel_eski', row['match_key']),
                            "Sicil": row.get('Sicil_eski', 'N/A'),
                            "Değişimler": " | ".join(degisim_notu)
                        })

                # Arayüz Raporu
                st.divider()
                c1, c2 = st.columns(2)
                c1.metric("Toplam Kayıt", len(df_eski))
                c2.metric("Güncellenen Kişi Sayısı", degisim_sayisi)

                if rapor_listesi:
                    st.subheader("📋 Değişim Raporu Detayları")
                    st.table(pd.DataFrame(rapor_listesi))
                else:
                    st.info("Herhangi bir veri değişimi tespit edilmedi.")

                # İndirme İşlemi
                guncellenen_df.drop(columns=['match_key'], inplace=True)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    guncellenen_df.to_excel(writer, index=False)
                
                st.download_button("Güncel Excel'i İndir", output.getvalue(), "guncellenmis_personel_listesi.xlsx")
            else:
                st.error("Belirlediğiniz anahtar sütunlar dosyalarda bulunamadı.")
        except Exception as e:
            st.error(f"Hata: {e}")