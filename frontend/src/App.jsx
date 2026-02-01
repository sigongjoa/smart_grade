import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, BarChart3, Fingerprint, Search, Users, FileUp, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
    // Mode: 'single' or 'batch'
    const [mode, setMode] = useState('single');

    // Single scan state
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);

    // Batch grade state
    const [pdfFile, setPdfFile] = useState(null);
    const [omrFile, setOmrFile] = useState(null);
    const [batchResult, setBatchResult] = useState(null);
    const [isBatchProcessing, setIsBatchProcessing] = useState(false);

    // Single scan handler
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

            const mappedGrades = Object.entries(data.grades).map(([q, details]) => ({
                q: parseInt(q),
                status: details.selected.length > 0 ? "correct" : "none",
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

    // Batch grade handler
    const handleBatchGrade = async () => {
        if (!pdfFile || !omrFile) {
            alert('Please upload both PDF answer key and OMR image.');
            return;
        }

        setIsBatchProcessing(true);
        setBatchResult(null);

        const formData = new FormData();
        formData.append('answer_pdf', pdfFile);
        formData.append('omr_image', omrFile);

        try {
            const response = await fetch('/api/batch-grade', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Batch grading failed');
            }

            const data = await response.json();
            setBatchResult(data);
        } catch (err) {
            console.error(err);
            alert("Error: " + err.message);
        } finally {
            setIsBatchProcessing(false);
        }
    };

    const clearBatchFiles = () => {
        setPdfFile(null);
        setOmrFile(null);
        setBatchResult(null);
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

            {/* Mode Tabs */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }} className="animate-fade">
                <button
                    onClick={() => setMode('single')}
                    className={`mode-tab ${mode === 'single' ? 'active' : ''}`}
                    style={{
                        padding: '12px 24px',
                        borderRadius: '12px',
                        border: 'none',
                        background: mode === 'single' ? 'var(--accent-primary)' : 'var(--bg-card)',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontWeight: 600,
                        transition: 'all 0.3s ease'
                    }}
                >
                    <Fingerprint size={18} /> Single Scan
                </button>
                <button
                    onClick={() => setMode('batch')}
                    className={`mode-tab ${mode === 'batch' ? 'active' : ''}`}
                    style={{
                        padding: '12px 24px',
                        borderRadius: '12px',
                        border: 'none',
                        background: mode === 'batch' ? 'var(--accent-primary)' : 'var(--bg-card)',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontWeight: 600,
                        transition: 'all 0.3s ease'
                    }}
                >
                    <Users size={18} /> Batch Grade
                </button>
            </div>

            <main className="dashboard-grid">
                {mode === 'single' ? (
                    /* Single Scan Mode */
                    <>
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
                    </>
                ) : (
                    /* Batch Grade Mode */
                    <>
                        <section className="animate-fade" style={{ animationDelay: '0.1s' }}>
                            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                    <h3><Users size={18} style={{ marginRight: 8 }} /> Batch Grade</h3>
                                    {(pdfFile || omrFile) && (
                                        <button
                                            onClick={clearBatchFiles}
                                            style={{
                                                background: 'transparent',
                                                border: '1px solid var(--danger)',
                                                color: 'var(--danger)',
                                                padding: '6px 12px',
                                                borderRadius: '8px',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '4px',
                                                fontSize: '0.8rem'
                                            }}
                                        >
                                            <X size={14} /> Clear
                                        </button>
                                    )}
                                </div>
                                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                                    Upload a PDF with answer key and an image containing multiple OMR cards.
                                </p>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                                    {/* PDF Upload */}
                                    <label className="upload-zone" style={{ height: '150px' }}>
                                        <input
                                            type="file"
                                            hidden
                                            accept=".pdf"
                                            onChange={(e) => setPdfFile(e.target.files[0])}
                                        />
                                        <FileUp size={32} color={pdfFile ? 'var(--success)' : 'var(--accent-primary)'} style={{ marginBottom: '0.5rem' }} />
                                        <p style={{ fontSize: '0.85rem', textAlign: 'center' }}>
                                            {pdfFile ? (
                                                <span style={{ color: 'var(--success)' }}>{pdfFile.name}</span>
                                            ) : (
                                                "Answer PDF"
                                            )}
                                        </p>
                                        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>PDF with answer key</span>
                                    </label>

                                    {/* OMR Image Upload */}
                                    <label className="upload-zone" style={{ height: '150px' }}>
                                        <input
                                            type="file"
                                            hidden
                                            accept="image/*"
                                            onChange={(e) => setOmrFile(e.target.files[0])}
                                        />
                                        <Fingerprint size={32} color={omrFile ? 'var(--success)' : 'var(--accent-primary)'} style={{ marginBottom: '0.5rem' }} />
                                        <p style={{ fontSize: '0.85rem', textAlign: 'center' }}>
                                            {omrFile ? (
                                                <span style={{ color: 'var(--success)' }}>{omrFile.name}</span>
                                            ) : (
                                                "OMR Image"
                                            )}
                                        </p>
                                        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Grid of OMR cards</span>
                                    </label>
                                </div>

                                <button
                                    onClick={handleBatchGrade}
                                    disabled={!pdfFile || !omrFile || isBatchProcessing}
                                    className="btn-primary"
                                    style={{
                                        width: '100%',
                                        padding: '14px',
                                        fontSize: '1rem',
                                        opacity: (!pdfFile || !omrFile || isBatchProcessing) ? 0.5 : 1,
                                        cursor: (!pdfFile || !omrFile || isBatchProcessing) ? 'not-allowed' : 'pointer'
                                    }}
                                >
                                    {isBatchProcessing ? (
                                        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                            <motion.div
                                                animate={{ rotate: 360 }}
                                                transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                                                style={{ width: '18px', height: '18px', border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%' }}
                                            />
                                            Processing...
                                        </span>
                                    ) : (
                                        'Start Batch Grading'
                                    )}
                                </button>
                            </div>

                            {/* Batch Results */}
                            <AnimatePresence>
                                {batchResult && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0 }}
                                        className="glass-card"
                                    >
                                        <h3 style={{ marginBottom: '1rem' }}>
                                            <CheckCircle size={18} style={{ marginRight: 8, color: 'var(--success)' }} />
                                            Grading Results
                                        </h3>

                                        {/* Answer Key Display */}
                                        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                                            <h4 style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                                                Answer Key ({batchResult.total_questions} questions)
                                            </h4>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                                {batchResult.answer_key.map((ans, idx) => (
                                                    <span key={idx} style={{
                                                        background: 'var(--accent-primary)',
                                                        color: 'white',
                                                        padding: '2px 8px',
                                                        borderRadius: '4px',
                                                        fontSize: '0.75rem',
                                                        fontWeight: 600
                                                    }}>
                                                        {idx + 1}.{ans}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Students Table */}
                                        <div style={{ overflowX: 'auto' }}>
                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                                        <th style={{ textAlign: 'left', padding: '12px 8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>#</th>
                                                        <th style={{ textAlign: 'left', padding: '12px 8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Name</th>
                                                        <th style={{ textAlign: 'center', padding: '12px 8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Score</th>
                                                        <th style={{ textAlign: 'center', padding: '12px 8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Percentage</th>
                                                        <th style={{ textAlign: 'center', padding: '12px 8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Status</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {batchResult.students.map((student, idx) => (
                                                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                                            <td style={{ padding: '12px 8px', fontSize: '0.9rem' }}>{idx + 1}</td>
                                                            <td style={{ padding: '12px 8px', fontSize: '0.9rem', fontWeight: 600 }}>{student.name}</td>
                                                            <td style={{ padding: '12px 8px', fontSize: '0.9rem', textAlign: 'center' }}>{student.score}</td>
                                                            <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                                                                <span style={{
                                                                    background: student.percentage >= 80 ? 'var(--success)' :
                                                                        student.percentage >= 60 ? 'var(--warning)' : 'var(--danger)',
                                                                    color: 'black',
                                                                    padding: '4px 10px',
                                                                    borderRadius: '12px',
                                                                    fontSize: '0.8rem',
                                                                    fontWeight: 700
                                                                }}>
                                                                    {student.percentage}%
                                                                </span>
                                                            </td>
                                                            <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                                                                {student.percentage >= 60 ? (
                                                                    <CheckCircle size={18} color="var(--success)" />
                                                                ) : (
                                                                    <AlertCircle size={18} color="var(--danger)" />
                                                                )}
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </section>

                        {/* Statistics Panel */}
                        <section className="animate-fade" style={{ animationDelay: '0.2s' }}>
                            <div className="glass-card" style={{ height: '100%' }}>
                                <h3><BarChart3 size={18} style={{ marginRight: 8 }} /> Statistics</h3>

                                {batchResult ? (
                                    <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                        {[
                                            { label: "Students", value: batchResult.statistics.student_count, trend: "Total" },
                                            { label: "Average Score", value: `${batchResult.statistics.average_score}%`, trend: batchResult.statistics.average_score >= 70 ? "Good" : "Needs Improvement" },
                                            { label: "Highest", value: `${batchResult.statistics.highest_score}%`, trend: "Best" },
                                            { label: "Lowest", value: `${batchResult.statistics.lowest_score}%`, trend: "Min" },
                                            { label: "Perfect Scores", value: batchResult.statistics.perfect_scores || 0, trend: "100%" },
                                            { label: "Failing (<60%)", value: batchResult.statistics.failing_scores || 0, trend: "Need Help" }
                                        ].map((item, idx) => (
                                            <div key={idx}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                                    <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{item.label}</span>
                                                    <span style={{ fontSize: '0.8rem', color: 'var(--accent-secondary)' }}>{item.trend}</span>
                                                </div>
                                                <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{item.value}</div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div style={{ marginTop: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                        <BarChart3 size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                                        <p>Statistics will appear after batch grading</p>
                                    </div>
                                )}

                                <div style={{ marginTop: '2rem', padding: '1rem', borderRadius: '16px', background: 'linear-gradient(135deg, rgba(124, 77, 255, 0.1), rgba(0, 229, 255, 0.1))', border: '1px solid var(--accent-primary)' }}>
                                    <h4 style={{ fontSize: '0.9rem', marginBottom: '8px' }}>Batch Mode</h4>
                                    <p style={{ fontSize: '0.8rem', opacity: 0.8 }}>
                                        Upload PDF with answers and scan image with multiple OMR cards in grid layout.
                                    </p>
                                </div>
                            </div>
                        </section>
                    </>
                )}
            </main>
        </div>
    );
}

export default App;
