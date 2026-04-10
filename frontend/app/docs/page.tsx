import Header from "../../components/Header";

export default function DocsPage() {
    return (
        <>
            <Header
                title="Regulatory Documents"
                subtitle="Manage and Query Internal Governance Documents"
            />
            <div style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ color: 'var(--bi-blue-primary)' }}>Document Repository</h3>
                <div style={{
                    background: 'white',
                    padding: '40px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    textAlign: 'center',
                    color: 'var(--text-secondary)'
                }}>
                    PDF Document Viewer and upload utilities will be placed here.
                </div>
            </div>
        </>
    );
}
