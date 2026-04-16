import styles from "./Header.module.css";

interface HeaderProps {
    title: string;
    subtitle: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
    return (
        <header className={styles.header}>
            <div className={styles.headerInfo}>
                <h2 className={styles.headerTitle}>{title}</h2>
                <p className={styles.headerSubtitle}>{subtitle}</p>
            </div>
            <div className={styles.headerStatus}>
                <div className={styles.statusDot}></div>
                System Online
            </div>
        </header>
    );
}
