import Header from "../../components/Header";

export default function SettingsPage() {
    return (
        <>
            <Header
                title="Settings"
                subtitle="System Preferences and Account Settings"
            />
            <div style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ color: 'var(--bi-blue-primary)' }}>Preferences</h3>
                <div style={{
                    background: 'white',
                    padding: '40px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    textAlign: 'center',
                    color: 'var(--text-secondary)'
                }}>
                    Configuration settings for RAG engine, LLM models, and user profile management will be implemented here.
                </div>
            </div>
        </>
    );
}
