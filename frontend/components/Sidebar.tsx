"use client";

import Image from "next/image";
import { MessageSquarePlus, Download, ShieldCheck } from "lucide-react";
import styles from "./Sidebar.module.css";

export default function Sidebar() {

    const handleNewChat = () => {
        if (confirm("Apakah Anda yakin ingin memulai percakapan baru? Riwayat saat ini akan dihapus.")) {
            localStorage.removeItem("sgo_chat_history");
            window.location.reload();
        }
    };

    const handleExportChat = () => {
        const saved = localStorage.getItem("sgo_chat_history");
        if (!saved) {
            alert("Belum ada riwayat percakapan untuk diekspor.");
            return;
        }

        try {
            const messages = JSON.parse(saved);
            let textOutput = "=== SGO Asisten Riwayat Percakapan ===\n\n";
            messages.forEach((msg: any) => {
                const role = msg.role === "user" ? "Anda" : "SGO Asisten";
                textOutput += `[${role}]:\n${msg.content}\n\n`;
            });

            const blob = new Blob([textOutput], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `SGO_Chat_History_${new Date().toISOString().slice(0, 10)}.txt`;
            link.click();
            URL.revokeObjectURL(url);
        } catch (e) {
            alert("Gagal mengekspor percakapan.");
        }
    };

    return (
        <aside className={styles.sidebar}>
            <div className={styles.brand}>
                <div className={styles.logoBox}>
                    <Image
                        src="/Logo-BI.png"
                        alt="Bank Indonesia"
                        width={180}
                        height={55}
                        style={{ objectFit: "contain", width: "auto", height: "auto", maxHeight: "45px" }}
                        priority
                    />
                </div>
                <div className={styles.brandText}>
                    <h1>Self Governance</h1>
                    <p>Observation Service</p>
                </div>
            </div>

            <nav className={styles.menu}>
                <div className={styles.menuItem} onClick={handleNewChat}>
                    <MessageSquarePlus size={20} />
                    <span>Percakapan Baru</span>
                </div>
                <div className={styles.menuItem} onClick={handleExportChat}>
                    <Download size={20} />
                    <span>Ekspor ke TXT</span>
                </div>
            </nav>

            <div className={styles.menuItem} style={{ marginTop: 'auto', opacity: 0.5, fontSize: '0.8rem', cursor: 'default' }}>
                <ShieldCheck size={16} />
                <span>v2.1.0 Enterprise Edition</span>
            </div>
        </aside>
    );
}
