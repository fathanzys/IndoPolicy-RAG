"use client";

import { useEffect, useState } from "react";
import Header from "../../components/Header";
import styles from "./monitoring.module.css";
import { MessageSquare, ThumbsUp, ThumbsDown, Activity, Clock } from "lucide-react";

interface Stats {
    total_chats: number;
    positive_feedback: number;
    negative_feedback: number;
    satisfaction_rate: number;
    recent_feedback: Array<{
        rating: string;
        question: string;
        comment: string;
    }>;
}

export default function MonitoringPage() {
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";
                const res = await fetch(`${apiUrl}/stats`);
                if (res.ok) {
                    const data = await res.ok ? await res.json() : null;
                    setStats(data);
                }
            } catch (e) {
                console.error("Failed to fetch stats", e);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
        // Polling setiap 30 detik
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className={styles.container}>
            <Header
                title="SGO System Monitoring"
                subtitle="Live Analytics & Feedback Intelligence"
            />

            {loading ? (
                <div style={{ textAlign: 'center', padding: '100px', color: 'var(--text-secondary)' }}>
                    Memuat data statistik...
                </div>
            ) : (
                <>
                    <div className={styles.grid}>
                        <div className={styles.card}>
                            <div className={styles.cardTitle}>
                                <MessageSquare size={16} /> Total Interact
                            </div>
                            <div className={styles.cardValue}>{stats?.total_chats || 0}</div>
                            <div className={styles.cardSub}>Pertanyaan yang diajukan user</div>
                        </div>

                        <div className={styles.card}>
                            <div className={styles.cardTitle}>
                                <Activity size={16} /> Satisfaction
                            </div>
                            <div className={`${styles.cardValue} ${styles.cardValueGreen}`}>{stats?.satisfaction_rate || 0}%</div>
                            <div className={styles.cardSub}>Rata-rata rating positif</div>
                        </div>

                        <div className={styles.card}>
                            <div className={styles.cardTitle}>
                                <ThumbsUp size={16} /> Positive
                            </div>
                            <div className={styles.cardValue}>{stats?.positive_feedback || 0}</div>
                            <div className={styles.cardSub}>Respon bermanfaat</div>
                        </div>

                        <div className={styles.card}>
                            <div className={styles.cardTitle}>
                                <ThumbsDown size={16} /> Negative
                            </div>
                            <div className={styles.cardValue}>{stats?.negative_feedback || 0}</div>
                            <div className={styles.cardSub}>Respon butuh perbaikan</div>
                        </div>
                    </div>

                    <div className={styles.historySection}>
                        <div className={styles.sectionHeader}>
                            <h3 className={styles.sectionTitle}>
                                <Clock size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
                                Recent Feedback
                            </h3>
                        </div>

                        <div className={styles.tableContainer}>
                            <table className={styles.table}>
                                <thead>
                                    <tr>
                                        <th>RATING</th>
                                        <th>PERTANYAAN</th>
                                        <th>KOMENTAR / CATATAN</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {stats?.recent_feedback && stats.recent_feedback.length > 0 ? (
                                        stats.recent_feedback.map((item, i) => (
                                            <tr key={i}>
                                                <td>
                                                    <span className={`${styles.badge} ${item.rating === 'UP' ? styles.badgeUp : styles.badgeDown}`}>
                                                        {item.rating === 'UP' ? 'BERMANFAAT' : 'KURANG'}
                                                    </span>
                                                </td>
                                                <td>{item.question}</td>
                                                <td>{item.comment || "-"}</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan={3} style={{ textAlign: 'center', padding: '40px' }}>
                                                Belum ada data feedback terbaru.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
