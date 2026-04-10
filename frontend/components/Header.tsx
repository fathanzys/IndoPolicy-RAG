import styles from "./Header.module.css";

interface HeaderProps {
    title: string;
    subtitle: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
    return (
        <header className={styles.header}>
            <div>
                <h2 className={styles.headerTitle}>{title}</h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                    {subtitle}
                </p>
            </div>
            <div className={styles.headerStatus}>
                <div className={styles.statusDot}></div>
                System Online • Secure
            </div>
        </header>
    );
}
