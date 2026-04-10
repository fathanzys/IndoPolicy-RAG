import styles from "./page.module.css";
import ChatBox from "../components/ChatBox";
import Header from "../components/Header";

export default function HomePage() {
  return (
    <>
      <Header
        title="Self Governance Observation (SGO)"
        subtitle="Bank Indonesia Internal Control System"
      />

      <div className={styles.chatWrapper}>
        <ChatBox />
      </div>
    </>
  );
}
