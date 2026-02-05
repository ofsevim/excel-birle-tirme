import streamlit as st
import pandas as pd
import io

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Excel Güncelleyici", layout="centered")

st.title("Excel Veri Güncelleme Aracı")
st.markdown("""
Bu araç, **Eski Liste** üzerindeki kayıtları, **Yeni Liste**'deki güncel bilgilerle (Görev Yeri, Ünvan vb.) yeniler.
* Büyük/Küçük harf duyarlılığı yoktur.
* Yeni kayıt eklemez, sadece mevcutları günceller.
""")

st.divider()

# Dosya Yükleme Alanları
col1, col2 = st.columns(2)

with col1:
    eski_file = st.file_uploader("1. Eski (Ana) Excel'i Yükle", type=["xlsx", "xls"])

with col2:
    yeni_file = st.file_uploader("2. Yeni Verili Excel'i Yükle", type=["xlsx", "xls"])

# Anahtar Sütun Girişi
keys_input = st.text_input("Eşleşecek Sütunlar (Virgülle ayırın)", placeholder="Örn: TC No, Ad, Soyad")

if st.button("Verileri Eşleştir ve Güncelle", type="primary"):
    if eski_file and yeni_file and keys_input:
        try:
            # Excel'leri oku
            df_eski = pd.read_excel(eski_file)
            df_yeni = pd.read_excel(yeni_file)

            # Sütunları temizle
            anahtar_sutunlar = [s.strip() for s in keys_input.split(",")]

            # Sütun varlık kontrolü
            missing_cols = [c for c in anahtar_sutunlar if c not in df_eski.columns or c not in df_yeni.columns]
            
            if missing_cols:
                st.error(f"Şu sütunlar dosyalarda bulunamadı: {', '.join(missing_cols)}")
            else:
                # Eşleşme için geçici küçük harf kolonları oluştur
                df_eski_temp = df_eski.copy()
                df_yeni_temp = df_yeni.copy()
                
                match_cols = []
                for col in anahtar_sutunlar:
                    m_col = f"{col}_match"
                    df_eski_temp[m_col] = df_eski_temp[col].astype(str).str.lower().str.strip()
                    df_yeni_temp[m_col] = df_yeni_temp[col].astype(str).str.lower().str.strip()
                    match_cols.append(m_col)

                # Indexleme ve Güncelleme
                df_eski_temp.set_index(match_cols, inplace=True)
                df_yeni_temp.set_index(match_cols, inplace=True)

                # Sadece eski listede olanları güncelle
                df_eski_temp.update(df_yeni_temp)

                # Sonucu hazırla
                sonuc = df_eski_temp.reset_index(drop=True)

                # Excel dosyasını belleğe (memory) yaz (İndirme için)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    sonuc.to_excel(writer, index=False)
                
                st.success("İşlem başarıyla tamamlandı!")
                
                st.download_button(
                    label="Güncellenmiş Excel'i İndir",
                    data=output.getvalue(),
                    file_name="guncellenmis_liste.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
    else:
        st.warning("Lütfen her iki dosyayı da yükleyin ve anahtar sütunları girin.")