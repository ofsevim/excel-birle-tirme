import streamlit as st
import pandas as pd
import io

# Sayfa Ayarları
st.set_page_config(page_title="Personel Güncelleyici", layout="wide")

st.title("🚀 Personel Veri Güncelleme Aracı (Sicil Odaklı)")
st.markdown("""
Bu araç, **Sicil** numarası üzerinden eşleştirme yapar. 
Eski listedeki personelin **Görev Yeri** ve **Unvan** bilgilerini yeni listedeki verilerle günceller.
""")

# Dosya Yükleme
col1, col2 = st.columns(2)
with col1:
    eski_file = st.file_uploader("1. Eski (Ana) Excel'i Yükle", type=["xlsx"])
with col2:
    yeni_file = st.file_uploader("2. Yeni Verili Excel'i Yükle", type=["xlsx"])

# Eşleşecek sütunlar (Sicil'i en başa aldık)
keys_input = st.text_input("Eşleşecek Sütunlar (Virgülle ayırın)", value="Sicil, Personel")

if st.button("Verileri Eşleştir ve Güncelle", type="primary"):
    if eski_file and yeni_file:
        try:
            # Excel dosyalarını oku
            df_eski = pd.read_excel(eski_file)
            df_yeni = pd.read_excel(yeni_file)

            # Sütun isimlerindeki boşlukları temizle
            df_eski.columns = [str(c).strip() for c in df_eski.columns]
            df_yeni.columns = [str(c).strip() for c in df_yeni.columns]
            
            anahtar_sutunlar = [s.strip() for s in keys_input.split(",")]

            # Sütun kontrolü
            missing = [c for c in anahtar_sutunlar if c not in df_eski.columns or c not in df_yeni.columns]
            
            if missing:
                st.error(f"Şu sütunlar dosyalarda bulunamadı: {missing}")
                st.info(f"Eski Dosya Sütunları: {list(df_eski.columns)}")
                st.info(f"Yeni Dosya Sütunları: {list(df_yeni.columns)}")
            else:
                # Geçici temiz tablolar oluştur
                df_eski_temp = df_eski.copy()
                df_yeni_temp = df_yeni.copy()
                
                match_cols = []
                for col in anahtar_sutunlar:
                    m_col = f"{col}_match"
                    # Sayısal verileri (Sicil gibi) metne çevir, küçük harf yap ve temizle
                    df_eski_temp[m_col] = df_eski_temp[col].astype(str).str.lower().str.strip()
                    df_yeni_temp[m_col] = df_yeni_temp[col].astype(str).str.lower().str.strip()
                    match_cols.append(m_col)

                # ÇOK ÖNEMLİ: Mükerrer (aynı sicile sahip birden fazla satır) kayıtları temizle
                # Bu adım "non-unique multi-index" hatasını engeller.
                df_eski_temp = df_eski_temp.drop_duplicates(subset=match_cols)
                df_yeni_temp = df_yeni_temp.drop_duplicates(subset=match_cols)

                # Index set et
                df_eski_temp.set_index(match_cols, inplace=True)
                df_yeni_temp.set_index(match_cols, inplace=True)

                # GÜNCELLEME İŞLEMİ
                # Eski listedeki verileri, yeni listedeki karşılıklarıyla değiştirir.
                df_eski_temp.update(df_yeni_temp)

                # Sonucu orijinal haline döndür (geçici kolonları at)
                sonuc = df_eski_temp.reset_index(drop=True)

                # Excel İndirme Hazırlığı
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    sonuc.to_excel(writer, index=False)
                
                st.success(f"İşlem tamam! {len(sonuc)} personel kontrol edildi ve güncellendi.")
                
                st.download_button(
                    label="Güncellenmiş Excel'i İndir",
                    data=output.getvalue(),
                    file_name="guncellenmiş_personel_listesi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Beklenmedik bir hata oluştu: {e}")
    else:
        st.warning("Lütfen her iki Excel dosyasını da yükleyin.")