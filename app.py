import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Görev Yeri Güncelleyici", layout="wide")
st.title("⚖️ Adalet Bakanlığı Personel Güncelleme")

st.markdown("""
**Mantık:** Sistem her iki dosyada da 'Sicil' sütununu arar. 
Sicil numarası eşleşen personelin **Görev Yeri** bilgisini yenisiyle değiştirir.
""")

c1, c2 = st.columns(2)
with c1:
    eski_file = st.file_uploader("1. Eski (Ana) Excel'i Yükle", type=["xlsx"])
with c2:
    yeni_file = st.file_uploader("2. Yeni Verili Excel'i Yükle", type=["xlsx"])

# Eşleştirme için tek ve sağlam anahtar
anahtar_sutun = "Sicil"

if st.button("Güncellemeyi Uygula ve Raporla", type="primary"):
    if eski_file and yeni_file:
        try:
            df_eski = pd.read_excel(eski_file)
            df_yeni = pd.read_excel(yeni_file)

            # Sütun isimlerini temizle (Başındaki sonundaki boşlukları siler)
            df_eski.columns = [str(c).strip() for c in df_eski.columns]
            df_yeni.columns = [str(c).strip() for c in df_yeni.columns]

            if anahtar_sutun in df_eski.columns and anahtar_sutun in df_yeni.columns:
                # Sicil sütunlarını temizle ve metne çevir (Eşleşmeyi garantilemek için)
                df_eski[anahtar_sutun] = df_eski[anahtar_sutun].astype(str).str.strip()
                df_yeni[anahtar_sutun] = df_yeni[anahtar_sutun].astype(str).str.strip()

                # Değişim takibi için eski hali sakla
                df_final = df_eski.copy()
                rapor_verisi = []

                # Güncelleme döngüsü
                for index, yeni_row in df_yeni.iterrows():
                    sicil = yeni_row[anahtar_sutun]
                    
                    # Eğer bu sicil eski dosyada varsa
                    if sicil in df_final[anahtar_sutun].values:
                        # Yeni görev yerini al
                        yeni_gorev = yeni_row['Görev Yeri']
                        eski_gorev = df_final.loc[df_final[anahtar_sutun] == sicil, 'Görev Yeri'].values[0]

                        # Eğer görev yeri gerçekten değişmişse
                        if str(eski_gorev).strip() != str(yeni_gorev).strip():
                            rapor_verisi.append({
                                "Sicil": sicil,
                                "Personel": df_final.loc[df_final[anahtar_sutun] == sicil, 'Personel'].values[0],
                                "Eski Yer": eski_gorev,
                                "Yeni Yer": yeni_gorev
                            })
                            # Güncelleme yap
                            df_final.loc[df_final[anahtar_sutun] == sicil, 'Görev Yeri'] = yeni_gorev

                if rapor_verisi:
                    st.success(f"✅ {len(rapor_verisi)} personelin görev yeri güncellendi!")
                    st.subheader("📋 Değişim Listesi")
                    st.table(pd.DataFrame(rapor_verisi))
                    
                    # Dosyayı indir
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_final.to_excel(writer, index=False)
                    st.download_button("Güncel Excel'i İndir", output.getvalue(), "guncellenmis_personel_listesi.xlsx")
                else:
                    st.warning("Eşleşen sicil bulundu ancak görev yeri değişikliği tespit edilemedi.")
            else:
                st.error(f"Her iki dosyada da '{anahtar_sutun}' sütunu bulunmalıdır.")
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")