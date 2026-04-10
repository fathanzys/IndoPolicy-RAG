"use client";
import { Send, Loader2 } from "lucide-react";
import { useState } from "react";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) { onSend(input); setInput(""); }
  };
  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.inputWrapper}>
        <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ketik pertanyaan Anda di sini..." disabled={disabled} className={styles.input} />
        <button type="submit" disabled={disabled || !input.trim()} className={styles.sendButton}>
          {disabled ? <Loader2 size={18} className={styles.loading} /> : <Send size={18} />}
        </button>
      </form>
      <p className={styles.disclaimer}>Informasi yang dihasilkan AI bersifat asistif. Harap verifikasi dengan dokumen resmi BI.</p>
    </div>
  );
}
