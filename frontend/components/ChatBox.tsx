"use client";
import { useState, useRef, useEffect } from "react";
import ChatMessage, { ReasoningStep } from "./ChatMessage";
import ChatInput from "./ChatInput";
import { ShieldCheck, Scale, FileSearch, Landmark } from "lucide-react";
import styles from "./ChatBox.module.css";

// ── Types ──────────────────────────────────────────────────
type Message = {
  role: "user" | "assistant";
  content: string;
  steps?: ReasoningStep[];
  total_steps?: number;
  sources?: string[];
  follow_ups?: string[];
};

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

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
      // Simpan hanya role + content (steps tidak perlu di-persist)
      const toSave = messages.map(({ role, content }) => ({ role, content }));
      localStorage.setItem("sgo_chat_history", JSON.stringify(toSave));
    }
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (text: string, overrideHistory?: Message[]) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const currentAbortController = new AbortController();
    abortControllerRef.current = currentAbortController;

    const newUserMsg: Message = { role: "user", content: text };
    const historyToUse = overrideHistory !== undefined ? overrideHistory : messages;
    
    // Create initial state: User message + Empty Assistant message
    const initialAiMsg: Message = { 
        role: "assistant", 
        content: "", 
        steps: [], 
        total_steps: 0, 
        sources: [], 
        follow_ups: [] 
    };
    
    setMessages([...historyToUse, newUserMsg, initialAiMsg]);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";
      const chatHistoryForApi = historyToUse.map(({ role, content }) => ({ role, content }));

      const res = await fetch(`${apiUrl}/ask/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text, chat_history: chatHistoryForApi }),
        signal: currentAbortController.signal,
      });

      if (!res.ok) throw new Error("Server error");
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // Assistant message state tracker
      let currentContent = "";
      let currentSteps: ReasoningStep[] = [];
      let currentSources: string[] = [];
      let currentFollowUps: string[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            
            if (data.type === "token") {
              currentContent += data.content;
            } else if (["thought", "action", "clarification"].includes(data.type)) {
              currentSteps = [...currentSteps, data];
            } else if (data.answer) {
              // Final payload if not using token stream for final answer
              currentContent = data.answer;
              if (data.steps) currentSteps = data.steps;
              if (data.sources) currentSources = data.sources;
              if (data.follow_ups) currentFollowUps = data.follow_ups;
            }

            // Update UI
            setMessages((prev) => {
              const newMsgs = [...prev];
              const lastIdx = newMsgs.length - 1;
              newMsgs[lastIdx] = {
                ...newMsgs[lastIdx],
                content: currentContent,
                steps: currentSteps,
                total_steps: currentSteps.filter(s => s.type === "action").length,
                sources: currentSources,
                follow_ups: currentFollowUps,
              };
              return newMsgs;
            });

          } catch (e) {
            console.error("Error parsing stream line", e);
          }
        }
      }
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Fetch aborted");
        return;
      }
      setMessages((prev) => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1].content = "⚠️ Terjadi gangguan koneksi ke server SGO Backend.";
          return newMsgs;
      });
    } finally {
      if (abortControllerRef.current === currentAbortController) {
        setLoading(false);
      }
    }
  };

  const handleEditMessage = (index: number, newText: string) => {
    const sliced = messages.slice(0, index);
    handleSendMessage(newText, sliced);
  };

  const handleFeedback = async (msg: Message, rating: "up" | "down") => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";
      await fetch(`${apiUrl}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: messages[messages.indexOf(msg) - 1]?.content || "",
          answer: msg.content,
          rating,
        }),
      });
    } catch (e) {
      console.error("Failed to send feedback", e);
    }
  };

  const suggestions = [
    { icon: "🏛️", title: "Risk Governance", desc: "Bagaimana struktur tata kelola risiko di BI?" },
    { icon: "⚖️", title: "Kepatuhan (Compliance)", desc: "Apa sanksi untuk pelanggaran kode etik?" },
    { icon: "🔍", title: "Audit Internal", desc: "Jelaskan prosedur audit Self Governance." },
    { icon: "📋", title: "Regulasi Terbaru", desc: "Apa mandat UU P2SK terkait pengawasan?" },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.chatArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.heroIcon}>
              <ShieldCheck size={36} strokeWidth={1.5} />
            </div>
            <h3 className={styles.welcomeTitle}>SGO Virtual Assistant</h3>
            <p className={styles.welcomeDesc}>
              Selamat datang di layanan <b>Self Governance Observation</b>. 
              Silakan ajukan pertanyaan terkait pengawasan, risiko, dan kepatuhan internal.
            </p>

            <div className={styles.suggestions}>
              {suggestions.map((s, i) => (
                <div key={i} className={styles.suggestionCard} onClick={() => handleSendMessage(s.desc)}>
                  <div className={styles.suggestionIcon}>{s.icon}</div>
                  <div className={styles.suggestionTitle}>{s.title}</div>
                  <div className={styles.suggestionDesc}>{s.desc}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className={styles.messagesWrapper}>
            {messages.map((msg, index) => (
              <ChatMessage
                key={index}
                role={msg.role}
                content={msg.content}
                steps={msg.steps}
                total_steps={msg.total_steps}
                sources={msg.sources}
                onEdit={(newContent) => handleEditMessage(index, newContent)}
                onFeedback={(rating) => handleFeedback(msg, rating)}
              />
            ))}

            {/* Render follow-ups only for the last assistant message and if not loading */}
            {!loading && messages.length > 0 && messages[messages.length - 1].role === "assistant" && messages[messages.length - 1].follow_ups?.length! > 0 && (
              <div className={styles.followUpContainer}>
                {messages[messages.length - 1].follow_ups?.map((q, i) => (
                  <button key={i} className={styles.suggestionChip} onClick={() => handleSendMessage(q)}>
                    <i>✨</i> {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {loading && (
          <div className={styles.loadingIndicator}>
            <div className={styles.typingDots}>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className={styles.loadingText}>Agent sedang menganalisis dokumen...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSendMessage} disabled={loading} />
    </div>
  );
}
