# Scraper Harga Pangan Malang

Scraper untuk mengambil data harga pangan strategis di Malang dari situs Bank Indonesia (BI.go.id).

## Deskripsi

Program ini mengambil data harga pangan strategis nasional sebagai referensi untuk harga di Malang, Jawa Timur. Data diambil dari situs resmi Bank Indonesia: https://www.bi.go.id/hargapangan

## Fitur

- ✅ Mengambil data harga 21 komoditas pangan strategis
- ✅ Data tersimpan dalam format CSV dan JSON
- ✅ Informasi lengkap: komoditas, harga, satuan, lokasi, tanggal, sumber
- ✅ Output yang mudah dibaca dengan statistik ringkasan
- ✅ **Aplikasi Web Streamlit untuk monitoring realtime**

## 🚀 Aplikasi Web Monitoring

### Fitur Aplikasi Streamlit:
- **📱 Interface Modern**: UI yang responsif dan mudah digunakan
- **🎛️ Side Menu**: Navigasi dengan radio button untuk memilih komoditas
- **📊 Visualisasi Data**: Chart tren harga 7 hari
- **💰 Metric Cards**: Tampilan harga dalam format yang menarik
- **📋 Tabel Lengkap**: Data semua komoditas dalam bentuk tabel
- **📈 Statistik**: Ringkasan harga rata-rata dan tertinggi

### Cara Menjalankan Aplikasi:

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Jalankan Aplikasi
```bash
# Cara 1: Menggunakan script
./run_app.sh

# Cara 2: Langsung dengan streamlit
streamlit run monitoring_pangan.py
```

#### 3. Akses Aplikasi
Buka browser dan akses: `http://localhost:8501`

### Fitur Aplikasi:
- **Judul**: MONITORING REALTIME HARGA KOMODITAS PANGAN DI MALANG
- **Side Menu**: Pilih komoditas dengan radio button
- **Dashboard**: Tampilan harga, chart tren, dan statistik
- **Pengembang**: M Nasri AW, @2025

## Komoditas yang Tersedia

1. Bawang Merah Ukuran Sedang
2. Bawang Putih Ukuran Sedang
3. Beras (berbagai kualitas)
4. Cabai Merah Besar & Keriting
5. Cabai Rawit Hijau & Merah
6. Daging Ayam Ras Segar
7. Daging Sapi Kualitas 1 & 2
8. Gula Pasir Premium & Lokal
9. Minyak Goreng Curah & Kemasan
10. Telur Ayam Ras Segar

## Cara Penggunaan Scraper

### 1. Persiapan
```bash
# Install dependencies jika diperlukan
pip install pandas
```

### 2. Jalankan Scraper
```bash
python scraper_ai.py
```

### 3. Output
Program akan menghasilkan:
- **harga_pangan_malang_YYYYMMDD.csv** - Data dalam format CSV
- **harga_pangan_malang_YYYYMMDD.json** - Data dalam format JSON

## Catatan Penting

- **Data Referensi**: Karena keterbatasan akses data kota spesifik, program menggunakan data harga nasional sebagai referensi untuk Malang.
- **Sumber Data**: Semua data berasal dari situs resmi Bank Indonesia (BI.go.id)
- **Tanggal Update**: Data berdasarkan informasi terakhir dari situs (per 14 Mei 2026)

## Struktur Data

Setiap record mengandung:
- `komoditas`: Nama komoditas pangan
- `harga`: Harga dalam Rupiah
- `satuan`: Satuan pengukuran (per kg)
- `lokasi`: Lokasi referensi data
- `tanggal`: Tanggal data
- `sumber`: Sumber data (BI.go.id)

## Contoh Output

```
=== SCRAPER HARGA PANGAN MALANG ===
Sumber: https://www.bi.go.id/hargapangan
Catatan: Menggunakan data nasional sebagai referensi karena data kota spesifik Malang mungkin tidak tersedia secara real-time
Data per 14 Mei 2026

Data berhasil di-scrape:
================================================================================
                      komoditas  harga satuan                      lokasi    tanggal   sumber
     Bawang Merah Ukuran Sedang  46800 per kg Nasional (referensi Malang) 2026-05-14 BI.go.id
     Bawang Putih Ukuran Sedang  39650 per kg Nasional (referensi Malang) 2026-05-14 BI.go.id
         Beras Kualitas Bawah I  14300 per kg Nasional (referensi Malang) 2026-05-14 BI.go.id
        ...
================================================================================

✅ Data disimpan ke: harga_pangan_malang_20260514.csv
✅ Data juga disimpan ke: harga_pangan_malang_20260514.json

📊 Total komoditas: 21
💰 Total nilai harga: Rp 861,450
```

## Teknologi yang Digunakan

- **Python 3.x**
- **Pandas** - Untuk manipulasi dan penyimpanan data
- **Streamlit** - Untuk aplikasi web interaktif
- **Plotly** - Untuk visualisasi data
- **JSON** - Untuk format data alternatif

## Lisensi

Data bersumber dari Bank Indonesia dan tunduk pada ketentuan penggunaan situs tersebut.

## Pengembang

Dibuat untuk keperluan analisis statistik harga pangan di Malang.
**M Nasri AW** - @2025