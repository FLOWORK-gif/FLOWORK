# Pemicu Proses Aplikasi

> Pemicu unik yang mengawasi aplikasi lain yang berjalan di komputer Anda. Anda bisa membuat otomasi yang bereaksi terhadap kapan sebuah program, game, atau service lain dibuka atau ditutup.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `process_trigger` |
| Tier | Free |
| Version | 1.0 |
| Author | Awenk Audico |

## How to Use
**Konsep:**
Secara berkala, trigger ini akan memeriksa daftar proses yang sedang berjalan di sistem operasi Anda. Jika nama proses yang Anda tentukan muncul (dimulai) atau menghilang (berhenti), ia akan memicu preset.

**Cara Penggunaan:**
1. Buat Aturan baru.
2. Masukkan nama proses aplikasi, termasuk ekstensinya (misal: `notepad.exe`, `chrome.exe`, `Spotify.exe`). Anda bisa melihat nama proses di Task Manager (Windows) atau Activity Monitor (Mac).
3. Pilih apakah akan memicu saat proses 'Dimulai' atau 'Berhenti'.
4. Pilih Preset yang akan dijalankan.

**Contoh Optimasi:**
- **Gaming Mode:** Saat `valorant.exe` dimulai, picu workflow untuk mematikan notifikasi, membuka Discord, dan meredupkan lampu kamar.
- **Productivity Mode:** Saat `Photoshop.exe` dimulai, jalankan preset yang membuka folder proyek terakhir dan memutar playlist fokus di Spotify.

## API Reference

::: triggers.process_trigger.listener
