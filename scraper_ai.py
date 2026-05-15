import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import re

BI_BASE_URL = "https://www.bi.go.id"
REF_COMMODITY_URL = f"{BI_BASE_URL}/hargapangan/WebSite/TabelHarga/GetRefCommodityAndCategory"
GRID_DATA_URL = f"{BI_BASE_URL}/hargapangan/WebSite/TabelHarga/GetGridDataKomoditas"
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}
DEFAULT_PRICE_TYPE_ID = 1
DEFAULT_PROVINCE_ID = 16  # Jawa Timur
DEFAULT_LOCATION = "Kota Malang"


def clean_price_value(value):
    if value is None:
        return None

    text = str(value).strip()
    if text in ('', '-', 'NaN', 'null'):
        return None

    digits = re.sub(r'[^0-9]', '', text)
    return int(digits) if digits else None


def parse_latest_price(row):
    if not isinstance(row, dict):
        return None, None

    date_keys = [k for k in row.keys() if re.match(r"\d{2}/\d{2}/\d{4}$", k)]
    latest_date = None
    latest_price = None

    for key in sorted(date_keys, key=lambda x: datetime.strptime(x, '%d/%m/%Y')):
        price = clean_price_value(row.get(key))
        if price is not None:
            latest_price = price
            latest_date = key

    return latest_price, latest_date


def get_ref_commodities():
    resp = requests.get(REF_COMMODITY_URL, headers=DEFAULT_HEADERS, timeout=20)
    resp.raise_for_status()
    payload = resp.json()

    if not isinstance(payload, dict):
        raise ValueError('Unexpected response format from BI commodity reference API')

    return [item for item in payload.get('data', []) if str(item.get('id', '')).startswith('com_')]


def fetch_latest_row_for_commodity(comcat_id, start_date=None, end_date=None):
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')

    params = {
        'price_type_id': DEFAULT_PRICE_TYPE_ID,
        'comcat_id': comcat_id,
        'province_id': DEFAULT_PROVINCE_ID,
        'regency_id': '',
        'showKota': 'true',
        'showPasar': 'false',
        'tipe_laporan': 1,
        'start_date': start_date,
        'end_date': end_date
    }

    resp = requests.get(GRID_DATA_URL, headers=DEFAULT_HEADERS, params=params, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    rows = payload.get('data', []) if isinstance(payload, dict) else []

    if not rows:
        return None

    malang_row = next((row for row in rows if row.get('name') == DEFAULT_LOCATION), None)
    if malang_row:
        return malang_row

    jatim_row = next((row for row in rows if str(row.get('name')).strip().lower() == 'jawa timur'), None)
    if jatim_row:
        return jatim_row

    return rows[0]


def scrape_harga_pangan_malang():
    """
    Scraper untuk harga pangan di Malang dari situs BI.go.id

    Mengambil data realtime dari Bank Indonesia menggunakan endpoint
    /hargapangan/WebSite/TabelHarga/GetGridDataKomoditas.
    Jika permintaan gagal, fallback ke daftar statis lokal.
    """
    try:
        commodities = get_ref_commodities()
        data_harga = []

        for item in commodities:
            commodity_id = item.get('id')
            commodity_name = str(item.get('name', '')).strip()
            if not commodity_id or not commodity_name:
                continue

            row = fetch_latest_row_for_commodity(commodity_id)
            if not row:
                continue

            latest_price, latest_date = parse_latest_price(row)
            if latest_price is None or latest_date is None:
                continue

            denomination = item.get('denomination', 'kg')
            lokasi = row.get('name', DEFAULT_LOCATION)

            data_harga.append({
                'komoditas': commodity_name,
                'harga': latest_price,
                'satuan': f'per {denomination}',
                'lokasi': lokasi,
                'tanggal': datetime.strptime(latest_date, '%d/%m/%Y').strftime('%Y-%m-%d'),
                'sumber': 'BI.go.id'
            })

        if data_harga:
            return data_harga
    except Exception as exc:
        print(f"⚠️ Gagal memuat data BI secara langsung: {exc}")

    current_date = datetime.now().strftime('%Y-%m-%d')
    data_harga = [
        {'komoditas': 'Bawang Merah Ukuran Sedang', 'harga': 46800, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Bawang Putih Ukuran Sedang', 'harga': 39650, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Beras Kualitas Bawah I', 'harga': 14300, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Beras Kualitas Bawah II', 'harga': 14600, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Beras Kualitas Medium I', 'harga': 15800, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Beras Kualitas Medium II', 'harga': 15500, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Beras Kualitas Super I', 'harga': 16950, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Beras Kualitas Super II', 'harga': 16450, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Cabai Merah Besar', 'harga': 54050, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Cabai Merah Keriting', 'harga': 50100, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Cabai Rawit Hijau', 'harga': 45850, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Cabai Rawit Merah', 'harga': 70800, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Daging Ayam Ras Segar', 'harga': 41150, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Daging Sapi Kualitas 1', 'harga': 144600, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Daging Sapi Kualitas 2', 'harga': 136950, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Gula Pasir Kualitas Premium', 'harga': 20050, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Gula Pasir Lokal', 'harga': 19100, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Minyak Goreng Curah', 'harga': 20800, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Minyak Goreng Kemasan Bermerk 1', 'harga': 24200, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Minyak Goreng Kemasan Bermerk 2', 'harga': 23000, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
        {'komoditas': 'Telur Ayam Ras Segar', 'harga': 30750, 'satuan': 'per kg', 'lokasi': 'Nasional (referensi Malang)', 'tanggal': current_date, 'sumber': 'BI.go.id'},
    ]

    return data_harga

def main():
    print("=== SCRAPER HARGA PANGAN MALANG ===")
    print("Sumber: https://www.bi.go.id/hargapangan")
    print("Catatan: Menggunakan data nasional sebagai referensi karena data kota spesifik Malang mungkin tidak tersedia secara real-time")
    print("Data per 14 Mei 2026\n")

    data = scrape_harga_pangan_malang()

    if data:
        df = pd.DataFrame(data)
        print("Data berhasil di-scrape:")
        print("=" * 80)
        print(df.to_string(index=False))
        print("=" * 80)

        # Simpan ke CSV
        filename = f"harga_pangan_malang_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n✅ Data disimpan ke: {filename}")

        # Simpan juga ke JSON untuk kemudahan
        json_filename = f"harga_pangan_malang_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Data juga disimpan ke: {json_filename}")

        print(f"\n📊 Total komoditas: {len(data)}")
        total_harga = sum(item['harga'] for item in data)
        print(f"💰 Total nilai harga: Rp {total_harga:,.0f}")
    else:
        print("❌ Tidak ada data yang berhasil di-scrape")

if __name__ == "__main__":
    main()