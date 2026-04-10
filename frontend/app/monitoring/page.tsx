import Header from "../../components/Header";

export default function MonitoringPage() {
    return (
        <>
            <Header
                title="Risk Monitoring"
                subtitle="Live Monitoring of Enterprise Risks"
            />
            <div style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ color: 'var(--bi-blue-primary)' }}>Active Risk Assessments</h3>
                <div style={{
                    background: 'white',
                    padding: '40px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    textAlign: 'center',
                    color: 'var(--text-secondary)'
                }}>
                    Risk tracking charts and tables will be available in the next release.
                </div>
            </div>
        </>
    );
}
