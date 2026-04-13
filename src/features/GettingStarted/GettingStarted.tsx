import { useState, useRef, type ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import './GettingStarted.css'; // Make sure this points to the merged file

export function GettingStarted() {
    const navigate = useNavigate();

    // === GLOBAL PROGRESS STATE ===
    const [step, setStep] = useState(0);
    const [showModal, setShowModal] = useState(false);

    // === STEP 0 STATE (Company Info 1) ===
    const [formData, setFormData] = useState({ companyName: '', founderName: '', hotline: '', phoneNumber: '', emailAddress: '' });
    const [touched, setTouched] = useState({ hotline: false, phoneNumber: false, emailAddress: false });

    // === STEP 1 STATE (Company Info 2) ===
    const [aboutUs, setAboutUs] = useState('');
    const [targetAudience, setTargetAudience] = useState('');

    // === STEP 2 STATE (Company Info 3) ===
    const [services, setServices] = useState<string[]>(['']);
    const [locations, setLocations] = useState<string[]>(['']);

    // === STEP 3 STATE (Product Database) ===
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // === STEP 4 STATE (Persona Post) ===
    const [postText, setPostText] = useState('');

    // === STEP 5 STATE (Choose Persona) ===
    const [selectedPersona, setSelectedPersona] = useState<number | null>(null);

    // === VALIDATION & HANDLERS ===
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phoneRegex = /^\+?[\d\s\-]{8,15}$/;
    const hotlineRegex = /^[\d\s\-]{3,10}$/;

    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    const handleFormBlur = (e: React.FocusEvent<HTMLInputElement>) => setTouched(prev => ({ ...prev, [e.target.name]: true }));

    const handleServiceChange = (index: number, value: string) => {
        const newServices = [...services];
        newServices[index] = value;
        setServices(newServices);
    };
    const handleLocationChange = (index: number, value: string) => {
        const newLocations = [...locations];
        newLocations[index] = value;
        setLocations(newLocations);
    };

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) setSelectedFile(file);
    };

    // Form Validity
    const isStep0Valid = emailRegex.test(formData.emailAddress) && phoneRegex.test(formData.phoneNumber) && hotlineRegex.test(formData.hotline) && formData.companyName.trim() !== '' && formData.founderName.trim() !== '';
    const isStep1Valid = aboutUs.trim() !== '' && targetAudience.trim() !== '';
    const isStep2Valid = services.every(s => s.trim() !== '') && locations.every(l => l.trim() !== '');
    const isStep3Valid = selectedFile !== null;
    const isStep4Valid = postText.trim() !== '';
    const isStep5Valid = selectedPersona !== null;

    // Navigation Handlers
    const nextStep = () => setStep(prev => prev + 1);
    const prevStep = () => {
        if (step === 0) navigate(-1);
        else setStep(prev => prev - 1);
    };

    // Dynamic Persona Mapping based on selection in Step 5
    const getPersonaDetails = () => {
        switch (selectedPersona) {
            case 1:
                return { name: "The Playful Rebel", tone: "Casual, Rebellious & Fun" };
            case 2:
                return { name: "The Trendsetter", tone: "Urban, Influencing & Authentic" };
            case 3:
                return { name: "The Ruler", tone: "Strategic, Exclusive & Elegant" };
            default:
                return { name: "Unknown", tone: "Unknown" };
        }
    };

    const errorStyle = { color: '#e74c3c', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' };

    // === RENDER DYNAMIC FORM ===
    const renderStep = () => {
        switch (step) {
            case 0:
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Company Information</h2>
                        <p className="gs-subtitle">SociaLift collects this information to better understand and serve your business.</p>
                        <form className="gs-form-grid">
                            <div className="gs-input-group"><label>Company Name</label><input name="companyName" placeholder="Company Name" type="text" value={formData.companyName} onChange={handleFormChange} /></div>
                            <div className="gs-input-group"><label>Founder Name</label><input name="founderName" placeholder="Founder Name" type="text" value={formData.founderName} onChange={handleFormChange} /></div>
                            <div className="gs-input-group"><label>Hotline</label><input name="hotline" placeholder="e.g. 19000" type="tel" value={formData.hotline} onChange={handleFormChange} onBlur={handleFormBlur}/>
                                {touched.hotline && !hotlineRegex.test(formData.hotline) && formData.hotline && <span style={errorStyle}>Invalid hotline.</span>}
                            </div>
                            <div className="gs-input-group"><label>Phone Number</label><input name="phoneNumber" placeholder="Phone Number" type="tel" value={formData.phoneNumber} onChange={handleFormChange} onBlur={handleFormBlur} />
                                {touched.phoneNumber && !phoneRegex.test(formData.phoneNumber) && formData.phoneNumber && <span style={errorStyle}>Invalid phone.</span>}
                            </div>
                            <div className="gs-input-group" style={{ gridColumn: '1 / -1' }}><label>Email Address</label><input name="emailAddress" placeholder="Email Address" type="email" value={formData.emailAddress} onChange={handleFormChange} onBlur={handleFormBlur} />
                                {touched.emailAddress && !emailRegex.test(formData.emailAddress) && formData.emailAddress && <span style={errorStyle}>Invalid email.</span>}
                            </div>
                            <div className="gs-button-row">
                                <button className="gs-continue-button" type="button" onClick={nextStep} disabled={!isStep0Valid} style={{ opacity: isStep0Valid ? 1 : 0.5, cursor: isStep0Valid ? 'pointer' : 'not-allowed' }}>Continue &rarr;</button>
                            </div>
                        </form>
                    </section>
                );
            case 1:
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Company Information</h2>
                        <p className="gs-subtitle">Tell us more about your brand.</p>
                        <form className="gs-form-wrapper">
                            <div className="gs-input-group">
                                <label className="gs-label-title" htmlFor="aboutUs">About Us</label>
                                <textarea id="aboutUs" className="gs-textarea" value={aboutUs} onChange={(e) => setAboutUs(e.target.value)} placeholder="e.g: Founded in 1998..." />
                            </div>
                            <div className="gs-input-group" style={{ marginTop: '1.5rem' }}>
                                <label className="gs-label-title" htmlFor="targetAudience">Target Audience</label>
                                <textarea id="targetAudience" className="gs-textarea" value={targetAudience} onChange={(e) => setTargetAudience(e.target.value)} placeholder="Brand-loyal shoppers aged 25 to 55..." />
                            </div>
                            <div className="gs-button-row">
                                <button className="gs-continue-button" type="button" onClick={nextStep} disabled={!isStep1Valid} style={{ opacity: isStep1Valid ? 1 : 0.5, cursor: isStep1Valid ? 'pointer' : 'not-allowed' }}>Continue &rarr;</button>
                            </div>
                        </form>
                    </section>
                );
            case 2:
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Company Information</h2>
                        <form className="gs-form-wrapper">
                            <div className="gs-form-grid">
                                <div className="gs-field-column">
                                    <label className="gs-col-title">Services</label>
                                    <div className="gs-dynamic-list">
                                        {services.map((service, index) => (
                                            <div className="gs-input-with-addon" key={`service-${index}`}>
                                                <input placeholder="Service name" type="text" value={service} onChange={(e) => handleServiceChange(index, e.target.value)} />
                                                {index === services.length - 1 ? <button className="gs-add-button" type="button" onClick={() => setServices([...services, ''])}>+</button> : <div className="gs-add-button-placeholder"></div>}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="gs-field-column">
                                    <label className="gs-col-title">Store Locations</label>
                                    <div className="gs-dynamic-list">
                                        {locations.map((location, index) => (
                                            <div className="gs-input-with-addon" key={`loc-${index}`}>
                                                <input placeholder="Location name" type="text" value={location} onChange={(e) => handleLocationChange(index, e.target.value)} />
                                                {index === locations.length - 1 ? <button className="gs-add-button" type="button" onClick={() => setLocations([...locations, ''])}>+</button> : <div className="gs-add-button-placeholder"></div>}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                            <div className="gs-button-row">
                                <button className="gs-continue-button" type="button" onClick={nextStep} disabled={!isStep2Valid} style={{ opacity: isStep2Valid ? 1 : 0.5 }}>Continue &rarr;</button>
                            </div>
                        </form>
                    </section>
                );
            case 3:
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Product Database</h2>
                        <p className="gs-subtitle">Upload your products to let SociaLift understand your inventory.</p>
                        <form className="gs-form-wrapper">
                            <div className="gs-input-group">
                                <label className="gs-label-title" style={{ textAlign: 'center' }}>Products</label>
                                <div className="gs-upload-container">
                                    <div className="gs-upload-surface">
                                        <div className="gs-upload-dashed">
                                            <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileChange} />
                                            {selectedFile ? (
                                                <div className="gs-file-selected">
                                                    <span className="gs-file-name">📄 {selectedFile.name}</span>
                                                    <button type="button" className="gs-change-file-btn" onClick={() => fileInputRef.current?.click()}>Change File</button>
                                                </div>
                                            ) : (
                                                <>
                                                    <div className="gs-upload-icon" aria-hidden="true"><span className="gs-upload-arrow" /></div>
                                                    <p>Drag and drop files here, or click to browse</p>
                                                    <button className="gs-browse-button" type="button" onClick={() => fileInputRef.current?.click()}>Browse Files</button>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="gs-button-row">
                                <button className="gs-continue-button" type="button" onClick={nextStep} disabled={!isStep3Valid} style={{ opacity: isStep3Valid ? 1 : 0.5 }}>Continue &rarr;</button>
                            </div>
                        </form>
                    </section>
                );
            case 4:
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Persona Generation</h2>
                        <p className="gs-subtitle">Write a sample post so we can get to know your brand's voice.</p>
                        <form className="gs-form-wrapper">
                            <div className="gs-input-group">
                                <label className="gs-label-title" htmlFor="samplePost">Sample Post</label>
                                <span className="gs-label-help">We need you to write a post to get to know your persona / voice better.</span>
                                <textarea id="samplePost" className="gs-textarea" value={postText} onChange={(e) => setPostText(e.target.value)} placeholder="e.g.: From the playground to the boardroom..." />
                            </div>
                            <div className="gs-button-row">
                                <button className="gs-continue-button" type="button" onClick={nextStep} disabled={!isStep4Valid} style={{ opacity: isStep4Valid ? 1 : 0.5 }}>Continue &rarr;</button>
                            </div>
                        </form>
                    </section>
                );
            case 5:
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Persona Generation</h2>
                        <p className="gs-subtitle">SociaLift provides persona for posts generation.</p>
                        <div className="gs-choices-section">
                            <h3 className="gs-choices-title">Choose Your Persona</h3>
                            <div className="gs-choices-list">
                                <button className={`gs-choice ${selectedPersona === 1 ? 'is-selected' : ''}`} type="button" onClick={() => setSelectedPersona(1)}>The Playful Rebel (Casual, Rebellious & Fun)</button>
                                <button className={`gs-choice ${selectedPersona === 2 ? 'is-selected' : ''}`} type="button" onClick={() => setSelectedPersona(2)}>The Trendsetter (Urban, Influencing & Authentic)</button>
                                <button className={`gs-choice ${selectedPersona === 3 ? 'is-selected' : ''}`} type="button" onClick={() => setSelectedPersona(3)}>The Ruler (Strategic, Exclusive & Elegant)</button>
                            </div>
                        </div>
                        <div className="gs-button-row">
                            <button className="gs-continue-button" type="button" onClick={nextStep} disabled={!isStep5Valid} style={{ opacity: isStep5Valid ? 1 : 0.5 }}>Continue &rarr;</button>
                        </div>
                    </section>
                );
            case 6:
                const persona = getPersonaDetails();
                return (
                    <section className="gs-form-card">
                        <h2 className="gs-title">Persona Generation</h2>
                        <div className="gs-results">
                            <div className="gs-result-item"><span className="gs-result-label">Final Persona:</span><span className="gs-result-value">{persona.name}</span></div>
                            <div className="gs-result-item"><span className="gs-result-label">Tone:</span><span className="gs-result-value">{persona.tone}</span></div>
                            <div className="gs-result-item gs-long-item"><span className="gs-result-label">Example Post:</span><span className="gs-result-value">Quality you can trust for the people who matter most. From Nike active wear to Gini & Jony play-ready outfits, we've curated a complete wardrobe solution for your modern family since 1998.</span></div>
                        </div>
                        <div className="gs-button-row">
                            <button className="gs-continue-button" type="button" onClick={() => setShowModal(true)}>Done!</button>
                        </div>
                    </section>
                );
            default:
                return null;
        }
    };

    return (
        <div className="getting-started-container">
            <header className="gs-header">
                <button aria-label="Go back" className="gs-back-button" type="button" onClick={prevStep}>
                    <span aria-hidden="true">&#8592;</span>
                </button>
                <h1>Getting Started</h1>
            </header>

            <main className="gs-main-layout">
                {/* ANIMATED SIDEBAR */}
                <aside className="gs-sidebar">
                    <div className={`gs-step ${step > 2 ? 'is-complete' : 'is-active'}`}>
                        {step > 2 ? <span className="gs-step-check">&#10003;</span> : <span className="gs-step-num">1</span>}
                        <span className="gs-step-text">Company Information</span>
                    </div>
                    <div className="gs-step-dots">
                        <div className={`gs-dot ${step > 2 ? 'dot-complete' : step >= 1 ? 'dot-active' : 'gray-dot'}`}></div>
                        <div className={`gs-dot ${step > 2 ? 'dot-complete' : step >= 2 ? 'dot-active' : 'gray-dot'}`}></div>
                    </div>

                    <div className={`gs-step ${step > 3 ? 'is-complete' : step === 3 ? 'is-active' : ''}`}>
                        {step > 3 ? <span className="gs-step-check">&#10003;</span> : <span className="gs-step-num">2</span>}
                        <span className="gs-step-text">Products Database</span>
                    </div>
                    <div className="gs-step-dots">
                        <div className={`gs-dot ${step > 3 ? 'dot-complete' : 'gray-dot'}`}></div>
                    </div>

                    <div className={`gs-step ${step > 5 ? 'is-complete' : step >= 4 ? 'is-active' : ''}`}>
                        {step > 5 ? <span className="gs-step-check">&#10003;</span> : <span className="gs-step-num">3</span>}
                        <span className="gs-step-text">Choose your Persona</span>
                    </div>
                    <div className="gs-step-dots">
                        <div className={`gs-dot ${step > 6 ? 'dot-complete' : step >= 5 ? 'dot-active' : 'gray-dot'}`}></div>
                        <div className={`gs-dot ${step > 6 ? 'dot-complete' : step >= 6 ? 'dot-active' : 'gray-dot'}`}></div>
                    </div>

                    <div className={`gs-badge ${step === 6 ? 'is-almost' : ''}`}>{step === 6 ? 'Almost there...' : 'In progress'}</div>
                </aside>

                {/* ANIMATED FORM MOUNT */}
                <div key={step} className="form-step-animated">
                    {renderStep()}
                </div>

                {/* SUCCESS MODAL OVERLAY */}
                {showModal && (
                    <>
                        <div className="gs-overlay" aria-hidden="true" />
                        <section className="gs-success-modal" aria-label="Success confirmation">
                            <div className="gs-success-icon" aria-hidden="true">&#10003;</div>
                            <h3>SUCCESS!</h3>
                            <p>To view or modify your Information, Products Database, or Persona, please navigate to your User Profile.</p>
                            <button className="gs-success-continue" type="button" onClick={() => navigate('/home')}>Continue</button>
                        </section>
                    </>
                )}
            </main>
        </div>
    );
}