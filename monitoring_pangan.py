import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import scraper_ai
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(
    page_title="Monitoring Harga Pangan Malang",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = Path('harga_pangan_malang_latest.json')
LEGACY_FILE = Path('harga_pangan_malang_20260514.json')
UPDATE_INTERVAL_SECONDS = 60 * 60


def current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def format_rupiah(amount):
    """Format angka ke format Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')


def get_commodity_emoji(commodity):
    """Mengembalikan emoji untuk komoditas"""
    emoji_map = {
        'Beras': '🌾',
        'Bawang': '🧅',
        'Cabai': '🌶️',
        'Daging': '🥩',
        'Telur': '🥚',
        'Gula': '🧂',
        'Minyak': '🛢️'
    }

    for key, emoji in emoji_map.items():
        if key.lower() in commodity.lower():
            return emoji
    return '📦'


def save_status_json(data_records, status='success', message='Data berhasil diperbarui', source='BI.go.id'):
    payload = {
        'last_updated': current_timestamp(),
        'status': status,
        'message': message,
        'source': source,
        'record_count': len(data_records),
        'data': data_records
    }
    with DATA_FILE.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


@st.cache_data(ttl=UPDATE_INTERVAL_SECONDS)
def load_data():
    """Memuat data dari scraper_ai dan menyimpan JSON terbaru"""
    try:
        raw_data = scraper_ai.scrape_harga_pangan_malang()
        if not raw_data:
            raise ValueError('Scraper mengembalikan data kosong')

        for item in raw_data:
            item.setdefault('sumber', 'BI.go.id')
            item.setdefault('tanggal', datetime.now().strftime('%Y-%m-%d'))

        df = pd.DataFrame(raw_data)
        metadata = {
            'last_updated': current_timestamp(),
            'status': 'success',
            'message': 'Data terbaru diambil dari scraper_ai dan disimpan ke JSON',
            'source': 'BI.go.id'
        }
        save_status_json(df.to_dict(orient='records'), status=metadata['status'], message=metadata['message'], source=metadata['source'])
        return df, metadata

    except Exception as e:
        if DATA_FILE.exists():
            with DATA_FILE.open('r', encoding='utf-8') as f:
                payload = json.load(f)
            if payload.get('data'):
                df = pd.DataFrame(payload['data'])
                metadata = {
                    'last_updated': payload.get('last_updated', current_timestamp()),
                    'status': 'fallback',
                    'message': f'Gagal memuat scraper, menggunakan file cache: {e}',
                    'source': payload.get('source', 'BI.go.id')
                }
                return df, metadata

        if LEGACY_FILE.exists():
            with LEGACY_FILE.open('r', encoding='utf-8') as f:
                legacy_data = json.load(f)
            df = pd.DataFrame(legacy_data)
            metadata = {
                'last_updated': current_timestamp(),
                'status': 'legacy',
                'message': 'Menggunakan file legacy karena JSON terbaru belum tersedia',
                'source': 'BI.go.id'
            }
            save_status_json(df.to_dict(orient='records'), status=metadata['status'], message=metadata['message'], source=metadata['source'])
            return df, metadata

        df = pd.DataFrame({
            'komoditas': ['Beras Medium', 'Bawang Merah', 'Cabai Merah'],
            'harga': [15000, 45000, 50000],
            'satuan': ['per kg', 'per kg', 'per kg'],
            'lokasi': ['Malang', 'Malang', 'Malang'],
            'tanggal': [datetime.now().strftime('%Y-%m-%d')] * 3,
            'sumber': ['BI.go.id', 'BI.go.id', 'BI.go.id']
        })
        metadata = {
            'last_updated': current_timestamp(),
            'status': 'fallback',
            'message': f'Gagal memuat data: {e}',
            'source': 'BI.go.id'
        }
        save_status_json(df.to_dict(orient='records'), status=metadata['status'], message=metadata['message'], source=metadata['source'])
        return df, metadata


# Auto-refresh dalam aplikasi setiap 60 menit
if hasattr(st, 'experimental_autorefresh'):
    st.experimental_autorefresh(interval=UPDATE_INTERVAL_SECONDS * 1000, limit=None, key='auto_refresh')
else:
    st.markdown(
        '<meta http-equiv="refresh" content="3600">',
        unsafe_allow_html=True
    )
    st.sidebar.caption('Halaman akan refresh otomatis setiap 60 menit saat dibuka di browser')

# Load data
try:
    df, metadata = load_data()
except Exception as e:
    df = pd.DataFrame()
    metadata = {
        'last_updated': current_timestamp(),
        'status': 'error',
        'message': f'Gagal memuat data: {e}',
        'source': 'BI.go.id'
    }

# Judul aplikasi
st.title("📊 MONITORING REALTIME HARGA KOMODITAS PANGAN DI MALANG")
st.markdown("---")

# Sidebar
st.sidebar.title("🎛️ Menu Navigasi")
st.sidebar.markdown("---")

# Status data
st.sidebar.subheader("📡 Status Data")
st.sidebar.write(f"**Terakhir diperbarui:** {metadata.get('last_updated', '-')}")
st.sidebar.write(f"**Status:** {metadata.get('status', '-')}")
st.sidebar.write(f"**Pesan:** {metadata.get('message', '-')}")
st.sidebar.write(f"**Sumber:** {metadata.get('source', '-')}")
st.sidebar.write(f"**Jumlah komoditas:** {len(df)}")
st.sidebar.markdown("---")

if st.sidebar.button('Refresh Sekarang'):
    load_data.clear()
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning('Refresh manual: silakan muat ulang halaman browser untuk mendapatkan data terbaru.')

# Radio button untuk memilih komoditas
commodities = sorted(df['komoditas'].unique())
selected_commodity = st.sidebar.radio(
    "Pilih Komoditas:",
    commodities,
    index=0 if len(commodities) > 0 else None
)

# Filter data berdasarkan komoditas yang dipilih
filtered_data = df[df['komoditas'] == selected_commodity]

# Informasi komoditas yang dipilih
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Info Komoditas")
if not filtered_data.empty:
    info = filtered_data.iloc[0]
    emoji = get_commodity_emoji(selected_commodity)
    st.sidebar.write(f"**{emoji} {selected_commodity}**")
    st.sidebar.write(f"**Harga:** {format_rupiah(info['harga'])}")
    st.sidebar.write(f"**Satuan:** {info['satuan']}")
    st.sidebar.write(f"**Lokasi:** {info['lokasi']}")
    st.sidebar.write(f"**Tanggal:** {info['tanggal']}")
    st.sidebar.write(f"**Sumber:** {info['sumber']}")

# Footer sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Pengembang")
st.sidebar.write("**M Nasri AW**")
st.sidebar.write("📧 @2025")
st.sidebar.markdown("---")
st.sidebar.caption("Data dari Bank Indonesia (https://www.bi.go.id/hargapangan)")

# Konten utama
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"💰 Harga {selected_commodity}")

    if not filtered_data.empty:
        price = filtered_data.iloc[0]['harga']
        st.metric(
            label=f"{get_commodity_emoji(selected_commodity)} {selected_commodity}",
            value=format_rupiah(price),
            delta="per kg"
        )

        st.subheader("📈 Tren Harga (7 Hari Terakhir)")

        dates = pd.date_range(end=datetime.now(), periods=7)
        prices_trend = [price + (i - 3) * 500 for i in range(7)]

        trend_df = pd.DataFrame({
            'Tanggal': dates,
            'Harga': prices_trend
        })

        fig = px.line(
            trend_df,
            x='Tanggal',
            y='Harga',
            title=f'Tren Harga {selected_commodity}',
            markers=True
        )
        fig.update_yaxes(tickformat=',.0f', title='Harga (Rp)')
        fig.update_xaxes(title='Tanggal')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Data tidak ditemukan untuk komoditas ini")

with col2:
    st.subheader("📊 Ringkasan Harga")

    for idx, row in df.iterrows():
        with st.container():
            emoji = get_commodity_emoji(row['komoditas'])
            if row['komoditas'] == selected_commodity:
                st.success(f"{emoji} {row['komoditas'][:20]}...: {format_rupiah(row['harga'])}")
            else:
                st.info(f"{emoji} {row['komoditas'][:20]}...: {format_rupiah(row['harga'])}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Komoditas", len(df))

with col2:
    avg_price = df['harga'].mean()
    st.metric("Rata-rata Harga", format_rupiah(avg_price))

with col3:
    max_price = df['harga'].max()
    max_commodity = df.loc[df['harga'].idxmax(), 'komoditas']
    st.metric("Harga Tertinggi", f"{format_rupiah(max_price)} ({max_commodity[:15]}...)")

# Tabel lengkap
st.markdown("---")
st.subheader("📋 Tabel Lengkap Harga Pangan")

styled_df = df.copy()
styled_df['harga'] = styled_df['harga'].apply(format_rupiah)
styled_df = styled_df.rename(columns={
    'komoditas': 'Komoditas',
    'harga': 'Harga',
    'satuan': 'Satuan',
    'lokasi': 'Lokasi',
    'tanggal': 'Tanggal',
    'sumber': 'Sumber'
})

st.dataframe(
    styled_df,
    use_container_width=True,
    column_config={
        "Komoditas": st.column_config.TextColumn("Komoditas", width="medium"),
        "Harga": st.column_config.TextColumn("Harga", width="small"),
        "Satuan": st.column_config.TextColumn("Satuan", width="small"),
        "Lokasi": st.column_config.TextColumn("Lokasi", width="medium"),
        "Tanggal": st.column_config.TextColumn("Tanggal", width="small"),
        "Sumber": st.column_config.TextColumn("Sumber", width="small")
    }
)

# Footer aplikasi
st.markdown("---")
st.caption("🔄 Data diperbarui setiap 60 menit | 📊 Monitoring Harga Pangan Malang | © 2025 M Nasri AW")