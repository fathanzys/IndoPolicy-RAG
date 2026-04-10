import { Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import styles from "./ChatMessage.module.css";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
}

export default function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`${styles.wrapper} ${isUser ? styles.wrapperUser : ""}`}>
      <div className={`${styles.avatar} ${isUser ? styles.avatarUser : styles.avatarBot}`}>
        {isUser ? "U" : "SGO"}
      </div>
      
      <div className={styles.contentWrapper}>
        <span className={styles.senderName} style={{textAlign: isUser ? "right" : "left"}}>
          {isUser ? "User" : "SGO Assistant"}
        </span>
        <div className={`${styles.bubble} ${isUser ? styles.bubbleUser : styles.bubbleBot}`}>
          <ReactMarkdown
            components={{
              p: ({node, ...props}) => <p style={{margin: "0 0 0.5em 0"}} {...props} />,
              ul: ({node, ...props}) => <ul style={{margin: "0 0 0.5em 1.5em", paddingLeft: "1em"}} {...props} />,
              ol: ({node, ...props}) => <ol style={{margin: "0 0 0.5em 1.5em", paddingLeft: "1em"}} {...props} />,
              li: ({node, ...props}) => <li style={{marginBottom: "0.25em"}} {...props} />,
              h3: ({node, ...props}) => <h3 style={{fontSize: "1.1em", marginTop: "0.5em", marginBottom: "0.5em"}} {...props} />,
              h4: ({node, ...props}) => <h4 style={{fontSize: "1em", marginTop: "0.5em", marginBottom: "0.5em"}} {...props} />,
              strong: ({node, ...props}) => <strong style={{fontWeight: 600, color: "inherit"}} {...props} />
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
