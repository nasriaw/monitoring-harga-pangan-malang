#!/bin/bash
# Script untuk menjalankan aplikasi monitoring harga pangan

echo "🚀 Menjalankan Monitoring Harga Pangan Malang..."
echo "📊 Aplikasi Streamlit untuk monitoring realtime harga komoditas pangan"
echo ""

# Cek apakah streamlit terinstall
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit tidak terinstall. Install dengan:"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Jalankan aplikasi
streamlit run monitoring_pangan.py --server.port 8501 --server.address 0.0.0.0