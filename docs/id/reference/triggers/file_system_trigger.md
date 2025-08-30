# Pemicu Perubahan File

> Mengawasi sebuah folder dan bereaksi secara otomatis terhadap aktivitas file. Trigger ini adalah mata dan telinga sistem Anda di dalam file explorer, siap bertindak saat ada file baru, perubahan, atau penghapusan.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `file_system_trigger` |
| Tier | Free |
| Version | 1.0 |
| Author | Awenk Audico |

## How to Use
**Konsep:**
Trigger ini menggunakan 'watchdog' untuk memantau sebuah direktori. Saat aktivitas yang Anda tentukan terjadi (misal: file baru muncul), ia akan langsung memicu preset.

**Cara Penggunaan:**
1. Drag & drop trigger ini ke kanan.
2. Klik 'Browse...' untuk memilih folder yang ingin Anda awasi.
3. Centang jenis kejadian yang relevan: 'Saat Dibuat', 'Saat Diubah', atau 'Saat Dihapus'. Anda bisa memilih lebih dari satu.
4. Tentukan Preset yang akan dieksekusi.

**Contoh Optimasi:**
- **ETL Otomatis:** Pantau folder 'uploads'. Setiap kali ada file CSV baru masuk, otomatis jalankan workflow untuk membaca, memproses, dan memasukkan datanya ke database.
- **Konversi Gambar:** Awasi folder 'gambar_mentah'. Setiap ada file .PNG baru, picu workflow untuk mengkonversinya menjadi .JPG dan memindahkannya ke folder lain.

## API Reference

::: triggers.file_system_trigger.listener
