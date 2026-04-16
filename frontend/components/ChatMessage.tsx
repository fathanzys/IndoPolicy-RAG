"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { ChevronDown, ChevronUp, Brain, Search, FileText, CheckCircle, XCircle, Pencil, ThumbsUp, ThumbsDown, BookOpen } from "lucide-react";
import styles from "./ChatMessage.module.css";

// ── Types ──────────────────────────────────────────────────────
export interface ReasoningStep {
  type: "thought" | "action" | "observation" | "clarification";
  content?: string;
  tool?: string;
  query?: string;
  chunks_found?: number;
  preview?: string;
  is_sufficient?: boolean;
  total_chunks?: number;
  question?: string;
  context_summary?: string;
}

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  steps?: ReasoningStep[];
  total_steps?: number;
  sources?: string[];
  onEdit?: (newContent: string) => void;
  onFeedback?: (rating: "up" | "down") => void;
}

// ── Step Icon & Label ──────────────────────────────────────────
function StepIcon({ step }: { step: ReasoningStep }) {
  if (step.type === "thought") return <Brain size={14} />;
  if (step.type === "observation") return <FileText size={14} />;
  if (step.type === "clarification") return <Search size={14} color="#ff9800" />;
  if (step.tool === "retrieve_policy_documents") return <Search size={14} />;
  if (step.tool === "check_context_quality") {
    return step.is_sufficient
      ? <CheckCircle size={14} />
      : <XCircle size={14} />;
  }
  return <FileText size={14} />;
}

function StepCard({ step }: { step: ReasoningStep }) {
  const cls =
    step.type === "thought"
      ? styles.stepThought
      : step.type === "observation"
      ? styles.stepObs
      : step.type === "clarification"
      ? styles.stepObs
      : step.tool === "check_context_quality"
      ? styles.stepCheck
      : styles.stepAction;

  // Label dinamis
  const label =
    step.type === "thought"
      ? "💭 Thought"
      : step.type === "observation"
      ? "📄 Observation"
      : step.type === "clarification"
      ? "⚠️ Stop & Clarify"
      : step.tool === "retrieve_policy_documents"
      ? "🔍 Retrieve Policy Documents"
      : step.tool === "check_context_quality"
      ? "✅ Check Context Quality"
      : "⚙️ Action";

  return (
    <div className={`${styles.stepCard} ${cls}`}>
      <div className={styles.stepHeader}>
        <StepIcon step={step} />
        <span className={styles.stepLabel}>{label}</span>
      </div>

      {/* Action: retrieve */}
      {step.type === "action" && step.tool === "retrieve_policy_documents" && (
        <div className={styles.stepBody}>
          <span className={styles.stepMeta}>Query:</span>
          <code className={styles.stepCode}>{step.query}</code>
          {step.chunks_found !== undefined && (
            <span className={styles.stepBadge}>
              {step.chunks_found} chunk{step.chunks_found !== 1 ? "s" : ""} ditemukan
            </span>
          )}
        </div>
      )}

      {/* Action: quality check */}
      {step.type === "action" && step.tool === "check_context_quality" && (
        <div className={styles.stepBody}>
          <span
            className={`${styles.stepBadge} ${
              step.is_sufficient ? styles.badgeGreen : styles.badgeOrange
            }`}
          >
            {step.is_sufficient ? "✅ Konteks Cukup" : "⚠️ Konteks Kurang"}
          </span>
          {step.total_chunks !== undefined && (
            <span className={styles.stepMeta}>{step.total_chunks} chunk terkumpul</span>
          )}
        </div>
      )}

      {/* Thought / Observation / Clarification */}
      {(step.type === "thought" || step.type === "observation" || step.type === "clarification") && step.content && (
        <p className={styles.stepContent} style={step.type === "clarification" ? { color: "#d97706", fontWeight: 500 } : {}}>
          {step.content}
        </p>
      )}
    </div>
  );
}

export default function ChatMessage({
  role,
  content,
  steps,
  total_steps,
  sources,
  onEdit,
  onFeedback,
}: ChatMessageProps) {
  const isUser = role === "user";
  const [showSteps, setShowSteps] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);
  const [editValue, setEditValue] = useState(content);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const hasSteps = !isUser && steps && steps.length > 0;
  const hasSources = !isUser && sources && sources.length > 0;

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(textareaRef.current.value.length, textareaRef.current.value.length);
    }
  }, [isEditing]);

  const handleSaveEdit = () => {
    if (editValue.trim() && editValue !== content) {
      onEdit?.(editValue);
    }
    setIsEditing(false);
  };

  const handleFeedbackClick = (rating: "up" | "down") => {
    if (feedback === rating) return;
    setFeedback(rating);
    onFeedback?.(rating);
  };

  return (
    <div className={`${styles.wrapper} ${isUser ? styles.wrapperUser : ""}`}>
      <div className={`${styles.avatar} ${isUser ? styles.avatarUser : styles.avatarBot}`}>
        {isUser ? "U" : "SGO"}
      </div>

      <div className={styles.contentWrapper}>
        <span className={styles.senderName} style={{ justifyContent: isUser ? "flex-end" : "flex-start", width: "100%" }}>
          {isUser && !isEditing && (
            <button className={styles.editButton} onClick={() => setIsEditing(true)} title="Edit Pesan">
              <Pencil size={12} />
            </button>
          )}
          {isUser ? "User" : "SGO Assistant"}
          {hasSteps && (
            <span className={styles.agentBadge}>
              🤖 Agentic · {total_steps} step{total_steps !== 1 ? "s" : ""}
            </span>
          )}
        </span>

        {isEditing ? (
          <div className={styles.editContainer}>
            <textarea
              ref={textareaRef}
              className={styles.editTextarea}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Escape") {
                  setIsEditing(false);
                  setEditValue(content);
                }
              }}
            />
            <div className={styles.editActions}>
              <button 
                className={styles.btnCancel} 
                onClick={() => { setIsEditing(false); setEditValue(content); }}
              >
                Batal
              </button>
              <button className={styles.btnSave} onClick={handleSaveEdit}>
                Save & Resubmit
              </button>
            </div>
          </div>
        ) : (
          <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleBot}`}>
            <ReactMarkdown
              components={{
                p: ({ node, ...props }) => <p style={{ margin: "0 0 0.5em 0" }} {...props} />,
                ul: ({ node, ...props }) => <ul style={{ margin: "0 0 0.5em 1.5em", paddingLeft: "1em" }} {...props} />,
                ol: ({ node, ...props }) => <ol style={{ margin: "0 0 0.5em 1.5em", paddingLeft: "1em" }} {...props} />,
                li: ({ node, ...props }) => <li style={{ marginBottom: "0.25em" }} {...props} />,
                h3: ({ node, ...props }) => <h3 style={{ fontSize: "1.1em", marginTop: "0.5em", marginBottom: "0.5em" }} {...props} />,
                h4: ({ node, ...props }) => <h4 style={{ fontSize: "1em", marginTop: "0.5em", marginBottom: "0.5em" }} {...props} />,
                strong: ({ node, ...props }) => <strong style={{ fontWeight: 600, color: "inherit" }} {...props} />,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        )}

        {/* ── Collapsible Reasoning Steps ── */}
        {hasSteps && (
          <div className={styles.reasoningWrapper}>
            <button
              className={styles.reasoningToggle}
              onClick={() => setShowSteps((v) => !v)}
            >
              {showSteps ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              <span>{showSteps ? "Sembunyikan" : "Lihat"} proses berpikir agent ({total_steps} langkah)</span>
            </button>

            {showSteps && (
              <div className={styles.stepsContainer}>
                {steps!.map((step, i) => (
                  <StepCard key={i} step={step} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Feedbacks & Sources Logic ── */}
        {!isUser && (
          <div className={styles.actionsWrapper}>
            <div className={styles.feedbackContainer}>
              <button 
                className={`${styles.feedbackBtn} ${feedback === "up" ? styles.feedbackBtnActive : ""}`}
                onClick={() => handleFeedbackClick("up")}
                title="Bermanfaat"
              >
                <ThumbsUp size={14} />
              </button>
              <button 
                className={`${styles.feedbackBtn} ${feedback === "down" ? styles.feedbackBtnActive : ""}`}
                onClick={() => handleFeedbackClick("down")}
                title="Tidak Bermanfaat"
              >
                <ThumbsDown size={14} />
              </button>
            </div>

            {hasSources && (
              <button
                className={styles.reasoningToggle}
                onClick={() => setShowSources(!showSources)}
              >
                <BookOpen size={14} />
                <span>{showSources ? "Sembunyikan" : "Lihat"} {sources?.length} Referensi Sumber</span>
              </button>
            )}
          </div>
        )}

        {/* ── Collapsible Sources ── */}
        {showSources && hasSources && (
          <div className={styles.sourcesWrapper}>
            <div className={styles.sourcesTitle}>
              <FileText size={14} />
              <span>Dokumen Referensi Resmi BI</span>
            </div>
            <div className={styles.sourceList}>
              {sources!.map((src, i) => (
                <div key={i} className={styles.sourceItem}>
                  <span className={styles.sourceMeta}>Referensi #{i + 1}</span>
                  <ReactMarkdown>{src}</ReactMarkdown>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
