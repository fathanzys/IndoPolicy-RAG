import Header from "../../components/Header";

export default function DashboardPage() {
    return (
        <>
            <Header
                title="Observation Dashboard"
                subtitle="Overview of Governance and Compliance Metrics"
            />
            <div style={{ padding: '40px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ color: 'var(--bi-blue-primary)' }}>Dashboard Overview</h3>
                <div style={{
                    background: 'white',
                    padding: '40px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    textAlign: 'center',
                    color: 'var(--text-secondary)'
                }}>
                    Dashboard Data and Analytics will be displayed here. (Feature coming soon)
                </div>
            </div>
        </>
    );
}
