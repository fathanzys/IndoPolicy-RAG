"use client";
import { useState, useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { Landmark, ShieldAlert } from "lucide-react";
import styles from "./ChatBox.module.css";

type Message = { role: "user" | "assistant"; content: string; };

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load history from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("sgo_chat_history");
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse history", e);
      }
    }
  }, []);

  // Save history and scroll to bottom
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("sgo_chat_history", JSON.stringify(messages));
    }
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (text: string) => {
    const newUserMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, newUserMsg]);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";
      const res = await fetch(`${apiUrl}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // Pass the previous messages as chat history
        body: JSON.stringify({ question: text, chat_history: messages }),
      });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      const newAiMsg: Message = { role: "assistant", content: data.answer || "Maaf, data tidak ditemukan dalam basis pengetahuan SGO." };
      setMessages((prev) => [...prev, newAiMsg]);
    } catch (error) {
      const errorMsg: Message = { role: "assistant", content: "⚠️ Terjadi gangguan koneksi ke server SGO Backend." };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    { title: "Risk Governance", desc: "Bagaimana struktur tata kelola risiko di BI?" },
    { title: "Kepatuhan (Compliance)", desc: "Apa sanksi untuk pelanggaran kode etik?" },
    { title: "Audit Internal", desc: "Jelaskan prosedur audit Self Governance." },
    { title: "Regulasi Terbaru", desc: "Apa mandat UU P2SK terkait pengawasan?" },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.chatArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.logoBig}>
              <ShieldAlert size={40} />
            </div>
            <h3 style={{ fontWeight: 600, color: "var(--bi-blue-primary)" }}>SGO Virtual Assistant</h3>
            <p style={{ fontSize: "0.9rem", maxWidth: "400px", textAlign: "center" }}>
              Selamat datang di layanan <b>Self Governance Observation</b>. Silakan ajukan pertanyaan terkait pengawasan, risiko, dan kepatuhan.
            </p>

            <div className={styles.suggestions}>
              {suggestions.map((s, i) => (
                <div key={i} className={styles.suggestionCard} onClick={() => handleSendMessage(s.desc)}>
                  <div className={styles.suggestionTitle}>{s.title}</div>
                  <div className={styles.suggestionDesc}>{s.desc}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <ChatMessage key={index} role={msg.role} content={msg.content} />
          ))
        )}

        {loading && (
          <div className={styles.loadingIndicator}>
            <div className="spinner"></div> Menganalisis dokumen regulasi...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSendMessage} disabled={loading} />
    </div>
  );
}
