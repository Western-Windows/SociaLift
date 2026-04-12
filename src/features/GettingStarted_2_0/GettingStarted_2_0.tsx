import { useState, useRef, type ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import './GettingStarted_2_0.css';

export interface GettingStarted_2_0Props {}

export function GettingStarted_2_0({}: GettingStarted_2_0Props) {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleBrowseClick = () => fileInputRef.current?.click();

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) setSelectedFile(file);
    };

    // Validation: A file must be selected
    const isFormValid = selectedFile !== null;

    return (
        <div className="getting-started-container">
            {/* ... header & sidebar remain unchanged ... */}
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button" onClick={() => navigate(-1)}><span aria-hidden="true">&#8592;</span></button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main-layout">
                <aside className="gs-sidebar">
                    <div className="gs-step is-complete"><span className="gs-step-check">&#10003;</span><span className="gs-step-text">Company Information</span></div>
                    <div className="gs-step is-active"><span className="gs-step-num">2</span><span className="gs-step-text">Products Database</span></div>
                    <div className="gs-step"><span className="gs-step-num idle-num">3</span><span className="gs-step-text">Choose your Persona</span></div>
                    <div className="gs-badge">In progress</div>
                </aside>

                <section className="gs-form-card">
                    <h2 className="gs-title">Product Database</h2>
                    <p className="gs-subtitle">SociaLift collects this information to better understand and serve your business.</p>

                    <form className="gs-form-wrapper">
                        <div className="gs-input-group">
                            <label className="gs-label-title" style={{ textAlign: 'center', width: '100%' }}>Products</label>
                            <div className="gs-upload-container">
                                <div className="gs-upload-surface">
                                    <div className="gs-upload-dashed">
                                        <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileChange} />
                                        {selectedFile ? (
                                            <div className="gs-file-selected">
                                                <span className="gs-file-name">📄 {selectedFile.name}</span>
                                                <button type="button" className="gs-change-file-btn" onClick={handleBrowseClick}>Change File</button>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="gs-upload-icon" aria-hidden="true"><span className="gs-upload-arrow" /></div>
                                                <p>Drag and drop files here, or click to browse</p>
                                                <button className="gs-browse-button" type="button" onClick={handleBrowseClick}>Browse Files</button>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="gs-button-row">
                            <button 
                                className="gs-continue-button" 
                                type="button" 
                                onClick={() => navigate('/getting-started/3-0')}
                                disabled={!isFormValid}
                                style={{ opacity: isFormValid ? 1 : 0.5, cursor: isFormValid ? 'pointer' : 'not-allowed' }}
                            >
                                Continue &rarr;
                            </button>
                        </div>
                    </form>
                </section>
            </main>
        </div>
    );
}