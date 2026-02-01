import pyodbc
from telegram import Update
from telegram.ext import ContextTypes
from db_conn import DB_CONN_STR

conn = pyodbc.connect(DB_CONN_STR)
cursor = conn.cursor()

# /status → semua device
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("""
        SELECT device_id, temp_c, ts_utc
        FROM (
            SELECT
                device_id,
                temp_c,
                ts_utc,
                ROW_NUMBER() OVER (
                    PARTITION BY device_id
                    ORDER BY ts_utc DESC
                ) AS rn
            FROM dbo.telemetry_temp
        ) t
        WHERE rn = 1
        ORDER BY device_id
    """)
    
    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("Belum ada data suhu.")
        return

    msg = "📊 STATUS SUHU TERKINI\n\n"
    for r in rows:
        msg += f"{r.device_id}: {r.temp_c} °C\n"

    await update.message.reply_text(msg)

# /device cek khusus text command
async def device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /device DEVICE_ID")
        return

    device_id = context.args[0]

    cursor.execute("""
        SELECT TOP 1 temp_c, ts_utc
        FROM dbo.telemetry_temp
        WHERE device_id = ?
        ORDER BY ts_utc DESC
    """, device_id)

    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("Device tidak ditemukan.")
        return

    await update.message.reply_text(
        f"📡 {device_id}\n🌡 {row.temp_c} °C\n⏱ {row.ts_utc}"
    )
