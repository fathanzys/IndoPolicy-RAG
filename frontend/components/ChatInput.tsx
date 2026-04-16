"use client";
import { Send, Loader2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (input.trim() && !disabled) { onSend(input); setInput(""); }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.inputWrapper}>
        <textarea 
          ref={textareaRef}
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          onKeyDown={handleKeyDown}
          placeholder="Ketik pertanyaan Anda di sini... (Shift + Enter untk baris baru)" 
          disabled={disabled} 
          className={styles.input} 
          rows={1}
        />
        <button type="submit" disabled={disabled || !input.trim()} className={styles.sendButton}>
          {disabled ? <Loader2 size={18} className={styles.loading} /> : <Send size={18} />}
        </button>
      </form>
      <p className={styles.disclaimer}>Informasi yang dihasilkan AI bersifat asistif. Harap verifikasi dengan dokumen resmi BI.</p>
    </div>
  );
}
