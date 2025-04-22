import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("Prediksi Prestasi Belajar Siswa Berdasarkan Bullying (Tanpa Model)")

# === KONFIGURASI GOOGLE SHEETS ===
secrets = st.secrets["google_sheets"]
creds = Credentials.from_service_account_info(secrets, scopes=[
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)

SPREADSHEET_NAME = "Penilaian Prestasi Siswa Tanpa Model"
sheet = client.open(SPREADSHEET_NAME).sheet1

HEADER = ["No", "Nama", "Jenis Kelamin", "Umur", "Kelas", 
          "X1", "X2", "X3", "Y", "Verbal", "Fisik", "Sosial", "Cyber", 
          "Nilai Akhir", "Kategori", "Sumber"]
if sheet.row_values(1) != HEADER:
    sheet.clear()
    sheet.append_row(HEADER)

# === FUNGSI PENDUKUNG ===
def hitung_nilai_akhir(row):
    skor = [row['X1'], row['X2'], row['X3'], row['Y'], row['Verbal'], row['Fisik'], row['Sosial'], row['Cyber']]
    return sum(skor) / len(skor)

def kategorikan(nilai):
    if nilai < 2:
        return "Cukup"
    elif nilai < 3:
        return "Sedang"
    elif nilai < 4:
        return "Baik"
    else:
        return "Sangat Baik"

# === INPUT DATA ===
opsi = st.radio("Pilih Metode Input", ["Input Manual", "Upload File CSV"])

if opsi == "Input Manual":
    st.header("Input Identitas Siswa")
    nama = st.text_input("Nama")
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    umur = st.number_input("Umur", min_value=5, max_value=25)
    kelas = st.text_input("Kelas")

    st.header("Input Skor Rata-rata")
    x1 = st.slider("Skor X1 (Bullying yang Dialami)", 1.0, 5.0, step=0.1)
    x2 = st.slider("Skor X2 (Reaksi terhadap Bullying)", 1.0, 5.0, step=0.1)
    x3 = st.slider("Skor X3 (Dukungan Sosial)", 1.0, 5.0, step=0.1)
    y = st.slider("Skor Y (Motivasi/Kemauan Belajar)", 1.0, 5.0, step=0.1)

    st.header("Input Jenis Bullying (Skor Likert 1-5)")
    verbal = st.slider("Bullying Verbal", 1, 5)
    fisik = st.slider("Bullying Fisik", 1, 5)
    sosial = st.slider("Bullying Sosial", 1, 5)
    cyber = st.slider("Bullying Cyber", 1, 5)

    if st.button("Hitung Nilai Akhir"):
        data_input = {
            "X1": x1,
            "X2": x2,
            "X3": x3,
            "Y": y,
            "Verbal": verbal,
            "Fisik": fisik,
            "Sosial": sosial,
            "Cyber": cyber
        }
        nilai_akhir = hitung_nilai_akhir(data_input)
        kategori = kategorikan(nilai_akhir)

        st.success(f"Nilai Akhir Prestasi Belajar: {nilai_akhir:.2f}")
        st.info(f"Kategori: {kategori}")

        df_output = pd.DataFrame([{
            "Nama": nama,
            "Jenis Kelamin": jenis_kelamin,
            "Umur": umur,
            "Kelas": kelas,
            "X1": x1,
            "X2": x2,
            "X3": x3,
            "Y": y,
            "Verbal": verbal,
            "Fisik": fisik,
            "Sosial": sosial,
            "Cyber": cyber,
            "Nilai Akhir": round(nilai_akhir, 2),
            "Kategori": kategori
        }])
        st.subheader("Data Lengkap Siswa")
        st.dataframe(df_output)

        row = [
            len(sheet.get_all_values()), nama, jenis_kelamin, umur, kelas,
            x1, x2, x3, y, verbal, fisik, sosial, cyber,
            round(nilai_akhir, 2), kategori, "Manual"
        ]
        sheet.append_row(row)
        st.success("Data berhasil disimpan ke Google Sheets.")

else:
    st.header("Upload File CSV")
    st.write("Format kolom: nama, jenis_kelamin, umur, kelas, X1, X2, X3, Y, Verbal, Fisik, Sosial, Cyber")

    uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("Data Diupload")
            st.dataframe(df)

            df['Nilai Akhir'] = df.apply(hitung_nilai_akhir, axis=1)
            df['Kategori'] = df['Nilai Akhir'].apply(kategorikan)

            st.subheader("Hasil Perhitungan")
            st.dataframe(df[['nama', 'jenis_kelamin', 'umur', 'kelas', 'Nilai Akhir', 'Kategori']])

            for idx, row in df.iterrows():
                new_row = [
                    len(sheet.get_all_values()),
                    row['nama'], row['jenis_kelamin'], row['umur'], row['kelas'],
                    row['X1'], row['X2'], row['X3'], row['Y'],
                    row['Verbal'], row['Fisik'], row['Sosial'], row['Cyber'],
                    round(row['Nilai Akhir'], 2), row['Kategori'], "CSV"
                ]
                sheet.append_row(new_row)

            st.success("Semua data berhasil disimpan ke Google Sheets.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
