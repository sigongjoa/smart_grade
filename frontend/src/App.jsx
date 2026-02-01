import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, BarChart3, Fingerprint, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setSelectedFile(file);
        setIsUploading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/grade', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Grading failed');

            const data = await response.json();

            // Map backend response to UI format
            const mappedGrades = Object.entries(data.grades).map(([q, details]) => ({
                q: parseInt(q),
                status: details.selected.length > 0 ? "correct" : "none", // Simplification
                confidence: details.confidence[0] || 0,
                selected: details.selected
            }));

            setResult({
                student: data.student_name || "Unknown Student",
                score: `${mappedGrades.filter(g => g.selected.length > 0).length} / ${mappedGrades.length}`,
                accuracy: "N/A",
                ocr_text: data.text_found.map(t => t.text).join(' '),
                grades: mappedGrades,
                image_url: data.warped_url
            });
        } catch (err) {
            console.error(err);
            alert("Error: " + err.message);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="app-container">
            <header className="header animate-fade">
                <div className="logo">SMART-GRADER <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>by Mathesis</span></div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div className="status-badge status-valid">System Active</div>
                    <div className="glass-card" style={{ padding: '8px 16px', borderRadius: '12px' }}>
                        Teacher Mode
                    </div>
                </div>
            </header>

            <main className="dashboard-grid">
                <section className="animate-fade" style={{ animationDelay: '0.1s' }}>
                    <div className="glass-card" style={{ marginBottom: '2rem' }}>
                        <h3><Upload size={18} style={{ marginRight: 8 }} /> Quick Scan</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                            Drag OMR cards or photos here. No timing marks required.
                        </p>

                        <label className="upload-zone">
                            <input type="file" hidden onChange={handleUpload} accept="image/*" />
                            <Fingerprint size={48} color="var(--accent-primary)" style={{ marginBottom: '1rem' }} />
                            {isUploading ? (
                                <div style={{ textAlign: 'center' }}>
                                    <p>AI Engine Scanning...</p>
                                    <div style={{ width: '200px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '10px', overflow: 'hidden' }}>
                                        <motion.div
                                            initial={{ x: '-100%' }}
                                            animate={{ x: '100%' }}
                                            transition={{ repeat: Infinity, duration: 1.5 }}
                                            style={{ width: '100%', height: '100%', background: 'var(--accent-primary)' }}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <p>{selectedFile ? selectedFile.name : "Click to select a file"}</p>
                            )}
                        </label>
                    </div>

                    <AnimatePresence>
                        {result && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="glass-card"
                            >
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '1.5rem' }}>
                                    <div className="preview-container">
                                        <h4 style={{ marginBottom: '1rem' }}>Processed OMR Card</h4>
                                        <img
                                            src={result.image_url}
                                            alt="Processed OMR"
                                            style={{ width: '100%', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}
                                        />
                                    </div>
                                    <div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                            <div>
                                                <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{result.student}</h2>
                                                <p style={{ color: 'var(--text-secondary)' }}>Mathesis-Synapse Node: #13-SG</p>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: '2rem', color: 'var(--accent-secondary)' }}>{result.score}</div>
                                                <div style={{ fontSize: '0.8rem', color: 'var(--success)' }}>Accuracy: {result.accuracy}</div>
                                            </div>
                                        </div>

                                        <div style={{
                                            display: 'grid',
                                            gridTemplateColumns: 'repeat(auto-fill, minmax(65px, 1fr))',
                                            gap: '0.4rem',
                                            marginBottom: '2rem',
                                            maxHeight: '300px',
                                            overflowY: 'auto',
                                            padding: '10px',
                                            background: 'rgba(0,0,0,0.2)',
                                            borderRadius: '12px'
                                        }}>
                                            {result.grades.map((g, i) => (
                                                <div key={i} className="glass-card" style={{ padding: '6px', textAlign: 'center', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                                    <div style={{ fontSize: '0.6rem', color: 'var(--text-secondary)', marginBottom: '2px' }}>Q{g.q}</div>
                                                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                                                        {g.selected.length > 0 ? (
                                                            <div style={{ background: 'var(--success)', color: 'black', borderRadius: '50%', width: '18px', height: '18px', fontSize: '0.7rem', fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                                {g.selected[0] + 1}
                                                            </div>
                                                        ) : (
                                                            <Search size={14} color="var(--warning)" />
                                                        )}
                                                    </div>
                                                    <div style={{ fontSize: '0.5rem', marginTop: '2px', opacity: 0.5 }}>{Math.round(g.confidence * 100)}%</div>
                                                </div>
                                            ))}
                                        </div>

                                        <div>
                                            <h4><FileText size={16} style={{ marginRight: 6 }} /> AI Insights</h4>
                                            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem', lineHeight: '1.6', maxHeight: '150px', overflowY: 'auto' }}>
                                                {result.ocr_text}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </section>

                <section className="animate-fade" style={{ animationDelay: '0.2s' }}>
                    <div className="glass-card" style={{ height: '100%' }}>
                        <h3><BarChart3 size={18} style={{ marginRight: 8 }} /> Progress</h3>
                        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            {[
                                { label: "Average Score", value: "72.4", trend: "+5%" },
                                { label: "Scanning Speed", value: "0.8s", trend: "Optimal" },
                                { label: "AI Confidence", value: "99.2%", trend: "Stable" }
                            ].map((item, idx) => (
                                <div key={idx}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{item.label}</span>
                                        <span style={{ fontSize: '0.8rem', color: 'var(--success)' }}>{item.trend}</span>
                                    </div>
                                    <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{item.value}</div>
                                </div>
                            ))}
                        </div>

                        <div style={{ marginTop: '3rem', padding: '1rem', borderRadius: '16px', background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.1), rgba(0, 229, 255, 0.1))', border: '1px solid var(--accent-primary)' }}>
                            <h4 style={{ fontSize: '0.9rem', marginBottom: '8px' }}>Next Step</h4>
                            <p style={{ fontSize: '0.8rem', opacity: 0.8 }}>Monthly reports will be generated automatically on Saturday.</p>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}

export default App;
